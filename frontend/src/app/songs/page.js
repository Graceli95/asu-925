'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import { MainLayout } from '../../layouts/MainLayout';
import { Button } from '../../components/ui/button';
import { Alert, AlertDescription } from '../../components/ui/alert';
import { useAuth } from '../../context/AuthContext';
import { useSongs } from '../../hooks/useSongs';
import { SongList } from '../../components/SongList';
import { SongForm } from '../../components/SongForm';
import { SearchBar } from '../../components/SearchBar';
import { Plus, Music, Search } from 'lucide-react';

/**
 * Songs page component
 */
export default function SongsPage() {
  const router = useRouter();
  const { isAuthenticated, loading: authLoading } = useAuth();
  const { 
    songs, 
    loading: songsLoading, 
    error: songsError,
    searchQuery,
    createSong,
    updateSong,
    deleteSong,
    searchSongs,
    clearSearch
  } = useSongs();
  
  const [showAddForm, setShowAddForm] = useState(false);
  const [editingSong, setEditingSong] = useState(null);

  // Redirect if not authenticated
  React.useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      router.push('/login');
    }
  }, [isAuthenticated, authLoading, router]);

  const handleAddSong = () => {
    setEditingSong(null);
    setShowAddForm(true);
  };

  const handleEditSong = (song) => {
    setEditingSong(song);
    setShowAddForm(true);
  };

  const handleDeleteSong = async (songId) => {
    if (window.confirm('Are you sure you want to delete this song?')) {
      try {
        await deleteSong(songId);
      } catch (error) {
        console.error('Error deleting song:', error);
      }
    }
  };

  const handlePlaySong = async (songId) => {
    try {
      await playSong(songId);
    } catch (error) {
      console.error('Error playing song:', error);
    }
  };

  const handleFormSubmit = async (songData) => {
    try {
      if (editingSong) {
        await updateSong(editingSong.id, songData);
      } else {
        await createSong(songData);
      }
      setShowAddForm(false);
      setEditingSong(null);
    } catch (error) {
      console.error('Error saving song:', error);
    }
  };

  const handleFormCancel = () => {
    setShowAddForm(false);
    setEditingSong(null);
  };

  const handleSearch = (query) => {
    searchSongs(query);
  };

  if (authLoading) {
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

  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold flex items-center gap-2">
              <Music className="h-8 w-8" />
              My Songs
            </h1>
            <p className="text-muted-foreground">
              Manage your music collection
            </p>
          </div>
          <Button onClick={handleAddSong} className="flex items-center gap-2">
            <Plus className="h-4 w-4" />
            Add Song
          </Button>
        </div>

        {/* Search Bar */}
        <div className="flex items-center gap-4">
          <SearchBar
            onSearch={handleSearch}
            value={searchQuery}
            loading={songsLoading}
            placeholder="Search songs by title or artist..."
          />
          {searchQuery && (
            <Button variant="outline" onClick={clearSearch}>
              Clear Search
            </Button>
          )}
        </div>

        {/* Error Display */}
        {songsError && (
          <Alert variant="destructive">
            <AlertDescription>{songsError}</AlertDescription>
          </Alert>
        )}

        {/* Songs List */}
        <SongList
          songs={songs}
          loading={songsLoading}
          onEdit={handleEditSong}
          onDelete={handleDeleteSong}
          onPlay={handlePlaySong}
          emptyMessage={searchQuery ? "No songs found matching your search." : "No songs yet. Add your first song to get started!"}
        />

        {/* Add/Edit Song Form Modal */}
        {showAddForm && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
            <div className="bg-background rounded-lg max-w-md w-full max-h-[90vh] overflow-y-auto">
              <SongForm
                song={editingSong}
                onSubmit={handleFormSubmit}
                onCancel={handleFormCancel}
                loading={songsLoading}
              />
            </div>
          </div>
        )}
      </div>
    </MainLayout>
  );
}
