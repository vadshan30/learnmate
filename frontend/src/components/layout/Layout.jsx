import { useState } from 'react'
import { Link, NavLink, Outlet, useLocation } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import {
  HiOutlineHome, HiOutlineUser, HiOutlineMap, HiOutlineChatBubbleLeftEllipsis,
  HiOutlineBookOpen, HiOutlineChartBar, HiOutlineCog6Tooth, HiOutlineBars3,
  HiOutlineXMark, HiOutlineSun, HiOutlineMoon, HiOutlineArrowLeftOnRectangle,
} from 'react-icons/hi2'
import { useTheme } from '../../context/ThemeContext'
import { useApp } from '../../context/AppContext'

const navItems = [
  { to: '/dashboard', label: 'Dashboard', icon: HiOutlineHome },
  { to: '/profile', label: 'Profile', icon: HiOutlineUser },
  { to: '/roadmap', label: 'Roadmap', icon: HiOutlineMap },
  { to: '/chat', label: 'AI Mentor', icon: HiOutlineChatBubbleLeftEllipsis },
  { to: '/resources', label: 'Resources', icon: HiOutlineBookOpen },
  { to: '/progress', label: 'Progress', icon: HiOutlineChartBar },
  { to: '/settings', label: 'Settings', icon: HiOutlineCog6Tooth },
]

function Sidebar({ collapsed, onToggle }) {
  const location = useLocation()

  return (
    <aside
      className={`hidden lg:flex flex-col fixed left-0 top-0 h-screen z-30 bg-white dark:bg-gray-900 border-r border-gray-200 dark:border-gray-800 transition-all duration-300 ${
        collapsed ? 'w-[72px]' : 'w-64'
      }`}
    >
      <div className={`flex items-center h-16 border-b border-gray-200 dark:border-gray-800 ${collapsed ? 'justify-center px-2' : 'px-6'}`}>
        {!collapsed && (
          <Link to="/dashboard" className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg gradient-bg flex items-center justify-center">
              <span className="text-white font-bold text-sm">LM</span>
            </div>
            <span className="font-display font-bold text-lg gradient-text">LearnMate</span>
          </Link>
        )}
        {collapsed && (
          <Link to="/dashboard" className="w-8 h-8 rounded-lg gradient-bg flex items-center justify-center">
            <span className="text-white font-bold text-sm">LM</span>
          </Link>
        )}
      </div>

      <nav className="flex-1 py-4 px-3 space-y-1">
        {navItems.map((item) => {
          const active = location.pathname === item.to
          return (
            <NavLink
              key={item.to}
              to={item.to}
              className={`flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all duration-200 group ${
                active
                  ? 'bg-primary-50 dark:bg-primary-950/50 text-primary-600 dark:text-primary-400'
                  : 'text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800'
              } ${collapsed ? 'justify-center' : ''}`}
              title={collapsed ? item.label : undefined}
            >
              <item.icon className={`w-5 h-5 flex-shrink-0 ${active ? 'text-primary-600 dark:text-primary-400' : ''}`} />
              {!collapsed && <span>{item.label}</span>}
            </NavLink>
          )
        })}
      </nav>

      <div className="p-3 border-t border-gray-200 dark:border-gray-800">
        <button
          onClick={onToggle}
          className="flex items-center gap-3 w-full px-3 py-2.5 rounded-xl text-sm font-medium text-gray-500 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
        >
          <HiOutlineArrowLeftOnRectangle className={`w-5 h-5 transition-transform duration-300 ${collapsed ? 'rotate-180' : ''}`} />
          {!collapsed && <span>Collapse</span>}
        </button>
      </div>
    </aside>
  )
}

function Navbar({ onMenuOpen }) {
  const { dark, toggle } = useTheme()
  const { student } = useApp()

  return (
    <header className="sticky top-0 z-20 h-16 glass border-b border-gray-200 dark:border-gray-800">
      <div className="flex items-center justify-between h-full px-4 lg:px-8">
        <div className="flex items-center gap-4">
          <button onClick={onMenuOpen} className="lg:hidden p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800">
            <HiOutlineBars3 className="w-5 h-5" />
          </button>
          <Link to="/dashboard" className="lg:hidden flex items-center gap-2">
            <div className="w-7 h-7 rounded-lg gradient-bg flex items-center justify-center">
              <span className="text-white font-bold text-xs">LM</span>
            </div>
            <span className="font-display font-bold gradient-text">LearnMate</span>
          </Link>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={toggle}
            className="p-2 rounded-xl hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
            aria-label="Toggle theme"
          >
            {dark ? <HiOutlineSun className="w-5 h-5 text-yellow-500" /> : <HiOutlineMoon className="w-5 h-5 text-gray-500" />}
          </button>

          {student && (
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-full gradient-bg flex items-center justify-center">
                <span className="text-white text-sm font-semibold">{(student.name || 'U')[0].toUpperCase()}</span>
              </div>
              <span className="hidden sm:block text-sm font-medium truncate max-w-[120px]">{student.name}</span>
            </div>
          )}
        </div>
      </div>
    </header>
  )
}

function MobileDrawer({ open, onClose }) {
  const location = useLocation()

  return (
    <AnimatePresence>
      {open && (
        <>
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/50 z-40 lg:hidden"
            onClick={onClose}
          />
          <motion.div
            initial={{ x: '-100%' }}
            animate={{ x: 0 }}
            exit={{ x: '-100%' }}
            transition={{ type: 'spring', damping: 25, stiffness: 250 }}
            className="fixed left-0 top-0 bottom-0 w-72 bg-white dark:bg-gray-900 z-50 lg:hidden shadow-2xl"
          >
            <div className="flex items-center justify-between h-16 px-6 border-b border-gray-200 dark:border-gray-800">
              <Link to="/dashboard" onClick={onClose} className="flex items-center gap-2">
                <div className="w-8 h-8 rounded-lg gradient-bg flex items-center justify-center">
                  <span className="text-white font-bold text-sm">LM</span>
                </div>
                <span className="font-display font-bold gradient-text">LearnMate</span>
              </Link>
              <button onClick={onClose} className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800">
                <HiOutlineXMark className="w-5 h-5" />
              </button>
            </div>
            <nav className="py-4 px-3 space-y-1">
              {navItems.map((item) => {
                const active = location.pathname === item.to
                return (
                  <NavLink
                    key={item.to}
                    to={item.to}
                    onClick={onClose}
                    className={`flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all ${
                      active
                        ? 'bg-primary-50 dark:bg-primary-950/50 text-primary-600 dark:text-primary-400'
                        : 'text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800'
                    }`}
                  >
                    <item.icon className="w-5 h-5" />
                    <span>{item.label}</span>
                  </NavLink>
                )
              })}
            </nav>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  )
}

export default function Layout() {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false)
  const [mobileOpen, setMobileOpen] = useState(false)

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-950">
      <Sidebar collapsed={sidebarCollapsed} onToggle={() => setSidebarCollapsed((p) => !p)} />
      <MobileDrawer open={mobileOpen} onClose={() => setMobileOpen(false)} />

      <div className={`transition-all duration-300 ${sidebarCollapsed ? 'lg:ml-[72px]' : 'lg:ml-64'}`}>
        <Navbar onMenuOpen={() => setMobileOpen(true)} />
        <main className="min-h-[calc(100vh-4rem)]">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
