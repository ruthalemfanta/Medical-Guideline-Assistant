# Medical Guidelines Directory

Place your medical guideline PDF documents in the appropriate subdirectories.

## Quick Start

1. **Create organization folders** (if they don't exist):
   ```bash
   mkdir -p data/guidelines/{who,cdc,nice,aha,esc,other}
   ```

2. **Add your PDF files**:
   ```
   data/guidelines/who/who_hypertension_2023.pdf
   data/guidelines/cdc/cdc_diabetes_screening_2023.pdf
   data/guidelines/nice/nice_hypertension_2022.pdf
   ```

3. **Process the documents**:
   ```bash
   # Via CLI
   python cli.py --add-document data/guidelines/who/who_hypertension_2023.pdf
   
   # Or via API (server must be running)
   curl -X POST "http://localhost:8000/upload-guideline" \
        -F "file=@data/guidelines/who/who_hypertension_2023.pdf"
   ```

## Supported Organizations

- **WHO**: World Health Organization
- **CDC**: Centers for Disease Control and Prevention  
- **NICE**: National Institute for Health and Care Excellence
- **AHA**: American Heart Association
- **ESC**: European Society of Cardiology
- **ACP**: American College of Physicians
- **USPSTF**: US Preventive Services Task Force

## File Requirements

- **Format**: PDF only
- **Content**: Text-based (not scanned images)
- **Language**: English
- **Size**: Up to 50MB per file
- **Quality**: Official guideline documents

## Example Files

You can test the system with sample guidelines. Here are some publicly available examples:

### WHO Guidelines
- Hypertension Guidelines: https://www.who.int/publications/i/item/9789240033986
- Diabetes Guidelines: https://www.who.int/publications/i/item/9789241549585

### CDC Guidelines  
- Diabetes Prevention: https://www.cdc.gov/diabetes/prevention/
- Vaccination Guidelines: https://www.cdc.gov/vaccines/hcp/acip-recs/

### NICE Guidelines
- Hypertension: https://www.nice.org.uk/guidance/ng136
- Type 2 Diabetes: https://www.nice.org.uk/guidance/ng28

## Processing Status

After adding documents, you can check processing status:

```bash
# Check system statistics
python cli.py --stats

# View processed documents
python -c "
from src.medical_assistant import MedicalGuidelineAssistant
assistant = MedicalGuidelineAssistant()
stats = assistant.get_system_stats()
print(f'Total documents: {stats[\"total_documents\"]}')
"
```