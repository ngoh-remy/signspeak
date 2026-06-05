import React, { useEffect, useRef, useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { HF_WS_BASE_URL, apiFetch } from '../api';
import {
  Camera, CameraOff, Volume2, VolumeX, RefreshCw, AlertCircle, Play, Square,
  CheckCircle, History, MessageSquareCode, Sparkles, Send, Trash2, ArrowLeftRight
} from 'lucide-react';
import { translations } from '../translations';
import './Translate.css';

export default function Translate() {
  const { user, language } = useAuth();
  const t = translations[language].translate;
  const signsT = translations[language].signs;
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const streamRef = useRef(null);
  const wsRef = useRef(null);
  const intervalRef = useRef(null);
  const sessionIdRef = useRef(null);

  // States
  const [isActive, setIsActive] = useState(false);
  const [status, setStatus] = useState('OFFLINE'); 
  const [bufferedFrames, setBufferedFrames] = useState(0);
  const [maxFrames] = useState(20);
  const [predictions, setPredictions] = useState([]); // List of current session's recognized signs
  const [sentenceTokens, setSentenceTokens] = useState([]); // Array of raw sign tokens
  const [lastPrediction, setLastPrediction] = useState(null); // { rawSign, confidence, timestamp }
  const [isMuted, setIsMuted] = useState(false);
  const [facingMode, setFacingMode] = useState('user'); // 'user' for front, 'environment' for back
  const [historyItems, setHistoryItems] = useState([]);
  const [errorMsg, setErrorMsg] = useState('');

  // Fetch translation history from backend on load
  useEffect(() => {
    if (user) {
      fetchHistory();
    }
  }, [user]);

  const fetchHistory = async () => {
    try {
      const data = await apiFetch('/api/history');
      setHistoryItems((data?.items || []).slice(0, 10));
    } catch (err) {
      console.error('Failed to load history:', err);
    }
  };

  // Speaks text using Web Speech API
  const speakText = (text) => {
    if (isMuted || !text) return;
    try {
      window.speechSynthesis.cancel(); // cancel any active speech
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.rate = 1.0;
      utterance.pitch = 1.0;
      // Set language profile based on selected language
      utterance.lang = language === 'fr' ? 'fr-FR' : 'en-US';
      window.speechSynthesis.speak(utterance);
    } catch (e) {
      console.error('Text-to-speech failed:', e);
    }
  };

  // Start webcam and connect WebSocket
  const startSession = async () => {
    setErrorMsg('');
    setStatus('CONNECTING');
    try {
      // 1. Get webcam stream
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { width: 640, height: 480, frameRate: 15, facingMode: facingMode }
      });
      streamRef.current = stream;
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
      }

      // 2. Establish WebSocket connection
      // Construct WS query params: user_id and session_id
      const sessionId = Math.random().toString(36).substring(7);
      sessionIdRef.current = sessionId;

      const queryParams = new URLSearchParams();
      if (user) queryParams.append('user_id', user.id);
      queryParams.append('session_id', sessionId);

      const wsUrl = `${HF_WS_BASE_URL}/ws/recognize?${queryParams.toString()}`;
      const ws = new WebSocket(wsUrl);
      wsRef.current = ws;

      ws.onopen = () => {
        setIsActive(true);
        setStatus('READY');
      };

      ws.onmessage = (event) => {
        const data = JSON.parse(event.data);

        if (data.type === 'connected') {
          setStatus('READY');
        } else if (data.type === 'processing') {
          setBufferedFrames(data.frames_buffered);
          if (data.frames_buffered > 0 && data.frames_buffered < 20) {
            setStatus('PROCESSING');
          } else {
            setStatus('READY');
          }
        } else if (data.type === 'recognition') {
          // Translate the recognized sign if possible
          const recognizedSignLower = data.sign.toLowerCase();
          const translatedSign = signsT[recognizedSignLower] || data.sign;

          const pred = {
            rawSign: recognizedSignLower,
            confidence: data.confidence,
            timestamp: new Date(data.timestamp)
          };
          setLastPrediction(pred);
          setPredictions(prev => [pred, ...prev]);

          // Update sentence tokens
          setSentenceTokens(prev => [...prev, recognizedSignLower]);

          // Audio feedback
          speakText(translatedSign);

          // Reset status
          setBufferedFrames(0);
          setStatus('READY');

          // Sync recognition history to backend database via REST API
          if (user) {
            apiFetch(`/api/history/record?sign_label=${encodeURIComponent(recognizedSignLower)}&confidence=${data.confidence}&session_id=${sessionIdRef.current}`, {
              method: 'POST'
            })
            .then(() => {
              fetchHistory();
            })
            .catch(err => {
              console.error('Failed to sync history to backend:', err);
            });
          }
        } else if (data.type === 'error') {
          setErrorMsg(data.message);
          stopSession();
        }
      };

      ws.onerror = () => {
        setErrorMsg('WebSocket connection error. Please make sure the backend is running.');
        stopSession();
      };

      ws.onclose = () => {
        setStatus('OFFLINE');
        setIsActive(false);
        stopSession();
      };

      // 3. Start drawing and streaming frames
      const canvas = canvasRef.current;
      const context = canvas.getContext('2d');

      intervalRef.current = setInterval(() => {
        if (ws.readyState === WebSocket.OPEN && videoRef.current) {
          // Draw video frame on canvas
          context.drawImage(videoRef.current, 0, 0, canvas.width, canvas.height);

          // Export as JPEG blob and send raw bytes
          canvas.toBlob((blob) => {
            if (blob) {
              blob.arrayBuffer().then((buffer) => {
                if (ws.readyState === WebSocket.OPEN) {
                  ws.send(buffer);
                }
              });
            }
          }, 'image/jpeg', 0.6); // 60% quality compress for bandwidth efficiency
        }
      }, 100); // 10 FPS — do NOT increase this; faster rates cause MediaPipe timestamp ordering crashes

    } catch (err) {
      console.error(err);
      setErrorMsg('Webcam access denied. Please allow camera permissions.');
      setStatus('OFFLINE');
      setIsActive(false);
    }
  };

  // Close webcam and WebSocket
  const stopSession = () => {
    setIsActive(false);
    setStatus('OFFLINE');
    setBufferedFrames(0);

    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }

    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }

    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop());
      streamRef.current = null;
    }

    if (videoRef.current) {
      videoRef.current.srcObject = null;
    }
  };

  const switchCamera = async () => {
    const newMode = facingMode === 'user' ? 'environment' : 'user';
    setFacingMode(newMode);
    
    if (isActive) {
      try {
        if (streamRef.current) {
          streamRef.current.getTracks().forEach(track => track.stop());
        }
        const newStream = await navigator.mediaDevices.getUserMedia({
          video: { width: 640, height: 480, frameRate: 15, facingMode: newMode }
        });
        streamRef.current = newStream;
        if (videoRef.current) {
          videoRef.current.srcObject = newStream;
        }
      } catch (err) {
        console.error('Failed to switch camera:', err);
      }
    }
  };

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      stopSession();
    };
  }, []);

  const handleSpeakSentence = () => {
    const fullSentence = sentenceTokens.map(token => signsT[token] || token).join(' ');
    speakText(fullSentence);
  };

  const handleClearSentence = () => {
    setSentenceTokens([]);
    setLastPrediction(null);
    setPredictions([]);
  };

  const handleBackspace = () => {
    setSentenceTokens(prev => {
      const newTokens = [...prev];
      newTokens.pop();
      return newTokens;
    });
  };

  return (
    <div className="translate-page fade-in-up container">
      {/* Background Orbs */}
      <div className="bg-orb bg-orb-1"></div>
      <div className="bg-orb bg-orb-2"></div>

      <header className="translate-header">
        <div className="badge badge-primary">{t.engineTitle}</div>
        <h1>{t.realTime}<span className="text-gradient">{t.signInterpreter}</span></h1>
        <p className="translate-lead">
          {t.leadText}
        </p>
      </header>

      {errorMsg && (
        <div className="translate-error card">
          <AlertCircle size={20} className="error-icon" />
          <div>
            <h4>{t.systemError}</h4>
            <p>{errorMsg}</p>
          </div>
        </div>
      )}

      <div className="translate-layout">
        {/* Main Feed Column */}
        <div className="translate-main">
          {/* Camera Card */}
          <div className="camera-card card">
            <div className="camera-feed-container">
              <video
                ref={videoRef}
                autoPlay
                playsInline
                muted
                className={`video-element ${isActive ? 'video-element--active' : ''}`}
                width="640"
                height="480"
              />
              <canvas ref={canvasRef} width="640" height="480" style={{ display: 'none' }} />

              {/* Status HUD Overlays */}
              <div className="camera-hud-top">
                <span className="hud-badge status-badge">
                  <span className={`status-dot status-dot--${isActive ? 'active' : 'idle'}`}></span>
                  {status === 'OFFLINE' ? t.cameraOffline : 
                   status === 'CONNECTING' ? t.connecting : 
                   status === 'READY' ? t.readyToSign : 
                   status === 'PROCESSING' ? t.processingMovement : status}
                </span>
                <span className="hud-badge mode-badge">
                  <ArrowLeftRight size={12} /> {t.webSocketStream}
                </span>
              </div>

              {!isActive && (
                <div className="camera-placeholder">
                  <CameraOff size={48} className="placeholder-icon" />
                  <p>{t.webcamDisabled}</p>
                  <button className="btn btn-primary btn-lg" onClick={startSession}>
                    <Play size={16} /> {t.enableCameraFeed}
                  </button>
                </div>
              )}

              {/* Frame Buffer progress bar — always visible when active so user knows each sign is captured */}
              {isActive && bufferedFrames > 0 && bufferedFrames < maxFrames && (
                <div className="buffer-overlay">
                  <div className="buffer-progress-container">
                    <span className="buffer-text">{t.capturingGestures} {bufferedFrames} / {maxFrames} {t.frames}</span>
                    <div className="confidence-bar">
                      <div
                        className="confidence-bar-fill"
                        style={{ width: `${(bufferedFrames / maxFrames) * 100}%` }}
                      />
                    </div>
                  </div>
                </div>
              )}
            </div>

            {/* Controls Bar */}
            <div className="camera-controls">
              {isActive ? (
                <button className="btn btn-danger" onClick={stopSession}>
                  <CameraOff size={16} /> {t.disconnectFeed}
                </button>
              ) : (
                <button className="btn btn-primary" onClick={startSession}>
                  <Camera size={16} /> {t.connectFeed}
                </button>
              )}

              <button
                className={`btn btn-secondary ${isMuted ? 'btn-danger' : ''}`}
                onClick={() => setIsMuted(!isMuted)}
                title={isMuted ? t.voiceOn : t.voiceOff}
              >
                {isMuted ? <VolumeX size={16} /> : <Volume2 size={16} />}
                <span className="hide-on-mobile">{isMuted ? t.voiceOff : t.voiceOn}</span>
              </button>

              <button
                className="btn btn-secondary"
                onClick={switchCamera}
                title={t.switchCamera}
              >
                <RefreshCw size={16} />
                <span className="hide-on-mobile">{t.switchCamera}</span>
              </button>
            </div>
          </div>

          {/* Translation Builder Card */}
          <div className="translation-builder-card card">
            <div className="builder-header">
              <div className="flex items-center gap-2">
                <Sparkles size={16} className="text-gradient" />
                <h3>{t.translationBuilder}</h3>
              </div>
              <div className="builder-actions">
                <button className="btn btn-secondary btn-sm" onClick={handleBackspace} disabled={sentenceTokens.length === 0}>
                  {t.backspace}
                </button>
                <button className="btn btn-secondary btn-sm" onClick={handleClearSentence} disabled={sentenceTokens.length === 0}>
                  <Trash2 size={12} /> {t.clear}
                </button>
              </div>
            </div>

            <div className="sentence-display">
              {sentenceTokens.length > 0 ? (
                <p className="sentence-text">
                  {sentenceTokens.map((token, idx) => (
                    <span key={idx}>{signsT[token] || token}{' '}</span>
                  ))}
                </p>
              ) : (
                <span className="sentence-placeholder">{t.sentencePlaceholder}</span>
              )}
            </div>

            <div className="builder-footer">
              <button className="btn btn-primary" onClick={handleSpeakSentence} disabled={sentenceTokens.length === 0}>
                <Volume2 size={16} /> {t.speakOutLoud}
              </button>
            </div>
          </div>
        </div>

        {/* Sidebar: Real-Time Predictions & History */}
        <div className="translate-sidebar">
          {/* Last Prediction Alert */}
          <div className="card last-prediction-card">
            <h3><Sparkles size={16} className="text-gradient" /> {t.latestResult}</h3>
            {lastPrediction ? (
              <div className="prediction-details">
                <div className="prediction-word">{signsT[lastPrediction.rawSign] || lastPrediction.rawSign}</div>
                <div className="confidence-box">
                  <div className="flex justify-between font-size-xs" style={{ marginBottom: '4px' }}>
                    <span>{t.confidenceScore}</span>
                    <strong>{(lastPrediction.confidence * 100).toFixed(1)}%</strong>
                  </div>
                  <div className="confidence-bar">
                    <div
                      className="confidence-bar-fill"
                      style={{ width: `${lastPrediction.confidence * 100}%` }}
                    />
                  </div>
                </div>
              </div>
            ) : (
              <div className="no-prediction-placeholder">
                <MessageSquareCode size={24} />
                <p>{t.awaitingGestures}</p>
              </div>
            )}
          </div>

          {/* Session History */}
          <div className="card session-history-card">
            <div className="flex items-center justify-between" style={{ marginBottom: '1rem' }}>
              <h3><History size={16} /> {t.persistentHistory}</h3>
              {user ? (
                <span className="badge badge-primary">{t.synced}</span>
              ) : (
                <span className="badge badge-warning">{t.sandbox}</span>
              )}
            </div>

            <div className="history-timeline">
              {user ? (
                historyItems.length > 0 ? (
                  historyItems.map((item, idx) => {
                    const translatedHistorySign = signsT[item.sign_label.toLowerCase()] || item.sign_label;
                    return (
                      <div key={item.id || idx} className="history-timeline-item">
                        <div className="item-dot"></div>
                        <div className="item-content">
                          <span className="item-sign">{translatedHistorySign}</span>
                          <span className="item-meta">
                            {(item.confidence * 100).toFixed(0)}% • {new Date(item.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                          </span>
                        </div>
                      </div>
                    );
                  })
                ) : (
                  <p className="no-history-text">{t.noHistory}</p>
                )
              ) : (
                <div className="auth-prompt-history">
                  <p>{t.authPrompt}</p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
