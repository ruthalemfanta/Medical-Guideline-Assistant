"""Hybrid retrieval system for medical guidelines."""

from typing import List, Dict, Any, Optional
import numpy as np
from rank_bm25 import BM25Okapi
import pickle
import os
from pathlib import Path

from sentence_transformers import SentenceTransformer
from langchain_core.documents import Document
from sentence_transformers import CrossEncoder

from .models import RetrievedDocument, ChunkMetadata, QueryAnalysis, PopulationType
from .config import settings


class SimpleVectorStore:
    """Simple vector store using numpy for similarity search."""
    
    def __init__(self, persist_directory: str):
        self.persist_directory = persist_directory
        self.documents = []
        self.embeddings_array = None
        Path(persist_directory).mkdir(parents=True, exist_ok=True)
        self._load_data()
    
    def add_documents(self, documents: List[Document], embeddings: List[List[float]]):
        """Add documents with their embeddings."""
        self.documents.extend(documents)
        
        if self.embeddings_array is None:
            self.embeddings_array = np.array(embeddings, dtype=np.float32)
        else:
            new_embeddings = np.array(embeddings, dtype=np.float32)
            self.embeddings_array = np.vstack([self.embeddings_array, new_embeddings])
        
        self._save_data()
    
    def similarity_search_with_score(self, query_embedding: List[float], k: int = 10):
        """Search for similar documents."""
        if not self.documents or self.embeddings_array is None:
            return []
        
        query_vector = np.array([query_embedding], dtype=np.float32)
        
        # Calculate cosine similarity
        query_norm = np.linalg.norm(query_vector)
        doc_norms = np.linalg.norm(self.embeddings_array, axis=1)
        
        # Avoid division by zero
        doc_norms = np.where(doc_norms == 0, 1e-8, doc_norms)
        query_norm = query_norm if query_norm != 0 else 1e-8
        
        similarities = np.dot(self.embeddings_array, query_vector.T).flatten() / (doc_norms * query_norm)
        
        # Get top k indices
        top_indices = np.argsort(similarities)[::-1][:k]
        
        results = []
        for idx in top_indices:
            if idx < len(self.documents):
                # Convert similarity to distance (lower = more similar for compatibility)
                distance = 1.0 - similarities[idx]
                results.append((self.documents[idx], float(distance)))
        
        return results
    
    def _save_data(self):
        """Save documents and embeddings."""
        try:
            docs_path = Path(self.persist_directory) / "documents.pkl"
            with open(docs_path, 'wb') as f:
                pickle.dump(self.documents, f)
            
            if self.embeddings_array is not None:
                embeddings_path = Path(self.persist_directory) / "embeddings.npy"
                np.save(embeddings_path, self.embeddings_array)
        except Exception as e:
            print(f"Warning: Could not save data: {e}")
    
    def _load_data(self):
        """Load documents and embeddings."""
        try:
            docs_path = Path(self.persist_directory) / "documents.pkl"
            if docs_path.exists():
                with open(docs_path, 'rb') as f:
                    self.documents = pickle.load(f)
            
            embeddings_path = Path(self.persist_directory) / "embeddings.npy"
            if embeddings_path.exists():
                self.embeddings_array = np.load(embeddings_path)
        except Exception as e:
            print(f"Warning: Could not load existing data: {e}")
            self.documents = []
            self.embeddings_array = None
    
    def persist(self):
        """Persist data."""
        self._save_data()


class MedicalRetrievalSystem:
    """Hybrid retrieval system combining dense and sparse retrieval."""
    
    def __init__(self):
        # Use free local embeddings instead of OpenAI
        self.embeddings_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Use simple vector store instead of ChromaDB
        self.vector_store = SimpleVectorStore(settings.chroma_persist_directory)
        
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