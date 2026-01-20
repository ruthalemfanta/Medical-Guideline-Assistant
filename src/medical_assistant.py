"""Main Medical Guideline Assistant system orchestrator."""

from typing import List, Optional
from datetime import datetime
import logging

from .models import MedicalResponse, QueryAnalysis, SafetyCheck
from .query_analyzer import MedicalQueryAnalyzer
from .retrieval_system import MedicalRetrievalSystem
from .answer_generator import MedicalAnswerGenerator
from .safety_validator import MedicalSafetyValidator
from .document_processor import MedicalDocumentProcessor
from .config import settings

# Configure logging
logging.basicConfig(level=getattr(logging, settings.log_level))
logger = logging.getLogger(__name__)


class MedicalGuidelineAssistant:
    """Main system orchestrating the medical guideline RAG pipeline."""
    
    def __init__(self):
        """Initialize all system components."""
        logger.info("Initializing Medical Guideline Assistant")
        
        self.query_analyzer = MedicalQueryAnalyzer()
        self.retrieval_system = MedicalRetrievalSystem()
        self.answer_generator = MedicalAnswerGenerator()
        self.safety_validator = MedicalSafetyValidator()
        self.document_processor = MedicalDocumentProcessor()
        
        logger.info("Medical Guideline Assistant initialized successfully")
    
    def process_query(self, query: str) -> MedicalResponse:
        """Process a medical query through the complete RAG pipeline."""
        
        logger.info(f"Processing query: {query[:100]}...")
        
        try:
            # Step 1: Query Analysis & Intent Classification
            logger.debug("Step 1: Analyzing query")
            query_analysis = self.query_analyzer.analyze_query(query)
            
            # Step 2: Handle conversational queries
            if query_analysis.intent == "conversational":
                logger.info("Handling conversational query")
                return self._create_conversational_response(query, query_analysis)
            
            # Step 3: Early safety check
            if not query_analysis.is_safe:
                logger.warning(f"Unsafe query detected: {query_analysis.risk_factors}")
                return self._create_refusal_response(query, query_analysis)
            
            # Step 4: Retrieval
            logger.debug("Step 4: Retrieving relevant documents")
            retrieved_docs = self.retrieval_system.retrieve(query_analysis)
            
            if not retrieved_docs:
                logger.warning("No relevant documents found")
                return self._create_no_evidence_response(query, query_analysis)
            
            # Step 5: Answer Generation
            logger.debug("Step 5: Generating answer")
            answer, citations, confidence = self.answer_generator.generate_answer(
                query_analysis, retrieved_docs
            )
            
            # Step 6: Safety Validation
            logger.debug("Step 6: Validating safety")
            safety_check = self.safety_validator.validate_response(
                query_analysis, answer, retrieved_docs
            )
            
            # Step 7: Final safety decision
            if not safety_check.is_safe:
                logger.warning(f"Response failed safety check: {safety_check.violations}")
                return self._create_refusal_response(query, query_analysis, safety_check)
            
            # Step 8: Create final response (don't add disclaimer to answer text)
            response = MedicalResponse(
                query=query,
                answer=answer,  # Clean answer without disclaimer
                citations=citations,
                safety_check=safety_check,
                confidence_score=confidence,
                retrieved_documents=retrieved_docs,
                disclaimer=self.safety_validator.get_educational_disclaimer()
            )
            
            logger.info(f"Query processed successfully. Confidence: {confidence}")
            return response
            
        except Exception as e:
            logger.error(f"Error processing query: {str(e)}")
            return self._create_error_response(query, str(e))
    
    def add_guideline_document(self, file_path: str) -> bool:
        """Add a new guideline document to the system."""
        
        logger.info(f"Adding guideline document: {file_path}")
        
        try:
            # Extract metadata
            metadata = self.document_processor.extract_metadata_from_pdf(file_path)
            logger.info(f"Extracted metadata: {metadata.guideline_name}")
            
            # Process document
            documents = self.document_processor.process_pdf(file_path, metadata)
            logger.info(f"Processed {len(documents)} chunks")
            
            # Add to retrieval system
            self.retrieval_system.add_documents(documents)
            logger.info("Document added to retrieval system")
            
            return True
            
        except Exception as e:
            logger.error(f"Error adding document: {str(e)}")
            return False
    
    def get_system_stats(self) -> dict:
        """Get system statistics."""
        return {
            "total_documents": self.retrieval_system.get_document_count(),
            "supported_sources": settings.supported_sources,
            "safety_checks_enabled": settings.enable_safety_checks,
            "citations_required": settings.require_citations
        }
    
    def _create_conversational_response(
        self, 
        query: str, 
        query_analysis: QueryAnalysis
    ) -> MedicalResponse:
        """Create a friendly conversational response."""
        
        query_lower = query.lower().strip()
        
        # Generate appropriate conversational responses
        if any(greeting in query_lower for greeting in ['hi', 'hello', 'hey']):
            conversational_answer = (
                "Hello! I'm here to help you find information from medical guidelines. "
                "You can ask me about medical conditions, treatments, or procedures based on "
                "official health organization guidelines like WHO, CDC, and NICE. "
                "What would you like to know?"
            )
        elif any(thanks in query_lower for thanks in ['thanks', 'thank you', 'thx']):
            conversational_answer = (
                "You're welcome! I'm glad I could help. Feel free to ask me any other "
                "questions about medical guidelines or health information."
            )
        elif any(response in query_lower for response in ['great', 'good', 'ok', 'okay', 'fine', 'nice', 'cool', 'awesome']):
            conversational_answer = (
                "Great! Is there anything specific about medical guidelines or health "
                "information you'd like to know more about?"
            )
        else:
            conversational_answer = (
                "I'm here to help you find information from medical guidelines. "
                "You can ask me about medical conditions, treatments, or procedures. "
                "What would you like to know?"
            )
        
        safety_check = SafetyCheck(
            is_safe=True,
            violations=[],
            requires_disclaimer=False,
            refusal_reason=None
        )
        
        return MedicalResponse(
            query=query,
            answer=conversational_answer,
            citations=[],
            safety_check=safety_check,
            confidence_score=1.0,  # High confidence for conversational responses
            retrieved_documents=[],
            disclaimer=""  # No disclaimer needed for conversational responses
        )
    
    def _create_refusal_response(
        self, 
        query: str, 
        query_analysis: QueryAnalysis,
        safety_check: Optional = None
    ) -> MedicalResponse:
        """Create a refusal response for unsafe queries."""
        
        if safety_check:
            refusal_answer = self.safety_validator.generate_refusal_response(safety_check)
        else:
            # Create a proper SafetyCheck for refusal
            temp_safety_check = SafetyCheck(
                is_safe=False,
                violations=query_analysis.risk_factors,
                requires_disclaimer=True,
                refusal_reason=f"Query intent: {query_analysis.intent.value}"
            )
            refusal_answer = self.safety_validator.generate_refusal_response(temp_safety_check)
        
        return MedicalResponse(
            query=query,
            answer=refusal_answer,
            citations=[],
            safety_check=safety_check or SafetyCheck(
                is_safe=False,
                violations=query_analysis.risk_factors,
                requires_disclaimer=True,
                refusal_reason="Unsafe query"
            ),
            confidence_score=0.0,
            retrieved_documents=[],
            disclaimer=self.safety_validator.get_educational_disclaimer()
        )
    
    def _create_no_evidence_response(
        self, 
        query: str, 
        query_analysis: QueryAnalysis
    ) -> MedicalResponse:
        """Create response when no evidence is found."""
        
        no_evidence_answer = (
            "I could not find specific information about this topic in the "
            "available medical guidelines. This may be because the topic is "
            "not covered in the current guideline database, or the question "
            "may need to be more specific."
        )
        
        safety_check = SafetyCheck(
            is_safe=True,
            violations=[],
            requires_disclaimer=True,
            refusal_reason=None
        )
        
        return MedicalResponse(
            query=query,
            answer=no_evidence_answer + self.safety_validator.get_educational_disclaimer(),
            citations=[],
            safety_check=safety_check,
            confidence_score=0.0,
            retrieved_documents=[],
            disclaimer=self.safety_validator.get_educational_disclaimer()
        )
    
    def _create_error_response(self, query: str, error_message: str) -> MedicalResponse:
        """Create response for system errors."""
        
        error_answer = (
            "I encountered an error while processing your query. "
            "Please try again or rephrase your question."
        )
        
        safety_check = SafetyCheck(
            is_safe=True,
            violations=[f"System error: {error_message}"],
            requires_disclaimer=True,
            refusal_reason=None
        )
        
        return MedicalResponse(
            query=query,
            answer=error_answer + self.safety_validator.get_educational_disclaimer(),
            citations=[],
            safety_check=safety_check,
            confidence_score=0.0,
            retrieved_documents=[],
            disclaimer=self.safety_validator.get_educational_disclaimer()
        )