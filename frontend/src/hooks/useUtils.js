import { useState, useEffect, useRef } from 'react'

/**
 * Debounce a value by a given delay
 * @param {*} value - The value to debounce
 * @param {number} delay - Delay in milliseconds
 * @returns {*} The debounced value
 */
export function useDebounce(value, delay = 300) {
  const [debouncedValue, setDebouncedValue] = useState(value)

  useEffect(() => {
    const timer = setTimeout(() => setDebouncedValue(value), delay)
    return () => clearTimeout(timer)
  }, [value, delay])

  return debouncedValue
}

/**
 * Persist state to localStorage
 * @param {string} key - Storage key
 * @param {*} initialValue - Initial value if no stored value exists
 * @returns {[*, Function]} State and setter tuple
 */
export function useLocalStorage(key, initialValue) {
  const [storedValue, setStoredValue] = useState(() => {
    try {
      const item = window.localStorage.getItem(key)
      return item ? JSON.parse(item) : initialValue
    } catch (error) {
      console.warn(`Error reading localStorage key "${key}":`, error)
      return initialValue
    }
  })

  const setValue = (value) => {
    try {
      const valueToStore = value instanceof Function ? value(storedValue) : value
      setStoredValue(valueToStore)
      window.localStorage.setItem(key, JSON.stringify(valueToStore))
    } catch (error) {
      console.warn(`Error setting localStorage key "${key}":`, error)
    }
  }

  return [storedValue, setValue]
}

/**
 * Search hook with debounced query and filtering
 * @param {Array} items - Items to search through
 * @param {Array} searchKeys - Object keys to search within
 * @param {number} debounceMs - Debounce delay
 * @returns {Object} Search state and handlers
 */
export function useSearch(items = [], searchKeys = ['name'], debounceMs = 300) {
  const [query, setQuery] = useState('')
  const debouncedQuery = useDebounce(query, debounceMs)
  const [isSearching, setIsSearching] = useState(false)

  const results = debouncedQuery.trim()
    ? items.filter(item =>
        searchKeys.some(key => {
          const value = item[key]
          return value && String(value).toLowerCase().includes(debouncedQuery.toLowerCase())
        })
      )
    : items

  useEffect(() => {
    if (query !== debouncedQuery) {
      setIsSearching(true)
    } else {
      setIsSearching(false)
    }
  }, [query, debouncedQuery])

  return {
    query,
    setQuery,
    results,
    isSearching,
    resultCount: results.length,
    hasQuery: debouncedQuery.trim().length > 0,
  }
}

/**
 * Click outside detector for dropdowns and modals
 * @param {Function} handler - Callback when clicked outside
 * @returns {React.RefObject} Ref to attach to the element
 */
export function useClickOutside(handler) {
  const ref = useRef(null)

  useEffect(() => {
    const listener = (event) => {
      if (!ref.current || ref.current.contains(event.target)) return
      handler(event)
    }

    document.addEventListener('mousedown', listener)
    document.addEventListener('touchstart', listener)
    return () => {
      document.removeEventListener('mousedown', listener)
      document.removeEventListener('touchstart', listener)
    }
  }, [handler])

  return ref
}

/**
 * Window size tracker for responsive logic
 * @returns {Object} Window width, height, and breakpoint flags
 */
export function useWindowSize() {
  const [size, setSize] = useState({
    width: window.innerWidth,
    height: window.innerHeight,
  })

  useEffect(() => {
    const handleResize = () => setSize({ width: window.innerWidth, height: window.innerHeight })
    window.addEventListener('resize', handleResize)
    return () => window.removeEventListener('resize', handleResize)
  }, [])

  return {
    ...size,
    isMobile: size.width < 768,
    isTablet: size.width >= 768 && size.width < 1024,
    isDesktop: size.width >= 1024,
  }
}
