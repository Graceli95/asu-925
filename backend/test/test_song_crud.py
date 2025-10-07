"""
Tests for song CRUD operations (Create, Read, Update, Delete)
"""

import pytest
from bson import ObjectId
from model import Song


class TestSongCRUD:
    """Test CRUD operations for songs"""
    
    def test_add_song_success(self, test_db, test_user, sample_song_data):
        """Test adding a song successfully"""
        result = test_db.add_song(
            sample_song_data["title"], 
            sample_song_data["artist"], 
            test_user, 
            sample_song_data["genre"], 
            sample_song_data["year"]
        )
        assert result is not None
        
        # Verify song was added
        songs = test_db.get_songs(test_user)
        assert len(songs) == 1
        assert songs[0].title == sample_song_data["title"]
        assert songs[0].artist == sample_song_data["artist"]
        assert songs[0].user == test_user
        assert songs[0].genre == sample_song_data["genre"]
        assert songs[0].year == sample_song_data["year"]
        assert songs[0].created_at is not None
    
    def test_add_song_without_optional_fields(self, test_db, test_user):
        """Test adding a song without optional fields"""
        result = test_db.add_song("Simple Song", "Simple Artist", test_user)
        assert result is not None
        
        songs = test_db.get_songs(test_user)
        assert len(songs) == 1
        assert songs[0].title == "Simple Song"
        assert songs[0].artist == "Simple Artist"
        assert songs[0].user == test_user
        assert songs[0].genre is None
        assert songs[0].year is None
    
    def test_add_multiple_songs(self, test_db, test_user, multiple_songs_data):
        """Test adding multiple songs"""
        for title, artist, genre, year in multiple_songs_data:
            result = test_db.add_song(title, artist, test_user, genre, year)
            assert result is not None
        
        songs = test_db.get_songs(test_user)
        assert len(songs) == 3
        
        # Check that songs are sorted by created_at descending
        titles = [song.title for song in songs]
        assert titles == ["Song 3", "Song 2", "Song 1"]
    
    def test_get_songs_by_user(self, test_db, test_user, test_user2):
        """Test getting songs filtered by user"""
        # Add songs for two different users
        test_db.add_song("User1 Song", "Artist", test_user, "Rock", 2020)
        test_db.add_song("User2 Song", "Artist", test_user2, "Pop", 2021)
        
        # Get songs for test_user
        user1_songs = test_db.get_songs(test_user)
        assert len(user1_songs) == 1
        assert user1_songs[0].title == "User1 Song"
        
        # Get songs for test_user2
        user2_songs = test_db.get_songs(test_user2)
        assert len(user2_songs) == 1
        assert user2_songs[0].title == "User2 Song"
        
        # Get all songs
        all_songs = test_db.get_songs()
        assert len(all_songs) == 2
    
    def test_update_song(self, test_db, test_user):
        """Test updating a song"""
        # Add a song first
        test_db.add_song("Original Title", "Original Artist", test_user, "Rock", 2020)
        songs = test_db.get_songs(test_user)
        song_id = str(songs[0]._id)
        
        # Update the song
        result = test_db.update_song(song_id, test_user, 
                                    title="Updated Title", 
                                    artist="Updated Artist",
                                    genre="Pop",
                                    year=2021)
        assert result is True
        
        # Verify the update
        updated_songs = test_db.get_songs(test_user)
        assert len(updated_songs) == 1
        assert updated_songs[0].title == "Updated Title"
        assert updated_songs[0].artist == "Updated Artist"
        assert updated_songs[0].genre == "Pop"
        assert updated_songs[0].year == 2021
        assert updated_songs[0].updated_at is not None
    
    def test_update_song_partial(self, test_db, test_user):
        """Test updating only some fields of a song"""
        # Add a song first
        test_db.add_song("Original Title", "Original Artist", test_user, "Rock", 2020)
        songs = test_db.get_songs(test_user)
        song_id = str(songs[0]._id)
        
        # Update only title
        result = test_db.update_song(song_id, test_user, title="New Title")
        assert result is True
        
        # Verify only title was updated
        updated_songs = test_db.get_songs(test_user)
        assert updated_songs[0].title == "New Title"
        assert updated_songs[0].artist == "Original Artist"  # Unchanged
        assert updated_songs[0].genre == "Rock"  # Unchanged
        assert updated_songs[0].year == 2020  # Unchanged
    
    def test_update_song_not_found(self, test_db, test_user):
        """Test updating a non-existent song"""
        fake_id = str(ObjectId())
        result = test_db.update_song(fake_id, test_user, title="New Title")
        assert result is False
    
    def test_delete_song(self, test_db, test_user):
        """Test deleting a song"""
        # Add a song first
        test_db.add_song("To Delete", "Artist", test_user, "Rock", 2020)
        songs = test_db.get_songs(test_user)
        song_id = str(songs[0]._id)
        
        # Delete the song
        result = test_db.delete_song(song_id, test_user)
        assert result is True
        
        # Verify song was deleted
        remaining_songs = test_db.get_songs(test_user)
        assert len(remaining_songs) == 0
    
    def test_delete_song_not_found(self, test_db, test_user):
        """Test deleting a non-existent song"""
        fake_id = str(ObjectId())
        result = test_db.delete_song(fake_id, test_user)
        assert result is False
    
    def test_delete_song_wrong_user(self, test_db, test_user, test_user2):
        """Test that users can only delete their own songs"""
        # Add song for test_user
        test_db.add_song("User1 Song", "Artist", test_user, "Rock", 2020)
        songs = test_db.get_songs(test_user)
        song_id = str(songs[0]._id)
        
        # Try to delete with different user
        result = test_db.delete_song(song_id, test_user2)
        assert result is False
        
        # Verify song still exists
        remaining_songs = test_db.get_songs(test_user)
        assert len(remaining_songs) == 1
    
    def test_play_song(self, test_db, test_user):
        """Test playing a song"""
        # Add a song first
        test_db.add_song("Playable Song", "Artist", test_user, "Rock", 2020)
        songs = test_db.get_songs(test_user)
        song_id = str(songs[0]._id)
        
        # Play the song
        result = test_db.play_song(song_id, test_user)
        assert result is True
        
        # Song played successfully - no history tracking
    
    def test_play_song_not_found(self, test_db, test_user):
        """Test playing a non-existent song"""
        fake_id = str(ObjectId())
        result = test_db.play_song(fake_id, test_user)
        assert result is False
