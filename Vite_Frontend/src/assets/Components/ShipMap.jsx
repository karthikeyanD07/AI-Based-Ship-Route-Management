import React, { useState, useEffect, useMemo, useCallback, useRef } from "react";
import { MapContainer, TileLayer, Marker, Popup } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import L from "leaflet";
import "../Styles/ShipMap.css";
import Navbar from "./Navbar";
import SP from "../Img/ship.png";
import { API_BASE_URL } from "../../config";
import { retryWithBackoff } from "../../utils/retry";

const ShipMap = () => {
  const [ships, setShips] = useState([]); 
  const [error, setError] = useState(null); // ✅ Track API errors

  // ✅ Memoized ship icon to prevent unnecessary re-creation
  const shipIcon = useMemo(
    () =>
      new L.Icon({
        iconUrl: SP,
        iconSize: [40, 40],
        iconAnchor: [20, 20],
        popupAnchor: [0, -20],
      }),
    []
  );

  const abortControllerRef = useRef(null);

  // ✅ Fetch ships data with retry logic
  const fetchShips = useCallback(async () => {
    // Cancel previous request if still pending
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
    
    abortControllerRef.current = new AbortController();
    
    try {
      await retryWithBackoff(async () => {
        const response = await fetch(`${API_BASE_URL}/api/ship-traffic`, { 
          signal: abortControllerRef.current.signal 
        });
        if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);

        const data = await response.json();
        if (data.ships && Array.isArray(data.ships)) {
          // Normalize backend payload fields to the UI's expectations
          const normalized = data.ships
            .map((s) => ({
              mmsi: s.MMSI ?? s.mmsi,
              latitude: parseFloat(s.latitude ?? s.lat),
              longitude: parseFloat(s.longitude ?? s.lon),
              sog: s.sog,
              cog: s.cog,
              status: s.status,
              name: s.name || `Vessel ${s.MMSI ?? s.mmsi}`,
            }))
            .filter((s) => !isNaN(s.latitude) && !isNaN(s.longitude));
          setShips(normalized);
          setError(null); // Reset error if fetch succeeds
        } else {
          throw new Error("Invalid ship data format");
        }
      });
    } catch (err) {
      if (err.name !== 'AbortError') {
        setError("🚨 Error fetching ship data. Backend might not be running.");
        console.error(err);
      }
    }
  }, []);

  // ✅ Try WebSocket first, fallback to polling
  useEffect(() => {
    let ws = null;
    let interval = null;
    
    // Try WebSocket connection
    try {
      const wsUrl = API_BASE_URL.replace('http', 'ws') + '/ws/ship-updates';
      ws = new WebSocket(wsUrl);
      
      ws.onopen = () => {
        console.log('WebSocket connected');
        setError(null);
      };
      
      ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (data.type === 'initial' || data.type === 'update') {
          const normalized = data.ships
            .map((s) => ({
              mmsi: s.MMSI ?? s.mmsi,
              latitude: parseFloat(s.latitude ?? s.lat),
              longitude: parseFloat(s.longitude ?? s.lon),
              sog: s.sog,
              cog: s.cog,
              status: s.status,
              name: s.name || `Vessel ${s.MMSI ?? s.mmsi}`,
            }))
            .filter((s) => !isNaN(s.latitude) && !isNaN(s.longitude));
          setShips(normalized);
          setError(null);
        }
      };
      
      ws.onerror = () => {
        console.warn('WebSocket error, falling back to polling');
        // Fallback to polling
        fetchShips();
        interval = setInterval(fetchShips, 5000);
      };
      
      ws.onclose = () => {
        console.log('WebSocket closed, falling back to polling');
        // Fallback to polling
        fetchShips();
        interval = setInterval(fetchShips, 5000);
      };
    } catch (err) {
      console.warn('WebSocket not available, using polling');
      // Fallback to polling
      fetchShips();
      interval = setInterval(fetchShips, 5000);
    }
    
    return () => {
      if (ws) ws.close();
      if (interval) clearInterval(interval);
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
    };
  }, [fetchShips]);

  return (
    <div className="map-body">
      <Navbar />
      <div className="map-title">
        <h1 style={{color:"#004080"}}>NeoECDIS</h1>
      </div>

      {/* ✅ Show error message if API fails */}
      {error && <div className="error">{error}</div>}

      <div className="map-container">
        <MapContainer
          center={[20.0, 70.0]}
          zoom={5}
          className="map"
          worldCopyJump={true}
          minZoom={3}
          maxBounds={[[-85, -180], [85, 180]]}
          maxBoundsViscosity={1.0}
        >
          <TileLayer url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png" noWrap={true} />

          {ships.map((ship) => (
            <Marker key={ship.mmsi} position={[ship.latitude, ship.longitude]} icon={shipIcon}>
              <Popup>
                <strong>{ship.name}</strong>
                <br />
                MMSI: {ship.mmsi}
                <br />
                Speed: {ship.sog ?? "N/A"} knots
                <br />
                Course: {ship.cog ?? "N/A"}°
                <br />
                Status: {ship.status ?? "Unknown"}
              </Popup>
            </Marker>
          ))}
        </MapContainer>
      </div>
    </div>
  );
};

export default ShipMap;
