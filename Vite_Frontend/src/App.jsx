import Home from './assets/Components/Home';
import Routess from './assets/Components/RoutesOptimization';
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Dashboard from './assets/Components/Dashboard';
import Navigation from './assets/Components/Navigation';
import Settings from './assets/Components/Settings';
import ErrorBoundary from './components/ErrorBoundary';
import "./App.css"

function App() {
  return (
    <ErrorBoundary>
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
