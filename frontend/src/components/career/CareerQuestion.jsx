import { motion } from 'framer-motion'

const categoryColors = {
  interests: 'bg-blue-100 dark:bg-blue-900/30 text-blue-600',
  skills: 'bg-purple-100 dark:bg-purple-900/30 text-purple-600',
  personality: 'bg-green-100 dark:bg-green-900/30 text-green-600',
  goals: 'bg-orange-100 dark:bg-orange-900/30 text-orange-600',
}

export default function CareerQuestion({ question, selectedAnswer, onAnswer }) {
  if (!question) return null

  return (
    <div className="glass-card p-6">
      <div className="flex items-center gap-3 mb-4">
        <span className="text-xs font-bold text-gray-400">Q{question.id}</span>
        {question.category && (
          <span className={`text-xs font-medium px-2 py-0.5 rounded-full ${categoryColors[question.category] || 'bg-gray-100 text-gray-600'}`}>
            {question.category}
          </span>
        )}
      </div>

      <h2 className="text-lg font-semibold mb-6">{question.text}</h2>

      <div className="space-y-3">
        {question.options.map((option) => {
          const isSelected = selectedAnswer === option.id
          return (
            <motion.button
              key={option.id}
              whileHover={{ scale: 1.01 }}
              whileTap={{ scale: 0.99 }}
              onClick={() => onAnswer(question.id, option.id)}
              className={`w-full text-left p-4 rounded-xl border-2 transition-all duration-200 ${
                isSelected
                  ? 'border-primary-500 bg-primary-50 dark:bg-primary-950/50 shadow-md'
                  : 'border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600'
              }`}
            >
              <div className="flex items-center gap-3">
                <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold ${
                  isSelected
                    ? 'bg-primary-500 text-white'
                    : 'bg-gray-100 dark:bg-gray-800 text-gray-500'
                }`}>
                  {option.id.toUpperCase()}
                </div>
                <span className="flex-1">{option.text}</span>
                {isSelected && (
                  <motion.div
                    initial={{ scale: 0 }}
                    animate={{ scale: 1 }}
                    className="w-5 h-5 rounded-full bg-primary-500 flex items-center justify-center"
                  >
                    <svg className="w-3 h-3 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                    </svg>
                  </motion.div>
                )}
              </div>
            </motion.button>
          )
        })}
      </div>
    </div>
  )
}
