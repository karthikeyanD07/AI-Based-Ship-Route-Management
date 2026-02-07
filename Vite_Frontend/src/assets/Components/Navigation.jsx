import React, { useState, useEffect } from "react";
import { MapContainer, TileLayer, LayersControl, useMapEvents, ZoomControl, Marker, Popup } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import L from "leaflet";
import axios from "axios";
import { useNavigate } from 'react-router-dom';
import Navbar from "./Navbar";
import { API_BASE_URL, OPENWEATHER_API_KEY } from "../../config";
import "../Styles/Routes.css";

// Robust Ship Icon (No external dependencies)
// Using L.divIcon ensures it renders even if external images fail
const shipIcon = L.divIcon({
  className: 'custom-ship-icon',
  html: `<div style="font-size: 24px; filter: drop-shadow(0 0 4px rgba(0,0,0,0.5)); cursor: pointer;">🚢</div>`,
  iconSize: [30, 30],
  popupAnchor: [0, -15],
});

const Navigation = () => {
  const navigate = useNavigate();
  const [error, setError] = useState(null);
  const [activeLayer, setActiveLayer] = useState("chart");
  const [ships, setShips] = useState([]);
  const [loading, setLoading] = useState(true);

  // Fetch Ships logic 
  useEffect(() => {
    const fetchShips = async () => {
      try {
        // LINUS PATCH: Added timeout to prevent hanging
        const response = await axios.get(`${API_BASE_URL}/api/ship-traffic`, { timeout: 5000 });
        if (response.data && response.data.ships) {
          setShips(response.data.ships);
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
    try {
      const res = await axios.post(`${API_BASE_URL}/api/ports/nearest`, {
        lat: ship.lat,
        lon: ship.lon
      });
      navigate(`/routes?mmsi=${ship.mmsi}&start=${res.data.port}`);
    } catch (err) {
      navigate(`/routes?mmsi=${ship.mmsi}`);
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

  return (
    <div style={{ background: "#1a1b26", minHeight: "100vh" }}>
      <Navbar />

      <div style={{ padding: "100px 24px 24px 24px" }}>
        {/* Header with Toggles */}
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "24px" }}>
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
              <Marker key={ship.mmsi} position={[ship.lat, ship.lon]} icon={shipIcon}>
                <Popup>
                  <div style={{ fontFamily: 'Inter', minWidth: '150px' }}>
                    <strong>{ship.name}</strong><br />
                    <span style={{ fontSize: '12px', color: '#565f89' }}>MMSI: {ship.mmsi}</span><br />
                    <div style={{ margin: '8px 0', fontWeight: 'bold', color: '#7aa2f7' }}>
                      {ship.sog} kts • {ship.status}
                    </div>
                    <button
                      onClick={() => handlePlanRoute(ship)}
                      style={{
                        width: '100%', padding: '6px', background: '#e0af68',
                        border: 'none', borderRadius: '4px', cursor: 'pointer',
                        color: '#1a1b26', fontWeight: 'bold', fontSize: '12px'
                      }}
                    >
                      Plan Route from Here
                    </button>
                  </div>
                </Popup>
              </Marker>
            ))}

            <MapClickHandler />
            <ZoomControl position="bottomright" />
          </MapContainer>
        </div>
      </div>
    </div>
  );
};

export default Navigation;
