import React from 'react';
import './TicTacToeBoard.css';

const TicTacToeBoard = ({ board, onCellClick, disabled = false, winner = null }) => {
  const handleCellClick = (row, col) => {
    if (disabled || board[row][col] !== '' || winner) {
      return;
    }
    onCellClick(row, col);
  };

  const getCellClass = (row, col) => {
    let className = 'cell';
    if (board[row][col] !== '') {
      className += ` filled ${board[row][col].toLowerCase()}`;
    }
    if (disabled || winner) {
      className += ' disabled';
    }
    return className;
  };

  return (
    <div className="tic-tac-toe-board">
      {board.map((row, rowIndex) => (
        <div key={rowIndex} className="board-row">
          {row.map((cell, colIndex) => (
            <button
              key={`${rowIndex}-${colIndex}`}
              className={getCellClass(rowIndex, colIndex)}
              onClick={() => handleCellClick(rowIndex, colIndex)}
              disabled={disabled || cell !== '' || winner}
            >
              {cell}
            </button>
          ))}
        </div>
      ))}
    </div>
  );
};

export default TicTacToeBoard;