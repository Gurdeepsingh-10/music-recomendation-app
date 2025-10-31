import { Link as RouterLink, useNavigate, useLocation } from 'react-router-dom';
import useAuthStore from '../store/authStore';
import {
  AppBar,
  Toolbar,
  Typography,
  Button,
  IconButton,
  Box,
  Tabs,
  Tab,
  Avatar,
  Paper
} from '@mui/material';
import LibraryMusicIcon from '@mui/icons-material/LibraryMusic';
import HomeRoundedIcon from '@mui/icons-material/HomeRounded';
import ExploreRoundedIcon from '@mui/icons-material/ExploreRounded';
import FavoriteRoundedIcon from '@mui/icons-material/FavoriteRounded';
import InsightsRoundedIcon from '@mui/icons-material/InsightsRounded';
import LogoutRoundedIcon from '@mui/icons-material/LogoutRounded';

const Navbar = ({ rightSlot }) => {
  const { isAuthenticated, user, logout } = useAuthStore();
  const navigate = useNavigate();
  const location = useLocation();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const navItems = [
    { path: '/', icon: <HomeRoundedIcon />, label: 'Home' },
    { path: '/discover', icon: <ExploreRoundedIcon />, label: 'Discover' },
    { path: '/for-you', icon: <FavoriteRoundedIcon />, label: 'For You' },
    { path: '/analytics', icon: <InsightsRoundedIcon />, label: 'Stats' },
  ];

  const value = navItems.findIndex(i => i.path === location.pathname);

  return (
    <AppBar position="sticky" color="transparent" elevation={0} sx={{ backdropFilter: 'blur(10px)', borderBottom: '1px solid', borderColor: 'divider' }}>
      <Toolbar sx={{ display: 'flex', gap: 2 }}>
        <IconButton color="primary" component={RouterLink} to="/" sx={{
          bgcolor: 'primary.main',
          color: 'white',
          '&:hover': { transform: 'scale(1.08)' }
        }}>
          <LibraryMusicIcon />
        </IconButton>
        <Typography variant="h6" sx={{ fontWeight: 800 }} component={RouterLink} to="/" color="inherit" style={{ textDecoration: 'none' }}>
          Music<Typography component="span" variant="h6" color="primary" sx={{ fontWeight: 800 }}>Rec</Typography>
        </Typography>

        {isAuthenticated && (
          <Tabs value={value !== -1 ? value : false} sx={{ ml: 2 }} textColor="inherit" indicatorColor="primary">
            {navItems.map((item) => (
              <Tab key={item.path}
                   icon={item.icon}
                   iconPosition="start"
                   label={item.label}
                   component={RouterLink}
                   to={item.path}
                   sx={{ minHeight: 48 }} />
            ))}
          </Tabs>
        )}

        <Box sx={{ flexGrow: 1 }} />

        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          {rightSlot}
          {isAuthenticated ? (
            <>
              <Paper sx={{ px: 1.5, py: 0.5, display: 'flex', alignItems: 'center', gap: 1, bgcolor: 'background.paper' }} elevation={0}>
                <Avatar sx={{ width: 28, height: 28 }}>{(user?.username || 'U').slice(0,1).toUpperCase()}</Avatar>
                <Typography variant="body2" color="text.secondary" sx={{ display: { xs: 'none', sm: 'block' } }}>
                  {user?.username || 'User'}
                </Typography>
              </Paper>
              <Button variant="contained" color="primary" startIcon={<LogoutRoundedIcon />} onClick={handleLogout} sx={{
                borderRadius: 999,
                '&:hover': { transform: 'translateY(-1px)' }
              }}>
                Logout
              </Button>
            </>
          ) : (
            <Box sx={{ display: 'flex', gap: 1 }}>
              <Button component={RouterLink} to="/login" color="inherit">Login</Button>
              <Button component={RouterLink} to="/signup" variant="contained">Sign Up</Button>
            </Box>
          )}
        </Box>
      </Toolbar>
    </AppBar>
  );
};

export default Navbar;