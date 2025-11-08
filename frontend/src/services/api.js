import axios from 'axios';

const API_BASE_URL = 'https://gamesai-backend-ninm.onrender.com';

// Create axios instance ...
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to requests
api.interceptors.request.use(
  (config) => {
    console.log('Making request to:', config.url);
    console.log('Request config:', config);
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Handle token refresh
api.interceptors.response.use(
  (response) => {
    console.log('Response received:', response.status, response.data);
    return response;
  },
  async (error) => {
    console.error('API Error:', error);
    console.error('Error response:', error.response?.data);
    console.error('Error status:', error.response?.status);
    
    const original = error.config;
    
    if (error.response?.status === 401 && !original._retry) {
      original._retry = true;
      
      const refreshToken = localStorage.getItem('refresh_token');
      if (refreshToken) {
        try {
          const response = await axios.post(`${API_BASE_URL}/auth/token/refresh/`, {
            refresh: refreshToken,
          });
          
          const { access } = response.data;
          localStorage.setItem('access_token', access);
          
          return api(original);
        } catch (refreshError) {
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
          window.location.href = '/login';
        }
      }
    }
    
    return Promise.reject(error);
  }
);

// Auth API
export const authAPI = {
  login: (credentials) => api.post('/api/auth/login/', credentials),
  register: (userData) => api.post('/api/auth/register/', userData),
  logout: (data) => api.post('/api/auth/logout/', data),
  getProfile: () => api.get('/api/auth/profile/'),
};

// Games API
export const gamesAPI = {
  getDashboard: () => api.get('/api/games/dashboard/'),
  getAvailableGames: () => api.get('/api/games/available/'),
  getMatchHistory: () => api.get('/api/games/history/'),
  
  // Tic Tac Toe
  startTicTacToe: () => api.post('/api/games/tic-tac-toe/start/'),
  getTicTacToeMatch: (matchId) => api.get(`/api/games/tic-tac-toe/${matchId}/`),
  makeTicTacToeMove: (matchId, move) => api.post(`/api/games/tic-tac-toe/${matchId}/move/`, move),
  
  // Chess
  startChess: () => api.post('/api/games/chess/start/'),
  getChessMatch: (matchId) => api.get(`/api/games/chess/${matchId}/`),
  makeChessMove: (matchId, move) => api.post(`/api/games/chess/${matchId}/move/`, move),
  getChessLegalMoves: (matchId, position) => api.post(`/api/games/chess/${matchId}/legal-moves/`, position),
};

export default api;