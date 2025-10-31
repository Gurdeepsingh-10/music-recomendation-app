import { useMemo } from 'react';
import { Box, IconButton, Tooltip } from '@mui/material';
import ColorizeIcon from '@mui/icons-material/Colorize';

const presetColors = ['#1DB954', '#7C4DFF', '#FF6D00', '#00B8D9', '#E91E63', '#8BC34A'];

const ThemeSwitcher = ({ accent, onChange }) => {
  const selected = useMemo(() => accent?.toLowerCase(), [accent]);

  return (
    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
      <Tooltip title="Accent color">
        <ColorizeIcon sx={{ color: 'text.secondary' }} />
      </Tooltip>
      {presetColors.map((c) => (
        <IconButton
          key={c}
          size="small"
          onClick={() => onChange(c)}
          sx={{
            width: 28,
            height: 28,
            borderRadius: '50%',
            border: '2px solid',
            borderColor: selected === c.toLowerCase() ? 'primary.main' : 'divider',
            backgroundColor: c,
            '&:hover': { transform: 'scale(1.1)' },
          }}
        />
      ))}
    </Box>
  );
};

export default ThemeSwitcher;


