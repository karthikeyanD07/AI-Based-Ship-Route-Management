import React, { useState, useEffect } from 'react';
import Navbar from './Navbar';
import DirectionsBoat from '@mui/icons-material/DirectionsBoat';
import Speed from '@mui/icons-material/Speed';
import Anchor from '@mui/icons-material/Anchor';
import Warning from '@mui/icons-material/Warning';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import L from 'leaflet';
import axios from 'axios';
import '../Styles/Dashboard.css';
import { API_BASE_URL } from "../../config";
// Custom Professional Ship SVG Marker
const shipIcon = L.divIcon({
  className: 'custom-ship-marker',
  html: `
    <div style="background-color: #7aa2f7; width: 28px; height: 28px; border-radius: 50%; display: flex; align-items: center; justify-content: center; box-shadow: 0 0 15px rgba(122, 162, 247, 0.6), inset 0 0 6px rgba(0,0,0,0.5); border: 2px solid #fff; transition: all 0.3s ease;">
      <svg viewBox="0 0 24 24" width="18" height="18" fill="#fff" style="transform: rotate(-45deg);">
        <path d="M20 21c-1.39 0-2.78-.47-4-1.32-2.44 1.71-5.56 1.71-8 0C6.78 20.53 5.39 21 4 21H2v2h2c1.38 0 2.74-.35 4-.99 2.52 1.29 5.48 1.29 8 0 1.26.65 2.62.99 4 .99h2v-2h-2zM3.95 19H4c1.6 0 3.02-.88 4-2 .98 1.12 2.4 2 4 2s3.02-.88 4-2c.98 1.12 2.4 2 4 2h.05l1.89-6.68c.08-.26.06-.54-.06-.78s-.34-.42-.6-.5L20 10.62V6c0-1.1-.9-2-2-2h-3V1H9v3H6c-1.1 0-2 .9-2 2v4.62l-1.29.42c-.26.08-.47.26-.6.5s-.15.52-.06.78L3.95 19zM6 6h12v3.97L12 8 6 9.97V6z"/>
      </svg>
    </div>
  `,
  iconSize: [28, 28],
  iconAnchor: [14, 14],
  popupAnchor: [0, -14],
});

import { useNavigate } from 'react-router-dom';

const Dashboard = () => {
  const navigate = useNavigate();
  const [ships, setShips] = useState([]);
  const [metrics, setMetrics] = useState({
    totalShips: 0,
    avgSpeed: 0,
    underwayCount: 0,
    alerts: 0
  });

  // Action: Bridge to Routes Page
  const handlePlanRoute = async (ship) => {
    try {
      // 1. Find nearest port to ship's current location
      const res = await axios.post(`${API_BASE_URL}/api/ports/nearest`, {
        lat: ship.lat,
        lon: ship.lon
      });
      const nearestPort = res.data.port; // e.g. "Colombo"

      // 2. Navigate with params
      navigate(`/routes?mmsi=${ship.mmsi}&start=${nearestPort}`);

    } catch (err) {
      console.error("Failed to find nearest port", err);
      // Fallback: just send MMSI
      navigate(`/routes?mmsi=${ship.mmsi}`);
    }
  };

  // Fetch Fleet Data
  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await axios.get(`${API_BASE_URL}/api/ship-traffic`);
        const shipData = response.data.ships;
        // Filter out ships with missing/invalid coordinates
        const validShips = (shipData || []).filter(
          s => typeof s.lat === 'number' && typeof s.lon === 'number'
            && isFinite(s.lat) && isFinite(s.lon)
        );
        setShips(validShips);

        // Calculate Metrics
        const total = validShips.length;
        const totalSpeed = validShips.reduce((acc, ship) => acc + (ship.sog || 0), 0);
        const avg = total > 0 ? (totalSpeed / total).toFixed(1) : 0;
        const underway = validShips.filter(s => s.status && s.status.includes('Underway')).length;
        const alerts = validShips.filter(s => s.sog < 5).length;

        setMetrics({ totalShips: total, avgSpeed: avg, underwayCount: underway, alerts });

      } catch (error) {
        console.error("Failed to fetch dashboard data:", error);
      }
    };

    fetchData();
    const interval = setInterval(fetchData, 10000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className='dashboard-body'>
      <Navbar />

      <div className="dashboard-container">
        {/* Header */}
        <header className="dashboard-header">
          <div>
            <h1>Command Center</h1>
            <span className="last-updated">Live Fleet Status • Indian Ocean Sector</span>
          </div>
          <div>
            <span className="status-badge" style={{ fontSize: '12px', padding: '6px 12px' }}>
              System Operational
            </span>
          </div>
        </header>

        {/* Top Metrics Row */}
        <div className="metrics-row">
          <div className="metric-card" style={{ borderColor: '#7aa2f7' }}>
            <div className="metric-title">
              <span><DirectionsBoat sx={{ fontSize: 18, mr: 1, verticalAlign: 'middle', color: '#7aa2f7' }} /> Active Fleet</span>
            </div>
            <div className="metric-value">{metrics.totalShips}</div>
            <div className="metric-sub">Vessels in Range</div>
          </div>

          <div className="metric-card" style={{ borderColor: '#9ece6a' }}>
            <div className="metric-title">
              <span><Speed sx={{ fontSize: 18, mr: 1, verticalAlign: 'middle', color: '#9ece6a' }} /> Avg Fleet Speed</span>
            </div>
            <div className="metric-value">{metrics.avgSpeed} <span style={{ fontSize: '16px' }}>kts</span></div>
            <div className="metric-sub">Optimal Performance</div>
          </div>

          <div className="metric-card" style={{ borderColor: '#e0af68' }}>
            <div className="metric-title">
              <span><Anchor sx={{ fontSize: 18, mr: 1, verticalAlign: 'middle', color: '#e0af68' }} /> Underway</span>
            </div>
            <div className="metric-value">{metrics.underwayCount}</div>
            <div className="metric-sub">En Route to Destination</div>
          </div>

          <div className="metric-card" style={{ borderColor: '#f7768e' }}>
            <div className="metric-title">
              <span><Warning sx={{ fontSize: 18, mr: 1, verticalAlign: 'middle', color: '#f7768e' }} /> Risk Alerts</span>
            </div>
            <div className="metric-value">{metrics.alerts}</div>
            <div className="metric-sub" style={{ color: metrics.alerts > 0 ? '#f7768e' : '#565f89' }}>
              {metrics.alerts > 0 ? 'Attention Required' : 'No Critical Issues'}
            </div>
          </div>
        </div>

        {/* Sidebar: Fleet List */}
        <div className="fleet-panel">
          <div className="panel-header">
            <span>Vessel Manifest</span>
            <span style={{ fontSize: '12px', opacity: 0.7 }}>{metrics.totalShips} Units</span>
          </div>
          <div className="fleet-list">
            {ships.map(ship => (
              <div key={ship.mmsi} className="fleet-item" onClick={() => handlePlanRoute(ship)}>
                <div className="ship-name">{ship.name}</div>
                <div className="ship-meta">
                  <span>MMSI: {ship.mmsi}</span>
                  <span style={{ color: '#7aa2f7' }}>{ship.sog} kts</span>
                </div>
                <div style={{ fontSize: '10px', color: '#565f89', marginTop: '4px' }}>
                  Click to Plan Route →
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Map Panel: Geo-Spatial View */}
        <div className="map-panel">
          <MapContainer
            center={[6.0, 80.0]}
            zoom={4}
            zoomControl={false}
            className="map-content"
            style={{ background: '#1a1b26' }}
          >
            <TileLayer
              url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
            />
            {ships.map(ship => (
              <Marker key={ship.mmsi} position={[ship.lat, ship.lon]} icon={shipIcon}>
                <Popup>
                  <strong>{ship.name}</strong><br />
                  Speed: {ship.sog} kts<br />
                  Status: {ship.status}
                  <button
                    onClick={() => handlePlanRoute(ship)}
                    style={{
                      marginTop: '8px', padding: '4px 8px', background: '#7aa2f7',
                      border: 'none', borderRadius: '4px', cursor: 'pointer', color: '#1a1b26', fontWeight: 'bold'
                    }}
                  >
                    Plan Route
                  </button>
                </Popup>
              </Marker>
            ))}
          </MapContainer>
        </div>

      </div>
    </div>
  );
};

export default Dashboard;
