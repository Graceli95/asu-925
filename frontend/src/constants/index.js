// API Configuration
export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// API Endpoints
export const API_ENDPOINTS = {
  // Authentication
  REGISTER: '/auth/register',
  LOGIN: '/auth/login',
  LOGOUT: '/auth/logout',
  REFRESH: '/auth/refresh',
  ME: '/auth/me',
  
  // Songs
  SONGS: '/songs',
  SONG_BY_ID: (id) => `/songs/${id}`,
  SONG_SEARCH: '/songs/search',
  SONG_PLAY: (id) => `/songs/${id}/play`,
  
  // Users
  USER_STATS: (username) => `/users/${username}/stats`,
};

// Music Genres
export const MUSIC_GENRES = [
  'Rock',
  'Pop',
  'Hip Hop',
  'R&B',
  'Country',
  'Jazz',
  'Classical',
  'Electronic',
  'Folk',
  'Blues',
  'Reggae',
  'Punk',
  'Metal',
  'Alternative',
  'Indie',
  'Funk',
  'Soul',
  'Gospel',
  'Latin',
  'World',
  'Other'
];

// App Constants
export const APP_CONFIG = {
  DEBOUNCE_DELAY: 300, // milliseconds
  MAX_YEAR: new Date().getFullYear(),
  MIN_YEAR: 1900,
  ITEMS_PER_PAGE: 20,
};
