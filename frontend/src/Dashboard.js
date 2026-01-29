import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { TrendingUp, TrendingDown, DollarSign, Users, BarChart3, Globe, Loader, AlertCircle, ChevronDown, ChevronUp } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import './Dashboard.css';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

function Dashboard() {
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [expandedCurrency, setExpandedCurrency] = useState(null);
  const [historicalData, setHistoricalData] = useState({});
  const [loadingChart, setLoadingChart] = useState(false);

  useEffect(() => {
    fetchDashboardData();
    // Refresh data every 5 minutes
    const interval = setInterval(fetchDashboardData, 5 * 60 * 1000);
    return () => clearInterval(interval);
  }, []);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API_BASE_URL}/api/dashboard`);
      setDashboardData(response.data);
      setError(null);
    } catch (err) {
      console.error('Failed to fetch dashboard data:', err);
      setError('Failed to load dashboard data. Please check that the backend is running.');
    } finally {
      setLoading(false);
    }
  };

  const fetchHistoricalData = async (currency) => {
    if (historicalData[currency]) {
      // Already have data for this currency
      return;
    }

    setLoadingChart(true);
    try {
      const response = await axios.get(`${API_BASE_URL}/api/exchange-rates/historical/${currency}`);
      if (response.data.success) {
        setHistoricalData(prev => ({
          ...prev,
          [currency]: response.data.historical_data
        }));
      }
    } catch (err) {
      console.error(`Failed to fetch historical data for ${currency}:`, err);
    } finally {
      setLoadingChart(false);
    }
  };

  const handleCurrencyClick = async (currency) => {
    if (expandedCurrency === currency) {
      // Collapse if already expanded
      setExpandedCurrency(null);
    } else {
      // Expand and fetch data if needed
      setExpandedCurrency(currency);
      await fetchHistoricalData(currency);
    }
  };

  if (loading) {
    return (
      <div className="dashboard-container">
        <div className="loading-spinner">
          <Loader size={48} className="animate-spin" />
          <p>Loading economic data...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="dashboard-container">
        <div className="error-message">
          <AlertCircle size={32} />
          <p>{error}</p>
          <button onClick={fetchDashboardData} className="retry-button">
            Retry
          </button>
        </div>
      </div>
    );
  }

  const indicators = dashboardData?.indicators || {};
  const news = dashboardData?.news?.articles || [];
  const rates = dashboardData?.exchange_rates?.rates || {};

  const renderIndicator = (title, data, icon, formatValue = (v) => v) => {
    if (!data?.success) {
      return (
        <div className="indicator-card error">
          <div className="indicator-header">
            <div className="icon-wrapper">{icon}</div>
            <h3>{title}</h3>
          </div>
          <p className="error-text">Data unavailable</p>
        </div>
      );
    }

    const value = data.latest_value || 'N/A';
    const date = data.latest_date || '';

    return (
      <div className="indicator-card">
        <div className="indicator-header">
          <div className="icon-wrapper">{icon}</div>
          <h3>{title}</h3>
        </div>
        <div className="indicator-value">
          {typeof value === 'number' ? formatValue(value) : value}
        </div>
        {date && <div className="indicator-date">As of {date}</div>}
      </div>
    );
  };

  const majorCurrencies = ['EUR', 'GBP', 'JPY', 'CAD', 'AUD', 'CHF'];

  return (
    <div className="dashboard-container">
      <div className="dashboard-header">
        <h1>Economic Dashboard</h1>
        <button onClick={fetchDashboardData} className="refresh-button">
          Refresh Data
        </button>
      </div>

      {/* Economic Indicators Section */}
      <section className="dashboard-section">
        <h2 className="section-title">Economic Indicators</h2>
        <div className="indicators-grid">
          {renderIndicator(
            'Inflation Rate',
            indicators.inflation,
            <BarChart3 size={24} />,
            (v) => `${v.toFixed(2)}%`
          )}
          {renderIndicator(
            'Unemployment Rate',
            indicators.unemployment,
            <Users size={24} />,
            (v) => `${v.toFixed(2)}%`
          )}
          {renderIndicator(
            'Federal Funds Rate',
            indicators.federal_funds_rate,
            <DollarSign size={24} />,
            (v) => `${v.toFixed(2)}%`
          )}
          {renderIndicator(
            'GDP Growth',
            indicators.gdp,
            <TrendingUp size={24} />,
            (v) => `${v.toFixed(2)}%`
          )}
        </div>
      </section>

      {/* Exchange Rates Section */}
      <section className="dashboard-section">
        <h2 className="section-title">USD Exchange Rates</h2>
        <div className="exchange-rates-grid">
          {majorCurrencies.map((currency) => (
            <React.Fragment key={currency}>
              <div className="exchange-card-wrapper">
                <div 
                  className={`exchange-card ${expandedCurrency === currency ? 'expanded' : ''}`}
                  onClick={() => handleCurrencyClick(currency)}
                >
                  <div className="exchange-header">
                    <Globe size={20} />
                    <span className="currency-code">{currency}</span>
                    {expandedCurrency === currency ? 
                      <ChevronUp size={16} className="chevron-icon" /> : 
                      <ChevronDown size={16} className="chevron-icon" />
                    }
                  </div>
                  <div className="exchange-rate">
                    {rates[currency]?.toFixed(4) || 'N/A'} {currency}
                  </div>
                  <div className="exchange-label">per USD</div>
                </div>
              </div>
            </React.Fragment>
          ))}
          
          {expandedCurrency && (
            <div className="chart-dropdown">
              {loadingChart ? (
                <div className="chart-loading">
                  <Loader size={24} className="animate-spin" />
                  <p>Loading historical data...</p>
                </div>
              ) : historicalData[expandedCurrency] && historicalData[expandedCurrency].length > 0 ? (
                <div className="chart-container">
                  <h4 className="chart-title">{expandedCurrency}/USD Exchange Rate Trend (Past Year)</h4>
                  <ResponsiveContainer width="100%" height={300}>
                    <LineChart data={historicalData[expandedCurrency]} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#333" />
                      <XAxis 
                        dataKey="date" 
                        stroke="#666"
                        tick={{ fill: '#999', fontSize: 12 }}
                        tickFormatter={(date) => {
                          const d = new Date(date);
                          return d.toLocaleDateString('en-US', { month: 'short', year: '2-digit' });
                        }}
                      />
                      <YAxis 
                        stroke="#666"
                        tick={{ fill: '#999', fontSize: 12 }}
                        domain={['auto', 'auto']}
                      />
                      <Tooltip 
                        contentStyle={{ 
                          backgroundColor: '#1a1a1a', 
                          border: '1px solid #ff4757',
                          borderRadius: '8px'
                        }}
                        labelStyle={{ color: '#fff' }}
                        itemStyle={{ color: '#ff4757' }}
                        formatter={(value) => [value.toFixed(4), `${expandedCurrency}`]}
                        labelFormatter={(date) => {
                          const d = new Date(date);
                          return d.toLocaleDateString('en-US', { 
                            month: 'long', 
                            day: 'numeric', 
                            year: 'numeric' 
                          });
                        }}
                      />
                      <Line 
                        type="monotone" 
                        dataKey="rate" 
                        stroke="#ff4757" 
                        strokeWidth={2}
                        dot={{ fill: '#ff4757', r: 3 }}
                        activeDot={{ r: 5 }}
                      />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              ) : (
                <div className="chart-error">
                  <AlertCircle size={24} />
                  <p>No historical data available</p>
                </div>
              )}
            </div>
          )}
        </div>
      </section>

      {/* News Section */}
      <section className="dashboard-section">
        <h2 className="section-title">Economic News</h2>
        <div className="news-feed">
          {news.length > 0 ? (
            news.map((article, index) => (
              <article key={index} className="news-card">
                <div className="news-source">{article.source || 'News Source'}</div>
                <h3 className="news-title">{article.title}</h3>
                {article.description && (
                  <p className="news-description">{article.description}</p>
                )}
                {article.published_at && (
                  <div className="news-date">
                    {new Date(article.published_at).toLocaleDateString()} at{' '}
                    {new Date(article.published_at).toLocaleTimeString()}
                  </div>
                )}
                {article.url && (
                  <a href={article.url} target="_blank" rel="noopener noreferrer" className="news-link">
                    Read Full Article →
                  </a>
                )}
              </article>
            ))
          ) : (
            <div className="no-data">No recent economic news available</div>
          )}
        </div>
      </section>

      {/* Last Updated */}
      <div className="dashboard-footer">
        <p>Last updated: {new Date(dashboardData?.timestamp).toLocaleString()}</p>
      </div>
    </div>
  );
}

export default Dashboard;
