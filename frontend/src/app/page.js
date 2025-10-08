import React from 'react';
import Link from 'next/link';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Music, Play, Users, Star } from 'lucide-react';

/**
 * Home page component
 */
export default function HomePage() {
  return (
    <div className="min-h-screen bg-background">
      {/* Hero Section */}
      <div className="container mx-auto px-4 py-16">
        <div className="text-center space-y-8">
          <div className="space-y-4">
            <div className="flex items-center justify-center gap-3">
              <Music className="h-12 w-12 text-primary" />
              <h1 className="text-5xl font-bold">Songs App</h1>
            </div>
            <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
              Organize, discover, and enjoy your music collection. 
              Create playlists, track your favorites, and never lose a song again.
            </p>
          </div>

          <div className="flex items-center justify-center gap-4">
            <Link href="/register">
              <Button size="lg" className="flex items-center gap-2">
                <Users className="h-5 w-5" />
                Get Started
              </Button>
            </Link>
            <Link href="/login">
              <Button variant="outline" size="lg" className="flex items-center gap-2">
                <Play className="h-5 w-5" />
                Sign In
              </Button>
            </Link>
          </div>
        </div>
      </div>

      {/* Features Section */}
      <div className="container mx-auto px-4 py-16">
        <div className="text-center mb-12">
          <h2 className="text-3xl font-bold mb-4">Why Choose Songs App?</h2>
          <p className="text-muted-foreground max-w-2xl mx-auto">
            Discover the features that make managing your music collection effortless and enjoyable.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <Card>
            <CardHeader className="text-center">
              <div className="mx-auto mb-4 p-3 bg-primary/10 rounded-full w-fit">
                <Music className="h-8 w-8 text-primary" />
              </div>
              <CardTitle>Organize Your Music</CardTitle>
            </CardHeader>
            <CardContent className="text-center">
              <p className="text-muted-foreground">
                Keep track of all your songs with detailed information including artist, genre, and year.
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="text-center">
              <div className="mx-auto mb-4 p-3 bg-primary/10 rounded-full w-fit">
                <Play className="h-8 w-8 text-primary" />
              </div>
              <CardTitle>YouTube Integration</CardTitle>
            </CardHeader>
            <CardContent className="text-center">
              <p className="text-muted-foreground">
                Add YouTube links to your songs and watch videos directly from your collection.
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="text-center">
              <div className="mx-auto mb-4 p-3 bg-primary/10 rounded-full w-fit">
                <Star className="h-8 w-8 text-primary" />
              </div>
              <CardTitle>Smart Search</CardTitle>
            </CardHeader>
            <CardContent className="text-center">
              <p className="text-muted-foreground">
                Find your favorite songs instantly with our powerful search functionality.
              </p>
            </CardContent>
          </Card>
        </div>
      </div>

      {/* CTA Section */}
      <div className="container mx-auto px-4 py-16">
        <div className="text-center space-y-6">
          <h2 className="text-3xl font-bold">Ready to Get Started?</h2>
          <p className="text-muted-foreground max-w-xl mx-auto">
            Join thousands of music lovers who trust Songs App to organize their collections.
          </p>
          <Link href="/register">
            <Button size="lg" className="flex items-center gap-2 mx-auto">
              <Users className="h-5 w-5" />
              Create Your Account
            </Button>
          </Link>
        </div>
      </div>

      {/* Footer */}
      <footer className="border-t bg-background">
        <div className="container mx-auto px-4 py-8">
          <div className="text-center text-muted-foreground">
            <p>&copy; {new Date().getFullYear()} Songs App. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  );
}
