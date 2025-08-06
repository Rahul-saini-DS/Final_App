@echo off
echo 🚀 Starting NEW Born Genius Application...

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python is not installed. Please install Python 3.8+ first.
    pause
    exit /b 1
)

REM Check if Node.js is installed  
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Node.js is not installed. Please install Node.js 16+ first.
    pause
    exit /b 1
)

echo ✅ Prerequisites check passed

REM Setup NEW Backend
echo 🔧 Setting up NEW Backend...
cd new_backend

REM Install Python dependencies
echo 📦 Installing Python dependencies...
pip install -r requirements.txt

REM Start backend in background
echo 🚀 Starting Flask backend on http://localhost:5000...
start /b python app.py

cd ..

REM Setup NEW Frontend
echo 🎨 Setting up NEW Frontend...
cd new_frontend

REM Install Node dependencies
echo 📦 Installing Node.js dependencies...
call npm install

REM Start frontend
echo 🚀 Starting React frontend on http://localhost:5173...
call npm run dev

cd ..

echo ✅ NEW Application is running!
echo 🌐 Frontend: http://localhost:5173
echo 🔗 Backend: http://localhost:5000
echo 📊 API Health: http://localhost:5000/api/health

pause
