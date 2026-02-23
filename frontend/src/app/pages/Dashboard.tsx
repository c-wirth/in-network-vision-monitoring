import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { Button } from '../components/ui/button';
import { Switch } from '../components/ui/switch';
import { Slider } from '../components/ui/slider';
import { Label } from '../components/ui/label';
import { 
  Video, 
  Cpu, 
  HardDrive, 
  Play, 
  Square,
  AlertCircle,
  CheckCircle2 
} from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';

export default function Dashboard() {
  const { user } = useAuth();
  const [detectionEnabled, setDetectionEnabled] = useState(true);
  const [sensitivity, setSensitivity] = useState([75]);
  const [isRecording, setIsRecording] = useState(false);
  const [liveTime, setLiveTime] = useState(0);

  // Simulate live timer
  useEffect(() => {
    const interval = setInterval(() => {
      setLiveTime((prev) => prev + 1);
    }, 1000);
    return () => clearInterval(interval);
  }, []);

  const formatTime = (seconds: number) => {
    const hrs = Math.floor(seconds / 3600);
    const mins = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    return `${hrs.toString().padStart(2, '0')}:${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  const systemStatus = [
    { label: 'Camera', status: 'online', icon: Video, color: 'bg-green-500' },
    { label: 'AI Engine', status: 'active', icon: Cpu, color: 'bg-blue-500' },
    { label: 'Storage', status: '78% free', icon: HardDrive, color: 'bg-yellow-500' },
  ];

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-3xl font-bold tracking-tight">Dashboard</h2>
        <p className="text-muted-foreground">Real-time monitoring and control center</p>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        {/* Live Video Feed */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle>Live Feed</CardTitle>
              <Badge variant={detectionEnabled ? 'default' : 'secondary'} className="animate-pulse">
                {detectionEnabled ? 'LIVE' : 'PAUSED'}
              </Badge>
            </div>
            <CardDescription>Main camera · {formatTime(liveTime)}</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="relative aspect-video bg-slate-900 rounded-lg overflow-hidden">
              {/* Simulated video feed */}
              <div className="absolute inset-0 bg-gradient-to-br from-slate-800 to-slate-900" />
              <div className="absolute inset-0 flex items-center justify-center">
                <Video className="w-24 h-24 text-slate-700" />
              </div>
              
              {/* Detection overlay indicators */}
              {detectionEnabled && (
                <>
                  <div className="absolute top-4 left-4 bg-red-500/20 border border-red-500 rounded px-3 py-1 text-xs text-red-400 font-mono">
                    REC
                  </div>
                  <div className="absolute top-4 right-4 space-y-1 text-xs text-slate-300 font-mono">
                    <div>FPS: 30.0</div>
                    <div>RES: 1920x1080</div>
                  </div>
                </>
              )}

              {/* Timestamp */}
              <div className="absolute bottom-4 left-4 bg-black/50 backdrop-blur-sm px-3 py-1 rounded text-xs text-white font-mono">
                {new Date().toLocaleString()}
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Controls Panel */}
        <div className="space-y-6">
          {/* Detection Toggle */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Detection Control</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between">
                <Label htmlFor="detection-toggle" className="font-medium">
                  Detection {detectionEnabled ? 'ON' : 'OFF'}
                </Label>
                <Switch
                  id="detection-toggle"
                  checked={detectionEnabled}
                  onCheckedChange={setDetectionEnabled}
                />
              </div>
              <p className="text-xs text-muted-foreground">
                {detectionEnabled 
                  ? 'AI is actively monitoring for motion and persons'
                  : 'Detection is paused. No alerts will be generated.'}
              </p>
            </CardContent>
          </Card>

          {/* Sensitivity Slider */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Sensitivity</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span className="text-muted-foreground">Level</span>
                  <span className="font-mono font-medium">{sensitivity[0]}%</span>
                </div>
                <Slider
                  value={sensitivity}
                  onValueChange={setSensitivity}
                  max={100}
                  step={1}
                  disabled={!detectionEnabled}
                />
                <div className="flex justify-between text-xs text-muted-foreground">
                  <span>Low</span>
                  <span>High</span>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Manual Recording */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Manual Recording</CardTitle>
            </CardHeader>
            <CardContent>
              <Button
                className="w-full"
                variant={isRecording ? 'destructive' : 'default'}
                onClick={() => setIsRecording(!isRecording)}
                disabled={user?.role !== 'admin'}
              >
                {isRecording ? (
                  <>
                    <Square className="w-4 h-4 mr-2" />
                    Stop Recording
                  </>
                ) : (
                  <>
                    <Play className="w-4 h-4 mr-2" />
                    Start Recording
                  </>
                )}
              </Button>
              {user?.role !== 'admin' && (
                <p className="text-xs text-muted-foreground mt-2 text-center">
                  Admin access required
                </p>
              )}
            </CardContent>
          </Card>
        </div>
      </div>

      {/* System Status */}
      <Card>
        <CardHeader>
          <CardTitle>System Status</CardTitle>
          <CardDescription>Current operational state</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-3">
            {systemStatus.map((item) => {
              const Icon = item.icon;
              return (
                <div
                  key={item.label}
                  className="flex items-center gap-3 p-4 rounded-lg border bg-card"
                >
                  <div className={`p-2 rounded-full ${item.color}`}>
                    <Icon className="w-4 h-4 text-white" />
                  </div>
                  <div>
                    <p className="text-sm font-medium">{item.label}</p>
                    <p className="text-xs text-muted-foreground">{item.status}</p>
                  </div>
                  <CheckCircle2 className="w-5 h-5 text-green-500 ml-auto" />
                </div>
              );
            })}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
