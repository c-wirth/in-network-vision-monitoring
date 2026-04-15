
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

  return (
    <div className="space-y-6">

      {/* Header */}
      <div>
        <h2 className="text-3xl font-bold tracking-tight">Dashboard</h2>
        <p className="text-muted-foreground">
          Real-time monitoring and control center
        </p>
      </div>

      {/* Main Content (single column) */}
      <div className="space-y-6">

        {/* Live Video Feed */}
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle>Live Feed</CardTitle>

              {/* Always LIVE for now */}
              <Badge variant="default" className="animate-pulse">
                LIVE
              </Badge>
            </div>

            <CardDescription>
              Main camera · {formatTime(liveTime)}
            </CardDescription>
          </CardHeader>

          <CardContent>
            <div className="relative aspect-video bg-slate-900 rounded-lg overflow-hidden">

              {/* MJPEG Stream */}
              <img
                src="http://127.0.0.1:8000/stream/mjpeg_stream"
                className="absolute inset-0 w-full h-full object-cover"
              />

              {/* Timestamp */}
              <div className="absolute bottom-4 left-4 bg-black/50 backdrop-blur-sm px-3 py-1 rounded text-xs text-white font-mono">
                {new Date().toLocaleString()}
              </div>

            </div>
          </CardContent>
        </Card>

      </div>
    </div>
  );
}


/*
=========================
DISABLED UI (KEEP FOR LATER)
=========================

--- CONTROLS PANEL ---

<div className="space-y-6">

  <Card>
    <CardHeader>
      <CardTitle className="text-lg">Detection Control</CardTitle>
    </CardHeader>
    <CardContent className="space-y-4">
      <div className="flex items-center justify-between">
        <Label>Detection {detectionEnabled ? 'ON' : 'OFF'}</Label>
        <Switch checked={detectionEnabled} onCheckedChange={setDetectionEnabled} />
      </div>
    </CardContent>
  </Card>

  <Card>
    <CardHeader>
      <CardTitle className="text-lg">Sensitivity</CardTitle>
    </CardHeader>
    <CardContent>
      <Slider value={sensitivity} onValueChange={setSensitivity} />
    </CardContent>
  </Card>

  <Card>
    <CardHeader>
      <CardTitle className="text-lg">Manual Recording</CardTitle>
    </CardHeader>
    <CardContent>
      <Button onClick={() => setIsRecording(!isRecording)}>
        {isRecording ? 'Stop Recording' : 'Start Recording'}
      </Button>
    </CardContent>
  </Card>

</div>

--- SYSTEM STATUS ---

<Card>
  <CardHeader>
    <CardTitle>System Status</CardTitle>
  </CardHeader>
  <CardContent>
    {systemStatus.map((item) => {
      const Icon = item.icon;
      return <Icon key={item.label} />;
    })}
  </CardContent>
</Card>

*/