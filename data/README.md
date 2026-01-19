# Data Directory Structure

This directory contains all data files for the Medical Guideline Assistant.

## Directory Structure

```
data/
├── guidelines/          # Medical guideline PDF documents
│   ├── who/            # WHO guidelines
│   ├── cdc/            # CDC guidelines
│   ├── nice/           # NICE guidelines
│   └── other/          # Other organization guidelines
├── chroma_db/          # Vector database (auto-created)
├── processed/          # Processed document chunks (auto-created)
└── logs/              # System logs (auto-created)
```

## Adding Medical Guidelines

### 1. PDF Documents
Place your medical guideline PDF files in the appropriate subdirectories:

**WHO Guidelines** → `data/guidelines/who/`
- `who_hypertension_2023.pdf`
- `who_diabetes_2022.pdf`
- `who_cardiovascular_2023.pdf`

**CDC Guidelines** → `data/guidelines/cdc/`
- `cdc_diabetes_screening_2023.pdf`
- `cdc_vaccination_2023.pdf`
- `cdc_preventive_care_2023.pdf`

**NICE Guidelines** → `data/guidelines/nice/`
- `nice_hypertension_2022.pdf`
- `nice_diabetes_2022.pdf`

**Other Organizations** → `data/guidelines/other/`
- `aha_heart_disease_2023.pdf`
- `esc_cardiology_2023.pdf`

### 2. Supported Formats
- **Primary**: PDF documents
- **Organizations**: WHO, CDC, NICE, AHA, ESC, ACP, USPSTF
- **Languages**: English (primary support)

### 3. File Naming Convention
Use descriptive names that include:
- Organization (who, cdc, nice)
- Topic (hypertension, diabetes)
- Year (2023, 2022)

Example: `who_hypertension_guidelines_2023.pdf`

## Auto-Created Directories

These directories are created automatically by the system:

### `chroma_db/`
- Vector embeddings database
- Automatically managed by ChromaDB
- Contains indexed document chunks

### `processed/`
- Processed document metadata
- Chunk information
- Processing logs

### `logs/`
- System operation logs
- Error logs
- Processing statistics

## Data Management

### Adding Documents via CLI
```bash
# Add a single document
python cli.py --add-document data/guidelines/who/who_hypertension_2023.pdf

# The system will automatically:
# 1. Extract metadata
# 2. Process into chunks
# 3. Add to vector database
# 4. Make available for queries
```

### Adding Documents via API
```bash
curl -X POST "http://localhost:8000/upload-guideline" \
     -H "Content-Type: multipart/form-data" \
     -F "file=@data/guidelines/who/who_hypertension_2023.pdf"
```

### Batch Processing
```python
import os
from src.medical_assistant import MedicalGuidelineAssistant

assistant = MedicalGuidelineAssistant()

# Process all PDFs in a directory
guidelines_dir = "data/guidelines/who"
for filename in os.listdir(guidelines_dir):
    if filename.endswith('.pdf'):
        file_path = os.path.join(guidelines_dir, filename)
        success = assistant.add_guideline_document(file_path)
        print(f"Processed {filename}: {'✅' if success else '❌'}")
```

## Storage Requirements

### Disk Space
- **PDF Documents**: ~1-10MB per guideline
- **Vector Database**: ~2-5x PDF size
- **Processed Data**: ~0.5x PDF size
- **Total**: ~4-16x original PDF size

### Example Calculation
- 50 PDF guidelines @ 5MB each = 250MB
- Vector database = ~750MB
- Processed data = ~125MB
- **Total storage needed**: ~1.1GB

## Data Security

### Local Storage
- All data stored locally
- No external data transmission
- HIPAA-compliant local processing

### Access Control
- File system permissions
- No network exposure of raw data
- API-only access to processed information

## Backup Recommendations

### What to Backup
1. **Original PDFs**: `data/guidelines/`
2. **Vector Database**: `data/chroma_db/`
3. **Configuration**: `.env` file

### Backup Script Example
```bash
#!/bin/bash
# backup_data.sh

DATE=$(date +%Y%m%d)
BACKUP_DIR="backups/medical_assistant_$DATE"

mkdir -p $BACKUP_DIR

# Backup guidelines
cp -r data/guidelines/ $BACKUP_DIR/

# Backup vector database
cp -r data/chroma_db/ $BACKUP_DIR/

# Backup configuration
cp .env $BACKUP_DIR/

echo "Backup completed: $BACKUP_DIR"
```

## Troubleshooting

### Common Issues

**"No documents found"**
- Check file paths in `data/guidelines/`
- Verify PDF files are not corrupted
- Check file permissions

**"Processing failed"**
- Ensure PDFs are text-based (not scanned images)
- Check available disk space
- Review logs in `data/logs/`

**"Vector database error"**
- Delete `data/chroma_db/` to reset
- Restart document processing
- Check ChromaDB permissions

### Verification Commands
```bash
# Check data structure
ls -la data/guidelines/*/

# Verify vector database
python -c "from src.retrieval_system import MedicalRetrievalSystem; r = MedicalRetrievalSystem(); print(f'Documents: {r.get_document_count()}')"

# Test document processing
python cli.py --stats
```