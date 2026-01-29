import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { X, User, Save } from 'lucide-react';
import './ProfileModal.css';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

function ProfileModal({ userId, isOpen, onClose, onSave }) {
  const [profile, setProfile] = useState({
    income_range: '',
    debt_level: '',
    dependents: '',
    risk_tolerance: 'moderate',
    financial_goals: {
      short_term: '',
      long_term: ''
    },
    preferences: {
      explanation_depth: 'moderate',
      focus_areas: []
    }
  });
  
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');

  useEffect(() => {
    if (isOpen) {
      loadProfile();
    }
  }, [isOpen, userId]);

  const loadProfile = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/users/${userId}/profile`);
      setProfile({
        income_range: response.data.income_range || '',
        debt_level: response.data.debt_level || '',
        dependents: response.data.dependents || '',
        risk_tolerance: response.data.risk_tolerance || 'moderate',
        financial_goals: response.data.financial_goals || { short_term: '', long_term: '' },
        preferences: response.data.preferences || { explanation_depth: 'moderate', focus_areas: [] }
      });
    } catch (error) {
      // Profile doesn't exist yet, that's okay
      console.log('No existing profile, starting fresh');
    }
  };

  const handleSave = async () => {
    setLoading(true);
    setMessage('');
    
    try {
      await axios.post(`${API_BASE_URL}/api/users/${userId}/profile`, {
        user_id: userId,
        income_range: profile.income_range,
        debt_level: parseFloat(profile.debt_level) || 0,
        dependents: parseInt(profile.dependents) || 0,
        risk_tolerance: profile.risk_tolerance,
        financial_goals: profile.financial_goals,
        preferences: profile.preferences
      });
      
      setMessage('Profile saved successfully!');
      setTimeout(() => {
        onSave();
        onClose();
      }, 1000);
    } catch (error) {
      setMessage('Error saving profile. Please try again.');
      console.error('Error saving profile:', error);
    } finally {
      setLoading(false);
    }
  };

  const toggleFocusArea = (area) => {
    const currentAreas = profile.preferences.focus_areas || [];
    const newAreas = currentAreas.includes(area)
      ? currentAreas.filter(a => a !== area)
      : [...currentAreas, area];
    
    setProfile({
      ...profile,
      preferences: {
        ...profile.preferences,
        focus_areas: newAreas
      }
    });
  };

  if (!isOpen) return null;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <div className="modal-title">
            <User size={24} />
            <h2>Your Financial Profile</h2>
          </div>
          <button className="close-button" onClick={onClose}>
            <X size={24} />
          </button>
        </div>

        <div className="modal-body">
          <p className="modal-description">
            Share your financial context to receive personalized economic guidance tailored to your situation.
          </p>

          <div className="form-section">
            <label>
              Annual Income Range
              <select
                value={profile.income_range}
                onChange={(e) => setProfile({ ...profile, income_range: e.target.value })}
              >
                <option value="">Select range</option>
                <option value="under_30k">Under $30,000</option>
                <option value="30k_50k">$30,000 - $50,000</option>
                <option value="50k_75k">$50,000 - $75,000</option>
                <option value="75k_100k">$75,000 - $100,000</option>
                <option value="100k_150k">$100,000 - $150,000</option>
                <option value="over_150k">Over $150,000</option>
              </select>
            </label>

            <label>
              Current Debt Level ($)
              <input
                type="number"
                placeholder="e.g., 25000"
                value={profile.debt_level}
                onChange={(e) => setProfile({ ...profile, debt_level: e.target.value })}
              />
            </label>

            <label>
              Number of Dependents
              <input
                type="number"
                placeholder="e.g., 2"
                value={profile.dependents}
                onChange={(e) => setProfile({ ...profile, dependents: e.target.value })}
              />
            </label>

            <label>
              Risk Tolerance
              <select
                value={profile.risk_tolerance}
                onChange={(e) => setProfile({ ...profile, risk_tolerance: e.target.value })}
              >
                <option value="conservative">Conservative - Prefer safety and stability</option>
                <option value="moderate">Moderate - Balance risk and reward</option>
                <option value="aggressive">Aggressive - Willing to take risks</option>
              </select>
            </label>
          </div>

          <div className="form-section">
            <h3>Financial Goals</h3>
            
            <label>
              Short-term (Next 3-6 months)
              <select
                value={profile.financial_goals.short_term}
                onChange={(e) => setProfile({
                  ...profile,
                  financial_goals: { ...profile.financial_goals, short_term: e.target.value }
                })}
              >
                <option value="">Select a goal</option>
                <option value="emergency_fund">Build Emergency Fund</option>
                <option value="pay_debt">Pay Off Debt</option>
                <option value="save_travel">Save for Travel</option>
                <option value="reduce_expenses">Reduce Expenses</option>
                <option value="increase_income">Increase Income</option>
                <option value="build_credit">Build Credit Score</option>
                <option value="start_investing">Start Investing</option>
              </select>
            </label>

            <label>
              Long-term (1+ years)
              <select
                value={profile.financial_goals.long_term}
                onChange={(e) => setProfile({
                  ...profile,
                  financial_goals: { ...profile.financial_goals, long_term: e.target.value }
                })}
              >
                <option value="">Select a goal</option>
                <option value="buy_home">Buy a Home</option>
                <option value="retirement">Retirement Planning</option>
                <option value="education">Education Fund</option>
                <option value="wealth_building">Wealth Building</option>
                <option value="passive_income">Generate Passive Income</option>
                <option value="pay_off_mortgage">Pay Off Mortgage</option>
                <option value="financial_independence">Achieve Financial Independence</option>
              </select>
            </label>
          </div>

          <div className="form-section">
            <label>
              Explanation Detail Level
              <select
                value={profile.preferences.explanation_depth}
                onChange={(e) => setProfile({
                  ...profile,
                  preferences: { ...profile.preferences, explanation_depth: e.target.value }
                })}
              >
                <option value="brief">Brief Summary - Quick, concise responses with key points</option>
                <option value="moderate">Moderate - Balanced explanations with examples</option>
                <option value="detailed">Detailed - Comprehensive explanations with full context and nuances</option>
              </select>
            </label>
            <p className="form-hint">Choose how detailed you want Pulse's responses to be. Brief is great for quick answers, Moderate for everyday decisions, and Detailed for in-depth analysis.</p>
          </div>

          {message && (
            <div className={`message ${message.includes('Error') ? 'error' : 'success'}`}>
              {message}
            </div>
          )}
        </div>

        <div className="modal-footer">
          <button className="button-secondary" onClick={onClose}>
            Cancel
          </button>
          <button className="button-primary" onClick={handleSave} disabled={loading}>
            <Save size={18} />
            {loading ? 'Saving...' : 'Save Profile'}
          </button>
        </div>
      </div>
    </div>
  );
}

export default ProfileModal;
