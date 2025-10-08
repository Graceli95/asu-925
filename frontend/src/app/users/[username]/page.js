'use client';

import React, { useState, useEffect } from 'react';
import { useRouter, useParams } from 'next/navigation';
import { MainLayout } from '../../../layouts/MainLayout';
import { Card, CardContent, CardHeader, CardTitle } from '../../../components/ui/card';
import { Button } from '../../../components/ui/button';
import { Alert, AlertDescription } from '../../../components/ui/alert';
import { useAuth } from '../../../context/AuthContext';
import { songService } from '../../../services/songService';
import { SongList } from '../../../components/songs/SongList';
import { SearchBar } from '../../../components/auth/SearchBar';
import { formatDate } from '../../../utils/date';
import { ArrowLeft, User, Music, BarChart3, TrendingUp, Calendar } from 'lucide-react';

/**
 * Dynamic user profile page
 * Route: /users/[username]
 */
export default function UserProfilePage() {
  const router = useRouter();
  const params = useParams();
  const { user: currentUser, isAuthenticated, loading: authLoading } = useAuth();
  
  const [profileUser, setProfileUser] = useState(null);
  const [songs, setSongs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');

  const username = params.username;

  // Redirect if not authenticated
  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      router.push('/login');
    }
  }, [isAuthenticated, authLoading, router]);

  // Fetch user profile and songs
  useEffect(() => {
    if (username && isAuthenticated) {
      fetchUserProfile();
    }
  }, [username, isAuthenticated]);

  const fetchUserProfile = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Fetch user's songs
      const songsData = await songService.getSongs(username);
      setSongs(songsData.songs || []);
      
      // Set profile user (for now, we'll use the username since we don't have user details endpoint)
      setProfileUser({
        username: username,
        // We could extend this to fetch actual user details if the backend supports it
      });
      
    } catch (error) {
      setError(error.message);
      console.error('Error fetching user profile:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (query) => {
    setSearchQuery(query);
    if (query.trim()) {
      // Filter songs locally for now, or implement server-side search
      const filteredSongs = songs.filter(song => 
        song.title.toLowerCase().includes(query.toLowerCase()) ||
        song.artist.toLowerCase().includes(query.toLowerCase())
      );
      setSongs(filteredSongs);
    } else {
      // Reset to all songs
      fetchUserProfile();
    }
  };

  const clearSearch = () => {
    setSearchQuery('');
    fetchUserProfile();
  };

  // Calculate user stats
  const stats = {
    totalSongs: songs.length,
    genres: songs.reduce((acc, song) => {
      const genre = song.genre || 'Unknown';
      acc[genre] = (acc[genre] || 0) + 1;
      return acc;
    }, {}),
    years: songs.reduce((acc, song) => {
      if (song.year) {
        acc[song.year] = (acc[song.year] || 0) + 1;
      }
      return acc;
    }, {}),
    artists: songs.reduce((acc, song) => {
      acc[song.artist] = (acc[song.artist] || 0) + 1;
      return acc;
    }, {})
  };

  const topGenres = Object.entries(stats.genres)
    .sort(([,a], [,b]) => b - a)
    .slice(0, 3);

  const topArtists = Object.entries(stats.artists)
    .sort(([,a], [,b]) => b - a)
    .slice(0, 5);

  const isOwnProfile = currentUser?.username === username;

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
          
          {isOwnProfile && (
            <Button onClick={() => router.push('/songs')}>
              Manage Songs
            </Button>
          )}
        </div>

        {/* User Profile Header */}
        <Card>
          <CardHeader>
            <div className="flex items-center gap-4">
              <div className="p-3 bg-primary/10 rounded-full">
                <User className="h-8 w-8 text-primary" />
              </div>
              <div>
                <CardTitle className="text-2xl">{profileUser?.username}</CardTitle>
                <p className="text-muted-foreground">
                  {isOwnProfile ? 'Your Music Collection' : `${profileUser?.username}'s Music Collection`}
                </p>
              </div>
            </div>
          </CardHeader>
        </Card>

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
                Songs in collection
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

        {/* Top Artists */}
        {topArtists.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Music className="h-5 w-5" />
                Top Artists
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {topArtists.map(([artist, count]) => (
                  <div key={artist} className="flex items-center justify-between">
                    <span className="font-medium">{artist}</span>
                    <span className="text-sm text-muted-foreground">{count} songs</span>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}

        {/* Search */}
        <div className="flex items-center gap-4">
          <SearchBar
            onSearch={handleSearch}
            value={searchQuery}
            loading={loading}
            placeholder={`Search ${profileUser?.username}'s songs...`}
          />
          {searchQuery && (
            <Button variant="outline" onClick={clearSearch}>
              Clear Search
            </Button>
          )}
        </div>

        {/* Songs List */}
        <div className="space-y-4">
          <h2 className="text-2xl font-semibold">
            {searchQuery ? 'Search Results' : 'Songs'}
          </h2>
          
          <SongList
            songs={songs}
            loading={loading}
            emptyMessage={
              searchQuery 
                ? `No songs found matching "${searchQuery}"` 
                : `${profileUser?.username} hasn't added any songs yet.`
            }
          />
        </div>
      </div>
    </MainLayout>
  );
}
