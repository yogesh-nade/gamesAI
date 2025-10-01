# Board Games Platform

A classic board games platform built with Django backend and React frontend, featuring JWT authentication and AI opponents.

## Features

### Backend (Django + Django REST Framework)
- JWT-based user authentication (register, login, logout)
- User models with gaming statistics
- Game models supporting multiple board games
- REST API endpoints for all game operations
- Tic Tac Toe AI using minimax algorithm with alpha-beta pruning
- Extensible architecture for adding new games

### Frontend (React)
- User authentication with token management
- Dashboard showing user stats and match history
- Interactive Tic Tac Toe game board
- Responsive design
- React Router for navigation
- Axios for API communication

### Currently Implemented
- **Tic Tac Toe**: Full implementation with AI opponent
- User authentication and registration
- Match history and statistics
- Dashboard with game selection

### Coming Soon
- Chess
- Checkers
- Multiplayer support
- Real-time gameplay

## Project Structure

```
board-games-platform/
├── backend/               # Django backend
│   ├── board_games/       # Main Django project
│   ├── accounts/          # User authentication app
│   ├── games/             # Games logic and AI
│   ├── requirements.txt   # Python dependencies
│   └── Dockerfile         # Backend Docker config
├── frontend/              # React frontend
│   ├── src/
│   │   ├── components/    # React components
│   │   ├── pages/         # Page components
│   │   ├── services/      # API services
│   │   └── context/       # React contexts
│   ├── package.json       # Node dependencies
│   └── Dockerfile         # Frontend Docker config
└── docker-compose.yml     # Docker orchestration
```

## Setup Instructions

### Method 1: Using Docker (Recommended)

1. **Clone and navigate to project:**
   ```bash
   cd "AI project"
   ```

2. **Build and run with Docker Compose:**
   ```bash
   docker-compose up --build
   ```

3. **Create Django superuser (in another terminal):**
   ```bash
   docker-compose exec backend python manage.py createsuperuser
   ```

4. **Access the application:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - Django Admin: http://localhost:8000/admin

### Method 2: Local Development

#### Backend Setup

1. **Create Python virtual environment:**
   ```bash
   cd backend
   python -m venv venv
   venv\Scripts\activate  # On Windows
   # source venv/bin/activate  # On Linux/Mac
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Setup environment variables:**
   ```bash
   copy .env.example .env
   # Edit .env with your settings
   ```

4. **Run migrations:**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Create superuser:**
   ```bash
   python manage.py createsuperuser
   ```

6. **Start development server:**
   ```bash
   python manage.py runserver
   ```

#### Frontend Setup

1. **Install Node.js dependencies:**
   ```bash
   cd frontend
   npm install
   ```

2. **Start React development server:**
   ```bash
   npm start
   ```

## API Endpoints

### Authentication
- `POST /api/auth/register/` - User registration
- `POST /api/auth/login/` - User login
- `POST /api/auth/logout/` - User logout
- `GET /api/auth/profile/` - Get user profile

### Games
- `GET /api/games/dashboard/` - Get dashboard data
- `GET /api/games/available/` - Get available games
- `GET /api/games/history/` - Get match history
- `POST /api/games/tic-tac-toe/start/` - Start Tic Tac Toe game
- `GET /api/games/tic-tac-toe/{id}/` - Get game state
- `POST /api/games/tic-tac-toe/{id}/move/` - Make a move

## Usage

1. **Register/Login:** Create an account or login with existing credentials
2. **Dashboard:** View your gaming statistics and match history
3. **Start Game:** Click "Play Tic Tac Toe" to start a new game
4. **Play:** Click on the board to make moves against the AI
5. **View Results:** See game results and updated statistics

## AI Implementation

The Tic Tac Toe AI uses the **minimax algorithm with alpha-beta pruning** for optimal gameplay:
- **Minimax:** Evaluates all possible game states to find the best move
- **Alpha-beta pruning:** Optimizes performance by eliminating unnecessary branches
- **Difficulty:** The AI plays optimally, making it very challenging to beat

## Extending the Platform

### Adding New Games

1. **Create new game model** in `games/models.py`
2. **Implement game logic** and AI in separate files
3. **Add API endpoints** in `games/views.py` and `games/urls.py`
4. **Create React components** for the game interface
5. **Add routes** in React Router

### Example: Adding Chess

1. Create `ChessMatch` model
2. Implement chess rules and AI in `chess_engine.py`
3. Add chess API endpoints
4. Create `ChessBoard` React component
5. Add chess page route

## Technologies Used

### Backend
- Django 4.2
- Django REST Framework
- djangorestframework-simplejwt (JWT tokens)
- django-cors-headers (CORS support)
- SQLite (development) / PostgreSQL (production)

### Frontend
- React 18
- React Router DOM
- Axios (HTTP client)
- CSS3 (custom styling)

### DevOps
- Docker & Docker Compose
- PostgreSQL (production database)

## Development Notes

- **Authentication:** JWT tokens stored in localStorage
- **API Communication:** Axios with automatic token refresh
- **Game State:** Stored in backend database
- **Real-time Updates:** Currently polling-based (WebSocket support planned)
- **Responsive Design:** Mobile-friendly interface

## Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/new-game`)
3. Commit changes (`git commit -am 'Add new game'`)
4. Push to branch (`git push origin feature/new-game`)
5. Create Pull Request

## License

This project is open source and available under the MIT License.