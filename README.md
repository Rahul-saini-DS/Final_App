# Born Genius Child Assessment Application

This application replicates your Streamlit app functionality with a proper frontend-backend architecture using React, Flask, and PostgreSQL.

## 🚀 Quick Start

### Prerequisites
- Python 3.8+ installed
- Node.js 16+ installed  
- PostgreSQL database running (or use SQLite for development)
- Git

### Backend Setup

1. **Navigate to backend directory:**
   ```bash
   cd backend
   ```

2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables:**
   - Copy `.env.example` to `.env`
   - Update database URL and JWT secret in `.env`

4. **Initialize database:**
   ```bash
   python init_db.py
   ```

5. **Run backend server:**
   ```bash
   python app.py
   ```
   Backend will run on http://localhost:5000

### Frontend Setup

1. **Navigate to frontend directory:**
   ```bash
   cd Frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Start development server:**
   ```bash
   npm run dev
   ```
   Frontend will run on http://localhost:5173

## 🎯 Features Replicated from Streamlit App

### ✅ User Information Collection
- Child and parent details form
- Age group selection (0-1, 1-2, 2-3, 3-4, 4-5, 5-6 years)
- Beautiful gradient UI matching Streamlit styling

### ✅ Three Assessment Types

#### 1. Physical Development Tasks
- **0-1 years**: Raise hands above head
- **1-2 years**: Stand on one leg
- **2-3 years**: Turn around in circle
- **3-4 years**: Stand still like statue
- **4-5 years**: Frog jump
- **5-6 years**: Kangaroo jump

Features:
- Live webcam feed
- 15-second timer
- Real-time detection simulation
- Success/failure feedback

#### 2. Linguistic Development Tasks
- **0-1 years**: Say "mama"
- **1-2 years**: Identify apple
- **2-3 years**: Rhyme with "cat"
- **3-4 years**: Fill in the blank
- **4-5 years**: Make sentence with "sun"
- **5-6 years**: Tell story about kite

Features:
- Audio recording capability
- Speech recognition simulation
- Target word tracking
- Adaptive time limits

#### 3. Intelligence Questions
- Age-appropriate cognitive questions
- Multiple choice format
- Categories: Scientific, Logical, Socio-emotional, Artistic
- Progress tracking
- Score calculation

## 🏗️ Architecture

### Backend (Flask)
- **Routes:**
  - `/api/v1/auth/*` - Authentication
  - `/api/v1/streamlit/*` - Streamlit-style assessment
  - `/api/v1/assessment/*` - Standard assessment

- **Models:**
  - User, Child, AgeGroup
  - AssessmentResult, AssessmentSession
  - Comprehensive scoring system

### Frontend (React + TypeScript)
- **Pages:**
  - `/` - Home with assessment options
  - `/streamlit-assessment` - Main assessment page
  - `/results` - Assessment results
  - `/login`, `/signup` - Authentication

- **Features:**
  - Responsive design
  - Real-time webcam integration
  - Progress tracking
  - Beautiful UI with gradients

### Database Schema
```sql
-- Age Groups
age_groups: age_range, min_age, max_age, display_name

-- Users & Children  
users: parent_name, email, password_hash, phone_number
children: child_name, sex, birth_date, age_group_id

-- Assessment Results
assessment_results: answers, scores, total_score, user_info
assessment_sessions: session tracking, progress states
```

## 🎨 UI/UX Features

### Streamlit-Style Design
- Gradient backgrounds (blue-purple theme)
- Card-based layout
- Emojis and icons
- Progress indicators
- Task badges (Physical 🏃, Linguistic 🗣️, Intelligence 🧩)

### Interactive Elements
- Live webcam preview
- Recording timers
- Success animations
- Error handling with toast notifications
- Mobile-responsive design

## 🔧 API Endpoints

### Authentication
- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/login` - User login

### Assessment
- `POST /api/v1/streamlit/user-info` - Save user information
- `GET /api/v1/streamlit/intelligence-questions/{age_group}` - Get questions
- `GET /api/v1/streamlit/physical-task/{age_group}` - Get physical task
- `GET /api/v1/streamlit/linguistic-task/{age_group}` - Get linguistic task
- `POST /api/v1/streamlit/submit-complete-assessment` - Submit results

## 🚨 Troubleshooting

### Common Issues

1. **Database Connection Error**
   - Check PostgreSQL is running
   - Verify DATABASE_URL in .env
   - Run `python init_db.py` to setup tables

2. **Module Not Found Errors**
   - Run `pip install -r requirements.txt`
   - Check Python version compatibility

3. **Frontend Build Errors**
   - Run `npm install` to install dependencies
   - Check Node.js version

4. **CORS Errors**
   - Ensure backend CORS_ORIGINS includes frontend URL
   - Check frontend API base URL configuration

### Development vs Production

**Development:**
- Uses SQLite database
- Debug mode enabled
- Hot reload for both frontend and backend

**Production:**
- PostgreSQL database required
- Set FLASK_ENV=production
- Build frontend with `npm run build`

## 📱 Mobile Support

The application is fully responsive and works on:
- Desktop browsers
- Tablet devices  
- Mobile phones
- Webcam access on supported devices

## 🔐 Security Features

- JWT token authentication
- Password hashing with passlib
- SQL injection prevention with SQLAlchemy
- CORS protection
- Input validation

## 📊 Assessment Scoring

### Scoring System
- **Physical Tasks**: 0-3 points (based on completion)
- **Linguistic Tasks**: 0-3 points (based on speech recognition)
- **Intelligence Questions**: 0-4 points (number of correct answers)
- **Total Score**: Sum of all three categories

### Age-Appropriate Content
Each age group has specifically designed:
- Physical challenges matching motor development
- Linguistic tasks for language milestones
- Cognitive questions for intellectual growth

## 🎯 Next Steps

1. **Start the application** using the setup instructions above
2. **Test the assessment flow** with different age groups
3. **Customize questions** by editing the intelligence questions in the backend
4. **Add AI integration** for real computer vision and speech recognition
5. **Deploy to production** using your preferred hosting platform

## 💡 Key Improvements Over Original

1. **Better Architecture**: Separate frontend/backend vs monolithic Streamlit
2. **Database Persistence**: Proper data storage vs session state
3. **User Authentication**: Multi-user support vs single session
4. **Responsive Design**: Works on all devices vs desktop only
5. **API Structure**: RESTful APIs vs direct function calls
6. **Scalability**: Can handle multiple concurrent users

---

The application successfully replicates your Streamlit prototype with a production-ready architecture. The interactive assessment page (`/streamlit-assessment`) provides the exact same user experience as your original Streamlit app, but with better performance, scalability, and user management.
