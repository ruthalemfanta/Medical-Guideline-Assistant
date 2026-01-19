"""Safety validation and evidence checking for medical responses."""

import re
from typing import List, Dict, Any, Tuple
from langchain_openai import OpenAI
from langchain_core.prompts import PromptTemplate

from .models import SafetyCheck, RetrievedDocument, QueryAnalysis, MedicalIntent
from .config import settings


class MedicalSafetyValidator:
    """Validates medical responses for safety and evidence grounding."""
    
    def __init__(self):
        # Skip OpenAI for now to avoid API costs
        self.llm = None
        
        # Unsafe response patterns
        self.unsafe_patterns = [
            r'\b(you should take|I recommend you|take this medication|do this treatment)\b',
            r'\b(you have|I diagnose you|you are diagnosed)\b',
            r'\b(I prescribe|take this prescription|this medication for you)\b',
            r'\b(this is an emergency|call 911|go to ER immediately)\b',
            r'\b(definitely take|certainly use|absolutely do)\b'  # Overconfident language
        ]
        
        # Required disclaimer triggers
        self.disclaimer_triggers = [
            'medication', 'drug', 'treatment', 'therapy', 'procedure'
        ]
    
    def validate_response(
        self, 
        query_analysis: QueryAnalysis,
        answer: str,
        retrieved_docs: List[RetrievedDocument]
    ) -> SafetyCheck:
        """Comprehensive safety validation of medical response."""
        
        violations = []
        is_safe = True
        refusal_reason = None
        
        # Step 1: Check for unsafe query intent
        if query_analysis.intent in [MedicalIntent.DIAGNOSIS, MedicalIntent.TREATMENT]:
            is_safe = False
            refusal_reason = f"Cannot provide {query_analysis.intent.value} - outside educational scope"
            violations.append(f"Unsafe intent: {query_analysis.intent.value}")
        
        # Step 2: Check for unsafe language patterns
        unsafe_language = self._check_unsafe_language(answer)
        if unsafe_language:
            violations.extend(unsafe_language)
            is_safe = False
        
        # Step 3: Determine if disclaimer is required
        requires_disclaimer = self._requires_disclaimer(answer, query_analysis)
        
        # Step 4: Final safety decision
        if not query_analysis.is_safe:
            is_safe = False
            refusal_reason = "Query flagged as unsafe during analysis"
            violations.extend(query_analysis.risk_factors)
        
        return SafetyCheck(
            is_safe=is_safe,
            violations=violations,
            requires_disclaimer=requires_disclaimer,
            refusal_reason=refusal_reason
        )
    
    def _check_unsafe_language(self, answer: str) -> List[str]:
        """Check for unsafe language patterns in response."""
        violations = []
        
        for pattern in self.unsafe_patterns:
            if re.search(pattern, answer, re.IGNORECASE):
                violations.append(f"Unsafe language pattern: {pattern}")
        
        return violations
    
    def _validate_evidence_grounding(
        self, 
        answer: str, 
        retrieved_docs: List[RetrievedDocument]
    ) -> List[str]:
        """Validate that answer is grounded in retrieved evidence."""
        
        if not retrieved_docs:
            return ["No evidence documents provided"]
        
        violations = []
        
        # Simple check: ensure answer contains content from retrieved docs
        answer_lower = answer.lower()
        found_evidence = False
        
        for doc in retrieved_docs:
            doc_words = set(doc.content.lower().split())
            answer_words = set(answer_lower.split())
            
            # Check for word overlap
            overlap = len(doc_words.intersection(answer_words))
            if overlap >= 5:  # At least 5 words in common
                found_evidence = True
                break
        
        if not found_evidence:
            violations.append("Answer does not appear to be grounded in retrieved evidence")
        
        return violations
    
    def _extract_claims(self, answer: str) -> List[str]:
        """Extract factual claims from answer."""
        
        prompt = PromptTemplate(
            input_variables=["answer"],
            template="""
            Extract the main factual claims from this medical answer.
            List each claim on a separate line.
            
            Answer: {answer}
            
            Claims:
            """
        )
        
        response = self.llm(prompt.format(answer=answer))
        
        claims = []
        for line in response.strip().split('\n'):
            line = line.strip()
            if line and not line.startswith('Claims:'):
                # Remove bullet points or numbers
                claim = re.sub(r'^[-•\d\.]\s*', '', line)
                if claim:
                    claims.append(claim)
        
        return claims
    
    def _is_claim_supported(
        self, 
        claim: str, 
        retrieved_docs: List[RetrievedDocument]
    ) -> bool:
        """Check if a claim is supported by retrieved documents."""
        
        # Combine all retrieved content
        evidence_text = "\n".join([doc.content for doc in retrieved_docs])
        
        prompt = PromptTemplate(
            input_variables=["claim", "evidence"],
            template="""
            Is the following claim supported by the evidence?
            Answer only "YES" or "NO".
            
            Claim: {claim}
            
            Evidence: {evidence}
            
            Supported:
            """
        )
        
        response = self.llm(prompt.format(claim=claim, evidence=evidence_text))
        return response.strip().upper() == "YES"
    
    def _check_confidence_level(self, answer: str) -> List[str]:
        """Check for overconfident language."""
        violations = []
        
        overconfident_words = [
            'always', 'never', 'definitely', 'certainly', 'absolutely',
            'guaranteed', 'proven', 'without doubt'
        ]
        
        for word in overconfident_words:
            if word in answer.lower():
                violations.append(f"Overconfident language: '{word}'")
        
        return violations
    
    def _requires_disclaimer(
        self, 
        answer: str, 
        query_analysis: QueryAnalysis
    ) -> bool:
        """Determine if response requires medical disclaimer."""
        
        # Always require disclaimer for medical content
        if settings.educational_disclaimer:
            return True
        
        # Check for specific triggers
        answer_lower = answer.lower()
        for trigger in self.disclaimer_triggers:
            if trigger in answer_lower:
                return True
        
        # Check intent type
        if query_analysis.intent in [
            MedicalIntent.RECOMMENDATION, 
            MedicalIntent.CONTRAINDICATION,
            MedicalIntent.PROCEDURE
        ]:
            return True
        
        return False
    
    def generate_refusal_response(self, safety_check: SafetyCheck) -> str:
        """Generate appropriate refusal response."""
        
        base_refusal = (
            "I cannot provide that type of medical information. "
            "This system is designed for educational purposes only and provides "
            "information from medical guidelines, not personal medical advice."
        )
        
        if safety_check.refusal_reason:
            if "diagnosis" in safety_check.refusal_reason.lower():
                return (
                    f"{base_refusal}\n\n"
                    "For diagnostic questions, please consult with a qualified "
                    "healthcare professional who can evaluate your specific situation."
                )
            elif "treatment" in safety_check.refusal_reason.lower():
                return (
                    f"{base_refusal}\n\n"
                    "For treatment recommendations, please consult with a qualified "
                    "healthcare professional who can assess your individual needs."
                )
        
        return (
            f"{base_refusal}\n\n"
            "I can help you understand what medical guidelines say about "
            "conditions, procedures, and general recommendations for educational purposes."
        )
    
    def get_educational_disclaimer(self) -> str:
        """Get standard educational disclaimer."""
        return (
            "\n\n⚠️ **Educational Disclaimer**: This information is for educational "
            "purposes only and is based on medical guidelines. It is not intended "
            "as medical advice, diagnosis, or treatment recommendations. Always "
            "consult qualified healthcare professionals for medical decisions."
        )