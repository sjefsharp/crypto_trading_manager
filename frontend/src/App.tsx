import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import Dashboard from './components/Dashboard';
import TradingPanel from './components/TradingPanel';
import MarketData from './components/MarketData';
import Portfolio from './components/Portfolio';
import TradingModeSettings from './components/TradingModeSettings';
import APIKeySettings from './components/APIKeySettings';
import './App.css';

const App = () => {
  return (
    <Router>
      <div className='App'>
        <Navbar />
        <div className='container'>
          <Routes>
            <Route path='/' element={<Dashboard />} />
            <Route path='/trading' element={<TradingPanel />} />
            <Route path='/market' element={<MarketData />} />
            <Route path='/portfolio' element={<Portfolio />} />
            <Route path='/settings' element={<TradingModeSettings />} />
            <Route path='/api-keys' element={<APIKeySettings />} />
          </Routes>
        </div>
      </div>
    </Router>
  );
};

export default App;
