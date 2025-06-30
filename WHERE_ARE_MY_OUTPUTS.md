# 🎯 **Output Locations - Quick Reference**

## 📍 **Where to Find Your Results**

### **Main Output Directory**: `c:\Users\mohan\Desktop\AL\outputs\`

```
outputs/
├── 🔍 search_results/        # LinkedIn search results (JSON)
├── ⚙️ processed_candidates/  # Processed & scored candidates (JSON)  
├── 📊 excel_exports/         # Organized Excel files (8 sheets each)
└── 📝 json_data/            # Raw data & backups
```

### **Log Files**: `c:\Users\mohan\Desktop\AL\logs\`
- `linkedin_agent_20250630.log` - Application logs & errors

---

## 🚀 **Quick Commands to Find Your Data**

### **Search for Python Developers** → Excel Export:
```bash
python linkedin_agent.py search --query "python developer" --excel-file auto
```
**Result**: `outputs/excel_exports/search_python_developer_TIMESTAMP.xlsx`

### **Search + Google Sheets**:
```bash
python linkedin_agent.py search --query "ML engineer" --sheets-name "ML Candidates 2025" --share-email your@email.com
```
**Result**: Online Google Sheet shared with your email

### **Export Existing Data**:
```bash
python linkedin_agent.py export --input candidates.json --excel organized_data.xlsx --include-analytics
```
**Result**: `outputs/excel_exports/organized_data.xlsx`

---

## 📊 **Excel File Contents** (8 Professional Sheets):

1. **📋 Candidates** - Names, titles, companies, fit scores
2. **📞 Contact_Info** - LinkedIn, email, social profiles
3. **🎓 Experience_Education** - Work history, degrees, schools
4. **⚡ Skills_Scoring** - Technical skills, match ratings
5. **🌐 Multi_Source_Data** - GitHub, Twitter, websites
6. **💬 Generated_Messages** - AI outreach messages
7. **📈 Analytics** - Charts, score distributions, insights
8. **📄 Summary** - Export metadata, top candidates

---

## 🎨 **File Naming Pattern**:
- **Format**: `{operation}_{query/description}_{timestamp}.{extension}`
- **Example**: `search_python_developer_20250630_141500.xlsx`
- **Timestamp**: `YYYYMMDD_HHMMSS` format

---

## 🔍 **How to Open Your Results**:

### **Excel Files**:
```bash
# Open outputs folder
explorer outputs\excel_exports

# Or double-click any .xlsx file
```

### **JSON Files** (for further processing):
```bash
# View in text editor
notepad outputs\search_results\latest_search.json

# Or import into other tools
```

### **Google Sheets**:
- Check your email for the shared link
- Or go to Google Sheets and look for the sheet name you provided

---

## 💡 **Pro Tips**:

✅ **Auto-Organization**: Files automatically go to the right folder
✅ **Timestamps**: Never overwrite previous results  
✅ **Multiple Formats**: Export to JSON + Excel + Google Sheets simultaneously
✅ **Team Sharing**: Google Sheets can be shared instantly with your team
✅ **Professional Format**: Excel files are beautifully formatted and ready for presentations

---

## 🆘 **Can't Find Your File?**

1. **Check the timestamp** - files are named with exact time
2. **Look in the right subfolder** - search results vs processed candidates
3. **Check the logs** - `logs/linkedin_agent_YYYYMMDD.log` shows what happened
4. **Google Sheets** - check your email for the share notification

**Your LinkedIn Sourcing Agent results are always organized and easy to find!** 🎉
