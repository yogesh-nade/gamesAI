import chess
import chess.engine
import time
from typing import Dict, Optional, Tuple

class OptimizedChessAI:
    """Fast Chess AI using python-chess library with optimized minimax and alpha-beta pruning"""
    
    def __init__(self, depth: int = 3, max_time: float = 2.0):
        """
        Initialize the AI with configurable depth and time limits
        
        Args:
            depth: Maximum search depth (3-4 recommended for fast play)
            max_time: Maximum thinking time in seconds
        """
        self.depth = depth
        self.max_time = max_time
        self.transposition_table: Dict[str, Tuple[float, int]] = {}
        self.start_time = 0
        self.nodes_searched = 0
        
        # Piece values for quick evaluation
        self.PIECE_VALUES = {
            chess.PAWN: 100,
            chess.ROOK: 500,
            chess.KNIGHT: 320,
            chess.BISHOP: 330,
            chess.QUEEN: 900,
            chess.KING: 20000
        }
        
        # Piece-square tables for positional evaluation (simplified)
        self.PST = {
            chess.PAWN: [
                0,  0,  0,  0,  0,  0,  0,  0,
                50, 50, 50, 50, 50, 50, 50, 50,
                10, 10, 20, 30, 30, 20, 10, 10,
                5,  5, 10, 25, 25, 10,  5,  5,
                0,  0,  0, 20, 20,  0,  0,  0,
                5, -5,-10,  0,  0,-10, -5,  5,
                5, 10, 10,-20,-20, 10, 10,  5,
                0,  0,  0,  0,  0,  0,  0,  0
            ],
            chess.KNIGHT: [
                -50,-40,-30,-30,-30,-30,-40,-50,
                -40,-20,  0,  0,  0,  0,-20,-40,
                -30,  0, 10, 15, 15, 10,  0,-30,
                -30,  5, 15, 20, 20, 15,  5,-30,
                -30,  0, 15, 20, 20, 15,  0,-30,
                -30,  5, 10, 15, 15, 10,  5,-30,
                -40,-20,  0,  5,  5,  0,-20,-40,
                -50,-40,-30,-30,-30,-30,-40,-50
            ],
            chess.BISHOP: [
                -20,-10,-10,-10,-10,-10,-10,-20,
                -10,  0,  0,  0,  0,  0,  0,-10,
                -10,  0,  5, 10, 10,  5,  0,-10,
                -10,  5,  5, 10, 10,  5,  5,-10,
                -10,  0, 10, 10, 10, 10,  0,-10,
                -10, 10, 10, 10, 10, 10, 10,-10,
                -10,  5,  0,  0,  0,  0,  5,-10,
                -20,-10,-10,-10,-10,-10,-10,-20
            ],
            chess.ROOK: [
                0,  0,  0,  0,  0,  0,  0,  0,
                5, 10, 10, 10, 10, 10, 10,  5,
                -5,  0,  0,  0,  0,  0,  0, -5,
                -5,  0,  0,  0,  0,  0,  0, -5,
                -5,  0,  0,  0,  0,  0,  0, -5,
                -5,  0,  0,  0,  0,  0,  0, -5,
                -5,  0,  0,  0,  0,  0,  0, -5,
                0,  0,  0,  5,  5,  0,  0,  0
            ],
            chess.QUEEN: [
                -20,-10,-10, -5, -5,-10,-10,-20,
                -10,  0,  0,  0,  0,  0,  0,-10,
                -10,  0,  5,  5,  5,  5,  0,-10,
                -5,  0,  5,  5,  5,  5,  0, -5,
                0,  0,  5,  5,  5,  5,  0, -5,
                -10,  5,  5,  5,  5,  5,  0,-10,
                -10,  0,  5,  0,  0,  0,  0,-10,
                -20,-10,-10, -5, -5,-10,-10,-20
            ],
            chess.KING: [
                -30,-40,-40,-50,-50,-40,-40,-30,
                -30,-40,-40,-50,-50,-40,-40,-30,
                -30,-40,-40,-50,-50,-40,-40,-30,
                -30,-40,-40,-50,-50,-40,-40,-30,
                -20,-30,-30,-40,-40,-30,-30,-20,
                -10,-20,-20,-20,-20,-20,-20,-10,
                20, 20,  0,  0,  0,  0, 20, 20,
                20, 30, 10,  0,  0, 10, 30, 20
            ]
        }

    def get_best_move(self, fen: str) -> Optional[str]:
        """
        Get the best move for the current position
        
        Args:
            fen: FEN string representation of the board
            
        Returns:
            Best move in UCI format (e.g., 'e2e4') or None if no moves available
        """
        board = chess.Board(fen)
        
        if board.is_game_over():
            return None
        
        self.start_time = time.time()
        self.nodes_searched = 0
        self.transposition_table.clear()  # Clear for new search
        
        best_move = None
        best_score = float('-inf') if board.turn else float('inf')
        
        # Get and order moves (captures and checks first for better pruning)
        moves = self.order_moves(board, list(board.legal_moves))
        
        for move in moves:
            if time.time() - self.start_time > self.max_time:
                break
                
            board.push(move)
            
            # Search with iterative deepening for better time management
            score = self.minimax(board, self.depth - 1, not board.turn, 
                               float('-inf'), float('inf'))
            
            board.pop()
            
            if board.turn:  # White to move (maximizing)
                if score > best_score:
                    best_score = score
                    best_move = move
            else:  # Black to move (minimizing)  
                if score < best_score:
                    best_score = score
                    best_move = move
        
        print(f"AI searched {self.nodes_searched} nodes in {time.time() - self.start_time:.2f}s")
        return str(best_move) if best_move else None

    def order_moves(self, board: chess.Board, moves: list) -> list:
        """
        Order moves for better alpha-beta pruning
        Captures and checks first, then other moves
        """
        def move_priority(move):
            priority = 0
            
            # Captures get high priority
            if board.is_capture(move):
                captured_piece = board.piece_at(move.to_square)
                if captured_piece:
                    priority += self.PIECE_VALUES[captured_piece.piece_type] // 10
                    
            # Checks get priority
            board.push(move)
            if board.is_check():
                priority += 50
            board.pop()
            
            # Promotions get priority
            if move.promotion:
                priority += 800
                
            return -priority  # Negative for descending sort
        
        return sorted(moves, key=move_priority)

    def minimax(self, board: chess.Board, depth: int, is_maximizing: bool, 
                alpha: float, beta: float) -> float:
        """
        Minimax with alpha-beta pruning and transposition table
        """
        self.nodes_searched += 1
        
        # Check time limit
        if time.time() - self.start_time > self.max_time:
            return self.evaluate_position(board)
        
        # Check transposition table
        board_hash = str(board.fen())
        if board_hash in self.transposition_table:
            stored_score, stored_depth = self.transposition_table[board_hash]
            if stored_depth >= depth:
                return stored_score
        
        # Terminal conditions
        if depth == 0 or board.is_game_over():
            score = self.evaluate_position(board)
            self.transposition_table[board_hash] = (score, depth)
            return score
        
        legal_moves = list(board.legal_moves)
        if not legal_moves:
            if board.is_check():
                # Checkmate
                score = -20000 if is_maximizing else 20000
            else:
                # Stalemate
                score = 0
            self.transposition_table[board_hash] = (score, depth)
            return score
        
        # Order moves for better pruning
        moves = self.order_moves(board, legal_moves)
        
        if is_maximizing:
            max_score = float('-inf')
            for move in moves:
                board.push(move)
                score = self.minimax(board, depth - 1, False, alpha, beta)
                board.pop()
                
                max_score = max(score, max_score)
                alpha = max(alpha, score)
                
                if beta <= alpha:
                    break  # Alpha-beta cutoff
            
            self.transposition_table[board_hash] = (max_score, depth)
            return max_score
        else:
            min_score = float('inf')
            for move in moves:
                board.push(move)
                score = self.minimax(board, depth - 1, True, alpha, beta)
                board.pop()
                
                min_score = min(score, min_score)
                beta = min(beta, score)
                
                if beta <= alpha:
                    break  # Alpha-beta cutoff
            
            self.transposition_table[board_hash] = (min_score, depth)
            return min_score

    def evaluate_position(self, board: chess.Board) -> float:
        """
        Fast position evaluation using material and piece-square tables
        """
        if board.is_checkmate():
            return -20000 if board.turn else 20000
        
        if board.is_stalemate() or board.is_insufficient_material():
            return 0
        
        score = 0
        
        # Material and positional evaluation
        for square in chess.SQUARES:
            piece = board.piece_at(square)
            if piece:
                value = self.PIECE_VALUES[piece.piece_type]
                
                # Positional bonus
                if piece.piece_type in self.PST:
                    square_index = square if piece.color else chess.square_mirror(square)
                    value += self.PST[piece.piece_type][square_index] // 10
                
                # Apply color
                if piece.color == chess.WHITE:
                    score += value
                else:
                    score -= value
        
        # Mobility bonus (number of legal moves)
        mobility = len(list(board.legal_moves))
        score += mobility * 2 if board.turn else -mobility * 2
        
        # King safety
        if board.is_check():
            score += -50 if board.turn else 50
            
        return score

    def board_to_fen(self, board_array) -> str:
        """
        Convert our internal board representation to FEN string
        """
        # Map our pieces to python-chess format
        piece_map = {
            'P': 'P', 'R': 'R', 'N': 'N', 'B': 'B', 'Q': 'Q', 'K': 'K',
            'p': 'p', 'r': 'r', 'n': 'n', 'b': 'b', 'q': 'q', 'k': 'k'
        }
        
        fen_rows = []
        for row in board_array:
            fen_row = ""
            empty_count = 0
            
            for cell in row:
                if cell == '' or cell is None:
                    empty_count += 1
                else:
                    if empty_count > 0:
                        fen_row += str(empty_count)
                        empty_count = 0
                    fen_row += piece_map.get(cell, '')
            
            if empty_count > 0:
                fen_row += str(empty_count)
            fen_rows.append(fen_row)
        
        board_fen = "/".join(fen_rows)
        
        # Default additional FEN components (we'll improve this later)
        return f"{board_fen} w KQkq - 0 1"

    def fen_to_board_array(self, fen: str) -> list:
        """
        Convert FEN string to our internal board representation
        """
        board = chess.Board(fen)
        board_array = [['' for _ in range(8)] for _ in range(8)]
        
        for square in chess.SQUARES:
            piece = board.piece_at(square)
            if piece:
                row = 7 - (square // 8)  # Convert to our coordinate system
                col = square % 8
                board_array[row][col] = str(piece)
        
        return board_array