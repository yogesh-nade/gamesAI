from django.contrib import admin
from .models import Game, Match, TicTacToeMatch, ChessMatch

@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ['name', 'game_type', 'max_players', 'min_players', 'created_at']
    list_filter = ['game_type', 'created_at']
    search_fields = ['name', 'game_type']

@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ['player', 'game', 'opponent', 'status', 'result', 'started_at']
    list_filter = ['status', 'result', 'game__game_type', 'started_at']
    search_fields = ['player__username', 'opponent']

@admin.register(TicTacToeMatch)
class TicTacToeMatchAdmin(admin.ModelAdmin):
    list_display = ['match', 'current_player']
    list_filter = ['current_player']

@admin.register(ChessMatch)
class ChessMatchAdmin(admin.ModelAdmin):
    list_display = ['match', 'current_player', 'move_count']
    list_filter = ['current_player']
    readonly_fields = ['board', 'fen']