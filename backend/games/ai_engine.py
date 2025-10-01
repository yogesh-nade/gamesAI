import copy
from typing import List, Tuple, Optional

class TicTacToeAI:
    """AI player for Tic Tac Toe using minimax algorithm with alpha-beta pruning"""
    
    def __init__(self, ai_symbol='O', human_symbol='X'):
        self.ai_symbol = ai_symbol
        self.human_symbol = human_symbol
    
    def get_best_move(self, board: List[List[str]]) -> Tuple[int, int]:
        """Get the best move for AI using minimax with alpha-beta pruning"""
        best_score = float('-inf')
        best_move = None
        
        for row in range(3):
            for col in range(3):
                if board[row][col] == '':
                    # Make the move
                    board[row][col] = self.ai_symbol
                    
                    # Calculate score
                    score = self.minimax(board, 0, False, float('-inf'), float('inf'))
                    
                    # Undo the move
                    board[row][col] = ''
                    
                    if score > best_score:
                        best_score = score
                        best_move = (row, col)
        
        return best_move if best_move else (0, 0)
    
    def minimax(self, board: List[List[str]], depth: int, is_maximizing: bool, 
                alpha: float, beta: float) -> int:
        """Minimax algorithm with alpha-beta pruning"""
        winner = self.check_winner(board)
        
        # Base cases
        if winner == self.ai_symbol:
            return 10 - depth
        elif winner == self.human_symbol:
            return depth - 10
        elif self.is_board_full(board):
            return 0
        
        if is_maximizing:
            max_score = float('-inf')
            for row in range(3):
                for col in range(3):
                    if board[row][col] == '':
                        board[row][col] = self.ai_symbol
                        score = self.minimax(board, depth + 1, False, alpha, beta)
                        board[row][col] = ''
                        
                        max_score = max(score, max_score)
                        alpha = max(alpha, score)
                        
                        if beta <= alpha:
                            break  # Alpha-beta pruning
                if beta <= alpha:
                    break
            return max_score
        else:
            min_score = float('inf')
            for row in range(3):
                for col in range(3):
                    if board[row][col] == '':
                        board[row][col] = self.human_symbol
                        score = self.minimax(board, depth + 1, True, alpha, beta)
                        board[row][col] = ''
                        
                        min_score = min(score, min_score)
                        beta = min(beta, score)
                        
                        if beta <= alpha:
                            break  # Alpha-beta pruning
                if beta <= alpha:
                    break
            return min_score
    
    def check_winner(self, board: List[List[str]]) -> Optional[str]:
        """Check if there's a winner on the board"""
        # Check rows
        for row in board:
            if row[0] == row[1] == row[2] != '':
                return row[0]
        
        # Check columns
        for col in range(3):
            if board[0][col] == board[1][col] == board[2][col] != '':
                return board[0][col]
        
        # Check diagonals
        if board[0][0] == board[1][1] == board[2][2] != '':
            return board[0][0]
        if board[0][2] == board[1][1] == board[2][0] != '':
            return board[0][2]
        
        return None
    
    def is_board_full(self, board: List[List[str]]) -> bool:
        """Check if the board is full"""
        return all(board[i][j] != '' for i in range(3) for j in range(3))
    
    def evaluate_position(self, board: List[List[str]]) -> int:
        """Evaluate the current board position"""
        winner = self.check_winner(board)
        if winner == self.ai_symbol:
            return 1
        elif winner == self.human_symbol:
            return -1
        else:
            return 0