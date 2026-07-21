import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import {
  HiOutlineArrowPath, HiOutlineArrowTopRightOnSquare,
  HiOutlineRocketLaunch, HiOutlineSparkles, HiOutlineLightBulb,
  HiOutlineCheckCircle, HiOutlineExclamationTriangle,
  HiOutlineBookOpen, HiOutlineBriefcase, HiOutlineAcademicCap,
  HiOutlineWrench, HiOutlineUser,
} from 'react-icons/hi2'
import CareerRadarChart from './CareerRadarChart'
import CareerScoreCard from './CareerScoreCard'
import { getCareerRecommendations } from '../../services/api'
import toast from 'react-hot-toast'

const fadeUp = { hidden: { opacity: 0, y: 20 }, visible: { opacity: 1, y: 0 } }

export default function CareerResult({ result, onRetake }) {
  const navigate = useNavigate()
  const [recommendations, setRecommendations] = useState(null)
  const [loadingRecs, setLoadingRecs] = useState(false)
  const [selectedCareer, setSelectedCareer] = useState(null)

  const topCareers = result?.top_careers || []
  const allScores = result?.all_scores || []
  const aiExplanation = result?.ai_explanation || {}
  const topCareer = topCareers[0]

  const handleViewRecommendations = async (careerId) => {
    if (selectedCareer === careerId) {
      setSelectedCareer(null)
      setRecommendations(null)
      return
    }
    setSelectedCareer(careerId)
    setLoadingRecs(true)
    try {
      const res = await getCareerRecommendations(careerId)
      setRecommendations(res.data?.data)
    } catch {
      toast.error('Failed to load recommendations')
    } finally {
      setLoadingRecs(false)
    }
  }

  const handleGenerateRoadmap = () => {
    if (topCareer) {
      navigate('/profile', { state: { careerGoal: topCareer.career_name, fromCareerTest: true } })
      toast.success(`Setting career goal to ${topCareer.career_name}. Save profile and generate roadmap!`)
    }
  }

  const topCareerExplanation = topCareer ? aiExplanation?.career_explanations?.[topCareer.career_id] : null

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="text-center">
        <motion.div
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          transition={{ type: 'spring', damping: 15 }}
          className="w-16 h-16 rounded-2xl bg-gradient-to-br from-primary-500 to-accent-500 flex items-center justify-center mx-auto mb-4"
        >
          <span className="text-3xl">🎯</span>
        </motion.div>
        <h1 className="text-2xl font-display font-bold mb-2">
          Your <span className="gradient-text">Career Matches</span>
        </h1>
        <p className="text-gray-500 dark:text-gray-400 text-sm">
          Based on your answers, here are your top career matches
        </p>
      </div>

      {/* Top Career Highlight */}
      {topCareer && (
        <motion.div
          variants={fadeUp}
          initial="hidden"
          animate="visible"
          className="glass-card p-6 border-2 border-primary-200 dark:border-primary-800/50"
        >
          <div className="flex items-center gap-3 mb-3">
            <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-primary-500 to-accent-500 flex items-center justify-center">
              <span className="text-2xl">🏆</span>
            </div>
            <div>
              <p className="text-xs text-gray-500 dark:text-gray-400">Your Top Career Match</p>
              <h2 className="text-xl font-bold">{topCareer.career_name}</h2>
            </div>
            <div className="ml-auto text-right">
              <span className="text-3xl font-bold text-primary-600">{Math.round(topCareer.percentage)}%</span>
              <p className="text-xs text-gray-500">match</p>
            </div>
          </div>
          {topCareer.description && (
            <p className="text-sm text-gray-600 dark:text-gray-300 mb-4">{topCareer.description}</p>
          )}
          {topCareer.skills?.length > 0 && (
            <div className="flex flex-wrap gap-1.5 mb-4">
              {topCareer.skills.map((skill, i) => (
                <span key={i} className="text-xs bg-primary-50 dark:bg-primary-950/50 text-primary-600 px-2.5 py-1 rounded-full font-medium">
                  {skill}
                </span>
              ))}
            </div>
          )}
          <button
            onClick={handleGenerateRoadmap}
            className="w-full btn-primary flex items-center justify-center gap-2"
          >
            <HiOutlineRocketLaunch className="w-4 h-4" />
            Generate AI Roadmap for {topCareer.career_name}
          </button>
        </motion.div>
      )}

      {/* Top 3 Cards */}
      <div className="grid sm:grid-cols-3 gap-4">
        {topCareers.map((career, i) => (
          <CareerScoreCard
            key={career.career_id}
            career={career}
            rank={i + 1}
            explanation={aiExplanation?.career_explanations?.[career.career_id]}
            onViewRecs={() => handleViewRecommendations(career.career_id)}
            isSelected={selectedCareer === career.career_id}
          />
        ))}
      </div>

      {/* Radar Chart */}
      {allScores.length > 0 && (
        <motion.div variants={fadeUp} initial="hidden" animate="visible" className="glass-card p-6">
          <h3 className="text-lg font-semibold mb-4">Career Score Distribution</h3>
          <CareerRadarChart scores={allScores} />
        </motion.div>
      )}

      {/* AI Explanation - Personality & Skill Match */}
      {aiExplanation && Object.keys(aiExplanation).length > 0 && (
        <motion.div variants={fadeUp} initial="hidden" animate="visible" className="glass-card p-6">
          <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <HiOutlineSparkles className="w-5 h-5 text-primary-500" />
            AI Career Analysis
          </h3>
          <div className="grid sm:grid-cols-2 gap-4">
            {aiExplanation.personality_summary && (
              <div className="p-4 rounded-xl bg-blue-50 dark:bg-blue-950/30 border border-blue-100 dark:border-blue-900/50">
                <div className="flex items-center gap-2 mb-2">
                  <HiOutlineUser className="w-4 h-4 text-blue-500" />
                  <h4 className="text-sm font-semibold text-blue-700 dark:text-blue-300">Personality Summary</h4>
                </div>
                <p className="text-sm text-gray-600 dark:text-gray-300">{aiExplanation.personality_summary}</p>
              </div>
            )}
            {aiExplanation.skill_match && (
              <div className="p-4 rounded-xl bg-purple-50 dark:bg-purple-950/30 border border-purple-100 dark:border-purple-900/50">
                <div className="flex items-center gap-2 mb-2">
                  <HiOutlineWrench className="w-4 h-4 text-purple-500" />
                  <h4 className="text-sm font-semibold text-purple-700 dark:text-purple-300">Skill Match Analysis</h4>
                </div>
                <p className="text-sm text-gray-600 dark:text-gray-300">{aiExplanation.skill_match}</p>
              </div>
            )}
          </div>
        </motion.div>
      )}

      {/* Detailed AI Explanations for Each Top Career */}
      {topCareers.map((career) => {
        const exp = aiExplanation?.career_explanations?.[career.career_id]
        if (!exp) return null
        return (
          <motion.div
            key={career.career_id}
            variants={fadeUp}
            initial="hidden"
            animate="visible"
            className="glass-card p-6"
          >
            <h3 className="text-lg font-semibold mb-4">{career.career_name} - Detailed Analysis</h3>

            <p className="text-sm text-gray-600 dark:text-gray-300 mb-4">{exp.explanation}</p>

            <div className="grid sm:grid-cols-2 gap-4 mb-4">
              {/* Strengths */}
              {exp.strengths?.length > 0 && (
                <div>
                  <h4 className="text-sm font-semibold flex items-center gap-1.5 mb-2 text-green-600 dark:text-green-400">
                    <HiOutlineCheckCircle className="w-4 h-4" /> Strengths
                  </h4>
                  <ul className="space-y-1">
                    {exp.strengths.map((s, i) => (
                      <li key={i} className="text-sm text-gray-600 dark:text-gray-300 flex items-start gap-2">
                        <span className="text-green-500 mt-0.5">•</span> {s}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Weaknesses */}
              {exp.weaknesses?.length > 0 && (
                <div>
                  <h4 className="text-sm font-semibold flex items-center gap-1.5 mb-2 text-amber-600 dark:text-amber-400">
                    <HiOutlineExclamationTriangle className="w-4 h-4" /> Areas to Improve
                  </h4>
                  <ul className="space-y-1">
                    {exp.weaknesses.map((w, i) => (
                      <li key={i} className="text-sm text-gray-600 dark:text-gray-300 flex items-start gap-2">
                        <span className="text-amber-500 mt-0.5">•</span> {w}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>

            <div className="grid sm:grid-cols-2 gap-4">
              {/* Learning Advice */}
              {exp.learning_advice && (
                <div className="p-3 rounded-xl bg-blue-50 dark:bg-blue-950/30">
                  <h4 className="text-xs font-semibold text-blue-600 dark:text-blue-400 mb-1 flex items-center gap-1">
                    <HiOutlineLightBulb className="w-3 h-3" /> Learning Advice
                  </h4>
                  <p className="text-sm text-gray-600 dark:text-gray-300">{exp.learning_advice}</p>
                </div>
              )}

              {/* Future Opportunities */}
              {exp.future_opportunities?.length > 0 && (
                <div className="p-3 rounded-xl bg-green-50 dark:bg-green-950/30">
                  <h4 className="text-xs font-semibold text-green-600 dark:text-green-400 mb-1">Future Opportunities</h4>
                  <ul className="space-y-0.5">
                    {exp.future_opportunities.map((o, i) => (
                      <li key={i} className="text-sm text-gray-600 dark:text-gray-300">• {o}</li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Suggested Technologies */}
              {exp.suggested_technologies?.length > 0 && (
                <div className="p-3 rounded-xl bg-purple-50 dark:bg-purple-950/30">
                  <h4 className="text-xs font-semibold text-purple-600 dark:text-purple-400 mb-1">Suggested Technologies</h4>
                  <div className="flex flex-wrap gap-1">
                    {exp.suggested_technologies.map((t, i) => (
                      <span key={i} className="text-xs bg-purple-100 dark:bg-purple-900/30 text-purple-600 px-2 py-0.5 rounded-full">{t}</span>
                    ))}
                  </div>
                </div>
              )}

              {/* Suggested Roadmap */}
              {exp.suggested_roadmap && (
                <div className="p-3 rounded-xl bg-amber-50 dark:bg-amber-950/30">
                  <h4 className="text-xs font-semibold text-amber-600 dark:text-amber-400 mb-1">Suggested Roadmap</h4>
                  <p className="text-sm text-gray-600 dark:text-gray-300">{exp.suggested_roadmap}</p>
                </div>
              )}
            </div>
          </motion.div>
        )
      })}

      {/* Resource Recommendations */}
      {recommendations && selectedCareer && (
        <motion.div
          initial={{ opacity: 0, height: 0 }}
          animate={{ opacity: 1, height: 'auto' }}
          className="glass-card p-6"
        >
          <h3 className="text-lg font-semibold mb-4">
            Recommended Resources for {topCareers.find(c => c.career_id === selectedCareer)?.career_name}
          </h3>
          {loadingRecs ? (
            <p className="text-sm text-gray-500">Loading recommendations...</p>
          ) : (
            <div className="space-y-5">
              {[
                { key: 'courses', icon: HiOutlineBookOpen, label: 'Courses', color: 'blue' },
                { key: 'projects', icon: HiOutlineBriefcase, label: 'Projects', color: 'purple' },
                { key: 'certifications', icon: HiOutlineAcademicCap, label: 'Certifications', color: 'green' },
                { key: 'books', icon: HiOutlineBookOpen, label: 'Books', color: 'amber' },
              ].map(({ key, icon: Icon, label, color }) => {
                const items = recommendations[key] || []
                if (items.length === 0) return null
                return (
                  <div key={key}>
                    <h4 className="text-sm font-medium flex items-center gap-1.5 mb-2">
                      <Icon className={`w-4 h-4 text-${color}-500`} />
                      {label}
                    </h4>
                    <div className="grid sm:grid-cols-2 gap-2">
                      {items.slice(0, 6).map((item, i) => (
                        <div key={i} className="flex items-center gap-2 p-2 rounded-lg bg-gray-50 dark:bg-gray-800/50 text-sm">
                          <span className="truncate flex-1">{item.title || item.name || 'Resource'}</span>
                          {item.url && (
                            <a href={item.url} target="_blank" rel="noopener noreferrer" className="text-primary-500 hover:text-primary-600 shrink-0">
                              <HiOutlineArrowTopRightOnSquare className="w-3.5 h-3.5" />
                            </a>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                )
              })}
            </div>
          )}
        </motion.div>
      )}

      {/* Actions */}
      <div className="flex justify-center gap-3">
        <button onClick={handleGenerateRoadmap} className="btn-primary flex items-center gap-2">
          <HiOutlineRocketLaunch className="w-4 h-4" /> Generate Roadmap
        </button>
        <button onClick={onRetake} className="btn-secondary flex items-center gap-2">
          <HiOutlineArrowPath className="w-4 h-4" /> Retake Test
        </button>
      </div>
    </div>
  )
}
