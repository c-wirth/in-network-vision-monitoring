import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Slider } from '../components/ui/slider';
import { Switch } from '../components/ui/switch';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { Badge } from '../components/ui/badge';
import { useAuth } from '../contexts/AuthContext';
import { 
  Settings as SettingsIcon, 
  Bell, 
  Mail, 
  Shield,
  Save,
  AlertCircle
} from 'lucide-react';
import { toast } from 'sonner';

export default function Settings() {
  const { user } = useAuth();
  const [sensitivity, setSensitivity] = useState([75]);
  const [minConfidence, setMinConfidence] = useState([65]);
  const [alertCooldown, setAlertCooldown] = useState('60');
  const [emailEnabled, setEmailEnabled] = useState(true);
  const [emailAddress, setEmailAddress] = useState('admin@example.com');
  const [smtpServer, setSmtpServer] = useState('smtp.gmail.com');
  const [smtpPort, setSmtpPort] = useState('587');

  const handleSave = () => {
    toast.success('Settings saved successfully');
  };

  const isAdmin = user?.role === 'admin';

  return (
    <div className="space-y-6 max-w-4xl">
      <div>
        <h2 className="text-3xl font-bold tracking-tight">Settings</h2>
        <p className="text-muted-foreground">Configure system behavior and preferences</p>
      </div>

      {!isAdmin && (
        <Card className="border-yellow-500/50 bg-yellow-50 dark:bg-yellow-900/10">
          <CardContent className="p-4 flex items-start gap-3">
            <AlertCircle className="w-5 h-5 text-yellow-600 dark:text-yellow-500 mt-0.5" />
            <div>
              <p className="font-medium text-yellow-900 dark:text-yellow-100">View Only Mode</p>
              <p className="text-sm text-yellow-800 dark:text-yellow-200">
                You're viewing as a viewer. Admin access required to modify settings.
              </p>
            </div>
          </CardContent>
        </Card>
      )}

      <Tabs defaultValue="detection" className="space-y-6">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="detection">
            <SettingsIcon className="w-4 h-4 mr-2" />
            Detection
          </TabsTrigger>
          <TabsTrigger value="alerts">
            <Bell className="w-4 h-4 mr-2" />
            Alerts
          </TabsTrigger>
          <TabsTrigger value="email">
            <Mail className="w-4 h-4 mr-2" />
            Email
          </TabsTrigger>
          <TabsTrigger value="access">
            <Shield className="w-4 h-4 mr-2" />
            Access
          </TabsTrigger>
        </TabsList>

        {/* Detection Settings */}
        <TabsContent value="detection" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Detection Sensitivity</CardTitle>
              <CardDescription>
                Adjust how sensitive the motion and person detection should be
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="space-y-4">
                <div>
                  <div className="flex justify-between mb-2">
                    <Label>Motion Sensitivity</Label>
                    <span className="text-sm font-mono">{sensitivity[0]}%</span>
                  </div>
                  <Slider
                    value={sensitivity}
                    onValueChange={setSensitivity}
                    max={100}
                    step={1}
                    disabled={!isAdmin}
                  />
                  <p className="text-xs text-muted-foreground mt-2">
                    Higher values = more sensitive (more detections)
                  </p>
                </div>

                <div>
                  <div className="flex justify-between mb-2">
                    <Label>Minimum Confidence</Label>
                    <span className="text-sm font-mono">{minConfidence[0]}%</span>
                  </div>
                  <Slider
                    value={minConfidence}
                    onValueChange={setMinConfidence}
                    max={100}
                    step={5}
                    disabled={!isAdmin}
                  />
                  <p className="text-xs text-muted-foreground mt-2">
                    Only trigger alerts above this confidence level
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Detection Zones</CardTitle>
              <CardDescription>
                Configure specific areas to monitor (Future feature)
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-center py-8 text-muted-foreground">
                <p className="text-sm">Zone configuration coming soon</p>
                <p className="text-xs mt-1">Draw custom detection areas on the video feed</p>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Alert Settings */}
        <TabsContent value="alerts" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Alert Frequency</CardTitle>
              <CardDescription>
                Control how often alerts are generated
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="cooldown">Alert Cooldown Period</Label>
                <Select value={alertCooldown} onValueChange={setAlertCooldown} disabled={!isAdmin}>
                  <SelectTrigger id="cooldown">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="0">No cooldown</SelectItem>
                    <SelectItem value="30">30 seconds</SelectItem>
                    <SelectItem value="60">1 minute</SelectItem>
                    <SelectItem value="300">5 minutes</SelectItem>
                    <SelectItem value="600">10 minutes</SelectItem>
                  </SelectContent>
                </Select>
                <p className="text-xs text-muted-foreground">
                  Prevent duplicate alerts within this time window
                </p>
              </div>

              <div className="flex items-center justify-between p-4 border rounded-lg">
                <div className="space-y-0.5">
                  <Label>Person Detection Alerts</Label>
                  <p className="text-xs text-muted-foreground">
                    Send alerts when a person is detected
                  </p>
                </div>
                <Switch defaultChecked disabled={!isAdmin} />
              </div>

              <div className="flex items-center justify-between p-4 border rounded-lg">
                <div className="space-y-0.5">
                  <Label>Motion Detection Alerts</Label>
                  <p className="text-xs text-muted-foreground">
                    Send alerts for general motion events
                  </p>
                </div>
                <Switch defaultChecked disabled={!isAdmin} />
              </div>

              <div className="flex items-center justify-between p-4 border rounded-lg">
                <div className="space-y-0.5">
                  <Label>Night Mode Alerts</Label>
                  <p className="text-xs text-muted-foreground">
                    Separate alert rules for nighttime (8PM-6AM)
                  </p>
                </div>
                <Switch disabled={!isAdmin} />
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Email Settings */}
        <TabsContent value="email" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Email Notifications</CardTitle>
              <CardDescription>
                Configure email alerts for detection events
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between p-4 border rounded-lg">
                <div className="space-y-0.5">
                  <Label>Enable Email Alerts</Label>
                  <p className="text-xs text-muted-foreground">
                    Send email notifications for events
                  </p>
                </div>
                <Switch 
                  checked={emailEnabled} 
                  onCheckedChange={setEmailEnabled}
                  disabled={!isAdmin}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="email">Recipient Email</Label>
                <Input
                  id="email"
                  type="email"
                  value={emailAddress}
                  onChange={(e) => setEmailAddress(e.target.value)}
                  placeholder="admin@example.com"
                  disabled={!isAdmin || !emailEnabled}
                />
              </div>

              <div className="grid gap-4 md:grid-cols-2">
                <div className="space-y-2">
                  <Label htmlFor="smtp">SMTP Server</Label>
                  <Input
                    id="smtp"
                    value={smtpServer}
                    onChange={(e) => setSmtpServer(e.target.value)}
                    placeholder="smtp.gmail.com"
                    disabled={!isAdmin || !emailEnabled}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="port">Port</Label>
                  <Input
                    id="port"
                    value={smtpPort}
                    onChange={(e) => setSmtpPort(e.target.value)}
                    placeholder="587"
                    disabled={!isAdmin || !emailEnabled}
                  />
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="smtp-user">SMTP Username</Label>
                <Input
                  id="smtp-user"
                  placeholder="your-email@gmail.com"
                  disabled={!isAdmin || !emailEnabled}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="smtp-pass">SMTP Password / App Password</Label>
                <Input
                  id="smtp-pass"
                  type="password"
                  placeholder="••••••••••••••••"
                  disabled={!isAdmin || !emailEnabled}
                />
              </div>

              {isAdmin && emailEnabled && (
                <Button variant="outline" className="w-full">
                  <Mail className="w-4 h-4 mr-2" />
                  Send Test Email
                </Button>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Access Control */}
        <TabsContent value="access" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Role-Based Access</CardTitle>
              <CardDescription>
                Manage user permissions and access levels
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-3">
                <div className="flex items-center justify-between p-4 border rounded-lg">
                  <div className="flex items-center gap-3">
                    <div>
                      <p className="font-medium">admin</p>
                      <p className="text-xs text-muted-foreground">Full system access</p>
                    </div>
                  </div>
                  <Badge>Admin</Badge>
                </div>

                <div className="flex items-center justify-between p-4 border rounded-lg">
                  <div className="flex items-center gap-3">
                    <div>
                      <p className="font-medium">viewer</p>
                      <p className="text-xs text-muted-foreground">Read-only access</p>
                    </div>
                  </div>
                  <Badge variant="secondary">Viewer</Badge>
                </div>
              </div>

              <div className="p-4 bg-slate-50 dark:bg-slate-900 rounded-lg border">
                <p className="text-sm font-medium mb-2">Permission Levels</p>
                <div className="space-y-1 text-xs text-muted-foreground">
                  <p>• <strong>Admin:</strong> Full control, settings, delete clips, manual recording</p>
                  <p>• <strong>Viewer:</strong> View live feed, alerts, and clips only</p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Security Settings</CardTitle>
              <CardDescription>
                Future encryption and security features
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-center py-8 text-muted-foreground">
                <Shield className="w-12 h-12 mx-auto mb-3 opacity-50" />
                <p className="text-sm">End-to-end encryption coming soon</p>
                <p className="text-xs mt-1">Secure video streams and stored footage</p>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Save Button */}
      {isAdmin && (
        <div className="flex justify-end pt-4 border-t">
          <Button onClick={handleSave} size="lg">
            <Save className="w-4 h-4 mr-2" />
            Save Settings
          </Button>
        </div>
      )}
    </div>
  );
}
