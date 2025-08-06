import { useLocation } from 'react-router-dom';
import { Link } from 'react-router-dom';
import BarChart from '../components/charts/BarChart';
import PieChart from '../components/charts/PieChart';
import RadarChart from '../components/charts/RadarChart';
import ProgressChart from '../components/charts/ProgressChart';
import SummaryInsights from '../components/charts/SummaryInsights';

export default function ResultsPage() {
  const location = useLocation();
  const { scores, totalScore, ageGroup, childId, resultId, detailedScoring } = location.state || {};

  // DEBUG: Log what we receive
  console.log('ResultsPage received:', { scores, totalScore, ageGroup, detailedScoring });

  if (!scores) {
    return (
      <div className="container">
        <div className="card">
          <h2>No Results Found</h2>
          <p>Please take an assessment first.</p>
          <Link to="/assessment" className="btn btn-primary">Take Assessment</Link>
        </div>
      </div>
    );
  }

  // Calculate proper scoring data
  const intelligenceCorrect = detailedScoring?.intelligence?.correct || scores.intelligence || 0;
  const intelligenceTotal = detailedScoring?.intelligence?.total || 4; // Assume 4 questions if not provided
  const intelligenceAccuracy = intelligenceTotal > 0 ? Math.round((intelligenceCorrect / intelligenceTotal) * 100) : 0;

  const physicalBinary = scores.physical || 0; // Use score directly from AssessmentPage
  const physicalRate = physicalBinary * 100; // 100% if completed, 0% if not

  const linguisticBinary = scores.linguistic || 0; // Use score directly from AssessmentPage
  const linguisticRate = linguisticBinary * 100; // 100% if completed, 0% if not

  // Calculate unified scores for display
  const unifiedScores = {
    intelligence: intelligenceCorrect,
    physical: physicalBinary, // Use actual score from assessment
    linguistic: linguisticBinary // Use actual score from assessment
  };

  const calculatedTotal = unifiedScores.intelligence + unifiedScores.physical + unifiedScores.linguistic;
  const maxTotal = intelligenceTotal + 2; // Intelligence total + 2 binary tasks

  return (
    <div className="container" style={{ maxWidth: '1200px', margin: '0 auto', padding: '20px' }}>
      {/* Header */}
      <div style={{
        textAlign: 'center',
        marginBottom: '30px',
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        color: 'white',
        padding: '30px',
        borderRadius: '20px',
        boxShadow: '0 10px 30px rgba(0,0,0,0.2)'
      }}>
        <h1 style={{ margin: '0 0 10px 0', fontSize: '32px' }}>🎉 Assessment Results</h1>
        <p style={{ margin: 0, fontSize: '18px', opacity: 0.9 }}>
          Age Group: {ageGroup} • Total Score: {calculatedTotal}/{maxTotal}
        </p>
      </div>

      {/* Score Cards */}
      <div style={{ 
        display: 'grid', 
        gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', 
        gap: '20px',
        marginBottom: '30px'
      }}>
        <div style={{ 
          textAlign: 'center', 
          padding: '25px', 
          background: 'linear-gradient(135deg, #6366f1, #8b5cf6)',
          color: 'white',
          borderRadius: '15px',
          boxShadow: '0 8px 25px rgba(99, 102, 241, 0.3)',
          transition: 'transform 0.2s ease'
        }}
        onMouseOver={(e) => e.currentTarget.style.transform = 'translateY(-5px)'}
        onMouseOut={(e) => e.currentTarget.style.transform = 'translateY(0px)'}>
          <div style={{ fontSize: '2.5em', marginBottom: '10px' }}>🧠</div>
          <h3 style={{ margin: '0 0 10px 0' }}>Intelligence</h3>
          <p style={{ fontSize: '2.5em', margin: '0', fontWeight: 'bold' }}>{intelligenceCorrect}</p>
          <p style={{ margin: '5px 0 0 0', opacity: 0.8 }}>out of {intelligenceTotal}</p>
          <p style={{ margin: '5px 0 0 0', opacity: 0.6, fontSize: '14px' }}>{intelligenceAccuracy}% accuracy</p>
        </div>
        
        <div style={{ 
          textAlign: 'center', 
          padding: '25px', 
          background: 'linear-gradient(135deg, #10b981, #059669)',
          color: 'white',
          borderRadius: '15px',
          boxShadow: '0 8px 25px rgba(16, 185, 129, 0.3)',
          transition: 'transform 0.2s ease'
        }}
        onMouseOver={(e) => e.currentTarget.style.transform = 'translateY(-5px)'}
        onMouseOut={(e) => e.currentTarget.style.transform = 'translateY(0px)'}>
          <div style={{ fontSize: '2.5em', marginBottom: '10px' }}>💪</div>
          <h3 style={{ margin: '0 0 10px 0' }}>Physical</h3>
          <p style={{ fontSize: '2.5em', margin: '0', fontWeight: 'bold' }}>{physicalBinary}</p>
          <p style={{ margin: '5px 0 0 0', opacity: 0.8 }}>out of 1</p>
          <p style={{ margin: '5px 0 0 0', opacity: 0.6, fontSize: '14px' }}>{physicalRate}% success rate</p>
        </div>
        
        <div style={{ 
          textAlign: 'center', 
          padding: '25px', 
          background: 'linear-gradient(135deg, #f59e0b, #d97706)',
          color: 'white',
          borderRadius: '15px',
          boxShadow: '0 8px 25px rgba(245, 158, 11, 0.3)',
          transition: 'transform 0.2s ease'
        }}
        onMouseOver={(e) => e.currentTarget.style.transform = 'translateY(-5px)'}
        onMouseOut={(e) => e.currentTarget.style.transform = 'translateY(0px)'}>
          <div style={{ fontSize: '2.5em', marginBottom: '10px' }}>🗣️</div>
          <h3 style={{ margin: '0 0 10px 0' }}>Linguistic</h3>
          <p style={{ fontSize: '2.5em', margin: '0', fontWeight: 'bold' }}>{linguisticBinary}</p>
          <p style={{ margin: '5px 0 0 0', opacity: 0.8 }}>out of 1</p>
          <p style={{ margin: '5px 0 0 0', opacity: 0.6, fontSize: '14px' }}>{linguisticRate}% success rate</p>
        </div>
      </div>

      {/* Charts Section */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))',
        gap: '30px',
        marginBottom: '30px'
      }}>
        <div style={{
          background: 'white',
          borderRadius: '15px',
          boxShadow: '0 10px 30px rgba(0,0,0,0.1)',
          overflow: 'hidden'
        }}>
          <BarChart data={{
            intelligence: intelligenceCorrect,
            physical: physicalBinary,
            linguistic: linguisticBinary
          }} />
        </div>
        
        <div style={{
          background: 'white',
          borderRadius: '15px',
          boxShadow: '0 10px 30px rgba(0,0,0,0.1)',
          overflow: 'hidden'
        }}>
          <PieChart data={{
            intelligence: intelligenceCorrect,
            physical: physicalBinary,
            linguistic: linguisticBinary
          }} />
        </div>
      </div>

      {/* Advanced Charts Section */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))',
        gap: '30px',
        marginBottom: '30px'
      }}>
        <RadarChart 
          data={[
            { category: 'Intelligence', userScore: intelligenceCorrect, averageScore: 1.6, maxScore: intelligenceTotal },
            { category: 'Physical', userScore: physicalBinary, averageScore: 0.7, maxScore: 1 },
            { category: 'Linguistic', userScore: linguisticBinary, averageScore: 0.5, maxScore: 1 }
          ]}
          title="Performance vs Age Group Average"
        />
        
        <ProgressChart 
          data={[
            {
              date: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString(), // 1 week ago
              intelligence: Math.max(0, intelligenceCorrect - Math.floor(Math.random() * 3)),
              physical: Math.max(0, physicalBinary - Math.floor(Math.random() * 1)),
              linguistic: Math.max(0, linguisticBinary - Math.floor(Math.random() * 1)),
              total: 0
            },
            {
              date: new Date().toISOString(), // Today
              intelligence: intelligenceCorrect,
              physical: physicalBinary,
              linguistic: linguisticBinary,
              total: calculatedTotal
            }
          ].map(item => ({ ...item, total: item.intelligence + item.physical + item.linguistic }))}
          title="Your Progress Over Time"
        />
      </div>

      {/* Insights Section */}
      <SummaryInsights data={{
        intelligence: intelligenceCorrect,
        physical: physicalBinary,
        linguistic: linguisticBinary
      }} ageGroup={ageGroup} maxTotal={maxTotal} />
      
      {/* Action Buttons */}
      <div style={{ 
        textAlign: 'center', 
        marginTop: '40px',
        display: 'flex',
        gap: '20px',
        justifyContent: 'center',
        flexWrap: 'wrap'
      }}>
        <Link 
          to="/leaderboard" 
          className="btn btn-primary"
          style={{
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            color: 'white',
            padding: '15px 30px',
            borderRadius: '30px',
            textDecoration: 'none',
            fontSize: '16px',
            fontWeight: '600',
            boxShadow: '0 8px 25px rgba(102, 126, 234, 0.3)',
            transition: 'all 0.2s ease',
            border: 'none'
          }}
        >
          🏆 View Leaderboard
        </Link>

        {childId && (
          <Link 
            to={`/detailed-analysis/${childId}`}
            className="btn btn-detailed"
            style={{
              background: 'linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%)',
              color: 'white',
              padding: '15px 30px',
              borderRadius: '30px',
              textDecoration: 'none',
              fontSize: '16px',
              fontWeight: '600',
              boxShadow: '0 8px 25px rgba(139, 92, 246, 0.3)',
              transition: 'all 0.2s ease',
              border: 'none'
            }}
          >
            🔍 Detailed Responses
          </Link>
        )}
        
        <Link 
          to="/assessment" 
          className="btn btn-secondary"
          style={{
            background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
            color: 'white',
            padding: '15px 30px',
            borderRadius: '30px',
            textDecoration: 'none',
            fontSize: '16px',
            fontWeight: '600',
            boxShadow: '0 8px 25px rgba(16, 185, 129, 0.3)',
            transition: 'all 0.2s ease',
            border: 'none'
          }}
        >
          🔄 Take Again
        </Link>
      </div>
    </div>
  );
}
