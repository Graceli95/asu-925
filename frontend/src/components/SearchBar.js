import React, { useState, useEffect } from 'react';
import { Input } from './ui/input';
import { Button } from './ui/button';
import { Search, X } from 'lucide-react';
import { debounce } from '../utils/date';

/**
 * SearchBar component with debounced search functionality
 * @param {Object} props - Component props
 * @param {Function} props.onSearch - Search callback
 * @param {string} props.placeholder - Placeholder text
 * @param {string} props.value - Current search value
 * @param {boolean} props.loading - Loading state
 */
export function SearchBar({ onSearch, placeholder = "Search songs...", value = "", loading = false }) {
  const [searchQuery, setSearchQuery] = useState(value);

  // Debounced search function
  const debouncedSearch = debounce((query) => {
    if (onSearch) {
      onSearch(query);
    }
  }, 300);

  // Handle input change
  const handleChange = (e) => {
    const query = e.target.value;
    setSearchQuery(query);
    debouncedSearch(query);
  };

  // Handle clear search
  const handleClear = () => {
    setSearchQuery('');
    if (onSearch) {
      onSearch('');
    }
  };

  // Update local state when value prop changes
  useEffect(() => {
    setSearchQuery(value);
  }, [value]);

  return (
    <div className="relative w-full max-w-md">
      <div className="relative">
        <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
        <Input
          type="text"
          placeholder={placeholder}
          value={searchQuery}
          onChange={handleChange}
          className="pl-10 pr-10"
          disabled={loading}
        />
        {searchQuery && (
          <Button
            variant="ghost"
            size="icon"
            onClick={handleClear}
            className="absolute right-1 top-1/2 transform -translate-y-1/2 h-8 w-8"
          >
            <X className="h-4 w-4" />
          </Button>
        )}
      </div>
    </div>
  );
}
