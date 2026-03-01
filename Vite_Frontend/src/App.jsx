import React, { useState, useEffect } from 'react';
import Home from './assets/Components/Home';
import Routess from './assets/Components/RoutesOptimization';
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Dashboard from './assets/Components/Dashboard';
import Navigation from './assets/Components/Navigation';
import Settings from './assets/Components/Settings';
import ErrorBoundary from './components/ErrorBoundary';
import WifiOff from '@mui/icons-material/WifiOff';
import "./App.css"

function App() {
  const [isOnline, setIsOnline] = useState(navigator.onLine);

  useEffect(() => {
    const handleOnline = () => setIsOnline(true);
    const handleOffline = () => setIsOnline(false);

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  return (
    <ErrorBoundary>
      {!isOnline && (
        <div style={{
          background: '#F43F5E',
          color: 'white',
          textAlign: 'center',
          padding: '8px',
          fontWeight: 600,
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          gap: '8px',
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          zIndex: 9999
        }}>
          <WifiOff fontSize="small" /> NO SATELLITE CONNECTION - RUNNING IN OFFLINE CACHE MODE
        </div>
      )}
      <BrowserRouter>
        <Routes>
          <Route path='/' element={<Home />}></Route>
          <Route path='/routes' element={<Routess />}></Route>
          <Route path='/dashboard' element={<Dashboard />}></Route>
          <Route path='/navigation' element={<Navigation />}></Route>
          <Route path='/settings' element={<Settings />}></Route>
        </Routes>
      </BrowserRouter>
    </ErrorBoundary>
  )
}

export default App
