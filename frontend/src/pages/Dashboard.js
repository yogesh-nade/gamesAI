import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Navbar from '../components/Navbar';
import { gamesAPI } from '../services/api';

const Dashboard = () => {
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      const response = await gamesAPI.getDashboard();
      setDashboardData(response.data);
    } catch (err) {
      setError('Failed to load dashboard data');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const startNewTicTacToeGame = async () => {
    try {
      const response = await gamesAPI.startTicTacToe();
      const matchId = response.data.match_id;
      navigate(`/tic-tac-toe/${matchId}`);
    } catch (err) {
      setError('Failed to start new game');
      console.error(err);
    }
  };

  const startNewChessGame = async () => {
    try {
      console.log('Starting chess game...');
      const response = await gamesAPI.startChess();
      console.log('Chess game response:', response);
      const matchId = response.data.match_id;
      console.log('Chess match ID:', matchId);
      navigate(`/chess/${matchId}`);
    } catch (err) {
      console.error('Chess game error details:', err);
      console.error('Error response:', err.response);
      console.error('Error message:', err.message);
      setError(`Failed to start chess game: ${err.response?.data?.error || err.message}`);
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString();
  };

  const getResultBadge = (result) => {
    const badgeStyle = {
      padding: '4px 8px',
      borderRadius: '4px',
      color: 'white',
      fontSize: '12px',
      fontWeight: 'bold',
    };

    const styles = {
      win: { ...badgeStyle, backgroundColor: '#28a745' },
      lose: { ...badgeStyle, backgroundColor: '#dc3545' },
      draw: { ...badgeStyle, backgroundColor: '#6c757d' },
    };

    return (
      <span style={styles[result] || styles.draw}>
        {result?.toUpperCase() || 'DRAW'}
      </span>
    );
  };

  if (loading) {
    return (
      <>
        <Navbar />
        <div className="container">
          <div className="loading">Loading dashboard...</div>
        </div>
      </>
    );
  }

  if (error) {
    return (
      <>
        <Navbar />
        <div className="container">
          <div className="error">{error}</div>
        </div>
      </>
    );
  }

  return (
    <>
      <Navbar />
      <div className="container">
        <h2>Welcome to Board Games Platform!</h2>
        
        {/* User Stats */}
        <div className="stats-grid">
          <div className="stat-card">
            <h3>{dashboardData.user.total_games}</h3>
            <p>Total Games</p>
          </div>
          <div className="stat-card">
            <h3>{dashboardData.user.total_wins}</h3>
            <p>Wins</p>
          </div>
          <div className="stat-card">
            <h3>{dashboardData.user.total_losses}</h3>
            <p>Losses</p>
          </div>
          <div className="stat-card">
            <h3>{dashboardData.user.win_rate}%</h3>
            <p>Win Rate</p>
          </div>
        </div>

        {/* Available Games */}
        <div className="card">
          <h3>Start a New Game</h3>
          <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
            <button onClick={startNewTicTacToeGame} className="btn btn-success">
              🎯 Play Tic Tac Toe
            </button>
            <button onClick={startNewChessGame} className="btn btn-success">
              ♟️ Play Chess
            </button>
            <button disabled className="btn" style={{ opacity: 0.6 }}>
              🔴 Checkers (Coming Soon)
            </button>
          </div>
        </div>

        {/* Recent Matches */}
        <div className="card">
          <h3>Recent Matches</h3>
          {dashboardData.recent_matches.length === 0 ? (
            <p>No matches played yet. Start your first game above!</p>
          ) : (
            <div style={{ overflowX: 'auto' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                <thead>
                  <tr style={{ backgroundColor: '#f8f9fa' }}>
                    <th style={{ padding: '10px', textAlign: 'left', border: '1px solid #dee2e6' }}>Game</th>
                    <th style={{ padding: '10px', textAlign: 'left', border: '1px solid #dee2e6' }}>Opponent</th>
                    <th style={{ padding: '10px', textAlign: 'left', border: '1px solid #dee2e6' }}>Result</th>
                    <th style={{ padding: '10px', textAlign: 'left', border: '1px solid #dee2e6' }}>Date</th>
                    <th style={{ padding: '10px', textAlign: 'left', border: '1px solid #dee2e6' }}>Status</th>
                  </tr>
                </thead>
                <tbody>
                  {dashboardData.recent_matches.map((match) => (
                    <tr key={match.id}>
                      <td style={{ padding: '10px', border: '1px solid #dee2e6' }}>
                        {match.game_name}
                      </td>
                      <td style={{ padding: '10px', border: '1px solid #dee2e6' }}>
                        {match.opponent}
                      </td>
                      <td style={{ padding: '10px', border: '1px solid #dee2e6' }}>
                        {match.result ? getResultBadge(match.result) : '-'}
                      </td>
                      <td style={{ padding: '10px', border: '1px solid #dee2e6' }}>
                        {formatDate(match.started_at)}
                      </td>
                      <td style={{ padding: '10px', border: '1px solid #dee2e6' }}>
                        <span style={{
                          padding: '4px 8px',
                          borderRadius: '4px',
                          backgroundColor: match.status === 'completed' ? '#d4edda' : '#fff3cd',
                          color: match.status === 'completed' ? '#155724' : '#856404',
                          fontSize: '12px',
                        }}>
                          {match.status.toUpperCase()}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </>
  );
};

export default Dashboard;