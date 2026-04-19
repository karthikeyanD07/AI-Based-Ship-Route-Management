import React, { useState, useEffect } from "react";
import Navbar from "./Navbar";
import { MapContainer, TileLayer, Polyline, Marker, Popup } from "react-leaflet";
import Autocomplete from "@mui/material/Autocomplete";
import TextField from "@mui/material/TextField";
import axios from "axios";
import L from "leaflet";
import DirectionsBoat from "@mui/icons-material/DirectionsBoat";
import AccessTime from "@mui/icons-material/AccessTime";
import Opacity from "@mui/icons-material/Opacity";
import Public from "@mui/icons-material/Public";
import MapIcon from "@mui/icons-material/Map";
import WaterDrop from "@mui/icons-material/WaterDrop";
import NatureIcon from "@mui/icons-material/Nature";
import MonetizationOnIcon from "@mui/icons-material/MonetizationOn";
import SettingsIcon from "@mui/icons-material/Settings";
import Air from "@mui/icons-material/Air";
import Waves from "@mui/icons-material/Waves";
import "../Styles/Routes.css";
import { API_BASE_URL } from "../../config";

// Ship Marker Component for Animation
const ShipMarker = ({ routePositions, color }) => {
  const [position, setPosition] = useState(null);
  const [index, setIndex] = useState(0);

  useEffect(() => {
    // COMMANDER SAFETY PATCH: Ensure routePositions is a valid array of points
    if (!Array.isArray(routePositions) || routePositions.length === 0) {
      setPosition(null);
      return;
    }

    setPosition(routePositions[0]);
    setIndex(0);

    const interval = setInterval(() => {
      setIndex(prev => (prev + 1 >= routePositions.length ? 0 : prev + 1));
    }, 250);

    return () => clearInterval(interval);
  }, [routePositions]);

  useEffect(() => {
    if (routePositions && routePositions[index]) {
      const pos = routePositions[index];
      // Final Leaflet safeguard
      if (Array.isArray(pos) && typeof pos[0] === 'number' && typeof pos[1] === 'number') {
        setPosition(pos);
      }
    }
  }, [index, routePositions]);

  if (!position) return null;

  return (
    <Marker
      position={position}
      icon={L.divIcon({
        className: 'custom-ship-marker',
        html: `
          <div style="background-color: ${color}; width: 28px; height: 28px; border-radius: 50%; display: flex; align-items: center; justify-content: center; box-shadow: 0 0 15px ${color}99, inset 0 0 6px rgba(0,0,0,0.5); border: 2px solid #fff; transition: all 0.3s ease;">
            <svg viewBox="0 0 24 24" width="18" height="18" fill="#fff" style="transform: rotate(-45deg);">
              <path d="M20 21c-1.39 0-2.78-.47-4-1.32-2.44 1.71-5.56 1.71-8 0C6.78 20.53 5.39 21 4 21H2v2h2c1.38 0 2.74-.35 4-.99 2.52 1.29 5.48 1.29 8 0 1.26.65 2.62.99 4 .99h2v-2h-2zM3.95 19H4c1.6 0 3.02-.88 4-2 .98 1.12 2.4 2 4 2s3.02-.88 4-2c.98 1.12 2.4 2 4 2h.05l1.89-6.68c.08-.26.06-.54-.06-.78s-.34-.42-.6-.5L20 10.62V6c0-1.1-.9-2-2-2h-3V1H9v3H6c-1.1 0-2 .9-2 2v4.62l-1.29.42c-.26.08-.47.26-.6.5s-.15.52-.06.78L3.95 19zM6 6h12v3.97L12 8 6 9.97V6z"/>
            </svg>
          </div>
        `,
        iconSize: [28, 28],
        iconAnchor: [14, 14],
        popupAnchor: [0, -14]
      })}
    >
      <Popup>Simulated Vessel Position</Popup>
    </Marker>
  );
};

const RoutesOptimization = () => {
  // Form State — default MMSI is empty until URL param sets it
  const [mmsi, setMmsi] = useState("");
  const [ports, setPorts] = useState([]);
  const [startPort, setStartPort] = useState("");
  const [endPort, setEndPort] = useState("");
  const [startSearch, setStartSearch] = useState("");
  const [endSearch, setEndSearch] = useState("");

  // Vessel Configuration
  const [vesselType, setVesselType] = useState("container");
  const [vesselSize, setVesselSize] = useState("medium");
  const [fuelType, setFuelType] = useState("HFO");

  // Views
  const [activeView, setActiveView] = useState("comparison");

  // Data
  const [comparisonData, setComparisonData] = useState(null);
  const [emissionsData, setEmissionsData] = useState(null);
  const [weatherData, setWeatherData] = useState(null);

  // UI State
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Load ports on mount
  useEffect(() => {
    fetchPorts();
  }, []);

  // Clear data when inputs change to prevent stale/static readings
  useEffect(() => {
    setComparisonData(null);
    setEmissionsData(null);
    setWeatherData(null);
  }, [startPort, endPort]);



  const fetchPorts = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/ports/all`);
      setPorts(response.data.ports);

      // C1/C4: Enhanced param handling — strip MMSI- prefix, only use defaults if no URL param given
      const params = new URLSearchParams(window.location.search);
      const paramMmsi = params.get('mmsi');
      const paramStart = params.get('start');
      const paramEnd = params.get('end');
      const paramType = params.get('type');
      const paramSize = params.get('size');

      if (response.data.ports.length > 0) {
        // C4: Strip MMSI- prefix (Navigator sends 'MMSI-412000000', we need '412000000')
        if (paramMmsi) {
          const cleanMmsi = paramMmsi.replace(/^MMSI-/i, '').slice(0, 9);
          setMmsi(cleanMmsi);
        } else if (!mmsi) {
          setMmsi("235123456"); // Default only if nothing came from URL
        }
        if (paramType) setVesselType(paramType);
        if (paramSize) setVesselSize(paramSize);

        // C1: Smart Port Matching — only use fallback default if NO param was given
        const resolvePort = (p) => {
          if (!p) return null;
          return response.data.ports.find(port => port.toLowerCase() === p.toLowerCase()) || null;
        };

        const finalStart = resolvePort(paramStart) ?? (paramStart ? null : "Singapore");
        const finalEnd = resolvePort(paramEnd) ?? (paramEnd ? null : "Rotterdam");

        if (finalStart) { setStartPort(finalStart); setStartSearch(finalStart); }
        if (finalEnd) { setEndPort(finalEnd); setEndSearch(finalEnd); }
      }
    } catch (err) {
      console.error("Failed to load ports:", err);
      setError("Failed to load ports");
    }
  };

  const validateMMSI = (value) => {
    return /^\d{9}$/.test(value);
  };

  const compareRoutes = async () => {
    if (!startPort || !endPort) {
      setError("Please select both departure and arrival ports");
      return;
    }

    if (!validateMMSI(mmsi)) {
      setError("MMSI must be exactly 9 digits");
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await axios.post(`${API_BASE_URL}/api/route/compare`, {
        ship_id: `MMSI-${mmsi}`,
        start_port: startPort,
        end_port: endPort,
        vessel_type: vesselType,
        vessel_size: vesselSize,
        fuel_type: fuelType
      });

      // DATA INTEGRITY PATCH: Ensure geometry is valid for Leaflet
      const sanitizedData = {
        ...response.data,
        routes: response.data.routes.map(r => ({
          ...r,
          route_points: (r.route_points || []).filter(p => 
            Array.isArray(p) && p.length >= 2 && 
            typeof p[0] === 'number' && typeof p[1] === 'number'
          )
        }))
      };

      setComparisonData(sanitizedData);
      setActiveView("comparison");

      // PERSISTENCE PATCH: Log optimization event for Dashboard history
      const optimalRoute = response.data.routes?.find(r => r.route_name === "balanced");
      if (optimalRoute) {
        try {
          await axios.post(`${API_BASE_URL}/api/routes/history`, {
            ship_id: `MMSI-${mmsi}`,
            start_port: startPort,
            end_port: endPort,
            savings_percent: optimalRoute.co2_savings_percent,
            best_route_type: "balanced"
          });
        } catch (hErr) {
          console.warn("History log skipped:", hErr);
        }
      }
    } catch (err) {
      console.error("Route comparison failed:", err);
      setError(err.response?.data?.detail || "Failed to compare routes");
    } finally {
      setLoading(false);
    }
  };

  const calculateEmissions = async () => {
    if (!comparisonData) {
      setError("Please compare routes first");
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const balancedRoute = comparisonData.routes.find(r => r.route_name === "balanced");
      const response = await axios.post(`${API_BASE_URL}/api/route/emissions`, {
        distance_km: balancedRoute.distance_km,
        speed_knots: balancedRoute.speed_knots,
        vessel_type: vesselType,
        vessel_size: vesselSize,
        fuel_type: fuelType
      });

      setEmissionsData(response.data);
      setActiveView("emissions");
    } catch (err) {
      console.error("Emissions calculation failed:", err);
      setError(err.response?.data?.detail || "Failed to calculate emissions");
    } finally {
      setLoading(false);
    }
  };

  const getWeatherRoute = async () => {
    if (!startPort || !endPort) {
      setError("Please select both departure and arrival ports");
      return;
    }

    setLoading(true);
    setError(null);

    try {
      // Clear previous data to avoid showing static/stale info
      setWeatherData(null);

      const response = await axios.post(`${API_BASE_URL}/api/route/weather-optimized`, {
        ship_id: `MMSI-${mmsi}`,
        start: startPort,
        end: endPort
      });

      // DATA INTEGRITY PATCH: Sanitize weather route points and segments
      const sanitizedWeather = {
        ...response.data,
        route_points: (response.data.route_points || []).filter(p => 
          Array.isArray(p) && p.length >= 2 && 
          typeof p[0] === 'number' && typeof p[1] === 'number'
        ),
        segments: (response.data.segments || []).filter(s => 
          typeof s.latitude === 'number' && typeof s.longitude === 'number'
        )
      };

      setWeatherData(sanitizedWeather);
      setActiveView("weather");
    } catch (err) {
      console.error("Weather routing failed:", err);
      setError(err.response?.data?.detail || "Failed to get weather route");
    } finally {
      setLoading(false);
    }
  };

  const getWindArrow = (direction) => {
    return `rotate(${direction}deg)`;
  };

  const getDangerColor = (level) => {
    if (level >= 1.0) return "#F43F5E"; // Extreme
    if (level >= 0.7) return "#FACC15"; // Rough
    if (level >= 0.4) return "#38BDF8"; // Moderate
    return "#34D399"; // Calm
  };

  return (
    <div className="app-container routes-page">
      {/* V4: Use shared Navbar instead of standalone header */}
      <Navbar />

      <div className="main-layout">
        {/* Sidebar */}
        <aside className="sidebar">
          <div className="form-group">
            <label>MMSI Number</label>
            <input
              type="text"
              value={mmsi}
              onChange={(e) => setMmsi(e.target.value.replace(/\D/g, '').slice(0, 9))}
              placeholder="e.g., 235123456"
              maxLength="9"
            />
            <span className="helper-text">9-digit Maritime Mobile Service Identity</span>
          </div>

          <div className="form-group">
            <label>Departure Port</label>
            <Autocomplete
              options={ports}
              value={startPort || null}
              onChange={(event, newValue) => {
                setStartPort(newValue || "");
                setStartSearch(newValue || "");
              }}
              inputValue={startSearch}
              onInputChange={(event, newInputValue) => {
                setStartSearch(newInputValue);
              }}
              renderInput={(params) => (
                <TextField
                  {...params}
                  placeholder="Search Departure Port"
                  variant="outlined"
                  size="small"
                  sx={{
                    '& .MuiOutlinedInput-root': {
                      backgroundColor: 'rgba(255, 255, 255, 0.05)',
                      color: '#a9b1d6',
                      '& fieldset': { borderColor: '#414868' },
                      '&:hover fieldset': { borderColor: '#7aa2f7' },
                      '&.Mui-focused fieldset': { borderColor: '#7aa2f7' },
                    },
                    '& .MuiInputBase-input': { color: '#c0caf5' },
                    '& .MuiSvgIcon-root': { color: '#565f89' }
                  }}
                />
              )}
            />
          </div>

          <div className="form-group">
            <label>Arrival Port</label>
            <Autocomplete
              options={ports}
              value={endPort || null}
              onChange={(event, newValue) => {
                setEndPort(newValue || "");
                setEndSearch(newValue || "");
              }}
              inputValue={endSearch}
              onInputChange={(event, newInputValue) => {
                setEndSearch(newInputValue);
              }}
              renderInput={(params) => (
                <TextField
                  {...params}
                  placeholder="Search Arrival Port"
                  variant="outlined"
                  size="small"
                  sx={{
                    '& .MuiOutlinedInput-root': {
                      backgroundColor: 'rgba(255, 255, 255, 0.05)',
                      color: '#a9b1d6',
                      '& fieldset': { borderColor: '#414868' },
                      '&:hover fieldset': { borderColor: '#7aa2f7' },
                      '&.Mui-focused fieldset': { borderColor: '#7aa2f7' },
                    },
                    '& .MuiInputBase-input': { color: '#c0caf5' },
                    '& .MuiSvgIcon-root': { color: '#565f89' }
                  }}
                />
              )}
            />
          </div>

          <details className="advanced-settings">
            <summary><SettingsIcon sx={{ fontSize: 18, verticalAlign: 'middle', mr: 1, color: 'var(--tn-blue)' }} /> Configuration</summary>

            <div className="form-group">
              <label>Vessel Type</label>
              <select value={vesselType} onChange={(e) => setVesselType(e.target.value)}>
                <option value="container">Container Ship</option>
                <option value="tanker">Oil Tanker</option>
                <option value="bulk">Bulk Carrier</option>
              </select>
            </div>

            <div className="form-group">
              <label>Vessel Size</label>
              <select value={vesselSize} onChange={(e) => setVesselSize(e.target.value)}>
                <option value="small">Small (&lt;5000 TEU)</option>
                <option value="medium">Medium (5000-10000 TEU)</option>
                <option value="large">Large (&gt;10000 TEU)</option>
              </select>
            </div>

            <div className="form-group">
              <label>Fuel Type</label>
              <select value={fuelType} onChange={(e) => setFuelType(e.target.value)}>
                <option value="HFO">Heavy Fuel Oil (HFO)</option>
                <option value="MGO">Marine Gas Oil (MGO)</option>
                <option value="LNG">Liquefied Natural Gas (LNG)</option>
              </select>
            </div>
          </details>

          {/* I5: Buttons with visible loading spinner */}
          <button
            className="btn btn-primary"
            onClick={compareRoutes}
            disabled={loading || !startPort || !endPort}
            style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px' }}
          >
            {loading && activeView === 'comparison'
              ? <><span className="btn-spinner" />Analyzing...</>
              : '⚓ Compare Routes'
            }
          </button>

          <button
            className="btn btn-secondary"
            onClick={getWeatherRoute}
            disabled={loading || !startPort || !endPort}
            style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px' }}
          >
            {loading && activeView === 'weather'
              ? <><span className="btn-spinner" />Loading...</>
              : '⛈️ Weather Routing'
            }
          </button>
        </aside>

        {/* Main Content */}
        <main className="content">
          {error && <div className="error"><SettingsIcon sx={{ fontSize: 18, mr: 1 }} /> {error}</div>}

          {/* Tabs */}
          <nav className="tabs">
            <button
              className={`tab-btn ${activeView === 'comparison' ? 'active' : ''}`}
              onClick={() => setActiveView('comparison')}
            >
              Route Comparison
            </button>
            {/* C3: Only re-fetch emissions if data doesn't exist yet */}
            <button
              className={`tab-btn ${activeView === 'emissions' ? 'active' : ''}`}
              onClick={() => {
                if (emissionsData) {
                  setActiveView('emissions');
                } else if (comparisonData) {
                  calculateEmissions();
                } else {
                  setError('Compare routes first');
                }
              }}
            >
              📊 Emissions
            </button>
            <button
              className={`tab-btn ${activeView === 'weather' ? 'active' : ''}`}
              onClick={() => {
                if (weatherData) {
                  setActiveView('weather');
                } else if (startPort && endPort) {
                  getWeatherRoute();
                } else {
                  setError('Select ports to view weather routing');
                }
              }}
            >
              Weather Routing
            </button>
          </nav>

          {activeView === "weather" && weatherData && (
            <div className="weather-stats-panel" style={{ background: 'rgba(31, 35, 53, 0.6)', padding: '16px', borderRadius: '12px', border: '1px solid rgba(122, 162, 247, 0.2)', marginBottom: '20px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '12px' }}>
                  <span style={{ fontSize: '13px', color: 'var(--tn-text-muted)' }}>Speed Efficiency Gauge</span>
                  <span style={{ fontWeight: 'bold', color: '#7aa2f7' }}>{weatherData.weather_impact?.speed_efficiency}%</span>
                </div>
                <div className="efficiency-bar-container" style={{ height: '8px', background: 'rgba(255,255,255,0.1)', borderRadius: '4px', overflow: 'hidden' }}>
                  <div style={{ width: `${weatherData.weather_impact?.speed_efficiency}%`, height: '100%', background: 'linear-gradient(90deg, #7aa2f7, #bb9af7)', transition: 'width 1s ease-out' }}></div>
                </div>
                <div style={{ marginTop: '12px', fontSize: '11px', color: '#94A3B8', textAlign: 'center' }}>
                  Tactical analysis based on {weatherData.segments?.length} voyage segments
                </div>
            </div>
          )}

          {/* Route Comparison View */}
          {activeView === 'comparison' && (
            <>
              {comparisonData ? (
                <>
                  {/* Stats Bar */}
                  <div className="stats-bar">
                    <div className="stat">
                      <span className="stat-label">Routes Analyzed</span>
                      <span className="stat-value">3</span>
                    </div>
                    <div className="stat">
                      <span className="stat-label">Best CO₂ Savings</span>
                      <span className="stat-value">
                        {Math.max(...comparisonData.routes.map(r => r.co2_savings_percent))}%
                      </span>
                    </div>
                    <div className="stat">
                      <span className="stat-label">Vessel Type</span>
                      <span className="stat-value">{vesselType}</span>
                    </div>
                  </div>

                  <div className="route-cards">
                    {comparisonData.routes.map(route => (
                      <div key={route.route_name} className={`route-card ${route.route_name}`}>
                        <div className="card-header">
                          {/* V5: Explicit color per route name so it's not illegible */}
                          <h3 style={{
                            color: route.route_name === 'fastest' ? 'var(--route-fastest)'
                              : route.route_name === 'balanced' ? 'var(--route-balanced)'
                              : 'var(--route-greenest)'
                          }}>{route.route_name.toUpperCase()}</h3>
                          <div className="speed-badge">{route.speed_knots} knots</div>
                        </div>

                        <div className="metrics-grid">
                          <div className="metric">
                            <div className="metric-icon"><MapIcon sx={{ color: 'var(--tn-blue)' }} /></div>
                            <div className="metric-data">
                              <span className="metric-value">{route.distance_km.toLocaleString()}</span>
                              <span className="metric-unit">km</span>
                            </div>
                          </div>

                          <div className="metric">
                            <div className="metric-icon"><AccessTime sx={{ color: 'var(--tn-purple)' }} /></div>
                            <div className="metric-data">
                              <span className="metric-value">{route.estimated_time_days}</span>
                              <span className="metric-unit">days</span>
                            </div>
                          </div>

                          <div className="metric">
                            <div className="metric-icon"><Public sx={{ color: 'var(--tn-green)' }} /></div>
                            <div className="metric-data">
                              <span className="metric-value">{route.total_co2_tonnes}</span>
                              <span className="metric-icon"><NatureIcon fontSize="small" /></span>
                            </div>
                          </div>

                          <div className="metric">
                            <div className="metric-icon"><Opacity sx={{ color: 'var(--tn-yellow)' }} /></div>
                            <div className="metric-data">
                              <span className="metric-value">{route.fuel_tonnes}</span>
                              <span className="metric-icon"><MonetizationOnIcon fontSize="small" /></span>
                            </div>
                          </div>
                        </div>

                        {route.co2_savings_tonnes > 0 && (
                          <div className="savings-badge">
                            <NatureIcon sx={{ fontSize: 16, mr: 0.5, verticalAlign: 'text-bottom' }} /> 
                            <strong>{route.co2_savings_percent}% Efficiency Gain</strong> vs baseline
                          </div>
                        )}
                        
                        <div style={{ marginTop: '20px', borderTop: '1px solid rgba(255,255,255,0.05)', paddingTop: '16px' }}>
                           <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                              <span style={{ fontSize: '11px', color: 'var(--tn-text-muted)' }}>CII Rating Potential</span>
                              <span className={`cii-badge cii-${route.cii_rating}`} style={{ width: '22px', height: '22px', fontSize: '12px' }}>{route.cii_rating}</span>
                           </div>
                            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                               <span style={{ fontSize: '11px', color: 'var(--tn-text-muted)' }}>Estimated Fuel Cost</span>
                               <span className="cost-value" style={{ fontSize: '13px' }}>${route.estimated_cost_usd?.toLocaleString()}</span>
                            </div>
                         </div>
                         
                         {route.weather_summary && (
                            <div style={{ marginTop: '16px', display: 'flex', gap: '12px', background: 'rgba(255,255,255,0.03)', padding: '8px', borderRadius: '6px' }}>
                               <div style={{ flex: 1, textAlign: 'center' }}>
                                  <div style={{ fontSize: '10px', color: 'var(--tn-text-muted)', textTransform: 'uppercase' }}>
                                    <Air sx={{ fontSize: 14, mr: 0.5, verticalAlign: 'middle' }} /> Wind
                                  </div>
                                  <div style={{ fontSize: '13px', fontWeight: 'bold' }}>{route.weather_summary.avg_wind_kts} kts</div>
                               </div>
                               <div style={{ width: '1px', background: 'rgba(255,255,255,0.1)' }}></div>
                               <div style={{ flex: 1, textAlign: 'center' }}>
                                  <div style={{ fontSize: '10px', color: 'var(--tn-text-muted)', textTransform: 'uppercase' }}>
                                    <Waves sx={{ fontSize: 14, mr: 0.5, verticalAlign: 'middle' }} /> Waves
                                  </div>
                                  <div style={{ fontSize: '13px', fontWeight: 'bold' }}>{route.weather_summary.avg_wave_m} m</div>
                               </div>
                            </div>
                         )}
                      </div>
                    ))}
                  </div>

                  <div className="recommendation" style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                    <div style={{ display: 'flex', alignItems: 'center' }}>
                       <DirectionsBoat sx={{ mr: 1.5, fontSize: 24 }} /> 
                       <span>{comparisonData.recommendation}</span>
                    </div>
                    <div style={{ background: 'rgba(255,255,255,0.2)', padding: '4px 12px', borderRadius: '20px', fontSize: '12px', fontWeight: 'bold' }}>
                       OPTIMIZED RECAP
                    </div>
                  </div>

                  <div className="map-container">
                    <MapContainer
                      center={[20, 0]}
                      zoom={2}
                      style={{ height: "100%", width: "100%" }}
                      scrollWheelZoom={true}
                    >
                      <TileLayer
                        url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
                        attribution='&copy; CARTO'
                      />
                      {comparisonData.routes.map(route => (
                        <Polyline
                          key={route.route_name}
                          positions={route.route_points}
                          color={route.color}
                          weight={4}
                          opacity={0.8}
                          lineCap="round"
                          lineJoin="round"
                          className="animated-route-line"
                        />
                      ))}

                      {/* Animate the Balanced Route (usually recommended) */}
                      {comparisonData.routes[1] && (
                        <ShipMarker
                          routePositions={comparisonData.routes[1].route_points}
                          color={comparisonData.routes[1].color}
                        />
                      )}
                    </MapContainer>
                  </div>
                </>
              ) : (
                <div className="empty-state">
                  <h3><MapIcon sx={{ fontSize: 24, mr: 1, verticalAlign: 'middle', color: 'var(--tn-text-muted)' }} /> No routes to display</h3>
                  <p>Select departure and arrival ports, then click "Compare Routes"</p>
                </div>
              )}
            </>
          )}

          {/* Emissions View */}
          {activeView === 'emissions' && (
            <>
              {emissionsData ? (
                <>
                  <div className="emissions-grid">
                    <div className="metric-card primary">
                      <h4>Total CO₂ Emissions</h4>
                      <span className="value">{emissionsData.total_co2_tonnes}</span>
                      <span className="unit">tonnes</span>
                    </div>

                    <div className="metric-card">
                      <h4>Fuel Consumed</h4>
                      <span className="value">{emissionsData.fuel_consumed_tonnes}</span>
                      <span className="unit">tonnes {emissionsData.fuel_type}</span>
                    </div>

                    <div className="metric-card">
                      <h4>Voyage Duration</h4>
                      <span className="value">{emissionsData.voyage_days}</span>
                      <span className="unit">days</span>
                    </div>

                    <div className="metric-card">
                      <h4>CO₂ per Kilometer</h4>
                      <span className="value">{emissionsData.co2_per_km}</span>
                      <span className="unit">tonnes/km</span>
                    </div>

                    <div className="metric-card">
                      <h4>Emission Factor</h4>
                      <span className="value">{emissionsData.emission_factor}</span>
                      <span className="unit">tCO₂/tFuel</span>
                    </div>

                    <div className="metric-card">
                      <h4>Vessel Type</h4>
                      <span className="value">{emissionsData.vessel_type}</span>
                    </div>

                    <div className="metric-card">
                      <h4>Vessel Size</h4>
                      <span className="value">{emissionsData.vessel_size}</span>
                    </div>

                    <div className="metric-card" style={{ borderColor: 'var(--tn-green)', background: 'rgba(158, 206, 106, 0.05)' }}>
                      <h4>CII Rating</h4>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                        <span className={`cii-badge cii-${emissionsData.cii_rating}`}>
                          {emissionsData.cii_rating}
                        </span>
                        <span className="unit" style={{ fontSize: '16px' }}>
                          {emissionsData.cii_score} gCO₂/dwt-nm
                        </span>
                      </div>
                    </div>

                    <div className="metric-card" style={{ borderColor: 'var(--tn-yellow)', background: 'rgba(224, 175, 104, 0.05)' }}>
                      <h4>Est. Fuel Cost</h4>
                      <span className="value cost-value">${emissionsData.estimated_cost_usd?.toLocaleString()}</span>
                      <span className="unit">USD</span>
                    </div>
                  </div>
                </>
              ) : (
                <div className="empty-state">
                  <h3><Public sx={{ fontSize: 24, mr: 1, verticalAlign: 'middle', color: 'var(--tn-text-muted)' }} /> No emissions data</h3>
                  <p>Compare routes first, then click "Emissions" tab</p>
                </div>
              )}
            </>
          )}

          {/* Weather Routing View */}
          {activeView === 'weather' && (
            <>
              {weatherData ? (
                <>
                  <div className="stats-bar">
                    <div className="stat">
                      <span className="stat-label">Speed Efficiency</span>
                      <span className="stat-value">{weatherData.weather_impact.speed_efficiency}%</span>
                    </div>

                    <div className="stat">
                      <span className="stat-label">Time Difference</span>
                      <span className="stat-value">{weatherData.weather_impact.time_difference_vs_simple}h</span>
                    </div>

                    <div className="stat">
                      <span className="stat-label">Total Distance</span>
                      <span className="stat-value">{weatherData.total_distance_km.toLocaleString()} km</span>
                    </div>
                  </div>

                  <h3 style={{ color: 'var(--tn-text)', margin: '32px 0 16px', display: 'flex', alignItems: 'center' }}>
                    <WaterDrop sx={{ mr: 1, color: 'var(--tn-cyan)' }} /> Weather Segments
                  </h3>
                  <div className="weather-segments">
                    {weatherData.segments.map(segment => (
                      <div key={segment.segment} className="segment-card">
                        <div className="segment-number">#{segment.segment}</div>

                        <div className="segment-details">
                          <div className="segment-info">
                            <div className="label">Distance</div>
                            <div className="value">{segment.distance_km} km</div>
                          </div>

                          <div className="segment-info">
                            <div className="label">Position</div>
                            <div className="value">{segment.latitude}°, {segment.longitude}°</div>
                          </div>

                          <div className="segment-info">
                            <div className="label">Speed</div>
                            <div className="value">{segment.adjusted_speed} kts</div>
                          </div>

                          <div className="segment-info">
                            <div className="label">Wind</div>
                            <div className="value">
                              <span className="wind-arrow" style={{ transform: getWindArrow(segment.weather.wind_direction) }}>
                                ↑
                              </span>
                              {' '}{segment.weather.wind_speed} kts
                            </div>
                          </div>

                          <div className="segment-info">
                            <div className="label">Waves</div>
                            <div className="value">{segment.weather.wave_height} m</div>
                          </div>

                          <div className="segment-info">
                            <div className="label">Temperature</div>
                            <div className="value">{segment.weather.temperature}°C</div>
                          </div>

                          <div className="segment-info">
                            <div className="label">Conditions</div>
                            <div className="value">
                              <span className={`conditions-badge ${segment.weather.conditions}`}>
                                {segment.weather.conditions}
                              </span>
                            </div>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>

                  <div className="map-container" style={{ marginTop: '32px' }}>
                    <MapContainer
                      center={[20, 0]}
                      zoom={2}
                      style={{ height: "100%", width: "100%" }}
                      scrollWheelZoom={true}
                    >
                      <TileLayer
                        url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
                        attribution='&copy; CARTO'
                      />
                      {weatherData.segments.map((seg, idx) => {
                        const chunk = Math.ceil(weatherData.route_points.length / weatherData.segments.length);
                        const segmentPoints = weatherData.route_points.slice(idx * chunk, (idx + 1) * chunk + 1);
                        
                        return (
                          <React.Fragment key={idx}>
                            <Polyline
                              positions={segmentPoints}
                              color={getDangerColor(seg.danger_level)}
                              weight={6}
                              opacity={0.9}
                              className="weather-segment-line"
                            />
                            
                            <Marker 
                              position={[seg.latitude, seg.longitude]} 
                              icon={L.divIcon({
                                className: 'tactical-weather-icon',
                                html: `
                                  <div class="tactical-marker-inner" style="background: rgba(15, 23, 42, 0.85); border: 1.5px solid ${getDangerColor(seg.danger_level)}; border-radius: 50%; width: 44px; height: 44px; display: flex; flex-direction: column; align-items: center; justify-content: center; box-shadow: 0 0 15px ${getDangerColor(seg.danger_level)}44;">
                                    <div style="font-size: 16px; transform: rotate(${seg.weather.wind_direction}deg); color: #fff; line-height:1;margin-bottom:-2px;">↑</div>
                                    <div style="font-size: 9px; font-weight: 800; color: ${getDangerColor(seg.danger_level)};">${seg.weather.wind_speed}kt</div>
                                  </div>
                                `,
                                iconSize: [44, 44],
                                iconAnchor: [22, 22],
                              })}
                            >
                              <Popup>
                                <div style={{ fontFamily: 'Inter', fontSize: '12px' }}>
                                  <strong>Tactical Segment {seg.segment}</strong><br/>
                                  💨 Wind: {seg.weather.wind_speed} kts @ {seg.weather.wind_direction}°<br/>
                                  🌊 Waves: {seg.weather.wave_height}m<br/>
                                  🚢 Speed: {seg.adjusted_speed} kts
                                </div>
                              </Popup>
                            </Marker>
                          </React.Fragment>
                        );
                      })}
                      
                      {/* Weather Ship Marker Animation */}
                      {activeView === "weather" && weatherData && weatherData.route_points && (
                          <ShipMarker 
                            routePositions={weatherData.route_points}
                            color="#38BDF8"
                          />
                      )}
                    </MapContainer>
                  </div>
                </>
              ) : (
                <div className="empty-state">
                  <h3><WaterDrop sx={{ fontSize: 24, mr: 1, verticalAlign: 'middle', color: 'var(--tn-text-muted)' }} /> No weather data</h3>
                  <p>Select ports and click "Weather Routing" to see weather-optimized route</p>
                </div>
              )}
            </>
          )}
        </main>
      </div>
    </div>
  );
};

export default RoutesOptimization;

