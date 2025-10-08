'use client';

import React, { useState, useMemo } from 'react';
import { useRouter } from 'next/navigation';
import { MainLayout } from '../../layouts/MainLayout';
import { Button } from '../../components/ui/button';
import { Alert, AlertDescription } from '../../components/ui/alert';
import { useAuth } from '../../context/AuthContext';
import { useSongs } from '../../hooks/useSongs';
import { SongList } from '../../components/songs/SongList';
import { SongForm } from '../../components/songs/SongForm';
import { SearchBar } from '../../components/auth/SearchBar';
import { Plus, Music, Search } from 'lucide-react';

/**
 * Songs page component
 */
export default function SongsPage() {
  const router = useRouter();
  const { user, isAuthenticated, loading: authLoading } = useAuth();
  const { 
    songs, 
    loading: songsLoading, 
    error: songsError,
    searchQuery,
    createSong,
    updateSong,
    deleteSong,
    searchSongs,
    clearSearch,
    fetchSongs
  } = useSongs();
  
  const [showAddForm, setShowAddForm] = useState(false);
  const [editingSong, setEditingSong] = useState(null);
  const [showAllSongs, setShowAllSongs] = useState(true);
  const [localSearchQuery, setLocalSearchQuery] = useState('');

  // Redirect if not authenticated
  React.useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      router.push('/login');
    }
  }, [isAuthenticated, authLoading, router]);

  // Use useMemo for client-side filtering - this is INSTANT and eliminates API calls!
  const filteredSongs = useMemo(() => {
    let filtered = songs;

    // Filter by user if "My Songs" is selected
    if (!showAllSongs && user?.username) {
      filtered = filtered.filter(song => song.user === user.username);
    }

    // Filter by search query (client-side search)
    if (localSearchQuery.trim()) {
      const query = localSearchQuery.toLowerCase();
      filtered = filtered.filter(song => 
        song.title.toLowerCase().includes(query) ||
        song.artist.toLowerCase().includes(query) ||
        song.genre?.toLowerCase().includes(query) ||
        song.user?.toLowerCase().includes(query)
      );
    }

    return filtered;
  }, [songs, showAllSongs, user?.username, localSearchQuery]);

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
    // Client-side search with useMemo - NO API CALLS!
    setLocalSearchQuery(query);
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
              {showAllSongs ? 'All Songs' : 'My Songs'}
            </h1>
            <p className="text-muted-foreground">
              {showAllSongs ? 'Browse songs from all users' : 'Manage your music collection'}
            </p>
          </div>
          <Button onClick={handleAddSong} className="flex items-center gap-2">
            <Plus className="h-4 w-4" />
            Add Song
          </Button>
        </div>

        {/* Search Bar and Filter */}
        <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-4">
          <div className="flex-1">
            <SearchBar
              onSearch={handleSearch}
              value={localSearchQuery}
              loading={false}
              placeholder="Search songs by title, artist, genre, or user..."
            />
          </div>
          <div className="flex gap-2">
            <Button 
              variant={showAllSongs ? "default" : "outline"}
              onClick={() => setShowAllSongs(true)}
            >
              All Songs
            </Button>
            <Button 
              variant={!showAllSongs ? "default" : "outline"}
              onClick={() => setShowAllSongs(false)}
            >
              My Songs
            </Button>
            {localSearchQuery && (
              <Button variant="outline" onClick={() => setLocalSearchQuery('')}>
                Clear Search
              </Button>
            )}
          </div>
        </div>

        {/* Error Display */}
        {songsError && (
          <Alert variant="destructive">
            <AlertDescription>{songsError}</AlertDescription>
          </Alert>
        )}

        {/* Results Count */}
        {!songsLoading && (
          <div className="text-sm text-muted-foreground">
            Showing <span className="font-semibold">{filteredSongs.length}</span> of{' '}
            <span className="font-semibold">{songs.length}</span> songs
            {localSearchQuery && (
              <span> matching "{localSearchQuery}"</span>
            )}
            {!showAllSongs && (
              <span> (your songs only)</span>
            )}
          </div>
        )}

        {/* Songs List */}
        <SongList
          songs={filteredSongs}
          loading={songsLoading}
          onEdit={handleEditSong}
          onDelete={handleDeleteSong}
          onPlay={handlePlaySong}
          emptyMessage={
            localSearchQuery 
              ? `No songs found matching "${localSearchQuery}"` 
              : showAllSongs 
                ? "No songs yet. Be the first to add one!" 
                : "You haven't added any songs yet."
          }
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
