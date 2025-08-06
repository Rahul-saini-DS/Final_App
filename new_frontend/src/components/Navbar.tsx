import { useAuth } from '../contexts/AuthContext';
import { Link } from 'react-router-dom';
import HamburgerMenu from './HamburgerMenu';
import './MobileResponsive.css';

export default function Navbar() {
  const { user, logout, isAuthenticated } = useAuth();

  return (
    <nav className="navbar">
      <div className="navbar-content">
        <Link to="/" className="logo">
          <img src="/logo.png" alt="Born Genius" className="logo-image" />
        </Link>
        <div className="nav-links">
          <Link to="/" className="nav-link">Home</Link>
          <Link to="/leaderboard" className="nav-link">Leaderboard</Link>
          {isAuthenticated ? (
            <>
              <Link to="/assessment" className="nav-link">Assessment</Link>
              <span className="nav-link">Hello, {user?.name}</span>
              <button onClick={logout} className="btn btn-secondary">
                Logout
              </button>
            </>
          ) : (
            <>
              <Link to="/login" className="btn btn-primary">Login</Link>
              <Link to="/register" className="btn btn-secondary">Register</Link>
            </>
          )}
        </div>
        <HamburgerMenu />
      </div>
    </nav>
  );
}
