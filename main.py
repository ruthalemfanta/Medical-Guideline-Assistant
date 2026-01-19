"""Main application entry point for the Medical Guideline Assistant."""

import os
import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import tempfile
import shutil

from src.medical_assistant import MedicalGuidelineAssistant
from src.models import MedicalResponse
from src.config import settings

# Initialize FastAPI app
app = FastAPI(
    title="Medical Guideline Assistant",
    description="Educational medical guideline assistant with grounded RAG",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the medical assistant
medical_assistant = MedicalGuidelineAssistant()


class QueryRequest(BaseModel):
    """Request model for medical queries."""
    query: str


class QueryResponse(BaseModel):
    """Response model for medical queries."""
    query: str
    answer: str
    citations: list
    confidence_score: float
    safety_check: dict
    disclaimer: str


@app.get("/")
async def root():
    """Root endpoint with system information."""
    return {
        "message": "Medical Guideline Assistant API",
        "version": "1.0.0",
        "description": "Educational medical guideline assistant",
        "endpoints": {
            "query": "/query",
            "upload": "/upload-guideline",
            "stats": "/stats",
            "health": "/health"
        }
    }


@app.post("/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    """Process a medical query."""
    
    try:
        response = medical_assistant.process_query(request.query)
        
        return QueryResponse(
            query=response.query,
            answer=response.answer,
            citations=[citation.dict() for citation in response.citations],
            confidence_score=response.confidence_score,
            safety_check=response.safety_check.dict(),
            disclaimer=response.disclaimer
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/upload-guideline")
async def upload_guideline(file: UploadFile = File(...)):
    """Upload a new medical guideline document."""
    
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            shutil.copyfileobj(file.file, tmp_file)
            tmp_path = tmp_file.name
        
        # Process the document
        success = medical_assistant.add_guideline_document(tmp_path)
        
        # Clean up temporary file
        os.unlink(tmp_path)
        
        if success:
            return {"message": f"Successfully added guideline: {file.filename}"}
        else:
            raise HTTPException(status_code=500, detail="Failed to process document")
            
    except Exception as e:
        # Clean up on error
        if 'tmp_path' in locals():
            try:
                os.unlink(tmp_path)
            except:
                pass
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/stats")
async def get_stats():
    """Get system statistics."""
    return medical_assistant.get_system_stats()


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "system": "Medical Guideline Assistant",
        "version": "1.0.0"
    }


def main():
    """Main function to run the application."""
    
    print("🏥 Medical Guideline Assistant")
    print("=" * 50)
    print(f"Starting server...")
    print(f"API Documentation: http://localhost:8000/docs")
    print(f"Health Check: http://localhost:8000/health")
    print("=" * 50)
    
    # Run the server
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level=settings.log_level.lower()
    )


if __name__ == "__main__":
    main()