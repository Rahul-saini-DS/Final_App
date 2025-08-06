import { useState, useRef } from 'react';

interface VoiceAssessmentProps {
  title: string;
  description: string;
  instruction: string;
  targetWords: string[];
  taskType: string;
  onComplete: (success: boolean, transcript?: string, successCount?: number) => void;
  onSkip: () => void;
}

export default function VoiceAssessment({
  title,
  description,
  instruction,
  targetWords,
  taskType,
  onComplete,
  onSkip
}: VoiceAssessmentProps) {
  const [isRecording, setIsRecording] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [message, setMessage] = useState('Click the microphone to start recording');
  const [transcript, setTranscript] = useState('');
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);

  const startRecording = async () => {
    try {
      console.log('Starting audio recording...');
      
      const stream = await navigator.mediaDevices.getUserMedia({ 
        audio: { 
          sampleRate: 16000, // Match Vosk requirements
          channelCount: 1,   // Mono audio
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true
        } 
      });
      
      console.log('Audio stream obtained:', stream.getAudioTracks()[0].getSettings());
      
      // Check if browser supports the required format
      let mimeType = 'audio/webm;codecs=opus';
      if (!MediaRecorder.isTypeSupported(mimeType)) {
        mimeType = 'audio/webm';
        console.log('Opus codec not supported, using default webm');
      }
      if (!MediaRecorder.isTypeSupported(mimeType)) {
        mimeType = 'audio/wav';
        console.log('WebM not supported, trying WAV');
      }
      
      const mediaRecorder = new MediaRecorder(stream, {
        mimeType: mimeType
      });
      
      console.log('MediaRecorder created with mimeType:', mimeType);
      
      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];
      
      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          console.log('Audio chunk received:', event.data.size, 'bytes');
          audioChunksRef.current.push(event.data);
        }
      };
      
      mediaRecorder.onstop = () => {
        console.log('Recording stopped, total chunks:', audioChunksRef.current.length);
        processAudio();
        stream.getTracks().forEach(track => track.stop());
      };
      
      mediaRecorder.onerror = (event) => {
        console.error('MediaRecorder error:', event);
        setMessage('Recording error occurred. Please try again.');
        setIsRecording(false);
      };
      
      mediaRecorder.start(100); // Collect data every 100ms
      setIsRecording(true);
      setMessage('🎙️ Recording... Speak now!');
      
      // Auto-stop after 5 seconds with countdown
      let countdown = 5;
      const countdownInterval = setInterval(() => {
        countdown--;
        if (countdown > 0) {
          setMessage(`🎙️ Recording... ${countdown} seconds left`);
        } else {
          clearInterval(countdownInterval);
        }
      }, 1000);
      
      setTimeout(() => {
        if (mediaRecorderRef.current && mediaRecorderRef.current.state === 'recording') {
          console.log('Auto-stopping recording after 5 seconds');
          mediaRecorderRef.current.stop();
          setIsRecording(false);
        }
        clearInterval(countdownInterval);
      }, 5000);
      
    } catch (error) {
      console.error('Error accessing microphone:', error);
      setMessage('Microphone access denied. Please allow microphone permission and try again.');
      setIsRecording(false);
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  };

  const processAudio = async () => {
    setIsProcessing(true);
    setMessage('🤖 AI is analyzing your speech...');
    
    try {
      console.log('Processing audio chunks:', audioChunksRef.current.length);
      
      if (audioChunksRef.current.length === 0) {
        throw new Error('No audio data recorded');
      }
      
      const audioBlob = new Blob(audioChunksRef.current, { 
        type: audioChunksRef.current[0].type || 'audio/webm' 
      });
      
      console.log('Audio blob created:', {
        size: audioBlob.size,
        type: audioBlob.type
      });
      
      if (audioBlob.size === 0) {
        throw new Error('Audio blob is empty');
      }
      
      // Convert to base64
      const reader = new FileReader();
      reader.onloadend = async () => {
        const base64Audio = reader.result as string;
        console.log('Audio converted to base64, length:', base64Audio.length);
        
        try {
          console.log('Sending audio to backend...');
          
          const controller = new AbortController();
          const timeoutId = setTimeout(() => controller.abort(), 30000); // 30 second timeout
          
          const response = await fetch('http://localhost:5000/api/ai/speech-assessment', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              audio: base64Audio,
              target_words: targetWords,
              task_type: taskType
            }),
            signal: controller.signal
          });
          
          clearTimeout(timeoutId);
          
          console.log('Response received:', response.status, response.statusText);
          
          if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            console.error('Backend error:', errorData);
            throw new Error(errorData.error || `Speech assessment failed (${response.status})`);
          }
          
          const result = await response.json();
          console.log('Speech assessment result:', result);
          
          setTranscript(result.transcript || '');
          setMessage(result.message || 'Assessment completed');
          
          setIsProcessing(false);
          
          // Show result for 3 seconds then complete
          setTimeout(() => {
            // Use actual success_count from backend if available, otherwise fallback to binary 1/0
            const successCount = result.success_count !== undefined ? result.success_count : (result.success ? 1 : 0);
            onComplete(result.success, result.transcript, successCount);
          }, 3000);
          
        } catch (error: any) {
          console.error('Speech assessment error:', error);
          
          if (error.name === 'AbortError') {
            setMessage('Speech assessment timed out. Please try again or skip.');
          } else {
            setMessage(`Speech assessment failed: ${error.message}. Please try again or skip.`);
          }
          
          setIsProcessing(false);
        }
      };
      
      reader.onerror = (error) => {
        console.error('FileReader error:', error);
        setMessage('Failed to process audio file. Please try again.');
        setIsProcessing(false);
      };
      
      reader.readAsDataURL(audioBlob);
      
    } catch (error: any) {
      console.error('Audio processing error:', error);
      setMessage(`Audio processing failed: ${error.message}. Please try again.`);
      setIsProcessing(false);
    }
  };

  return (
    <div style={{ textAlign: 'center', padding: '20px' }}>
      <h3 style={{ marginBottom: '15px', color: '#667eea' }}>{title}</h3>
      <p style={{ marginBottom: '15px', fontSize: '1.1em' }}>{description}</p>
      <p style={{ marginBottom: '20px', color: '#666', fontWeight: 'bold' }}>
        {instruction}
      </p>
      
      {targetWords.length > 0 && (
        <p style={{ marginBottom: '20px', fontSize: '14px', color: '#667eea' }}>
          Target words: {targetWords.join(', ')}
        </p>
      )}
      
      <div style={{
        width: '200px',
        height: '200px',
        margin: '20px auto',
        borderRadius: '50%',
        background: isRecording 
          ? 'linear-gradient(45deg, #ff6b6b, #ee5a52)' 
          : 'linear-gradient(45deg, #667eea, #764ba2)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        cursor: isProcessing ? 'not-allowed' : 'pointer',
        transition: 'all 0.3s ease',
        transform: isRecording ? 'scale(1.1)' : 'scale(1)',
        animation: isRecording ? 'pulse 1.5s infinite' : 'none'
      }}
      onClick={!isProcessing && !isRecording ? startRecording : stopRecording}
      >
        <div style={{ color: 'white', fontSize: '4em' }}>
          {isProcessing ? '🤖' : isRecording ? '🎙️' : '🎤'}
        </div>
      </div>
      
      <div style={{ 
        background: '#f8f9ff', 
        padding: '15px', 
        borderRadius: '8px', 
        marginBottom: '20px',
        minHeight: '50px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center'
      }}>
        <p style={{ margin: 0, fontWeight: '500' }}>{message}</p>
      </div>
      
      {transcript && (
        <div style={{ 
          background: '#e8f5e8', 
          padding: '15px', 
          borderRadius: '8px', 
          marginBottom: '20px',
          border: '2px solid #4caf50'
        }}>
          <p style={{ margin: 0, fontWeight: 'bold', color: '#2e7d32' }}>
            You said: "{transcript}"
          </p>
        </div>
      )}
      
      {isRecording && (
        <div style={{ marginBottom: '20px' }}>
          <div style={{
            width: '100%',
            height: '6px',
            background: '#e0e0e0',
            borderRadius: '3px',
            overflow: 'hidden'
          }}>
            <div style={{
              width: '100%',
              height: '100%',
              background: 'linear-gradient(90deg, #ff6b6b, #ee5a52)',
              animation: 'recording 5s linear forwards',
              borderRadius: '3px'
            }} />
          </div>
          <p style={{ marginTop: '10px', color: '#666' }}>
            Recording will stop automatically in 5 seconds
          </p>
        </div>
      )}
      
      <div style={{ display: 'flex', gap: '15px', justifyContent: 'center', flexWrap: 'wrap' }}>
        {isRecording && (
          <button 
            className="btn btn-secondary"
            onClick={stopRecording}
            style={{ fontSize: '1.1em', padding: '12px 24px' }}
          >
            ⏹️ Stop Recording
          </button>
        )}
        
        {!isRecording && !isProcessing && (
          <button 
            className="btn btn-primary"
            onClick={startRecording}
            style={{ fontSize: '1.1em', padding: '12px 24px' }}
          >
            🎙️ Start Recording
          </button>
        )}
        
        <button 
          className="btn btn-secondary"
          onClick={() => onSkip()}
          disabled={isRecording || isProcessing}
          style={{ fontSize: '1.1em', padding: '12px 24px' }}
        >
          Skip AI Assessment
        </button>
      </div>
      
      <style>
        {`
          @keyframes pulse {
            0% { box-shadow: 0 0 0 0 rgba(255, 107, 107, 0.7); }
            70% { box-shadow: 0 0 0 20px rgba(255, 107, 107, 0); }
            100% { box-shadow: 0 0 0 0 rgba(255, 107, 107, 0); }
          }
          
          @keyframes recording {
            0% { width: 0%; }
            100% { width: 100%; }
          }
        `}
      </style>
    </div>
  );
}
