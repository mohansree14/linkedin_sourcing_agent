# 📁 Output Locations Guide

## Where Your Results Are Saved

The LinkedIn Sourcing Agent organizes all outputs in dedicated folders for easy management:

```
c:\Users\mohan\Desktop\AL\
├── outputs/
│   ├── search_results/        # Search command results
│   ├── processed_candidates/  # Processed candidate data
│   ├── excel_exports/         # Excel files with organized data
│   └── json_data/            # Raw JSON data files
├── logs/                     # Application logs
└── linkedin_sourcing_agent/  # Main application
```

## 🔍 Search Results
**Location**: `outputs/search_results/`

**File Format**: `search_{query}_{timestamp}.json`

**Example**: `search_python_developer_20250630_141500.json`

**Command Examples**:
```bash
# Auto-generated path
python linkedin_agent.py search --query "python developer" --limit 10

# Custom path
python linkedin_agent.py search --query "ML engineer" --output custom_results.json
```

## ⚙️ Processed Candidates
**Location**: `outputs/processed_candidates/`

**File Format**: `processed_candidates_{timestamp}.json`

**Example**: `processed_candidates_20250630_141500.json`

**Command Examples**:
```bash
# Process and auto-save
python linkedin_agent.py process --input candidates.json --generate-outreach

# Process with custom output
python linkedin_agent.py process --input candidates.json --output my_processed.json
```

## 📊 Excel Exports
**Location**: `outputs/excel_exports/`

**File Format**: `{operation}_{query/name}_{timestamp}.xlsx`

**Example**: `search_python_developer_20250630_141500.xlsx`

**Contains 8 Organized Sheets**:
1. **Candidates** - Main candidate information
2. **Contact_Info** - Contact details and social profiles  
3. **Experience_Education** - Work history and education
4. **Skills_Scoring** - Technical skills and fit scores
5. **Multi_Source_Data** - GitHub, Twitter, website data
6. **Generated_Messages** - AI-generated outreach messages
7. **Analytics** - Summary statistics and insights
8. **Summary** - Export metadata and top candidates

**Command Examples**:
```bash
# Auto-generated Excel path
python linkedin_agent.py search --query "data scientist" --excel-file auto

# Custom Excel path
python linkedin_agent.py search --query "DevOps engineer" --excel-file my_devops_candidates.xlsx

# Export existing data to Excel
python linkedin_agent.py export --input candidates.json --excel organized_data.xlsx --include-analytics
```

## 🌐 Google Sheets Exports
**Location**: Online at Google Sheets

**Naming**: Custom names you provide

**Sharing**: Automatically shared with specified emails

**Command Examples**:
```bash
# Export to Google Sheets
python linkedin_agent.py search --query "frontend developer" --sheets-name "Frontend Candidates 2025"

# Export and share
python linkedin_agent.py search --query "backend developer" --sheets-name "Backend Team Candidates" --share-email hr@company.com

# Export existing data to Google Sheets
python linkedin_agent.py export --input candidates.json --sheets "Organized Candidate Database" --share-email team@company.com
```

## 📝 JSON Data Files
**Location**: `outputs/json_data/`

**File Format**: Various JSON files for raw data

**Use Case**: For further processing, analysis, or importing into other tools

## 📋 Logs
**Location**: `logs/`

**File Format**: `linkedin_agent_{date}.log`

**Example**: `linkedin_agent_20250630.log`

**Contains**: Application logs, API calls, errors, and execution details

## 🛠️ Output File Examples

### Search Results JSON Structure:
```json
[
  {
    "name": "John Smith",
    "headline": "Senior Python Developer at TechCorp",
    "location": "San Francisco, CA",
    "linkedin_url": "https://linkedin.com/in/johnsmith",
    "fit_score": 8.5,
    "skills": ["Python", "Django", "AWS"],
    "experience": [...],
    "education": [...],
    "github_profile": {...},
    "generated_messages": [...]
  }
]
```

### Excel File Sheets:
- **Candidates**: Structured table with names, titles, companies, fit scores
- **Contact_Info**: LinkedIn URLs, emails, social media profiles
- **Skills_Scoring**: Technical skills, match scores, relevance ratings
- **Analytics**: Charts and graphs showing score distributions, locations

## 🎯 Quick Access Commands

### View Recent Outputs:
```bash
# List recent search results
dir outputs\search_results\

# List recent Excel exports  
dir outputs\excel_exports\

# View latest log
type logs\linkedin_agent_20250630.log
```

### Open Output Folder:
```bash
# Open outputs folder in Explorer
explorer outputs

# Open specific subfolder
explorer outputs\excel_exports
```

## 💡 Pro Tips

1. **Automatic Organization**: Files are automatically organized by type and timestamped
2. **Custom Paths**: Use `--output` to specify exact file locations
3. **Multiple Formats**: Export the same data to JSON, Excel, and Google Sheets simultaneously
4. **Backup Originals**: JSON files serve as backups for re-processing
5. **Share Easily**: Google Sheets can be shared with team members automatically

## 🔧 Troubleshooting

**Can't find your file?**
- Check the appropriate subfolder in `outputs/`
- Look for timestamp in filename
- Check logs for any export errors

**Permission errors?**
- Ensure you have write permissions to the directory
- Close Excel files before overwriting
- Check Google Sheets sharing permissions

**Files too large?**
- Large datasets create large Excel files
- Consider using filters to reduce candidate count
- JSON files are typically smaller than Excel files
