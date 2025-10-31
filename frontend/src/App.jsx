import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import Navbar from './components/Navbar';
import Home from './pages/Home';
import Login from './pages/Login';
import Signup from './pages/Signup';
import Discover from './pages/Discover';
import ForYou from './pages/ForYou';
import Analytics from './pages/Analytics';
import { useEffect, useMemo, useState } from 'react';
import { ThemeProvider, CssBaseline, Container } from '@mui/material';
import { createAppTheme } from './theme';
import ThemeSwitcher from './components/ThemeSwitcher';

function App() {
  const [accent, setAccent] = useState('#1DB954');
  useEffect(() => {
    const saved = localStorage.getItem('accentColor');
    if (saved) setAccent(saved);
  }, []);
  const theme = useMemo(() => createAppTheme(accent), [accent]);

  const handleAccentChange = (c) => {
    setAccent(c);
    localStorage.setItem('accentColor', c);
  };

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Router>
        <Toaster position="top-right" />
        <Navbar rightSlot={<ThemeSwitcher accent={accent} onChange={handleAccentChange} />} />
        <Container maxWidth="lg" sx={{ py: 3 }}>
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/login" element={<Login />} />
            <Route path="/signup" element={<Signup />} />
            <Route path="/discover" element={<Discover />} />
            <Route path="/for-you" element={<ForYou />} />
            <Route path="/analytics" element={<Analytics />} />
          </Routes>
        </Container>
      </Router>
    </ThemeProvider>
  );
}

export default App;