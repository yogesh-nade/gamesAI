import React from 'react';
import { useAuth } from '../context/AuthContext';

const Navbar = () => {
  const { user, logout } = useAuth();

  const handleLogout = async () => {
    await logout();
  };

  return (
    <nav className="navbar">
      <div className="container">
        <h1>Board Games Platform</h1>
        <div>
          <span>Welcome, {user?.username}!</span>
          <button onClick={handleLogout} className="btn btn-secondary" style={{ marginLeft: '10px' }}>
            Logout
          </button>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;