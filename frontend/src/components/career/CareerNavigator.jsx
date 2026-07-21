export default function CareerNavigator({ questions, currentIndex, questionStatus, onJumpTo }) {
  return (
    <div className="glass-card p-4">
      <p className="text-xs font-semibold text-gray-500 dark:text-gray-400 mb-3 uppercase tracking-wider">
        Question Navigator
      </p>
      <div className="flex flex-wrap gap-2">
        {questions.map((q, i) => {
          const status = questionStatus[q.id]
          const isCurrent = i === currentIndex
          let cls = ''
          if (isCurrent) {
            cls = 'bg-primary-500 text-white ring-2 ring-primary-300 dark:ring-primary-700'
          } else if (status === 'answered') {
            cls = 'bg-green-500 text-white'
          } else if (status === 'skipped') {
            cls = 'bg-yellow-400 text-gray-900'
          } else if (status === 'visited') {
            cls = 'bg-blue-100 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400'
          } else {
            cls = 'bg-gray-100 dark:bg-gray-800 text-gray-500 dark:text-gray-400'
          }
          return (
            <button
              key={q.id}
              type="button"
              onClick={() => onJumpTo(i)}
              className={`w-9 h-9 rounded-lg text-xs font-bold transition-all hover:scale-110 ${cls}`}
            >
              {i + 1}
            </button>
          )
        })}
      </div>
      <div className="flex flex-wrap gap-3 mt-3 text-[10px] text-gray-500 dark:text-gray-400">
        <span className="flex items-center gap-1">
          <span className="w-2.5 h-2.5 rounded bg-green-500 inline-block" /> Answered
        </span>
        <span className="flex items-center gap-1">
          <span className="w-2.5 h-2.5 rounded bg-yellow-400 inline-block" /> Skipped
        </span>
        <span className="flex items-center gap-1">
          <span className="w-2.5 h-2.5 rounded bg-blue-100 dark:bg-blue-900/30 border border-blue-300 dark:border-blue-700 inline-block" /> Visited
        </span>
        <span className="flex items-center gap-1">
          <span className="w-2.5 h-2.5 rounded bg-gray-200 dark:bg-gray-700 inline-block" /> Not Visited
        </span>
      </div>
    </div>
  )
}
