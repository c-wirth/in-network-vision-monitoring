import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { Progress } from '../components/ui/progress';
import { 
  Video, 
  Cpu, 
  HardDrive, 
  Mail,
  Activity,
  Clock,
  Gauge,
  CheckCircle2,
  AlertCircle,
  Signal
} from 'lucide-react';

interface SystemMetric {
  label: string;
  value: string;
  status: 'healthy' | 'warning' | 'error';
  icon: React.ElementType;
  description?: string;
}

export default function Status() {
  const [fps, setFps] = useState(30);
  const [inferenceTime, setInferenceTime] = useState(45);
  const [uptime, setUptime] = useState(0);

  // Simulate real-time metrics
  useEffect(() => {
    const interval = setInterval(() => {
      setFps(28 + Math.random() * 4);
      setInferenceTime(40 + Math.random() * 15);
      setUptime((prev) => prev + 1);
    }, 1000);
    return () => clearInterval(interval);
  }, []);

  const formatUptime = (seconds: number) => {
    const days = Math.floor(seconds / (3600 * 24));
    const hours = Math.floor((seconds % (3600 * 24)) / 3600);
    const mins = Math.floor((seconds % 3600) / 60);
    return `${days}d ${hours}h ${mins}m`;
  };

  const systemMetrics: SystemMetric[] = [
    {
      label: 'Camera Connection',
      value: 'Connected',
      status: 'healthy',
      icon: Video,
      description: 'RTSP stream active',
    },
    {
      label: 'Last Heartbeat',
      value: '2s ago',
      status: 'healthy',
      icon: Activity,
      description: 'Real-time monitoring',
    },
    {
      label: 'AI Inference',
      value: `${inferenceTime.toFixed(1)}ms`,
      status: inferenceTime > 50 ? 'warning' : 'healthy',
      icon: Cpu,
      description: 'Model: YOLOv8',
    },
    {
      label: 'Frame Rate',
      value: `${fps.toFixed(1)} FPS`,
      status: fps < 25 ? 'warning' : 'healthy',
      icon: Gauge,
      description: 'Target: 30 FPS',
    },
    {
      label: 'Storage Health',
      value: '78% Free',
      status: 'healthy',
      icon: HardDrive,
      description: '234 GB available',
    },
    {
      label: 'Email Service',
      value: 'Operational',
      status: 'healthy',
      icon: Mail,
      description: 'SMTP configured',
    },
  ];

  const storageMetrics = {
    total: 1000,
    used: 220,
    clips: 180,
    logs: 25,
    cache: 15,
  };

  const networkMetrics = {
    latency: 12,
    bandwidth: 8.5,
    packetsLost: 0.02,
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-3xl font-bold tracking-tight">System Status</h2>
        <p className="text-muted-foreground">Diagnostics and health monitoring</p>
      </div>

      {/* System Uptime */}
      <Card>
        <CardContent className="p-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="p-3 bg-green-100 dark:bg-green-900/30 rounded-full">
                <CheckCircle2 className="w-6 h-6 text-green-600 dark:text-green-400" />
              </div>
              <div>
                <p className="text-2xl font-bold">{formatUptime(uptime)}</p>
                <p className="text-sm text-muted-foreground">System Uptime</p>
              </div>
            </div>
            <Badge variant="default" className="bg-green-600">
              All Systems Operational
            </Badge>
          </div>
        </CardContent>
      </Card>

      {/* Core Metrics */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {systemMetrics.map((metric) => {
          const Icon = metric.icon;
          return (
            <Card key={metric.label}>
              <CardContent className="p-6">
                <div className="flex items-start justify-between mb-4">
                  <div className={`p-2 rounded-lg ${
                    metric.status === 'healthy' 
                      ? 'bg-green-100 dark:bg-green-900/30' 
                      : metric.status === 'warning'
                      ? 'bg-yellow-100 dark:bg-yellow-900/30'
                      : 'bg-red-100 dark:bg-red-900/30'
                  }`}>
                    <Icon className={`w-5 h-5 ${
                      metric.status === 'healthy' 
                        ? 'text-green-600 dark:text-green-400' 
                        : metric.status === 'warning'
                        ? 'text-yellow-600 dark:text-yellow-400'
                        : 'text-red-600 dark:text-red-400'
                    }`} />
                  </div>
                  {metric.status === 'healthy' ? (
                    <CheckCircle2 className="w-5 h-5 text-green-500" />
                  ) : metric.status === 'warning' ? (
                    <AlertCircle className="w-5 h-5 text-yellow-500" />
                  ) : (
                    <AlertCircle className="w-5 h-5 text-red-500" />
                  )}
                </div>
                <p className="text-sm font-medium text-muted-foreground mb-1">
                  {metric.label}
                </p>
                <p className="text-2xl font-bold mb-1">{metric.value}</p>
                {metric.description && (
                  <p className="text-xs text-muted-foreground">{metric.description}</p>
                )}
              </CardContent>
            </Card>
          );
        })}
      </div>

      {/* Storage Details */}
      <Card>
        <CardHeader>
          <CardTitle>Storage Breakdown</CardTitle>
          <CardDescription>Disk usage by category</CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span className="font-medium">Total Usage</span>
              <span className="text-muted-foreground">
                {storageMetrics.used} GB / {storageMetrics.total} GB
              </span>
            </div>
            <Progress value={(storageMetrics.used / storageMetrics.total) * 100} />
          </div>

          <div className="grid gap-4 md:grid-cols-3">
            <div className="space-y-1">
              <div className="flex items-center justify-between">
                <span className="text-sm text-muted-foreground">Video Clips</span>
                <span className="text-sm font-mono">{storageMetrics.clips} GB</span>
              </div>
              <Progress value={(storageMetrics.clips / storageMetrics.total) * 100} className="h-2" />
            </div>
            <div className="space-y-1">
              <div className="flex items-center justify-between">
                <span className="text-sm text-muted-foreground">System Logs</span>
                <span className="text-sm font-mono">{storageMetrics.logs} GB</span>
              </div>
              <Progress value={(storageMetrics.logs / storageMetrics.total) * 100} className="h-2" />
            </div>
            <div className="space-y-1">
              <div className="flex items-center justify-between">
                <span className="text-sm text-muted-foreground">Cache</span>
                <span className="text-sm font-mono">{storageMetrics.cache} GB</span>
              </div>
              <Progress value={(storageMetrics.cache / storageMetrics.total) * 100} className="h-2" />
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Network Performance */}
      <Card>
        <CardHeader>
          <CardTitle>Network Performance</CardTitle>
          <CardDescription>Camera stream and connectivity metrics</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid gap-6 md:grid-cols-3">
            <div className="space-y-2">
              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                <Signal className="w-4 h-4" />
                Latency
              </div>
              <p className="text-3xl font-bold">{networkMetrics.latency}ms</p>
              <Progress value={100 - networkMetrics.latency} className="h-1" />
              <p className="text-xs text-muted-foreground">Excellent</p>
            </div>
            <div className="space-y-2">
              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                <Activity className="w-4 h-4" />
                Bandwidth
              </div>
              <p className="text-3xl font-bold">{networkMetrics.bandwidth} Mbps</p>
              <Progress value={(networkMetrics.bandwidth / 10) * 100} className="h-1" />
              <p className="text-xs text-muted-foreground">Stable stream</p>
            </div>
            <div className="space-y-2">
              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                <AlertCircle className="w-4 h-4" />
                Packet Loss
              </div>
              <p className="text-3xl font-bold">{networkMetrics.packetsLost}%</p>
              <Progress value={networkMetrics.packetsLost * 10} className="h-1" />
              <p className="text-xs text-muted-foreground">Negligible</p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* AI Model Info */}
      <Card>
        <CardHeader>
          <CardTitle>AI Detection Engine</CardTitle>
          <CardDescription>Model information and performance</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-2">
            <div className="space-y-3">
              <div className="flex justify-between text-sm">
                <span className="text-muted-foreground">Model Architecture</span>
                <span className="font-mono">YOLOv8n</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-muted-foreground">Input Resolution</span>
                <span className="font-mono">640x640</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-muted-foreground">Classes Detected</span>
                <span className="font-mono">80 objects</span>
              </div>
            </div>
            <div className="space-y-3">
              <div className="flex justify-between text-sm">
                <span className="text-muted-foreground">Avg Inference Time</span>
                <span className="font-mono">{inferenceTime.toFixed(1)}ms</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-muted-foreground">Detection Threshold</span>
                <span className="font-mono">0.65</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-muted-foreground">GPU Acceleration</span>
                <span className="font-mono">Enabled (CUDA)</span>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
