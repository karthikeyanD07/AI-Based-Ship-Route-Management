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
    alerts: 0,
    fleetCo2: 0
  });
  const [history, setHistory] = useState([]);
  const [planningShip, setPlanningShip] = useState(null); // I1: track which ship is being planned

  // C2 + I1: Bridge to Routes Page — pass nearest port as start AND destination as end
  const handlePlanRoute = async (ship) => {
    setPlanningShip(ship.mmsi); // I1: show loading state on that item
    try {
      const res = await axios.post(`${API_BASE_URL}/api/ports/nearest`, {
        lat: ship.lat,
        lon: ship.lon
      });
      const nearestPort = res.data.port;

      // C2: Pass destination_hint as end port
      const rawMmsi = String(ship.mmsi).replace(/^MMSI-/, '');
      const params = new URLSearchParams({ mmsi: rawMmsi, start: nearestPort });
      if (ship.destination_hint) params.set('end', ship.destination_hint);

      navigate(`/routes?${params.toString()}`);
    } catch (err) {
      console.error("Failed to find nearest port", err);
      const rawMmsi = String(ship.mmsi).replace(/^MMSI-/, '');
      navigate(`/routes?mmsi=${rawMmsi}`);
    } finally {
      setPlanningShip(null);
    }
  };

  // Fetch Fleet Data
  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await axios.get(`${API_BASE_URL}/api/ship-traffic`);
        const shipData = response.data.ships;
        const validShips = (shipData || []).filter(
          s => typeof s.lat === 'number' && typeof s.lon === 'number'
            && isFinite(s.lat) && isFinite(s.lon)
        );
        setShips(validShips);

        const summary = response.data.summary || {};
        const total = validShips.length;
        const totalSpeed = validShips.reduce((acc, ship) => acc + (ship.sog || 0), 0);
        const avg = total > 0 ? (totalSpeed / total).toFixed(1) : 0;
        const underway = validShips.filter(s => s.status && s.status.includes('Underway')).length;
        const alerts = validShips.filter(s => s.sog < 5).length;

        setMetrics({
          totalShips: total,
          avgSpeed: avg,
          underwayCount: underway,
          alerts,
          fleetCo2: summary.estimated_fleet_co2_daily || 0
        });

      } catch (error) {
        console.error("Failed to fetch dashboard data:", error);
      }
    };

    const fetchHistory = async () => {
      try {
        const response = await axios.get(`${API_BASE_URL}/api/routes/history`);
        setHistory(response.data.history || []);
      } catch (err) {
        console.error("History fetch failed", err);
      }
    };

    fetchData();
    fetchHistory();
    const interval = setInterval(() => {
      fetchData();
      fetchHistory();
    }, 10000);
    return () => clearInterval(interval);
  }, []);

  // V2: Real efficiency score calculated from speed (higher speed relative to fleet average = higher score)
  const getEfficiencyScore = (ship) => {
    const avgFleet = parseFloat(metrics.avgSpeed) || 12;
    const ratio = ship.sog / avgFleet;
    // Vessels near avg speed are most efficient (not racing, not crawling)
    const score = Math.max(60, Math.min(99, 100 - Math.abs(ratio - 1) * 40));
    return score.toFixed(1);
  };

  // V3: Dynamic alerts generated from real ship data
  const getDynamicAlerts = () => {
    const alerts = [];
    const slowShips = ships.filter(s => s.sog < 3 && s.status !== 'At Anchor');
    if (slowShips.length > 0) {
      alerts.push({ level: 'critical', icon: '⚠️', title: 'DRIFTING VESSELS', msg: `${slowShips.length} vessel(s) near-stationary in monitored sector.` });
    }
    const fastShips = ships.filter(s => s.sog > 18);
    if (fastShips.length > 0) {
      alerts.push({ level: 'warning', icon: '⚡', title: 'OVER-SPEED ALERT', msg: `${fastShips.length} vessel(s) exceeding 18 kts — elevated fuel burn.` });
    }
    if (ships.length > 20) {
      alerts.push({ level: 'warning', icon: '⚓', title: 'TRAFFIC DENSITY', msg: `${ships.length} vessels active in sector — congestion risk elevated.` });
    }
    // Always have at least one advisory
    if (alerts.length === 0) {
      alerts.push({ level: 'info', icon: '✅', title: 'SECTOR NOMINAL', msg: 'All vessels operating within standard parameters.' });
    }
    return alerts;
  };

  const dynamicAlerts = getDynamicAlerts();

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
            <div className="metric-sub">Vessels in Operations</div>
          </div>

          <div className="metric-card" style={{ borderColor: '#9ece6a' }}>
            <div className="metric-title">
              <span><Speed sx={{ fontSize: 18, mr: 1, verticalAlign: 'middle', color: '#9ece6a' }} /> Global Fleet CO₂</span>
            </div>
            <div className="metric-value">{metrics.fleetCo2.toLocaleString()} <span style={{ fontSize: '14px' }}>t/day</span></div>
            <div className="metric-sub">Integrated Fleet Footprint</div>
          </div>

          <div className="metric-card" style={{ borderColor: '#e0af68' }}>
            <div className="metric-title">
              <span><Anchor sx={{ fontSize: 18, mr: 1, verticalAlign: 'middle', color: '#e0af68' }} /> Average Speed</span>
            </div>
            <div className="metric-value">{metrics.avgSpeed} <span style={{ fontSize: '14px' }}>kts</span></div>
            <div className="metric-sub">Sustainable Cruising SOG</div>
          </div>

          <div className="metric-card" style={{ borderColor: '#f7768e' }}>
            <div className="metric-title">
              <span><Warning sx={{ fontSize: 18, mr: 1, verticalAlign: 'middle', color: '#f7768e' }} /> Risk Alerts</span>
            </div>
            <div className="metric-value">{metrics.alerts}</div>
            <div className="metric-sub" style={{ color: metrics.alerts > 0 ? '#f7768e' : '#565f89' }}>
              {metrics.alerts > 0 ? 'Protocol Violation' : 'Nominal Safety Status'}
            </div>
          </div>
        </div>

        {/* Sidebar: Intelligence Panels */}
        <div className="fleet-panel">
          <div className="panel-header">
             <span>Voyage History</span>
             <span style={{ fontSize: '11px', color: '#7aa2f7' }}>{history.length} Logs</span>
          </div>
          <div className="fleet-list history-list">
             {history.length === 0 ? (
               <div style={{ padding: '16px', fontSize: '12px', color: '#565f89', textAlign: 'center' }}>
                 No recent optimizations recorded.
               </div>
             ) : (
                history.map((entry, idx) => (
                  <div
                    key={idx}
                    className="fleet-item history-item"
                    title="Click to re-run this voyage"
                    onClick={() => navigate(`/routes?mmsi=${entry.ship_id}&start=${entry.start_port}&end=${entry.end_port}`)}
                    style={{ cursor: 'pointer' }}
                  >
                     <div className="ship-name" style={{ fontSize: '13px' }}>{entry.start_port} → {entry.end_port}</div>
                     <div className="ship-meta">
                        <span style={{ color: '#4ECDC4', fontWeight: 'bold' }}>{entry.savings_percent}% Save</span>
                        <span style={{ fontSize: '10px', color: '#7aa2f7' }}>↺ Re-run</span>
                        <span style={{ fontSize: '10px' }}>{new Date(entry.timestamp).toLocaleDateString()}</span>
                     </div>
                  </div>
                ))
             )}
          </div>

          <div className="panel-header" style={{ marginTop: '24px' }}>
            <span>Fleet Efficiency Leaderboard</span>
            <span style={{ fontSize: '11px', color: '#9ece6a' }}>Top 5 Vessels</span>
          </div>
          <div className="fleet-list leaderboard-list">
             {/* V2: Sort by real efficiency score */}
             {(ships || [])
               .map(ship => ({ ...ship, effScore: parseFloat(getEfficiencyScore(ship)) }))
               .sort((a, b) => b.effScore - a.effScore)
               .slice(0, 5)
               .map((ship, idx) => (
               <div key={ship.mmsi} className="fleet-item" style={{ borderLeft: `3px solid ${idx === 0 ? '#9ece6a' : idx === 1 ? '#7aa2f7' : '#565f89'}` }}>
                  <div className="ship-name" style={{ fontSize: '13px' }}>
                     <span style={{ color: '#9ece6a', marginRight: '8px' }}>#{idx+1}</span>
                     {ship.name}
                  </div>
                  <div className="ship-meta">
                     <span style={{ color: '#9ece6a' }}>{ship.effScore}% Efficiency Score</span>
                     <span style={{ color: '#565f89', fontSize: '11px' }}>{ship.sog} kts</span>
                  </div>
               </div>
             ))}
          </div>

          {/* V3: Dynamic alerts from real data */}
          <div className="panel-header" style={{ marginTop: '24px' }}>
            <span>Mission Control: Alerts</span>
            <span style={{ fontSize: '11px', color: '#f7768e' }}>Real-time Feed</span>
          </div>
          <div className="fleet-list alerts-feed" style={{ maxHeight: '180px' }}>
             {dynamicAlerts.map((alert, idx) => (
               <div key={idx} className={`fleet-item alert-item ${alert.level}`}>
                  <div className="ship-name" style={{ color: alert.level === 'critical' ? '#f7768e' : '#e0af68', fontSize: '11px' }}>
                    {alert.icon} {alert.title}
                  </div>
                  <div style={{ fontSize: '12px', color: '#F8FAFC' }}>{alert.msg}</div>
               </div>
             ))}
          </div>

          <div className="panel-header" style={{ marginTop: '24px' }}>
            <span>Live Vessel Feed</span>
            <span style={{ fontSize: '11px', opacity: 0.7 }}>{metrics.totalShips} Units</span>
          </div>
          <div className="fleet-list">
            {ships.map(ship => (
              <div
                key={ship.mmsi}
                className="fleet-item"
                onClick={() => !planningShip && handlePlanRoute(ship)}
                style={{ cursor: planningShip === ship.mmsi ? 'wait' : 'pointer', opacity: planningShip && planningShip !== ship.mmsi ? 0.6 : 1 }}
              >
                <div className="ship-name">{ship.name}</div>
                <div className="ship-meta">
                  <span>MMSI: {ship.mmsi}</span>
                  {/* I1: Loading indicator per ship */}
                  {planningShip === ship.mmsi
                    ? <span style={{ color: '#e0af68', fontSize: '11px' }}>⏳ Planning...</span>
                    : <span style={{ color: '#7aa2f7' }}>{ship.sog} kts</span>
                  }
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
                  Status: {ship.status}<br />
                  Dest: {ship.destination_hint || 'N/A'}
                  <button
                    onClick={() => handlePlanRoute(ship)}
                    style={{
                      marginTop: '8px', padding: '4px 8px', background: '#7aa2f7',
                      border: 'none', borderRadius: '4px', cursor: 'pointer', color: '#1a1b26',
                      fontWeight: 'bold', display: 'block', width: '100%'
                    }}
                  >
                    {planningShip === ship.mmsi ? '⏳ Planning...' : 'Plan Route'}
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
