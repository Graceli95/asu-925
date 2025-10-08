import apiClient from '../utils/apiClient';
import { API_ENDPOINTS } from '../constants';

/**
 * Song service for handling song CRUD operations
 */
export const songService = {
  /**
   * Get all songs for the current user
   * @param {string} user - Optional user filter
   * @returns {Promise<Object>} - Songs list
   */
  async getSongs(user = null) {
    try {
      const params = user ? { user } : {};
      const response = await apiClient.get(API_ENDPOINTS.SONGS, { params });
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to fetch songs');
    }
  },

  /**
   * Get a specific song by ID
   * @param {string} songId - Song ID
   * @returns {Promise<Object>} - Song data
   */
  async getSongById(songId) {
    try {
      const response = await apiClient.get(API_ENDPOINTS.SONG_BY_ID(songId));
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to fetch song');
    }
  },

  /**
   * Create a new song
   * @param {Object} songData - Song data
   * @returns {Promise<Object>} - Created song data
   */
  async createSong(songData) {
    try {
      const response = await apiClient.post(API_ENDPOINTS.SONGS, songData);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to create song');
    }
  },

  /**
   * Update an existing song
   * @param {string} songId - Song ID
   * @param {Object} songData - Updated song data
   * @returns {Promise<Object>} - Update confirmation
   */
  async updateSong(songId, songData) {
    try {
      const response = await apiClient.put(API_ENDPOINTS.SONG_BY_ID(songId), songData);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to update song');
    }
  },

  /**
   * Delete a song
   * @param {string} songId - Song ID
   * @returns {Promise<Object>} - Deletion confirmation
   */
  async deleteSong(songId) {
    try {
      const response = await apiClient.delete(API_ENDPOINTS.SONG_BY_ID(songId));
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to delete song');
    }
  },

  /**
   * Search songs
   * @param {string} query - Search query
   * @param {string} user - Optional user filter
   * @returns {Promise<Object>} - Search results
   */
  async searchSongs(query, user = null) {
    try {
      const params = { query };
      if (user) params.user = user;
      
      const response = await apiClient.get(API_ENDPOINTS.SONG_SEARCH, { params });
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to search songs');
    }
  },

  /**
   * Mark a song as played
   * @param {string} songId - Song ID
   * @returns {Promise<Object>} - Play confirmation
   */
  async playSong(songId) {
    try {
      const response = await apiClient.post(API_ENDPOINTS.SONG_PLAY(songId));
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to mark song as played');
    }
  }
};
