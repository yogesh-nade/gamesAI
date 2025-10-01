from rest_framework import serializers
from .models import Game, Match, TicTacToeMatch, ChessMatch

class GameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Game
        fields = ['id', 'name', 'game_type', 'description', 'max_players', 'min_players']

class MatchSerializer(serializers.ModelSerializer):
    game_name = serializers.CharField(source='game.name', read_only=True)
    game_type = serializers.CharField(source='game.game_type', read_only=True)
    
    class Meta:
        model = Match
        fields = ['id', 'game_name', 'game_type', 'opponent', 'status', 'result', 
                 'started_at', 'completed_at', 'game_state', 'moves_history']
        read_only_fields = ['id', 'started_at', 'completed_at']

class TicTacToeMatchSerializer(serializers.ModelSerializer):
    match = MatchSerializer(read_only=True)
    
    class Meta:
        model = TicTacToeMatch
        fields = ['id', 'match', 'board', 'current_player']
        read_only_fields = ['id']

class TicTacToeMoveSerializer(serializers.Serializer):
    row = serializers.IntegerField(min_value=0, max_value=2)
    col = serializers.IntegerField(min_value=0, max_value=2)

class ChessMatchSerializer(serializers.ModelSerializer):
    match = MatchSerializer(read_only=True)
    
    class Meta:
        model = ChessMatch
        fields = ['id', 'match', 'board', 'current_player', 'fen', 'move_count']
        read_only_fields = ['id']

class ChessMoveSerializer(serializers.Serializer):
    from_row = serializers.IntegerField(min_value=0, max_value=7)
    from_col = serializers.IntegerField(min_value=0, max_value=7)
    to_row = serializers.IntegerField(min_value=0, max_value=7)
    to_col = serializers.IntegerField(min_value=0, max_value=7)
    promotion = serializers.CharField(max_length=1, required=False, allow_blank=True)