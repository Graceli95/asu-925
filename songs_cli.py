#!/usr/bin/env python3
"""
Songs CLI CRUD Application
A command-line interface for managing songs with MongoDB backend
"""

from typing import List, Dict, Any
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt, Confirm
from db.songs_db import SongsDatabase
from service import SongService
from model import Song

console = Console()


class SongsCLICommands:
    """CLI commands handler for songs operations"""
    
    def __init__(self, song_service: SongService):
        self.service = song_service
    
    def add_song(self, title: str, artist: str, user: str, genre: str = None, year: int = None) -> bool:
        """Add a new song"""
        result = self.service.add_song(title, artist, user, genre, year)
        
        if result["success"]:
            console.print(f"[green]✓ {result['message']}[/green]")
            return True
        else:
            console.print(f"[red]✗ {result['message']}[/red]")
            return False
    
    def list_songs(self, user: str = None, user_filter: str = None) -> None:
        """List all songs"""
        target_user = user_filter or user
        songs = self.service.get_songs(target_user)
        display_songs(songs, f"Songs for {target_user}" if target_user else "All Songs")
    
    def search_songs(self, query: str, user: str, all_users: bool = False) -> None:
        """Search songs by title or artist"""
        search_user = None if all_users else user
        result = self.service.search_songs(query, search_user)
        
        if result["success"]:
            display_songs(result["results"], f"Search Results for '{query}'")
            if len(result["results"]) == 0:
                console.print(f"[yellow]{result['message']}[/yellow]")
        else:
            console.print(f"[red]✗ {result['message']}[/red]")
    
    def play_song(self, song_id: str, user: str) -> bool:
        """Mark a song as played"""
        result = self.service.play_song(song_id, user)
        
        if result["success"]:
            console.print(f"[green]✓ {result['message']}[/green]")
            return True
        else:
            console.print(f"[red]✗ {result['message']}[/red]")
            return False
    
    def update_song(self, song_id: str, user: str, **updates) -> bool:
        """Update a song"""
        if not updates:
            console.print("[red]No updates provided[/red]")
            return False
        
        result = self.service.update_song(song_id, user, **updates)
        
        if result["success"]:
            console.print(f"[green]✓ {result['message']}[/green]")
            return True
        else:
            console.print(f"[red]✗ {result['message']}[/red]")
            return False
    
    def delete_song(self, song_id: str, user: str, confirm: bool = False) -> bool:
        """Delete a song"""
        song = self.service.get_song_by_id(song_id, user)
        if not song:
            console.print("[red]✗ Song not found[/red]")
            return False
        
        if not confirm:
            if not Confirm.ask(f"Are you sure you want to delete '{song.title}' by '{song.artist}'?"):
                console.print("[yellow]Operation cancelled[/yellow]")
                return False
        
        result = self.service.delete_song(song_id, user)
        
        if result["success"]:
            console.print(f"[green]✓ {result['message']}[/green]")
            return True
        else:
            console.print(f"[red]✗ {result['message']}[/red]")
            return False
    
    def show_stats(self, user: str) -> None:
        """Show user statistics"""
        stats = self.service.get_user_stats(user)
        
        if stats["total_songs"] == 0:
            console.print("[yellow]No songs found for this user[/yellow]")
            return
        
        console.print(f"\n[bold]Statistics for {user}[/bold]")
        console.print(f"Total Songs: [green]{stats['total_songs']}[/green]")
        
        # Top genres
        if stats["genres"]:
            console.print("\n[bold]Top Genres:[/bold]")
            for genre, count in list(stats["genres"].items())[:5]:
                console.print(f"  {genre}: {count}")
        
        # Top artists
        if stats["artists"]:
            console.print("\n[bold]Top Artists:[/bold]")
            for artist, count in list(stats["artists"].items())[:5]:
                console.print(f"  {artist}: {count}")
        
        # Years distribution
        if stats["years"]:
            console.print("\n[bold]Years Distribution:[/bold]")
            for year, count in list(stats["years"].items())[:5]:
                console.print(f"  {year}: {count}")


def display_songs(songs: List[Song], title: str = "Songs"):
    """Display songs in a table format"""
    if not songs:
        console.print("[yellow]No songs found[/yellow]")
        return
    
    table = Table(title=title)
    table.add_column("ID", style="cyan", no_wrap=True)
    table.add_column("Title", style="magenta")
    table.add_column("Artist", style="blue")
    table.add_column("Genre", style="green")
    table.add_column("Year", style="yellow")
    table.add_column("User", style="red")
    table.add_column("Created", style="dim")
    
    for song in songs:
        table.add_row(
            str(song._id),
            song.title,
            song.artist,
            song.genre or 'N/A',
            str(song.year) if song.year else 'N/A',
            song.user,
            song.created_at.strftime('%Y-%m-%d %H:%M')
        )
    
    console.print(table)


def main():
    """Main interactive CLI interface"""
    console.print("[bold blue]🎵 Songs CLI CRUD Application[/bold blue]")
    console.print("[dim]A command-line interface for managing songs with MongoDB backend[/dim]\n")
    
    # Get username
    user = Prompt.ask("Enter your username")
    console.print(f"[green]Welcome, {user}![/green]\n")
    
    # Initialize database, service, and CLI commands
    try:
        db = SongsDatabase()
        song_service = SongService(db)
        cli_commands = SongsCLICommands(song_service)
    except Exception as e:
        console.print(f"[red]Error initializing database: {e}[/red]")
        return
    
    while True:
        console.print("\n[bold]Available Commands:[/bold]")
        console.print("1. add - Add a new song")
        console.print("2. list - List all songs")
        console.print("3. search - Search songs")
        console.print("4. play - Mark a song as played")
        console.print("5. update - Update a song")
        console.print("6. delete - Delete a song")
        console.print("7. stats - Show user statistics")
        console.print("8. quit - Exit the application")
        
        choice = Prompt.ask("\nEnter your choice", choices=["1", "2", "3", "4", "5", "6", "7", "8"])
        
        if choice == "1":  # Add song
            title = Prompt.ask("Enter song title")
            artist = Prompt.ask("Enter artist name")
            genre = Prompt.ask("Enter genre (optional)", default="")
            year_str = Prompt.ask("Enter year (optional)", default="")
            
            year = None
            if year_str:
                try:
                    year = int(year_str)
                except ValueError:
                    console.print("[red]Invalid year format[/red]")
                    continue
            
            cli_commands.add_song(title, artist, user, genre or None, year)
        
        elif choice == "2":  # List songs
            cli_commands.list_songs(user)
        
        elif choice == "3":  # Search songs
            query = Prompt.ask("Enter search query")
            all_users = Confirm.ask("Search across all users?", default=False)
            cli_commands.search_songs(query, user, all_users)
        
        elif choice == "4":  # Play song
            song_id = Prompt.ask("Enter song ID")
            cli_commands.play_song(song_id, user)
        
        elif choice == "5":  # Update song
            song_id = Prompt.ask("Enter song ID")
            song = song_service.get_song_by_id(song_id, user)
            if not song:
                console.print("[red]✗ Song not found[/red]")
                continue
            
            console.print(f"Current song: {song.title} by {song.artist}")
            
            updates = {}
            new_title = Prompt.ask("Enter new title (or press Enter to keep current)", default=song.title)
            if new_title != song.title:
                updates['title'] = new_title
            
            new_artist = Prompt.ask("Enter new artist (or press Enter to keep current)", default=song.artist)
            if new_artist != song.artist:
                updates['artist'] = new_artist
            
            new_genre = Prompt.ask("Enter new genre (or press Enter to keep current)", default=song.genre or '')
            if new_genre != (song.genre or ''):
                updates['genre'] = new_genre or None
            
            new_year_str = Prompt.ask("Enter new year (or press Enter to keep current)", default=str(song.year or ''))
            if new_year_str != str(song.year or ''):
                try:
                    updates['year'] = int(new_year_str) if new_year_str else None
                except ValueError:
                    console.print("[red]Invalid year format[/red]")
                    continue
            
            if updates:
                cli_commands.update_song(song_id, user, **updates)
            else:
                console.print("[yellow]No changes made[/yellow]")
        
        elif choice == "6":  # Delete song
            song_id = Prompt.ask("Enter song ID")
            cli_commands.delete_song(song_id, user)
        
        elif choice == "7":  # Stats
            cli_commands.show_stats(user)
        
        elif choice == "8":  # Quit
            console.print("[green]Goodbye![/green]")
            break


if __name__ == '__main__':
    main()