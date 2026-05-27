import React, { useState } from 'react';
import { Search, Info, Hand, Layers, AlertCircle, HelpCircle, ArrowRight } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { translations } from '../translations';
import './Dictionary.css';

// Pre-defined subset of key demo-quality vocabulary with academic/technical descriptions
const DEMO_SIGNS = [
  { sign: 'hello', category: 'Salutation', complexity: 'Low', description: 'Hand moves from forehead outward, simulating a polite salute. Used as standard introductory gesture.' },
  { sign: 'thank you', category: 'Politeness', complexity: 'Medium', description: 'Touch fingertips of active flat hand to lips/chin, then move hand forward and down toward the listener.' },
  { sign: 'please', category: 'Politeness', complexity: 'Low', description: 'Rub the flat palm of the active hand in a circular motion over the chest area.' },
  { sign: 'yes', category: 'Affirmation', complexity: 'Low', description: 'Make a fist with active hand and tilt it up and down, simulating a nodding head.' },
  { sign: 'no', category: 'Negation', complexity: 'Low', description: 'Quickly snap index and middle fingers down together onto the thumb.' },
  { sign: 'help', category: 'Assistance', complexity: 'High', description: 'Place active closed hand, thumb pointing up, on flat palm of inactive hand, then raise both hands together.' },
  { sign: 'sorry', category: 'Politeness', complexity: 'Low', description: 'Make a fist (A-handshape) and rub it in circular motions over the chest area.' },
  { sign: 'love', category: 'Emotion', complexity: 'Low', description: 'Cross both hands over the chest, palms facing inward and fingers touching opposite shoulders.' },
  { sign: 'good', category: 'Evaluation', complexity: 'Medium', description: 'Place fingertips of active flat hand on lips, move it down, and rest it flat on the palm of inactive hand.' },
  { sign: 'bad', category: 'Evaluation', complexity: 'Medium', description: 'Touch active flat hand to lips, move it down while turning palm outward and downward.' },
  { sign: 'eat', category: 'Action', complexity: 'Low', description: 'Bring active hand in a closed "O" handshape to the mouth twice, imitating eating.' },
  { sign: 'water', category: 'Noun', complexity: 'Medium', description: 'Form "W" shape with active hand (index, middle, ring finger up) and tap index finger against chin twice.' }
];

export default function Dictionary() {
  const { language } = useAuth();
  const t = translations[language].dictionary;
  const signsT = translations[language].signs;
  const dictT = translations[language].dictionarySigns;

  const [searchTerm, setSearchTerm] = useState('');
  const [selectedSign, setSelectedSign] = useState(DEMO_SIGNS[0]);

  const filteredSigns = DEMO_SIGNS.filter(item => {
    const translatedName = signsT[item.sign.toLowerCase()] || item.sign;
    return translatedName.toLowerCase().includes(searchTerm.toLowerCase());
  });

  return (
    <div className="dictionary-page fade-in-up container">
      <div className="bg-orb bg-orb-1"></div>
      <div className="bg-orb bg-orb-2"></div>

      <header className="dictionary-header">
        <div className="badge badge-primary">{t.vocabRef}</div>
        <h1>{t.supported}<span className="text-gradient">{t.aslDict}</span></h1>
        <p className="dictionary-lead">
          {t.leadText}
        </p>
      </header>

      <div className="dictionary-layout">
        {/* Left Side: Search & List */}
        <div className="dictionary-sidebar card">
          <div className="search-box">
            <Search className="search-icon" size={18} />
            <input
              type="text"
              className="form-input search-input"
              placeholder={t.searchPlaceholder}
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>

          <div className="signs-list">
            {filteredSigns.length > 0 ? (
              filteredSigns.map(item => {
                const signKey = item.sign.toLowerCase();
                const translatedName = signsT[signKey] || item.sign;
                const translatedDict = dictT[signKey] || item;
                return (
                  <button
                    key={item.sign}
                    className={`sign-item-btn ${selectedSign?.sign === item.sign ? 'sign-item-btn--active' : ''}`}
                    onClick={() => setSelectedSign(item)}
                  >
                    <span className="sign-name">{translatedName}</span>
                    <span className={`badge ${
                      item.complexity === 'Low' ? 'badge-success' :
                      item.complexity === 'Medium' ? 'badge-warning' : 'badge-primary'
                    }`}>
                      {translatedDict.complexity}
                    </span>
                  </button>
                );
              })
            ) : (
              <div className="no-signs">
                <AlertCircle size={20} />
                <p>{t.noSignsFound}</p>
              </div>
            )}
          </div>
        </div>

        {/* Right Side: Details */}
        <div className="dictionary-details card">
          {selectedSign ? (
            (() => {
              const signKey = selectedSign.sign.toLowerCase();
              const translatedDict = dictT[signKey] || selectedSign;
              return (
                <div className="details-content">
                  <div className="details-header">
                    <div>
                      <h2 className="selected-sign-title">{signsT[signKey] || selectedSign.sign}</h2>
                      <span className="badge badge-primary" style={{ marginTop: '4px' }}>
                        {translatedDict.category}
                      </span>
                    </div>

                    <div className="details-complexity">
                      <span className="complexity-label">{t.inferenceCost}</span>
                      <span className={`badge ${
                        selectedSign.complexity === 'Low' ? 'badge-success' :
                        selectedSign.complexity === 'Medium' ? 'badge-warning' : 'badge-primary'
                      }`}>
                        {translatedDict.complexity} {t.complexity}
                      </span>
                    </div>
                  </div>

                  <div className="details-section">
                    <h3><Hand size={16} /> {t.physicalKinematics}</h3>
                    <p>{translatedDict.description}</p>
                  </div>

                  <div className="details-section">
                    <h3><Layers size={16} /> {t.techNote}</h3>
                    <div className="tech-note">
                      <p>
                        {t.techNoteText}
                      </p>
                      <ul className="tech-bullets">
                        <li><strong>{t.sequenceFrames}:</strong> 30 (1.0 second duration at 30 FPS)</li>
                        <li><strong>{t.keypointFeatures}:</strong> 1,662 features per frame</li>
                        <li><strong>{t.weightFactor}:</strong> {selectedSign.complexity === 'Low' ? '1.0x (Static translation offset)' : selectedSign.complexity === 'Medium' ? '1.5x (Uni-directional movement)' : '2.0x (Complex double-hand sequence)'}</li>
                      </ul>
                    </div>
                  </div>

                  <div className="details-cta">
                    <p>{t.readyToTry}</p>
                    <ArrowRight size={16} className="cta-arrow" />
                  </div>
                </div>
              );
            })()
          ) : (
            <div className="select-prompt">
              <HelpCircle size={40} className="prompt-icon" />
              <p>{t.selectPrompt}</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
