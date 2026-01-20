"""Query analysis and intent classification for medical queries."""

import re
from typing import List, Optional, Tuple
from langchain_openai import OpenAI
from langchain_core.prompts import PromptTemplate

from .models import QueryAnalysis, MedicalIntent, PopulationType
from .config import settings


class MedicalQueryAnalyzer:
    """Analyzes medical queries for intent, safety, and decomposition."""
    
    def __init__(self):
        self.llm = OpenAI(
            api_key=settings.openai_api_key,
            temperature=0.0,  # Deterministic for safety
            model="gpt-3.5-turbo-instruct"
        )
        
        # Risk patterns that indicate unsafe queries
        self.risk_patterns = [
            r'\b(should I|what should I|recommend for me|advise me|prescribe for me)\b',
            r'\b(do I have|am I|diagnose me|what do I have)\b',
            r'\b(treat me|treatment for me|cure me|medication for me)\b',
            r'\b(my dosage|how much should I|how often should I)\b',
            r'\b(I have emergency|I have urgent|I have critical)\b'
        ]
        
        # Population indicators
        self.population_patterns = {
            PopulationType.PREGNANT: [r'\b(pregnant|pregnancy|expecting|maternal)\b'],
            PopulationType.PEDIATRIC: [r'\b(child|children|pediatric|infant|baby)\b'],
            PopulationType.ELDERLY: [r'\b(elderly|senior|geriatric|older adult)\b'],
        }
    
    def analyze_query(self, query: str) -> QueryAnalysis:
        """Analyze query for intent, safety, and structure."""
        
        # Step 1: Safety screening
        is_safe, risk_factors = self._safety_screen(query)
        
        # Step 2: Intent classification
        intent = self._classify_intent(query)
        
        # Step 3: Population detection
        population = self._detect_population(query)
        
        # Step 4: Entity extraction
        condition, intervention = self._extract_entities(query)
        
        # Step 5: Query decomposition (if needed)
        decomposed = self._decompose_query(query) if self._needs_decomposition(query) else []
        
        return QueryAnalysis(
            original_query=query,
            intent=intent,
            population=population,
            condition=condition,
            intervention=intervention,
            is_safe=is_safe,
            risk_factors=risk_factors,
            decomposed_queries=decomposed
        )
    
    def _safety_screen(self, query: str) -> Tuple[bool, List[str]]:
        """Screen query for safety violations."""
        risk_factors = []
        
        for pattern in self.risk_patterns:
            if re.search(pattern, query, re.IGNORECASE):
                risk_factors.append(f"Pattern: {pattern}")
        
        # Additional safety checks
        if any(word in query.lower() for word in ['emergency', 'urgent', 'critical']):
            risk_factors.append("Emergency language detected")
        
        is_safe = len(risk_factors) == 0
        return is_safe, risk_factors
    
    def _classify_intent(self, query: str) -> MedicalIntent:
        """Classify the medical intent of the query."""
        
        # Simple rule-based classification to avoid OpenAI API calls
        query_lower = query.lower().strip()
        
        # Handle conversational queries
        conversational_greetings = ['hi', 'hello', 'hey', 'good morning', 'good afternoon', 'good evening']
        conversational_thanks = ['thanks', 'thank you', 'thx', 'appreciate it']
        conversational_responses = ['great', 'good', 'ok', 'okay', 'fine', 'nice', 'cool', 'awesome']
        
        # Check for conversational patterns first, but be more specific
        if query_lower in conversational_greetings or any(greeting == query_lower for greeting in conversational_greetings):
            return MedicalIntent.CONVERSATIONAL
        elif query_lower in conversational_thanks or any(thanks == query_lower for thanks in conversational_thanks):
            return MedicalIntent.CONVERSATIONAL
        elif query_lower in conversational_responses and len(query_lower.split()) <= 2:
            return MedicalIntent.CONVERSATIONAL
        # Medical content queries
        elif any(word in query_lower for word in ['what is', 'define', 'definition', 'meaning']):
            return MedicalIntent.DEFINITION
        elif any(word in query_lower for word in ['recommend', 'should', 'best', 'treatment']):
            return MedicalIntent.RECOMMENDATION
        elif any(word in query_lower for word in ['contraindication', 'avoid', 'not use', 'warning']):
            return MedicalIntent.CONTRAINDICATION
        elif any(word in query_lower for word in ['procedure', 'how to', 'steps', 'process']):
            return MedicalIntent.PROCEDURE
        elif any(word in query_lower for word in ['diagnose', 'do i have', 'am i', 'symptoms']):
            return MedicalIntent.DIAGNOSIS
        elif any(word in query_lower for word in ['treat me', 'cure me', 'medication for me']):
            return MedicalIntent.TREATMENT
        else:
            return MedicalIntent.DEFINITION  # Default to safe intent
    
    def _detect_population(self, query: str) -> Optional[PopulationType]:
        """Detect target population from query."""
        for pop_type, patterns in self.population_patterns.items():
            for pattern in patterns:
                if re.search(pattern, query, re.IGNORECASE):
                    return pop_type
        return PopulationType.GENERAL
    
    def _extract_entities(self, query: str) -> Tuple[Optional[str], Optional[str]]:
        """Extract medical condition and intervention entities."""
        
        # Simple keyword extraction
        condition = None
        intervention = None
        
        # Common medical conditions
        conditions = ['hiv', 'aids', 'hypertension', 'diabetes', 'cancer', 'tuberculosis']
        for cond in conditions:
            if cond in query.lower():
                condition = cond
                break
        
        # Common interventions
        interventions = ['antiretroviral', 'insulin', 'chemotherapy', 'surgery', 'medication']
        for interv in interventions:
            if interv in query.lower():
                intervention = interv
                break
        
        return condition, intervention
    
    def _needs_decomposition(self, query: str) -> bool:
        """Determine if query needs decomposition."""
        # Simple heuristic - complex queries with multiple clauses
        return len(query.split(' and ')) > 1 or len(query.split(' or ')) > 1
    
    def _decompose_query(self, query: str) -> List[str]:
        """Decompose complex queries into simpler sub-queries."""
        
        # Simple decomposition by splitting on 'and' and 'or'
        sub_queries = []
        
        if ' and ' in query:
            parts = query.split(' and ')
            sub_queries.extend([part.strip() for part in parts if part.strip()])
        elif ' or ' in query:
            parts = query.split(' or ')
            sub_queries.extend([part.strip() for part in parts if part.strip()])
        
        return sub_queries if len(sub_queries) > 1 else []