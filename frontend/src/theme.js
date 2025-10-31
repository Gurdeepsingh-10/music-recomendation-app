import { experimental_extendTheme as extendTheme } from '@mui/material/styles';

export function createAppTheme(accentHex = '#1DB954') {
  // Material 3-like dark theme tokens with transparency preserved
  return extendTheme({
    cssVarPrefix: 'musicrec',
    colorSchemes: {
      dark: {
        palette: {
          mode: 'dark',
          primary: { main: accentHex },
          secondary: { main: '#8AB4F8' },
          background: {
            default: '#121212',
            paper: 'rgba(24,24,24,0.85)',
          },
          surfaceContainer: {
            low: 'rgba(30,30,30,0.75)'
          },
          text: {
            primary: '#FFFFFF',
            secondary: '#B3B3B3',
          },
          divider: 'rgba(255,255,255,0.08)'
        }
      }
    },
    shape: {
      borderRadius: 14
    },
    components: {
      MuiPaper: {
        styleOverrides: {
          root: {
            backdropFilter: 'blur(8px)'
          }
        }
      },
      MuiButton: {
        defaultProps: { disableElevation: true },
        styleOverrides: {
          root: {
            transition: 'transform 180ms cubic-bezier(0.34, 1.56, 0.64, 1), box-shadow 200ms',
          },
          contained: {
            backgroundImage: 'linear-gradient(135deg, var(--musicrec-palette-primary-main) 0%, rgba(29,185,84,0.8) 100%)'
          }
        }
      },
      MuiCard: {
        styleOverrides: {
          root: {
            backgroundColor: 'rgba(32,32,32,0.8)',
            border: '1px solid rgba(255,255,255,0.06)',
            transition: 'transform 180ms cubic-bezier(0.34, 1.56, 0.64, 1)',
          }
        }
      }
    },
    typography: {
      fontFamily: "'Inter', system-ui, -apple-system, Segoe UI, Roboto, 'Helvetica Neue', Arial, 'Noto Sans', 'Apple Color Emoji', 'Segoe UI Emoji'"
    }
  });
}


