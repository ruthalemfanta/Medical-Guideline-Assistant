# Educational Medical Guideline Assistant

A research-grade RAG system for answering questions strictly grounded in official medical guidelines (WHO, CDC, NICE, etc.) with zero improvisation.

## 🎯 Core Principles

- **Safety First**: No medical advice outside documents, no diagnosis/prescriptions
- **Document Grounded**: Every answer must be traceable to source guidelines
- **Educational Only**: Explicit disclaimers and educational focus
- **Precise Citations**: Exact guideline sections with page numbers

## 🏗️ Architecture

Modern multi-stage RAG pipeline:
1. Intent & Risk Classification
2. Query Decomposition
3. Hybrid + Structured Retrieval
4. Evidence Validation & Reranking
5. Grounded Answer Synthesis
6. Consistency & Safety Check

## 🚀 Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Edit .env with your OpenAI API key

# Run the API server
python main.py

# Or use the CLI
python cli.py --query "What is hypertension according to WHO?"
```

## 📁 Project Structure

```
medical-guideline-assistant/
├── src/                    # Core system components
│   ├── medical_assistant.py   # Main orchestrator
│   ├── query_analyzer.py      # Intent classification & safety
│   ├── retrieval_system.py    # Hybrid retrieval
│   ├── answer_generator.py    # Grounded synthesis
│   ├── safety_validator.py    # Safety validation
│   ├── document_processor.py  # Document ingestion
│   ├── models.py              # Data models
│   └── config.py              # Configuration
├── examples/               # Usage examples
├── tests/                 # Test suite
├── docs/                  # Documentation
├── config/                # Sample configurations
├── main.py               # API server
├── cli.py                # Command-line interface
└── requirements.txt      # Dependencies
```

## 🔧 Features

### Safety-First Design
- Multi-layer safety validation
- Intent-based query classification
- Unsafe language detection
- Automatic refusal for medical advice

### Intelligent Retrieval
- Hybrid dense + sparse search
- Medical-aware reranking
- Population-specific filtering
- Section-based relevance

### Grounded Generation
- Evidence-only responses
- Automatic citation extraction
- Confidence scoring
- Educational disclaimers

### Document Processing
- Semantic section extraction
- Medical metadata preservation
- Population-aware chunking
- Guideline organization detection

## 📖 Usage Examples

### API Usage
```bash
curl -X POST "http://localhost:8000/query" \
     -H "Content-Type: application/json" \
     -d '{"query": "What does WHO recommend for hypertension treatment?"}'
```

### Python SDK
```python
from src.medical_assistant import MedicalGuidelineAssistant

assistant = MedicalGuidelineAssistant()
response = assistant.process_query("What is diabetes?")

print(f"Answer: {response.answer}")
print(f"Confidence: {response.confidence_score}")
print(f"Citations: {len(response.citations)}")
```

### CLI Interface
```bash
# Interactive mode
python cli.py --interactive

# Single query
python cli.py --query "What are ACE inhibitor contraindications?"

# Add guideline document
python cli.py --add-document guidelines/who_hypertension_2023.pdf
```

## 🛡️ Safety Features

### Query Safety
- ✅ Educational questions: "What is hypertension?"
- ❌ Medical advice: "Should I take this medication?"
- ❌ Diagnosis: "Do I have diabetes?"
- ❌ Emergency: "I'm having chest pain"

### Response Safety
- Evidence grounding validation
- Citation requirement
- Educational disclaimers
- Confidence assessment

## 📊 System Components

| Component | Purpose | Key Features |
|-----------|---------|--------------|
| Query Analyzer | Intent classification & safety | Risk detection, entity extraction |
| Retrieval System | Document retrieval | Hybrid search, medical reranking |
| Answer Generator | Response synthesis | Grounded generation, citations |
| Safety Validator | Response validation | Multi-layer safety checks |
| Document Processor | Guideline ingestion | Semantic parsing, metadata |

## 🔬 Evaluation Metrics

- **Document Consistency**: Answers traceable to sources
- **Citation Correctness**: Accurate guideline references  
- **Refusal Accuracy**: Proper unsafe query handling
- **Hallucination Rate**: Zero unsupported claims
- **Educational Compliance**: Appropriate disclaimers

## 📚 Documentation

- [Architecture Guide](docs/ARCHITECTURE.md) - System design and components
- [Usage Guide](docs/USAGE.md) - Detailed usage instructions
- [API Documentation](http://localhost:8000/docs) - Interactive API docs

## 🧪 Testing

```bash
# Run safety validator tests
python tests/test_safety_validator.py

# Run example usage
python examples/example_usage.py
```

## 🔧 Configuration

Key environment variables:
- `OPENAI_API_KEY`: Required for LLM operations
- `ENABLE_SAFETY_CHECKS`: Enable/disable safety validation
- `REQUIRE_CITATIONS`: Require citations in responses
- `EDUCATIONAL_DISCLAIMER`: Add educational disclaimers

## ⚠️ Important Disclaimer

This system is for educational purposes only. It does not provide medical advice, diagnosis, or treatment recommendations. Always consult qualified healthcare professionals for medical decisions.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure safety compliance
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details.