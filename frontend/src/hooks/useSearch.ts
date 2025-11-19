import { useState } from "react";

export const useSearch = () => {
  const [isSearching, setIsSearching] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");

  const openSearch = () => {
    setIsSearching(true);
  };

  const closeSearch = () => {
    setIsSearching(false);
    setSearchQuery("");
  };

  const resetSearch = () => {
    setSearchQuery("");
  };

  return {
    isSearching,
    setIsSearching,
    searchQuery,
    setSearchQuery,
    openSearch,
    closeSearch,
    resetSearch,
  };
};
