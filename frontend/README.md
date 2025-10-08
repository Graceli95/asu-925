# Songs App Frontend

A modern NextJS frontend application for managing your music collection with YouTube integration.

## Features

- **User Authentication**: Secure login and registration with JWT tokens
- **Song Management**: Add, edit, delete, and search songs
- **YouTube Integration**: Embed YouTube videos for your songs
- **Responsive Design**: Works on desktop and mobile devices
- **Dark Mode**: Built-in dark mode support
- **Real-time Search**: Debounced search with instant results

## Tech Stack

- **NextJS 14**: React framework with App Router
- **React 18**: Modern React with hooks
- **Tailwind CSS**: Utility-first CSS framework
- **shadcn/ui**: Beautiful, accessible UI components
- **Axios**: HTTP client for API requests
- **Lucide React**: Icon library

## Getting Started

### Prerequisites

- Node.js 18+ 
- npm or yarn
- Backend API running on `http://localhost:8000`

### Installation

1. Install dependencies:
```bash
npm install
```

2. Create environment file:
```bash
# Create .env.local file
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local
```

3. Start the development server:
```bash
npm run dev
```

4. Open [http://localhost:3000](http://localhost:3000) in your browser.

## Project Structure

```
src/
├── components/          # Reusable UI components
│   ├── ui/             # shadcn/ui components
│   ├── SongCard.js     # Song display component
│   ├── SongForm.js     # Song creation/editing form
│   ├── SongList.js     # Songs grid/list component
│   ├── SearchBar.js    # Search input with debouncing
│   └── YouTubePlayer.js # YouTube video player
├── layouts/            # Layout components
│   ├── Navbar.js       # Navigation bar
│   ├── Footer.js       # Footer component
│   └── MainLayout.js   # Main layout wrapper
├── pages/              # Next.js pages
│   ├── _app.js         # App wrapper with providers
│   ├── index.js        # Home page
│   ├── login.js        # Login page
│   ├── register.js      # Registration page
│   ├── dashboard.js    # Dashboard page
│   └── songs.js        # Songs management page
├── context/            # React Context providers
│   └── AuthContext.js  # Authentication context
├── hooks/              # Custom React hooks
│   └── useSongs.js     # Songs management hook
├── services/           # API service layer
│   ├── authService.js  # Authentication API calls
│   └── songService.js  # Songs API calls
├── utils/              # Utility functions
│   ├── apiClient.js    # Axios configuration
│   ├── youtube.js      # YouTube URL utilities
│   ├── date.js         # Date formatting utilities
│   └── index.js        # General utilities
├── constants/          # App constants
│   └── index.js        # API endpoints, genres, etc.
└── styles/             # Global styles
    └── globals.css     # Tailwind CSS imports
```

## API Integration

The frontend communicates with the Python FastAPI backend using:

- **HTTP-only Cookies**: For secure authentication
- **Axios Interceptors**: For automatic token refresh
- **Error Handling**: Comprehensive error management

### Authentication Flow

1. User logs in with username/email and password
2. Backend sets HTTP-only cookies (access_token, refresh_token)
3. Frontend automatically includes cookies in all requests
4. Axios interceptor handles token refresh on 401 errors

## Key Features

### Song Management
- Create, read, update, delete songs
- Search songs by title or artist
- Filter by genre and year
- Mark songs as played

### YouTube Integration
- Add YouTube links to songs (stored locally)
- Embed YouTube videos in song cards
- Extract video IDs from various YouTube URL formats
- Display video thumbnails

### User Experience
- Responsive design for all screen sizes
- Loading states and error handling
- Form validation with helpful error messages
- Debounced search for better performance

## Environment Variables

Create a `.env.local` file in the root directory:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run start` - Start production server
- `npm run lint` - Run ESLint

## Contributing

1. Follow the existing code structure
2. Use TypeScript for type safety
3. Follow the component naming conventions
4. Add proper error handling
5. Test on multiple screen sizes

## License

This project is part of the Songs App application.