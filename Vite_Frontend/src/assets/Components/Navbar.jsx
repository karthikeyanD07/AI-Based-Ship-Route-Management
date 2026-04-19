import React, { useState, useEffect, useRef } from "react";
import "../Styles/Navbar.css";
import { Link, useLocation } from "react-router-dom";
import MenuIcon from "@mui/icons-material/Menu";
import CloseIcon from "@mui/icons-material/Close";
import MapIcon from "@mui/icons-material/Map";
import AltRouteIcon from "@mui/icons-material/AltRoute";
import DashboardIcon from "@mui/icons-material/Dashboard";
import PersonIcon from "@mui/icons-material/Person";
import HomeIcon from "@mui/icons-material/Home";

const Navbar = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [showProfile, setShowProfile] = useState(false);
  const [theme, setTheme] = useState(() => localStorage.getItem('theme') || 'dark');
  const location = useLocation();
  const profileRef = useRef(null);
  const sidebarRef = useRef(null);

  // P6: Active route highlight
  const isActive = (path) => location.pathname === path;

  const toggleNavbar = () => setIsOpen(prev => !prev);
  const handleShowProfile = () => setShowProfile(prev => !prev);

  const toggleTheme = () => {
    const next = theme === 'dark' ? 'light' : 'dark';
    setTheme(next);
    localStorage.setItem('theme', next);
    document.documentElement.setAttribute('data-theme', next);
  };

  // I6: Close sidebar and profile on outside click
  useEffect(() => {
    const handleOutsideClick = (e) => {
      if (profileRef.current && !profileRef.current.contains(e.target)) {
        setShowProfile(false);
      }
      if (sidebarRef.current && !sidebarRef.current.contains(e.target) && isOpen) {
        // Don't close when clicking the menu toggle itself
        const menuToggle = document.querySelector('.menu-toggle');
        if (!menuToggle?.contains(e.target)) {
          setIsOpen(false);
        }
      }
    };
    document.addEventListener('mousedown', handleOutsideClick);
    return () => document.removeEventListener('mousedown', handleOutsideClick);
  }, [isOpen]);

  // Apply theme on mount and change
  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
  }, [theme]);

  // V9: Update page title per route
  useEffect(() => {
    const titles = {
      '/dashboard': 'Command Center — NeoECDIS',
      '/navigation': 'Smart Navigator — NeoECDIS',
      '/routes': 'Route Optimizer — NeoECDIS',
      '/settings': 'Settings — NeoECDIS',
    };
    document.title = titles[location.pathname] || 'NeoECDIS Maritime Intelligence';
  }, [location.pathname]);

  return (
    <div>
      <header className="navbar-header">
        <div className="menu-toggle" onClick={toggleNavbar}>
          {isOpen ? <CloseIcon style={{ fontSize: "28px" }} /> : <MenuIcon style={{ fontSize: "28px" }} />}
        </div>
        <div className="navbar-title">
          <h1 style={{ color: "#e6ebf2", fontWeight: 600, letterSpacing: 0.4 }}>NeoECDIS</h1>
        </div>
        <div ref={profileRef}>
          <div className="navbar-profile" onClick={handleShowProfile}>
            <PersonIcon style={{ fontSize: "26px" }} />
          </div>
          {showProfile && (
            <div className="profile-card">
              <div className="profile-row"><strong>Signed in</strong> as Captain</div>
              <button className="profile-btn" onClick={toggleTheme}>
                {theme === 'dark' ? '☀️ Switch to Light' : '🌙 Switch to Dark'}
              </button>
              <div className="profile-links">
                <Link to="/routes" onClick={() => setShowProfile(false)}>Plan Route</Link>
                <Link to="/navigation" onClick={() => setShowProfile(false)}>Live Map</Link>
                <Link to="/settings" onClick={() => setShowProfile(false)}>Settings</Link>
              </div>
            </div>
          )}
        </div>
      </header>

      <main ref={sidebarRef} className={`navbar-main ${isOpen ? "open" : ""}`}>
        <nav>
          <ul>
            <Link to="/dashboard" onClick={() => setIsOpen(false)}>
              <li className={isActive('/dashboard') ? 'nav-active' : ''}>
                <DashboardIcon />
                <span>Captain's Dashboard</span>
              </li>
            </Link>
            <Link to="/navigation" onClick={() => setIsOpen(false)}>
              <li className={isActive('/navigation') ? 'nav-active' : ''}>
                <MapIcon />
                <span>Smart Navigator</span>
              </li>
            </Link>
            <Link to="/routes" onClick={() => setIsOpen(false)}>
              <li className={isActive('/routes') ? 'nav-active' : ''}>
                <AltRouteIcon />
                <span>Routes</span>
              </li>
            </Link>
          </ul>
        </nav>
      </main>
    </div>
  );
};

export default Navbar;
