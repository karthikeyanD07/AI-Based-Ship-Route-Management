import React, { useState, useEffect } from "react";
import { MapContainer, TileLayer, LayersControl, useMapEvents, ZoomControl } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import L from "leaflet";
import axios from "axios";
import Navbar from "./Navbar";
import { API_BASE_URL, OPENWEATHER_API_KEY } from "../../config";

const Navigation = () => {
  const [error, setError] = useState(null);

  const handleMapClick = async (e) => {
    const { lat, lng } = e.latlng;
    setError(null);

    try {
      // Use backend API for weather
      const response = await axios.get(`${API_BASE_URL}/api/weather`, {
        params: { lat, lon: lng }
      });
      
      const { wind, main, weather } = response.data;

      L.popup()
        .setLatLng([lat, lng])
        .setContent(
          `<b>Weather Info:</b><br>
           🌡️ Temperature: ${main.temp}°C<br>
           🌬️ Wind Speed: ${wind.speed} m/s<br>
           💨 Pressure: ${main.pressure} hPa<br>
           🌩️ Condition: ${weather[0].description}`
        )
        .openOn(e.target._map);
    } catch (error) {
      setError("Failed to fetch weather data. Check API configuration.");
      console.error("Error fetching weather data:", error);
    }
  };

  function MapClickHandler() {
    useMapEvents({ click: handleMapClick });
    return null;
  }

  return (
    <div>
      <Navbar />
      <div style={{ padding: "20px" }}>
        <h1 style={{ color: "#004080" }}>Marine Navigation</h1>
        {error && (
          <div className="error" style={{ color: "red", padding: "10px" }}>
            {error}
          </div>
        )}
        <MapContainer
          center={[20, 80]}
          zoom={3}
          style={{ height: "90vh", width: "100%" }}
          worldCopyJump={true}
          minZoom={3}
          maxBounds={[[-85, -180], [85, 180]]}
          zoomControl={false}
          maxBoundsViscosity={1.0}
        >
          <LayersControl position="topright">
            {/* Base Marine Navigation Chart */}
            <LayersControl.BaseLayer checked name="OpenSeaMap">
              <TileLayer
                url="https://tiles.openseamap.org/seamark/{z}/{x}/{y}.png"
                noWrap={true}
              />
            </LayersControl.BaseLayer>

            {/* Alternative base layers */}
            <LayersControl.BaseLayer name="OpenStreetMap">
              <TileLayer
                url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                noWrap={true}
              />
            </LayersControl.BaseLayer>

            {/* Weather Overlays */}
            {OPENWEATHER_API_KEY && (
              <>
                <LayersControl.Overlay name="Wind Layer">
                  <TileLayer
                    url={`https://tile.openweathermap.org/map/wind_new/{z}/{x}/{y}.png?appid=${OPENWEATHER_API_KEY}`}
                    opacity={0.6}
                    noWrap={true}
                  />
                </LayersControl.Overlay>

                <LayersControl.Overlay name="Temperature Layer">
                  <TileLayer
                    url={`https://tile.openweathermap.org/map/temp_new/{z}/{x}/{y}.png?appid=${OPENWEATHER_API_KEY}`}
                    opacity={0.5}
                    noWrap={true}
                  />
                </LayersControl.Overlay>

                <LayersControl.Overlay name="Pressure Layer">
                  <TileLayer
                    url={`https://tile.openweathermap.org/map/pressure_new/{z}/{x}/{y}.png?appid=${OPENWEATHER_API_KEY}`}
                    opacity={0.5}
                    noWrap={true}
                  />
                </LayersControl.Overlay>
              </>
            )}
          </LayersControl>

          <MapClickHandler />
          <ZoomControl position="bottomright" />
        </MapContainer>
      </div>
    </div>
  );
};

export default Navigation;
