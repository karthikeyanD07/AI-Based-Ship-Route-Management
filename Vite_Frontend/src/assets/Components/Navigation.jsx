import React, { useState, useEffect } from "react";
import { MapContainer, TileLayer, LayersControl, useMapEvents, ZoomControl, Marker, Popup, Circle, useMap } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import L from "leaflet";
import axios from "axios";
import { useNavigate } from 'react-router-dom';
import DirectionsBoat from "@mui/icons-material/DirectionsBoat";
import Navbar from "./Navbar";
import { API_BASE_URL, OPENWEATHER_API_KEY } from "../../config";
import "../Styles/Routes.css";

// Professional SVG Ship Icon for live map
const shipIcon = L.divIcon({
  className: 'custom-ship-marker',
  html: `
    <div class="ship-radar-ping"></div>
    <div style="background-color: #7aa2f7; width: 32px; height: 32px; border-radius: 50%; display: flex; align-items: center; justify-content: center; box-shadow: 0 0 20px rgba(122, 162, 247, 0.5), inset 0 0 8px rgba(0,0,0,0.4); border: 2.5px solid #fff; transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275); position: relative; z-index: 2;">
      <svg viewBox="0 0 24 24" width="20" height="20" fill="#fff" style="transform: rotate(-45deg);">
        <path d="M20 21c-1.39 0-2.78-.47-4-1.32-2.44 1.71-5.56 1.71-8 0C6.78 20.53 5.39 21 4 21H2v2h2c1.38 0 2.74-.35 4-.99 2.52 1.29 5.48 1.29 8 0 1.26.65 2.62.99 4 .99h2v-2h-2zM3.95 19H4c1.6 0 3.02-.88 4-2 .98 1.12 2.4 2 4 2s3.02-.88 4-2c.98 1.12 2.4 2 4 2h.05l1.89-6.68c.08-.26.06-.54-.06-.78s-.34-.42-.6-.5L20 10.62V6c0-1.1-.9-2-2-2h-3V1H9v3H6c-1.1 0-2 .9-2 2v4.62l-1.29.42c-.26.08-.47.26-.6.5s-.15.52-.06.78L3.95 19zM6 6h12v3.97L12 8 6 9.97V6z"/>
      </svg>
    </div>
  `,
  iconSize: [32, 32],
  iconAnchor: [16, 16],
  popupAnchor: [0, -16],
});

const Navigation = () => {
  const navigate = useNavigate();
  const [error, setError] = useState(null);
  const [activeLayer, setActiveLayer] = useState("chart");
  const [ships, setShips] = useState([]);
  const [loading, setLoading] = useState(true);
  const [routingShip, setRoutingShip] = useState(null); // I3: track popup button loading

  // Fetch Ships logic 
  useEffect(() => {
    const fetchShips = async () => {
      try {
        // LINUS PATCH: Added timeout to prevent hanging
        const response = await axios.get(`${API_BASE_URL}/api/ship-traffic`, { timeout: 5000 });
        if (response.data && response.data.ships) {
          const valid = response.data.ships.filter(
            s => typeof s.lat === 'number' && typeof s.lon === 'number'
              && isFinite(s.lat) && isFinite(s.lon)
          );
          setShips(valid);
        }
        setLoading(false);
      } catch (err) {
        console.error("Failed to load ships for Navigator", err);
        setError("Failed to load live traffic: " + (err.message || "Timeout"));
        setLoading(false);
      }
    };
    fetchShips();
    const interval = setInterval(fetchShips, 10000);
    return () => clearInterval(interval);
  }, []);

  const handlePlanRoute = async (ship) => {
    setRoutingShip(ship.mmsi); // I3: show loading in popup button
    try {
      setLoading(true);
      const res = await axios.post(`${API_BASE_URL}/api/ports/nearest`, {
        lat: ship.lat,
        lon: ship.lon
      });
      
      const rawMmsi = String(ship.mmsi).replace(/^MMSI-/i, '').slice(0, 9);
      const params = new URLSearchParams({
        mmsi: rawMmsi,
        start: res.data.port,
        end: ship.destination_hint || "Rotterdam",
        type: ship.vessel_type || "container",
        size: ship.vessel_size || "medium"
      });
      
      navigate(`/routes?${params.toString()}`);
    } catch (err) {
      console.error("Failed to find nearest port:", err);
      const rawMmsi = String(ship.mmsi).replace(/^MMSI-/i, '').slice(0, 9);
      navigate(`/routes?mmsi=${rawMmsi}&lat=${ship.lat}&lon=${ship.lon}`);
    } finally {
      setLoading(false);
      setRoutingShip(null);
    }
  };

  const handleMapClick = async (e) => {
    const { lat, lng } = e.latlng;
    setError(null);

    try {
      const response = await axios.get(`${API_BASE_URL}/api/weather`, {
        params: { lat, lon: lng }
      });

      const { wind, main } = response.data;

      L.popup()
        .setLatLng([lat, lng])
        .setContent(
          `<div style="font-family: 'Inter', sans-serif; text-align: center;">
             <div style="font-weight: 700; color: #7aa2f7; margin-bottom: 4px;">Conditions</div>
             <div>🌡️ ${main.temp}°C</div>
             <div>🌬️ ${wind.speed} m/s</div>
             <div>🌊 ${main.pressure} hPa</div>
           </div>`
        )
        .openOn(e.target._map);
    } catch (error) {
      console.error("Error fetching data:", error);
    }
  };

  function MapClickHandler() {
    useMapEvents({ click: handleMapClick });
    return null;
  }

  // Tactical Region Quick-Focus
  const HotspotControls = () => {
    const map = useMap();
    const hotspots = [
      { name: "Global", center: [6.0, 80.0], zoom: 4 },
      { name: "Malacca", center: [1.29, 103.85], zoom: 11 },
      { name: "Suez", center: [30.59, 32.27], zoom: 10 },
      { name: "Cape", center: [-34.35, 18.47], zoom: 8 },
      { name: "English Channel", center: [50.5, -0.5], zoom: 8 },
      { name: "Panama", center: [9.08, -79.69], zoom: 11 }
    ];

    return (
      <div className="hotspot-bar" style={{ 
        position: 'absolute', bottom: '24px', left: '50%', transform: 'translateX(-50%)', 
        zIndex: 1000, display: 'flex', gap: '8px', background: 'rgba(26, 27, 38, 0.9)', 
        padding: '8px', borderRadius: '40px', border: '1px solid rgba(122, 162, 247, 0.2)', 
        backdropFilter: 'blur(10px)', boxShadow: '0 8px 32px rgba(0,0,0,0.5)'
      }}>
        {hotspots.map(spot => (
          <button 
            key={spot.name}
            onClick={() => map.setView(spot.center, spot.zoom)}
            style={{ 
              background: 'transparent', border: 'none', padding: '8px 16px', 
              color: '#94A3B8', fontSize: '12px', fontWeight: 'bold', 
              cursor: 'pointer', borderRadius: '20px', transition: 'all 0.2s'
            }}
            onMouseOver={(e) => { e.target.style.color = '#7aa2f7'; e.target.style.background = 'rgba(122, 162, 247, 0.1)'; }}
            onMouseOut={(e) => { e.target.style.color = '#94A3B8'; e.target.style.background = 'transparent'; }}
          >
            {spot.name}
          </button>
        ))}
      </div>
    );
  };

  return (
    <div style={{ background: "#1a1b26", minHeight: "100vh" }}>
      <Navbar />

      <div style={{ padding: "100px 24px 24px 24px" }}>
        {/* Header with Toggles */}
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "24px", flexWrap: 'wrap', gap: '12px' }}>
          <div>
            <h1 style={{ color: "#e0af68", fontSize: "28px", fontWeight: "700", margin: 0 }}>Smart Navigator</h1>
            <p style={{ color: "#565f89", margin: "4px 0 0 0", fontSize: "14px" }}>
              Live Traffic • Electronic Charts • Weather Integration
            </p>
          </div>

          <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
            {/* Status Indicator */}
            <div style={{
              padding: '6px 12px', borderRadius: '20px', fontSize: '12px', fontWeight: '600',
              background: ships.length > 0 ? 'rgba(78, 205, 196, 0.1)' : 'rgba(247, 118, 142, 0.1)',
              color: ships.length > 0 ? '#4ECDC4' : '#f7768e',
              border: `1px solid ${ships.length > 0 ? '#4ECDC4' : '#f7768e'}`
            }}>
              {loading ? "Scanning..." : `${ships.length} Vessels Online`}
            </div>

            {/* View Toggle */}
            <div style={{ background: "#1f2335", padding: "4px", borderRadius: "8px", border: "1px solid #292e42", display: "flex", gap: "4px" }}>
              <button
                onClick={() => setActiveLayer("chart")}
                style={{
                  background: activeLayer === "chart" ? "#7aa2f7" : "transparent",
                  color: activeLayer === "chart" ? "#1a1b26" : "#7aa2f7",
                  border: "none", padding: "8px 16px", borderRadius: "6px", fontWeight: "600", cursor: "pointer", transition: "all 0.2s"
                }}
              >
                ⚓ ENC Chart
              </button>
              <button
                onClick={() => setActiveLayer("weather")}
                style={{
                  background: activeLayer === "weather" ? "#bb9af7" : "transparent",
                  color: activeLayer === "weather" ? "#1a1b26" : "#bb9af7",
                  border: "none", padding: "8px 16px", borderRadius: "6px", fontWeight: "600", cursor: "pointer", transition: "all 0.2s"
                }}
              >
                ⛈️ Weather Map
              </button>
            </div>
          </div>
        </div>

        {error && (
          <div className="error" style={{ marginBottom: "16px", color: '#ff6b6b', background: 'rgba(255,107,107,0.1)', padding: '10px', borderRadius: '8px' }}>
            ⚠️ {error}
          </div>
        )}

        <div style={{
          height: "calc(100vh - 200px)",
          border: "1px solid #292e42",
          borderRadius: "12px",
          overflow: "hidden",
          boxShadow: "0 10px 30px rgba(0,0,0,0.3)"
        }}>
          <MapContainer
            center={[6.0, 80.0]}
            zoom={4}
            style={{ height: "100%", width: "100%", background: "#1a1b26" }}
            zoomControl={false}
            worldCopyJump={true}
          >
            <LayersControl position="topright">
              {/* Base Maps */}
              <LayersControl.BaseLayer checked name="Dark Matter (Default)">
                <TileLayer
                  url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
                  noWrap={true}
                />
              </LayersControl.BaseLayer>

              <LayersControl.Overlay checked={activeLayer === "chart"} name="OpenSeaMap (Nautical)">
                <TileLayer
                  url="https://tiles.openseamap.org/seamark/{z}/{x}/{y}.png"
                  opacity={1.0}
                />
              </LayersControl.Overlay>

              {/* Weather Overlays */}
              {OPENWEATHER_API_KEY && (
                <>
                  <LayersControl.Overlay checked={activeLayer === "weather"} name="Wind Speed">
                    <TileLayer
                      url={`https://tile.openweathermap.org/map/wind_new/{z}/{x}/{y}.png?appid=${OPENWEATHER_API_KEY}`}
                      opacity={0.6}
                    />
                  </LayersControl.Overlay>

                  <LayersControl.Overlay name="Pressure">
                    <TileLayer
                      url={`https://tile.openweathermap.org/map/pressure_new/{z}/{x}/{y}.png?appid=${OPENWEATHER_API_KEY}`}
                      opacity={0.5}
                    />
                  </LayersControl.Overlay>
                </>
              )}
            </LayersControl>

            {/* Live Ship Traffic Layer */}
            {ships.map(ship => (
              <Marker key={ship.mmsi} position={[ship.lat, ship.lon]} icon={L.divIcon({
                className: 'custom-ship-marker',
                html: `
                  <div class="ship-radar-ping"></div>
                  <div style="background-color: ${ship.vessel_type === 'tanker' ? '#f7768e' : ship.vessel_type === 'bulk' ? '#e0af68' : '#7aa2f7'}; width: 32px; height: 32px; border-radius: 50%; display: flex; align-items: center; justify-content: center; box-shadow: 0 0 20px rgba(122, 162, 247, 0.4), inset 0 0 8px rgba(0,0,0,0.4); border: 2.5px solid #fff; transition: all 0.3s ease; position: relative;">
                    <svg viewBox="0 0 24 24" width="18" height="18" fill="#fff" style="transform: rotate(${ship.cog - 45}deg);">
                      <path d="M20 21c-1.39 0-2.78-.47-4-1.32-2.44 1.71-5.56 1.71-8 0C6.78 20.53 5.39 21 4 21H2v2h2c1.38 0 2.74-.35 4-.99 2.52 1.29 5.48 1.29 8 0 1.26.65 2.62.99 4 .99h2v-2h-2zM3.95 19H4c1.6 0 3.02-.88 4-2 .98 1.12 2.4 2 4 2s3.02-.88 4-2.1c.98 1.12 2.4 2 4 2h.05l1.89-6.68c.08-.26.06-.54-.06-.78s-.34-.42-.6-.5L20 10.62V6c0-1.1-.9-2-2-2h-3V1H9v3H6c-1.1 0-2 .9-2 2v4.62l-1.29.42c-.26.08-.47.26-.6.5s-.15.52-.06.78L3.95 19zM6 6h12v3.97L12 8 6 9.97V6z"/>
                    </svg>
                  </div>
                `,
                iconSize: [32, 32],
                iconAnchor: [16, 16],
                popupAnchor: [0, -16],
              })}>
                <Popup>
                  <div style={{ fontFamily: 'Inter', minWidth: '180px', padding: '4px' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                      <strong style={{ fontSize: '15px', color: '#1a1b26' }}>{ship.name || "Unknown Vessel"}</strong>
                      <span style={{ fontSize: '10px', background: '#e0af68', color: '#1a1b26', padding: '2px 6px', borderRadius: '10px', fontWeight: 'bold' }}>
                        {(ship.vessel_type || "cargo").toUpperCase()}
                      </span>
                    </div>
                    
                    <div style={{ fontSize: '12px', color: '#565f89', marginBottom: '12px' }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                        <span>MMSI:</span> <span>{ship.mmsi}</span>
                      </div>
                      <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '4px' }}>
                        <span>Status:</span> <span style={{ color: '#4ECDC4', fontWeight: 'bold' }}>{ship.status}</span>
                      </div>
                      <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '4px' }}>
                        <span>Course:</span> <span>{ship.cog}° @ {ship.sog} kts</span>
                      </div>
                    </div>

                    <button
                      onClick={() => handlePlanRoute(ship)}
                      disabled={routingShip === ship.mmsi}
                      style={{
                        width: '100%', padding: '10px',
                        background: routingShip === ship.mmsi
                          ? 'rgba(122, 162, 247, 0.4)'
                          : 'linear-gradient(135deg, #7aa2f7, #bb9af7)',
                        border: 'none', borderRadius: '6px', cursor: routingShip === ship.mmsi ? 'wait' : 'pointer',
                        color: '#fff', fontWeight: 'bold', fontSize: '13px',
                        boxShadow: '0 4px 12px rgba(122, 162, 247, 0.3)',
                        transition: 'all 0.2s ease',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        gap: '8px'
                      }}
                    >
                      <DirectionsBoat fontSize="small" />
                      {routingShip === ship.mmsi ? '⏳ Planning...' : 'Plan Voyage Optimizer'}
                    </button>
                    <div style={{ textAlign: 'center', marginTop: '8px', fontSize: '10px', color: '#94A3B8' }}>
                      Dest. Hint: {ship.destination_hint || "N/A"}
                    </div>
                  </div>
                </Popup>
              </Marker>
            ))}

            {/* Port Density Clusters */}
            <LayersControl.Overlay checked name="Port Traffic Density">
                <>
                  <Circle center={[1.29, 103.85]} radius={30000} pathOptions={{ color: '#4ECDC4', fillColor: '#4ECDC4', fillOpacity: 0.15 }}>
                    <Popup>Singapore: High density port sector.</Popup>
                  </Circle>
                  <Circle center={[30.59, 32.27]} radius={20000} pathOptions={{ color: '#ff6b6b', fillColor: '#ff6b6b', fillOpacity: 0.1 }}>
                    <Popup>Suez: Congestion Alert Active.</Popup>
                  </Circle>
                  <Circle center={[6.92, 79.86]} radius={15000} pathOptions={{ color: '#7aa2f7', fillColor: '#7aa2f7', fillOpacity: 0.2 }}>
                    <Popup>Colombo: Busy transporthub.</Popup>
                  </Circle>
                </>
            </LayersControl.Overlay>

            <MapClickHandler />
            <HotspotControls />
            <ZoomControl position="bottomright" />
          </MapContainer>
        </div>
      </div>
    </div>
  );
};

export default Navigation;
