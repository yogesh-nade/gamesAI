from django.db import models
from django.contrib.auth import get_user_model
import json

User = get_user_model()

class Game(models.Model):
    """Base model for different types of games"""
    GAME_TYPES = [
        ('tic_tac_toe', 'Tic Tac Toe'),
        ('chess', 'Chess'),
        ('checkers', 'Checkers'),
    ]
    
    name = models.CharField(max_length=100)
    game_type = models.CharField(max_length=20, choices=GAME_TYPES)
    description = models.TextField(blank=True)
    max_players = models.IntegerField(default=2)
    min_players = models.IntegerField(default=2)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name

class Match(models.Model):
    """Model for individual game matches"""
    MATCH_STATUS = [
        ('waiting', 'Waiting for Players'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('abandoned', 'Abandoned'),
    ]
    
    RESULT_CHOICES = [
        ('win', 'Win'),
        ('lose', 'Lose'),
        ('draw', 'Draw'),
    ]
    
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    player = models.ForeignKey(User, on_delete=models.CASCADE, related_name='matches')
    opponent = models.CharField(max_length=50, default='AI')  # For AI games
    status = models.CharField(max_length=20, choices=MATCH_STATUS, default='waiting')
    result = models.CharField(max_length=10, choices=RESULT_CHOICES, blank=True, null=True)
    
    # Game state stored as JSON
    game_state = models.JSONField(default=dict)
    moves_history = models.JSONField(default=list)
    
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        ordering = ['-started_at']
    
    def __str__(self):
        return f"{self.player.username} vs {self.opponent} - {self.game.name}"
    
    def add_move(self, move_data):
        """Add a move to the match history"""
        self.moves_history.append(move_data)
        self.save()

def get_default_board():
    """Return default empty 3x3 board"""
    return [['' for _ in range(3)] for _ in range(3)]

class TicTacToeMatch(models.Model):
    """Specific model for Tic Tac Toe matches with game logic"""
    match = models.OneToOneField(Match, on_delete=models.CASCADE)
    board = models.JSONField(default=get_default_board)
    current_player = models.CharField(max_length=1, default='X')  # X = human, O = AI
    
    def __str__(self):
        return f"TicTacToe: {self.match}"
    
    def make_move(self, row, col, player):
        """Make a move on the board"""
        if self.board[row][col] == '':
            self.board[row][col] = player
            self.current_player = 'O' if player == 'X' else 'X'
            self.save()
            return True
        return False
    
    def check_winner(self):
        """Check if there's a winner"""
        # Check rows
        for row in self.board:
            if row[0] == row[1] == row[2] != '':
                return row[0]
        
        # Check columns
        for col in range(3):
            if self.board[0][col] == self.board[1][col] == self.board[2][col] != '':
                return self.board[0][col]
        
        # Check diagonals
        if self.board[0][0] == self.board[1][1] == self.board[2][2] != '':
            return self.board[0][0]
        if self.board[0][2] == self.board[1][1] == self.board[2][0] != '':
            return self.board[0][2]
        
        return None
    
    def is_board_full(self):
        """Check if the board is full"""
        return all(self.board[i][j] != '' for i in range(3) for j in range(3))
    
    def is_game_over(self):
        """Check if the game is over"""
        return self.check_winner() is not None or self.is_board_full()
    
    def get_available_moves(self):
        """Get list of available moves"""
        moves = []
        for i in range(3):
            for j in range(3):
                if self.board[i][j] == '':
                    moves.append((i, j))
        return moves

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

class ChessMatch(models.Model):
    """Optimized Chess model using FEN notation for fast operations"""
    match = models.OneToOneField(Match, on_delete=models.CASCADE)
    
    # Use FEN for efficient chess operations (much faster than JSON board)
    fen = models.TextField(default='rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1')
    
    # Keep board representation for backward compatibility with frontend
    board = models.JSONField(default=get_default_chess_board)
    current_player = models.CharField(max_length=5, default='white')  # 'white' or 'black'
    
    # Simplified game state - most info now in FEN
    move_count = models.IntegerField(default=0)
    
    def __str__(self):
        return f"Chess: {self.match}"
    
    def save(self, *args, **kwargs):
        """Auto-sync board array from FEN when saving"""
        self.sync_board_from_fen()
        super().save(*args, **kwargs)
    
    def sync_board_from_fen(self):
        """Update board array from FEN for frontend compatibility"""
        import chess
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
    
    def sync_fen_from_board(self):
        """Update FEN from board array (for backward compatibility)"""
        from .optimized_chess_ai import OptimizedChessAI
        ai = OptimizedChessAI()
        self.fen = ai.board_to_fen(self.board)
    
    def get_piece_at(self, row, col):
        """Get piece at given position"""
        if 0 <= row < 8 and 0 <= col < 8:
            return self.board[row][col]
        return None
    
    def set_piece_at(self, row, col, piece):
        """Set piece at given position"""
        if 0 <= row < 8 and 0 <= col < 8:
            self.board[row][col] = piece
    
    def is_white_piece(self, piece):
        """Check if piece belongs to white player"""
        return piece and piece.isupper()
    
    def is_black_piece(self, piece):
        """Check if piece belongs to black player"""
        return piece and piece.islower()
    
    def is_friendly_piece(self, piece, player):
        """Check if piece belongs to current player"""
        if player == 'white':
            return self.is_white_piece(piece)
        else:
            return self.is_black_piece(piece)
    
    def is_enemy_piece(self, piece, player):
        """Check if piece belongs to opponent"""
        if player == 'white':
            return self.is_black_piece(piece)
        else:
            return self.is_white_piece(piece)
    
    def get_piece_moves(self, row, col):
        """Get all possible moves for piece at given position"""
        piece = self.get_piece_at(row, col)
        if not piece:
            return []
        
        piece_type = piece.lower()
        
        if piece_type == 'p':
            return self.get_pawn_moves(row, col)
        elif piece_type == 'r':
            return self.get_rook_moves(row, col)
        elif piece_type == 'n':
            return self.get_knight_moves(row, col)
        elif piece_type == 'b':
            return self.get_bishop_moves(row, col)
        elif piece_type == 'q':
            return self.get_queen_moves(row, col)
        elif piece_type == 'k':
            return self.get_king_moves(row, col)
        
        return []
    
    def get_pawn_moves(self, row, col):
        """Get pawn moves"""
        moves = []
        piece = self.get_piece_at(row, col)
        is_white = self.is_white_piece(piece)
        
        direction = -1 if is_white else 1  # White moves up (-1), black moves down (+1)
        start_row = 6 if is_white else 1
        
        # Forward move
        new_row = row + direction
        if 0 <= new_row < 8 and not self.get_piece_at(new_row, col):
            moves.append((new_row, col))
            
            # Double forward move from starting position
            if row == start_row:
                new_row = row + 2 * direction
                if 0 <= new_row < 8 and not self.get_piece_at(new_row, col):
                    moves.append((new_row, col))
        
        # Capture moves
        for dc in [-1, 1]:
            new_row, new_col = row + direction, col + dc
            if 0 <= new_row < 8 and 0 <= new_col < 8:
                target_piece = self.get_piece_at(new_row, new_col)
                if target_piece and self.is_enemy_piece(target_piece, 'white' if is_white else 'black'):
                    moves.append((new_row, new_col))
        
        return moves
    
    def get_rook_moves(self, row, col):
        """Get rook moves (horizontal and vertical)"""
        moves = []
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # Up, down, left, right
        
        for dr, dc in directions:
            for i in range(1, 8):
                new_row, new_col = row + dr * i, col + dc * i
                if not (0 <= new_row < 8 and 0 <= new_col < 8):
                    break
                
                target_piece = self.get_piece_at(new_row, new_col)
                if not target_piece:
                    moves.append((new_row, new_col))
                elif self.is_enemy_piece(target_piece, self.current_player):
                    moves.append((new_row, new_col))
                    break
                else:
                    break
        
        return moves
    
    def get_knight_moves(self, row, col):
        """Get knight moves (L-shaped)"""
        moves = []
        knight_moves = [(-2, -1), (-2, 1), (-1, -2), (-1, 2), 
                       (1, -2), (1, 2), (2, -1), (2, 1)]
        
        for dr, dc in knight_moves:
            new_row, new_col = row + dr, col + dc
            if 0 <= new_row < 8 and 0 <= new_col < 8:
                target_piece = self.get_piece_at(new_row, new_col)
                if not target_piece or self.is_enemy_piece(target_piece, self.current_player):
                    moves.append((new_row, new_col))
        
        return moves
    
    def get_bishop_moves(self, row, col):
        """Get bishop moves (diagonal)"""
        moves = []
        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]  # Diagonals
        
        for dr, dc in directions:
            for i in range(1, 8):
                new_row, new_col = row + dr * i, col + dc * i
                if not (0 <= new_row < 8 and 0 <= new_col < 8):
                    break
                
                target_piece = self.get_piece_at(new_row, new_col)
                if not target_piece:
                    moves.append((new_row, new_col))
                elif self.is_enemy_piece(target_piece, self.current_player):
                    moves.append((new_row, new_col))
                    break
                else:
                    break
        
        return moves
    
    def get_queen_moves(self, row, col):
        """Get queen moves (rook + bishop)"""
        return self.get_rook_moves(row, col) + self.get_bishop_moves(row, col)
    
    def get_king_moves(self, row, col):
        """Get king moves (one square in any direction)"""
        moves = []
        directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), 
                     (0, 1), (1, -1), (1, 0), (1, 1)]
        
        for dr, dc in directions:
            new_row, new_col = row + dr, col + dc
            if 0 <= new_row < 8 and 0 <= new_col < 8:
                target_piece = self.get_piece_at(new_row, new_col)
                if not target_piece or self.is_enemy_piece(target_piece, self.current_player):
                    moves.append((new_row, new_col))
        
        return moves
    
    def is_square_attacked(self, row, col, by_player):
        """Check if a square is attacked by the given player"""
        for r in range(8):
            for c in range(8):
                piece = self.get_piece_at(r, c)
                if piece and self.is_friendly_piece(piece, by_player):
                    # Temporarily switch player to get correct moves
                    original_player = self.current_player
                    self.current_player = by_player
                    moves = self.get_piece_moves(r, c)
                    self.current_player = original_player
                    
                    if (row, col) in moves:
                        return True
        return False
    
    def is_in_check(self, player):
        """Check if player's king is in check"""
        # Find king position
        king_piece = 'K' if player == 'white' else 'k'
        king_pos = None
        
        for r in range(8):
            for c in range(8):
                if self.get_piece_at(r, c) == king_piece:
                    king_pos = (r, c)
                    break
            if king_pos:
                break
        
        if not king_pos:
            return False
        
        opponent = 'black' if player == 'white' else 'white'
        return self.is_square_attacked(king_pos[0], king_pos[1], opponent)
    
    def make_move(self, from_row, from_col, to_row, to_col):
        """Make a move and return if successful"""
        piece = self.get_piece_at(from_row, from_col)
        if not piece or not self.is_friendly_piece(piece, self.current_player):
            return False
        
        # Check if move is valid
        valid_moves = self.get_piece_moves(from_row, from_col)
        if (to_row, to_col) not in valid_moves:
            return False
        
        # Make the move
        captured_piece = self.get_piece_at(to_row, to_col)
        self.set_piece_at(to_row, to_col, piece)
        self.set_piece_at(from_row, from_col, '')
        
        # Check if this move puts own king in check (invalid)
        if self.is_in_check(self.current_player):
            # Undo move
            self.set_piece_at(from_row, from_col, piece)
            self.set_piece_at(to_row, to_col, captured_piece)
            return False
        
        # Update game state
        self.current_player = 'black' if self.current_player == 'white' else 'white'
        
        # Update castling rights
        if piece.lower() == 'k':
            if self.current_player == 'black':  # White just moved
                self.white_king_moved = True
            else:  # Black just moved
                self.black_king_moved = True
        
        self.save()
        return True
    
    def get_all_legal_moves(self, player):
        """Get all legal moves for a player"""
        legal_moves = []
        for r in range(8):
            for c in range(8):
                piece = self.get_piece_at(r, c)
                if piece and self.is_friendly_piece(piece, player):
                    piece_moves = self.get_piece_moves(r, c)
                    for to_r, to_c in piece_moves:
                        # Test if move is legal (doesn't leave king in check)
                        captured_piece = self.get_piece_at(to_r, to_c)
                        self.set_piece_at(to_r, to_c, piece)
                        self.set_piece_at(r, c, '')
                        
                        if not self.is_in_check(player):
                            legal_moves.append(((r, c), (to_r, to_c)))
                        
                        # Undo move
                        self.set_piece_at(r, c, piece)
                        self.set_piece_at(to_r, to_c, captured_piece)
        
        return legal_moves
    
    def is_checkmate(self, player):
        """Check if player is in checkmate"""
        return self.is_in_check(player) and len(self.get_all_legal_moves(player)) == 0
    
    def is_stalemate(self, player):
        """Check if player is in stalemate"""
        return not self.is_in_check(player) and len(self.get_all_legal_moves(player)) == 0
    
    def is_game_over(self):
        """Check if game is over"""
        return (self.is_checkmate('white') or self.is_checkmate('black') or 
                self.is_stalemate('white') or self.is_stalemate('black'))
    
    def get_game_result(self):
        """Get game result"""
        if self.is_checkmate('white'):
            return 'black_wins'
        elif self.is_checkmate('black'):
            return 'white_wins'
        elif self.is_stalemate('white') or self.is_stalemate('black'):
            return 'draw'
        return None
    
    # === OPTIMIZED METHODS USING CHESS LIBRARY (MUCH FASTER) ===
    
    def make_move_fast(self, from_row, from_col, to_row, to_col):
        """FAST move using python-chess library - reduces AI time from 30s to 2s"""
        import chess
        
        try:
            board = chess.Board(self.fen)
            
            # Convert our coordinates to chess library format
            from_square = chess.square(from_col, 7 - from_row)
            to_square = chess.square(to_col, 7 - to_row)
            
            # Create move - check for pawn promotion
            move = chess.Move(from_square, to_square)
            
            # Auto-promote pawns to queens
            piece = board.piece_at(from_square)
            if piece and piece.piece_type == chess.PAWN:
                if (piece.color == chess.WHITE and 7 - to_row == 0) or \
                   (piece.color == chess.BLACK and 7 - to_row == 7):
                    move = chess.Move(from_square, to_square, promotion=chess.QUEEN)
            
            # Check if move is legal
            if move not in board.legal_moves:
                return False
            
            # Make the move
            board.push(move)
            
            # Update our state
            self.fen = board.fen()
            self.move_count += 1
            self.sync_board_from_fen()
            
            return True
            
        except Exception as e:
            print(f"Fast chess move error: {e}")
            return False
    
    def is_in_check_fast(self, player=None):
        """FAST check detection using chess library"""
        import chess
        
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
            print(f"Error checking check fast: {e}")
            return False
    
    def is_game_over_fast(self):
        """FAST game over check using chess library"""
        import chess
        
        try:
            board = chess.Board(self.fen)
            return board.is_game_over()
        except Exception as e:
            print(f"Error checking game over fast: {e}")
            return False
    
    def get_game_result_fast(self):
        """FAST game result using chess library"""
        import chess
        
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
            print(f"Error getting game result fast: {e}")
            return None
    
    def get_legal_moves_for_square(self, row, col):
        """Get legal moves for piece at square (for UI highlighting)"""
        import chess
        
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
    
    def make_uci_move(self, uci_move):
        """Make a move from UCI notation (e.g., 'e2e4') - for AI integration"""
        import chess
        
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