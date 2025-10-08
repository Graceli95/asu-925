import React, { useState } from 'react';
import Link from 'next/link';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Alert, AlertDescription } from './ui/alert';
import { extractYoutubeId, getYoutubeThumbnailUrl } from '../utils/youtube';
import { formatDate } from '../utils/date';
import { Play, Edit, Trash2, Music, ExternalLink } from 'lucide-react';

/**
 * SongCard component for displaying song information
 * @param {Object} props - Component props
 * @param {Object} props.song - Song data
 * @param {Function} props.onEdit - Edit callback
 * @param {Function} props.onDelete - Delete callback
 * @param {Function} props.onPlay - Play callback
 * @param {string} props.youtubeLink - YouTube link (optional)
 */
export function SongCard({ song, onEdit, onDelete, onPlay, youtubeLink }) {
  const [showVideo, setShowVideo] = useState(false);
  
  const youtubeId = youtubeLink ? extractYoutubeId(youtubeLink) : null;
  const thumbnailUrl = youtubeId ? getYoutubeThumbnailUrl(youtubeId) : null;

  const handlePlay = () => {
    if (onPlay) {
      onPlay(song.id);
    }
    setShowVideo(true);
  };

  const handleEdit = () => {
    if (onEdit) {
      onEdit(song);
    }
  };

  const handleDelete = () => {
    if (onDelete) {
      onDelete(song.id);
    }
  };

  return (
    <Card className="w-full max-w-sm">
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <Link href={`/songs/${song.id}`}>
              <CardTitle className="text-lg leading-tight hover:text-primary cursor-pointer transition-colors">
                {song.title}
              </CardTitle>
            </Link>
            <p className="text-sm text-muted-foreground mt-1">{song.artist}</p>
          </div>
          <div className="flex gap-1">
            <Button
              variant="ghost"
              size="icon"
              onClick={handleEdit}
              className="h-8 w-8"
            >
              <Edit className="h-4 w-4" />
            </Button>
            <Button
              variant="ghost"
              size="icon"
              onClick={handleDelete}
              className="h-8 w-8 text-destructive hover:text-destructive"
            >
              <Trash2 className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </CardHeader>
      
      <CardContent className="pt-0">
        <div className="space-y-3">
          {/* Song Details */}
          <div className="space-y-1 text-sm">
            {song.genre && (
              <div className="flex items-center gap-2">
                <Music className="h-4 w-4 text-muted-foreground" />
                <span className="text-muted-foreground">{song.genre}</span>
              </div>
            )}
            {song.year && (
              <div className="text-muted-foreground">
                Released: {song.year}
              </div>
            )}
            <div className="text-muted-foreground">
              Added: {formatDate(song.created_at)}
            </div>
          </div>

          {/* YouTube Thumbnail/Video */}
          {youtubeId && (
            <div className="space-y-2">
              {showVideo ? (
                <div className="aspect-video w-full">
                  <iframe
                    src={`https://www.youtube.com/embed/${youtubeId}`}
                    title={`${song.title} by ${song.artist}`}
                    className="w-full h-full rounded-md"
                    allowFullScreen
                  />
                </div>
              ) : (
                <div className="relative aspect-video w-full">
                  <img
                    src={thumbnailUrl}
                    alt={`${song.title} thumbnail`}
                    className="w-full h-full object-cover rounded-md"
                  />
                  <Button
                    onClick={handlePlay}
                    className="absolute inset-0 m-auto h-12 w-12 rounded-full"
                    size="icon"
                  >
                    <Play className="h-6 w-6 ml-1" />
                  </Button>
                </div>
              )}
            </div>
          )}

          {/* Action Buttons */}
          <div className="flex gap-2">
            <Link href={`/songs/${song.id}`} className="flex-1">
              <Button
                variant="outline"
                size="sm"
                className="w-full"
              >
                <ExternalLink className="h-4 w-4 mr-2" />
                View Details
              </Button>
            </Link>
            <Button
              onClick={handlePlay}
              variant="outline"
              size="sm"
              className="flex-1"
            >
              <Play className="h-4 w-4 mr-2" />
              Play
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
