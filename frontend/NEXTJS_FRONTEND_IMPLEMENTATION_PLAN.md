<!-- eef549cc-3ec8-4c2d-adea-60856d9379f1 33adbbcd-3392-4654-bf7c-cbc31b117baa -->
# NextJS Frontend Implementation Plan

**Created**: October 7, 2025  
**Plan Date**: October 7, 2024  
**Status**: Completed ✅

## Project Setup

- Initialize NextJS 14 project with JavaScript in `frontend/` folder
- Install dependencies: React, Next.js, shadcn/ui, Tailwind CSS, axios, react-youtube
- Configure `next.config.js` for API proxy to Python backend (localhost:8000)
- Set up Tailwind CSS with shadcn/ui configuration
- Create `.env.local` with `NEXT_PUBLIC_API_URL=http://localhost:8000`

## Directory Structure

Follow the specified structure:

- `src/components/` - Reusable UI components (forms, cards, modals, video player)
- `src/layouts/` - Navbar, Footer, AuthLayout components
- `src/pages/` - Next.js pages for routing (index, login, register, dashboard, songs)
- `src/styles/` - Global CSS and Tailwind imports
- `src/hooks/` - Custom hooks (useAuth, useSongs)
- `src/utils/` - Helper functions (extractYoutubeId, formatDate)
- `src/context/` - AuthContext for user state management
- `src/services/` - API service layer (authService, songService)
- `src/config/` - API base URL and configuration
- `src/constants/` - API endpoints, genres list

## Authentication System

### Context & Services

- **AuthContext** (`src/context/AuthContext.js`): Manage user state, login/logout/register functions using HTTP-only cookies (no localStorage needed)
- **authService** (`src/services/authService.js`): API calls for `/auth/register`, `/auth/login`, `/auth/me`, `/auth/logout`, `/auth/refresh` with `withCredentials: true`
- **useAuth hook** (`src/hooks/useAuth.js`): Convenience hook to access AuthContext

### Pages

- **Login Page** (`src/pages/login.js`): Form with username/email and password, redirect to dashboard on success
- **Register Page** (`src/pages/register.js`): Form with username, email, password, first_name, last_name, validation for password requirements
- **Protected Routes**: Create HOC or middleware to check authentication before rendering dashboard/songs pages

## Song Management Features

### Services

- **songService** (`src/services/songService.js`): API calls for:
- GET `/songs` - list user's songs
- POST `/songs` - create song
- PUT `/songs/{id}` - update song
- DELETE `/songs/{id}` - delete song
- GET `/songs/search?query=` - search songs
- POST `/songs/{id}/play` - mark as played

### Components

- **SongCard** (`src/components/SongCard.js`): Display song info (title, artist, genre, year), YouTube embed if link provided, edit/delete buttons
- **SongForm** (`src/components/SongForm.js`): Form for creating/editing songs with fields: title, artist, genre (dropdown), year, youtube_link (optional)
- **SongList** (`src/components/SongList.js`): Grid/list of SongCard components
- **YouTubePlayer** (`src/components/YouTubePlayer.js`): Embedded YouTube player using react-youtube library
- **SearchBar** (`src/components/SearchBar.js`): Search input with debouncing

### Pages

- **Dashboard** (`src/pages/dashboard.js`): Protected page showing user stats (total songs, top genres, recent songs)
- **Songs Page** (`src/pages/songs.js`): Main song management interface with search, add button, song list/grid
- **Song Detail Modal**: Modal/page showing full song details with YouTube player

## UI Components (shadcn/ui)

Install and configure these shadcn/ui components:

- Button, Input, Label, Card, Dialog, Form, Select, Alert, Avatar, Dropdown Menu
- Configure in `components/ui/` directory as per shadcn/ui convention

## Layout Components

- **Navbar** (`src/layouts/Navbar.js`): App logo, navigation links (Dashboard, Songs), user menu (profile, logout)
- **Footer** (`src/layouts/Footer.js`): Simple footer with copyright
- **MainLayout** (`src/layouts/MainLayout.js`): Wrapper with Navbar + children + Footer

## Utilities & Helpers

- **extractYoutubeId** (`src/utils/youtube.js`): Parse YouTube URL to extract video ID
- **formatDate** (`src/utils/date.js`): Format datetime strings for display
- **apiClient** (`src/utils/apiClient.js`): Axios instance with interceptors for JWT token attachment and refresh token handling

## Styling

- Use Tailwind CSS for utility classes
- shadcn/ui components for consistent design system
- Responsive design (mobile-first approach)
- Dark mode enabled by default (using next-themes for theme switching)

## Key Implementation Details

1. **YouTube Links**: Store in frontend state/localStorage, not persisted to backend (as per user preference)
2. **JWT Token**: Use HTTP-only cookies automatically sent by browser - configure axios with `withCredentials: true`, no manual token management needed
3. **Token Refresh**: Implement automatic token refresh using axios interceptors to call `/auth/refresh` when receiving 401 errors
4. **Error Handling**: Global error boundary, toast notifications for API errors
5. **Loading States**: Skeleton loaders for data fetching states
6. **Form Validation**: Client-side validation matching backend schema requirements

## File Creation Order

1. Configuration files (next.config.js, tailwind.config.js, .env.local)
2. Constants and utilities
3. API services layer
4. Context providers
5. Custom hooks
6. UI components (shadcn/ui)
7. Reusable components
8. Layout components
9. Pages (auth pages first, then protected pages)
10. Global styles

### To-dos

- [x] Initialize NextJS project with required dependencies and configuration
- [x] Create configuration files (next.config.js, tailwind.config, .env.local)
- [x] Create complete directory structure as specified
- [x] Implement constants and utility functions (API endpoints, YouTube parser, date formatter)
- [x] Create API service layer (apiClient, authService, songService)
- [x] Implement AuthContext and useAuth hook
- [x] Install and configure shadcn/ui components
- [x] Build reusable components (SongCard, SongForm, YouTubePlayer, SearchBar)
- [x] Create layout components (Navbar, Footer, MainLayout)
- [x] Implement authentication pages (login, register)
- [x] Create protected pages (dashboard, songs page)
- [x] Add global styles and finalize styling
