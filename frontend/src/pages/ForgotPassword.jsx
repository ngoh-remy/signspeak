import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Mail, AlertCircle, CheckCircle, ArrowLeft } from 'lucide-react';
import './Auth.css';

export default function ForgotPassword() {
  const { forgotPassword, loading } = useAuth();
  const [email, setEmail] = useState('');
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);
  const [devToken, setDevToken] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setMessage('');
    setDevToken(null);

    if (!email) {
      setError('Please enter your email address.');
      return;
    }

    const res = await forgotPassword(email);
    if (res.success) {
      setSuccess(true);
      setMessage(res.message || 'If an account exists, a reset link has been sent.');
      if (res.dev_token) {
        setDevToken(res.dev_token);
      }
    } else {
      setError(res.error || 'Failed to request password reset. Please try again.');
    }
  };

  return (
    <div className="auth-page fade-in-up">
      <div className="bg-orb bg-orb-1"></div>
      <div className="bg-orb bg-orb-2"></div>

      <div className="auth-container">
        <div className="auth-card card">
          <div className="auth-header">
            <div className="auth-logo">
              <img src="/logo.png" alt="SignSpeak Logo" />
            </div>
            <h2>Forgot Password</h2>
            <p>Enter your email to receive a reset link</p>
          </div>

          {error && (
            <div className="auth-error-banner">
              <AlertCircle size={16} />
              <span>{error}</span>
            </div>
          )}

          {success ? (
            <div className="auth-success-message" style={{ textAlign: 'center', color: 'var(--text-primary)' }}>
              <CheckCircle size={48} className="mx-auto mb-4" style={{ color: 'var(--color-success)', margin: '0 auto 16px auto' }} />
              <p className="mb-4">{message}</p>
              
              {devToken && (
                <div style={{ background: 'rgba(124, 58, 237, 0.1)', padding: '16px', borderRadius: '8px', marginBottom: '16px', border: '1px solid rgba(124, 58, 237, 0.3)' }}>
                  <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: '8px' }}>
                    [DEVELOPER MODE] Since email sending is simulated, click below to reset:
                  </p>
                  <Link to={`/reset-password?token=${devToken}`} className="btn btn-primary" style={{ width: '100%' }}>
                    Go to Reset Password Page
                  </Link>
                </div>
              )}

              <Link to="/login" className="btn btn-secondary" style={{ display: 'inline-block', width: '100%' }}>
                Return to Login
              </Link>
            </div>
          ) : (
            <form className="auth-form" onSubmit={handleSubmit}>
              <div className="form-group">
                <label className="form-label" htmlFor="email">Email Address</label>
                <div className="input-with-icon">
                  <Mail className="input-icon" size={16} />
                  <input
                    id="email"
                    type="email"
                    className="form-input"
                    placeholder="name@example.com"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    disabled={loading}
                    required
                  />
                </div>
              </div>

              <button type="submit" className="btn btn-primary btn-lg auth-submit-btn" disabled={loading}>
                {loading ? (
                  <>
                    <div className="spinner" style={{ width: '16px', height: '16px', borderWidth: '1.5px' }}></div>
                    Sending...
                  </>
                ) : (
                  'Send Reset Link'
                )}
              </button>
            </form>
          )}

          {!success && (
            <div className="auth-footer">
              <Link to="/login" className="auth-link" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px' }}>
                <ArrowLeft size={16} /> Back to Sign In
              </Link>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
