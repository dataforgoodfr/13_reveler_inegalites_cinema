import { useState, useEffect } from 'react';

export function useMediaQuery(query: string) {
  const [matches, setMatches] = useState(() => {
    if (window) {
      return window.matchMedia(query).matches;
    }
    return false;
  });

  useEffect(() => {
    if (!window) {
      return;
    }
    const mediaQueryList = window.matchMedia(query);
    const listener = (e: MediaQueryListEvent): void => setMatches(e.matches);

    mediaQueryList.addEventListener('change', listener);
    return () => mediaQueryList.removeEventListener('change', listener);
  }, [query]);

  return matches;
}
