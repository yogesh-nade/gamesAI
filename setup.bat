@echo off
echo Setting up Board Games Platform...
echo.

echo Creating Python virtual environment...
cd backend
python -m venv venv
call venv\Scripts\activate

echo Installing Python dependencies...
pip install -r requirements.txt

echo Running Django migrations...
python manage.py makemigrations accounts
python manage.py makemigrations games
python manage.py migrate

echo Creating sample game data...
python manage.py shell -c "
from games.models import Game
if not Game.objects.filter(game_type='tic_tac_toe').exists():
    Game.objects.create(
        name='Tic Tac Toe',
        game_type='tic_tac_toe',
        description='Classic 3x3 board game',
        max_players=2,
        min_players=2
    )
    print('Created Tic Tac Toe game')
"

echo.
echo Django setup complete!
echo.
echo To create a superuser, run: python manage.py createsuperuser
echo To start the backend server, run: python manage.py runserver
echo.
echo Setting up React frontend...
cd ..\frontend

if exist "node_modules\" (
    echo Node modules already exist, skipping npm install
) else (
    echo Installing Node.js dependencies...
    npm install
)

echo.
echo Frontend setup complete!
echo.
echo To start the frontend server, run: npm start
echo.
echo Setup finished! You can now:
echo 1. Start the backend: cd backend && python manage.py runserver
echo 2. Start the frontend: cd frontend && npm start
echo 3. Or use Docker: docker-compose up --build
echo.
pause