import React, { useState } from "react";
import "../Styles/Navbar.css";
import { Link } from "react-router-dom";
import MenuIcon from "@mui/icons-material/Menu";
import CloseIcon from "@mui/icons-material/Close";
import MapIcon from "@mui/icons-material/Map";
import AltRouteIcon from "@mui/icons-material/AltRoute";
import DashboardIcon from "@mui/icons-material/Dashboard";
import PersonIcon from "@mui/icons-material/Person";
import ThunderstormIcon from "@mui/icons-material/Thunderstorm";
import HomeIcon from "@mui/icons-material/Home";

const Navbar = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [showProfile, setShowProfile] = useState(false);
  const [theme, setTheme] = useState(() => localStorage.getItem('theme') || 'dark');

  const toggleNavbar = () => {
    setIsOpen(!isOpen);
  };

  const handleShowProfile = () => {
    setShowProfile(!showProfile);
  };

  const toggleTheme = () => {
    const next = theme === 'dark' ? 'light' : 'dark';
    setTheme(next);
    localStorage.setItem('theme', next);
    document.documentElement.setAttribute('data-theme', next);
  };

  // ensure attribute on first paint
  if (document.documentElement.getAttribute('data-theme') !== theme) {
    document.documentElement.setAttribute('data-theme', theme);
  }

  return (
    <div>
      <header className="navbar-header">
        <div className="menu-toggle" onClick={toggleNavbar}>
          {isOpen ? <CloseIcon style={{ fontSize: "28px" }} /> : <MenuIcon style={{ fontSize: "28px" }} />}
        </div>
        <div className="navbar-title">
          <h1 style={{ color: "#e6ebf2", fontWeight: 600, letterSpacing: 0.4 }}>NeoECDIS</h1>
        </div>
        <div className="navbar-profile" onClick={handleShowProfile}>
          <PersonIcon style={{ fontSize: "26px" }} />
        </div>
      </header>

      <main className={`navbar-main ${isOpen ? "open" : ""}`}>
        <nav>
          <ul>
            <Link to="/dashboard">
              <li>
                <DashboardIcon />
                <span>Captain’s Dashboard</span>
              </li>
            </Link>
            <Link to="/map">
              <li>
                <MapIcon />
                <span>Smart Navigator</span>
              </li>
            </Link>
            <Link to="/routes">
              <li>
                <AltRouteIcon />
                <span>Routes</span>
              </li>
            </Link>
            <Link to="/weather">
              <li>
                <ThunderstormIcon />
                <span>Sea Conditions</span>
              </li>
            </Link>
          </ul>
        </nav>
      </main>

      <div className="profile-container">
        {showProfile && (
          <div className="profile-card">
            <div className="profile-row"><strong>Signed in</strong> as Captain</div>
            <button className="profile-btn" onClick={toggleTheme}>{theme === 'dark' ? 'Switch to Light' : 'Switch to Dark'}</button>
            <div className="profile-links">
              <Link to="/routes">Plan Route</Link>
              <Link to="/map">Live Map</Link>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Navbar;
