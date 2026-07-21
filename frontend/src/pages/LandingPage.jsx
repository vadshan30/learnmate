import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import {
  HiOutlineAcademicCap, HiOutlineSparkles, HiOutlineChartBarSquare,
  HiOutlineRocketLaunch, HiOutlineBolt,
  HiOutlineCheckBadge, HiOutlineUserGroup, HiOutlineClock,
} from 'react-icons/hi2'

const fadeUp = { hidden: { opacity: 0, y: 30 }, visible: { opacity: 1, y: 0 } }
const stagger = { visible: { transition: { staggerChildren: 0.1 } } }

function Navbar() {
  return (
    <nav className="fixed top-0 w-full z-50 glass border-b border-white/10">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        <Link to="/" className="flex items-center gap-2">
          <div className="w-9 h-9 rounded-xl gradient-bg flex items-center justify-center shadow-lg">
            <span className="text-white font-bold text-sm">LM</span>
          </div>
          <span className="font-display font-bold text-xl gradient-text">LearnMate AI</span>
        </Link>
        <div className="flex items-center gap-3">
          <Link to="/login" className="btn-ghost">Sign In</Link>
          <Link to="/register" className="btn-primary text-sm !px-5 !py-2.5">Get Started</Link>
        </div>
      </div>
    </nav>
  )
}

function Hero() {
  return (
    <section className="relative min-h-screen flex items-center justify-center overflow-hidden pt-16">
      <div className="absolute inset-0 bg-gradient-to-br from-primary-50 via-white to-accent-50 dark:from-gray-950 dark:via-gray-900 dark:to-gray-950" />
      <div className="absolute top-20 left-10 w-72 h-72 bg-primary-300/20 dark:bg-primary-600/10 rounded-full blur-3xl" />
      <div className="absolute bottom-20 right-10 w-96 h-96 bg-accent-300/20 dark:bg-accent-600/10 rounded-full blur-3xl" />

      <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
        <motion.div initial="hidden" animate="visible" variants={stagger}>
          <motion.div variants={fadeUp} className="inline-flex items-center gap-2 mb-6 px-4 py-2 rounded-full bg-primary-100 dark:bg-primary-900/30 text-primary-700 dark:text-primary-300 text-sm font-medium">
            <HiOutlineSparkles className="w-4 h-4" />
            AI-Powered Learning Platform
          </motion.div>

          <motion.h1 variants={fadeUp} className="text-5xl sm:text-6xl lg:text-7xl font-display font-extrabold tracking-tight mb-6">
            Your Personalised
            <br />
            <span className="gradient-text">Learning Coach</span>
          </motion.h1>

          <motion.p variants={fadeUp} className="text-lg sm:text-xl text-gray-600 dark:text-gray-400 max-w-2xl mx-auto mb-10 leading-relaxed">
            LearnMate AI analyses your skills, understands your goals, and generates a customised roadmap powered by Google Gemini AI. Track progress and achieve your career dreams.
          </motion.p>

          <motion.div variants={fadeUp} className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <Link to="/register" className="btn-primary text-base !px-8 !py-4 shadow-xl">
              <span className="flex items-center gap-2"><HiOutlineRocketLaunch className="w-5 h-5" /> Start Learning</span>
            </Link>
            <Link to="/dashboard" className="btn-secondary text-base !px-8 !py-4">
              View Dashboard
            </Link>
          </motion.div>

          <motion.div variants={fadeUp} className="mt-16 flex items-center justify-center gap-8 text-sm text-gray-500 dark:text-gray-400">
            <div className="flex items-center gap-2"><HiOutlineCheckBadge className="w-4 h-4 text-green-500" /> AI-Generated Roadmaps</div>
            <div className="flex items-center gap-2"><HiOutlineCheckBadge className="w-4 h-4 text-green-500" /> Skill Gap Analysis</div>
            <div className="flex items-center gap-2"><HiOutlineCheckBadge className="w-4 h-4 text-green-500" /> Progress Tracking</div>
          </motion.div>
        </motion.div>
      </div>
    </section>
  )
}

const features = [
  { icon: HiOutlineAcademicCap, title: 'Smart Skill Analysis', desc: 'AI analyses your current skills and identifies gaps for your target career.' },
  { icon: HiOutlineChartBarSquare, title: 'Personalised Roadmaps', desc: 'Get a 10-week learning plan tailored to your goals, skills, and schedule.' },
  { icon: HiOutlineBolt, title: 'RAG-Powered Resources', desc: 'Semantic search finds the best courses, projects, and certs for you.' },
  { icon: HiOutlineClock, title: 'Progress Tracking', desc: 'Visualise your learning streak, hours studied, and topic completion.' },
  { icon: HiOutlineUserGroup, title: 'Adaptive Learning', desc: 'Roadmaps adjust based on your progress and changing interests.' },
]

function Features() {
  return (
    <section className="py-24 bg-white dark:bg-gray-900">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <motion.div initial="hidden" whileInView="visible" viewport={{ once: true }} variants={stagger} className="text-center mb-16">
          <motion.h2 variants={fadeUp} className="text-3xl sm:text-4xl font-display font-bold mb-4">Powerful Features</motion.h2>
          <motion.p variants={fadeUp} className="text-gray-500 dark:text-gray-400 max-w-lg mx-auto">Everything you need to accelerate your learning journey</motion.p>
        </motion.div>
        <motion.div initial="hidden" whileInView="visible" viewport={{ once: true }} variants={stagger} className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {features.map((f) => (
            <motion.div key={f.title} variants={fadeUp} whileHover={{ y: -4 }} className="glass-card p-6 group cursor-default">
              <div className="w-12 h-12 rounded-xl bg-primary-100 dark:bg-primary-900/30 flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                <f.icon className="w-6 h-6 text-primary-600 dark:text-primary-400" />
              </div>
              <h3 className="font-semibold text-lg mb-2">{f.title}</h3>
              <p className="text-gray-500 dark:text-gray-400 text-sm leading-relaxed">{f.desc}</p>
            </motion.div>
          ))}
        </motion.div>
      </div>
    </section>
  )
}

const steps = [
  { num: '01', title: 'Create Your Profile', desc: 'Tell us about your skills, interests, and career goals.' },
  { num: '02', title: 'Generate Roadmap', desc: 'Our AI creates a personalised 10-week learning plan.' },
  { num: '03', title: 'Learn & Build', desc: 'Follow weekly objectives, complete projects, and earn certifications.' },
  { num: '04', title: 'Track Progress', desc: 'Monitor your growth with analytics and achieve your learning goals.' },
]

function HowItWorks() {
  return (
    <section className="py-24 bg-gray-50 dark:bg-gray-950">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <motion.div initial="hidden" whileInView="visible" viewport={{ once: true }} variants={stagger} className="text-center mb-16">
          <motion.h2 variants={fadeUp} className="text-3xl sm:text-4xl font-display font-bold mb-4">How LearnMate Works</motion.h2>
          <motion.p variants={fadeUp} className="text-gray-500 dark:text-gray-400 max-w-lg mx-auto">Four simple steps to transform your learning</motion.p>
        </motion.div>
        <motion.div initial="hidden" whileInView="visible" viewport={{ once: true }} variants={stagger} className="grid sm:grid-cols-2 lg:grid-cols-4 gap-8">
          {steps.map((s, i) => (
            <motion.div key={s.num} variants={fadeUp} className="relative">
              <span className="text-6xl font-display font-extrabold gradient-text opacity-20 absolute -top-4 -left-2">{s.num}</span>
              <div className="relative pt-10">
                <h3 className="font-semibold text-lg mb-2">{s.title}</h3>
                <p className="text-gray-500 dark:text-gray-400 text-sm leading-relaxed">{s.desc}</p>
              </div>
              {i < steps.length - 1 && (
                <div className="hidden lg:block absolute top-1/2 -right-4 w-8 border-t-2 border-dashed border-gray-300 dark:border-gray-700" />
              )}
            </motion.div>
          ))}
        </motion.div>
      </div>
    </section>
  )
}

function CTA() {
  return (
    <section className="py-24">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        <motion.div
          initial="hidden" whileInView="visible" viewport={{ once: true }} variants={fadeUp}
          className="relative rounded-3xl overflow-hidden p-12 sm:p-16 text-center gradient-bg"
        >
          <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjAiIGhlaWdodD0iNjAiIHZpZXdCb3g9IjAgMCA2MCA2MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48ZyBmaWxsPSJub25lIiBmaWxsLXJ1bGU9ImV2ZW5vZGQiPjxnIGZpbGw9IiNmZmZmZmYiIGZpbGwtb3BhY2l0eT0iLjA1Ij48cGF0aCBkPSJNMzYgMzRoLTJ2LTRoMnYtMmgtNHY2aDJ2Mmgydi0yaDJ2LTJoLTJ2MnptMC0xMGgtMnYyaDJ2LTJ6Ii8+PC9nPjwvZz48L3N2Zz4=')] opacity-30" />
          <div className="relative">
            <h2 className="text-3xl sm:text-4xl font-display font-bold text-white mb-4">Ready to Transform Your Learning?</h2>
            <p className="text-white/80 max-w-xl mx-auto mb-8">Join LearnMate AI and get a personalised roadmap to your dream career.</p>
            <Link to="/register" className="inline-flex items-center gap-2 px-8 py-4 bg-white text-primary-600 font-bold rounded-xl hover:bg-gray-100 transition-all shadow-xl">
              <HiOutlineRocketLaunch className="w-5 h-5" /> Get Started Free
            </Link>
          </div>
        </motion.div>
      </div>
    </section>
  )
}

function Footer() {
  return (
    <footer className="py-12 border-t border-gray-200 dark:border-gray-800">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
        <div className="flex items-center justify-center gap-2 mb-4">
          <div className="w-8 h-8 rounded-lg gradient-bg flex items-center justify-center">
            <span className="text-white font-bold text-xs">LM</span>
          </div>
          <span className="font-display font-bold gradient-text">LearnMate AI</span>
        </div>
        <p className="text-gray-500 dark:text-gray-400 text-sm">AI-powered personalised learning platform. Built with FastAPI + React.</p>
      </div>
    </footer>
  )
}

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-950">
      <Navbar />
      <Hero />
      <Features />
      <HowItWorks />
      <CTA />
      <Footer />
    </div>
  )
}
