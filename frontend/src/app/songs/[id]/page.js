'use client';

import React, { useState, useEffect } from 'react';
import { useRouter, useParams } from 'next/navigation';
import { MainLayout } from '../../../layouts/MainLayout';
import { Button } from '../../../components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '../../../components/ui/card';
import { Alert, AlertDescription } from '../../../components/ui/alert';
import { useAuth } from '../../../context/AuthContext';
import { songService } from '../../../services/songService';
import { YouTubePlayer } from '../../../components/songs/YouTubePlayer';
import { SongForm } from '../../../components/songs/SongForm';
import { formatDate } from '../../../utils/date';
import { extractYoutubeId } from '../../../utils/youtube';
import { ArrowLeft, Edit, Trash2, Play, Music, Calendar, User } from 'lucide-react';

/**
 * Dynamic song detail page
 * Route: /songs/[id]
 */
export default function SongDetailPage() {
  const router = useRouter();
  const params = useParams();
  const { user, isAuthenticated, loading: authLoading } = useAuth();
  
  const [song, setSong] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showEditForm, setShowEditForm] = useState(false);
  const [youtubeLink, setYoutubeLink] = useState('');

  const songId = params.id;

  // Redirect if not authenticated
  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      router.push('/login');
    }
  }, [isAuthenticated, authLoading, router]);

  // Fetch song details
  useEffect(() => {
    if (songId && isAuthenticated) {
      fetchSong();
    }
  }, [songId, isAuthenticated]);

  // Load YouTube link from song data
  useEffect(() => {
    if (song && song.youtube_link) {
      setYoutubeLink(song.youtube_link);
    }
  }, [song]);

  const fetchSong = async () => {
    try {
      setLoading(true);
      setError(null);
      const songData = await songService.getSongById(songId);
      setSong(songData);
    } catch (error) {
      setError(error.message);
      console.error('Error fetching song:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleEdit = () => {
    setShowEditForm(true);
  };

  const handleDelete = async () => {
    if (window.confirm('Are you sure you want to delete this song?')) {
      try {
        await songService.deleteSong(songId);
        router.push('/songs');
      } catch (error) {
        setError(error.message);
        console.error('Error deleting song:', error);
      }
    }
  };

  const handlePlay = async () => {
    try {
      await songService.playSong(songId);
    } catch (error) {
      console.error('Error playing song:', error);
    }
  };

  const handleFormSubmit = async (songData) => {
    try {
      await songService.updateSong(songId, songData);
      
      setShowEditForm(false);
      await fetchSong(); // Refresh song data
    } catch (error) {
      setError(error.message);
      console.error('Error updating song:', error);
    }
  };

  const handleFormCancel = () => {
    setShowEditForm(false);
  };

  if (authLoading || loading) {
    return (
      <MainLayout>
        <div className="flex items-center justify-center min-h-[400px]">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
        </div>
      </MainLayout>
    );
  }

  if (!isAuthenticated) {
    return null; // Will redirect
  }

  if (error) {
    return (
      <MainLayout>
        <div className="space-y-4">
          <Button 
            variant="outline" 
            onClick={() => router.back()}
            className="flex items-center gap-2"
          >
            <ArrowLeft className="h-4 w-4" />
            Go Back
          </Button>
          <Alert variant="destructive">
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        </div>
      </MainLayout>
    );
  }

  if (!song) {
    return (
      <MainLayout>
        <div className="text-center py-12">
          <h1 className="text-2xl font-bold mb-4">Song Not Found</h1>
          <p className="text-muted-foreground mb-4">
            The song you're looking for doesn't exist or you don't have permission to view it.
          </p>
          <Button onClick={() => router.push('/songs')}>
            Back to Songs
          </Button>
        </div>
      </MainLayout>
    );
  }

  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <Button 
            variant="outline" 
            onClick={() => router.back()}
            className="flex items-center gap-2"
          >
            <ArrowLeft className="h-4 w-4" />
            Go Back
          </Button>
          
          <div className="flex gap-2">
            <Button
              variant="outline"
              onClick={handleEdit}
              className="flex items-center gap-2"
            >
              <Edit className="h-4 w-4" />
              Edit
            </Button>
            {user && song && user.username === song.user && (
              <Button
                variant="outline"
                onClick={handleDelete}
                className="flex items-center gap-2 text-destructive hover:text-destructive"
              >
                <Trash2 className="h-4 w-4" />
                Delete
              </Button>
            )}
          </div>
        </div>

        {/* Song Details */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Song Information */}
          <div className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-2xl">
                  <Music className="h-6 w-6" />
                  {song.title}
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-3">
                  <div className="flex items-center gap-2">
                    <User className="h-4 w-4 text-muted-foreground" />
                    <span className="font-medium">Artist:</span>
                    <span>{song.artist}</span>
                  </div>
                  
                  {song.genre && (
                    <div className="flex items-center gap-2">
                      <Music className="h-4 w-4 text-muted-foreground" />
                      <span className="font-medium">Genre:</span>
                      <span>{song.genre}</span>
                    </div>
                  )}
                  
                  {song.year && (
                    <div className="flex items-center gap-2">
                      <Calendar className="h-4 w-4 text-muted-foreground" />
                      <span className="font-medium">Year:</span>
                      <span>{song.year}</span>
                    </div>
                  )}
                  
                  <div className="flex items-center gap-2">
                    <Calendar className="h-4 w-4 text-muted-foreground" />
                    <span className="font-medium">Added:</span>
                    <span>{formatDate(song.created_at)}</span>
                  </div>
                  
                  {song.updated_at && (
                    <div className="flex items-center gap-2">
                      <Calendar className="h-4 w-4 text-muted-foreground" />
                      <span className="font-medium">Updated:</span>
                      <span>{formatDate(song.updated_at)}</span>
                    </div>
                  )}
                </div>

                <div className="pt-4">
                  <Button
                    onClick={handlePlay}
                    className="w-full flex items-center gap-2"
                  >
                    <Play className="h-4 w-4" />
                    Mark as Played
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* YouTube Player */}
          <div className="space-y-4">
            {youtubeLink && extractYoutubeId(youtubeLink) ? (
              <Card>
                <CardHeader>
                  <CardTitle>Video</CardTitle>
                </CardHeader>
                <CardContent>
                  <YouTubePlayer
                    youtubeLink={youtubeLink}
                    title={`${song.title} by ${song.artist}`}
                    showControls={true}
                  />
                </CardContent>
              </Card>
            ) : (
              <Card>
                <CardContent className="text-center py-12">
                  <Music className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                  <p className="text-muted-foreground">
                    No YouTube video available for this song.
                  </p>
                  <p className="text-sm text-muted-foreground mt-2">
                    Edit the song to add a YouTube link.
                  </p>
                </CardContent>
              </Card>
            )}
          </div>
        </div>

        {/* Edit Form Modal */}
        {showEditForm && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
            <div className="bg-background rounded-lg max-w-md w-full max-h-[90vh] overflow-y-auto">
              <SongForm
                song={song}
                onSubmit={handleFormSubmit}
                onCancel={handleFormCancel}
                loading={loading}
              />
            </div>
          </div>
        )}
      </div>
    </MainLayout>
  );
}
