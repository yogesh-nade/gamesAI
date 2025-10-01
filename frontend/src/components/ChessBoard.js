import React, { useState } from 'react';
import './ChessBoard.css';

const ChessBoard = ({ board, onMove, disabled = false, currentPlayer, legalMoves = [], selectedSquare = null }) => {
  const [draggedPiece, setDraggedPiece] = useState(null);

  const getPieceSymbol = (piece) => {
    const pieceSymbols = {
      'K': '♔', 'Q': '♕', 'R': '♖', 'B': '♗', 'N': '♘', 'P': '♙',
      'k': '♚', 'q': '♛', 'r': '♜', 'b': '♝', 'n': '♞', 'p': '♟'
    };
    return pieceSymbols[piece] || '';
  };

  const isWhitePiece = (piece) => piece && piece === piece.toUpperCase();
  const isBlackPiece = (piece) => piece && piece === piece.toLowerCase();

  const canSelectPiece = (piece, row, col) => {
    if (disabled || !piece) return false;
    if (currentPlayer === 'white' && !isWhitePiece(piece)) return false;
    if (currentPlayer === 'black' && !isBlackPiece(piece)) return false;
    return true;
  };

  const isSquareHighlighted = (row, col) => {
    return legalMoves.some(([r, c]) => r === row && c === col);
  };

  const isSquareSelected = (row, col) => {
    return selectedSquare && selectedSquare[0] === row && selectedSquare[1] === col;
  };

  const handleSquareClick = (row, col) => {
    if (disabled) return;

    const piece = board[row][col];
    
    // If a square is selected and this is a legal move
    if (selectedSquare && isSquareHighlighted(row, col)) {
      onMove(selectedSquare[0], selectedSquare[1], row, col);
      return;
    }

    // If clicking on own piece, select it
    if (canSelectPiece(piece, row, col)) {
      onMove(row, col, null, null); // Signal piece selection
    } else if (selectedSquare) {
      // Deselect if clicking on invalid square
      onMove(null, null, null, null); // Signal deselection
    }
  };

  const handleDragStart = (e, row, col) => {
    const piece = board[row][col];
    if (!canSelectPiece(piece, row, col)) {
      e.preventDefault();
      return;
    }
    setDraggedPiece({ row, col, piece });
    e.dataTransfer.effectAllowed = 'move';
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    e.dataTransfer.dropEffect = 'move';
  };

  const handleDrop = (e, row, col) => {
    e.preventDefault();
    if (!draggedPiece) return;

    const { row: fromRow, col: fromCol } = draggedPiece;
    setDraggedPiece(null);

    if (fromRow === row && fromCol === col) return; // Same square

    onMove(fromRow, fromCol, row, col);
  };

  const getSquareClass = (row, col) => {
    let className = 'chess-square';
    
    // Alternating colors
    if ((row + col) % 2 === 0) {
      className += ' light';
    } else {
      className += ' dark';
    }

    // Highlighting
    if (isSquareSelected(row, col)) {
      className += ' selected';
    } else if (isSquareHighlighted(row, col)) {
      className += ' highlighted';
    }

    return className;
  };

  const renderSquare = (row, col) => {
    const piece = board[row][col];
    const pieceSymbol = getPieceSymbol(piece);

    return (
      <div
        key={`${row}-${col}`}
        className={getSquareClass(row, col)}
        onClick={() => handleSquareClick(row, col)}
        onDragOver={handleDragOver}
        onDrop={(e) => handleDrop(e, row, col)}
      >
        {piece && (
          <div
            className={`chess-piece ${isWhitePiece(piece) ? 'white' : 'black'}`}
            draggable={!disabled && canSelectPiece(piece, row, col)}
            onDragStart={(e) => handleDragStart(e, row, col)}
          >
            {pieceSymbol}
          </div>
        )}
        
        {/* Coordinate labels */}
        {col === 0 && (
          <div className="rank-label">{8 - row}</div>
        )}
        {row === 7 && (
          <div className="file-label">{String.fromCharCode(97 + col)}</div>
        )}
      </div>
    );
  };

  return (
    <div className="chess-board-container">
      <div className="chess-board">
        {board.map((row, rowIndex) =>
          row.map((_, colIndex) => renderSquare(rowIndex, colIndex))
        )}
      </div>
    </div>
  );
};

export default ChessBoard;