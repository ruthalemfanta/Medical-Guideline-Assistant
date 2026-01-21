"""Answer generation with grounded synthesis for medical guidelines."""

from typing import List, Optional
import google.genai as genai
from .models import RetrievedDocument, Citation, QueryAnalysis, MedicalIntent
from .config import settings


class MedicalAnswerGenerator:
    """Generates grounded answers from medical guideline evidence."""
    
    def __init__(self):
        # Initialize Gemini Flash 2.0 for proper answer generation
        self.client = genai.Client(api_key=settings.google_api_key)
    
    def generate_answer(
        self, 
        query_analysis: QueryAnalysis,
        retrieved_docs: List[RetrievedDocument]
    ) -> tuple[str, List[Citation], float]:
        """Generate grounded answer with citations."""
        
        if not retrieved_docs:
            return self._generate_no_evidence_response(), [], 0.0
        
        # Format evidence context
        evidence_context = self._format_evidence_context(retrieved_docs)
        
        # Generate answer using Gemini
        answer = self._generate_llm_answer(query_analysis, evidence_context)
        
        # Create simple source attribution (no detailed citations)
        citations = []  # Disabled as requested
        
        # Calculate confidence score
        confidence = self._calculate_confidence(answer, retrieved_docs)
        
        return answer, citations, confidence
    
    def _format_evidence_context(self, retrieved_docs: List[RetrievedDocument]) -> str:
        """Format retrieved documents as evidence context."""
        
        evidence_parts = []
        
        for i, doc in enumerate(retrieved_docs[:5], 1):  # Top 5 documents
            metadata = doc.metadata
            
            # Clean content
            content = doc.content.strip()
            
            # Skip obvious metadata/headers
            if any(skip in content.lower() for skip in [
                'prepared for educational purposes only',
                'page 1 of', 'page 2 of', 'page 3 of'
            ]):
                continue
            
            evidence_part = f"""
            [Evidence {i}]
            Source: {metadata.guideline} ({metadata.guideline_metadata.organization} {metadata.guideline_metadata.publication_year})
            Content: {content}
            """
            
            evidence_parts.append(evidence_part.strip())
        
        return "\n\n".join(evidence_parts)
    
    def _generate_llm_answer(self, query_analysis: QueryAnalysis, evidence_context: str) -> str:
        """Generate answer using Gemini with proper prompting."""
        
        prompt = f"""
        You are a medical information assistant that provides educational information based on medical guidelines.
        
        CRITICAL INSTRUCTIONS:
        1. ONLY use information explicitly stated in the evidence below
        2. If the evidence does not contain relevant information for the query, say "I don't have specific information about this topic in the available medical guidelines"
        3. DO NOT make up or infer information not present in the evidence
        4. If the evidence contains related but not directly relevant information, acknowledge the limitation first, then provide what relevant context you can
        5. Always maintain an educational, not advisory tone
        6. Include source attribution (e.g., "According to WHO guidelines...")
        7. Be honest about the scope and limitations of the available information
        
        QUERY: {query_analysis.original_query}
        
        EVIDENCE FROM MEDICAL GUIDELINES:
        {evidence_context}
        
        RESPONSE:
        """
        
        try:
            response = self.client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt
            )
            return response.text.strip()
            
        except Exception as e:
            return f"I encountered an error while processing your query: {str(e)}"
    
    def _calculate_confidence(self, answer: str, retrieved_docs: List[RetrievedDocument]) -> float:
        """Calculate confidence score based on answer quality and evidence."""
        
        if not retrieved_docs:
            return 0.0
        
        factors = []
        
        # Document count factor
        doc_factor = min(len(retrieved_docs) / 3.0, 1.0)
        factors.append(doc_factor)
        
        # Relevance score factor (normalized)
        avg_relevance = sum(doc.relevance_score for doc in retrieved_docs) / len(retrieved_docs)
        normalized_relevance = max(0.0, min(1.0, (avg_relevance + 5.0) / 10.0))
        factors.append(normalized_relevance)
        
        # Answer quality factors
        answer_lower = answer.lower()
        
        # Penalize "I don't know" responses (but don't eliminate them)
        if "don't have specific information" in answer_lower:
            factors.append(0.3)  # Lower confidence for no-knowledge responses
        else:
            # Higher confidence for substantive answers
            length_factor = min(len(answer) / 200.0, 1.0)
            factors.append(length_factor)
        
        # Source attribution factor
        source_factor = 1.0 if any(phrase in answer_lower for phrase in [
            'according to', 'who guidelines', 'guidelines state', 'evidence shows'
        ]) else 0.7
        factors.append(source_factor)
        
        return round(sum(factors) / len(factors), 2)
    
    def _generate_no_evidence_response(self) -> str:
        """Generate response when no evidence is available."""
        return (
            "I could not find specific information about this topic in the "
            "available medical guidelines. This may be because:\n\n"
            "• The topic is not covered in the current guideline database\n"
            "• The question may need to be more specific\n"
            "• The information may be in a section not yet indexed\n\n"
            "Please try rephrasing your question or consult the original "
            "guideline documents directly."
        )