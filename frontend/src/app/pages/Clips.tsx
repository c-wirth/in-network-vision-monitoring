import { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router';
import { Card, CardContent } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Grid3x3, List, Video } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';

interface Clip {
  id: number;
  url: string;
}

export default function Clips() {
  const { user } = useAuth();
  const [searchParams] = useSearchParams();
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
  const [clips, setClips] = useState<Clip[]>([]);
  const [highlightedClip, setHighlightedClip] = useState<number | null>(null);

  // ------------------------
  // Fetch clips from backend
  // ------------------------
  useEffect(() => {
    const fetchClips = async () => {
      const token = localStorage.getItem("access_token");

      const res = await fetch("http://127.0.0.1:8000/clips", {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (!res.ok) return;

      const data = await res.json();
      setClips(data);
    };

    fetchClips();
  }, []);

  // ------------------------
  // Highlight logic (unchanged)
  // ------------------------
  useEffect(() => {
    const highlight = searchParams.get('highlight');
    if (highlight) {
      setHighlightedClip(Number(highlight));
      setTimeout(() => setHighlightedClip(null), 3000);
    }
  }, [searchParams]);

  return (
    <div className="space-y-6">
      <h2 className="text-3xl font-bold">Clip Archive</h2>

      {/* View Toggle */}
      <div className="flex gap-2">
        <Button onClick={() => setViewMode('grid')}>
          <Grid3x3 />
        </Button>
        <Button onClick={() => setViewMode('list')}>
          <List />
        </Button>
      </div>

      {/* Clips */}
      {clips.length === 0 ? (
        <Card>
          <CardContent className="p-8 text-center">
            <Video className="mx-auto mb-4" />
            <p>No clips found</p>
          </CardContent>
        </Card>
      ) : viewMode === 'grid' ? (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {clips.map((clip) => (
            <Card
              key={clip.id}
              className={highlightedClip === clip.id ? 'ring-2 ring-primary' : ''}
            >
              <CardContent className="p-2">
                <video
                  src={`http://127.0.0.1:8000${clip.url}`}
                  controls
                  className="w-full"
                />
              </CardContent>
            </Card>
          ))}
        </div>
      ) : (
        <div className="space-y-2">
          {clips.map((clip) => (
            <Card key={clip.id}>
              <CardContent className="p-2 flex gap-4 items-center">
                <video
                  src={`http://127.0.0.1:8000${clip.url}`}
                  controls
                  className="w-48"
                />
                <div className="flex-1">
                  <p>Clip ID: {clip.id}</p>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}