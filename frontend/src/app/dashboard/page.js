'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { MainLayout } from '../../layouts/MainLayout';
import { Card, CardContent, CardHeader, CardTitle } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { Alert, AlertDescription } from '../../components/ui/alert';
import { useAuth } from '../../context/AuthContext';
import { useSongs } from '../../hooks/useSongs';
import { SongList } from '../../components/SongList';
import { SongForm } from '../../components/SongForm';
import { SearchBar } from '../../components/SearchBar';
import { Music, Plus, BarChart3, TrendingUp, Calendar } from 'lucide-react';

/**
 * Dashboard page component
 */
export default function DashboardPage() {
  const router = useRouter();
  const { user, isAuthenticated, loading: authLoading } = useAuth();
  const { songs, loading: songsLoading, searchSongs, clearSearch } = useSongs();
  const [showAddForm, setShowAddForm] = useState(false);
  const [editingSong, setEditingSong] = useState(null);

  // Redirect if not authenticated
  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      router.push('/login');
    }
  }, [isAuthenticated, authLoading, router]);

  // Calculate stats
  const stats = {
    totalSongs: songs.length,
    genres: songs.reduce((acc, song) => {
      const genre = song.genre || 'Unknown';
      acc[genre] = (acc[genre] || 0) + 1;
      return acc;
    }, {}),
    recentSongs: songs.slice(0, 5)
  };

  const topGenres = Object.entries(stats.genres)
    .sort(([,a], [,b]) => b - a)
    .slice(0, 3);

  const handleAddSong = () => {
    setEditingSong(null);
    setShowAddForm(true);
  };

  const handleEditSong = (song) => {
    setEditingSong(song);
    setShowAddForm(true);
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
      <div className="space-y-8">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold">Dashboard</h1>
            <p className="text-muted-foreground">
              Welcome back, {user?.username}!
            </p>
          </div>
          <Button onClick={handleAddSong} className="flex items-center gap-2">
            <Plus className="h-4 w-4" />
            Add Song
          </Button>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Songs</CardTitle>
              <Music className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.totalSongs}</div>
              <p className="text-xs text-muted-foreground">
                Songs in your collection
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Top Genre</CardTitle>
              <BarChart3 className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {topGenres[0]?.[0] || 'None'}
              </div>
              <p className="text-xs text-muted-foreground">
                {topGenres[0]?.[1] || 0} songs
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Genres</CardTitle>
              <TrendingUp className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {Object.keys(stats.genres).length}
              </div>
              <p className="text-xs text-muted-foreground">
                Different genres
              </p>
            </CardContent>
          </Card>
        </div>

        {/* Recent Songs */}
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-2xl font-semibold">Recent Songs</h2>
            <Button variant="outline" onClick={() => router.push('/songs')}>
              View All Songs
            </Button>
          </div>
          
          {songsLoading ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
              {Array.from({ length: 4 }).map((_, index) => (
                <div key={index} className="animate-pulse">
                  <div className="bg-gray-200 rounded-lg h-64"></div>
                </div>
              ))}
            </div>
          ) : (
            <SongList
              songs={stats.recentSongs}
              onEdit={handleEditSong}
              emptyMessage="No songs yet. Add your first song to get started!"
            />
          )}
        </div>

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
