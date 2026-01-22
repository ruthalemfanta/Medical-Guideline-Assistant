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
        citations = [] 
        
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
            if any(skip in content.lower() for skip in [
                'prepared for educational purposes only',
                'page 1 of', 'page 2 of', 'page 3 of'
            ]):
                continue
            
            source_name = metadata.guideline if metadata.guideline else "Medical Guideline"
            
            evidence_part = f"""
            [Evidence {i}]
            Source: {source_name}
            Content: {content}
            """
            
            evidence_parts.append(evidence_part.strip())
        
        return "\n\n".join(evidence_parts)
    
    def _generate_llm_answer(self, query_analysis: QueryAnalysis, evidence_context: str) -> str:
        """Generate answer using Gemini with proper prompting."""
        
        prompt = f"""
        You are a medical information assistant. Provide CONCISE, educational answers based ONLY on the evidence provided. Answer in a polite friendly manner.
        
        CRITICAL INSTRUCTIONS:
        1. Keep answers conscise.
        2. ONLY use information explicitly stated in the evidence below
        3. DO NOT add extra information not in the evidence
        4. DO NOT make up years, organizations, or publication dates
        5. If the evidence doesn't contain relevant information, say "I don't have specific information about this topic in the available medical guidelines"
        6. For simple definition questions, give a brief definition only
        7. Use simple, clear language
        
        QUERY: {query_analysis.original_query}
        
        EVIDENCE FROM MEDICAL GUIDELINES:
        {evidence_context}
        
        Provide a CONCISE response (maximum 100 words for simple questions):
        """
        
        try:
            response = self.client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt
            )
            raw_answer = response.text.strip()
            
            # Format the answer to clean up markdown symbols
            formatted_answer = self._format_markdown_to_text(raw_answer)
            
            return formatted_answer
            
        except Exception as e:
            return f"I encountered an error while processing your query: {str(e)}"
    
    def _format_markdown_to_text(self, text: str) -> str:
        """Convert markdown formatting to clean text formatting."""
        
        # Convert bold text (**text** or __text__)
        import re
        
        # Replace **bold** with BOLD TEXT 
        text = re.sub(r'\*\*(.*?)\*\*', r'\1', text) 
        text = re.sub(r'__(.*?)__', r'\1', text)      
        
        # Replace *italic* with regular text 
        text = re.sub(r'\*(.*?)\*', r'\1', text)
        
        # Clean up bullet points - convert * to •
        text = re.sub(r'^\s*\*\s+', '• ', text, flags=re.MULTILINE)
        
        # Clean up numbered lists - ensure proper formatting
        text = re.sub(r'^\s*(\d+)\.\s+', r'\1. ', text, flags=re.MULTILINE)
        
        # Clean up headers (### or ##)
        text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)
        
        # Clean up any remaining markdown artifacts
        text = re.sub(r'`([^`]+)`', r'\1', text) 
        text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)  
        
        # Clean up extra whitespace
        text = re.sub(r'\n\s*\n\s*\n', '\n\n', text) 
        text = re.sub(r'[ \t]+', ' ', text)  
        
        return text.strip()
    
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
            # For concise answers, prefer shorter responses for simple questions
            answer_length = len(answer)
            if answer_length < 200:
                length_factor = 1.0  # Good concise answer
            elif answer_length < 500:
                length_factor = 0.8  # Acceptable length
            else:
                length_factor = 0.6  # Too verbose, lower confidence
            factors.append(length_factor)
        
        # Source attribution factor - but don't require made-up citations
        source_factor = 1.0 if any(phrase in answer_lower for phrase in [
            'according to', 'guidelines', 'evidence shows'
        ]) else 0.8  # Slightly lower but still good if no attribution
        factors.append(source_factor)
        
        # Penalize if answer contains suspicious citations (made-up years)
        if any(suspicious in answer_lower for suspicious in ['2026', '2027', '2028']):
            factors.append(0.3)  # Heavy penalty for made-up citations
        
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