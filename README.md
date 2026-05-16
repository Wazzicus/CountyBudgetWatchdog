# County Budget Watchdog

An AI-powered public finance tracking agent built for Kenyan citizens. The system breaks down technical budgets and legislative adjustments into accessible plain language using a conversational interface.

## Architecture

This project uses a decoupled client-server architecture:
- **Backend (FastAPI)**: An asynchronous Python backend that manages a WebSocket connection. It integrates the lightweight `google-genai` SDK and uses function calling to act autonomously. 
- **Frontend (Next.js)**: A single-page dashboard featuring a sleek, dark-themed UI built with custom CSS. It displays a real-time agent feed alongside the chat interface.

## Core Agent Tools

The autonomous Gemini agent relies on three primary tools:
1. `fetch_ward_allocation`: Simulates pulling granular budget row details for specific wards.
2. `check_gazette_amendments`: Retrieves recent text amendments with explicit publication dates from the Kenya Gazette.
3. `trigger_sms_alert`: Formats a webhook payload designed for SMS gateways (e.g., Africa's Talking) to notify users of critical updates.

## Getting Started

### Prerequisites
- Node.js (v18+)
- Python 3.11+
- A Gemini API Key from Google AI Studio.

### Running the Backend

1. Navigate to the `backend` directory:
   ```bash
   cd backend
   ```
2. Create and activate a virtual environment (optional but recommended):
   ```bash
   python -m venv venv
   # On Windows:
   .\venv\Scripts\activate
   # On Mac/Linux:
   source venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Set your Gemini API Key as an environment variable:
   ```powershell
   # Windows PowerShell
   $env:GEMINI_API_KEY="your_api_key_here"
   
   # Mac/Linux
   export GEMINI_API_KEY="your_api_key_here"
   ```
5. Start the FastAPI server (it runs on port 8000 by default):
   ```bash
   uvicorn main:app --reload
   ```

### Running the Frontend

1. Navigate to the `frontend` directory:
   ```bash
   cd frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Start the Next.js development server:
   ```bash
   npm run dev
   ```
4. Open your browser to `http://localhost:3000`.

## Deployment (Google Cloud Run)

A `Dockerfile` is provided in the `backend` directory for containerized deployment. 

gcloud run deploy budget-watchdog-backend --source ./backend --region us-central1 --allow-unauthenticated --set-env-vars GEMINI_API_KEY="your_working_api_key_here"
```
