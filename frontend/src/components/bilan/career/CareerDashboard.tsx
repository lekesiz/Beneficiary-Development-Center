import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  Button,
  LinearProgress,
  Chip,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Paper,
  Alert,
  Skeleton,
  Avatar
} from '@mui/material';
import {
  TrendingUp as TrendingUpIcon,
  Work as WorkIcon,
  School as SchoolIcon,
  Analytics as AnalyticsIcon,
  LocationOn as LocationIcon,
  AttachMoney as MoneyIcon,
  Timeline as TimelineIcon,
  Assessment as AssessmentIcon
} from '@mui/icons-material';
import { careerApi } from '../../../api/bilan';
import { useAuth } from '../../../contexts/AuthContext';
import type { CareerPath, JobOpportunity, SkillGapAnalysis, JobMarketData } from '../../../types/bilan';

const CareerDashboard: React.FC = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [loading, setLoading] = useState(true);
  const [careerPaths, setCareerPaths] = useState<CareerPath[]>([]);
  const [jobOpportunities, setJobOpportunities] = useState<JobOpportunity[]>([]);
  const [skillAnalysis, setSkillAnalysis] = useState<SkillGapAnalysis | null>(null);
  const [marketData, setMarketData] = useState<JobMarketData[]>([]);

  useEffect(() => {
    fetchCareerData();
  }, []);

  const fetchCareerData = async () => {
    try {
      setLoading(true);
      const [pathsRes, opportunitiesRes, marketRes] = await Promise.all([
        careerApi.getCareerPaths(),
        careerApi.getJobOpportunities({ per_page: 5 }),
        careerApi.searchMarketData({ per_page: 3 })
      ]);

      setCareerPaths(pathsRes.data);
      setJobOpportunities(opportunitiesRes.data.items);
      setMarketData(marketRes.data.items);

      // Get latest skill analysis if career path exists
      if (pathsRes.data.length > 0) {
        // This would need an endpoint to get the latest analysis
        // For now, we'll skip it
      }
    } catch (err) {
      console.error('Error fetching career data:', err);
    } finally {
      setLoading(false);
    }
  };

  const activePath = careerPaths.find(p => p.careerStatus === 'PLANNING' || p.careerStatus === 'TRANSITIONING');

  if (loading) {
    return <CareerDashboardSkeleton />;
  }

  return (
    <Box p={3}>
      <Typography variant="h4" gutterBottom>
        Career Intelligence Center
      </Typography>

      {/* Active Career Path */}
      {activePath ? (
        <Card sx={{ mb: 3 }}>
          <CardContent>
            <Box display="flex" justifyContent="space-between" alignItems="start" mb={2}>
              <Box>
                <Typography variant="h6" gutterBottom>
                  Active Career Path
                </Typography>
                <Typography variant="h5">
                  {activePath.targetJobTitle}
                </Typography>
                {activePath.targetIndustry && (
                  <Typography variant="body2" color="textSecondary">
                    Industry: {activePath.targetIndustry}
                  </Typography>
                )}
              </Box>
              <Chip
                label={activePath.careerStatus.replace('_', ' ')}
                color="primary"
              />
            </Box>

            <Box mb={2}>
              <Box display="flex" justifyContent="space-between" mb={1}>
                <Typography variant="body2">Progress</Typography>
                <Typography variant="body2">{activePath.progressPercentage}%</Typography>
              </Box>
              <LinearProgress
                variant="determinate"
                value={activePath.progressPercentage}
                sx={{ height: 8, borderRadius: 4 }}
              />
            </Box>

            <Grid container spacing={2}>
              <Grid item xs={6}>
                <Typography variant="body2" color="textSecondary">
                  Milestones Completed
                </Typography>
                <Typography variant="h6">
                  {activePath.milestones?.filter(m => m.status === 'completed').length || 0} / {activePath.milestones?.length || 0}
                </Typography>
              </Grid>
              <Grid item xs={6}>
                <Typography variant="body2" color="textSecondary">
                  Estimated Completion
                </Typography>
                <Typography variant="h6">
                  {activePath.estimatedCompletion 
                    ? new Date(activePath.estimatedCompletion).toLocaleDateString() 
                    : 'Not Set'}
                </Typography>
              </Grid>
            </Grid>

            <Box display="flex" gap={2} mt={2}>
              <Button
                variant="outlined"
                onClick={() => navigate(`/bilan/career/paths/${activePath.id}`)}
              >
                View Details
              </Button>
              <Button
                variant="contained"
                onClick={() => navigate(`/bilan/career/paths/${activePath.id}/milestones`)}
              >
                Update Progress
              </Button>
            </Box>
          </CardContent>
        </Card>
      ) : (
        <Alert severity="info" sx={{ mb: 3 }}>
          <Typography variant="body1" gutterBottom>
            No active career path found
          </Typography>
          <Button
            variant="contained"
            size="small"
            onClick={() => navigate('/bilan/career/paths/new')}
            sx={{ mt: 1 }}
          >
            Create Career Path
          </Button>
        </Alert>
      )}

      <Grid container spacing={3}>
        {/* Job Market Insights */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                <TrendingUpIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
                Hot Job Markets
              </Typography>
              
              {marketData.length === 0 ? (
                <Typography variant="body2" color="textSecondary">
                  No market data available
                </Typography>
              ) : (
                <List>
                  {marketData.map((data, index) => (
                    <ListItem key={data.id} divider={index < marketData.length - 1}>
                      <ListItemText
                        primary={data.jobTitle}
                        secondary={
                          <Box>
                            <Typography variant="body2" color="textSecondary">
                              {data.location} • {data.industry}
                            </Typography>
                            <Box display="flex" alignItems="center" gap={1} mt={0.5}>
                              <Chip
                                label={`Demand: ${data.demandLevel}`}
                                size="small"
                                color={data.demandLevel === 'HIGH' || data.demandLevel === 'VERY_HIGH' ? 'success' : 'default'}
                              />
                              {data.averageSalary && (
                                <Typography variant="body2">
                                  Avg: ${data.averageSalary.toLocaleString()}
                                </Typography>
                              )}
                            </Box>
                          </Box>
                        }
                      />
                    </ListItem>
                  ))}
                </List>
              )}
              
              <Button
                fullWidth
                variant="outlined"
                sx={{ mt: 2 }}
                onClick={() => navigate('/bilan/career/market')}
              >
                Explore Job Market
              </Button>
            </CardContent>
          </Card>
        </Grid>

        {/* Job Opportunities */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                <WorkIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
                Matched Opportunities
              </Typography>
              
              {jobOpportunities.length === 0 ? (
                <Typography variant="body2" color="textSecondary">
                  No opportunities found yet
                </Typography>
              ) : (
                <List>
                  {jobOpportunities.slice(0, 3).map((opp, index) => (
                    <ListItem key={opp.id} divider={index < 2}>
                      <ListItemText
                        primary={opp.jobTitle}
                        secondary={
                          <Box>
                            <Typography variant="body2" color="textSecondary">
                              {opp.companyName}
                            </Typography>
                            <Box display="flex" alignItems="center" gap={1} mt={0.5}>
                              <LocationIcon sx={{ fontSize: 16 }} />
                              <Typography variant="body2">{opp.location}</Typography>
                              <Chip
                                label={`${opp.matchScore}% Match`}
                                size="small"
                                color={opp.matchScore > 80 ? 'success' : 'default'}
                              />
                            </Box>
                          </Box>
                        }
                      />
                    </ListItem>
                  ))}
                </List>
              )}
              
              <Button
                fullWidth
                variant="outlined"
                sx={{ mt: 2 }}
                onClick={() => navigate('/bilan/career/opportunities')}
              >
                View All Opportunities
              </Button>
            </CardContent>
          </Card>
        </Grid>

        {/* Skills Analysis */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                <AnalyticsIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
                Skills Analysis
              </Typography>
              
              {skillAnalysis ? (
                <Box>
                  <Box mb={2}>
                    <Typography variant="body2" color="textSecondary">
                      Critical Skill Gaps
                    </Typography>
                    <Box display="flex" flexWrap="wrap" gap={1} mt={1}>
                      {skillAnalysis.criticalGaps.slice(0, 3).map(skill => (
                        <Chip
                          key={skill}
                          label={skill}
                          size="small"
                          color="error"
                        />
                      ))}
                    </Box>
                  </Box>
                  
                  <Box mb={2}>
                    <Typography variant="body2" color="textSecondary">
                      Priority Skills to Develop
                    </Typography>
                    <Box display="flex" flexWrap="wrap" gap={1} mt={1}>
                      {skillAnalysis.prioritySkills.slice(0, 3).map(skill => (
                        <Chip
                          key={skill}
                          label={skill}
                          size="small"
                          color="primary"
                        />
                      ))}
                    </Box>
                  </Box>
                  
                  <Typography variant="body2" color="textSecondary">
                    Last analyzed: {new Date(skillAnalysis.analysisDate).toLocaleDateString()}
                  </Typography>
                </Box>
              ) : (
                <Box textAlign="center" py={3}>
                  <AssessmentIcon sx={{ fontSize: 48, color: 'text.secondary', mb: 1 }} />
                  <Typography variant="body2" color="textSecondary">
                    No skill analysis available
                  </Typography>
                </Box>
              )}
              
              <Button
                fullWidth
                variant="outlined"
                sx={{ mt: 2 }}
                onClick={() => navigate('/bilan/career/skills')}
              >
                Analyze My Skills
              </Button>
            </CardContent>
          </Card>
        </Grid>

        {/* Career Tools */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                <SchoolIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
                Career Tools
              </Typography>
              
              <List>
                <ListItem
                  button
                  onClick={() => navigate('/bilan/career/documents')}
                >
                  <ListItemIcon>
                    <Avatar sx={{ bgcolor: 'primary.light' }}>📄</Avatar>
                  </ListItemIcon>
                  <ListItemText
                    primary="Resume & Documents"
                    secondary="Manage your career documents"
                  />
                </ListItem>
                
                <ListItem
                  button
                  onClick={() => navigate('/bilan/career/insights')}
                >
                  <ListItemIcon>
                    <Avatar sx={{ bgcolor: 'secondary.light' }}>💡</Avatar>
                  </ListItemIcon>
                  <ListItemText
                    primary="AI Career Insights"
                    secondary="Get personalized recommendations"
                  />
                </ListItem>
                
                <ListItem
                  button
                  onClick={() => navigate('/bilan/career/timeline')}
                >
                  <ListItemIcon>
                    <Avatar sx={{ bgcolor: 'success.light' }}>📈</Avatar>
                  </ListItemIcon>
                  <ListItemText
                    primary="Career Timeline"
                    secondary="Track your career journey"
                  />
                </ListItem>
              </List>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

const CareerDashboardSkeleton: React.FC = () => (
  <Box p={3}>
    <Skeleton variant="text" width={300} height={40} sx={{ mb: 3 }} />
    <Skeleton variant="rectangular" height={200} sx={{ mb: 3 }} />
    <Grid container spacing={3}>
      {[1, 2, 3, 4].map(i => (
        <Grid item xs={12} md={6} key={i}>
          <Skeleton variant="rectangular" height={300} />
        </Grid>
      ))}
    </Grid>
  </Box>
);

export default CareerDashboard;