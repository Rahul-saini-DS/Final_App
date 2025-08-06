import { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import axios from 'axios';

const API_BASE_URL = 'http://localhost:5000/api';

interface DetailedResponse {
  response_id: number;
  question_id: string;
  question_text: string;
  child_answer: string;
  correct_answer: string;
  is_correct: boolean;
  response_time: number;
  difficulty_level: number;
  attempts: number;
}

interface AITaskResponse {
  task_type: string;
  task_name: string;
  description: string;
  success: number; // 0 or 1
  was_skipped: boolean;
  was_completed: boolean;
  completion_time?: number;
  ai_feedback?: string;
}

interface AttemptData {
  attempt_number: number;
  result_id: number;
  assessment_date: string;
  age_group: string;
  scores: {
    intelligence: number;
    intelligence_total: number;
    intelligence_percentage: number;
    physical: number; // 0 or 1
    linguistic: number; // 0 or 1
    total: number;
    max_total: number;
  };
  intelligence_responses: DetailedResponse[];
  ai_tasks: AITaskResponse[];
}

interface ResponseAnalysis {
  child_id: number;
  attempts: AttemptData[];
  summary: {
    total_attempts: number;
    latest_attempt: {
      date: string;
      age_group: string;
      total_score: number;
      max_score: number;
      intelligence_score: number;
      physical_score: number; // 0 or 1
      linguistic_score: number; // 0 or 1
    } | null;
  };
}

export default function DetailedAnalysisPage() {
  const { childId } = useParams<{ childId: string }>();
  const { token } = useAuth();
  const [analysis, setAnalysis] = useState<ResponseAnalysis | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchDetailedAnalysis();
  }, [childId]);

  const fetchDetailedAnalysis = async () => {
    if (!childId || !token) return;

    try {
      const response = await axios.get(`${API_BASE_URL}/child-responses/${childId}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setAnalysis(response.data);
    } catch (err) {
      setError('Failed to load detailed analysis');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div style={{ 
        minHeight: '100vh', 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center',
        background: 'rgba(0,0,0,0.1)',
        color: 'white',
        fontSize: '18px'
      }}>
        <div style={{
          background: 'rgba(255,255,255,0.2)',
          padding: '30px',
          borderRadius: '15px',
          textAlign: 'center'
        }}>
          <div>Loading detailed analysis...</div>
          <div style={{ marginTop: '10px', fontSize: '14px', opacity: 0.8 }}>
            Child ID: {childId}
          </div>
        </div>
      </div>
    );
  }

  if (error || !analysis) {
    return (
      <div style={{ 
        minHeight: '100vh', 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center',
        background: 'rgba(0,0,0,0.1)',
        color: 'white',
        fontSize: '18px'
      }}>
        <div style={{
          background: 'rgba(255,255,255,0.2)',
          padding: '30px',
          borderRadius: '15px',
          textAlign: 'center'
        }}>
          <h2 style={{ color: '#ff6b6b', marginBottom: '15px' }}>Error</h2>
          <p>{error || 'No analysis data available'}</p>
          <div style={{ marginTop: '10px', fontSize: '14px', opacity: 0.8 }}>
            Child ID: {childId} | Token: {token ? 'Available' : 'Missing'}
          </div>
        </div>
      </div>
    );
  }

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
        <h1 style={{ margin: '0 0 10px 0', fontSize: '32px' }}>📊 Assessment History</h1>
        <p style={{ margin: 0, fontSize: '18px', opacity: 0.9 }}>
          Child ID: {childId} • Total Attempts: {analysis.summary.total_attempts}
        </p>
      </div>

      {/* Summary Cards for Latest Attempt */}
      {analysis.summary.latest_attempt && (
        <div>
          <h2 style={{ textAlign: 'center', marginBottom: '20px', color: '#374151' }}>
            📈 Latest Assessment Results
          </h2>
          <div style={{ 
            display: 'grid', 
            gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', 
            gap: '20px',
            marginBottom: '40px'
          }}>
            <div style={{ 
              textAlign: 'center', 
              padding: '25px', 
              background: 'linear-gradient(135deg, #6366f1, #8b5cf6)',
              color: 'white',
              borderRadius: '15px',
              boxShadow: '0 8px 25px rgba(99, 102, 241, 0.3)'
            }}>
              <div style={{ fontSize: '2.5em', marginBottom: '10px' }}>🧠</div>
              <h3 style={{ margin: '0 0 10px 0' }}>Intelligence</h3>
              <p style={{ fontSize: '2.5em', margin: '0', fontWeight: 'bold' }}>
                {analysis.summary.latest_attempt.intelligence_score}
              </p>
              <p style={{ margin: '5px 0 0 0', opacity: 0.8 }}>
                out of {analysis.attempts[0]?.scores?.intelligence_total || 4} questions
              </p>
            </div>
            
            <div style={{ 
              textAlign: 'center', 
              padding: '25px', 
              background: analysis.summary.latest_attempt.physical_score === 1 
                ? 'linear-gradient(135deg, #10b981, #059669)' 
                : 'linear-gradient(135deg, #ef4444, #dc2626)',
              color: 'white',
              borderRadius: '15px',
              boxShadow: '0 8px 25px rgba(16, 185, 129, 0.3)'
            }}>
              <div style={{ fontSize: '2.5em', marginBottom: '10px' }}>💪</div>
              <h3 style={{ margin: '0 0 10px 0' }}>Physical</h3>
              <p style={{ fontSize: '2.5em', margin: '0', fontWeight: 'bold' }}>
                {analysis.summary.latest_attempt.physical_score}
              </p>
              <p style={{ margin: '5px 0 0 0', opacity: 0.8 }}>
                {analysis.summary.latest_attempt.physical_score === 1 ? 'Successfully Completed' : 'Not Completed'}
              </p>
            </div>
            
            <div style={{ 
              textAlign: 'center', 
              padding: '25px', 
              background: analysis.summary.latest_attempt.linguistic_score === 1 
                ? 'linear-gradient(135deg, #10b981, #059669)' 
                : 'linear-gradient(135deg, #ef4444, #dc2626)',
              color: 'white',
              borderRadius: '15px',
              boxShadow: '0 8px 25px rgba(245, 158, 11, 0.3)'
            }}>
              <div style={{ fontSize: '2.5em', marginBottom: '10px' }}>🗣️</div>
              <h3 style={{ margin: '0 0 10px 0' }}>Linguistic</h3>
              <p style={{ fontSize: '2.5em', margin: '0', fontWeight: 'bold' }}>
                {analysis.summary.latest_attempt.linguistic_score}
              </p>
              <p style={{ margin: '5px 0 0 0', opacity: 0.8 }}>
                {analysis.summary.latest_attempt.linguistic_score === 1 ? 'Successfully Completed' : 'Not Completed'}
              </p>
            </div>

            <div style={{ 
              textAlign: 'center', 
              padding: '25px', 
              background: 'linear-gradient(135deg, #ec4899, #be185d)',
              color: 'white',
              borderRadius: '15px',
              boxShadow: '0 8px 25px rgba(236, 72, 153, 0.3)'
            }}>
              <div style={{ fontSize: '2.5em', marginBottom: '10px' }}>🎯</div>
              <h3 style={{ margin: '0 0 10px 0' }}>Total Score</h3>
              <p style={{ fontSize: '2.5em', margin: '0', fontWeight: 'bold' }}>
                {analysis.summary.latest_attempt.total_score}/{analysis.summary.latest_attempt.max_score}
              </p>
              <p style={{ margin: '5px 0 0 0', opacity: 0.8 }}>
                Latest attempt
              </p>
            </div>
          </div>
        </div>
      )}

      {/* All Attempts */}
      <div>
        <h2 style={{ textAlign: 'center', marginBottom: '30px', color: '#374151' }}>
          📋 All Assessment Attempts
        </h2>
        
        {analysis.attempts.map((attempt, attemptIndex) => (
          <div key={attempt.result_id} style={{
            marginBottom: '40px',
            border: '3px solid #e0e4e7',
            borderRadius: '20px',
            overflow: 'hidden',
            boxShadow: '0 10px 30px rgba(0,0,0,0.1)'
          }}>
            {/* Attempt Header */}
            <div style={{
              background: attemptIndex === 0 
                ? 'linear-gradient(135deg, #10b981, #059669)' 
                : 'linear-gradient(135deg, #6b7280, #4b5563)',
              color: 'white',
              padding: '20px',
              textAlign: 'center'
            }}>
              <h3 style={{ margin: '0 0 10px 0', fontSize: '1.4em' }}>
                {attemptIndex === 0 ? '🌟 Latest Attempt' : `📅 Attempt #${attempt.attempt_number}`}
              </h3>
              <p style={{ margin: 0, opacity: 0.9 }}>
                Date: {new Date(attempt.assessment_date).toLocaleDateString('en-US', {
                  year: 'numeric',
                  month: 'short',
                  day: 'numeric',
                  hour: '2-digit',
                  minute: '2-digit'
                })} • 
                Age Group: {attempt.age_group} years • 
                Score: {attempt.scores.total}/{attempt.scores.max_total} 
                ({Math.round((attempt.scores.total / attempt.scores.max_total) * 100)}%)
              </p>
            </div>

            <div style={{ padding: '30px' }}>
              {/* Attempt Score Summary */}
              <div style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))',
                gap: '15px',
                marginBottom: '30px'
              }}>
                <div style={{ textAlign: 'center', padding: '15px', background: '#f8f9fa', borderRadius: '10px' }}>
                  <div style={{ fontSize: '1.8em', fontWeight: 'bold', color: '#6366f1' }}>
                    {attempt.scores.intelligence}/{attempt.scores.intelligence_total}
                  </div>
                  <div style={{ fontSize: '0.9em', color: '#666' }}>
                    Intelligence ({attempt.scores.intelligence_percentage}%)
                  </div>
                  <div style={{ fontSize: '0.8em', color: '#999', marginTop: '5px' }}>
                    {attempt.scores.intelligence} correct answers
                  </div>
                </div>
                
                <div style={{ textAlign: 'center', padding: '15px', background: '#f8f9fa', borderRadius: '10px' }}>
                  <div style={{ fontSize: '1.8em', fontWeight: 'bold', color: '#10b981' }}>
                    {attempt.scores.physical}/1
                  </div>
                  <div style={{ fontSize: '0.9em', color: '#666' }}>Physical</div>
                  <div style={{ fontSize: '0.8em', color: '#999', marginTop: '5px' }}>
                    {attempt.scores.physical === 1 ? 'Task completed' : 'Task failed/skipped'}
                  </div>
                </div>
                
                <div style={{ textAlign: 'center', padding: '15px', background: '#f8f9fa', borderRadius: '10px' }}>
                  <div style={{ fontSize: '1.8em', fontWeight: 'bold', color: '#f59e0b' }}>
                    {attempt.scores.linguistic}/1
                  </div>
                  <div style={{ fontSize: '0.9em', color: '#666' }}>Linguistic</div>
                  <div style={{ fontSize: '0.8em', color: '#999', marginTop: '5px' }}>
                    {attempt.scores.linguistic === 1 ? 'Task completed' : 'Task failed/skipped'}
                  </div>
                </div>
                
                <div style={{ textAlign: 'center', padding: '15px', background: '#e3f2fd', borderRadius: '10px' }}>
                  <div style={{ fontSize: '1.8em', fontWeight: 'bold', color: '#1976d2' }}>
                    {attempt.scores.total}/{attempt.scores.max_total}
                  </div>
                  <div style={{ fontSize: '0.9em', color: '#666' }}>Total Score</div>
                  <div style={{ fontSize: '0.8em', color: '#999', marginTop: '5px' }}>
                    {Math.round((attempt.scores.total / attempt.scores.max_total) * 100)}% overall
                  </div>
                </div>
              </div>

              {/* Intelligence Questions for this attempt */}
              <div style={{ marginBottom: '30px' }}>
                <h4 style={{ color: '#374151', marginBottom: '15px' }}>🧠 Intelligence Questions</h4>
                {attempt.intelligence_responses.length > 0 ? (
                  <div style={{ display: 'grid', gap: '10px' }}>
                    {attempt.intelligence_responses.map((response, index) => (
                      <div key={response.response_id} style={{
                        background: 'white',
                        borderRadius: '8px',
                        padding: '15px',
                        border: `2px solid ${response.is_correct ? '#10b981' : '#ef4444'}`
                      }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                          <strong>Q{index + 1}: {response.question_text || 'Question not available'}</strong>
                          <span>{response.is_correct ? '✅' : '❌'}</span>
                        </div>
                        <div style={{ marginTop: '8px', fontSize: '0.9em', color: '#666' }}>
                          <div><strong>Child's Answer:</strong> {response.child_answer || 'No answer provided'}</div>
                          <div><strong>Correct Answer:</strong> {response.correct_answer || 'Not available'}</div>
                          <div style={{ marginTop: '5px', fontSize: '0.8em' }}>
                            <span>Response Time: {response.response_time || 0}s</span> | 
                            <span> Difficulty: {response.difficulty_level || 1}</span> | 
                            <span> Attempts: {response.attempts || 1}</span>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div style={{ 
                    textAlign: 'center', 
                    padding: '20px', 
                    background: '#f8f9fa', 
                    borderRadius: '8px',
                    color: '#666'
                  }}>
                    No intelligence questions recorded for this attempt
                  </div>
                )}
              </div>

              {/* AI Tasks for this attempt */}
              <div>
                <h4 style={{ color: '#374151', marginBottom: '15px' }}>🚀 Development Tasks</h4>
                {attempt.ai_tasks.length > 0 ? (
                  <div style={{ display: 'grid', gap: '15px' }}>
                    {attempt.ai_tasks.map((task, index) => (
                      <div key={index} style={{
                        background: 'white',
                        borderRadius: '10px',
                        padding: '20px',
                        border: `2px solid ${task.success === 1 ? '#10b981' : task.was_skipped ? '#f59e0b' : '#ef4444'}`
                      }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
                          <h5 style={{ margin: 0, color: '#374151' }}>
                            {task.task_type === 'physical' || task.task_type === 'physical_assessment' 
                              ? 'Physical Development Assessment'
                              : task.task_type === 'linguistic' || task.task_type === 'linguistic_assessment'
                              ? 'Linguistic Development Assessment'
                              : task.description || task.task_name || 'Development Task'}
                          </h5>
                          <span style={{
                            padding: '6px 12px',
                            borderRadius: '15px',
                            fontSize: '0.8em',
                            fontWeight: 'bold',
                            backgroundColor: task.was_skipped 
                              ? '#f59e0b' 
                              : (task.success === 1 && task.was_completed) 
                              ? '#10b981' 
                              : '#ef4444',
                            color: 'white'
                          }}>
                            {task.was_skipped 
                              ? 'Skipped' 
                              : (task.success === 1 && task.was_completed) 
                              ? 'Successfully Completed' 
                              : task.was_completed 
                              ? 'Attempted but Failed'
                              : 'Not Attempted'}
                          </span>
                        </div>
                        
                        <div style={{ fontSize: '0.9em', color: '#666', marginBottom: '10px' }}>
                          <div><strong>Assessment Type:</strong> {
                            task.task_type === 'physical' || task.task_type === 'physical_assessment' 
                              ? 'Physical Development' 
                              : task.task_type === 'linguistic' || task.task_type === 'linguistic_assessment'
                              ? 'Linguistic Development'
                              : task.task_type?.replace('_', ' ').toUpperCase() || 'Development Task'
                          }</div>
                          <div><strong>Task Details:</strong> {task.task_name || 'Standard assessment task'}</div>
                          <div><strong>Status:</strong> {
                            task.was_skipped 
                              ? 'Task was skipped by user'
                              : task.was_completed 
                              ? `Task was completed (${task.success === 1 ? 'successful' : 'unsuccessful'})`
                              : 'Task was not attempted'
                          }</div>
                          {(task.completion_time && task.completion_time > 0) && (
                            <div><strong>Duration:</strong> {task.completion_time}s</div>
                          )}
                        </div>
                        
                        <div style={{ marginTop: '15px' }}>
                          <div style={{ 
                            display: 'flex', 
                            justifyContent: 'space-between', 
                            alignItems: 'center',
                            background: task.success === 1 ? '#e8f5e8' : '#ffeaea',
                            padding: '15px',
                            borderRadius: '10px',
                            border: `2px solid ${task.success === 1 ? '#10b981' : '#ef4444'}`
                          }}>
                            <div style={{ textAlign: 'center', flex: 1 }}>
                              <div style={{ 
                                fontSize: '3em', 
                                fontWeight: 'bold',
                                color: task.success === 1 ? '#10b981' : '#ef4444'
                              }}>
                                {task.success === 1 ? '✅' : '❌'}
                              </div>
                              <div style={{ fontSize: '1.2em', fontWeight: 'bold', color: '#374151' }}>
                                Score: {task.success}/1
                              </div>
                              <div style={{ fontSize: '0.9em', color: '#666', marginTop: '5px' }}>
                                {task.success === 1 ? 'Task Successful' : 'Task Not Successful'}
                              </div>
                            </div>
                            
                            <div style={{ textAlign: 'center', flex: 1 }}>
                              <div style={{ fontSize: '1.5em', marginBottom: '8px' }}>
                                {task.was_completed ? '✅' : '⏸️'}
                              </div>
                              <div style={{ fontSize: '1.1em', fontWeight: 'bold', color: '#374151' }}>
                                {task.was_completed ? 'Completed' : 'Not Completed'}
                              </div>
                              <div style={{ fontSize: '0.9em', color: '#666', marginTop: '5px' }}>
                                {task.was_skipped 
                                  ? 'User chose to skip' 
                                  : task.was_completed 
                                  ? 'User attempted task'
                                  : 'Task not attempted'}
                              </div>
                            </div>
                          </div>
                        </div>
                        
                        {task.ai_feedback && (
                          <div style={{ 
                            marginTop: '10px', 
                            padding: '10px', 
                            background: '#e0f2fe', 
                            borderRadius: '8px',
                            fontSize: '0.9em',
                            color: '#0277bd'
                          }}>
                            <strong>AI Feedback:</strong> {task.ai_feedback}
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                ) : (
                  <div style={{ 
                    textAlign: 'center', 
                    padding: '20px', 
                    background: '#f8f9fa', 
                    borderRadius: '8px',
                    color: '#666'
                  }}>
                    No AI tasks recorded for this attempt
                  </div>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
