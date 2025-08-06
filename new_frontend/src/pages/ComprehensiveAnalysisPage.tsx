import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import axios from 'axios';

const API_BASE_URL = 'http://localhost:5000/api';

interface AnalysisData {
  child_id: number;
  child_name: string;
  age_group: string;
  comprehensive_analysis: string;
  statistics_by_type: {
    [key: string]: {
      total_questions: number;
      correct_answers: number;
      accuracy: number;
      avg_response_time: number;
      total_hints: number;
    };
  };
  generated_at: string;
}

export default function ComprehensiveAnalysisPage() {
  const { childId } = useParams<{ childId: string }>();
  const { token } = useAuth();
  const navigate = useNavigate();
  const [analysis, setAnalysis] = useState<AnalysisData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchComprehensiveAnalysis();
  }, [childId]);

  const fetchComprehensiveAnalysis = async () => {
    if (!childId || !token) return;

    try {
      setLoading(true);
      const response = await axios.get(`${API_BASE_URL}/child-comprehensive-analysis/${childId}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setAnalysis(response.data);
    } catch (err: any) {
      setError(err.response?.data?.error || 'Failed to load comprehensive analysis');
    } finally {
      setLoading(false);
    }
  };

  const getAssessmentTypeIcon = (type: string) => {
    switch (type) {
      case 'intelligence': return '🧠';
      case 'physical': return '🏃‍♂️';
      case 'linguistic': return '🗣️';
      default: return '📊';
    }
  };

  const getAssessmentTypeName = (type: string) => {
    switch (type) {
      case 'intelligence': return 'Intellectual Development';
      case 'physical': return 'Physical Development';
      case 'linguistic': return 'Language Development';
      default: return type.charAt(0).toUpperCase() + type.slice(1);
    }
  };

  const getAccuracyColor = (accuracy: number) => {
    if (accuracy >= 80) return '#10b981'; // Green
    if (accuracy >= 65) return '#f59e0b'; // Yellow
    if (accuracy >= 50) return '#f97316'; // Orange
    return '#ef4444'; // Red
  };

  const getPerformanceLevel = (accuracy: number) => {
    if (accuracy >= 80) return { level: 'Excellent', emoji: '⭐' };
    if (accuracy >= 65) return { level: 'Good', emoji: '👍' };
    if (accuracy >= 50) return { level: 'Developing', emoji: '📈' };
    return { level: 'Needs Support', emoji: '💪' };
  };

  if (loading) {
    return (
      <div style={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        minHeight: '60vh',
        flexDirection: 'column'
      }}>
        <div style={{ 
          fontSize: '48px', 
          animation: 'spin 2s linear infinite',
          marginBottom: '20px'
        }}>🔄</div>
        <p style={{ fontSize: '18px', color: '#666' }}>Analyzing comprehensive assessment data...</p>
        <style>
          {`
            @keyframes spin {
              from { transform: rotate(0deg); }
              to { transform: rotate(360deg); }
            }
          `}
        </style>
      </div>
    );
  }

  if (error || !analysis) {
    return (
      <div style={{ 
        maxWidth: '800px', 
        margin: '0 auto', 
        padding: '40px 20px',
        textAlign: 'center'
      }}>
        <div style={{
          background: 'linear-gradient(135deg, #fee2e2, #fecaca)',
          border: '2px solid #fca5a5',
          borderRadius: '15px',
          padding: '30px',
          marginBottom: '20px'
        }}>
          <div style={{ fontSize: '48px', marginBottom: '15px' }}>❌</div>
          <h2 style={{ color: '#dc2626', marginBottom: '10px' }}>Analysis Error</h2>
          <p style={{ color: '#7f1d1d', marginBottom: '20px' }}>
            {error || 'No comprehensive analysis data available for this child.'}
          </p>
          <button
            onClick={() => navigate(-1)}
            style={{
              background: '#dc2626',
              color: 'white',
              border: 'none',
              padding: '12px 24px',
              borderRadius: '8px',
              fontSize: '16px',
              cursor: 'pointer'
            }}
          >
            Go Back
          </button>
        </div>
      </div>
    );
  }

  return (
    <div style={{ 
      maxWidth: '1200px', 
      margin: '0 auto', 
      padding: '20px',
      fontFamily: 'system-ui, -apple-system, sans-serif'
    }}>
      {/* Header */}
      <div style={{
        textAlign: 'center',
        marginBottom: '30px',
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        color: 'white',
        padding: '40px',
        borderRadius: '20px',
        boxShadow: '0 10px 30px rgba(0,0,0,0.2)'
      }}>
        <h1 style={{ 
          margin: '0 0 15px 0', 
          fontSize: '36px',
          fontWeight: 'bold'
        }}>
          📈 Comprehensive Assessment Analysis
        </h1>
        <div style={{ fontSize: '20px', opacity: 0.9, marginBottom: '10px' }}>
          <strong>{analysis.child_name}</strong> • Age Group: {analysis.age_group}
        </div>
        <div style={{ fontSize: '16px', opacity: 0.8 }}>
          Generated on {new Date(analysis.generated_at).toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'long',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
          })}
        </div>
      </div>

      {/* Statistics Cards */}
      {Object.keys(analysis.statistics_by_type).length > 0 && (
        <div style={{ 
          display: 'grid', 
          gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', 
          gap: '20px',
          marginBottom: '40px'
        }}>
          {Object.entries(analysis.statistics_by_type).map(([type, stats]) => {
            const performance = getPerformanceLevel(stats.accuracy);
            return (
              <div key={type} style={{ 
                background: 'white',
                borderRadius: '15px',
                padding: '25px',
                boxShadow: '0 8px 25px rgba(0,0,0,0.1)',
                border: `3px solid ${getAccuracyColor(stats.accuracy)}`,
                transition: 'transform 0.2s ease',
                cursor: 'pointer'
              }}
              onMouseEnter={(e) => e.currentTarget.style.transform = 'translateY(-5px)'}
              onMouseLeave={(e) => e.currentTarget.style.transform = 'translateY(0)'}
              >
                <div style={{ 
                  display: 'flex', 
                  alignItems: 'center', 
                  marginBottom: '15px' 
                }}>
                  <span style={{ fontSize: '32px', marginRight: '15px' }}>
                    {getAssessmentTypeIcon(type)}
                  </span>
                  <div>
                    <h3 style={{ 
                      margin: 0, 
                      color: '#1f2937',
                      fontSize: '18px'
                    }}>
                      {getAssessmentTypeName(type)}
                    </h3>
                    <div style={{ 
                      display: 'flex', 
                      alignItems: 'center',
                      marginTop: '5px'
                    }}>
                      <span style={{ 
                        fontSize: '24px',
                        color: getAccuracyColor(stats.accuracy),
                        fontWeight: 'bold',
                        marginRight: '10px'
                      }}>
                        {stats.accuracy}%
                      </span>
                      <span style={{ 
                        fontSize: '14px',
                        color: '#6b7280',
                        background: '#f3f4f6',
                        padding: '4px 8px',
                        borderRadius: '12px'
                      }}>
                        {performance.emoji} {performance.level}
                      </span>
                    </div>
                  </div>
                </div>
                
                <div style={{ 
                  display: 'grid', 
                  gridTemplateColumns: '1fr 1fr',
                  gap: '15px',
                  fontSize: '14px'
                }}>
                  <div style={{ textAlign: 'center', padding: '10px', background: '#f8fafc', borderRadius: '8px' }}>
                    <div style={{ fontWeight: 'bold', color: '#1f2937' }}>Questions</div>
                    <div style={{ fontSize: '20px', color: '#4f46e5', fontWeight: 'bold' }}>
                      {stats.total_questions}
                    </div>
                  </div>
                  
                  <div style={{ textAlign: 'center', padding: '10px', background: '#f0fdf4', borderRadius: '8px' }}>
                    <div style={{ fontWeight: 'bold', color: '#1f2937' }}>Correct</div>
                    <div style={{ fontSize: '20px', color: '#16a34a', fontWeight: 'bold' }}>
                      {stats.correct_answers}
                    </div>
                  </div>
                  
                  {stats.avg_response_time > 0 && (
                    <div style={{ textAlign: 'center', padding: '10px', background: '#fffbeb', borderRadius: '8px' }}>
                      <div style={{ fontWeight: 'bold', color: '#1f2937' }}>Avg Time</div>
                      <div style={{ fontSize: '16px', color: '#d97706', fontWeight: 'bold' }}>
                        {stats.avg_response_time}s
                      </div>
                    </div>
                  )}
                  
                  {stats.total_hints > 0 && (
                    <div style={{ textAlign: 'center', padding: '10px', background: '#fef3f2', borderRadius: '8px' }}>
                      <div style={{ fontWeight: 'bold', color: '#1f2937' }}>Hints Used</div>
                      <div style={{ fontSize: '16px', color: '#dc2626', fontWeight: 'bold' }}>
                        {stats.total_hints}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Comprehensive Analysis */}
      <div style={{
        background: 'white',
        borderRadius: '20px',
        padding: '40px',
        boxShadow: '0 10px 30px rgba(0,0,0,0.1)',
        marginBottom: '30px'
      }}>
        <div style={{ 
          display: 'flex', 
          alignItems: 'center', 
          marginBottom: '30px',
          paddingBottom: '20px',
          borderBottom: '2px solid #e5e7eb'
        }}>
          <span style={{ fontSize: '36px', marginRight: '15px' }}>🎯</span>
          <h2 style={{ 
            margin: 0, 
            color: '#1f2937',
            fontSize: '28px',
            fontWeight: 'bold'
          }}>
            Detailed Analysis & Insights
          </h2>
        </div>
        
        <div style={{
          fontSize: '18px',
          lineHeight: '1.8',
          color: '#374151',
          background: 'linear-gradient(135deg, #f8fafc, #f1f5f9)',
          padding: '30px',
          borderRadius: '15px',
          border: '1px solid #e2e8f0',
          whiteSpace: 'pre-line'
        }}>
          {analysis.comprehensive_analysis}
        </div>
      </div>

      {/* Action Buttons */}
      <div style={{ 
        display: 'flex', 
        justifyContent: 'center', 
        gap: '20px',
        marginTop: '40px'
      }}>
        <button
          onClick={() => navigate(-1)}
          style={{
            background: 'linear-gradient(135deg, #6b7280, #4b5563)',
            color: 'white',
            border: 'none',
            padding: '15px 30px',
            borderRadius: '12px',
            fontSize: '16px',
            fontWeight: 'bold',
            cursor: 'pointer',
            transition: 'all 0.2s ease'
          }}
          onMouseEnter={(e) => e.currentTarget.style.transform = 'translateY(-2px)'}
          onMouseLeave={(e) => e.currentTarget.style.transform = 'translateY(0)'}
        >
          ← Back to Results
        </button>
        
        <button
          onClick={() => window.print()}
          style={{
            background: 'linear-gradient(135deg, #3b82f6, #2563eb)',
            color: 'white',
            border: 'none',
            padding: '15px 30px',
            borderRadius: '12px',
            fontSize: '16px',
            fontWeight: 'bold',
            cursor: 'pointer',
            transition: 'all 0.2s ease'
          }}
          onMouseEnter={(e) => e.currentTarget.style.transform = 'translateY(-2px)'}
          onMouseLeave={(e) => e.currentTarget.style.transform = 'translateY(0)'}
        >
          🖨️ Print Report
        </button>
      </div>

      {/* Print Styles */}
      <style>
        {`
          @media print {
            body * {
              visibility: hidden;
            }
            .print-section, .print-section * {
              visibility: visible;
            }
            .print-section {
              position: absolute;
              left: 0;
              top: 0;
            }
          }
        `}
      </style>
    </div>
  );
}
