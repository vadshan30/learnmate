import { useMemo } from 'react'
import { motion } from 'framer-motion'
import { HiOutlineClock, HiOutlineArrowRight, HiOutlineArrowTrendingUp, HiOutlineArrowTrendingDown, HiOutlineMinus } from 'react-icons/hi2'

export default function CareerHistory({ history }) {
  const comparison = useMemo(() => {
    if (!history || history.length < 2) return null
    const latest = history[0]
    const previous = history[1]
    const latestTop = latest.top_careers?.[0]
    const previousTop = previous.top_careers?.[0]
    if (!latestTop || !previousTop) return null

    const scoreDiff = (latestTop.percentage || 0) - (previousTop.percentage || 0)
    const sameCareer = latestTop.career_id === previousTop.career_id

    return {
      latestCareer: latestTop.career_name,
      previousCareer: previousTop.career_name,
      latestScore: latestTop.percentage,
      previousScore: previousTop.percentage,
      scoreDiff,
      sameCareer,
    }
  }, [history])

  if (!history || history.length === 0) {
    return (
      <div className="glass-card p-12 text-center">
        <HiOutlineClock className="w-12 h-12 text-gray-300 dark:text-gray-600 mx-auto mb-3" />
        <p className="text-gray-500 dark:text-gray-400">No test history yet</p>
        <p className="text-sm text-gray-400 dark:text-gray-500 mt-1">Take the career aptitude test to see your results here</p>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {/* Comparison Card */}
      {comparison && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="glass-card p-5 border-2 border-primary-100 dark:border-primary-900/50"
        >
          <h3 className="text-sm font-semibold mb-3 text-gray-500 dark:text-gray-400">Latest Comparison</h3>
          <div className="flex items-center gap-4">
            <div className="flex-1 text-center">
              <p className="text-xs text-gray-500 mb-1">Previous</p>
              <p className="font-semibold text-sm">{comparison.previousCareer}</p>
              <p className="text-lg font-bold text-gray-500">{Math.round(comparison.previousScore)}%</p>
            </div>
            <div className="flex flex-col items-center gap-1">
              {comparison.sameCareer ? (
                <HiOutlineMinus className="w-5 h-5 text-gray-400" />
              ) : comparison.scoreDiff > 0 ? (
                <HiOutlineArrowTrendingUp className="w-5 h-5 text-green-500" />
              ) : (
                <HiOutlineArrowTrendingDown className="w-5 h-5 text-red-500" />
              )}
              <span className={`text-xs font-bold ${
                comparison.scoreDiff > 0 ? 'text-green-600' : comparison.scoreDiff < 0 ? 'text-red-600' : 'text-gray-500'
              }`}>
                {comparison.scoreDiff > 0 ? '+' : ''}{comparison.scoreDiff.toFixed(1)}%
              </span>
            </div>
            <div className="flex-1 text-center">
              <p className="text-xs text-gray-500 mb-1">Latest</p>
              <p className="font-semibold text-sm">{comparison.latestCareer}</p>
              <p className="text-lg font-bold text-primary-600">{Math.round(comparison.latestScore)}%</p>
            </div>
          </div>
          {comparison.sameCareer && (
            <p className="text-xs text-center text-gray-500 mt-2">Same top career across both attempts</p>
          )}
        </motion.div>
      )}

      {/* History List */}
      <div className="space-y-3">
        {history.map((item, i) => {
          const topCareer = item.top_careers?.[0]
          const date = item.created_at ? new Date(item.created_at).toLocaleDateString('en-US', {
            year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit',
          }) : 'Unknown'

          // Compare with next item (older)
          const prevItem = history[i + 1]
          const prevTop = prevItem?.top_careers?.[0]
          const scoreChange = prevTop ? (topCareer?.percentage || 0) - (prevTop.percentage || 0) : null

          return (
            <motion.div
              key={item.id || i}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.05 }}
              className="glass-card p-4 flex items-center gap-4"
            >
              <div className={`w-10 h-10 rounded-xl flex items-center justify-center shrink-0 ${
                i === 0 ? 'bg-primary-100 dark:bg-primary-900/30' : 'bg-gray-100 dark:bg-gray-800'
              }`}>
                <span className={`font-bold text-sm ${i === 0 ? 'text-primary-600' : 'text-gray-500'}`}>#{i + 1}</span>
              </div>

              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-1">
                  <span className="font-semibold text-sm truncate">
                    {topCareer?.career_name || 'Unknown Career'}
                  </span>
                  {topCareer && (
                    <span className="text-xs font-bold text-primary-600">{Math.round(topCareer.percentage)}%</span>
                  )}
                  {scoreChange !== null && scoreChange !== 0 && (
                    <span className={`text-xs font-bold ${scoreChange > 0 ? 'text-green-600' : 'text-red-600'}`}>
                      {scoreChange > 0 ? '↑' : '↓'}{Math.abs(scoreChange).toFixed(1)}%
                    </span>
                  )}
                </div>
                <div className="flex items-center gap-3 text-xs text-gray-500">
                  <span>{date}</span>
                  {item.top_careers?.length > 1 && (
                    <>
                      <span>·</span>
                      <span>Also matched: {item.top_careers.slice(1, 3).map(c => c.career_name).join(', ')}</span>
                    </>
                  )}
                </div>
              </div>

              <div className="flex items-center gap-1 text-xs text-gray-400">
                {Object.keys(item.answers || {}).length} answers
                <HiOutlineArrowRight className="w-3 h-3" />
              </div>
            </motion.div>
          )
        })}
      </div>
    </div>
  )
}
