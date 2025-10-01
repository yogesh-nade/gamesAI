# Optimized Chess Models using python-chess library
# This file contains the new optimized ChessMatch model

from django.db import models
from accounts.models import User
import chess

def get_default_chess_board():
    """Return default chess starting position"""
    return [
        ['r', 'n', 'b', 'q', 'k', 'b', 'n', 'r'],  # Black pieces (row 0)
        ['p', 'p', 'p', 'p', 'p', 'p', 'p', 'p'],  # Black pawns (row 1)
        ['', '', '', '', '', '', '', ''],             # Empty (row 2)
        ['', '', '', '', '', '', '', ''],             # Empty (row 3)
        ['', '', '', '', '', '', '', ''],             # Empty (row 4)
        ['', '', '', '', '', '', '', ''],             # Empty (row 5)
        ['P', 'P', 'P', 'P', 'P', 'P', 'P', 'P'],  # White pawns (row 6)
        ['R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R'],  # White pieces (row 7)
    ]

class OptimizedChessMatch(models.Model):
    """
    Optimized Chess model using python-chess library for all chess logic
    This is much faster than the previous implementation
    """
    match = models.OneToOneField('Match', on_delete=models.CASCADE)
    
    # Store game state as FEN (Forsyth-Edwards Notation) for efficiency
    fen = models.TextField(default='rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1')
    
    # Keep board array for frontend compatibility (auto-synced from FEN)
    board = models.JSONField(default=get_default_chess_board)
    current_player = models.CharField(max_length=5, default='white')
    
    # Simple move counter
    move_count = models.IntegerField(default=0)
    
    def __str__(self):
        return f"Chess: {self.match}"
    
    def save(self, *args, **kwargs):
        """Auto-sync board array from FEN when saving"""
        self.sync_board_from_fen()
        super().save(*args, **kwargs)
    
    def sync_board_from_fen(self):
        """Update board array from FEN for frontend compatibility"""
        board = chess.Board(self.fen)
        
        # Clear board array
        self.board = [['' for _ in range(8)] for _ in range(8)]
        
        # Fill from chess.Board
        for square in chess.SQUARES:
            piece = board.piece_at(square)
            if piece:
                row = 7 - (square // 8)  # Convert chess.py coordinates to our system
                col = square % 8
                self.board[row][col] = str(piece)
        
        # Update current player from FEN
        self.current_player = 'white' if board.turn else 'black'
    
    def get_chess_board(self):
        """Get python-chess Board object"""
        return chess.Board(self.fen)
    
    def make_move(self, from_row, from_col, to_row, to_col):
        """
        Make a move using optimized chess library
        Much faster than previous implementation
        """
        try:
            board = chess.Board(self.fen)
            
            # Convert our coordinates to chess library format
            from_square = chess.square(from_col, 7 - from_row)
            to_square = chess.square(to_col, 7 - to_row)
            
            # Create move
            move = chess.Move(from_square, to_square)
            
            # Check for pawn promotion (auto-promote to queen for now)
            if board.piece_at(from_square) and board.piece_at(from_square).piece_type == chess.PAWN:
                if (7 - to_row == 0 and board.piece_at(from_square).color == chess.WHITE) or \
                   (7 - to_row == 7 and board.piece_at(from_square).color == chess.BLACK):
                    move = chess.Move(from_square, to_square, promotion=chess.QUEEN)
            
            # Check if move is legal
            if move not in board.legal_moves:
                return False
            
            # Make the move
            board.push(move)
            
            # Update our state
            self.fen = board.fen()
            self.move_count += 1
            
            # Note: save() will auto-sync the board array
            return True
            
        except Exception as e:
            print(f"Chess move error: {e}")
            return False
    
    def make_uci_move(self, uci_move):
        """Make a move from UCI notation (e.g., 'e2e4')"""
        try:
            board = chess.Board(self.fen)
            move = chess.Move.from_uci(uci_move)
            
            if move not in board.legal_moves:
                return False
            
            board.push(move)
            self.fen = board.fen()
            self.move_count += 1
            return True
            
        except Exception as e:
            print(f"UCI move error: {e}")
            return False
    
    def get_legal_moves_for_square(self, row, col):
        """Get legal moves for piece at given square (for frontend highlighting)"""
        try:
            board = chess.Board(self.fen)
            from_square = chess.square(col, 7 - row)
            
            legal_moves = []
            for move in board.legal_moves:
                if move.from_square == from_square:
                    to_row = 7 - (move.to_square // 8)
                    to_col = move.to_square % 8
                    legal_moves.append((to_row, to_col))
            
            return legal_moves
            
        except Exception as e:
            print(f"Error getting legal moves: {e}")
            return []
    
    def is_in_check(self, player=None):
        """Check if the given player's king is in check"""
        try:
            board = chess.Board(self.fen)
            
            if player is None:
                return board.is_check()
            
            # For specific player check
            if player == 'white':
                if board.turn == chess.WHITE:
                    return board.is_check()
                else:
                    # Create temp board with white to move
                    temp_fen_parts = self.fen.split()
                    temp_fen_parts[1] = 'w'
                    temp_fen = ' '.join(temp_fen_parts)
                    temp_board = chess.Board(temp_fen)
                    return temp_board.is_check()
            else:  # player == 'black'
                if board.turn == chess.BLACK:
                    return board.is_check()
                else:
                    # Create temp board with black to move
                    temp_fen_parts = self.fen.split()
                    temp_fen_parts[1] = 'b'
                    temp_fen = ' '.join(temp_fen_parts)
                    temp_board = chess.Board(temp_fen)
                    return temp_board.is_check()
                    
        except Exception as e:
            print(f"Error checking check: {e}")
            return False
    
    def is_game_over(self):
        """Check if the game is over"""
        try:
            board = chess.Board(self.fen)
            return board.is_game_over()
        except Exception as e:
            print(f"Error checking game over: {e}")
            return False
    
    def get_game_result(self):
        """Get the result of the game"""
        try:
            board = chess.Board(self.fen)
            
            if board.is_checkmate():
                # Current player is checkmated, so the other player wins
                if board.turn == chess.WHITE:
                    return 'black_wins'
                else:
                    return 'white_wins'
            elif (board.is_stalemate() or 
                  board.is_insufficient_material() or 
                  board.is_seventyfive_moves() or 
                  board.is_fivefold_repetition()):
                return 'draw'
            else:
                return None  # Game not over
                
        except Exception as e:
            print(f"Error getting game result: {e}")
            return None
    
    def get_piece_at(self, row, col):
        """Get piece at given position (for backward compatibility)"""
        if 0 <= row < 8 and 0 <= col < 8:
            return self.board[row][col]
        return None
    
    def get_game_info(self):
        """Get comprehensive game information"""
        try:
            board = chess.Board(self.fen)
            return {
                'current_player': self.current_player,
                'is_check': board.is_check(),
                'is_game_over': board.is_game_over(),
                'is_checkmate': board.is_checkmate(),
                'is_stalemate': board.is_stalemate(),
                'move_count': self.move_count,
                'fen': self.fen,
                'legal_moves_count': len(list(board.legal_moves))
            }
        except Exception as e:
            print(f"Error getting game info: {e}")
            return {}