import { Component } from 'react'
import { motion } from 'framer-motion'
import { HiOutlineExclamationTriangle } from 'react-icons/hi2'

export default class ErrorBoundary extends Component {
  constructor(props) {
    super(props)
    this.state = { hasError: false, error: null }
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error }
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-950 px-4">
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="glass-card p-8 max-w-md w-full text-center space-y-4"
          >
            <HiOutlineExclamationTriangle className="w-12 h-12 text-yellow-500 mx-auto" />
            <h2 className="text-xl font-display font-bold">Something went wrong</h2>
            <p className="text-gray-500 dark:text-gray-400 text-sm">
              {this.state.error?.message || 'An unexpected error occurred.'}
            </p>
            <button
              onClick={() => { this.setState({ hasError: false, error: null }); window.location.reload() }}
              className="btn-primary"
            >
              Reload Page
            </button>
          </motion.div>
        </div>
      )
    }
    return this.props.children
  }
}
