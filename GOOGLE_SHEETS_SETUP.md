# Google Sheets Setup Guide

To export candidate data to Google Sheets, you need to set up Google Service Account credentials.

## Step 1: Create a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Google Sheets API and Google Drive API

## Step 2: Create Service Account

1. Go to **IAM & Admin** > **Service Accounts**
2. Click **Create Service Account**
3. Enter a name (e.g., "LinkedIn Sourcing Agent")
4. Click **Create and Continue**
5. Skip role assignment (click **Continue**)
6. Click **Done**

## Step 3: Generate Credentials

1. Click on your newly created service account
2. Go to **Keys** tab
3. Click **Add Key** > **Create New Key**
4. Select **JSON** format
5. Download the file and save it as `service_account.json` in your project directory

## Step 4: Share Sheets with Service Account

For each Google Sheet you want to write to:
1. Open the Google Sheet
2. Click **Share**
3. Add the service account email (from the JSON file)
4. Give it **Editor** permissions

## Step 5: Configure the Agent

Add this to your `.env` file:
```
GOOGLE_SERVICE_ACCOUNT_FILE=service_account.json
```

## Usage Examples

### Export search results to Google Sheets:
```bash
python linkedin_agent.py search --query "python developer" --sheets-name "Python Developers 2025" --share-email your@email.com
```

### Export existing data to Google Sheets:
```bash
python linkedin_agent.py export --input candidates.json --sheets "Organized Candidates" --include-analytics --include-messages
```

### Export to both Excel and Google Sheets:
```bash
python linkedin_agent.py search --query "ML engineer" --excel-file ml_engineers.xlsx --sheets-name "ML Engineers 2025"
```

## Sheet Structure

The exported Google Sheet will contain these organized tabs:
- **Candidates** - Main candidate information
- **Contact_Info** - Contact details and social profiles
- **Experience_Education** - Work history and education
- **Skills_Scoring** - Skills and fit scores
- **Multi_Source_Data** - GitHub, Twitter, website data
- **Generated_Messages** - AI-generated outreach messages
- **Analytics** - Summary statistics and insights
- **Summary** - Export metadata and top candidates

## Troubleshooting

### "Permission denied" error:
- Make sure the service account email is added to the Google Sheet with Editor permissions
- Check that the Google Sheets API is enabled in your Google Cloud project

### "File not found" error:
- Ensure `service_account.json` is in the correct directory
- Update the `GOOGLE_SERVICE_ACCOUNT_FILE` path in your `.env` file

### Import errors:
- Install required packages: `pip install gspread google-auth pandas openpyxl`
