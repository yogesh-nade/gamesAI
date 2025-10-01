import copy
from typing import List, Tuple, Optional

class ChessAI:
    """AI player for Chess using minimax algorithm with alpha-beta pruning"""
    
    # Piece values for evaluation
    PIECE_VALUES = {
        'p': -100, 'P': 100,    # Pawn
        'n': -320, 'N': 320,    # Knight
        'b': -330, 'B': 330,    # Bishop
        'r': -500, 'R': 500,    # Rook
        'q': -900, 'Q': 900,    # Queen
        'k': -20000, 'K': 20000  # King
    }
    
    # Position values for pieces (encourages good positioning)
    PAWN_TABLE = [
        [0,  0,  0,  0,  0,  0,  0,  0],
        [50, 50, 50, 50, 50, 50, 50, 50],
        [10, 10, 20, 30, 30, 20, 10, 10],
        [5,  5, 10, 25, 25, 10,  5,  5],
        [0,  0,  0, 20, 20,  0,  0,  0],
        [5, -5,-10,  0,  0,-10, -5,  5],
        [5, 10, 10,-20,-20, 10, 10,  5],
        [0,  0,  0,  0,  0,  0,  0,  0]
    ]
    
    KNIGHT_TABLE = [
        [-50,-40,-30,-30,-30,-30,-40,-50],
        [-40,-20,  0,  0,  0,  0,-20,-40],
        [-30,  0, 10, 15, 15, 10,  0,-30],
        [-30,  5, 15, 20, 20, 15,  5,-30],
        [-30,  0, 15, 20, 20, 15,  0,-30],
        [-30,  5, 10, 15, 15, 10,  5,-30],
        [-40,-20,  0,  5,  5,  0,-20,-40],
        [-50,-40,-30,-30,-30,-30,-40,-50]
    ]
    
    BISHOP_TABLE = [
        [-20,-10,-10,-10,-10,-10,-10,-20],
        [-10,  0,  0,  0,  0,  0,  0,-10],
        [-10,  0,  5, 10, 10,  5,  0,-10],
        [-10,  5,  5, 10, 10,  5,  5,-10],
        [-10,  0, 10, 10, 10, 10,  0,-10],
        [-10, 10, 10, 10, 10, 10, 10,-10],
        [-10,  5,  0,  0,  0,  0,  5,-10],
        [-20,-10,-10,-10,-10,-10,-10,-20]
    ]
    
    ROOK_TABLE = [
        [0,  0,  0,  0,  0,  0,  0,  0],
        [5, 10, 10, 10, 10, 10, 10,  5],
        [-5,  0,  0,  0,  0,  0,  0, -5],
        [-5,  0,  0,  0,  0,  0,  0, -5],
        [-5,  0,  0,  0,  0,  0,  0, -5],
        [-5,  0,  0,  0,  0,  0,  0, -5],
        [-5,  0,  0,  0,  0,  0,  0, -5],
        [0,  0,  0,  5,  5,  0,  0,  0]
    ]
    
    QUEEN_TABLE = [
        [-20,-10,-10, -5, -5,-10,-10,-20],
        [-10,  0,  0,  0,  0,  0,  0,-10],
        [-10,  0,  5,  5,  5,  5,  0,-10],
        [-5,  0,  5,  5,  5,  5,  0, -5],
        [0,  0,  5,  5,  5,  5,  0, -5],
        [-10,  5,  5,  5,  5,  5,  0,-10],
        [-10,  0,  5,  0,  0,  0,  0,-10],
        [-20,-10,-10, -5, -5,-10,-10,-20]
    ]
    
    KING_TABLE = [
        [-30,-40,-40,-50,-50,-40,-40,-30],
        [-30,-40,-40,-50,-50,-40,-40,-30],
        [-30,-40,-40,-50,-50,-40,-40,-30],
        [-30,-40,-40,-50,-50,-40,-40,-30],
        [-20,-30,-30,-40,-40,-30,-30,-20],
        [-10,-20,-20,-20,-20,-20,-20,-10],
        [20, 20,  0,  0,  0,  0, 20, 20],
        [20, 30, 10,  0,  0, 10, 30, 20]
    ]
    
    def __init__(self, color='black', max_depth=3):
        self.color = color  # 'white' or 'black'
        self.max_depth = max_depth
    
    def get_best_move(self, chess_match):
        """Get the best move for AI using minimax with alpha-beta pruning"""
        legal_moves = chess_match.get_all_legal_moves(self.color)
        
        if not legal_moves:
            return None
        
        best_move = None
        best_score = float('-inf') if self.color == 'black' else float('inf')
        
        for move in legal_moves:
            from_pos, to_pos = move
            from_row, from_col = from_pos
            to_row, to_col = to_pos
            
            # Make the move
            original_piece = chess_match.get_piece_at(to_row, to_col)
            moving_piece = chess_match.get_piece_at(from_row, from_col)
            
            chess_match.set_piece_at(to_row, to_col, moving_piece)
            chess_match.set_piece_at(from_row, from_col, '')
            
            # Evaluate position
            if self.color == 'black':
                score = self.minimax(chess_match, self.max_depth - 1, False, float('-inf'), float('inf'))
                if score > best_score:
                    best_score = score
                    best_move = move
            else:
                score = self.minimax(chess_match, self.max_depth - 1, True, float('-inf'), float('inf'))
                if score < best_score:
                    best_score = score
                    best_move = move
            
            # Undo the move
            chess_match.set_piece_at(from_row, from_col, moving_piece)
            chess_match.set_piece_at(to_row, to_col, original_piece)
        
        return best_move
    
    def minimax(self, chess_match, depth, is_maximizing, alpha, beta):
        """Minimax algorithm with alpha-beta pruning"""
        # Check terminal conditions
        if depth == 0 or chess_match.is_game_over():
            return self.evaluate_position(chess_match)
        
        current_player = 'black' if is_maximizing else 'white'
        legal_moves = chess_match.get_all_legal_moves(current_player)
        
        if not legal_moves:
            # No legal moves - checkmate or stalemate
            if chess_match.is_in_check(current_player):
                # Checkmate
                return -20000 if is_maximizing else 20000
            else:
                # Stalemate
                return 0
        
        if is_maximizing:
            max_score = float('-inf')
            for move in legal_moves:
                from_pos, to_pos = move
                from_row, from_col = from_pos
                to_row, to_col = to_pos
                
                # Make move
                original_piece = chess_match.get_piece_at(to_row, to_col)
                moving_piece = chess_match.get_piece_at(from_row, from_col)
                
                chess_match.set_piece_at(to_row, to_col, moving_piece)
                chess_match.set_piece_at(from_row, from_col, '')
                
                score = self.minimax(chess_match, depth - 1, False, alpha, beta)
                
                # Undo move
                chess_match.set_piece_at(from_row, from_col, moving_piece)
                chess_match.set_piece_at(to_row, to_col, original_piece)
                
                max_score = max(score, max_score)
                alpha = max(alpha, score)
                
                if beta <= alpha:
                    break  # Alpha-beta pruning
            
            return max_score
        else:
            min_score = float('inf')
            for move in legal_moves:
                from_pos, to_pos = move
                from_row, from_col = from_pos
                to_row, to_col = to_pos
                
                # Make move
                original_piece = chess_match.get_piece_at(to_row, to_col)
                moving_piece = chess_match.get_piece_at(from_row, from_col)
                
                chess_match.set_piece_at(to_row, to_col, moving_piece)
                chess_match.set_piece_at(from_row, from_col, '')
                
                score = self.minimax(chess_match, depth - 1, True, alpha, beta)
                
                # Undo move
                chess_match.set_piece_at(from_row, from_col, moving_piece)
                chess_match.set_piece_at(to_row, to_col, original_piece)
                
                min_score = min(score, min_score)
                beta = min(beta, score)
                
                if beta <= alpha:
                    break  # Alpha-beta pruning
            
            return min_score
    
    def evaluate_position(self, chess_match):
        """Evaluate the current position"""
        score = 0
        
        for row in range(8):
            for col in range(8):
                piece = chess_match.get_piece_at(row, col)
                if piece:
                    # Material value
                    piece_value = self.PIECE_VALUES.get(piece, 0)
                    
                    # Positional value
                    position_value = self.get_position_value(piece, row, col)
                    
                    score += piece_value + position_value
        
        # Add bonus for castling rights, king safety, etc.
        score += self.evaluate_special_factors(chess_match)
        
        return score
    
    def get_position_value(self, piece, row, col):
        """Get positional value for a piece"""
        piece_type = piece.lower()
        is_white = piece.isupper()
        
        # Flip the table for white pieces (they start from bottom)
        eval_row = 7 - row if is_white else row
        
        if piece_type == 'p':
            value = self.PAWN_TABLE[eval_row][col]
        elif piece_type == 'n':
            value = self.KNIGHT_TABLE[eval_row][col]
        elif piece_type == 'b':
            value = self.BISHOP_TABLE[eval_row][col]
        elif piece_type == 'r':
            value = self.ROOK_TABLE[eval_row][col]
        elif piece_type == 'q':
            value = self.QUEEN_TABLE[eval_row][col]
        elif piece_type == 'k':
            value = self.KING_TABLE[eval_row][col]
        else:
            value = 0
        
        return value if is_white else -value
    
    def evaluate_special_factors(self, chess_match):
        """Evaluate special factors like king safety, castling rights"""
        score = 0
        
        # Castling rights bonus
        if not chess_match.white_king_moved:
            if not chess_match.white_rook_king_moved:
                score += 30
            if not chess_match.white_rook_queen_moved:
                score += 30
        
        if not chess_match.black_king_moved:
            if not chess_match.black_rook_king_moved:
                score -= 30
            if not chess_match.black_rook_queen_moved:
                score -= 30
        
        # King safety - penalize being in check
        if chess_match.is_in_check('white'):
            score -= 50
        if chess_match.is_in_check('black'):
            score += 50
        
        return score