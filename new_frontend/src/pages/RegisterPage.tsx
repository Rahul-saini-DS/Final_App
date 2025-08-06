import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

export default function RegisterPage() {
  const [step, setStep] = useState(1);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const { register } = useAuth();
  const navigate = useNavigate();

  // Parent data
  const [parentData, setParentData] = useState({
    name: '',
    email: '',
    password: '',
    confirmPassword: ''
  });

  // Child data
  const [childData, setChildData] = useState({
    name: '',
    dateOfBirth: '',
    sex: ''
  });

  const getAgeLabel = (dateOfBirth: string) => {
    if (!dateOfBirth) return '';
    
    const today = new Date();
    const birthDate = new Date(dateOfBirth);
    const ageInMonths = (today.getFullYear() - birthDate.getFullYear()) * 12 + (today.getMonth() - birthDate.getMonth());
    
    if (ageInMonths < 12) return "Baby Genius (0–1 yrs) 👶";
    if (ageInMonths < 24) return "Toddler Genius (1–2 yrs) 🚼";
    if (ageInMonths < 36) return "Little Explorer (2–3 yrs) 🧸";
    if (ageInMonths < 48) return "Creative Kid (3–4 yrs) 🎨";
    if (ageInMonths < 60) return "Smart Scholar (4–5 yrs) 📚";
    return "Young Genius (5–6 yrs) 🌟";
  };

  const handleStep1Submit = (e: any) => {
    e.preventDefault();
    setError('');
    
    if (parentData.password !== parentData.confirmPassword) {
      setError("Passwords don't match. Please try again.");
      return;
    }

    setStep(2);
  };

  const handleStep2Submit = async (e: any) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const fullUserData = {
        // Parent data - using parentName to match backend expectation
        parentName: parentData.name,
        email: parentData.email,
        password: parentData.password,
        // Child data
        childData: {
          name: childData.name,
          dateOfBirth: childData.dateOfBirth,
          sex: childData.sex
        }
      };

      await register(fullUserData);
      navigate('/');
    } catch (err: any) {
      setError(err.response?.data?.message || err.message || 'Registration failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container">
      <div className="card" style={{ maxWidth: '500px', margin: '50px auto' }}>
        <h2>Join Born Genius Family</h2>
        <div style={{ textAlign: 'center', marginBottom: '20px' }}>
          <div style={{ display: 'flex', justifyContent: 'center', gap: '10px', marginBottom: '10px' }}>
            <div style={{
              width: '12px',
              height: '12px',
              borderRadius: '50%',
              backgroundColor: step >= 1 ? '#6B46C1' : '#E5E7EB'
            }}></div>
            <div style={{
              width: '12px',
              height: '12px',
              borderRadius: '50%',
              backgroundColor: step >= 2 ? '#6B46C1' : '#E5E7EB'
            }}></div>
          </div>
          <p>Step {step} of 2: {step === 1 ? 'Parent Info' : 'Child Info'}</p>
        </div>

        {error && <div className="error">{error}</div>}

        {step === 1 ? (
          <form onSubmit={handleStep1Submit}>
            <div className="form-group">
              <label>👤 Full Name</label>
              <input
                type="text"
                value={parentData.name}
                onChange={(e: any) => setParentData({...parentData, name: e.target.value})}
                placeholder="Your full name"
                required
              />
            </div>
            <div className="form-group">
              <label>📧 Email</label>
              <input
                type="email"
                value={parentData.email}
                onChange={(e: any) => setParentData({...parentData, email: e.target.value})}
                placeholder="your.email@example.com"
                required
              />
            </div>
            <div className="form-group">
              <label>🔒 Password</label>
              <input
                type="password"
                value={parentData.password}
                onChange={(e: any) => setParentData({...parentData, password: e.target.value})}
                placeholder="Create a secure password"
                required
              />
            </div>
            <div className="form-group">
              <label>🔄 Confirm Password</label>
              <input
                type="password"
                value={parentData.confirmPassword}
                onChange={(e: any) => setParentData({...parentData, confirmPassword: e.target.value})}
                placeholder="Confirm your password"
                required
              />
            </div>
            <button type="submit" className="btn btn-primary" style={{ width: '100%' }}>
              Continue to Child Info ➡️
            </button>
            <div style={{ textAlign: 'center', marginTop: '15px' }}>
              <p>Already have an account? <Link to="/login">Login here 🔑</Link></p>
            </div>
          </form>
        ) : (
          <form onSubmit={handleStep2Submit}>
            <div className="form-group">
              <label>👶 Child's Name</label>
              <input
                type="text"
                value={childData.name}
                onChange={(e: any) => setChildData({...childData, name: e.target.value})}
                placeholder="Your child's name"
                required
              />
            </div>
            <div className="form-group">
              <label>📅 Date of Birth</label>
              <input
                type="date"
                value={childData.dateOfBirth}
                onChange={(e: any) => setChildData({...childData, dateOfBirth: e.target.value})}
                required
              />
            </div>
            <div className="form-group">
              <label>👦 Gender</label>
              <select
                value={childData.sex}
                onChange={(e: any) => setChildData({...childData, sex: e.target.value})}
                required
              >
                <option value="">Select Gender</option>
                <option value="boy">👦 Boy</option>
                <option value="girl">👧 Girl</option>
                <option value="other">🧸 Other</option>
              </select>
            </div>
            {childData.dateOfBirth && (
              <div style={{
                backgroundColor: '#FEF3C7',
                padding: '15px',
                borderRadius: '8px',
                marginBottom: '15px',
                textAlign: 'center'
              }}>
                <p style={{ color: '#6B46C1', fontWeight: 'bold', margin: 0 }}>
                  {getAgeLabel(childData.dateOfBirth)}
                </p>
              </div>
            )}
            <button 
              type="submit" 
              className="btn btn-primary" 
              style={{ width: '100%' }}
              disabled={loading}
            >
              {loading ? '🔄 Creating Account...' : 'Start Assessment ➡️'}
            </button>
            <button
              type="button"
              onClick={() => setStep(1)}
              className="btn btn-secondary"
              style={{ width: '100%', marginTop: '10px' }}
            >
              ⬅️ Back to Parent Info
            </button>
          </form>
        )}
      </div>
    </div>
  );
}
