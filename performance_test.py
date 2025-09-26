#!/usr/bin/env python3
"""
Performance test for the Songs CLI application
Tests adding 1000 songs and measures performance
"""

import time
import os
from typing import List, Dict, Any
from rich.console import Console
from rich.progress import Progress, TaskID
from rich.table import Table
from db.songs_db import SongsDatabase
from service import SongService

console = Console()

# Test data for song generation
ARTISTS = [
    "The Beatles", "Queen", "Led Zeppelin", "Pink Floyd", "The Rolling Stones",
    "AC/DC", "Michael Jackson", "Madonna", "Prince", "David Bowie",
    "The Who", "Eagles", "Fleetwood Mac", "Nirvana", "Radiohead",
    "U2", "Coldplay", "Red Hot Chili Peppers", "Green Day", "Pearl Jam",
    "Metallica", "Black Sabbath", "Deep Purple", "The Doors", "Jimi Hendrix",
    "Bob Dylan", "Johnny Cash", "Elvis Presley", "Frank Sinatra", "Ray Charles"
]

SONG_PREFIXES = [
    "Love Song", "Rock Anthem", "Blues Track", "Dance Beat", "Ballad",
    "Summer Hit", "Winter Song", "Night Music", "Morning Light", "Sunset",
    "Dreams", "Memories", "Freedom", "Journey", "Adventure",
    "Heart", "Soul", "Spirit", "Energy", "Power",
    "Mystery", "Wonder", "Magic", "Thunder", "Lightning",
    "Fire", "Water", "Earth", "Air", "Sky"
]

GENRES = [
    "Rock", "Pop", "Jazz", "Blues", "Classical",
    "Electronic", "Hip Hop", "R&B", "Country", "Folk",
    "Reggae", "Metal", "Punk", "Alternative", "Indie"
]

YEARS = list(range(1950, 2024))

def generate_test_songs(count: int, user: str) -> List[Dict[str, Any]]:
    """Generate test song data"""
    import random
    
    songs = []
    for i in range(count):
        artist = random.choice(ARTISTS)
        prefix = random.choice(SONG_PREFIXES)
        title = f"{prefix} #{i+1:04d}"
        genre = random.choice(GENRES)
        year = random.choice(YEARS)
        
        songs.append({
            "title": title,
            "artist": artist,
            "user": user,
            "genre": genre,
            "year": year
        })
    
    return songs

def cleanup_test_data(service: SongService, user: str, console: Console):
    """Clean up test data from database and files"""
    console.print("[yellow]Cleaning up test data...[/yellow]")
    
    # Get all songs for the test user
    songs = service.get_songs(user)
    
    with Progress() as progress:
        task = progress.add_task("[red]Deleting...", total=len(songs))
        
        for song in songs:
            service.delete_song(str(song._id), user)
            progress.update(task, advance=1)
    
    console.print(f"[green]Cleaned up {len(songs)} test songs[/green]")

def run_performance_test(song_count: int = 1000) -> Dict[str, Any]:
    """Run the performance test"""
    console.print(f"[bold blue]🎵 Songs CLI Performance Test[/bold blue]")
    console.print(f"[dim]Testing with {song_count} song additions[/dim]\n")
    
    test_user = "PerformanceTestUser"
    
    # Initialize services
    try:
        db = SongsDatabase()
        service = SongService(db)
    except Exception as e:
        console.print(f"[red]Error initializing services: {e}[/red]")
        return {"success": False, "error": str(e)}
    
    # Clean up any existing test data
    cleanup_test_data(service, test_user, console)
    
    # Generate test data
    console.print("[yellow]Generating test data...[/yellow]")
    test_songs = generate_test_songs(song_count, test_user)
    console.print(f"[green]Generated {len(test_songs)} test songs[/green]\n")
    
    # Performance metrics
    metrics = {
        "total_songs": song_count,
        "successful_additions": 0,
        "failed_additions": 0,
        "total_time": 0,
        "average_time_per_song": 0,
        "songs_per_second": 0,
        "file_creation_time": 0,
        "database_time": 0
    }
    
    # Run the test
    console.print("[bold green]Starting performance test...[/bold green]")
    
    start_time = time.time()
    
    with Progress() as progress:
        task = progress.add_task("[green]Adding songs...", total=song_count)
        
        for i, song_data in enumerate(test_songs):
            song_start = time.time()
            
            result = service.add_song(
                song_data["title"],
                song_data["artist"],
                song_data["user"],
                song_data["genre"],
                song_data["year"]
            )
            
            song_end = time.time()
            
            if result["success"]:
                metrics["successful_additions"] += 1
            else:
                metrics["failed_additions"] += 1
                console.print(f"[red]Failed to add song {i+1}: {result['message']}[/red]")
            
            progress.update(task, advance=1)
            
            # Update progress every 100 songs
            if (i + 1) % 100 == 0:
                elapsed = time.time() - start_time
                rate = (i + 1) / elapsed
                progress.console.print(f"[dim]Progress: {i+1}/{song_count} songs, Rate: {rate:.2f} songs/sec[/dim]")
    
    end_time = time.time()
    
    # Calculate final metrics
    metrics["total_time"] = end_time - start_time
    if metrics["successful_additions"] > 0:
        metrics["average_time_per_song"] = metrics["total_time"] / metrics["successful_additions"]
        metrics["songs_per_second"] = metrics["successful_additions"] / metrics["total_time"]
    
    # Display results
    display_results(metrics, console)
    
    # Verify file creation
    verify_file_creation(service, test_user, console)
    
    # Ask if user wants to clean up
    should_cleanup = console.input("\n[yellow]Clean up test data? (y/N): [/yellow]").lower().strip()
    if should_cleanup in ['y', 'yes']:
        cleanup_test_data(service, test_user, console)
    else:
        console.print(f"[blue]Test data retained for user: {test_user}[/blue]")
    
    return metrics

def display_results(metrics: Dict[str, Any], console: Console):
    """Display performance test results"""
    console.print("\n[bold green]Performance Test Results[/bold green]")
    console.print("=" * 50)
    
    # Create results table
    table = Table(show_header=True, header_style="bold blue")
    table.add_column("Metric", style="cyan", no_wrap=True)
    table.add_column("Value", style="green")
    
    table.add_row("Total Songs", str(metrics["total_songs"]))
    table.add_row("Successful Additions", str(metrics["successful_additions"]))
    table.add_row("Failed Additions", str(metrics["failed_additions"]))
    table.add_row("Success Rate", f"{(metrics['successful_additions'] / metrics['total_songs']) * 100:.1f}%")
    table.add_row("Total Time", f"{metrics['total_time']:.2f} seconds")
    table.add_row("Average Time per Song", f"{metrics['average_time_per_song']:.4f} seconds")
    table.add_row("Songs per Second", f"{metrics['songs_per_second']:.2f}")
    
    console.print(table)
    
    # Performance assessment
    console.print("\n[bold yellow]Performance Assessment:[/bold yellow]")
    if metrics["songs_per_second"] > 10:
        console.print("[green]✓ Excellent performance (>10 songs/sec)[/green]")
    elif metrics["songs_per_second"] > 5:
        console.print("[yellow]✓ Good performance (>5 songs/sec)[/yellow]")
    elif metrics["songs_per_second"] > 2:
        console.print("[orange3]⚠ Fair performance (>2 songs/sec)[/orange3]")
    else:
        console.print("[red]⚠ Poor performance (<2 songs/sec)[/red]")

def verify_file_creation(service: SongService, test_user: str, console: Console):
    """Verify that files were created properly"""
    console.print("\n[yellow]Verifying file creation...[/yellow]")
    
    songs = service.get_songs(test_user)
    assets_dir = "assets"
    
    if not os.path.exists(assets_dir):
        console.print("[red]❌ Assets directory not found[/red]")
        return
    
    files_found = 0
    files_missing = 0
    
    for song in songs[:10]:  # Check first 10 songs for efficiency
        expected_filename = f"{song.artist} - {song.title}.txt"
        # Sanitize the filename
        import re
        sanitized = re.sub(r'[<>:"/\\|?*]', '_', expected_filename)
        sanitized = re.sub(r'_+', '_', sanitized)
        sanitized = sanitized.strip('_ ')
        
        filepath = os.path.join(assets_dir, sanitized)
        if os.path.exists(filepath):
            files_found += 1
        else:
            files_missing += 1
    
    console.print(f"[green]✓ Files found: {files_found}/10 (sample check)[/green]")
    if files_missing > 0:
        console.print(f"[red]❌ Files missing: {files_missing}/10[/red]")
    
    # Count total files in assets directory
    total_files = len([f for f in os.listdir(assets_dir) if f.endswith('.txt')])
    console.print(f"[blue]Total .txt files in assets: {total_files}[/blue]")

def main():
    """Main function to run the performance test"""
    try:
        # You can change this number to test different volumes
        song_count = 1000
        
        console.print(f"[bold]Starting performance test with {song_count} songs...[/bold]\n")
        
        # Run the test
        results = run_performance_test(song_count)
        
        if results.get("success") == False:
            console.print(f"[red]Test failed: {results.get('error')}[/red]")
            return
        
        console.print("\n[bold green]Performance test completed! 🎉[/bold green]")
        
    except KeyboardInterrupt:
        console.print("\n[yellow]Performance test interrupted by user[/yellow]")
    except Exception as e:
        console.print(f"\n[red]Error during performance test: {e}[/red]")

if __name__ == "__main__":
    main()
