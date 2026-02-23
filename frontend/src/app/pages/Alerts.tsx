import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { Button } from '../components/ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { 
  AlertCircle, 
  User, 
  Calendar,
  Filter,
  ExternalLink
} from 'lucide-react';
import { useNavigate } from 'react-router';

interface Alert {
  id: string;
  type: 'motion' | 'person';
  timestamp: Date;
  confidence?: number;
  description: string;
  clipId?: string;
}

// Mock alert data
const MOCK_ALERTS: Alert[] = [
  {
    id: 'a1',
    type: 'person',
    timestamp: new Date(Date.now() - 1000 * 60 * 5),
    confidence: 94,
    description: 'Person detected in main entrance',
    clipId: 'c1',
  },
  {
    id: 'a2',
    type: 'motion',
    timestamp: new Date(Date.now() - 1000 * 60 * 15),
    description: 'Motion detected in parking area',
    clipId: 'c2',
  },
  {
    id: 'a3',
    type: 'person',
    timestamp: new Date(Date.now() - 1000 * 60 * 32),
    confidence: 87,
    description: 'Person detected near loading dock',
    clipId: 'c3',
  },
  {
    id: 'a4',
    type: 'motion',
    timestamp: new Date(Date.now() - 1000 * 60 * 45),
    description: 'Motion detected in warehouse',
    clipId: 'c4',
  },
  {
    id: 'a5',
    type: 'person',
    timestamp: new Date(Date.now() - 1000 * 60 * 67),
    confidence: 92,
    description: 'Person detected at front gate',
    clipId: 'c5',
  },
  {
    id: 'a6',
    type: 'person',
    timestamp: new Date(Date.now() - 1000 * 60 * 120),
    confidence: 78,
    description: 'Person detected in corridor A',
    clipId: 'c6',
  },
  {
    id: 'a7',
    type: 'motion',
    timestamp: new Date(Date.now() - 1000 * 60 * 180),
    description: 'Motion detected in back entrance',
    clipId: 'c7',
  },
];

export default function Alerts() {
  const navigate = useNavigate();
  const [filterType, setFilterType] = useState<string>('all');
  const [searchQuery, setSearchQuery] = useState('');

  const filteredAlerts = MOCK_ALERTS.filter((alert) => {
    const matchesType = filterType === 'all' || alert.type === filterType;
    const matchesSearch = alert.description.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesType && matchesSearch;
  });

  const getRelativeTime = (date: Date) => {
    const minutes = Math.floor((Date.now() - date.getTime()) / (1000 * 60));
    if (minutes < 60) return `${minutes}m ago`;
    const hours = Math.floor(minutes / 60);
    if (hours < 24) return `${hours}h ago`;
    const days = Math.floor(hours / 24);
    return `${days}d ago`;
  };

  const handleViewClip = (clipId: string) => {
    navigate(`/clips?highlight=${clipId}`);
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-3xl font-bold tracking-tight">Alerts & Activity Log</h2>
        <p className="text-muted-foreground">Event history and detection timeline</p>
      </div>

      {/* Filters */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg flex items-center gap-2">
            <Filter className="w-4 h-4" />
            Filters
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-3">
            <div className="space-y-2">
              <Label>Event Type</Label>
              <Select value={filterType} onValueChange={setFilterType}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Events</SelectItem>
                  <SelectItem value="person">Person Detection</SelectItem>
                  <SelectItem value="motion">Motion Only</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2 md:col-span-2">
              <Label>Search</Label>
              <Input
                placeholder="Search by description..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Results Summary */}
      <div className="flex items-center justify-between">
        <p className="text-sm text-muted-foreground">
          Showing {filteredAlerts.length} of {MOCK_ALERTS.length} events
        </p>
      </div>

      {/* Alerts List */}
      <div className="space-y-3">
        {filteredAlerts.map((alert) => (
          <Card key={alert.id} className="hover:shadow-md transition-shadow">
            <CardContent className="p-4">
              <div className="flex items-start gap-4">
                {/* Icon */}
                <div className={`p-2 rounded-full ${
                  alert.type === 'person' ? 'bg-blue-100 dark:bg-blue-900/30' : 'bg-orange-100 dark:bg-orange-900/30'
                }`}>
                  {alert.type === 'person' ? (
                    <User className={`w-5 h-5 ${
                      alert.type === 'person' ? 'text-blue-600 dark:text-blue-400' : 'text-orange-600 dark:text-orange-400'
                    }`} />
                  ) : (
                    <AlertCircle className={`w-5 h-5 ${
                      alert.type === 'person' ? 'text-blue-600 dark:text-blue-400' : 'text-orange-600 dark:text-orange-400'
                    }`} />
                  )}
                </div>

                {/* Content */}
                <div className="flex-1 min-w-0">
                  <div className="flex items-start justify-between gap-2 mb-2">
                    <div>
                      <div className="flex items-center gap-2 mb-1">
                        <Badge variant={alert.type === 'person' ? 'default' : 'secondary'}>
                          {alert.type === 'person' ? 'Person' : 'Motion'}
                        </Badge>
                        {alert.confidence && (
                          <Badge variant="outline" className="font-mono text-xs">
                            {alert.confidence}% confidence
                          </Badge>
                        )}
                      </div>
                      <p className="text-sm font-medium">{alert.description}</p>
                    </div>
                  </div>
                  
                  <div className="flex items-center gap-4 text-xs text-muted-foreground">
                    <span className="flex items-center gap-1">
                      <Calendar className="w-3 h-3" />
                      {alert.timestamp.toLocaleString()}
                    </span>
                    <span>·</span>
                    <span>{getRelativeTime(alert.timestamp)}</span>
                  </div>
                </div>

                {/* Action */}
                {alert.clipId && (
                  <Button 
                    variant="outline" 
                    size="sm"
                    onClick={() => handleViewClip(alert.clipId!)}
                  >
                    <ExternalLink className="w-4 h-4 mr-2" />
                    View Clip
                  </Button>
                )}
              </div>
            </CardContent>
          </Card>
        ))}

        {filteredAlerts.length === 0 && (
          <Card>
            <CardContent className="p-12 text-center">
              <AlertCircle className="w-12 h-12 mx-auto text-muted-foreground mb-4" />
              <p className="text-muted-foreground">No alerts match your filters</p>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
}
