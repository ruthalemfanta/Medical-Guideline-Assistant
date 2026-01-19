# Medical Guideline Assistant - Usage Guide

## Quick Start

### 1. Installation

```bash
# Clone the repository
git clone https://github.com/medical-ai/guideline-assistant.git
cd guideline-assistant

# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Edit .env with your OpenAI API key
```

### 2. Basic Usage

#### API Server
```bash
# Start the API server
python main.py

# The server will be available at:
# - API: http://localhost:8000
# - Documentation: http://localhost:8000/docs
```

#### Command Line Interface
```bash
# Ask a question
python cli.py --query "What is hypertension according to WHO?"

# Add a guideline document
python cli.py --add-document path/to/guideline.pdf

# Interactive mode
python cli.py --interactive

# Show system statistics
python cli.py --stats
```

## API Usage

### Query Endpoint

**POST** `/query`

```json
{
  "query": "What does WHO recommend for hypertension treatment?"
}
```

**Response:**
```json
{
  "query": "What does WHO recommend for hypertension treatment?",
  "answer": "According to WHO Hypertension Guidelines (2023), first-line treatment for adults includes...",
  "citations": [
    {
      "guideline_name": "WHO Hypertension Guidelines 2023",
      "section": "Treatment Recommendations",
      "page_number": 42,
      "organization": "WHO",
      "year": 2023,
      "quote": "First-line treatment for adults with confirmed hypertension..."
    }
  ],
  "confidence_score": 0.85,
  "safety_check": {
    "is_safe": true,
    "violations": [],
    "requires_disclaimer": true,
    "refusal_reason": null
  },
  "disclaimer": "⚠️ Educational Disclaimer: This information is for educational purposes only..."
}
```

### Upload Guideline

**POST** `/upload-guideline`

Upload a PDF medical guideline document.

```bash
curl -X POST "http://localhost:8000/upload-guideline" \
     -H "accept: application/json" \
     -H "Content-Type: multipart/form-data" \
     -F "file=@who_hypertension_2023.pdf"
```

## Example Queries

### ✅ Safe Educational Queries

```python
# Definitions
"What is hypertension according to WHO guidelines?"
"How is diabetes defined in CDC guidelines?"

# General recommendations
"What does WHO recommend for hypertension treatment?"
"What are the screening guidelines for diabetes?"

# Contraindications
"What are the contraindications for ACE inhibitors?"
"When should metformin be avoided?"

# Procedures
"How is blood pressure measured according to guidelines?"
"What is the protocol for diabetes screening?"
```

### ❌ Unsafe Queries (Will Be Refused)

```python
# Personal medical advice
"Should I take this medication?"
"What treatment do you recommend for me?"

# Diagnosis
"Do I have diabetes?"
"What's wrong with my symptoms?"

# Emergency situations
"I'm having chest pain, what should I do?"
"Is this an emergency?"
```

## Python SDK Usage

```python
from src.medical_assistant import MedicalGuidelineAssistant

# Initialize the assistant
assistant = MedicalGuidelineAssistant()

# Add a guideline document
success = assistant.add_guideline_document("path/to/guideline.pdf")

# Process a query
response = assistant.process_query("What is hypertension?")

# Access response components
print(f"Answer: {response.answer}")
print(f"Confidence: {response.confidence_score}")
print(f"Safe: {response.safety_check.is_safe}")

# Access citations
for citation in response.citations:
    print(f"Source: {citation.guideline_name}")
    print(f"Section: {citation.section}")
    print(f"Quote: {citation.quote}")
```

## Configuration

### Environment Variables

```bash
# Required
OPENAI_API_KEY=your_openai_api_key_here

# Optional
CHROMA_PERSIST_DIRECTORY=./data/chroma_db
MAX_RETRIEVAL_DOCS=10
RERANK_TOP_K=5
LOG_LEVEL=INFO
ENABLE_SAFETY_CHECKS=true
REQUIRE_CITATIONS=true
EDUCATIONAL_DISCLAIMER=true
```

### Supported Document Formats

- **PDF**: Medical guideline documents
- **Organizations**: WHO, CDC, NICE, AHA, ESC, ACP, USPSTF

### System Requirements

- Python 3.8+
- OpenAI API key
- 4GB+ RAM (for vector embeddings)
- 1GB+ disk space (for document storage)

## Safety Features

### Query Safety
- Intent classification (safe vs unsafe)
- Risk pattern detection
- Population-specific filtering
- Emergency language detection

### Response Safety
- Evidence grounding validation
- Unsafe language screening
- Overconfidence detection
- Mandatory disclaimers

### Refusal Mechanisms
- Diagnosis requests → Refused
- Treatment advice → Refused
- Emergency situations → Refused
- Insufficient evidence → Acknowledged

## Best Practices

### For Educators
1. Use for teaching medical concepts
2. Always include disclaimers
3. Encourage critical thinking
4. Supplement with official sources

### For Students
1. Use for understanding guidelines
2. Don't rely for clinical decisions
3. Verify with primary sources
4. Discuss with instructors

### For Developers
1. Monitor safety metrics
2. Regular guideline updates
3. User feedback integration
4. Performance optimization

## Troubleshooting

### Common Issues

**No results for query**
- Check if relevant guidelines are loaded
- Try more specific queries
- Verify document processing succeeded

**Low confidence scores**
- Add more relevant documents
- Check query specificity
- Review retrieval settings

**Safety violations**
- Review query phrasing
- Avoid personal medical language
- Use educational framing

### Logging

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# This will show detailed processing steps
```

### Performance Optimization

```python
# Batch document processing
documents = ["doc1.pdf", "doc2.pdf", "doc3.pdf"]
for doc in documents:
    assistant.add_guideline_document(doc)

# Adjust retrieval parameters
settings.max_retrieval_docs = 15
settings.rerank_top_k = 8
```

## Integration Examples

### Web Application
```javascript
// Frontend query
const response = await fetch('/query', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ query: userQuestion })
});

const result = await response.json();
displayAnswer(result.answer, result.citations);
```

### Educational Platform
```python
class MedicalEducationBot:
    def __init__(self):
        self.assistant = MedicalGuidelineAssistant()
    
    def answer_student_question(self, question):
        response = self.assistant.process_query(question)
        
        if not response.safety_check.is_safe:
            return self.educational_redirect(response)
        
        return self.format_educational_response(response)
```

## Support

For technical support, feature requests, or bug reports:
- GitHub Issues: [github.com/medical-ai/guideline-assistant/issues]
- Documentation: [docs.medical-ai.com]
- Email: support@medical-ai.com