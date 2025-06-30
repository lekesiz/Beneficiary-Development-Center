import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/Card';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Loader2, Shield, Users, BookOpen, ChevronRight, Eye, EyeOff, Sparkles, Zap, Globe, Lock, ArrowRight, CheckCircle } from 'lucide-react';
import { useToast } from '@/hooks/useToast';

export const LoginPage: React.FC = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [focusedField, setFocusedField] = useState<string | null>(null);

  // Fix for sm:max-w-md override
  React.useEffect(() => {
    const style = document.createElement('style');
    style.innerHTML = `
      .login-page * {
        max-width: none !important;
      }
      @media (min-width: 640px) {
        .sm\\:max-w-md {
          max-width: 100% !important;
        }
      }
    `;
    document.head.appendChild(style);
    return () => {
      document.head.removeChild(style);
    };
  }, []);
  
  const { login } = useAuth();
  const navigate = useNavigate();
  const { toast } = useToast();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');

    try {
      await login(email, password, 1); // Default tenant ID
      navigate('/dashboard');
    } catch (err) {
      setError('Invalid email or password. Please try again.');
      toast.error('Login failed. Please check your credentials.');
    } finally {
      setIsLoading(false);
    }
  };

  const demoAccounts = [
    { 
      role: 'Administrator', 
      email: 'admin@example.com', 
      password: 'admin123', 
      color: 'blue',
      icon: Shield,
      description: 'Full system access',
      features: ['Manage all users', 'System settings', 'Full reports']
    },
    { 
      role: 'User', 
      email: 'user@example.com', 
      password: 'user123', 
      color: 'emerald',
      icon: Users,
      description: 'Standard access',
      features: ['View content', 'Basic features', 'Reports']
    }
  ];

  const handleDemoLogin = (email: string, password: string) => {
    setEmail(email);
    setPassword(password);
    setError('');
  };

  return (
    <div className="login-page min-h-screen bg-gradient-to-br from-indigo-50 via-white to-blue-50 flex items-center justify-center p-4 relative overflow-hidden">
      {/* Enhanced Background Elements */}
      <div className="absolute inset-0 bg-grid-slate-100 [mask-image:radial-gradient(ellipse_at_center,white,rgba(255,255,255,0.4))] -z-10" />
      <div className="absolute top-0 left-0 w-96 h-96 bg-gradient-to-br from-blue-400/20 to-purple-400/20 rounded-full blur-3xl -translate-x-48 -translate-y-48 animate-pulse" />
      <div className="absolute bottom-0 right-0 w-96 h-96 bg-gradient-to-br from-emerald-400/20 to-blue-400/20 rounded-full blur-3xl translate-x-48 translate-y-48 animate-pulse delay-1000" />
      
      <div className="w-full max-w-6xl mx-auto grid lg:grid-cols-2 gap-8 items-center relative z-10">
        {/* Left Side - Enhanced Branding */}
        <div className="hidden lg:block space-y-8 animate-fade-in">
          <div className="space-y-6">
            {/* Logo & Brand */}
            <div className="flex items-center space-x-4">
              <div className="relative">
                <div className="w-16 h-16 bg-gradient-to-br from-blue-600 to-indigo-700 rounded-2xl flex items-center justify-center shadow-2xl shadow-blue-500/25">
                  <Shield className="w-8 h-8 text-white" />
                </div>
                <div className="absolute -top-1 -right-1 w-6 h-6 bg-gradient-to-br from-emerald-400 to-emerald-500 rounded-full flex items-center justify-center">
                  <Sparkles className="w-3 h-3 text-white" />
                </div>
              </div>
              <div>
                <h1 className="text-4xl font-bold bg-gradient-to-r from-slate-900 to-slate-700 bg-clip-text text-transparent">
                  BDC Platform
                </h1>
                <p className="text-slate-600 font-medium">Beneficiary Development Center</p>
              </div>
            </div>
            
            {/* Hero Content */}
            <div className="space-y-4 pt-6">
              <div className="inline-flex items-center px-4 py-2 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-full border border-blue-200/50">
                <Zap className="w-4 h-4 text-blue-600 mr-2" />
                <span className="text-sm font-medium text-blue-700">Next-Generation Development Platform</span>
              </div>
              
              <h2 className="text-4xl font-bold text-slate-900 leading-tight">
                Transform Lives Through
                <span className="bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent"> Digital Innovation</span>
              </h2>
              
              <p className="text-lg text-slate-600 leading-relaxed">
                Empowering communities with cutting-edge tools for skill development, 
                education, and sustainable growth programs.
              </p>
            </div>
          </div>

          {/* Enhanced Features */}
          <div className="grid grid-cols-1 gap-4">
            {[
              { icon: Users, title: "Smart Analytics", desc: "AI-powered insights for personalized learning paths", color: "blue" },
              { icon: Globe, title: "Global Scale", desc: "Multi-tenant platform serving communities worldwide", color: "emerald" },
              { icon: Lock, title: "Enterprise Security", desc: "Bank-level encryption and compliance standards", color: "purple" }
            ].map((feature, index) => (
              <div key={index} className="group flex items-center space-x-4 p-4 bg-white/60 backdrop-blur-sm rounded-xl border border-white/50 hover:bg-white/80 hover:shadow-lg hover:shadow-slate-200/50 transition-all duration-300">
                <div className={`w-12 h-12 rounded-xl flex items-center justify-center group-hover:scale-110 transition-transform duration-300 ${
                  feature.color === 'blue' ? 'bg-blue-100' : 
                  feature.color === 'emerald' ? 'bg-emerald-100' : 
                  'bg-purple-100'
                }`}>
                  <feature.icon className={`w-6 h-6 ${
                    feature.color === 'blue' ? 'text-blue-600' : 
                    feature.color === 'emerald' ? 'text-emerald-600' : 
                    'text-purple-600'
                  }`} />
                </div>
                <div className="flex-1">
                  <h3 className="font-semibold text-slate-900">{feature.title}</h3>
                  <p className="text-sm text-slate-600">{feature.desc}</p>
                </div>
                <ArrowRight className="w-5 h-5 text-slate-400 group-hover:text-slate-600 group-hover:translate-x-1 transition-all duration-300" />
              </div>
            ))}
          </div>

          {/* Enhanced Statistics */}
          <div className="grid grid-cols-3 gap-4 pt-6">
            {[
              { value: "50K+", label: "Active Users", icon: "👥" },
              { value: "1.2K+", label: "Programs", icon: "📚" },
              { value: "98%", label: "Success Rate", icon: "🎯" }
            ].map((stat, index) => (
              <div key={index} className="text-center p-3 bg-white/50 rounded-lg backdrop-blur-sm border border-white/50">
                <div className="text-xl mb-1">{stat.icon}</div>
                <div className="text-2xl font-bold bg-gradient-to-r from-slate-900 to-slate-700 bg-clip-text text-transparent">{stat.value}</div>
                <div className="text-xs text-slate-600 font-medium">{stat.label}</div>
              </div>
            ))}
          </div>
        </div>

        {/* Right Side - Modern Login Form */}
        <div className="w-full animate-slide-up">
          {/* Mobile Logo */}
          <div className="lg:hidden flex justify-center mb-8">
            <div className="flex items-center space-x-3">
              <div className="w-12 h-12 bg-gradient-to-br from-blue-600 to-indigo-700 rounded-xl flex items-center justify-center shadow-lg">
                <Shield className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-slate-900">BDC Platform</h1>
                <p className="text-slate-600 text-sm">Beneficiary Development Center</p>
              </div>
            </div>
          </div>

          <Card className="shadow-2xl border-0 bg-white/95 backdrop-blur-xl overflow-hidden w-full mx-auto !max-w-none">
            {/* Header with Gradient */}
            <div className="bg-gradient-to-r from-blue-600 to-indigo-600 p-8 lg:p-10 text-center">
              <div className="flex justify-center mb-4">
                <div className="w-16 h-16 bg-white/20 rounded-2xl flex items-center justify-center backdrop-blur-sm">
                  <Lock className="w-8 h-8 text-white" />
                </div>
              </div>
              <h2 className="text-3xl font-bold text-white mb-2">Welcome Back</h2>
              <p className="text-blue-100 text-lg">Sign in to continue your journey</p>
            </div>
            
            <CardContent className="p-8 lg:p-10 space-y-6">
              {error && (
                <Alert variant="destructive" className="animate-slide-down border-red-200 bg-red-50">
                  <AlertDescription className="text-red-700">{error}</AlertDescription>
                </Alert>
              )}

              <form onSubmit={handleSubmit} className="space-y-6">
                <div className="space-y-2">
                  <label htmlFor="email" className="text-sm font-semibold text-slate-700 flex items-center">
                    <Users className="w-4 h-4 mr-2" />
                    Email Address
                  </label>
                  <div className="relative">
                    <Input
                      id="email"
                      type="email"
                      placeholder="Enter your email"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      onFocus={() => setFocusedField('email')}
                      onBlur={() => setFocusedField(null)}
                      required
                      className={`h-12 pl-4 pr-4 text-base transition-all duration-200 border-2 ${
                        focusedField === 'email' 
                          ? 'border-blue-500 shadow-lg shadow-blue-500/25' 
                          : 'border-slate-200 hover:border-slate-300'
                      }`}
                      disabled={isLoading}
                    />
                  </div>
                </div>

                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <label htmlFor="password" className="text-sm font-semibold text-slate-700 flex items-center">
                      <Lock className="w-4 h-4 mr-2" />
                      Password
                    </label>
                    <Link 
                      to="/forgot-password" 
                      className="text-sm text-blue-600 hover:text-blue-700 font-medium hover:underline transition-colors"
                    >
                      Forgot password?
                    </Link>
                  </div>
                  <div className="relative">
                    <Input
                      id="password"
                      type={showPassword ? "text" : "password"}
                      placeholder="Enter your password"
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      onFocus={() => setFocusedField('password')}
                      onBlur={() => setFocusedField(null)}
                      required
                      className={`h-12 pl-4 pr-12 text-base transition-all duration-200 border-2 ${
                        focusedField === 'password' 
                          ? 'border-blue-500 shadow-lg shadow-blue-500/25' 
                          : 'border-slate-200 hover:border-slate-300'
                      }`}
                      disabled={isLoading}
                    />
                    <button
                      type="button"
                      onClick={() => setShowPassword(!showPassword)}
                      className="absolute right-3 top-1/2 transform -translate-y-1/2 text-slate-400 hover:text-slate-600 transition-colors"
                    >
                      {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                    </button>
                  </div>
                </div>

                <Button
                  type="submit"
                  className="w-full h-12 text-base font-semibold bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 transform hover:scale-[1.02] transition-all duration-200 shadow-lg hover:shadow-xl"
                  disabled={isLoading}
                >
                  {isLoading ? (
                    <>
                      <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                      Signing in...
                    </>
                  ) : (
                    <>
                      Sign In
                      <ArrowRight className="w-4 h-4 ml-2" />
                    </>
                  )}
                </Button>
              </form>

              {/* Enhanced Demo Accounts */}
              <div className="pt-6 border-t border-slate-200">
                <div className="flex items-center justify-center mb-4">
                  <div className="flex-1 border-t border-slate-200"></div>
                  <span className="px-4 text-sm font-medium text-slate-500">Quick Demo Access</span>
                  <div className="flex-1 border-t border-slate-200"></div>
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                  {demoAccounts.map((account) => {
                    const IconComponent = account.icon;
                    return (
                      <button
                        key={account.role}
                        type="button"
                        className={`group relative overflow-hidden p-3 rounded-lg transition-all duration-300 hover:-translate-y-0.5 ${
                          account.color === 'blue' 
                            ? 'bg-gradient-to-r from-blue-50 to-blue-100/50 border border-blue-200/50 hover:shadow-lg hover:shadow-blue-500/25' 
                            : account.color === 'emerald'
                            ? 'bg-gradient-to-r from-emerald-50 to-emerald-100/50 border border-emerald-200/50 hover:shadow-lg hover:shadow-emerald-500/25'
                            : 'bg-gradient-to-r from-purple-50 to-purple-100/50 border border-purple-200/50 hover:shadow-lg hover:shadow-purple-500/25'
                        }`}
                        onClick={() => handleDemoLogin(account.email, account.password)}
                        disabled={isLoading}
                      >
                        <div className="flex items-center space-x-3">
                          <div className={`w-10 h-10 rounded-lg flex items-center justify-center shadow-md group-hover:scale-110 transition-transform duration-300 ${
                            account.color === 'blue' 
                              ? 'bg-gradient-to-br from-blue-500 to-blue-600' 
                              : account.color === 'emerald'
                              ? 'bg-gradient-to-br from-emerald-500 to-emerald-600'
                              : 'bg-gradient-to-br from-purple-500 to-purple-600'
                          }`}>
                            <IconComponent className="w-5 h-5 text-white" />
                          </div>
                          <div className="flex-1 text-left">
                            <div className="flex items-center justify-between">
                              <h3 className="font-semibold text-slate-900 text-sm">{account.role}</h3>
                              <ArrowRight className="w-3 h-3 text-slate-400 group-hover:text-slate-600 group-hover:translate-x-1 transition-all duration-300" />
                            </div>
                            <p className="text-xs text-slate-600 mb-1">{account.description}</p>
                            <div className="flex flex-wrap gap-1">
                              {account.features.slice(0, 2).map((feature, idx) => (
                                <span key={idx} className={`text-xs px-2 py-0.5 rounded-full ${
                                  account.color === 'blue' 
                                    ? 'bg-blue-100 text-blue-700' 
                                    : account.color === 'emerald'
                                    ? 'bg-emerald-100 text-emerald-700'
                                    : 'bg-purple-100 text-purple-700'
                                }`}>
                                  {feature}
                                </span>
                              ))}
                            </div>
                          </div>
                        </div>
                      </button>
                    );
                  })}
                </div>
              </div>

              {/* Footer */}
              <div className="text-center pt-4 space-y-3">
                <div className="flex items-center justify-center space-x-4 text-xs text-slate-500">
                  <div className="flex items-center">
                    <CheckCircle className="w-3 h-3 mr-1 text-green-500" />
                    <span>SSL Secured</span>
                  </div>
                  <div className="flex items-center">
                    <Shield className="w-3 h-3 mr-1 text-blue-500" />
                    <span>GDPR Compliant</span>
                  </div>
                </div>
                <p className="text-sm text-slate-600">
                  Need assistance?{' '}
                  <Link to="/support" className="font-semibold text-blue-600 hover:text-blue-700 transition-colors">
                    Contact Support
                  </Link>
                </p>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};