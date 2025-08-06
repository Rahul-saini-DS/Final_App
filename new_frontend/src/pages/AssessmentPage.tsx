import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import CameraAssessment from '../components/ai/CameraAssessment';
import VoiceAssessment from '../components/ai/VoiceAssessment';
import axios from 'axios';

const API_BASE_URL = 'http://localhost:5000/api';

interface Question {
  id: string;
  category: string;
  question: string;
  options: string[];
  image?: string;
  interaction?: string;
  points: number;
}

interface Task {
  task: string;
  title: string;
  description: string;
  instruction: string;
  type: string;
  icon: string;
  target_words?: string[];
}

export default function AssessmentPage() {
  const [ageGroup, setAgeGroup] = useState<string>('0-1');
  const [currentStep, setCurrentStep] = useState<number>(0);
  const [intelligenceQuestions, setIntelligenceQuestions] = useState<Question[]>([]);
  const [physicalTask, setPhysicalTask] = useState<Task | null>(null);
  const [linguisticTask, setLinguisticTask] = useState<Task | null>(null);
  const [answers, setAnswers] = useState<{ [key: string]: number }>({});
  const [scores, setScores] = useState({
    intelligence: 0,
    physical: 0,
    linguistic: 0
  });
  const [taskStates, setTaskStates] = useState({
    physical: { attempted: false, skipped: false, successCount: 0 },
    linguistic: { attempted: false, skipped: false, successCount: 0 }
  });
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string>('');
  
  const { isAuthenticated } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    if (!isAuthenticated) {
      navigate('/login');
    }
  }, [isAuthenticated, navigate]);

  useEffect(() => {
    loadAssessmentData();
  }, [ageGroup]);

  const loadAssessmentData = async () => {
    setLoading(true);
    setError('');
    
    try {
      // Load real Streamlit intelligence questions
      const questionsResponse = await axios.get(`${API_BASE_URL}/questions/${ageGroup}`);
      setIntelligenceQuestions(questionsResponse.data.questions);

      // Load physical task
      const physicalResponse = await axios.get(`${API_BASE_URL}/physical/${ageGroup}`);
      setPhysicalTask(physicalResponse.data.task);

      // Load linguistic task
      const linguisticResponse = await axios.get(`${API_BASE_URL}/linguistic/${ageGroup}`);
      setLinguisticTask(linguisticResponse.data.task);

    } catch (err: any) {
      console.error('Error loading assessment data:', err);
      setError('Failed to load assessment data. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleAnswerSelect = (questionId: string, optionIndex: number) => {
    setAnswers(prev => ({
      ...prev,
      [questionId]: optionIndex
    }));
  };

  const handleSubmitIntelligence = () => {
    // Calculate intelligence score based on CORRECT answers, not total answers
    const correctAnswers = Object.entries(answers).filter(([, optionIndex]) => {
      // Find the question and check if the selected option is correct (assuming index 0 is correct)
      return optionIndex === 0;
    }).length;
    
    // Store the actual number of correct answers (not normalized)
    setScores(prev => ({ ...prev, intelligence: correctAnswers }));
    setCurrentStep(prev => prev + 1);
  };

  const handleSubmitAssessment = async () => {
    try {
      // Calculate final scores to ensure consistency (don't rely on state timing)
      const finalIntelligenceScore = scores.intelligence;
      const finalPhysicalScore = (taskStates.physical.attempted && !taskStates.physical.skipped && taskStates.physical.successCount >= 5) ? 1 : 0;
      const finalLinguisticScore = (taskStates.linguistic.attempted && !taskStates.linguistic.skipped && taskStates.linguistic.successCount >= 1) ? 1 : 0;
      const totalScore = finalIntelligenceScore + finalPhysicalScore + finalLinguisticScore;
      
      // Prepare detailed intelligence responses
      const intelligenceResponses = Object.entries(answers).map(([questionId, optionIndex]) => {
        const question = intelligenceQuestions.find(q => q.id === questionId);
        const selectedOption = question?.options[optionIndex] || 'Unknown';
        const correctAnswer = question?.options[0] || 'Unknown'; // Assuming first option is correct
        
        return {
          question_id: questionId,
          question: question?.question || 'Unknown question',
          user_answer: selectedOption,
          correct_answer: correctAnswer,
          correct: optionIndex === 0, // Assuming first option (index 0) is always correct
          response_time: 30, // Default response time (you can track this with timestamps)
          difficulty: 1,
          attempts: 1
        };
      });
      
      // Prepare physical task details with correct state tracking
      const physicalDetails = {
        task_type: 'physical_assessment',
        task_name: 'Physical Development Assessment',
        success_count: taskStates.physical.successCount, // Use actual success count
        total_attempts: taskStates.physical.attempted ? 1 : 0,
        completion_time: taskStates.physical.attempted ? 30 : 0,
        success_rate: taskStates.physical.attempted ? (finalPhysicalScore > 0 ? 1 : 0) : 0,
        feedback: taskStates.physical.skipped 
          ? 'Physical task was skipped' 
          : finalPhysicalScore > 0
          ? 'Successfully completed physical task' 
          : taskStates.physical.attempted 
          ? 'Physical task attempted but not completed successfully'
          : 'Physical task not attempted',
        completed: finalPhysicalScore > 0, // ONLY completed if actually successful
        skipped: taskStates.physical.skipped
      };
      
      // Prepare linguistic task details with correct state tracking
      const linguisticDetails = {
        task_type: 'linguistic_assessment', 
        task_name: 'Linguistic Development Assessment',
        success_count: taskStates.linguistic.successCount, // Use actual success count
        total_attempts: taskStates.linguistic.attempted ? 1 : 0,
        completion_time: taskStates.linguistic.attempted ? 20 : 0,
        success_rate: taskStates.linguistic.attempted ? (finalLinguisticScore > 0 ? 1 : 0) : 0,
        feedback: taskStates.linguistic.skipped 
          ? 'Linguistic task was skipped' 
          : finalLinguisticScore > 0
          ? 'Successfully completed linguistic task' 
          : taskStates.linguistic.attempted 
          ? 'Linguistic task attempted but not completed successfully'
          : 'Linguistic task not attempted',
        completed: finalLinguisticScore > 0, // ONLY completed if actually successful
        skipped: taskStates.linguistic.skipped
      };
      
      const response = await axios.post(`${API_BASE_URL}/submit-assessment`, {
        age_group: ageGroup,
        intelligence_score: finalIntelligenceScore,
        physical_score: finalPhysicalScore,  // Use calculated final score
        linguistic_score: finalLinguisticScore,  // Use calculated final score
        total_score: totalScore,
        // New: Include detailed responses
        intelligence_responses: intelligenceResponses,
        physical_details: physicalDetails,
        linguistic_details: linguisticDetails
      });

      const navigateData = { 
        scores: {
          intelligence: finalIntelligenceScore,
          physical: finalPhysicalScore,  // Use calculated final score
          linguistic: finalLinguisticScore  // Use calculated final score
        },
        totalScore: totalScore,
        maxScore: intelligenceQuestions.length + 2, // Correct max score: intelligence questions + 2 binary tasks
        ageGroup: ageGroup,
        childId: response.data.child_id,
        resultId: response.data.result_id
      };

      // DEBUG: Log what we're sending
      console.log('AssessmentPage sending to ResultsPage:', navigateData);

      navigate('/results', { state: navigateData });
    } catch (err) {
      setError('Failed to submit assessment. Please try again.');
    }
  };

  if (loading) {
    return (
      <div className="container">
        <div className="loading">Loading assessment...</div>
      </div>
    );
  }

  const renderAgeSelection = () => (
    <div className="card">
      <h2 style={{ marginBottom: '20px', color: '#667eea' }}>Select Age Group</h2>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '15px' }}>
        {['0-1', '1-2', '2-3', '3-4', '4-5', '5-6'].map((age) => (
          <button
            key={age}
            className={`option-btn ${ageGroup === age ? 'selected' : ''}`}
            onClick={() => setAgeGroup(age)}
          >
            {age} years
          </button>
        ))}
      </div>
      <button 
        className="btn btn-primary" 
        style={{ marginTop: '20px', width: '100%' }}
        onClick={() => setCurrentStep(1)}
      >
        Start Assessment
      </button>
    </div>
  );

  const renderIntelligenceQuestions = () => (
    <div className="card">
      <h2 style={{ marginBottom: '20px', color: '#667eea' }}>
        Intelligence Questions (Age {ageGroup})
      </h2>
      <p style={{ marginBottom: '30px', color: '#666' }}>
        These are real questions from our Streamlit assessment system
      </p>
      
      {intelligenceQuestions.map((question, index) => (
        <div key={question.id} className="question-card">
          <h3 style={{ marginBottom: '15px', color: '#333' }}>
            {index + 1}. {question.question}
          </h3>
          <p style={{ marginBottom: '15px', fontSize: '14px', color: '#667eea' }}>
            Category: {question.category.replace('_', ' ').toUpperCase()}
          </p>
          
          <div style={{ display: 'grid', gap: '10px' }}>
            {question.options.map((option, optionIndex) => (
              <button
                key={optionIndex}
                className={`option-btn ${answers[question.id] === optionIndex ? 'selected' : ''}`}
                onClick={() => handleAnswerSelect(question.id, optionIndex)}
              >
                {option}
              </button>
            ))}
          </div>
        </div>
      ))}
      
      <button 
        className="btn btn-primary" 
        style={{ marginTop: '20px', width: '100%' }}
        onClick={handleSubmitIntelligence}
        disabled={Object.keys(answers).length !== intelligenceQuestions.length}
      >
        Continue to Physical Assessment
      </button>
    </div>
  );

  const renderPhysicalTask = () => (
    <div className="card">
      <h2 style={{ marginBottom: '20px', color: '#667eea' }}>Physical Assessment</h2>
      {physicalTask && (
        <CameraAssessment
          taskType={physicalTask.task}
          title={physicalTask.title}
          description={physicalTask.description}
          instruction={physicalTask.instruction}
          onComplete={(success, successCount = 0) => {
            setTaskStates(prev => ({ 
              ...prev, 
              physical: { 
                attempted: true, 
                skipped: false, 
                successCount: successCount 
              } 
            }));
            // Set score based on actual success AND success count (matches backend logic)
            const physicalScore = (success && successCount >= 5) ? 1 : 0;
            setScores(prev => ({ ...prev, physical: physicalScore }));
            setCurrentStep(prev => prev + 1);
          }}
          onSkip={() => {
            setTaskStates(prev => ({ 
              ...prev, 
              physical: { attempted: false, skipped: true, successCount: 0 } 
            }));
            setCurrentStep(prev => prev + 1);
          }}
        />
      )}
    </div>
  );

  const renderLinguisticTask = () => (
    <div className="card">
      <h2 style={{ marginBottom: '20px', color: '#667eea' }}>Linguistic Assessment</h2>
      {linguisticTask && (
        <VoiceAssessment
          title={linguisticTask.title}
          description={linguisticTask.description}
          instruction={linguisticTask.instruction}
          targetWords={linguisticTask.target_words || []}
          taskType={linguisticTask.task}
          onComplete={(success, _transcript, successCount = 0) => {
            setTaskStates(prev => ({ 
              ...prev, 
              linguistic: { 
                attempted: true, 
                skipped: false, 
                successCount: successCount 
              } 
            }));
            // Set score based on actual success AND success count (matches backend logic)
            const linguisticScore = (success && successCount >= 1) ? 1 : 0;
            setScores(prev => ({ ...prev, linguistic: linguisticScore }));
            setCurrentStep(prev => prev + 1);
          }}
          onSkip={() => {
            setTaskStates(prev => ({ 
              ...prev, 
              linguistic: { attempted: false, skipped: true, successCount: 0 } 
            }));
            setCurrentStep(prev => prev + 1);
          }}
        />
      )}
    </div>
  );

  const renderSummary = () => {
    // Calculate final scores for display consistency
    const displayPhysicalScore = (taskStates.physical.attempted && !taskStates.physical.skipped && taskStates.physical.successCount >= 5) ? 1 : 0;
    const displayLinguisticScore = (taskStates.linguistic.attempted && !taskStates.linguistic.skipped && taskStates.linguistic.successCount >= 1) ? 1 : 0;
    const displayTotalScore = scores.intelligence + displayPhysicalScore + displayLinguisticScore;

    return (
    <div className="card">
      <h2 style={{ marginBottom: '20px', color: '#667eea' }}>Assessment Complete!</h2>
      
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '20px', marginBottom: '30px' }}>
        <div style={{ textAlign: 'center', padding: '20px', background: '#f8f9ff', borderRadius: '10px' }}>
          <h3 style={{ color: '#667eea' }}>Intelligence</h3>
          <p style={{ fontSize: '2em', margin: '10px 0', color: scores.intelligence >= 3 ? '#4CAF50' : scores.intelligence >= 2 ? '#FF9800' : '#FF5722' }}>
            {scores.intelligence}/{intelligenceQuestions.length} {scores.intelligence >= 3 ? '✅' : scores.intelligence >= 2 ? '⚠️' : '❌'}
          </p>
          <p style={{ color: '#666', fontSize: '0.9em' }}>
            {scores.intelligence >= 3 ? 'Excellent cognitive skills!' : 
             scores.intelligence >= 2 ? 'Good progress, keep practicing!' : 
             scores.intelligence >= 1 ? 'Some correct answers' :
             'Try answering more questions next time'}
          </p>
        </div>
        
        <div style={{ textAlign: 'center', padding: '20px', background: '#f8f9ff', borderRadius: '10px' }}>
          <h3 style={{ color: '#667eea' }}>Physical</h3>
          <p style={{ fontSize: '2em', margin: '10px 0', color: displayPhysicalScore ? '#4CAF50' : '#FF5722' }}>
            {displayPhysicalScore}/1 {displayPhysicalScore ? '✅' : '❌'}
          </p>
          <p style={{ color: '#666', fontSize: '0.9em' }}>
            {displayPhysicalScore ? 'Great motor skills!' : 'Development Task: Failed or Skipped'}
          </p>
        </div>
        
        <div style={{ textAlign: 'center', padding: '20px', background: '#f8f9ff', borderRadius: '10px' }}>
          <h3 style={{ color: '#667eea' }}>Linguistic</h3>
          <p style={{ fontSize: '2em', margin: '10px 0', color: displayLinguisticScore ? '#4CAF50' : '#FF5722' }}>
            {displayLinguisticScore}/1 {displayLinguisticScore ? '✅' : '❌'}
          </p>
          <p style={{ color: '#666', fontSize: '0.9em' }}>
            {displayLinguisticScore ? 'Excellent communication!' : 'Development Task: Failed or Skipped'}
          </p>
        </div>
      </div>
      
      <div style={{ textAlign: 'center', padding: '25px', background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', borderRadius: '15px', color: 'white', marginBottom: '20px' }}>
        <h2 style={{ margin: '0 0 10px 0' }}>Total Score</h2>
        <p style={{ fontSize: '3em', margin: '0', fontWeight: 'bold' }}>
          {displayTotalScore}/{intelligenceQuestions.length + 2}
        </p>
        <small style={{ opacity: 0.9 }}>This Assessment • Max possible: {intelligenceQuestions.length + 2} points</small>
      </div>
      
      <button 
        className="btn btn-primary" 
        style={{ width: '100%' }}
        onClick={handleSubmitAssessment}
      >
        Submit Assessment & View Results
      </button>
    </div>
  )};

  return (
    <div className="container">
      {error && <div className="error">{error}</div>}
      
      {/* Progress Bar */}
      <div className="progress-bar">
        <div 
          className="progress-fill" 
          style={{ width: `${(currentStep / 4) * 100}%` }}
        />
      </div>
      
      {currentStep === 0 && renderAgeSelection()}
      {currentStep === 1 && renderIntelligenceQuestions()}
      {currentStep === 2 && renderPhysicalTask()}
      {currentStep === 3 && renderLinguisticTask()}
      {currentStep === 4 && renderSummary()}
    </div>
  );
}
