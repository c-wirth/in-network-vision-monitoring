# Security Monitoring Dashboard

## ⚠️ IMPORTANT
Complete Setup before Run.  
The frontend depends on the backend running.

---

## Overview
This project consists of:
- FastAPI backend (Python)
- React frontend (Vite)

---

## Setup

### Backend (from ROOT folder)

1. Create and activate virtual environment

python -m venv venv

Activate:
Windows: venv\Scripts\activate  
Mac/Linux: source venv/bin/activate

2. Install backend dependencies

pip install -r requirements.txt

---

### Frontend

1. Install Node.js (version 18+ recommended)

node -v

2. Navigate to frontend folder

cd frontend

3. Install frontend dependencies

npm install

---

## Environment Configuration

Create a file named .env in the root directory with the following contents:

DATABASE_URL=sqlite:///./app.db  
SECRET_KEY=change_me  
ALGORITHM=HS256  
ACCESS_TOKEN_EXPIRE_MINUTES=30  

EMAIL_ADDRESS=your_email@gmail.com  
EMAIL_PASSWORD=your_app_password  

CLIP_STORAGE_PATH=path/to/clips  

Notes:
- Use a Gmail app password, not your normal email password
- CLIP_STORAGE_PATH should point to a valid folder on your machine

---

## Test Mode

The live stream uses a local video file.

Update the file:
application/services/LiveStreamService.py

Find:
video_path = "..."

Replace with a valid local .mp4 file path on your machine.

---

## Run

1. Start backend (from ROOT)

uvicorn application.main:app --reload

Backend runs at:
http://127.0.0.1:8000

---

2. Start frontend (from frontend folder)

npm run dev

---

3. Open the application

http://localhost:5173

---

4. Register and login

- Click Register New User
- Use a valid email address (used for notifications)
- Then log in
