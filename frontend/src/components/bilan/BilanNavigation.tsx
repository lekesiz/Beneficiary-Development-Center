import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import {
  Box,
  Drawer,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Divider,
  Typography,
  Chip,
  Avatar
} from '@mui/material';
import {
  Dashboard as DashboardIcon,
  Assessment as AssessmentIcon,
  TrendingUp as CareerIcon,
  Gavel as ComplianceIcon,
  School as LearningIcon,
  ArrowBack as BackIcon
} from '@mui/icons-material';

interface BilanNavigationProps {
  open: boolean;
  onClose?: () => void;
  variant?: 'permanent' | 'persistent' | 'temporary';
  width?: number;
}

const BilanNavigation: React.FC<BilanNavigationProps> = ({ 
  open, 
  onClose, 
  variant = 'permanent',
  width = 240 
}) => {
  const navigate = useNavigate();
  const location = useLocation();

  const navigationItems = [
    {
      title: 'Dashboard',
      path: '/bilan',
      icon: <DashboardIcon />,
      color: 'primary'
    },
    {
      title: '360° Assessments',
      path: '/bilan/assessments',
      icon: <AssessmentIcon />,
      color: 'secondary',
      badge: 'New'
    },
    {
      title: 'Career Intelligence',
      path: '/bilan/career',
      icon: <CareerIcon />,
      color: 'success'
    },
    {
      title: 'Legal Compliance',
      path: '/bilan/compliance',
      icon: <ComplianceIcon />,
      color: 'warning'
    },
    {
      title: 'Advanced Learning',
      path: '/bilan/learning',
      icon: <LearningIcon />,
      color: 'error'
    }
  ];

  const isActive = (path: string) => {
    if (path === '/bilan') {
      return location.pathname === path;
    }
    return location.pathname.startsWith(path);
  };

  return (
    <Drawer
      variant={variant}
      open={open}
      onClose={onClose}
      sx={{
        width: width,
        flexShrink: 0,
        '& .MuiDrawer-paper': {
          width: width,
          boxSizing: 'border-box',
          top: 64, // Account for app bar
          height: 'calc(100% - 64px)'
        },
      }}
    >
      <Box p={2}>
        <Box display="flex" alignItems="center" gap={1} mb={2}>
          <Avatar sx={{ bgcolor: 'primary.main', width: 32, height: 32 }}>
            B
          </Avatar>
          <Typography variant="h6">
            Bilan de Compétence
          </Typography>
        </Box>
        
        <Typography variant="body2" color="textSecondary">
          French Skills Assessment
        </Typography>
      </Box>

      <Divider />

      <List>
        <ListItem disablePadding>
          <ListItemButton onClick={() => navigate('/dashboard')}>
            <ListItemIcon>
              <BackIcon />
            </ListItemIcon>
            <ListItemText primary="Back to Main" />
          </ListItemButton>
        </ListItem>
      </List>

      <Divider />

      <List>
        {navigationItems.map((item) => (
          <ListItem key={item.path} disablePadding>
            <ListItemButton
              selected={isActive(item.path)}
              onClick={() => navigate(item.path)}
              sx={{
                '&.Mui-selected': {
                  bgcolor: `${item.color}.light`,
                  '&:hover': {
                    bgcolor: `${item.color}.light`,
                  }
                }
              }}
            >
              <ListItemIcon sx={{ color: isActive(item.path) ? `${item.color}.main` : 'inherit' }}>
                {item.icon}
              </ListItemIcon>
              <ListItemText 
                primary={item.title}
                primaryTypographyProps={{
                  fontWeight: isActive(item.path) ? 600 : 400
                }}
              />
              {item.badge && (
                <Chip 
                  label={item.badge} 
                  size="small" 
                  color={item.color as any}
                />
              )}
            </ListItemButton>
          </ListItem>
        ))}
      </List>

      <Box flexGrow={1} />

      <Divider />

      <Box p={2}>
        <Typography variant="caption" color="textSecondary">
          Compliance Status
        </Typography>
        <Box display="flex" alignItems="center" gap={1} mt={1}>
          <Box
            sx={{
              width: 8,
              height: 8,
              borderRadius: '50%',
              bgcolor: 'success.main'
            }}
          />
          <Typography variant="body2">
            All requirements met
          </Typography>
        </Box>
      </Box>
    </Drawer>
  );
};

export default BilanNavigation;