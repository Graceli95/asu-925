'use client';

import React, { useState, useEffect } from 'react';
import { useRouter, useParams } from 'next/navigation';
import { MainLayout } from '../../layouts/MainLayout';
import { Button } from '../../components/ui/button';
import { Alert, AlertDescription } from '../../components/ui/alert';
import { useAuth } from '../../context/AuthContext';
import { songService } from '../../services/songService';
import { SongForm } from '../../components/SongForm';
import { ArrowLeft } from 'lucide-react';

/**
 * Dynamic song edit page
 * Route: /songs/[id]/edit
 */
export default function SongEditPage() {
  const router = useRouter();
  const params = useParams();
  const { isAuthenticated, loading: authLoading } = useAuth();
  
  const [song, setSong] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

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

  const handleFormSubmit = async (songData) => {
    try {
      await songService.updateSong(songId, songData);
      
      // Update YouTube link in localStorage
      if (songData.youtube_link) {
        localStorage.setItem(`song_${songId}_youtube`, songData.youtube_link);
      }
      
      router.push(`/songs/${songId}`);
    } catch (error) {
      setError(error.message);
      console.error('Error updating song:', error);
    }
  };

  const handleFormCancel = () => {
    router.push(`/songs/${songId}`);
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
            The song you're trying to edit doesn't exist or you don't have permission to edit it.
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
          
          <h1 className="text-2xl font-bold">Edit Song</h1>
        </div>

        {/* Edit Form */}
        <div className="max-w-md mx-auto">
          <SongForm
            song={song}
            onSubmit={handleFormSubmit}
            onCancel={handleFormCancel}
            loading={loading}
          />
        </div>
      </div>
    </MainLayout>
  );
}
