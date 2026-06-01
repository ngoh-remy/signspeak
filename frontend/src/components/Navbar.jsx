import { Link, useLocation, useNavigate } from 'react-router-dom';
import { Hand, Menu, X, LogOut, User, BookOpen, Mic, Info, Sun, Moon } from 'lucide-react';
import { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { translations } from '../translations';
import './Navbar.css';

export default function Navbar() {
  const [menuOpen, setMenuOpen] = useState(false);
  const { user, logout, language, changeLanguage, theme, toggleTheme } = useAuth();
  const t = translations[language].nav;
  const location = useLocation();
  const navigate = useNavigate();

  const navLinks = [
    { path: '/translate', label: t.translate, icon: <Mic size={16} /> },
    { path: '/dictionary', label: t.dictionary, icon: <BookOpen size={16} /> },
  ];

  const handleLogout = () => {
    logout();
    navigate('/');
    setMenuOpen(false);
  };

  return (
    <nav className="navbar">
      <div className="navbar-container">
        {/* Logo */}
        <Link to="/" className="navbar-logo" onClick={() => setMenuOpen(false)}>
          <img src="/logo.png" alt="SignSpeak logo" className="navbar-logo-img" />
          <span className="navbar-logo-text">SignSpeak</span>
        </Link>

        {/* Desktop Links */}
        <div className="navbar-links">
          {navLinks.map(link => (
            <Link
              key={link.path}
              to={link.path}
              className={`navbar-link ${location.pathname === link.path ? 'navbar-link--active' : ''}`}
            >
              {link.icon}
              {link.label}
            </Link>
          ))}
        </div>

        {/* Desktop Auth & Language */}
        <div className="navbar-auth">
          <button className="navbar-theme-toggle" onClick={toggleTheme} aria-label="Toggle theme">
            {theme === 'dark' ? <Sun size={18} /> : <Moon size={18} />}
          </button>
          <div className="language-switcher">
            <button 
              className={`lang-btn ${language === 'en' ? 'active' : ''}`} 
              onClick={() => changeLanguage('en')}
            >EN</button>
            <button 
              className={`lang-btn ${language === 'fr' ? 'active' : ''}`} 
              onClick={() => changeLanguage('fr')}
            >FR</button>
          </div>
          {user ? (
            <div className="navbar-user">
              <div className="navbar-avatar">
                <User size={14} />
              </div>
              <span className="navbar-username">{user.username}</span>
              <button className="navbar-logout" onClick={handleLogout} title={t.logout}>
                <LogOut size={16} />
              </button>
            </div>
          ) : (
            <div className="navbar-auth-buttons">
              <Link to="/login" className="btn btn-ghost btn-sm">{t.signIn}</Link>
              <Link to="/register" className="btn btn-primary btn-sm">{t.getStarted}</Link>
            </div>
          )}
        </div>

        {/* Mobile Menu Button */}
        <button
          id="mobile-menu-toggle"
          className="navbar-mobile-toggle"
          onClick={() => setMenuOpen(!menuOpen)}
          aria-label="Toggle menu"
        >
          {menuOpen ? <X size={22} /> : <Menu size={22} />}
        </button>
      </div>

      {/* Mobile Dropdown */}
      {menuOpen && (
        <div className="navbar-mobile-menu">
          {navLinks.map(link => (
            <Link
              key={link.path}
              to={link.path}
              className={`navbar-mobile-link ${location.pathname === link.path ? 'navbar-mobile-link--active' : ''}`}
              onClick={() => setMenuOpen(false)}
            >
              {link.icon}
              {link.label}
            </Link>
          ))}
          <div className="navbar-mobile-divider" />
          
          <button className="navbar-mobile-link" onClick={() => { toggleTheme(); setMenuOpen(false); }}>
            {theme === 'dark' ? <><Sun size={16} /> Light Mode</> : <><Moon size={16} /> Dark Mode</>}
          </button>

          <div className="navbar-mobile-lang">
            <button 
              className={`lang-btn ${language === 'en' ? 'active' : ''}`} 
              onClick={() => changeLanguage('en')}
            >EN</button>
            <button 
              className={`lang-btn ${language === 'fr' ? 'active' : ''}`} 
              onClick={() => changeLanguage('fr')}
            >FR</button>
          </div>

          {user ? (
            <button className="navbar-mobile-link navbar-mobile-logout" onClick={handleLogout}>
              <LogOut size={16} />
              {t.logout} ({user.username})
            </button>
          ) : (
            <>
              <Link to="/login" className="navbar-mobile-link" onClick={() => setMenuOpen(false)}>
                {t.signIn}
              </Link>
              <Link to="/register" className="btn btn-primary" style={{ margin: '0.5rem 1rem' }} onClick={() => setMenuOpen(false)}>
                {t.getStarted}
              </Link>
            </>
          )}
        </div>
      )}
    </nav>
  );
}
