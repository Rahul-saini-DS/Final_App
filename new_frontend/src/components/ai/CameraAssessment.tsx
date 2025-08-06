import { useRef, useEffect, useState } from 'react';

interface CameraAssessmentProps {
  taskType: string;
  title: string;
  description: string;
  instruction: string;
  onComplete: (success: boolean, successCount?: number) => void;
  onSkip: () => void;
}

export default function CameraAssessment({ 
  taskType, 
  title, 
  description, 
  instruction, 
  onComplete, 
  onSkip 
}: CameraAssessmentProps) {
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [isActive, setIsActive] = useState(false);
  const [message, setMessage] = useState('Click Start to begin assessment');
  const [stream, setStream] = useState<MediaStream | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [feedback, setFeedback] = useState<string>('');
  const [successCount, setSuccessCount] = useState(0);
  const [showFeedback, setShowFeedback] = useState(false);
  const intervalRef = useRef<number | null>(null);

  const startCamera = async () => {
    try {
      const mediaStream = await navigator.mediaDevices.getUserMedia({ 
        video: { width: 640, height: 480 } 
      });
      setStream(mediaStream);
      if (videoRef.current) {
        videoRef.current.srcObject = mediaStream;
        videoRef.current.play();
      }
      setIsActive(true);
      setMessage('Camera started. Follow the instruction below.');
      
      // Start assessment after camera is ready
      setTimeout(() => {
        startAssessment();
      }, 1000);
    } catch (error) {
      console.error('Error accessing camera:', error);
      setMessage('Camera access denied. Please allow camera permission.');
    }
  };

  const stopCamera = () => {
    // Clear any running interval first
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
    
    if (stream) {
      stream.getTracks().forEach(track => track.stop());
      setStream(null);
    }
    setIsActive(false);
    setIsProcessing(false);
  };

  const captureFrame = (): string | null => {
    if (!videoRef.current || !canvasRef.current) return null;
    
    const canvas = canvasRef.current;
    const context = canvas.getContext('2d');
    if (!context) return null;
    
    canvas.width = videoRef.current.videoWidth;
    canvas.height = videoRef.current.videoHeight;
    context.drawImage(videoRef.current, 0, 0);
    
    return canvas.toDataURL('image/jpeg', 0.8);
  };

  const startAssessment = async () => {
    setIsProcessing(true);
    setMessage('Assessment in progress...');
    setSuccessCount(0);
    setShowFeedback(false);
    
    let currentSuccessCount = 0;
    const requiredSuccessFrames = 5; // Reduced from 10 to 5
    let frameCount = 0;
    const maxFrames = 60; // 30 seconds at 2 FPS
    let isProcessingFrame = false; // Flag to prevent overlapping requests
    
    intervalRef.current = setInterval(async () => {
      // Skip if already processing a frame
      if (isProcessingFrame) {
        return;
      }
      
      frameCount++;
      isProcessingFrame = true;
      
      const frameData = captureFrame();
      if (!frameData) {
        if (intervalRef.current) {
          clearInterval(intervalRef.current);
          intervalRef.current = null;
        }
        setMessage('Error capturing video frame');
        setFeedback('❌ Camera error - please try again');
        setShowFeedback(true);
        setIsProcessing(false);
        isProcessingFrame = false;
        return;
      }
      
      try {
        const response = await fetch('http://localhost:5000/api/ai/physical-assessment', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            task_type: taskType,
            frame: frameData
          })
        });
        
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const result = await response.json();
        
        if (result.success) {
          currentSuccessCount++;
          setSuccessCount(currentSuccessCount);
          setMessage(`${result.message} (${currentSuccessCount}/${requiredSuccessFrames})`);
          setFeedback('✅ Great! Keep going!');
          
          if (currentSuccessCount >= requiredSuccessFrames) {
            if (intervalRef.current) {
              clearInterval(intervalRef.current);
              intervalRef.current = null;
            }
            setMessage('🎉 Assessment completed successfully!');
            setFeedback('🎉 Perfect! You completed the task successfully!');
            setShowFeedback(true);
            setIsProcessing(false);
            setTimeout(() => {
              stopCamera();
              onComplete(true, currentSuccessCount);
            }, 2000);
            isProcessingFrame = false;
            return;
          }
        } else {
          currentSuccessCount = Math.max(0, currentSuccessCount - 1); // Gradual decrease instead of reset
          setSuccessCount(currentSuccessCount);
          setMessage(result.message || 'Follow the instruction');
          setFeedback(getTaskSpecificFeedback(taskType, result.message));
        }
        
      } catch (error) {
        console.error('Assessment error:', error);
        setMessage('Assessment failed - trying again...');
        setFeedback('⚠️ Connection issue - retrying...');
        currentSuccessCount = Math.max(0, currentSuccessCount - 1);
        setSuccessCount(currentSuccessCount);
      }
      
      isProcessingFrame = false;
      
      // Timeout after maximum frames
      if (frameCount >= maxFrames) {
        if (intervalRef.current) {
          clearInterval(intervalRef.current);
          intervalRef.current = null;
        }
        setMessage('⏰ Time up! Try again or skip this assessment.');
        setFeedback('⏰ Time\'s up! Don\'t worry, you can try again or skip this task.');
        setShowFeedback(true);
        setIsProcessing(false);
        setTimeout(() => {
          stopCamera();
          // Pass actual success count even on timeout - backend will decide if it's enough
          onComplete(false, currentSuccessCount);
        }, 3000);
      }
    }, 500); // Process every 500ms (2 FPS) instead of 100ms
  };

  const getTaskSpecificFeedback = (taskType: string, message: string): string => {
    switch (taskType) {
      case 'raise_hands':
        return '🙌 Try raising both hands high above your head!';
      case 'one_leg':
        return '🦵 Try standing on one leg - use something for balance if needed!';
      case 'turn_around':
        return '🔄 Try turning around slowly in a circle!';
      case 'stand_still':
        return '🧘 Try standing very still without moving!';
      case 'frog_jump':
        return '🐸 Try jumping like a frog - squat and jump forward!';
      case 'kangaroo_jump':
        return '🦘 Try jumping with both feet together like a kangaroo!';
      default:
        return message || '🎯 Follow the instruction shown above';
    }
  };

  useEffect(() => {
    return () => {
      // Cleanup when component unmounts
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
      stopCamera();
    };
  }, []);

  return (
    <div style={{ textAlign: 'center', padding: '20px' }}>
      <h3 style={{ marginBottom: '15px', color: '#667eea' }}>{title}</h3>
      <p style={{ marginBottom: '15px', fontSize: '1.1em' }}>{description}</p>
      <p style={{ marginBottom: '20px', color: '#666', fontWeight: 'bold' }}>
        Instruction: {instruction}
      </p>
      
      <div style={{ position: 'relative', marginBottom: '20px' }}>
        <video
          ref={videoRef}
          style={{
            width: '100%',
            maxWidth: '640px',
            height: 'auto',
            border: '3px solid #667eea',
            borderRadius: '10px',
            backgroundColor: '#f0f0f0'
          }}
          muted
          playsInline
        />
        <canvas ref={canvasRef} style={{ display: 'none' }} />
        
        {!isActive && (
          <div style={{
            position: 'absolute',
            top: '50%',
            left: '50%',
            transform: 'translate(-50%, -50%)',
            background: 'rgba(0,0,0,0.7)',
            color: 'white',
            padding: '20px',
            borderRadius: '10px'
          }}>
            <p>📹 Camera Assessment</p>
            <p style={{ fontSize: '0.9em', marginTop: '10px' }}>
              Allow camera access to start
            </p>
          </div>
        )}
      </div>
      
      <div style={{ 
        background: '#f8f9ff', 
        padding: '15px', 
        borderRadius: '8px', 
        marginBottom: '20px',
        minHeight: '50px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        flexDirection: 'column'
      }}>
        <p style={{ margin: '0 0 10px 0', fontWeight: '500' }}>{message}</p>
        
        {isProcessing && (
          <div style={{ width: '100%', marginTop: '10px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '5px' }}>
              <span style={{ fontSize: '0.9em', color: '#666' }}>Progress: {successCount}/5</span>
              <span style={{ fontSize: '0.9em', color: '#667eea' }}>{Math.round((successCount / 5) * 100)}%</span>
            </div>
            <div style={{
              width: '100%',
              height: '6px',
              background: '#e0e0e0',
              borderRadius: '3px',
              overflow: 'hidden'
            }}>
              <div style={{
                width: `${(successCount / 5) * 100}%`,
                height: '100%',
                background: 'linear-gradient(90deg, #667eea, #764ba2)',
                borderRadius: '3px',
                transition: 'width 0.3s ease'
              }} />
            </div>
          </div>
        )}
        
        {showFeedback && feedback && (
          <div style={{ 
            marginTop: '10px', 
            padding: '8px 12px', 
            background: feedback.includes('✅') ? '#e8f5e8' : feedback.includes('❌') ? '#fde8e8' : '#fff3cd',
            border: `1px solid ${feedback.includes('✅') ? '#4CAF50' : feedback.includes('❌') ? '#f44336' : '#ff9800'}`,
            borderRadius: '6px',
            fontSize: '0.9em'
          }}>
            {feedback}
          </div>
        )}
      </div>
      
      <div style={{ display: 'flex', gap: '15px', justifyContent: 'center' }}>
        {!isActive && !isProcessing && (
          <button 
            className="btn btn-primary"
            onClick={startCamera}
            style={{ fontSize: '1.1em', padding: '12px 24px' }}
          >
            📹 Start Camera Assessment
          </button>
        )}
        
        {isActive && !isProcessing && (
          <button 
            className="btn btn-secondary"
            onClick={() => {
              stopCamera();
              onComplete(false);
            }}
          >
            Stop Assessment
          </button>
        )}
        
        <button 
          className="btn btn-secondary"
          onClick={() => {
            stopCamera();
            onSkip();
          }}
          disabled={isProcessing}
        >
          Skip AI Assessment
        </button>
      </div>
      
      {isProcessing && (
        <div style={{ marginTop: '15px' }}>
          <div style={{
            width: '100%',
            height: '4px',
            background: '#e0e0e0',
            borderRadius: '2px',
            overflow: 'hidden'
          }}>
            <div style={{
              width: '30%',
              height: '100%',
              background: 'linear-gradient(90deg, #667eea, #764ba2)',
              animation: 'loading 2s ease-in-out infinite',
              borderRadius: '2px'
            }} />
          </div>
          <p style={{ marginTop: '10px', color: '#666' }}>
            AI is analyzing your movement...
          </p>
        </div>
      )}
      
      <style>
        {`
          @keyframes loading {
            0% { transform: translateX(-100%); }
            50% { transform: translateX(0%); }
            100% { transform: translateX(100%); }
          }
        `}
      </style>
    </div>
  );
}
