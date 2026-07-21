import { useState, useRef, useEffect, useMemo, useCallback } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { HiOutlineMagnifyingGlass, HiOutlineXMark, HiOutlinePlus } from 'react-icons/hi2'

const KEYBOARD = {
  ENTER: 'Enter',
  ESCAPE: 'Escape',
  ARROW_UP: 'ArrowUp',
  ARROW_DOWN: 'ArrowDown',
  BACKSPACE: 'Backspace',
  TAB: 'Tab',
}

export default function SearchableMultiSelect({
  label,
  categories = [],
  value = [],
  onChange,
  placeholder = 'Search...',
  maxSelections = 20,
  allowCustom = true,
  customPlaceholder = 'Type a custom value...',
  emptyMessage = 'No results found',
  error,
  required,
}) {
  const [inputValue, setInputValue] = useState('')
  const [isOpen, setIsOpen] = useState(false)
  const [highlightedIndex, setHighlightedIndex] = useState(-1)
  const [recentlySelected, setRecentlySelected] = useState([])
  const inputRef = useRef(null)
  const dropdownRef = useRef(null)
  const listRef = useRef(null)

  // Validate and filter categories at the top
  const validCategories = useMemo(() => {
    return categories.filter((cat) => {
      if (!cat || typeof cat !== 'object' || !cat.name) {
        console.error('Invalid skills category (missing name):', cat)
        return false
      }
      if (!Array.isArray(cat.skills)) {
        console.error(`Invalid skills category "${cat.name}": skills is not an array`, cat)
        return false
      }
      return true
    })
  }, [categories])

  // Flatten all items with category info
  const allItems = useMemo(() => {
    const items = []
    for (const cat of validCategories) {
      for (const skill of cat.skills) {
        items.push({ name: skill, category: cat.name })
      }
    }
    return items
  }, [validCategories])

  // Filter items based on search query
  const filteredCategories = useMemo(() => {
    const q = inputValue.trim().toLowerCase()
    if (!q) {
      // Show recently selected first, then all categories
      const result = []

      if (recentlySelected.length > 0) {
        result.push({
          name: 'Recently Selected',
          skills: recentlySelected.filter((s) => !value.includes(s)),
        })
      }

      for (const cat of validCategories) {
        const remaining = cat.skills.filter((s) => !value.includes(s))
        if (remaining.length > 0) {
          result.push({ name: cat.name, skills: remaining })
        }
      }
      return result
    }

    const result = []
    for (const cat of validCategories) {
      const matches = cat.skills.filter(
        (s) =>
          s.toLowerCase().includes(q) && !value.includes(s)
      )
      if (matches.length > 0) {
        result.push({ name: cat.name, skills: matches })
      }
    }
    return result
  }, [inputValue, validCategories, value, recentlySelected])

  // Build flat list for keyboard navigation
  const flatOptions = useMemo(() => {
    const opts = []
    for (const cat of filteredCategories) {
      for (const s of cat.skills) {
        opts.push(s)
      }
    }
    // Custom option at the end
    if (allowCustom && inputValue.trim() && !allItems.some((i) => i.name.toLowerCase() === inputValue.trim().toLowerCase())) {
      opts.push(`__custom__${inputValue.trim()}`)
    }
    return opts
  }, [filteredCategories, inputValue, allowCustom, allItems])

  // Close dropdown on outside click
  useEffect(() => {
    function handleClick(e) {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target)) {
        setIsOpen(false)
      }
    }
    document.addEventListener('mousedown', handleClick)
    return () => document.removeEventListener('mousedown', handleClick)
  }, [])

  // Scroll highlighted item into view
  useEffect(() => {
    if (highlightedIndex >= 0 && listRef.current) {
      const item = listRef.current.querySelector(`[data-index="${highlightedIndex}"]`)
      if (item) item.scrollIntoView({ block: 'nearest' })
    }
  }, [highlightedIndex])

  const addItem = useCallback(
    (name) => {
      const trimmed = name.trim()
      if (!trimmed) return
      if (value.some((v) => v.toLowerCase() === trimmed.toLowerCase())) return
      if (value.length >= maxSelections) return

      onChange([...value, trimmed])
      setRecentlySelected((prev) => {
        const next = [trimmed, ...prev.filter((s) => s !== trimmed)]
        return next.slice(0, 10)
      })
      setInputValue('')
      setHighlightedIndex(-1)
      inputRef.current?.focus()
    },
    [value, onChange, maxSelections]
  )

  const removeItem = useCallback(
    (name) => {
      onChange(value.filter((v) => v !== name))
    },
    [value, onChange]
  )

  const handleKeyDown = useCallback(
    (e) => {
      if (e.key === KEYBOARD.ENTER) {
        e.preventDefault()
        if (highlightedIndex >= 0 && highlightedIndex < flatOptions.length) {
          const opt = flatOptions[highlightedIndex]
          if (opt.startsWith('__custom__')) {
            addItem(opt.replace('__custom__', ''))
          } else {
            addItem(opt)
          }
        } else if (allowCustom && inputValue.trim()) {
          addItem(inputValue.trim())
        }
      } else if (e.key === KEYBOARD.ESCAPE) {
        setIsOpen(false)
      } else if (e.key === KEYBOARD.ARROW_DOWN) {
        e.preventDefault()
        setHighlightedIndex((prev) =>
          prev < flatOptions.length - 1 ? prev + 1 : 0
        )
      } else if (e.key === KEYBOARD.ARROW_UP) {
        e.preventDefault()
        setHighlightedIndex((prev) =>
          prev > 0 ? prev - 1 : flatOptions.length - 1
        )
      } else if (e.key === KEYBOARD.BACKSPACE && !inputValue && value.length > 0) {
        removeItem(value[value.length - 1])
      }
    },
    [highlightedIndex, flatOptions, addItem, inputValue, allowCustom, value, removeItem]
  )

  const showCustomOption =
    allowCustom &&
    inputValue.trim() &&
    !allItems.some((i) => i.name.toLowerCase() === inputValue.trim().toLowerCase()) &&
    !value.some((v) => v.toLowerCase() === inputValue.trim().toLowerCase())

  const atLimit = value.length >= maxSelections

  return (
    <div className="space-y-2" ref={dropdownRef}>
      <label className="block text-sm font-medium mb-1.5">
        {label}
        {required && <span className="text-red-500 ml-0.5">*</span>}
        <span className="text-xs font-normal text-gray-400 dark:text-gray-500 ml-2">
          ({value.length}/{maxSelections})
        </span>
      </label>

      {/* Selected chips + input */}
      <div
        className={`input-field flex flex-wrap gap-2 min-h-[48px] !py-2 cursor-text focus-within:ring-2 focus-within:ring-primary-500 ${
          error ? 'ring-2 ring-red-500' : ''
        } ${atLimit ? 'opacity-70' : ''}`}
        onClick={() => inputRef.current?.focus()}
      >
        <AnimatePresence mode="popLayout">
          {value.map((tag) => (
            <motion.span
              key={tag}
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.8 }}
              layout
              className="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg bg-primary-100 dark:bg-primary-900/30 text-primary-700 dark:text-primary-300 text-sm font-medium"
            >
              {tag}
              <button
                type="button"
                onClick={(e) => {
                  e.stopPropagation()
                  removeItem(tag)
                }}
                className="hover:text-red-500 ml-0.5"
              >
                <HiOutlineXMark className="w-3.5 h-3.5" />
              </button>
            </motion.span>
          ))}
        </AnimatePresence>
        {!atLimit && (
          <input
            ref={inputRef}
            type="text"
            value={inputValue}
            onChange={(e) => {
              setInputValue(e.target.value)
              setIsOpen(true)
              setHighlightedIndex(-1)
            }}
            onFocus={() => setIsOpen(true)}
            onKeyDown={handleKeyDown}
            placeholder={value.length === 0 ? placeholder : ''}
            className="flex-1 min-w-[120px] bg-transparent outline-none text-sm"
            disabled={atLimit}
          />
        )}
      </div>

      {/* Dropdown */}
      <AnimatePresence>
        {isOpen && (filteredCategories.length > 0 || showCustomOption) && (
          <motion.div
            initial={{ opacity: 0, y: -8 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -8 }}
            transition={{ duration: 0.15 }}
            className="relative z-30"
          >
            <div className="absolute top-0 left-0 right-0 max-h-72 overflow-y-auto bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl shadow-xl mt-1 p-2">
              {/* Search icon inside dropdown */}
              <div className="sticky top-0 z-10 pb-2 bg-white dark:bg-gray-800">
                <div className="relative">
                  <HiOutlineMagnifyingGlass className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                  <input
                    type="text"
                    value={inputValue}
                    onChange={(e) => {
                      setInputValue(e.target.value)
                      setHighlightedIndex(-1)
                    }}
                    onKeyDown={handleKeyDown}
                    placeholder={customPlaceholder}
                    className="w-full pl-9 pr-3 py-2 text-sm bg-gray-50 dark:bg-gray-700/50 border border-gray-200 dark:border-gray-600 rounded-lg outline-none focus:border-primary-500 dark:focus:border-primary-500"
                    autoFocus
                  />
                </div>
              </div>

              <div ref={listRef} className="overflow-y-auto max-h-56">
                {filteredCategories.map((cat) => (
                  <div key={cat.name}>
                    <div className="px-3 py-1.5 text-[11px] font-semibold uppercase tracking-wider text-gray-400 dark:text-gray-500 sticky top-0 bg-white dark:bg-gray-800">
                      {cat.name}
                    </div>
                    {(cat.skills ?? []).map((skill) => {
                      const flatIdx = flatOptions.indexOf(skill)
                      const isHighlighted = flatIdx === highlightedIndex
                      return (
                        <button
                          key={skill}
                          type="button"
                          data-index={flatIdx}
                          onMouseEnter={() => setHighlightedIndex(flatIdx)}
                          onMouseDown={(e) => {
                            e.preventDefault()
                            addItem(skill)
                          }}
                          className={`w-full text-left px-3 py-2 rounded-lg text-sm transition-colors ${
                            isHighlighted
                              ? 'bg-primary-100 dark:bg-primary-900/30 text-primary-700 dark:text-primary-300'
                              : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700/50'
                          }`}
                        >
                          {skill}
                        </button>
                      )
                    })}
                  </div>
                ))}

                {/* Custom option */}
                {showCustomOption && (
                  <div className="border-t border-gray-200 dark:border-gray-700 mt-1 pt-1">
                    <button
                      type="button"
                      data-index={flatOptions.length - 1}
                      onMouseEnter={() => setHighlightedIndex(flatOptions.length - 1)}
                      onMouseDown={(e) => {
                        e.preventDefault()
                        addItem(inputValue.trim())
                      }}
                      className={`w-full text-left px-3 py-2 rounded-lg text-sm flex items-center gap-2 transition-colors ${
                        highlightedIndex === flatOptions.length - 1
                          ? 'bg-primary-100 dark:bg-primary-900/30 text-primary-700 dark:text-primary-300'
                          : 'text-primary-600 dark:text-primary-400 hover:bg-primary-50 dark:hover:bg-primary-900/20'
                      }`}
                    >
                      <HiOutlinePlus className="w-4 h-4 shrink-0" />
                      <span>Add &quot;{inputValue.trim()}&quot;</span>
                    </button>
                  </div>
                )}
              </div>

              {filteredCategories.length === 0 && !showCustomOption && (
                <div className="px-3 py-4 text-sm text-gray-400 dark:text-gray-500 text-center">
                  {emptyMessage}
                </div>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Error message */}
      {error && <p className="text-red-500 text-xs mt-1">{error.message}</p>}
    </div>
  )
}
