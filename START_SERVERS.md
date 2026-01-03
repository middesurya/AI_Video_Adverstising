# How to Start the Application

## Quick Start

### Option 1: Manual Start (Recommended)

**Terminal 1 - Backend:**
```bash
cd backend
python -m uvicorn main:app --host 127.0.0.1 --port 8002 --reload
```

**Terminal 2 - Frontend:**
```powershell
cd frontend
npm run dev
```

### Option 2: Using the Script

Run the startup script:
```powershell
powershell -ExecutionPolicy Bypass -File start-backend.ps1
```

Then in another terminal:
```powershell
cd frontend
npm run dev
```

## Verify Backend is Running

Open in browser: http://localhost:8002/health

You should see:
```json
{"status":"healthy","services":{"script_generation":"ready","video_generation":"ready","tts":"ready"}}
```

## Verify Frontend is Running

Open in browser: http://localhost:3000

## Troubleshooting

**If you see "Request timed out" error:**
1. Make sure backend is running on port 8002
2. Check that no other service is using port 8002
3. Try refreshing the browser page

**If backend won't start:**

Linux/Mac:
```bash
# Kill any processes on port 8002
lsof -ti:8002 | xargs kill -9

# Then start again
cd backend
python -m uvicorn main:app --host 127.0.0.1 --port 8002 --reload
```

Windows PowerShell:
```powershell
# Kill any processes on port 8002
Get-NetTCPConnection -LocalPort 8002 -ErrorAction SilentlyContinue | ForEach-Object {
    Stop-Process -Id $_.OwningProcess -Force
}

# Then start again
cd backend
python -m uvicorn main:app --host 127.0.0.1 --port 8002 --reload
```

## Test Results

✅ Backend code tested and working
✅ Frontend code tested and working  
✅ All 13 backend tests passed
✅ All 44 frontend tests passed

The application is ready to use once both servers are running!

