import React, { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import Navbar from '../components/Navbar';
import TicTacToeBoard from '../components/TicTacToeBoard';
import { gamesAPI } from '../services/api';

const TicTacToePage = () => {
  const { matchId } = useParams();
  const navigate = useNavigate();
  const [gameState, setGameState] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [making_move, setMakingMove] = useState(false);
  const [gameOver, setGameOver] = useState(false);
  const [winner, setWinner] = useState(null);
  const [result, setResult] = useState(null);

  useEffect(() => {
    fetchGameState();
  }, [matchId, fetchGameState]);

  const fetchGameState = useCallback(async () => {
    try {
      const response = await gamesAPI.getTicTacToeMatch(matchId);
      setGameState(response.data);
      
      // Check if game is already over
      if (response.data.match.status === 'completed') {
        setGameOver(true);
        setResult(response.data.match.result);
      }
    } catch (err) {
      setError('Failed to load game state');
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, [matchId]);

  const handleCellClick = async (row, col) => {
    if (making_move || gameOver) return;

    setMakingMove(true);
    try {
      const response = await gamesAPI.makeTicTacToeMove(matchId, { row, col });
      
      if (response.data.game_over) {
        setGameOver(true);
        setWinner(response.data.winner);
        setResult(response.data.result);
        setGameState(response.data.tic_tac_toe_match);
      } else {
        setGameState(response.data.tic_tac_toe_match);
      }
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to make move');
      console.error(err);
    } finally {
      setMakingMove(false);
    }
  };

  const startNewGame = async () => {
    try {
      const response = await gamesAPI.startTicTacToe();
      const newMatchId = response.data.match_id;
      navigate(`/tic-tac-toe/${newMatchId}`);
    } catch (err) {
      setError('Failed to start new game');
      console.error(err);
    }
  };

  const goToDashboard = () => {
    navigate('/dashboard');
  };

  const getGameStatus = () => {
    if (gameOver) {
      if (winner === 'X') {
        return { message: '🎉 You Won!', color: '#28a745' };
      } else if (winner === 'O') {
        return { message: '😔 You Lost!', color: '#dc3545' };
      } else {
        return { message: "🤝 It's a Draw!", color: '#6c757d' };
      }
    } else if (making_move) {
      return { message: 'AI is thinking...', color: '#ffc107' };
    } else if (gameState?.current_player === 'X') {
      return { message: 'Your turn (X)', color: '#007bff' };
    } else {
      return { message: 'AI turn (O)', color: '#dc3545' };
    }
  };

  if (loading) {
    return (
      <>
        <Navbar />
        <div className="container">
          <div className="loading">Loading game...</div>
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
          <button onClick={goToDashboard} className="btn">
            Back to Dashboard
          </button>
        </div>
      </>
    );
  }

  const status = getGameStatus();

  return (
    <>
      <Navbar />
      <div className="container">
        <div className="card" style={{ textAlign: 'center', maxWidth: '600px', margin: '0 auto' }}>
          <h2>Tic Tac Toe</h2>
          
          <div style={{ 
            fontSize: '1.2em', 
            fontWeight: 'bold', 
            color: status.color,
            margin: '20px 0' 
          }}>
            {status.message}
          </div>

          {gameState && (
            <TicTacToeBoard
              board={gameState.board}
              onCellClick={handleCellClick}
              disabled={making_move || gameState.current_player !== 'X'}
              winner={winner}
            />
          )}

          <div style={{ marginTop: '20px' }}>
            <button 
              onClick={startNewGame} 
              className="btn btn-success"
              style={{ marginRight: '10px' }}
            >
              New Game
            </button>
            <button onClick={goToDashboard} className="btn btn-secondary">
              Dashboard
            </button>
          </div>

          {gameOver && (
            <div className="card" style={{ marginTop: '20px', backgroundColor: '#f8f9fa' }}>
              <h4>Game Statistics</h4>
              <p><strong>Result:</strong> {result?.toUpperCase()}</p>
              <p><strong>Total Moves:</strong> {gameState?.match?.moves_history?.length || 0}</p>
            </div>
          )}
        </div>
      </div>
    </>
  );
};

export default TicTacToePage;