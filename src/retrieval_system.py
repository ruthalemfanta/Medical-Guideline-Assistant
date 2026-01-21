"""Hybrid retrieval system for medical guidelines."""

from typing import List, Dict, Any, Optional
from enum import Enum
from datetime import datetime
import numpy as np
from rank_bm25 import BM25Okapi
import pickle
import os
from pathlib import Path

from sentence_transformers import SentenceTransformer
from langchain_core.documents import Document
from sentence_transformers import CrossEncoder
from pinecone import Pinecone

from .models import (
    RetrievedDocument,
    ChunkMetadata,
    QueryAnalysis,
    PopulationType,
    GuidelineMetadata,
)
from .config import settings


class PineconeVectorStore:
    """Cloud vector store backed by Pinecone."""

    def __init__(self, api_key: str, index_name: str, host: str, namespace: str = "default"):
        if not api_key or not host:
            raise RuntimeError("Pinecone API key and host are required for the vector store.")

        self.namespace = namespace
        self.client = Pinecone(api_key=api_key)
        self.index = self.client.Index(host=host)
        self.index_name = index_name

    def add_documents(self, documents: List[Document], embeddings: List[List[float]]):
        """Upsert documents with embeddings into Pinecone."""
        vectors = []
        for doc, embedding in zip(documents, embeddings):
            metadata = self._sanitize_metadata(dict(doc.metadata))
            metadata["page_content"] = doc.page_content
            # Use chunk_id if present; otherwise fallback to hash
            vector_id = metadata.get("chunk_id") or str(abs(hash(doc.page_content)) % (10**12))
            vectors.append({
                "id": vector_id,
                "values": embedding,
                "metadata": metadata,
            })

        if vectors:
            self.index.upsert(vectors=vectors, namespace=self.namespace)

    def _sanitize_metadata(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Flatten and clean metadata to Pinecone-friendly primitives."""
        clean: Dict[str, Any] = {}

        def handle_value(key: str, value: Any, prefix: str = ""):
            if value is None:
                return
            if isinstance(value, Enum):
                value = value.value
            elif hasattr(value, "isoformat"):
                value = value.isoformat()
            if isinstance(value, dict):
                for sub_key, sub_val in value.items():
                    handle_value(f"{key}_{sub_key}", sub_val, prefix)
                return
            if isinstance(value, (str, int, float, bool, list)):
                clean[prefix + key] = value

        for k, v in metadata.items():
            handle_value(k, v)

        return clean

    def similarity_search_with_score(self, query_embedding: List[float], k: int = 10):
        """Query Pinecone and return documents with scores."""
        result = self.index.query(
            vector=query_embedding,
            top_k=k,
            include_metadata=True,
            namespace=self.namespace,
        )

        matches = getattr(result, "matches", []) or []
        docs_with_scores = []
        for match in matches:
            md = match.metadata or {}
            content = md.pop("page_content", "")

            # Rehydrate guideline metadata from flattened fields
            gm_fields = {
                key[len("guideline_metadata_"):]: value
                for key, value in list(md.items())
                if key.startswith("guideline_metadata_")
            }
            for key in list(md.keys()):
                if key.startswith("guideline_metadata_"):
                    md.pop(key)

            guideline_meta = GuidelineMetadata(
                guideline_name=md.get("guideline") or gm_fields.get("guideline_name") or "Unknown Guideline",
                organization=gm_fields.get("organization") or "Unknown",
                publication_year=int(gm_fields.get("publication_year") or datetime.now().year),
                version=gm_fields.get("version"),
                country=gm_fields.get("country"),
                specialty=gm_fields.get("specialty"),
                last_updated=datetime.fromisoformat(gm_fields["last_updated"]) if gm_fields.get("last_updated") else None,
            )

            md["guideline_metadata"] = guideline_meta
            doc = Document(page_content=content, metadata=md)
            # Pinecone returns similarity score; convert to distance-compatible format
            distance = 1.0 - float(match.score) if match.score is not None else 1.0
            docs_with_scores.append((doc, distance))

        return docs_with_scores


class MedicalRetrievalSystem:
    """Hybrid retrieval system combining dense and sparse retrieval."""
    
    def __init__(self):
        # Use free local embeddings instead of OpenAI
        self.embeddings_model = SentenceTransformer('all-MiniLM-L6-v2')
        # Pinecone vector store (cloud)
        self.vector_store = PineconeVectorStore(
            api_key=settings.pinecone_api_key,
            index_name=settings.pinecone_index,
            host=settings.pinecone_host,
            namespace=settings.pinecone_namespace,
        )
        
        # Initialize reranker
        self.reranker = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')
        
        # BM25 will be initialized when documents are added
        self.bm25 = None
        self.documents = []
        
        print("✅ Using simple vector store with free local embeddings")
    
    def add_documents(self, documents: List[Document]) -> None:
        """Add documents to both vector and BM25 indices."""
        
        print(f"Adding {len(documents)} documents...")
        
        # Generate embeddings using local model
        texts = [doc.page_content for doc in documents]
        embeddings = self.embeddings_model.encode(texts).tolist()
        
        # Add to vector store
        self.vector_store.add_documents(documents, embeddings)
        
        # Update BM25 index
        self.documents.extend(documents)
        corpus = [doc.page_content for doc in self.documents]
        tokenized_corpus = [doc.split() for doc in corpus]
        self.bm25 = BM25Okapi(tokenized_corpus)
        
        print(f"✅ Added {len(documents)} documents")
    
    def retrieve(
        self, 
        query_analysis: QueryAnalysis, 
        k: int = None
    ) -> List[RetrievedDocument]:
        """Retrieve relevant documents using hybrid approach."""
        
        k = k or settings.max_retrieval_docs
        query = query_analysis.original_query
        
        # Step 1: Dense retrieval (semantic)
        dense_docs = self._dense_retrieval(query, k * 2)
        
        # Step 2: Sparse retrieval (BM25)
        sparse_docs = self._sparse_retrieval(query, k * 2)
        
        # Step 3: Combine and deduplicate
        combined_docs = self._combine_results(dense_docs, sparse_docs)
        
        # Step 4: Apply metadata filters
        filtered_docs = self._apply_filters(combined_docs, query_analysis)
        
        # Step 5: Rerank
        reranked_docs = self._rerank(query, filtered_docs)
        
        # Step 6: Convert to RetrievedDocument format
        retrieved_docs = []
        for doc, score in reranked_docs[:k]:
            chunk_metadata = ChunkMetadata(**doc.metadata)
            retrieved_doc = RetrievedDocument(
                content=doc.page_content,
                metadata=chunk_metadata,
                relevance_score=score,
                rerank_score=score
            )
            retrieved_docs.append(retrieved_doc)
        
        return retrieved_docs
    
    def _dense_retrieval(self, query: str, k: int) -> List[tuple]:
        """Dense vector retrieval."""
        query_embedding = self.embeddings_model.encode([query])[0].tolist()
        results = self.vector_store.similarity_search_with_score(query_embedding, k=k)
        return [(doc, 1.0 - score) for doc, score in results]  # Convert distance to similarity
    
    def _sparse_retrieval(self, query: str, k: int) -> List[tuple]:
        """Sparse BM25 retrieval."""
        if not self.bm25:
            return []
        
        tokenized_query = query.split()
        scores = self.bm25.get_scores(tokenized_query)
        
        # Get top k documents
        top_indices = np.argsort(scores)[::-1][:k]
        
        results = []
        for idx in top_indices:
            if idx < len(self.documents):
                doc = self.documents[idx]
                score = scores[idx]
                results.append((doc, score))
        
        return results
    
    def _combine_results(
        self, 
        dense_results: List[tuple], 
        sparse_results: List[tuple]
    ) -> List[tuple]:
        """Combine dense and sparse results, removing duplicates."""
        
        seen_content = set()
        combined = []
        
        # Add dense results
        for doc, score in dense_results:
            content_hash = hash(doc.page_content[:100])
            if content_hash not in seen_content:
                seen_content.add(content_hash)
                combined.append((doc, score, 'dense'))
        
        # Add sparse results
        for doc, score in sparse_results:
            content_hash = hash(doc.page_content[:100])
            if content_hash not in seen_content:
                seen_content.add(content_hash)
                combined.append((doc, score, 'sparse'))
        
        return combined
    
    def _apply_filters(
        self, 
        documents: List[tuple], 
        query_analysis: QueryAnalysis
    ) -> List[tuple]:
        """Apply metadata-based filters."""
        
        filtered = []
        
        for doc, score, source in documents:
            metadata = doc.metadata
            
            # Population filter
            if query_analysis.population and query_analysis.population != PopulationType.GENERAL:
                doc_population = metadata.get('population', 'general')
                if (doc_population != query_analysis.population.value and 
                    doc_population != 'general'):
                    continue
            
            filtered.append((doc, score, source))
        
        return filtered
    
    def _rerank(self, query: str, documents: List[tuple]) -> List[tuple]:
        """Rerank documents using cross-encoder."""
        
        if not documents:
            return []
        
        # Prepare pairs for reranking
        pairs = []
        docs = []
        
        for doc, score, source in documents:
            pairs.append([query, doc.page_content])
            docs.append((doc, score))
        
        # Get reranking scores
        rerank_scores = self.reranker.predict(pairs)
        
        # Combine with original scores
        final_results = []
        for i, (doc, original_score) in enumerate(docs):
            final_score = 0.3 * original_score + 0.7 * rerank_scores[i]
            final_results.append((doc, final_score))
        
        # Sort by final score
        final_results.sort(key=lambda x: x[1], reverse=True)
        
        return final_results
    
    def get_document_count(self) -> int:
        """Get total number of indexed documents."""
        return len(self.documents)
    
    def search_by_metadata(self, filters: Dict[str, Any]) -> List[Document]:
        """Search documents by metadata filters."""
        
        matching_docs = []
        
        for doc in self.documents:
            match = True
            for key, value in filters.items():
                if key not in doc.metadata or doc.metadata[key] != value:
                    match = False
                    break
            
            if match:
                matching_docs.append(doc)
        
        return matching_docs