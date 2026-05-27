import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { UserPlus, User, Mail, Lock, AlertCircle, ShieldAlert } from 'lucide-react';
import { translations } from '../translations';
import './Auth.css';

export default function Register() {
  const { register, loading, language } = useAuth();
  const t = translations[language].auth;
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (!username || !email || !password || !confirmPassword) {
      setError('Please fill in all fields.');
      return;
    }

    if (password !== confirmPassword) {
      setError('Passwords do not match.');
      return;
    }

    if (password.length < 6) {
      setError('Password must be at least 6 characters long.');
      return;
    }

    const res = await register(username, email, password);
    if (res.success) {
      navigate('/translate');
    } else {
      setError(res.error || 'Registration failed. Try a different username or email.');
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
            <h2>{t.getStarted}</h2>
            <p>{t.createAccountDesc}</p>
          </div>

          {error && (
            <div className="auth-error-banner">
              <AlertCircle size={16} />
              <span>{error}</span>
            </div>
          )}

          <form className="auth-form" onSubmit={handleSubmit}>
            <div className="form-group">
              <label className="form-label" htmlFor="username">{t.username}</label>
              <div className="input-with-icon">
                <User className="input-icon" size={16} />
                <input
                  id="username"
                  type="text"
                  className="form-input"
                  placeholder="johndoe"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  disabled={loading}
                  required
                />
              </div>
            </div>

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
                  type="password"
                  className="form-input"
                  placeholder="••••••••"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  disabled={loading}
                  required
                />
              </div>
            </div>

            <div className="form-group">
              <label className="form-label" htmlFor="confirmPassword">{t.confirmPassword}</label>
              <div className="input-with-icon">
                <Lock className="input-icon" size={16} />
                <input
                  id="confirmPassword"
                  type="password"
                  className="form-input"
                  placeholder="••••••••"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  disabled={loading}
                  required
                />
              </div>
            </div>

            <button type="submit" className="btn btn-primary btn-lg auth-submit-btn" disabled={loading}>
              {loading ? (
                <>
                  <div className="spinner" style={{ width: '16px', height: '16px', borderWidth: '1.5px' }}></div>
                  {t.creatingAccount}
                </>
              ) : (
                <>
                  <UserPlus size={16} />
                  {t.signUp}
                </>
              )}
            </button>
          </form>

          <div className="auth-footer">
            <p>
              {t.alreadyHaveAccount} <Link to="/login" className="auth-link">{t.signInInstead}</Link>
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
