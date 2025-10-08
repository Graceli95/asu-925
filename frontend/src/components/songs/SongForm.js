import React, { useState, useEffect } from 'react';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Label } from '../ui/label';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Alert, AlertDescription } from '../ui/alert';
import { MUSIC_GENRES, APP_CONFIG } from '../../constants';
import { isValidYoutubeUrl } from '../../utils/youtube';
import { validatePassword } from '../../utils';
import { X, Music, Calendar, User, Link } from 'lucide-react';

/**
 * SongForm component for creating and editing songs
 * @param {Object} props - Component props
 * @param {Object} props.song - Song data for editing (optional)
 * @param {Function} props.onSubmit - Submit callback
 * @param {Function} props.onCancel - Cancel callback
 * @param {boolean} props.loading - Loading state
 */
export function SongForm({ song = null, onSubmit, onCancel, loading = false }) {
  const [formData, setFormData] = useState({
    title: song?.title || '',
    artist: song?.artist || '',
    genre: song?.genre || '',
    year: song?.year || '',
    youtube_link: song?.youtube_link || ''
  });
  
  const [errors, setErrors] = useState({});
  const [youtubeError, setYoutubeError] = useState('');

  const isEditing = !!song;

  // Validate form data
  const validateForm = () => {
    const newErrors = {};

    if (!formData.title.trim()) {
      newErrors.title = 'Title is required';
    }

    if (!formData.artist.trim()) {
      newErrors.artist = 'Artist is required';
    }

    if (formData.year && (formData.year < APP_CONFIG.MIN_YEAR || formData.year > APP_CONFIG.MAX_YEAR)) {
      newErrors.year = `Year must be between ${APP_CONFIG.MIN_YEAR} and ${APP_CONFIG.MAX_YEAR}`;
    }

    if (formData.youtube_link && !isValidYoutubeUrl(formData.youtube_link)) {
      newErrors.youtube_link = 'Please enter a valid YouTube URL';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  // Handle input changes
  const handleChange = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    
    // Clear error when user starts typing
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: '' }));
    }
  };

  // Handle form submission
  const handleSubmit = (e) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }

    // Prepare data for submission
    const submitData = {
      title: formData.title.trim(),
      artist: formData.artist.trim(),
      genre: formData.genre || null,
      year: formData.year ? parseInt(formData.year) : null,
    };

    // Add YouTube link to local storage (not sent to backend)
    if (formData.youtube_link.trim()) {
      localStorage.setItem(`song_${song?.id || 'new'}_youtube`, formData.youtube_link.trim());
    }

    onSubmit(submitData);
  };

  return (
    <Card className="w-full max-w-md mx-auto">
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2">
            <Music className="h-5 w-5" />
            {isEditing ? 'Edit Song' : 'Add New Song'}
          </CardTitle>
          {onCancel && (
            <Button variant="ghost" size="icon" onClick={onCancel}>
              <X className="h-4 w-4" />
            </Button>
          )}
        </div>
      </CardHeader>
      
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-4">
          {/* Title */}
          <div className="space-y-2">
            <Label htmlFor="title" className="flex items-center gap-2">
              <Music className="h-4 w-4" />
              Title *
            </Label>
            <Input
              id="title"
              value={formData.title}
              onChange={(e) => handleChange('title', e.target.value)}
              placeholder="Enter song title"
              className={errors.title ? 'border-destructive' : ''}
            />
            {errors.title && (
              <Alert variant="destructive">
                <AlertDescription>{errors.title}</AlertDescription>
              </Alert>
            )}
          </div>

          {/* Artist */}
          <div className="space-y-2">
            <Label htmlFor="artist" className="flex items-center gap-2">
              <User className="h-4 w-4" />
              Artist *
            </Label>
            <Input
              id="artist"
              value={formData.artist}
              onChange={(e) => handleChange('artist', e.target.value)}
              placeholder="Enter artist name"
              className={errors.artist ? 'border-destructive' : ''}
            />
            {errors.artist && (
              <Alert variant="destructive">
                <AlertDescription>{errors.artist}</AlertDescription>
              </Alert>
            )}
          </div>

          {/* Genre */}
          <div className="space-y-2">
            <Label htmlFor="genre">Genre</Label>
            <select
              id="genre"
              value={formData.genre}
              onChange={(e) => handleChange('genre', e.target.value)}
              className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
            >
              <option value="">Select a genre</option>
              {MUSIC_GENRES.map(genre => (
                <option key={genre} value={genre}>{genre}</option>
              ))}
            </select>
          </div>

          {/* Year */}
          <div className="space-y-2">
            <Label htmlFor="year" className="flex items-center gap-2">
              <Calendar className="h-4 w-4" />
              Year
            </Label>
            <Input
              id="year"
              type="number"
              value={formData.year}
              onChange={(e) => handleChange('year', e.target.value)}
              placeholder="Release year"
              min={APP_CONFIG.MIN_YEAR}
              max={APP_CONFIG.MAX_YEAR}
              className={errors.year ? 'border-destructive' : ''}
            />
            {errors.year && (
              <Alert variant="destructive">
                <AlertDescription>{errors.year}</AlertDescription>
              </Alert>
            )}
          </div>

          {/* YouTube Link */}
          <div className="space-y-2">
            <Label htmlFor="youtube_link" className="flex items-center gap-2">
              <Link className="h-4 w-4" />
              YouTube Link (Optional)
            </Label>
            <Input
              id="youtube_link"
              value={formData.youtube_link}
              onChange={(e) => handleChange('youtube_link', e.target.value)}
              placeholder="https://www.youtube.com/watch?v=..."
              className={errors.youtube_link ? 'border-destructive' : ''}
            />
            {errors.youtube_link && (
              <Alert variant="destructive">
                <AlertDescription>{errors.youtube_link}</AlertDescription>
              </Alert>
            )}
            <p className="text-xs text-muted-foreground">
              YouTube links are stored locally and not saved to the server.
            </p>
          </div>

          {/* Submit Buttons */}
          <div className="flex gap-2 pt-4">
            <Button
              type="submit"
              disabled={loading}
              className="flex-1"
            >
              {loading ? 'Saving...' : (isEditing ? 'Update Song' : 'Add Song')}
            </Button>
            {onCancel && (
              <Button type="button" variant="outline" onClick={onCancel}>
                Cancel
              </Button>
            )}
          </div>
        </form>
      </CardContent>
    </Card>
  );
}
