import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { HiOutlineHome } from 'react-icons/hi2'

export default function NotFound() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-950 px-4">
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        className="text-center"
      >
        <span className="text-9xl font-display font-extrabold gradient-text">404</span>
        <h1 className="text-2xl font-display font-bold mt-4 mb-2">Page Not Found</h1>
        <p className="text-gray-500 dark:text-gray-400 mb-8">The page you're looking for doesn't exist.</p>
        <Link to="/" className="btn-primary inline-flex items-center gap-2">
          <HiOutlineHome className="w-5 h-5" /> Go Home
        </Link>
      </motion.div>
    </div>
  )
}
