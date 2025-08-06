import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import './HamburgerMenu.css';

const HamburgerMenu: React.FC = () => {
  const [isOpen, setIsOpen] = useState<boolean>(false);
  const { user, logout, isAuthenticated } = useAuth();

  // Prevent body scroll when menu is open
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = 'unset';
    }
    
    // Cleanup on unmount
    return () => {
      document.body.style.overflow = 'unset';
    };
  }, [isOpen]);

  const toggleMenu = (): void => {
    setIsOpen(!isOpen);
  };

  const closeMenu = (): void => {
    setIsOpen(false);
  };

  const handleLogout = (): void => {
    logout();
    closeMenu();
  };

  return (
    <div className="hamburger-menu">
      <button className="hamburger-button" onClick={toggleMenu}>
        <span className={`hamburger-line ${isOpen ? 'open' : ''}`}></span>
        <span className={`hamburger-line ${isOpen ? 'open' : ''}`}></span>
        <span className={`hamburger-line ${isOpen ? 'open' : ''}`}></span>
      </button>
      
      <nav className={`mobile-nav ${isOpen ? 'open' : ''}`}>
        <ul>
          <li>
            <Link to="/" onClick={closeMenu}>🏠 Home</Link>
          </li>
          <li>
            <Link to="/leaderboard" onClick={closeMenu}>🏆 Leaderboard</Link>
          </li>
          {isAuthenticated ? (
            <>
              <li>
                <Link to="/assessment" onClick={closeMenu}>📝 Assessment</Link>
              </li>
              <li>
                <span className="user-greeting">Hello, {user?.name}</span>
              </li>
              <li>
                <button onClick={handleLogout} className="logout-btn">🚪 Logout</button>
              </li>
            </>
          ) : (
            <>
              <li>
                <Link to="/login" onClick={closeMenu}>🔑 Login</Link>
              </li>
              <li>
                <Link to="/register" onClick={closeMenu}>📋 Register</Link>
              </li>
            </>
          )}
        </ul>
      </nav>
      
      {/* Overlay to close menu when clicking outside */}
      {isOpen && <div className="menu-overlay" onClick={closeMenu}></div>}
    </div>
  );
};

export default HamburgerMenu;