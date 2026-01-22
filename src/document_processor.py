"""Document processing and ingestion for medical guidelines."""

import os
import re
from typing import List, Dict, Any, Optional
from pathlib import Path
import pdfplumber
from datetime import datetime

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

from .models import GuidelineMetadata, ChunkMetadata, PopulationType
from .config import settings


class MedicalDocumentProcessor:
    """Processes medical guideline documents with semantic awareness."""
    
    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        
        # Medical section patterns
        self.section_patterns = {
            'introduction': r'\b(introduction|background|overview)\b',
            'recommendations': r'\b(recommendations?|guidelines?|treatment)\b',
            'contraindications': r'\b(contraindications?|warnings?|precautions?)\b',
            'dosage': r'\b(dosage|dose|administration|posology)\b',
            'adverse_effects': r'\b(adverse|side effects?|reactions?)\b',
            'special_populations': r'\b(special populations?|pregnancy|pediatric|elderly)\b',
            'monitoring': r'\b(monitoring|follow-up|surveillance)\b'
        }
    
    def process_pdf(self, file_path: str, metadata: GuidelineMetadata) -> List[Document]:
        """Process a PDF medical guideline into structured chunks."""
        
        documents = []
        
        print(f"Processing PDF: {file_path}")
        
        with pdfplumber.open(file_path) as pdf:
            print(f"PDF has {len(pdf.pages)} pages")
            
            full_text = ""
            page_texts = {}
            
            # Extract text from each page
            for page_num, page in enumerate(pdf.pages, 1):
                page_text = page.extract_text()
                if page_text:
                    page_texts[page_num] = page_text
                    full_text += f"\n[PAGE {page_num}]\n{page_text}"
                    print(f"Extracted {len(page_text)} chars from page {page_num}")
            
            print(f"Total extracted text: {len(full_text)} characters")
            
            # Extract document structure
            sections = self._extract_sections(full_text)
            print(f"Found {len(sections)} sections: {list(sections.keys())}")
            
            # Process each section
            for section_name, section_content in sections.items():
                print(f"Processing section '{section_name}' ({len(section_content)} chars)")
                
                section_docs = self._process_section(
                    section_content, 
                    section_name, 
                    metadata,
                    page_texts
                )
                
                print(f"Created {len(section_docs)} chunks from section '{section_name}'")
                documents.extend(section_docs)
        
        print(f"Total documents created: {len(documents)}")
        return documents
    
    def _extract_sections(self, text: str) -> Dict[str, str]:
        """Extract sections from document text."""
        sections = {}
        
        # Split by pages first to preserve all content
        pages = text.split('[PAGE ')
        
        for page in pages[1:]:  # Skip first empty split
            if page.strip():
                # Get page number and content
                lines = page.split('\n', 1)
                if len(lines) > 1:
                    page_num = lines[0].split(']')[0]
                    page_content = lines[1] if len(lines) > 1 else lines[0]
                    
                    # Store each page as a section to preserve all content
                    sections[f"page_{page_num}"] = page_content
        
        # If no pages found, treat whole text as one section
        if not sections:
            sections["content"] = text
        
        return sections
    
    def _process_section(
        self, 
        section_content: str, 
        section_name: str, 
        metadata: GuidelineMetadata,
        page_texts: Dict[int, str]
    ) -> List[Document]:
        """Process a section into chunks with metadata."""
        
        # Only skip if content is too short
        if len(section_content.strip()) < 50:
            return []
        
        # Split section into chunks
        chunks = self.text_splitter.split_text(section_content)
        documents = []
        
        for i, chunk in enumerate(chunks):
            # Skip very short chunks
            if len(chunk.strip()) < 30:
                continue
                
            # Find page number for this chunk
            page_num = self._find_page_number(chunk, page_texts)
            
            # Detect population type
            population = self._detect_population_in_text(chunk)
            
            # Create chunk metadata
            chunk_metadata = ChunkMetadata(
                guideline=metadata.guideline_name,
                section=section_name,
                population=population,
                page_number=page_num,
                chunk_id=f"{metadata.guideline_name}_{section_name}_{i}",
                guideline_metadata=metadata
            )
            
            # Create document
            doc = Document(
                page_content=chunk,
                metadata=chunk_metadata.dict()
            )
            documents.append(doc)
        
        return documents
    
    def _find_page_number(self, chunk: str, page_texts: Dict[int, str]) -> Optional[int]:
        """Find the page number where this chunk appears."""
        for page_num, page_text in page_texts.items():
            if chunk[:100] in page_text:  # Check first 100 chars
                return page_num
        return None
    
    def _detect_population_in_text(self, text: str) -> PopulationType:
        """Detect population type from text content."""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ['pregnant', 'pregnancy', 'maternal']):
            return PopulationType.PREGNANT
        elif any(word in text_lower for word in ['pediatric', 'children', 'infant']):
            return PopulationType.PEDIATRIC
        elif any(word in text_lower for word in ['elderly', 'geriatric', 'older adult']):
            return PopulationType.ELDERLY
        else:
            return PopulationType.GENERAL
    
    def extract_metadata_from_pdf(self, file_path: str) -> GuidelineMetadata:
        """Extract metadata from PDF document."""
        
        with pdfplumber.open(file_path) as pdf:
            # Get first few pages for metadata extraction
            first_pages = ""
            for page in pdf.pages[:3]:  # First 3 pages usually contain metadata
                page_text = page.extract_text()
                if page_text:
                    first_pages += page_text + "\n"
        
        # Extract organization
        organization = self._extract_organization(first_pages)
        
        # Extract year
        year = self._extract_year(first_pages)
        
        # Extract guideline name
        guideline_name = self._extract_guideline_name(first_pages, file_path)
        
        return GuidelineMetadata(
            guideline_name=guideline_name,
            organization=organization,
            publication_year=year,
            last_updated=datetime.now()
        )
    
    def _extract_organization(self, text: str) -> str:
        """Extract organization from document text."""
        text_upper = text.upper()
        
        # Check for known organizations
        orgs = ['WHO', 'CDC', 'NICE', 'AHA', 'ESC', 'ACP', 'USPSTF']
        for org in orgs:
            if org in text_upper:
                return org
        
        return "Unknown"
    
    def _extract_year(self, text: str) -> int:
        """Extract publication year from text."""
        # Look for 4-digit years
        years = re.findall(r'\b(20\d{2})\b', text)
        if years:
            return int(max(years))  # Return most recent year
        return datetime.now().year
    
    def _extract_guideline_name(self, text: str, file_path: str) -> str:
        """Extract guideline name from text or filename."""
        # Try to extract from first line or title
        lines = text.split('\n')[:10]  # First 10 lines
        
        for line in lines:
            line = line.strip()
            if len(line) > 20 and len(line) < 200:  # Reasonable title length
                if any(word in line.lower() for word in ['guideline', 'recommendation', 'standard']):
                    return line
        
        # Fallback to filename
        return Path(file_path).stem