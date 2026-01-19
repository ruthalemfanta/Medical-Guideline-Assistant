# Medical Guideline Assistant - Architecture

## Overview

The Medical Guideline Assistant is a research-grade RAG (Retrieval-Augmented Generation) system designed specifically for educational medical applications. It follows a multi-stage pipeline with strong safety constraints.

## Core Design Principles

### 🔒 Safety First
- No medical advice outside documents
- No diagnosis or prescriptions
- Explicit educational disclaimers
- Cite exact guideline sections

### 🎯 Intelligence Goals
- Correct guideline selection
- Precise citation
- Handle ambiguous questions safely
- Refuse when evidence is missing

## System Architecture

```
User Query
    ↓
Intent & Risk Classifier
    ↓
Query Decomposition
    ↓
Hybrid + Structured Retrieval
    ↓
Evidence Validation & Reranking
    ↓
Grounded Answer Synthesis
    ↓
Consistency & Safety Check
    ↓
Final Response
```

## Components

### 1. Query Analyzer (`query_analyzer.py`)
- **Intent Classification**: Categorizes queries into safe/unsafe intents
- **Safety Screening**: Detects risky patterns and language
- **Entity Extraction**: Identifies medical conditions and interventions
- **Query Decomposition**: Breaks complex queries into sub-questions

**Key Features:**
- Risk pattern detection
- Population type identification
- Medical entity recognition
- Complex query handling

### 2. Document Processor (`document_processor.py`)
- **Semantic Parsing**: Extracts document structure and sections
- **Intelligent Chunking**: Creates medically-aware chunks
- **Metadata Extraction**: Preserves guideline context
- **Population Detection**: Identifies target populations

**Key Features:**
- Section-aware chunking
- Medical metadata preservation
- Population-specific content tagging
- Guideline organization detection

### 3. Retrieval System (`retrieval_system.py`)
- **Hybrid Retrieval**: Combines dense (semantic) and sparse (BM25) search
- **Metadata Filtering**: Applies population and section filters
- **Medical Reranking**: Prioritizes guideline content over commentary
- **Evidence Validation**: Ensures retrieved content is relevant

**Key Features:**
- Dense + sparse retrieval combination
- Medical-aware reranking
- Population-based filtering
- Section relevance scoring

### 4. Answer Generator (`answer_generator.py`)
- **Grounded Synthesis**: Generates answers strictly from evidence
- **Intent-Aware Generation**: Adapts response style to query type
- **Citation Extraction**: Identifies supporting quotes
- **Confidence Scoring**: Assesses answer reliability

**Key Features:**
- Evidence-grounded generation
- Intent-specific templates
- Automatic citation extraction
- Multi-factor confidence scoring

### 5. Safety Validator (`safety_validator.py`)
- **Response Validation**: Checks generated answers for safety
- **Evidence Grounding**: Ensures all claims are supported
- **Language Screening**: Detects unsafe advisory language
- **Refusal Generation**: Creates appropriate refusal responses

**Key Features:**
- Multi-layer safety validation
- Evidence-claim verification
- Unsafe language detection
- Educational disclaimer management

### 6. Medical Assistant (`medical_assistant.py`)
- **Pipeline Orchestration**: Coordinates all components
- **Error Handling**: Manages system failures gracefully
- **Response Assembly**: Creates final structured responses
- **System Management**: Handles document ingestion and stats

## Data Models

### Core Models (`models.py`)
- `QueryAnalysis`: Query intent and safety analysis
- `RetrievedDocument`: Document with relevance scoring
- `Citation`: Structured citation information
- `SafetyCheck`: Safety validation results
- `MedicalResponse`: Complete system response

### Metadata Models
- `GuidelineMetadata`: Document-level metadata
- `ChunkMetadata`: Chunk-level context preservation
- `PopulationType`: Target population enumeration
- `MedicalIntent`: Query intent classification

## Safety Architecture

### Multi-Layer Safety
1. **Query Analysis**: Pre-screening for unsafe intents
2. **Intent Classification**: Categorizing query types
3. **Response Validation**: Post-generation safety checks
4. **Evidence Grounding**: Claim-evidence verification
5. **Language Screening**: Unsafe pattern detection

### Refusal Mechanisms
- Intent-based refusal (diagnosis, treatment)
- Risk pattern detection
- Evidence insufficiency handling
- Graceful error responses

## Retrieval Strategy

### Hybrid Approach
- **Dense Retrieval**: Semantic similarity using embeddings
- **Sparse Retrieval**: Keyword matching with BM25
- **Metadata Filtering**: Population and section constraints
- **Medical Reranking**: Domain-specific relevance scoring

### Evidence Validation
- Document relevance scoring
- Section appropriateness checking
- Population alignment verification
- Guideline authority assessment

## Answer Generation Strategy

### Grounded Synthesis
- Strict evidence adherence
- Quote-based responses
- Citation requirement
- Confidence assessment

### Intent-Aware Templates
- Definition responses
- Recommendation explanations
- Contraindication warnings
- Procedure descriptions

## Evaluation Metrics

### Safety Metrics
- Refusal accuracy for unsafe queries
- Citation correctness
- Evidence grounding rate
- Disclaimer compliance

### Quality Metrics
- Answer relevance
- Citation accuracy
- Confidence calibration
- Response completeness

## Scalability Considerations

### Document Processing
- Batch processing capabilities
- Incremental index updates
- Metadata preservation
- Version management

### Retrieval Optimization
- Vector index optimization
- Caching strategies
- Query optimization
- Load balancing

## Future Enhancements

### Advanced Features
- Multi-language support
- Guideline version comparison
- Conflict detection
- Update notifications

### Integration Capabilities
- EHR system integration
- Clinical decision support
- Educational platform APIs
- Mobile applications