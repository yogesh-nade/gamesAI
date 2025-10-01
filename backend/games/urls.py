from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('available/', views.available_games, name='available_games'),
    path('tic-tac-toe/start/', views.start_tic_tac_toe, name='start_tic_tac_toe'),
    path('tic-tac-toe/<int:match_id>/', views.get_tic_tac_toe_match, name='get_tic_tac_toe_match'),
    path('tic-tac-toe/<int:match_id>/move/', views.make_tic_tac_toe_move, name='make_tic_tac_toe_move'),
    path('chess/start/', views.start_chess, name='start_chess'),
    path('chess/<int:match_id>/', views.get_chess_match, name='get_chess_match'),
    path('chess/<int:match_id>/move/', views.make_chess_move, name='make_chess_move'),
    path('chess/<int:match_id>/legal-moves/', views.get_chess_legal_moves, name='get_chess_legal_moves'),
    path('history/', views.match_history, name='match_history'),
]