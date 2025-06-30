# 📁 LinkedIn Sourcing Agent - Output Structure

## 🗂️ Directory Overview

The LinkedIn Sourcing Agent saves all outputs in organized directories for easy access and management.

```
outputs/
├── search_results/         # Raw search results (unused currently)
├── processed_candidates/   # Processed candidate data (unused currently)  
├── excel_exports/         # 📊 EXCEL WORKBOOKS (.xlsx files)
├── json_data/            # 📝 JSON format data
└── README.md            # This documentation

logs/
└── linkedin_agent_YYYYMMDD.log  # System logs
```

## 📊 **Excel Files** (Primary Output)

**Location**: `outputs/excel_exports/`

Each Excel file contains **8 organized sheets**:

| Sheet Name | Content | Outreach Messages |
|------------|---------|-------------------|
| **Candidates** | Main candidate data with clean company names | ❌ |
| **Contact_Info** | LinkedIn URLs, emails, contact details | ❌ |
| **Experience_Education** | Professional background, work history | ❌ |
| **Skills_Scoring** | Technical skills, fit scores, strengths | ❌ |
| **Multi_Source_Data** | GitHub, Twitter, additional profiles | ❌ |
| **Generated_Messages** | 🎯 **OUTREACH MESSAGES SAVED HERE** | ✅ |
| **Analytics** | Search and scoring analytics | ❌ |
| **Summary** | Executive summary and statistics | ❌ |

### 🎯 **Where Outreach Messages Are Saved**

**Primary Location**: `Generated_Messages` sheet in Excel files

**API Response**: Also included in the JSON response under `outreach_message` field

**CLI vs API Behavior**:
- **API** (`/source-candidates`): ✅ Generates outreach messages automatically
- **CLI** (`search` command): ❌ Simple search only (no outreach generation)

### 📋 **Generated_Messages Sheet Structure**

| Column | Description | Example |
|--------|-------------|---------|
| Name | Candidate name | "Sarah Chen" |
| Message_Type | Type of message | "LinkedIn Outreach" |
| Message_Content | Full outreach message | "Hi Sarah Chen, I hope this message finds you well..." |
| Generation_Method | How it was created | "Template" or "AI-Generated" |
| Character_Count | Message length | 247 |
| Generated_Date | When it was created | "2025-06-30 17:52:01" |

## 📝 **JSON Files**

**Location**: `outputs/json_data/`

Contains raw candidate data in JSON format with all fields including:
- Candidate profiles and details
- Scoring breakdowns and insights
- LinkedIn URLs and contact information
- **Note**: CLI searches may not include `outreach_message` field

## 📋 **Logs**

**Location**: `logs/`

System logs with search history, API calls, and error tracking.

## 🔍 **Finding Your Messages**

### **Method 1: Excel File (Recommended)**
1. Open any `.xlsx` file in `outputs/excel_exports/`
2. Navigate to the **"Generated_Messages"** sheet
3. Find the `Message_Content` column

### **Method 2: API Response**
```json
{
  "top_candidates": [
    {
      "name": "Sarah Chen",
      "outreach_message": "Hi Sarah Chen, I hope this message finds you well..."
    }
  ]
}
```

### **Method 3: Check Logs**
Look for "outreach_message" in the log files to see if messages were generated.

## 🚀 **Pro Tips**

- **Use the API** (`/source-candidates`) for complete functionality including outreach messages
- **Excel exports** are the most organized way to review candidates and messages
- **CLI searches** are faster but don't include outreach generation
- Check the `Generated_Messages` sheet first when looking for outreach content

---

*For more details, see the main README.md in the project root.*
