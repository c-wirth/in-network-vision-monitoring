import { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { Button } from '../components/ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { 
  Play, 
  Download, 
  Trash2, 
  Grid3x3, 
  List,
  Video,
  Calendar,
  AlertCircle
} from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '../components/ui/alert-dialog';

interface Clip {
  id: string;
  timestamp: Date;
  duration: number;
  triggerType: 'motion' | 'person' | 'manual';
  confidence?: number;
  thumbnail: string;
  size: string;
}

// Mock clip data
const MOCK_CLIPS: Clip[] = [
  {
    id: 'c1',
    timestamp: new Date(Date.now() - 1000 * 60 * 5),
    duration: 45,
    triggerType: 'person',
    confidence: 94,
    thumbnail: '🎥',
    size: '12.3 MB',
  },
  {
    id: 'c2',
    timestamp: new Date(Date.now() - 1000 * 60 * 15),
    duration: 30,
    triggerType: 'motion',
    thumbnail: '🎥',
    size: '8.1 MB',
  },
  {
    id: 'c3',
    timestamp: new Date(Date.now() - 1000 * 60 * 32),
    duration: 60,
    triggerType: 'person',
    confidence: 87,
    thumbnail: '🎥',
    size: '15.7 MB',
  },
  {
    id: 'c4',
    timestamp: new Date(Date.now() - 1000 * 60 * 45),
    duration: 25,
    triggerType: 'motion',
    thumbnail: '🎥',
    size: '6.4 MB',
  },
  {
    id: 'c5',
    timestamp: new Date(Date.now() - 1000 * 60 * 67),
    duration: 90,
    triggerType: 'manual',
    thumbnail: '🎥',
    size: '22.1 MB',
  },
  {
    id: 'c6',
    timestamp: new Date(Date.now() - 1000 * 60 * 120),
    duration: 40,
    triggerType: 'person',
    confidence: 78,
    thumbnail: '🎥',
    size: '10.9 MB',
  },
];

export default function Clips() {
  const { user } = useAuth();
  const [searchParams] = useSearchParams();
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
  const [filterType, setFilterType] = useState<string>('all');
  const [deleteClipId, setDeleteClipId] = useState<string | null>(null);
  const [highlightedClip, setHighlightedClip] = useState<string | null>(null);

  useEffect(() => {
    const highlight = searchParams.get('highlight');
    if (highlight) {
      setHighlightedClip(highlight);
      setTimeout(() => setHighlightedClip(null), 3000);
    }
  }, [searchParams]);

  const filteredClips = MOCK_CLIPS.filter((clip) => {
    return filterType === 'all' || clip.triggerType === filterType;
  });

  const handleDelete = (clipId: string) => {
    // Simulate delete
    console.log('Deleting clip:', clipId);
    setDeleteClipId(null);
  };

  const formatDuration = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-3xl font-bold tracking-tight">Clip Archive</h2>
        <p className="text-muted-foreground">Video recording management</p>
      </div>

      {/* Controls */}
      <Card>
        <CardContent className="p-4">
          <div className="flex items-center justify-between gap-4">
            <div className="flex items-center gap-4">
              <Select value={filterType} onValueChange={setFilterType}>
                <SelectTrigger className="w-[180px]">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Clips</SelectItem>
                  <SelectItem value="person">Person Detection</SelectItem>
                  <SelectItem value="motion">Motion Detection</SelectItem>
                  <SelectItem value="manual">Manual Recording</SelectItem>
                </SelectContent>
              </Select>
              <p className="text-sm text-muted-foreground">
                {filteredClips.length} clips
              </p>
            </div>

            <div className="flex items-center gap-2">
              <Button
                variant={viewMode === 'grid' ? 'default' : 'outline'}
                size="sm"
                onClick={() => setViewMode('grid')}
              >
                <Grid3x3 className="w-4 h-4" />
              </Button>
              <Button
                variant={viewMode === 'list' ? 'default' : 'outline'}
                size="sm"
                onClick={() => setViewMode('list')}
              >
                <List className="w-4 h-4" />
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Clips Grid/List */}
      {viewMode === 'grid' ? (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {filteredClips.map((clip) => (
            <Card 
              key={clip.id}
              className={`overflow-hidden transition-all ${
                highlightedClip === clip.id ? 'ring-2 ring-primary animate-pulse' : ''
              }`}
            >
              {/* Thumbnail */}
              <div className="relative aspect-video bg-slate-900 flex items-center justify-center">
                <Video className="w-16 h-16 text-slate-700" />
                <div className="absolute bottom-2 right-2 bg-black/70 backdrop-blur-sm px-2 py-1 rounded text-xs text-white font-mono">
                  {formatDuration(clip.duration)}
                </div>
                <Badge 
                  className="absolute top-2 left-2"
                  variant={clip.triggerType === 'person' ? 'default' : clip.triggerType === 'motion' ? 'secondary' : 'outline'}
                >
                  {clip.triggerType}
                </Badge>
              </div>

              <CardContent className="p-4 space-y-3">
                <div className="space-y-1">
                  <div className="flex items-center gap-2 text-xs text-muted-foreground">
                    <Calendar className="w-3 h-3" />
                    {clip.timestamp.toLocaleString()}
                  </div>
                  {clip.confidence && (
                    <Badge variant="outline" className="text-xs font-mono">
                      {clip.confidence}% confidence
                    </Badge>
                  )}
                  <p className="text-xs text-muted-foreground">{clip.size}</p>
                </div>

                <div className="flex gap-2">
                  <Button size="sm" className="flex-1">
                    <Play className="w-3 h-3 mr-1" />
                    Play
                  </Button>
                  <Button size="sm" variant="outline">
                    <Download className="w-3 h-3" />
                  </Button>
                  {user?.role === 'admin' && (
                    <Button 
                      size="sm" 
                      variant="outline"
                      onClick={() => setDeleteClipId(clip.id)}
                    >
                      <Trash2 className="w-3 h-3 text-destructive" />
                    </Button>
                  )}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      ) : (
        <div className="space-y-2">
          {filteredClips.map((clip) => (
            <Card 
              key={clip.id}
              className={`transition-all ${
                highlightedClip === clip.id ? 'ring-2 ring-primary' : ''
              }`}
            >
              <CardContent className="p-4">
                <div className="flex items-center gap-4">
                  <div className="w-32 h-20 bg-slate-900 rounded flex items-center justify-center flex-shrink-0">
                    <Video className="w-8 h-8 text-slate-700" />
                  </div>
                  
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <Badge 
                        variant={clip.triggerType === 'person' ? 'default' : clip.triggerType === 'motion' ? 'secondary' : 'outline'}
                      >
                        {clip.triggerType}
                      </Badge>
                      {clip.confidence && (
                        <Badge variant="outline" className="text-xs font-mono">
                          {clip.confidence}%
                        </Badge>
                      )}
                    </div>
                    <p className="text-sm text-muted-foreground">
                      {clip.timestamp.toLocaleString()} · {formatDuration(clip.duration)} · {clip.size}
                    </p>
                  </div>

                  <div className="flex items-center gap-2">
                    <Button size="sm">
                      <Play className="w-4 h-4 mr-2" />
                      Play
                    </Button>
                    <Button size="sm" variant="outline">
                      <Download className="w-4 h-4" />
                    </Button>
                    {user?.role === 'admin' && (
                      <Button 
                        size="sm" 
                        variant="outline"
                        onClick={() => setDeleteClipId(clip.id)}
                      >
                        <Trash2 className="w-4 h-4 text-destructive" />
                      </Button>
                    )}
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* Delete Confirmation Dialog */}
      <AlertDialog open={deleteClipId !== null} onOpenChange={() => setDeleteClipId(null)}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Delete Clip?</AlertDialogTitle>
            <AlertDialogDescription>
              This action cannot be undone. The clip will be permanently removed from storage.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction 
              className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
              onClick={() => deleteClipId && handleDelete(deleteClipId)}
            >
              Delete
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>

      {filteredClips.length === 0 && (
        <Card>
          <CardContent className="p-12 text-center">
            <Video className="w-12 h-12 mx-auto text-muted-foreground mb-4" />
            <p className="text-muted-foreground">No clips found</p>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
