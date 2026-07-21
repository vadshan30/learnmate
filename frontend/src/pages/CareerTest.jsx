import { useState, useEffect, useCallback, useRef } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  HiOutlineAcademicCap, HiOutlineArrowRight, HiOutlineArrowLeft,
  HiOutlineCheckCircle, HiOutlineClock, HiOutlineTrophy,
  HiOutlineSparkles, HiOutlineArrowPath, HiOutlineExclamationTriangle,
} from 'react-icons/hi2'
import { useApp } from '../context/AppContext'
import { useAuth } from '../context/AuthContext'
import { useGuest } from '../context/GuestContext'
import {
  getCareerTestQuestions,
  submitCareerTest,
  getCareerTestHistory,
} from '../services/api'
import CareerQuestion from '../components/career/CareerQuestion'
import CareerProgress from '../components/career/CareerProgress'
import CareerNavigator from '../components/career/CareerNavigator'
import CareerResult from '../components/career/CareerResult'
import CareerHistory from '../components/career/CareerHistory'
import RetakeDialog from '../components/career/RetakeDialog'
import LoadingSpinner from '../components/common/LoadingSpinner'
import toast from 'react-hot-toast'

const fadeUp = { hidden: { opacity: 0, y: 20 }, visible: { opacity: 1, y: 0 } }
const stagger = { visible: { transition: { staggerChildren: 0.06 } } }

const STORAGE_KEY = 'learnmate_career_test_progress'

function readSavedProgress() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    if (raw) {
      const data = JSON.parse(raw)
      if (data && data.phase && data.phase !== 'intro' && data.phase !== 'submitting') {
        return data
      }
    }
  } catch { /* corrupted data — ignore */ }
  return null
}

function saveProgressToStorage(phase, questions, currentIndex, answers, questionStatus, startTime, result) {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify({
      phase, questions, currentIndex, answers, questionStatus, startTime, result,
    }))
  } catch { /* storage full — ignore */ }
}

function clearSavedProgress() {
  try { localStorage.removeItem(STORAGE_KEY) } catch { /* ignore */ }
}

function formatTime(totalSeconds) {
  const m = Math.floor(totalSeconds / 60)
  const s = totalSeconds % 60
  return `${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`
}

export default function CareerTest() {
  const { student } = useApp()
  const { user } = useAuth()
  const { isGuest } = useGuest()

  const saved = useRef(readSavedProgress()).current

  const [phase, setPhase] = useState(saved?.phase || 'intro')
  const [questions, setQuestions] = useState(saved?.questions || [])
  const [currentIndex, setCurrentIndex] = useState(saved?.currentIndex || 0)
  const [answers, setAnswers] = useState(saved?.answers || {})
  const [questionStatus, setQuestionStatus] = useState(saved?.questionStatus || {})
  const [result, setResult] = useState(saved?.result || null)
  const [history, setHistory] = useState([])
  const [historyLoading, setHistoryLoading] = useState(false)
  const [loading, setLoading] = useState(false)
  const [showRetakeDialog, setShowRetakeDialog] = useState(false)
  const [showConfirmDialog, setShowConfirmDialog] = useState(false)
  const [startTime] = useState(saved?.startTime || Date.now())
  const [elapsed, setElapsed] = useState(0)

  const userIdRef = useRef(user?.id || localStorage.getItem('learnmate_guest_id') || 'guest')
  userIdRef.current = user?.id || localStorage.getItem('learnmate_guest_id') || 'guest'

  // ── Timer ──────────────────────────────────────────────────
  useEffect(() => {
    if (phase !== 'quiz') return
    const tick = () => setElapsed(Math.floor((Date.now() - startTime) / 1000))
    tick()
    const interval = setInterval(tick, 1000)
    return () => clearInterval(interval)
  }, [phase, startTime])

  // ── Mark current question as visited ───────────────────────
  useEffect(() => {
    if (phase === 'quiz' && questions.length > 0) {
      const qid = questions[currentIndex]?.id
      if (qid && !questionStatus[qid]) {
        setQuestionStatus((prev) => ({ ...prev, [qid]: 'visited' }))
      }
    }
  }, [currentIndex, phase, questions])

  // ── Debug logging ──────────────────────────────────────────
  useEffect(() => {
    console.log('[CareerTest] Mount | phase:', saved?.phase || 'intro', '| questions:', saved?.questions?.length || 0)
    return () => console.log('[CareerTest] Unmount')
  }, [])

  // ── Persist progress ───────────────────────────────────────
  useEffect(() => {
    const hasProgress = phase !== 'intro' || questions.length > 0 || Object.keys(answers).length > 0
    if (hasProgress && phase !== 'submitting') {
      saveProgressToStorage(phase, questions, currentIndex, answers, questionStatus, startTime, result)
    }
  }, [phase, questions, currentIndex, answers, questionStatus, startTime, result])

  // ── Fetch questions ────────────────────────────────────────
  const fetchQuestions = useCallback(async () => {
    setLoading(true)
    try {
      const res = await getCareerTestQuestions()
      setQuestions(res.data?.data?.questions || [])
    } catch {
      toast.error('Failed to load questions')
    } finally {
      setLoading(false)
    }
  }, [])

  // ── Fetch history ──────────────────────────────────────────
  const fetchHistory = useCallback(async () => {
    setHistoryLoading(true)
    try {
      const res = await getCareerTestHistory(userIdRef.current)
      setHistory(res.data?.data || [])
    } catch { /* ignore */ }
    setHistoryLoading(false)
  }, [])

  useEffect(() => {
    if (phase === 'quiz' && questions.length === 0) fetchQuestions()
  }, [phase, questions.length, fetchQuestions])

  useEffect(() => {
    if (phase === 'history') fetchHistory()
  }, [phase, fetchHistory])

  // ── Answer a question ──────────────────────────────────────
  const handleAnswer = (questionId, answerId) => {
    setAnswers((prev) => ({ ...prev, [questionId]: answerId }))
    setQuestionStatus((prev) => ({ ...prev, [questionId]: 'answered' }))
  }

  // ── Navigation ─────────────────────────────────────────────
  const handleNext = () => {
    const qid = questions[currentIndex]?.id
    if (qid && !answers[qid]) {
      setQuestionStatus((prev) => {
        if (prev[qid] === 'answered') return prev
        return { ...prev, [qid]: 'skipped' }
      })
    }
    if (currentIndex < questions.length - 1) {
      setCurrentIndex((i) => i + 1)
    }
  }

  const handlePrev = () => {
    if (currentIndex > 0) setCurrentIndex((i) => i - 1)
  }

  const handleJumpToQuestion = (index) => {
    setCurrentIndex(index)
    const qid = questions[index]?.id
    if (qid && !questionStatus[qid]) {
      setQuestionStatus((prev) => ({ ...prev, [qid]: 'visited' }))
    }
  }

  // ── Submission ─────────────────────────────────────────────
  const skippedQuestions = questions.filter((q) => !answers[q.id])
  const answeredCount = questions.length - skippedQuestions.length
  const skippedCount = skippedQuestions.length
  const isLastQuestion = currentIndex === questions.length - 1

  const submitTest = async () => {
    setPhase('submitting')
    setShowConfirmDialog(false)
    try {
      const res = await submitCareerTest(userIdRef.current, answers)
      setResult(res.data?.data)
      clearSavedProgress()
      setPhase('result')
      toast.success('Test completed! Here are your results.')
    } catch {
      toast.error('Failed to submit test. Please try again.')
      setPhase('quiz')
    }
  }

  const handleSubmit = () => {
    if (skippedCount > 0) {
      setShowConfirmDialog(true)
    } else {
      submitTest()
    }
  }

  const handleReviewUnanswered = () => {
    setShowConfirmDialog(false)
    const firstSkipped = questions.findIndex((q) => !answers[q.id])
    if (firstSkipped >= 0) setCurrentIndex(firstSkipped)
  }

  // ── Retake ─────────────────────────────────────────────────
  const handleRetakeConfirm = () => {
    setShowRetakeDialog(false)
    setAnswers({})
    setQuestionStatus({})
    setCurrentIndex(0)
    setResult(null)
    clearSavedProgress()
    fetchQuestions()
    setPhase('quiz')
  }

  const handleRetake = () => {
    if (history.length > 0) {
      setShowRetakeDialog(true)
    } else {
      handleRetakeConfirm()
    }
  }

  const lastResult = history.length > 0 ? history[0] : null

  if (loading && phase === 'quiz') {
    return (
      <div className="page-container flex items-center justify-center min-h-[60vh]">
        <LoadingSpinner size="lg" />
      </div>
    )
  }

  return (
    <div className="page-container max-w-4xl mx-auto">
      <motion.div initial="hidden" animate="visible" variants={stagger}>
        <AnimatePresence mode="wait">
          {/* ── INTRO PHASE ──────────────────────────────── */}
          {phase === 'intro' && (
            <motion.div key="intro" variants={fadeUp} initial="hidden" animate="visible" exit={{ opacity: 0 }}>
              <div className="text-center py-12">
                <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-primary-500 to-accent-500 flex items-center justify-center mx-auto mb-6">
                  <HiOutlineAcademicCap className="w-10 h-10 text-white" />
                </div>
                <h1 className="text-3xl font-display font-bold mb-3">
                  Career <span className="gradient-text">Aptitude Test</span>
                </h1>
                <p className="text-gray-500 dark:text-gray-400 max-w-xl mx-auto mb-8">
                  Discover your ideal tech career path through 25 carefully crafted questions.
                  You can skip questions and come back to them later.
                </p>

                <div className="grid sm:grid-cols-3 gap-4 max-w-2xl mx-auto mb-8">
                  {[
                    { icon: HiOutlineClock, title: '5-10 min', desc: 'Quick assessment' },
                    { icon: HiOutlineSparkles, title: 'AI-Powered', desc: 'Personalised insights' },
                    { icon: HiOutlineTrophy, title: 'Top Matches', desc: 'Your best-fit careers' },
                  ].map((f, i) => (
                    <div key={i} className="glass-card p-4 text-center">
                      <f.icon className="w-6 h-6 mx-auto mb-2 text-primary-500" />
                      <p className="font-semibold text-sm">{f.title}</p>
                      <p className="text-xs text-gray-500">{f.desc}</p>
                    </div>
                  ))}
                </div>

                {lastResult && lastResult.top_careers?.[0] && (
                  <div className="glass-card p-4 max-w-md mx-auto mb-6">
                    <p className="text-xs text-gray-500 dark:text-gray-400 mb-1">Your last result</p>
                    <div className="flex items-center justify-center gap-2">
                      <span className="font-semibold">{lastResult.top_careers[0].career_name}</span>
                      <span className="text-sm font-bold text-primary-600">{Math.round(lastResult.top_careers[0].percentage)}%</span>
                    </div>
                  </div>
                )}

                <div className="flex flex-col sm:flex-row gap-3 justify-center">
                  <button
                    onClick={() => setPhase('quiz')}
                    className="btn-primary flex items-center justify-center gap-2"
                  >
                    {history.length > 0 ? 'Discover your ideal career' : 'Start Test'} <HiOutlineArrowRight className="w-4 h-4" />
                  </button>
                  <button
                    onClick={() => setPhase('history')}
                    className="btn-secondary flex items-center justify-center gap-2"
                  >
                    <HiOutlineClock className="w-4 h-4" /> View History
                  </button>
                </div>

                {history.length > 0 && (
                  <p className="text-sm text-gray-400 mt-4">
                    You have {history.length} past test{history.length !== 1 ? 's' : ''}
                  </p>
                )}
              </div>
            </motion.div>
          )}

          {/* ── QUIZ PHASE ──────────────────────────────── */}
          {phase === 'quiz' && questions.length > 0 && (
            <motion.div key="quiz" variants={fadeUp} initial="hidden" animate="visible" exit={{ opacity: 0 }}>
              <div className="mb-6">
                <h1 className="text-2xl font-display font-bold mb-1">
                  Career <span className="gradient-text">Aptitude Test</span>
                </h1>
                <p className="text-sm text-gray-500 dark:text-gray-400">
                  Skip any question and come back to it later.
                </p>
              </div>

              <CareerProgress
                current={currentIndex}
                total={questions.length}
                answered={answeredCount}
                skipped={skippedCount}
                elapsed={elapsed}
              />

              <div className="mt-4">
                <CareerNavigator
                  questions={questions}
                  currentIndex={currentIndex}
                  questionStatus={questionStatus}
                  onJumpTo={handleJumpToQuestion}
                />
              </div>

              <div className="mt-6">
                <CareerQuestion
                  question={questions[currentIndex]}
                  selectedAnswer={answers[questions[currentIndex]?.id]}
                  onAnswer={handleAnswer}
                />
              </div>

              <div className="flex items-center justify-between mt-8">
                <button
                  onClick={handlePrev}
                  disabled={currentIndex === 0}
                  className="btn-secondary flex items-center gap-2 disabled:opacity-40"
                >
                  <HiOutlineArrowLeft className="w-4 h-4" /> Previous
                </button>

                <div className="flex items-center gap-2">
                  {isLastQuestion ? (
                    <button
                      onClick={handleSubmit}
                      className="btn-primary flex items-center gap-2"
                    >
                      <HiOutlineCheckCircle className="w-4 h-4" /> Submit Test
                    </button>
                  ) : (
                    <button
                      onClick={handleNext}
                      className="btn-primary flex items-center gap-2"
                    >
                      Next <HiOutlineArrowRight className="w-4 h-4" />
                    </button>
                  )}
                </div>
              </div>
            </motion.div>
          )}

          {/* ── SUBMITTING PHASE ────────────────────────── */}
          {phase === 'submitting' && (
            <motion.div key="submitting" variants={fadeUp} initial="hidden" animate="visible" exit={{ opacity: 0 }}>
              <div className="text-center py-20">
                <LoadingSpinner size="lg" />
                <p className="text-lg font-semibold mt-4">Analysing your answers...</p>
                <p className="text-sm text-gray-500 mt-1">Our AI is generating personalised career insights</p>
              </div>
            </motion.div>
          )}

          {/* ── RESULT PHASE ────────────────────────────── */}
          {phase === 'result' && result && (
            <motion.div key="result" variants={fadeUp} initial="hidden" animate="visible" exit={{ opacity: 0 }}>
              <CareerResult result={result} onRetake={handleRetake} />
            </motion.div>
          )}

          {/* ── HISTORY PHASE ───────────────────────────── */}
          {phase === 'history' && (
            <motion.div key="history" variants={fadeUp} initial="hidden" animate="visible" exit={{ opacity: 0 }}>
              <div className="flex items-center justify-between mb-6">
                <h1 className="text-2xl font-display font-bold">
                  Test <span className="gradient-text">History</span>
                </h1>
                <div className="flex gap-2">
                  <button onClick={() => setPhase('intro')} className="btn-secondary text-sm">
                    Back
                  </button>
                  <button
                    onClick={handleRetake}
                    className="btn-primary text-sm flex items-center gap-1"
                  >
                    <HiOutlineArrowPath className="w-4 h-4" /> Retake
                  </button>
                </div>
              </div>
              {historyLoading ? (
                <div className="flex items-center justify-center py-12">
                  <LoadingSpinner size="lg" />
                </div>
              ) : (
                <CareerHistory history={history} />
              )}
            </motion.div>
          )}
        </AnimatePresence>
      </motion.div>

      {/* ── RETAKE DIALOG ──────────────────────────────── */}
      <RetakeDialog
        open={showRetakeDialog}
        onClose={() => setShowRetakeDialog(false)}
        onConfirm={handleRetakeConfirm}
        previousCareer={lastResult?.top_careers?.[0]?.career_name}
        previousScore={lastResult?.top_careers?.[0]?.percentage}
      />

      {/* ── CONFIRM SUBMIT DIALOG ──────────────────────── */}
      <AnimatePresence>
        {showConfirmDialog && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-50 flex items-center justify-center p-4"
          >
            {/* Backdrop */}
            <div className="absolute inset-0 bg-black/50 backdrop-blur-sm" onClick={() => setShowConfirmDialog(false)} />

            {/* Modal */}
            <motion.div
              initial={{ opacity: 0, scale: 0.95, y: 10 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95, y: 10 }}
              className="relative bg-white dark:bg-gray-900 rounded-2xl shadow-2xl p-6 max-w-md w-full space-y-5"
            >
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-xl bg-amber-100 dark:bg-amber-900/30 flex items-center justify-center shrink-0">
                  <HiOutlineExclamationTriangle className="w-5 h-5 text-amber-600 dark:text-amber-400" />
                </div>
                <div>
                  <h3 className="font-semibold text-lg">Unanswered Questions</h3>
                  <p className="text-sm text-gray-500 dark:text-gray-400">
                    You have {skippedCount} unanswered question{skippedCount !== 1 ? 's' : ''}
                  </p>
                </div>
              </div>

              {/* Stats */}
              <div className="grid grid-cols-3 gap-3 text-center">
                <div className="p-3 rounded-xl bg-green-50 dark:bg-green-900/20">
                  <p className="text-2xl font-bold text-green-600 dark:text-green-400">{answeredCount}</p>
                  <p className="text-xs text-gray-500">Answered</p>
                </div>
                <div className="p-3 rounded-xl bg-yellow-50 dark:bg-yellow-900/20">
                  <p className="text-2xl font-bold text-yellow-600 dark:text-yellow-400">{skippedCount}</p>
                  <p className="text-xs text-gray-500">Skipped</p>
                </div>
                <div className="p-3 rounded-xl bg-gray-50 dark:bg-gray-800">
                  <p className="text-2xl font-bold text-gray-600 dark:text-gray-300">{formatTime(elapsed)}</p>
                  <p className="text-xs text-gray-500">Time</p>
                </div>
              </div>

              {/* Skipped question list */}
              <div className="max-h-40 overflow-y-auto space-y-1">
                <p className="text-xs font-semibold text-gray-500 uppercase tracking-wider">Skipped Questions</p>
                {skippedQuestions.map((q) => (
                  <div key={q.id} className="flex items-center gap-2 px-3 py-2 rounded-lg bg-gray-50 dark:bg-gray-800/50 text-sm">
                    <span className="w-6 h-6 rounded-full bg-yellow-100 dark:bg-yellow-900/30 text-yellow-700 dark:text-yellow-400 flex items-center justify-center text-xs font-bold shrink-0">
                      {q.id}
                    </span>
                    <span className="text-gray-700 dark:text-gray-300 truncate">{q.text}</span>
                  </div>
                ))}
              </div>

              {/* Actions */}
              <div className="flex gap-3">
                <button
                  onClick={handleReviewUnanswered}
                  className="btn-secondary flex-1 flex items-center justify-center gap-2"
                >
                  <HiOutlineArrowLeft className="w-4 h-4" /> Review Questions
                </button>
                <button
                  onClick={submitTest}
                  className="btn-primary flex-1 flex items-center justify-center gap-2"
                >
                  <HiOutlineCheckCircle className="w-4 h-4" /> Submit Anyway
                </button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}
