import { useState, useEffect } from 'react';
import { songService } from '../services/songService';

/**
 * Custom hook for managing songs
 * @param {Object} options - Hook options
 * @returns {Object} - Songs state and operations
 */
export function useSongs(options = {}) {
  const [songs, setSongs] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');

  const { autoFetch = true, user = null } = options;

  // Fetch songs on mount and when dependencies change
  useEffect(() => {
    if (autoFetch) {
      fetchSongs();
    }
  }, [autoFetch, user]);

  /**
   * Fetch songs from API
   */
  const fetchSongs = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await songService.getSongs(user);
      setSongs(data.songs || []);
    } catch (error) {
      setError(error.message);
      console.error('Error fetching songs:', error);
    } finally {
      setLoading(false);
    }
  };

  /**
   * Create a new song
   * @param {Object} songData - Song data
   */
  const createSong = async (songData) => {
    try {
      setLoading(true);
      setError(null);
      const newSong = await songService.createSong(songData);
      setSongs(prev => [newSong, ...prev]);
      return newSong;
    } catch (error) {
      setError(error.message);
      throw error;
    } finally {
      setLoading(false);
    }
  };

  /**
   * Update an existing song
   * @param {string} songId - Song ID
   * @param {Object} songData - Updated song data
   */
  const updateSong = async (songId, songData) => {
    try {
      setLoading(true);
      setError(null);
      await songService.updateSong(songId, songData);
      
      // Update local state
      setSongs(prev => prev.map(song => 
        song.id === songId ? { ...song, ...songData } : song
      ));
    } catch (error) {
      setError(error.message);
      throw error;
    } finally {
      setLoading(false);
    }
  };

  /**
   * Delete a song
   * @param {string} songId - Song ID
   */
  const deleteSong = async (songId) => {
    try {
      setLoading(true);
      setError(null);
      await songService.deleteSong(songId);
      
      // Remove from local state
      setSongs(prev => prev.filter(song => song.id !== songId));
    } catch (error) {
      setError(error.message);
      throw error;
    } finally {
      setLoading(false);
    }
  };

  /**
   * Search songs
   * @param {string} query - Search query
   */
  const searchSongs = async (query) => {
    try {
      setLoading(true);
      setError(null);
      setSearchQuery(query);
      
      if (!query.trim()) {
        await fetchSongs();
        return;
      }
      
      // Search all songs (don't filter by user)
      const data = await songService.searchSongs(query);
      setSongs(data.results || []);
    } catch (error) {
      setError(error.message);
      console.error('Error searching songs:', error);
    } finally {
      setLoading(false);
    }
  };

  /**
   * Mark a song as played
   * @param {string} songId - Song ID
   */
  const playSong = async (songId) => {
    try {
      await songService.playSong(songId);
      // Could update local state to track play count if needed
    } catch (error) {
      setError(error.message);
      throw error;
    }
  };

  /**
   * Clear error
   */
  const clearError = () => {
    setError(null);
  };

  /**
   * Clear search query and reset to all songs
   */
  const clearSearch = () => {
    setSearchQuery('');
    fetchSongs();
  };

  return {
    songs,
    loading,
    error,
    searchQuery,
    fetchSongs,
    createSong,
    updateSong,
    deleteSong,
    searchSongs,
    playSong,
    clearError,
    clearSearch
  };
}
