import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { MessageCircleHeart, Loader2, Eye, EyeOff } from 'lucide-react';
import { toast } from 'sonner';

const Landing = () => {
  const navigate = useNavigate();
  const { login, register, isAuthenticated } = useAuth();
  const [isLogin, setIsLogin] = useState(true);
  const [loading, setLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: ''
  });

  React.useEffect(() => {
    if (isAuthenticated) {
      navigate('/chat');
    }
  }, [isAuthenticated, navigate]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    
    try {
      if (isLogin) {
        await login(formData.email, formData.password);
        toast.success('Welcome back!');
      } else {
        if (!formData.name.trim()) {
          toast.error('Please enter your name');
          setLoading(false);
          return;
        }
        await register(formData.name, formData.email, formData.password);
        toast.success('Account created successfully!');
      }
      navigate('/chat');
    } catch (error) {
      const message = error.response?.data?.detail || 'Something went wrong. Please try again.';
      toast.error(message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen relative overflow-hidden">
      {/* Background Image with Overlay */}
      <div 
        className="absolute inset-0 bg-cover bg-center bg-no-repeat"
        style={{
          backgroundImage: 'url(https://images.unsplash.com/photo-1759434188758-194121b6169b?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2Nzd8MHwxfHNlYXJjaHwyfHxzZXJlbmUlMjBtaXN0eSUyMGZvcmVzdCUyMG1vcm5pbmclMjBsaWdodHxlbnwwfHx8fDE3NzI1Mzg1MTh8MA&ixlib=rb-4.1.0&q=85)'
        }}
      />
      <div className="absolute inset-0 bg-gradient-to-b from-white/90 via-white/80 to-white/95" />
      
      <div className="relative z-10 min-h-screen flex flex-col items-center justify-center px-4 py-12">
        {/* Logo & Tagline */}
        <div className="text-center mb-8 animate-fade-in">
          <div className="flex items-center justify-center gap-3 mb-4">
            <div className="p-3 rounded-2xl bg-primary/10">
              <MessageCircleHeart className="w-10 h-10 text-primary" strokeWidth={1.5} />
            </div>
            <h1 className="font-heading text-4xl md:text-5xl font-extrabold tracking-tight text-foreground">
              Sereni
            </h1>
          </div>
          <p className="text-lg md:text-xl text-muted-foreground max-w-md mx-auto leading-relaxed">
            A safe space for your mind. Talk, reflect, and find peace.
          </p>
        </div>

        {/* Auth Card */}
        <Card className="w-full max-w-md shadow-card border-border/40 animate-slide-up animation-delay-200" data-testid="auth-card">
          <CardHeader className="text-center pb-4">
            <CardTitle className="font-heading text-2xl">
              {isLogin ? 'Welcome Back' : 'Create Account'}
            </CardTitle>
            <CardDescription>
              {isLogin ? 'Sign in to continue your journey' : 'Start your wellness journey today'}
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              {!isLogin && (
                <div className="space-y-2">
                  <Label htmlFor="name">Name</Label>
                  <Input
                    id="name"
                    data-testid="name-input"
                    type="text"
                    placeholder="Your name"
                    value={formData.name}
                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                    className="rounded-xl"
                  />
                </div>
              )}
              
              <div className="space-y-2">
                <Label htmlFor="email">Email</Label>
                <Input
                  id="email"
                  data-testid="email-input"
                  type="email"
                  placeholder="you@example.com"
                  value={formData.email}
                  onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                  required
                  className="rounded-xl"
                />
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="password">Password</Label>
                <div className="relative">
                  <Input
                    id="password"
                    data-testid="password-input"
                    type={showPassword ? 'text' : 'password'}
                    placeholder="••••••••"
                    value={formData.password}
                    onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                    required
                    className="rounded-xl pr-10"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground transition-colors"
                  >
                    {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                  </button>
                </div>
              </div>

              <Button
                type="submit"
                data-testid="auth-submit-btn"
                disabled={loading}
                className="w-full rounded-full py-6 text-base font-semibold bg-primary hover:bg-primary/90 transition-all hover:-translate-y-0.5"
              >
                {loading ? (
                  <Loader2 className="w-5 h-5 animate-spin" />
                ) : (
                  isLogin ? 'Sign In' : 'Create Account'
                )}
              </Button>
            </form>

            <div className="mt-6 text-center">
              <button
                type="button"
                onClick={() => setIsLogin(!isLogin)}
                className="text-sm text-muted-foreground hover:text-primary transition-colors"
                data-testid="toggle-auth-mode"
              >
                {isLogin ? "Don't have an account? " : 'Already have an account? '}
                <span className="font-semibold text-primary">
                  {isLogin ? 'Sign up' : 'Sign in'}
                </span>
              </button>
            </div>
          </CardContent>
        </Card>

        {/* Disclaimer */}
        <div className="mt-8 text-center max-w-lg animate-fade-in animation-delay-400">
          <p className="text-xs text-muted-foreground leading-relaxed">
            <strong>Academic Project Notice:</strong> Sereni is an educational project for mental health awareness. 
            It is not a substitute for professional medical advice, diagnosis, or treatment. 
            If you're in crisis, please contact emergency services or a mental health helpline immediately.
          </p>
        </div>
      </div>
    </div>
  );
};

export default Landing;
