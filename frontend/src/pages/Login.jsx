import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { LogIn, Mail, Lock, AlertCircle, ShieldAlert, Eye, EyeOff } from 'lucide-react';
import { translations } from '../translations';
import './Auth.css';

export default function Login() {
  const { login, loading, language } = useAuth();
  const t = translations[language].auth;
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (!email || !password) {
      setError('Please fill in all fields.');
      return;
    }

    const res = await login(email, password);
    if (res.success) {
      navigate('/translate');
    } else {
      setError(res.error || 'Failed to sign in. Please check your credentials.');
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
            <h2>{t.welcomeBack}</h2>
            <p>{t.signInDesc}</p>
          </div>

          {error && (
            <div className="auth-error-banner">
              <AlertCircle size={16} />
              <span>{error}</span>
            </div>
          )}

          <form className="auth-form" onSubmit={handleSubmit}>
            <div className="form-group">
              <label className="form-label" htmlFor="email">{t.email}</label>
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

            <div className="form-group">
              <label className="form-label" htmlFor="password">{t.password}</label>
              <div className="input-with-icon">
                <Lock className="input-icon" size={16} />
                <input
                  id="password"
                  type={showPassword ? "text" : "password"}
                  className="form-input pr-10"
                  placeholder="••••••••"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  disabled={loading}
                  required
                />
                <button
                  type="button"
                  className="password-toggle-btn"
                  onClick={() => setShowPassword(!showPassword)}
                  aria-label="Toggle password visibility"
                >
                  {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
                </button>
              </div>
            </div>

            <button type="submit" className="btn btn-primary btn-lg auth-submit-btn" disabled={loading}>
              {loading ? (
                <>
                  <div className="spinner" style={{ width: '16px', height: '16px', borderWidth: '1.5px' }}></div>
                  {t.signingIn}
                </>
              ) : (
                <>
                  <LogIn size={16} />
                  {t.signInBtn}
                </>
              )}
            </button>
          </form>

          <div className="auth-footer">
            <p>
              {t.dontHaveAccount} <Link to="/register" className="auth-link">{t.createOneNow}</Link>
            </p>
          </div>
        </div>

        {/* Defense Notice */}
        <div className="auth-defense-notice card">
          <ShieldAlert size={18} className="notice-icon" />
          <div>
            <h4>{t.defenseSandbox}</h4>
            <p>{t.defenseSandboxDesc}</p>
          </div>
        </div>
      </div>
    </div>
  );
}
