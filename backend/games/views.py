from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.contrib.auth import get_user_model

from .models import Game, Match, TicTacToeMatch, ChessMatch
from .serializers import (
    GameSerializer, MatchSerializer, TicTacToeMatchSerializer, 
    TicTacToeMoveSerializer, ChessMatchSerializer, ChessMoveSerializer
)
from .ai_engine import TicTacToeAI
from .optimized_chess_ai import OptimizedChessAI

User = get_user_model()

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard(request):
    """Get dashboard data for the user"""
    user = request.user
    recent_matches = Match.objects.filter(player=user).order_by('-started_at')[:10]
    
    dashboard_data = {
        'user': {
            'username': user.username,
            'total_games': user.total_games,
            'total_wins': user.total_wins,
            'total_losses': user.total_losses,
            'total_draws': user.total_draws,
            'win_rate': user.win_rate,
        },
        'recent_matches': MatchSerializer(recent_matches, many=True).data,
        'available_games': GameSerializer(Game.objects.all(), many=True).data,
    }
    
    return Response(dashboard_data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def available_games(request):
    """Get list of available games"""
    games = Game.objects.all()
    return Response(GameSerializer(games, many=True).data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def start_tic_tac_toe(request):
    """Start a new Tic Tac Toe game"""
    try:
        # Get or create Tic Tac Toe game
        game, created = Game.objects.get_or_create(
            game_type='tic_tac_toe',
            defaults={
                'name': 'Tic Tac Toe',
                'description': 'Classic 3x3 board game',
                'max_players': 2,
                'min_players': 2,
            }
        )
        
        # Create new match
        match = Match.objects.create(
            game=game,
            player=request.user,
            opponent='AI',
            status='in_progress'
        )
        
        # Create TicTacToe specific match
        tic_tac_toe_match = TicTacToeMatch.objects.create(match=match)
        
        return Response({
            'match_id': match.id,
            'tic_tac_toe_match': TicTacToeMatchSerializer(tic_tac_toe_match).data
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_tic_tac_toe_match(request, match_id):
    """Get current state of a Tic Tac Toe match"""
    match = get_object_or_404(Match, id=match_id, player=request.user)
    tic_tac_toe_match = get_object_or_404(TicTacToeMatch, match=match)
    
    return Response(TicTacToeMatchSerializer(tic_tac_toe_match).data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def make_tic_tac_toe_move(request, match_id):
    """Make a move in Tic Tac Toe game"""
    match = get_object_or_404(Match, id=match_id, player=request.user)
    tic_tac_toe_match = get_object_or_404(TicTacToeMatch, match=match)
    
    if match.status != 'in_progress':
        return Response({'error': 'Game is not in progress'}, 
                       status=status.HTTP_400_BAD_REQUEST)
    
    # Validate move
    move_serializer = TicTacToeMoveSerializer(data=request.data)
    if not move_serializer.is_valid():
        return Response(move_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    row = move_serializer.validated_data['row']
    col = move_serializer.validated_data['col']
    
    # Check if it's player's turn
    if tic_tac_toe_match.current_player != 'X':
        return Response({'error': 'Not your turn'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Make player move
    if not tic_tac_toe_match.make_move(row, col, 'X'):
        return Response({'error': 'Invalid move'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Add move to history
    match.add_move({
        'player': 'X',
        'row': row,
        'col': col,
        'timestamp': timezone.now().isoformat()
    })
    
    # Check if game is over after player move
    game_result = check_game_result(tic_tac_toe_match, match, request.user)
    if game_result:
        return Response(game_result)
    
    # Make AI move
    ai = TicTacToeAI()
    ai_row, ai_col = ai.get_best_move(tic_tac_toe_match.board)
    tic_tac_toe_match.make_move(ai_row, ai_col, 'O')
    
    # Add AI move to history
    match.add_move({
        'player': 'O',
        'row': ai_row,
        'col': ai_col,
        'timestamp': timezone.now().isoformat()
    })
    
    # Check if game is over after AI move
    game_result = check_game_result(tic_tac_toe_match, match, request.user)
    if game_result:
        return Response(game_result)
    
    return Response({
        'tic_tac_toe_match': TicTacToeMatchSerializer(tic_tac_toe_match).data,
        'ai_move': {'row': ai_row, 'col': ai_col}
    })

def check_game_result(tic_tac_toe_match, match, user):
    """Check if the game is over and update match result"""
    if tic_tac_toe_match.is_game_over():
        winner = tic_tac_toe_match.check_winner()
        match.status = 'completed'
        match.completed_at = timezone.now()
        
        if winner == 'X':
            match.result = 'win'
            user.total_wins += 1
        elif winner == 'O':
            match.result = 'lose'
            user.total_losses += 1
        else:
            match.result = 'draw'
            user.total_draws += 1
        
        user.total_games += 1
        user.save()
        match.save()
        
        return {
            'game_over': True,
            'winner': winner,
            'result': match.result,
            'tic_tac_toe_match': TicTacToeMatchSerializer(tic_tac_toe_match).data
        }
    
    return None

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def match_history(request):
    """Get match history for the user"""
    matches = Match.objects.filter(player=request.user).order_by('-started_at')
    return Response(MatchSerializer(matches, many=True).data)

# Chess Views
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def start_chess(request):
    """Start a new Chess game"""
    print(f"🔥 start_chess called by user: {request.user}")
    print(f"🔥 Request method: {request.method}")
    print(f"🔥 Request headers: {dict(request.headers)}")
    try:
        # Get or create Chess game
        game, created = Game.objects.get_or_create(
            game_type='chess',
            defaults={
                'name': 'Chess',
                'description': 'Classic chess game with AI opponent',
                'max_players': 2,
                'min_players': 2,
            }
        )
        
        # Create new match
        match = Match.objects.create(
            game=game,
            player=request.user,
            opponent='AI',
            status='in_progress'
        )
        
        # Create Chess specific match
        chess_match = ChessMatch.objects.create(match=match)
        
        return Response({
            'match_id': match.id,
            'chess_match': ChessMatchSerializer(chess_match).data
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        import traceback
        error_details = {
            'error': str(e),
            'type': type(e).__name__,
            'traceback': traceback.format_exc()
        }
        print(f"Chess start error: {error_details}")
        return Response(error_details, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_chess_match(request, match_id):
    """Get current state of a Chess match"""
    match = get_object_or_404(Match, id=match_id, player=request.user)
    chess_match = get_object_or_404(ChessMatch, match=match)
    
    # Add additional game state info using FAST methods
    response_data = ChessMatchSerializer(chess_match).data
    response_data['is_in_check'] = {
        'white': chess_match.is_in_check_fast('white'),
        'black': chess_match.is_in_check_fast('black')
    }
    response_data['is_game_over'] = chess_match.is_game_over_fast()
    
    if chess_match.is_game_over_fast():
        response_data['game_result'] = chess_match.get_game_result_fast()
    
    return Response(response_data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def make_chess_move(request, match_id):
    """Make a move in Chess game"""
    match = get_object_or_404(Match, id=match_id, player=request.user)
    chess_match = get_object_or_404(ChessMatch, match=match)
    
    if match.status != 'in_progress':
        return Response({'error': 'Game is not in progress'}, 
                       status=status.HTTP_400_BAD_REQUEST)
    
    # Validate move
    move_serializer = ChessMoveSerializer(data=request.data)
    if not move_serializer.is_valid():
        return Response(move_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    from_row = move_serializer.validated_data['from_row']
    from_col = move_serializer.validated_data['from_col']
    to_row = move_serializer.validated_data['to_row']
    to_col = move_serializer.validated_data['to_col']
    
    # Check if it's player's turn (human plays white)
    if chess_match.current_player != 'white':
        return Response({'error': 'Not your turn'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Make player move using FAST method
    if not chess_match.make_move_fast(from_row, from_col, to_row, to_col):
        return Response({'error': 'Invalid move'}, status=status.HTTP_400_BAD_REQUEST)
    
    chess_match.save()  # Make sure board is synced
    
    # Add move to history
    match.add_move({
        'player': 'white',
        'from': [from_row, from_col],
        'to': [to_row, to_col],
        'timestamp': timezone.now().isoformat()
    })
    
    # Check if game is over after player move (using FAST method)
    game_result = check_chess_game_result_fast(chess_match, match, request.user)
    if game_result:
        return Response(game_result)
    
    # Make AI move using optimized engine
    ai = OptimizedChessAI(depth=3, max_time=2.0)  # Fast 2-second max
    ai_move_uci = ai.get_best_move(chess_match.fen)
    
    if ai_move_uci:
        import chess
        
        # Convert UCI move (e.g., 'e2e4') to our coordinate system
        move = chess.Move.from_uci(ai_move_uci)
        
        # Convert to our row/col system
        from_square = move.from_square
        to_square = move.to_square
        
        ai_from_row = 7 - (from_square // 8)
        ai_from_col = from_square % 8
        ai_to_row = 7 - (to_square // 8)
        ai_to_col = to_square % 8
        
        # Make the AI move using FASTEST method (UCI)
        if chess_match.make_uci_move(ai_move_uci):
            chess_match.save()  # Sync board
        
        # Add AI move to history
        match.add_move({
            'player': 'black',
            'from': [ai_from_row, ai_from_col],
            'to': [ai_to_row, ai_to_col],
            'move_uci': ai_move_uci,
            'timestamp': timezone.now().isoformat()
        })
    
    # Check if game is over after AI move (using FAST method)
    game_result = check_chess_game_result_fast(chess_match, match, request.user)
    if game_result:
        return Response(game_result)

    response_data = {
        'chess_match': ChessMatchSerializer(chess_match).data,
        'is_in_check': {
            'white': chess_match.is_in_check_fast('white'),
            'black': chess_match.is_in_check_fast('black')
        }
    }
    
    if ai_move_uci:
        response_data['ai_move'] = {
            'from': [ai_from_row, ai_from_col],
            'to': [ai_to_row, ai_to_col],
            'uci': ai_move_uci
        }
    
    return Response(response_data)

def check_chess_game_result_fast(chess_match, match, user):
    """FAST check if chess game is over using optimized methods"""
    if chess_match.is_game_over_fast():
        match.status = 'completed'
        match.completed_at = timezone.now()
        
        game_result = chess_match.get_game_result_fast()
        
        if game_result == 'white_wins':
            match.result = 'win'
            user.total_wins += 1
        elif game_result == 'black_wins':
            match.result = 'lose'
            user.total_losses += 1
        else:  # draw
            match.result = 'draw'
            user.total_draws += 1
        
        user.total_games += 1
        user.save()
        match.save()
        
        return {
            'game_over': True,
            'game_result': game_result,
            'result': match.result,
            'chess_match': ChessMatchSerializer(chess_match).data
        }
    
    return None

def check_chess_game_result(chess_match, match, user):
    """Check if the chess game is over and update match result (OLD SLOW VERSION)"""
    if chess_match.is_game_over():
        match.status = 'completed'
        match.completed_at = timezone.now()
        
        game_result = chess_match.get_game_result()
        
        if game_result == 'white_wins':
            match.result = 'win'
            user.total_wins += 1
        elif game_result == 'black_wins':
            match.result = 'lose'
            user.total_losses += 1
        else:  # draw
            match.result = 'draw'
            user.total_draws += 1
        
        user.total_games += 1
        user.save()
        match.save()
        
        return {
            'game_over': True,
            'game_result': game_result,
            'result': match.result,
            'chess_match': ChessMatchSerializer(chess_match).data
        }
    
    return None

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def get_chess_legal_moves(request, match_id):
    """Get legal moves for a piece at given position"""
    match = get_object_or_404(Match, id=match_id, player=request.user)
    chess_match = get_object_or_404(ChessMatch, match=match)
    
    try:
        row = request.data.get('row')
        col = request.data.get('col')
        
        if row is None or col is None:
            return Response({'error': 'Row and col required'}, status=status.HTTP_400_BAD_REQUEST)
        
        piece = chess_match.get_piece_at(row, col)
        if not piece:
            return Response({'legal_moves': []})
        
        # Check if it's the player's piece
        if not chess_match.is_friendly_piece(piece, 'white'):
            return Response({'legal_moves': []})
        
        # Get all legal moves and filter for this piece
        all_legal_moves = chess_match.get_all_legal_moves('white')
        piece_moves = []
        
        for move in all_legal_moves:
            from_pos, to_pos = move
            if from_pos == (row, col):
                piece_moves.append(list(to_pos))
        
        return Response({'legal_moves': piece_moves})
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)