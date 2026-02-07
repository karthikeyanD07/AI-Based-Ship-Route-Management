import React, { useState, useEffect } from 'react';
import Navbar from './Navbar';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import L from 'leaflet';
import axios from 'axios';
import '../Styles/Dashboard.css';
import { API_BASE_URL } from "../../config";
import SP from "../Img/ship.png";

// Custom Ship Icon
const shipIcon = new L.Icon({
  iconUrl: SP,
  iconSize: [30, 30],
  iconAnchor: [15, 15],
  popupAnchor: [0, -15],
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
        setShips(shipData);

        // Calculate Metrics
        const total = shipData.length;
        const totalSpeed = shipData.reduce((acc, ship) => acc + (ship.sog || 0), 0);
        const avg = total > 0 ? (totalSpeed / total).toFixed(1) : 0;
        const underway = shipData.filter(s => s.status.includes('Underway')).length;

        // Simulate Alerts (e.g. speed < 5 knots in open ocean)
        const alerts = shipData.filter(s => s.sog < 5).length;

        setMetrics({
          totalShips: total,
          avgSpeed: avg,
          underwayCount: underway,
          alerts: alerts
        });

      } catch (error) {
        console.error("Failed to fetch dashboard data:", error);
      }
    };

    fetchData();
    const interval = setInterval(fetchData, 10000); // Poll every 10s
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
              <span>🚢 Active Fleet</span>
            </div>
            <div className="metric-value">{metrics.totalShips}</div>
            <div className="metric-sub">Vessels in Range</div>
          </div>

          <div className="metric-card" style={{ borderColor: '#9ece6a' }}>
            <div className="metric-title">
              <span>⚡ Avg Fleet Speed</span>
            </div>
            <div className="metric-value">{metrics.avgSpeed} <span style={{ fontSize: '16px' }}>kts</span></div>
            <div className="metric-sub">Optimal Performance</div>
          </div>

          <div className="metric-card" style={{ borderColor: '#e0af68' }}>
            <div className="metric-title">
              <span>⚓ Underway</span>
            </div>
            <div className="metric-value">{metrics.underwayCount}</div>
            <div className="metric-sub">En Route to Destination</div>
          </div>

          <div className="metric-card" style={{ borderColor: '#f7768e' }}>
            <div className="metric-title">
              <span>⚠️ Risk Alerts</span>
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
