import { Link } from 'react-router-dom';
import '../components/MobileResponsive.css';

export default function HomePage() {
  return (
    <div className="container">
      <div className="card" style={{ textAlign: 'center', marginTop: '50px' }}>
        <h1 style={{ color: '#667eea', marginBottom: '20px', fontSize: '3em' }}>
          Welcome to Born Genius
        </h1>
        <p style={{ fontSize: '1.2em', marginBottom: '30px', color: '#666' }}>
          Discover and nurture your child's intellectual potential through comprehensive assessments
          that evaluate cognitive abilities, physical development, and linguistic skills.
        </p>
        <div className="home-buttons" style={{ display: 'flex', gap: '20px', justifyContent: 'center', flexWrap: 'wrap' }}>
          <Link to="/assessment" className="btn btn-primary" style={{ fontSize: '1.1em', padding: '15px 30px' }}>
            Start Assessment
          </Link>
          <Link to="/leaderboard" className="btn btn-secondary" style={{ fontSize: '1.1em', padding: '15px 30px' }}>
            View Leaderboard
          </Link>
        </div>
      </div>

      <div className="assessment-cards" style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '20px', marginTop: '40px' }}>
        <div className="card assessment-card">
          <h3 style={{ color: '#667eea', marginBottom: '15px' }}>🧠 Intelligence Assessment</h3>
          <p>Evaluate cognitive abilities through scientifically designed questions that measure logical thinking, problem-solving, and analytical skills.</p>
        </div>
        
        <div className="card assessment-card">
          <h3 style={{ color: '#667eea', marginBottom: '15px' }}>🏃 Physical Development</h3>
          <p>Assess motor skills and physical coordination through interactive exercises tailored to different age groups.</p>
        </div>
        
        <div className="card assessment-card">
          <h3 style={{ color: '#667eea', marginBottom: '15px' }}>🗣️ Linguistic Skills</h3>
          <p>Measure language development and communication abilities through speech recognition and vocabulary exercises.</p>
        </div>
      </div>
    </div>
  );
}
