YSM V4 - AI CAREER MENTOR

Features:
- Full-screen AI Mentor room
- Talking-avatar style animation with lip/mouth animation while speaking
- Browser voice input and speech output
- Hindi, English, Bengali, Marathi, Tamil, Telugu and Gujarati language selector
- Multi-turn mentor conversation for the active page session
- Assessment context is sent to the AI mentor
- Optional real generative AI backend using the OpenAI Responses API
- Local fallback mentor works without an API key

RUN:
1. Extract the ZIP.
2. Open the YSM_Final folder in VS Code.
3. Install dependencies: pip install -r requirements.txt
4. Run: python app.py
5. Open the localhost URL shown by Flask.

REAL AI:
Set the OPENAI_API_KEY environment variable before starting Flask. Do not paste the key into HTML/JS.
Windows PowerShell example:
  $env:OPENAI_API_KEY="YOUR_KEY"
  python app.py

Without a key, the mentor uses a safe local fallback so the UI can still be tested.

AI FIX: The app now loads .env automatically using python-dotenv. Create .env beside app.py with OPENAI_API_KEY=sk-proj-... and OPENAI_MODEL=gpt-5.6. Do not share the key.
