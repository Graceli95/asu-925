import React, { useState } from 'react';
import { Card, CardContent } from './ui/card';
import { Button } from './ui/button';
import { Alert, AlertDescription } from './ui/alert';
import { extractYoutubeId } from '../utils/youtube';
import { Play, Pause, Volume2, VolumeX, Maximize } from 'lucide-react';

/**
 * YouTubePlayer component for embedding YouTube videos
 * @param {Object} props - Component props
 * @param {string} props.youtubeLink - YouTube URL
 * @param {string} props.title - Video title
 * @param {boolean} props.autoplay - Auto-play video
 * @param {boolean} props.showControls - Show player controls
 */
export function YouTubePlayer({ youtubeLink, title = "Video", autoplay = false, showControls = true }) {
  const [isPlaying, setIsPlaying] = useState(false);
  const [isMuted, setIsMuted] = useState(false);
  const [player, setPlayer] = useState(null);

  const youtubeId = extractYoutubeId(youtubeLink);

  if (!youtubeId) {
    return (
      <Alert>
        <AlertDescription>
          Invalid YouTube URL. Please check the link and try again.
        </AlertDescription>
      </Alert>
    );
  }

  const handlePlayerReady = (event) => {
    setPlayer(event.target);
  };

  const handlePlay = () => {
    if (player) {
      if (isPlaying) {
        player.pauseVideo();
      } else {
        player.playVideo();
      }
      setIsPlaying(!isPlaying);
    }
  };

  const handleMute = () => {
    if (player) {
      if (isMuted) {
        player.unMute();
      } else {
        player.mute();
      }
      setIsMuted(!isMuted);
    }
  };

  const handleFullscreen = () => {
    if (player) {
      player.requestFullscreen();
    }
  };

  return (
    <Card className="w-full">
      <CardContent className="p-0">
        <div className="relative aspect-video bg-black rounded-lg overflow-hidden">
          <iframe
            src={`https://www.youtube.com/embed/${youtubeId}?enablejsapi=1&autoplay=${autoplay ? 1 : 0}&controls=${showControls ? 1 : 0}`}
            title={title}
            className="w-full h-full"
            allowFullScreen
            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
            onLoad={() => console.log('YouTube iframe loaded')}
          />
          
          {/* Custom Controls Overlay */}
          {showControls && (
            <div className="absolute bottom-4 left-4 right-4 flex items-center justify-between bg-black/50 backdrop-blur-sm rounded-lg p-2">
              <div className="flex items-center gap-2">
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={handlePlay}
                  className="h-8 w-8 text-white hover:bg-white/20"
                >
                  {isPlaying ? (
                    <Pause className="h-4 w-4" />
                  ) : (
                    <Play className="h-4 w-4" />
                  )}
                </Button>
                
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={handleMute}
                  className="h-8 w-8 text-white hover:bg-white/20"
                >
                  {isMuted ? (
                    <VolumeX className="h-4 w-4" />
                  ) : (
                    <Volume2 className="h-4 w-4" />
                  )}
                </Button>
              </div>
              
              <Button
                variant="ghost"
                size="icon"
                onClick={handleFullscreen}
                className="h-8 w-8 text-white hover:bg-white/20"
              >
                <Maximize className="h-4 w-4" />
              </Button>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
