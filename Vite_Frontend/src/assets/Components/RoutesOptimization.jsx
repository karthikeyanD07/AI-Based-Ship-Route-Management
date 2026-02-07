import React, { useState, useEffect } from "react";
import { MapContainer, TileLayer, Polyline, Marker, Popup } from "react-leaflet";
import { Autocomplete, TextField } from "@mui/material";
import axios from "axios";
import L from "leaflet";
import "../Styles/Routes.css";
import { API_BASE_URL } from "../../config";

// Ship Marker Component for Animation
const ShipMarker = ({ routePositions, color }) => {
  const [position, setPosition] = useState(null);
  const [index, setIndex] = useState(0);

  useEffect(() => {
    if (!routePositions || routePositions.length === 0) return;

    // Start at beginning
    setPosition(routePositions[0]);

    const interval = setInterval(() => {
      setIndex(prev => {
        const next = prev + 1;
        if (next >= routePositions.length) return 0; // Loop
        return next;
      });
    }, 200); // Animation speed

    return () => clearInterval(interval);
  }, [routePositions]);

  useEffect(() => {
    if (routePositions && routePositions[index]) {
      setPosition(routePositions[index]);
    }
  }, [index, routePositions]);

  if (!position) return null;

  return (
    <Marker
      position={position}
      icon={L.divIcon({
        className: 'ship-icon',
        html: `<div class="ship-marker-inner" style="font-size: 24px; color: ${color}; text-shadow: 0 0 5px ${color};">🚢</div>`,
        iconSize: [30, 30],
        iconAnchor: [15, 15]
      })}
    >
      <Popup>Simulated Vessel Position</Popup>
    </Marker>
  );
};

const RoutesOptimization = () => {
  // Form State
  const [mmsi, setMmsi] = useState("235123456");
  const [ports, setPorts] = useState([]);
  const [filteredPortsStart, setFilteredPortsStart] = useState([]);
  const [filteredPortsEnd, setFilteredPortsEnd] = useState([]);
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

  // Filter ports for start
  useEffect(() => {
    if (startSearch) {
      const filtered = ports.filter(port =>
        port.toLowerCase().includes(startSearch.toLowerCase())
      );
      setFilteredPortsStart(filtered);
    } else {
      setFilteredPortsStart(ports);
    }
  }, [startSearch, ports]);

  // Filter ports for end
  useEffect(() => {
    if (endSearch) {
      const filtered = ports.filter(port =>
        port.toLowerCase().includes(endSearch.toLowerCase())
      );
      setFilteredPortsEnd(filtered);
    } else {
      setFilteredPortsEnd(ports);
    }
  }, [endSearch, ports]);

  const fetchPorts = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/ports/all`);
      setPorts(response.data.ports);
      setFilteredPortsStart(response.data.ports);
      setFilteredPortsEnd(response.data.ports);

      // Linus Patch: Check for "Click-to-Plan" params
      const params = new URLSearchParams(window.location.search);
      const paramMmsi = params.get('mmsi');
      const paramStart = params.get('start');

      if (response.data.ports.length > 0) {
        if (paramMmsi) setMmsi(paramMmsi);

        if (paramStart && response.data.ports.includes(paramStart)) {
          setStartPort(paramStart);
          setStartSearch(paramStart);
          setEndPort(""); // Force user to choose destination
          setEndSearch("");
        } else {
          // Defaults
          setStartPort("Singapore");
          setEndPort("Rotterdam");
          setStartSearch("Singapore");
          setEndSearch("Rotterdam");
        }
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

      setComparisonData(response.data);
      setActiveView("comparison");
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

      setWeatherData(response.data);
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

  return (
    <div className="app-container">
      {/* Header */}
      <header className="app-header">
        <h1>⚓ NeoECDIS Maritime Intelligence</h1>
      </header>

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
            <summary>⚙️ Vessel Configuration</summary>

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

          <button
            className="btn btn-primary"
            onClick={compareRoutes}
            disabled={loading || !startPort || !endPort}
          >
            {loading && activeView === 'comparison' ? 'Analyzing...' : 'Compare Routes'}
          </button>

          <button
            className="btn btn-secondary"
            onClick={getWeatherRoute}
            disabled={loading || !startPort || !endPort}
          >
            {loading && activeView === 'weather' ? 'Loading...' : 'Weather Routing'}
          </button>
        </aside>

        {/* Main Content */}
        <main className="content">
          {error && <div className="error">⚠️ {error}</div>}

          {/* Tabs */}
          <nav className="tabs">
            <button
              className={`tab-btn ${activeView === 'comparison' ? 'active' : ''}`}
              onClick={() => setActiveView('comparison')}
            >
              Route Comparison
            </button>
            <button
              className={`tab-btn ${activeView === 'emissions' ? 'active' : ''}`}
              onClick={() => comparisonData ? calculateEmissions() : setError('Compare routes first')}
            >
              Emissions
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
                          <h3>{route.route_name.toUpperCase()}</h3>
                          <div className="speed-badge">{route.speed_knots} knots</div>
                        </div>

                        <div className="metrics-grid">
                          <div className="metric">
                            <div className="metric-icon">📍</div>
                            <div className="metric-data">
                              <span className="metric-value">{route.distance_km.toLocaleString()}</span>
                              <span className="metric-unit">km</span>
                            </div>
                          </div>

                          <div className="metric">
                            <div className="metric-icon">⏱️</div>
                            <div className="metric-data">
                              <span className="metric-value">{route.estimated_time_days}</span>
                              <span className="metric-unit">days</span>
                            </div>
                          </div>

                          <div className="metric">
                            <div className="metric-icon">🌍</div>
                            <div className="metric-data">
                              <span className="metric-value">{route.total_co2_tonnes}</span>
                              <span className="metric-unit">tonnes CO₂</span>
                            </div>
                          </div>

                          <div className="metric">
                            <div className="metric-icon">⛽</div>
                            <div className="metric-data">
                              <span className="metric-value">{route.fuel_tonnes}</span>
                              <span className="metric-unit">tonnes fuel</span>
                            </div>
                          </div>
                        </div>

                        {route.co2_savings_tonnes > 0 && (
                          <div className="savings-badge">
                            💚 Saves {route.co2_savings_tonnes}t CO₂ ({route.co2_savings_percent}%)
                          </div>
                        )}
                      </div>
                    ))}
                  </div>

                  <div className="recommendation">
                    📊 {comparisonData.recommendation}
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
                          weight={3}
                          opacity={0.9}
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
                  <h3>🗺️ No routes to display</h3>
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
                  <h3>📊 No emissions data</h3>
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

                  <h3 style={{ color: 'var(--tn-text)', margin: '32px 0 16px' }}>🌦️ Weather Segments</h3>
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
                      <Polyline
                        positions={weatherData.route_points}
                        color="#7dcfff"
                        weight={3}
                        opacity={0.9}
                      />
                    </MapContainer>
                  </div>
                </>
              ) : (
                <div className="empty-state">
                  <h3>🌦️ No weather data</h3>
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
