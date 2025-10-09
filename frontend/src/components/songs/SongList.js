import React from 'react';
import { SongCard } from './SongCard';

/**
 * SongList component for displaying a list of songs
 * @param {Object} props - Component props
 * @param {Array} props.songs - Array of song objects
 * @param {Function} props.onEdit - Edit callback
 * @param {Function} props.onDelete - Delete callback
 * @param {Function} props.onPlay - Play callback
 * @param {boolean} props.loading - Loading state
 * @param {string} props.emptyMessage - Message when no songs
 * @param {Object} props.currentUser - Current logged-in user (optional)
 */
export function SongList({ 
  songs = [], 
  onEdit, 
  onDelete, 
  onPlay, 
  loading = false,
  emptyMessage = "No songs found",
  currentUser
}) {
  if (loading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
        {Array.from({ length: 8 }).map((_, index) => (
          <div key={index} className="animate-pulse">
            <div className="bg-gray-200 rounded-lg h-64"></div>
          </div>
        ))}
      </div>
    );
  }

  if (songs.length === 0) {
    return (
      <div className="text-center py-12">
        <div className="text-muted-foreground text-lg">
          {emptyMessage}
        </div>
        <p className="text-sm text-muted-foreground mt-2">
          Add your first song to get started!
        </p>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
      {songs.map((song) => {
        return (
          <SongCard
            key={song.id}
            song={song}
            youtubeLink={song.youtube_link}
            onEdit={onEdit}
            onDelete={onDelete}
            onPlay={onPlay}
            currentUser={currentUser}
          />
        );
      })}
    </div>
  );
}
