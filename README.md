# Medical Guideline Assistant

A complete full-stack RAG system with React frontend for answering questions strictly grounded in official medical guidelines (WHO, CDC, NICE, etc.) with zero improvisation.

## 🎯 Core Principles

- **Safety First**: No medical advice outside documents, no diagnosis/prescriptions
- **Document Grounded**: Every answer must be traceable to source guidelines
- **Educational Only**: Explicit disclaimers and educational focus
- **Precise Citations**: Exact guideline sections with page numbers

## 🚀 Quick Start

### Automated Setup (Recommended)
```bash
python setup.py
```

### Manual Setup
```bash
# Backend
python -m venv medical-assistant-env
source medical-assistant-env/bin/activate  # On Windows: medical-assistant-env\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your OpenAI API key
python main.py

# Frontend (in another terminal)
cd guideline-helper
npm install
npm run dev
```

### Start Both Servers
```bash
python start.py
```

### Access the Application
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## 🏗️ Architecture

### Backend (Python/FastAPI)
1. Intent & Risk Classification
2. Query Decomposition  
3. Hybrid + Structured Retrieval
4. Evidence Validation & Reranking
5. Grounded Answer Synthesis
6. Consistency & Safety Check

### Frontend (React/TypeScript)
- Modern chat interface with real-time messaging
- Drag & drop document upload
- Citation display with confidence scoring
- Backend connection monitoring
- Responsive design with dark/light themes

## 📁 Project Structure

```
medical-guideline-assistant/
├── src/                           # Backend Python code
│   ├── medical_assistant.py      # Main orchestrator
│   ├── query_analyzer.py         # Intent classification & safety
│   ├── retrieval_system.py       # Hybrid retrieval
│   ├── answer_generator.py       # Grounded synthesis
│   ├── safety_validator.py       # Safety validation
│   ├── document_processor.py     # Document ingestion
│   ├── models.py                 # Data models
│   └── config.py                 # Configuration
├── guideline-helper/             # React frontend
│   ├── src/
│   │   ├── components/           # UI components
│   │   ├── hooks/               # Custom React hooks
│   │   ├── services/            # API integration
│   │   └── pages/               # Application pages
│   └── package.json
├── data/                         # Document storage
├── main.py                       # FastAPI server
├── cli.py                        # Command-line interface
├── setup.py                      # Automated setup script
├── start.py                      # Start both servers
├── test_integration.py           # Integration tests
└── requirements.txt              # Python dependencies
```

## 🔧 Features

### Full-Stack Integration
- **Real-time Chat**: Conversational interface with medical query handling
- **Document Management**: Upload, track, and manage PDF guidelines
- **Status Monitoring**: Real-time backend connection status
- **Error Handling**: Comprehensive error handling and user feedback

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

### Modern UI/UX
- Responsive design for all devices
- Drag & drop file uploads
- Real-time typing indicators
- Confidence score visualization
- Clean citation display

## 📖 Usage Examples

### Web Interface
1. Start servers: `python start.py`
2. Open http://localhost:5173
3. Upload medical guideline PDFs via drag & drop
4. Ask questions like:
   - "Hi" → Friendly conversational response
   - "What are WHO guidelines for hypertension?" → Medical answer with citations
   - "Thanks" → Acknowledgment

### API Usage
```bash
curl -X POST "http://localhost:8000/query" \
     -H "Content-Type: application/json" \
     -d '{"query": "What does WHO recommend for hypertension treatment?"}'
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
- ✅ Conversational: "Hi", "Thanks", "Great"
- ❌ Medical advice: "Should I take this medication?"
- ❌ Diagnosis: "Do I have diabetes?"
- ❌ Emergency: "I'm having chest pain"

### Response Safety
- Evidence grounding validation
- Citation requirement
- Educational disclaimers
- Confidence assessment

## 🧪 Testing

### Integration Tests
```bash
python test_integration.py
```

### Manual Testing
```bash
# Start backend
python main.py

# In another terminal, start frontend
cd guideline-helper && npm run dev

# Test full workflow in browser
```

## 🔧 Configuration

### Backend Environment (.env)
```env
OPENAI_API_KEY=your_openai_api_key_here
ENABLE_SAFETY_CHECKS=true
REQUIRE_CITATIONS=true
LOG_LEVEL=INFO
```

### Frontend Configuration
- API base URL in `guideline-helper/src/services/api.ts`
- Theme settings in `guideline-helper/src/components/ui/`

## 🚨 Troubleshooting

### Common Issues
1. **Backend not available**: Check if Python server is running on port 8000
2. **Upload failures**: Ensure files are PDF format and < 50MB
3. **No responses**: Verify OpenAI API key and uploaded documents
4. **CORS errors**: Check backend CORS configuration

### Debug Mode
```bash
# Backend debug logging
export LOG_LEVEL=DEBUG
python main.py

# Frontend debug mode
cd guideline-helper
npm run dev -- --debug
```

## ⚠️ Important Disclaimer

This system is for educational purposes only. It does not provide medical advice, diagnosis, or treatment recommendations. Always consult qualified healthcare professionals for medical decisions.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure safety compliance
5. Test both frontend and backend
6. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details.