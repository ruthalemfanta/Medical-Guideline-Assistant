"""Answer generation with grounded synthesis for medical guidelines."""

from typing import List, Optional
from .models import RetrievedDocument, Citation, QueryAnalysis, MedicalIntent
from .config import settings


class MedicalAnswerGenerator:
    """Generates grounded answers from medical guideline evidence."""
    
    def __init__(self):
        # No LLM needed for current implementation
        pass
    
    def generate_answer(
        self, 
        query_analysis: QueryAnalysis,
        retrieved_docs: List[RetrievedDocument]
    ) -> tuple[str, List[Citation], float]:
        """Generate grounded answer with citations."""
        
        if not retrieved_docs:
            return self._no_evidence_response(), [], 0.0
        
        # Generate answer based on content
        answer = self._create_answer(query_analysis, retrieved_docs)
        
        # Extract citations
        citations = self._create_citations(retrieved_docs, answer)
        
        # Calculate confidence score
        confidence = self._calculate_confidence(answer, retrieved_docs)
        
        return answer, citations, confidence
    
    def _create_answer(self, query_analysis: QueryAnalysis, retrieved_docs: List[RetrievedDocument]) -> str:
        """Create answer from retrieved documents."""
        
        query_lower = query_analysis.original_query.lower()
        
        # Get clean content from top documents
        clean_content = self._extract_clean_content(retrieved_docs)
        
        if not clean_content:
            return self._no_evidence_response()
        
        # Determine answer type based on query
        if self._is_hiv_query(query_lower):
            return self._create_hiv_answer(query_lower, clean_content)
        else:
            return self._create_non_hiv_answer(query_lower, clean_content)
    
    def _extract_clean_content(self, retrieved_docs: List[RetrievedDocument]) -> List[str]:
        """Extract clean, meaningful content from documents."""
        
        clean_content = []
        
        for doc in retrieved_docs[:3]:  # Top 3 most relevant
            content = doc.content.strip()
            
            # Skip metadata/headers
            if any(skip in content.lower() for skip in [
                'prepared for educational purposes only',
                'page 1 of', 'page 2 of', 'page 3 of'
            ]):
                continue
            
            # Clean and filter substantial content
            clean_text = content.replace('**', '').replace('###', '').strip()
            if len(clean_text) > 50:
                clean_content.append(clean_text)
        
        return clean_content
    
    def _is_hiv_query(self, query_lower: str) -> bool:
        """Check if query is HIV-related."""
        return any(keyword in query_lower for keyword in ['hiv', 'aids', 'antiretroviral', 'art'])
    
    def _create_hiv_answer(self, query_lower: str, content_list: List[str]) -> str:
        """Create answer for HIV-related queries."""
        
        # Treatment guidelines
        if any(word in query_lower for word in ['treatment', 'guidelines', 'therapy']):
            return self._format_hiv_treatment_answer(content_list)
        
        # General HIV information
        elif any(word in query_lower for word in ['what is', 'about hiv', 'hiv?']):
            return self._format_hiv_definition_answer(content_list)
        
        # Prevention
        elif 'prevention' in query_lower:
            return self._format_hiv_prevention_answer(content_list)
        
        # Default: return first relevant content
        return self._format_basic_content(content_list)
    
    def _create_non_hiv_answer(self, query_lower: str, content_list: List[str]) -> str:
        """Create answer for non-HIV queries."""
        
        combined_content = " ".join(content_list).lower()
        
        # Check if asking about general medical topics we don't cover
        general_topics = ['diabetes', 'hypertension', 'heart disease', 'stroke', 'kidney', 'liver']
        
        # Special handling for cancer
        if 'cancer' in query_lower:
            # Check if we have HIV-related cancer content
            if any(hiv_cancer in combined_content for hiv_cancer in ['kaposi', 'cervical']):
                return self._format_hiv_cancer_answer(query_lower, content_list)
            else:
                return self._no_knowledge_response()
        
        # Check other general medical topics
        if any(topic in query_lower for topic in general_topics):
            return self._no_knowledge_response()
        
        # For other queries, return formatted content
        return self._format_basic_content(content_list)
    
    def _format_hiv_treatment_answer(self, content_list: List[str]) -> str:
        """Format HIV treatment guidelines answer."""
        
        answer = "According to WHO HIV treatment guidelines:\n\n"
        
        # Look for guideline lists
        for content in content_list:
            if 'list of relevant hiv guidelines' in content.lower():
                lines = content.split('\n')
                guidelines = []
                
                for line in lines:
                    line = line.strip()
                    if (line and ('guidelines for' in line.lower() or 
                                line.startswith(('1.', '2.', '3.', '4.', '5.')))):
                        clean_line = line.replace('1.', '•').replace('2.', '•').replace('3.', '•').replace('4.', '•').replace('5.', '•')
                        guidelines.append(clean_line)
                
                if guidelines:
                    answer += "**Key Guidelines:**\n"
                    answer += "\n".join(guidelines[:5]) + "\n\n"
                    break
        
        # Add objectives if found
        for content in content_list:
            if 'objectives' in content.lower() and 'guidelines' in content.lower():
                answer += "**Objectives:**\n"
                answer += "These guidelines provide evidence-informed clinical recommendations for HIV treatment and management.\n\n"
                break
        
        return answer.strip()
    
    def _format_hiv_definition_answer(self, content_list: List[str]) -> str:
        """Format HIV definition answer."""
        
        answer = "HIV (Human Immunodeficiency Virus) is a retrovirus that attacks the body's immune system.\n\n"
        
        # Extract key facts from content
        facts = []
        for content in content_list:
            sentences = content.split('.')
            for sentence in sentences:
                sentence = sentence.strip()
                if (len(sentence) > 30 and 
                    any(keyword in sentence.lower() for keyword in ['hiv', 'virus', 'immune', 'transmission'])):
                    facts.append(sentence)
                    if len(facts) >= 3:
                        break
        
        if facts:
            answer += "**Key Facts:**\n"
            for fact in facts[:3]:
                answer += f"• {fact}\n"
        else:
            answer += ("**Key Facts:**\n"
                      "• If left untreated, HIV can progress to AIDS\n"
                      "• With proper treatment, people with HIV can live normal lives\n"
                      "• Effective treatment prevents transmission (U=U)")
        
        return answer
    
    def _format_hiv_prevention_answer(self, content_list: List[str]) -> str:
        """Format HIV prevention answer."""
        
        answer = "HIV Prevention Methods:\n\n"
        
        # Look for prevention content
        prevention_content = []
        for content in content_list:
            if any(keyword in content.lower() for keyword in ['prevention', 'prevent', 'transmission']):
                prevention_content.append(content)
        
        if prevention_content:
            # Extract key prevention points
            sentences = prevention_content[0].split('.')
            for sentence in sentences[:3]:
                if len(sentence.strip()) > 20:
                    answer += f"• {sentence.strip()}\n"
        else:
            answer += ("• Use condoms consistently and correctly\n"
                      "• Get tested regularly\n"
                      "• Consider PrEP if at high risk")
        
        return answer
    
    def _format_hiv_cancer_answer(self, query_lower: str, content_list: List[str]) -> str:
        """Format HIV-related cancer answer."""
        
        if 'what is cancer' in query_lower or 'what cancer is' in query_lower:
            # Be honest about limitations first, then provide relevant context
            answer = ("I don't have comprehensive information about cancer in general. "
                     "However, according to the HIV guidelines in my database, "
                     "certain cancers are of particular concern for people with HIV:\n\n")
            
            combined_content = " ".join(content_list).lower()
            
            if 'kaposi' in combined_content:
                answer += "**Kaposi's Sarcoma**: A cancer that commonly affects people with HIV, particularly those with advanced HIV disease.\n\n"
            
            if 'cervical' in combined_content:
                answer += "**Cervical Cancer**: Women living with HIV have increased risk of cervical cancer.\n\n"
            
            answer += ("For comprehensive information about cancer in general, "
                      "please consult general medical resources or speak with a healthcare provider.")
            
            return answer
        
        # For treatment questions, also acknowledge limitations
        elif 'treatment' in query_lower:
            return ("I don't have general cancer treatment information. However, according to WHO HIV guidelines:\n\n" + 
                   self._format_basic_content(content_list))
        
        return self._format_basic_content(content_list)
    
    def _format_basic_content(self, content_list: List[str]) -> str:
        """Format basic content response."""
        
        if not content_list:
            return self._no_evidence_response()
        
        main_content = content_list[0]
        
        # Truncate if too long
        if len(main_content) > 400:
            sentences = main_content.split('.')
            return '. '.join(sentences[:3]) + '.'
        
        return main_content
    
    def _create_citations(self, retrieved_docs: List[RetrievedDocument], answer: str) -> List[Citation]:
        """Create citations from retrieved documents."""
        
        citations = []
        
        for doc in retrieved_docs[:3]:  # Top 3 citations
            metadata = doc.metadata
            quote = self._find_relevant_quote(doc.content, answer)
            
            citation = Citation(
                guideline_name=metadata.guideline,
                section=metadata.section,
                page_number=metadata.page_number,
                organization=metadata.guideline_metadata.organization,
                year=metadata.guideline_metadata.publication_year,
                quote=quote
            )
            
            citations.append(citation)
        
        return citations
    
    def _find_relevant_quote(self, doc_content: str, answer: str) -> str:
        """Find relevant quote from document."""
        
        sentences = doc_content.split('.')
        answer_words = set(answer.lower().split())
        
        # Find sentence with most word overlap
        best_sentence = ""
        best_overlap = 0
        
        for sentence in sentences:
            if len(sentence.strip()) > 30:
                sentence_words = set(sentence.lower().split())
                overlap = len(sentence_words.intersection(answer_words))
                
                if overlap > best_overlap:
                    best_overlap = overlap
                    best_sentence = sentence.strip()
        
        if best_sentence:
            return best_sentence[:200] + "..." if len(best_sentence) > 200 else best_sentence
        
        # Fallback
        return doc_content[:200] + "..."
    
    def _calculate_confidence(self, answer: str, retrieved_docs: List[RetrievedDocument]) -> float:
        """Calculate confidence score."""
        
        if not retrieved_docs:
            return 0.0
        
        # Factors for confidence
        factors = []
        
        # Document count factor
        doc_factor = min(len(retrieved_docs) / 3.0, 1.0)
        factors.append(doc_factor)
        
        # Relevance score factor (normalized)
        avg_relevance = sum(doc.relevance_score for doc in retrieved_docs) / len(retrieved_docs)
        normalized_relevance = max(0.0, min(1.0, (avg_relevance + 5.0) / 10.0))
        factors.append(normalized_relevance)
        
        # Answer length factor
        length_factor = min(len(answer) / 300.0, 1.0)
        factors.append(length_factor)
        
        # Citation presence factor
        citation_factor = 1.0 if any(word in answer.lower() for word in ['according to', 'who guidelines']) else 0.7
        factors.append(citation_factor)
        
        return round(sum(factors) / len(factors), 2)
    
    def _no_evidence_response(self) -> str:
        """Response when no evidence is available."""
        return (
            "I could not find specific information about this topic in the "
            "available medical guidelines. This may be because the topic is "
            "not covered in the current guideline database or the question "
            "may need to be more specific."
        )
    
    def _no_knowledge_response(self) -> str:
        """Response when topic is outside our knowledge base."""
        return (
            "I don't have specific information about this topic in the available "
            "medical guidelines. The current database primarily contains "
            "HIV-related guidelines from WHO."
        )