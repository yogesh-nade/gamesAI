import React, { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import Navbar from '../components/Navbar';
import ChessBoard from '../components/ChessBoard';
import { gamesAPI } from '../services/api';

const ChessPage = () => {
  const { matchId } = useParams();
  const navigate = useNavigate();
  const [gameState, setGameState] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [makingMove, setMakingMove] = useState(false);
  const [gameOver, setGameOver] = useState(false);
  const [gameResult, setGameResult] = useState(null);
  const [selectedSquare, setSelectedSquare] = useState(null);
  const [legalMoves, setLegalMoves] = useState([]);
  const [isInCheck, setIsInCheck] = useState({ white: false, black: false });

  const fetchGameState = useCallback(async () => {
    try {
      const response = await gamesAPI.getChessMatch(matchId);
      setGameState(response.data);
      setIsInCheck(response.data.is_in_check || { white: false, black: false });
      
      // Check if game is already over
      if (response.data.match.status === 'completed' || response.data.is_game_over) {
        setGameOver(true);
        setGameResult(response.data.game_result);
      }
    } catch (err) {
      setError('Failed to load game state');
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, [matchId]);

  useEffect(() => {
    fetchGameState();
  }, [fetchGameState]);

  const handleSquareClick = async (fromRow, fromCol, toRow, toCol) => {
    if (makingMove || gameOver) return;

    // If toRow is null, this is a piece selection/deselection
    if (toRow === null) {
      if (fromRow === null) {
        // Deselect
        setSelectedSquare(null);
        setLegalMoves([]);
      } else {
        // Select piece and get legal moves
        try {
          const response = await gamesAPI.getChessLegalMoves(matchId, { 
            row: fromRow, 
            col: fromCol 
          });
          setSelectedSquare([fromRow, fromCol]);
          setLegalMoves(response.data.legal_moves || []);
        } catch (err) {
          console.error('Failed to get legal moves:', err);
          setLegalMoves([]);
        }
      }
      return;
    }

    // This is a move attempt
    setMakingMove(true);
    setError('');

    try {
      const response = await gamesAPI.makeChessMove(matchId, {
        from_row: fromRow,
        from_col: fromCol,
        to_row: toRow,
        to_col: toCol
      });

      if (response.data.game_over) {
        setGameOver(true);
        setGameResult(response.data.game_result);
        setGameState(response.data.chess_match);
      } else {
        setGameState(response.data.chess_match);
        setIsInCheck(response.data.is_in_check || { white: false, black: false });
      }

      // Clear selection after successful move
      setSelectedSquare(null);
      setLegalMoves([]);

    } catch (err) {
      setError(err.response?.data?.error || 'Failed to make move');
      console.error(err);
    } finally {
      setMakingMove(false);
    }
  };

  const startNewGame = async () => {
    try {
      const response = await gamesAPI.startChess();
      const newMatchId = response.data.match_id;
      navigate(`/chess/${newMatchId}`);
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
      if (gameResult === 'white_wins') {
        return { message: '🎉 You Won!', color: '#28a745' };
      } else if (gameResult === 'black_wins') {
        return { message: '😔 You Lost!', color: '#dc3545' };
      } else {
        return { message: "🤝 It's a Draw!", color: '#6c757d' };
      }
    } else if (makingMove) {
      return { message: 'AI is thinking...', color: '#ffc107' };
    } else if (gameState?.current_player === 'white') {
      const checkStatus = isInCheck.white ? ' (Check!)' : '';
      return { message: `Your turn (White)${checkStatus}`, color: isInCheck.white ? '#dc3545' : '#007bff' };
    } else {
      const checkStatus = isInCheck.black ? ' (Check!)' : '';
      return { message: `AI turn (Black)${checkStatus}`, color: isInCheck.black ? '#dc3545' : '#dc3545' };
    }
  };

  const formatGameResult = (result) => {
    switch (result) {
      case 'white_wins': return 'White Wins';
      case 'black_wins': return 'Black Wins';
      case 'draw': return 'Draw';
      default: return '';
    }
  };

  if (loading) {
    return (
      <>
        <Navbar />
        <div className="container">
          <div className="loading">Loading chess game...</div>
        </div>
      </>
    );
  }

  if (error && !gameState) {
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
        <div className="card" style={{ textAlign: 'center', maxWidth: '800px', margin: '0 auto' }}>
          <h2>♟️ Chess</h2>
          
          <div style={{ 
            fontSize: '1.2em', 
            fontWeight: 'bold', 
            color: status.color,
            margin: '20px 0' 
          }}>
            {status.message}
          </div>

          {error && (
            <div className="error" style={{ marginBottom: '20px' }}>
              {error}
            </div>
          )}

          {gameState && (
            <ChessBoard
              board={gameState.board}
              onMove={handleSquareClick}
              disabled={makingMove || gameState.current_player !== 'white'}
              currentPlayer={gameState.current_player}
              legalMoves={legalMoves}
              selectedSquare={selectedSquare}
            />
          )}

          {/* Game Info Panel */}
          <div className="card" style={{ margin: '20px 0', backgroundColor: '#f8f9fa' }}>
            <h4>Game Information</h4>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px', textAlign: 'left' }}>
              <div><strong>Current Turn:</strong> {gameState?.current_player === 'white' ? 'White (You)' : 'Black (AI)'}</div>
              <div><strong>Move:</strong> {gameState?.fullmove_number || 1}</div>
              <div><strong>White in Check:</strong> {isInCheck.white ? 'Yes' : 'No'}</div>
              <div><strong>Black in Check:</strong> {isInCheck.black ? 'Yes' : 'No'}</div>
            </div>
          </div>

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
              <h4>Game Over</h4>
              <p><strong>Result:</strong> {formatGameResult(gameResult)}</p>
              <p><strong>Total Moves:</strong> {gameState?.match?.moves_history?.length || 0}</p>
              {gameState?.match?.moves_history && gameState.match.moves_history.length > 0 && (
                <div style={{ textAlign: 'left', maxHeight: '200px', overflow: 'auto' }}>
                  <strong>Move History:</strong>
                  <div style={{ fontSize: '0.9em', marginTop: '10px' }}>
                    {gameState.match.moves_history.map((move, index) => (
                      <div key={index} style={{ marginBottom: '5px' }}>
                        {Math.floor(index / 2) + 1}. {index % 2 === 0 ? 'White' : 'Black'}: 
                        {` ${String.fromCharCode(97 + move.from[1])}${8 - move.from[0]} → ${String.fromCharCode(97 + move.to[1])}${8 - move.to[0]}`}
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </>
  );
};

export default ChessPage;