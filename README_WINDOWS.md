# Windows Installation & Activation Guide - AI Agent

## Overview
This agent automates work-related reporting and audits on a schedule (Mon, Wed, Fri at 9:00 and 17:00).

## Prerequisites
1. **Python 3.10+**: Installed and added to system PATH.
2. **API Keys**:
    - Google Cloud Service Account JSON.
    - Trello API Key and Token.
    - Gmail App Password (not your regular password).

## Setup Instructions

### 1. Environment Configuration
- Copy `.env-example` to `.env`.
- Fill in all the required API keys and paths in `.env`.
- Make sure `GOOGLE_CREDENTIALS_PATH` points to your service account JSON file.

### 2. Install Dependencies
Open a terminal in the project root and run:
```bash
pip install pandas google-api-python-client google-auth-oauthlib pytrello
```

### 3. Activate Scheduler
Run the provided PowerShell script as Administrator to create the Windows Scheduled Tasks:
```powershell
Set-ExecutionPolicy RemoteSigned -Scope Process
.\setup_windows.ps1
```

## Manual Testing & Interactive Mode
- **Run All Now**:
  ```bash
  python core/ai_agent.py --now
  ```
- **Telegram Listener Mode**:
  Starts the agent in a reactive mode where it listens for instructions via Telegram.
  ```bash
  python core/ai_agent.py --listen
  ```

## Logs
All activity is logged in the `logs/` directory.
