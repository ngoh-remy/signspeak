import React from 'react';
import { Link } from 'react-router-dom';
import { ChevronRight } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { translations } from '../translations';
import './Landing.css';

export default function Landing() {
  const { language } = useAuth();
  const t = translations[language].landing;
  return (
    <div className="landing-page fade-in-up">
      {/* Decorative Orbs */}
      <div className="bg-orb bg-orb-1"></div>
      <div className="bg-orb bg-orb-2"></div>

      {/* Hero Section */}
      <header className="hero-section container">
        <div className="hero-content">
          <h1 className="hero-title">
            {t.heroTitlePart1} <span className="text-gradient">{t.heroTitlePart2}</span>
          </h1>
          <p className="hero-subtitle">
            {t.heroSubtitle}
          </p>
          <div className="hero-cta">
            <Link to="/translate" className="btn btn-primary btn-lg">
              {t.startTranslating} <ChevronRight size={18} />
            </Link>
          </div>
        </div>

        <div className="hero-visual">
          <div className="hero-visual-card card">
            <div className="camera-sim">
              <div className="camera-sim-glow"></div>
              <div className="camera-sim-hud">
                <span className="hud-label">{t.liveFeed}</span>
                <span className="hud-status">{t.connected}</span>
              </div>
              <div className="hand-gesture-illustration">
                <img src="/logo.png" alt="Hand Sign Illustration" className="illustration-img" />
              </div>
              <div className="inference-overlay card">
                <div className="overlay-header">
                  <span>{t.detectedGesture}</span>
                  <span className="badge badge-success">98.4% {t.confidence}</span>
                </div>
                <div className="overlay-word">{t.hello}</div>
              </div>
            </div>
          </div>
        </div>
      </header>
    </div>
  );
}
