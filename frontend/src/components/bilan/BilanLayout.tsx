import React, { Suspense } from 'react';
import { Outlet } from 'react-router-dom';
import { Box, CircularProgress, useTheme, useMediaQuery } from '@mui/material';
import BilanNavigation from './BilanNavigation';

const BilanLayout: React.FC = () => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const [mobileOpen, setMobileOpen] = React.useState(false);

  const drawerWidth = 240;

  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen);
  };

  return (
    <Box sx={{ display: 'flex' }}>
      <BilanNavigation
        open={!isMobile || mobileOpen}
        onClose={handleDrawerToggle}
        variant={isMobile ? 'temporary' : 'permanent'}
        width={drawerWidth}
      />
      
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          width: { md: `calc(100% - ${drawerWidth}px)` },
          ml: { md: `${drawerWidth}px` },
          minHeight: '100vh',
          bgcolor: 'background.default'
        }}
      >
        <Suspense
          fallback={
            <Box
              display="flex"
              justifyContent="center"
              alignItems="center"
              minHeight="60vh"
            >
              <CircularProgress />
            </Box>
          }
        >
          <Outlet />
        </Suspense>
      </Box>
    </Box>
  );
};

export default BilanLayout;