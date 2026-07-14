import { useState, useRef, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import {
  HiOutlinePaperAirplane, HiOutlineTrash, HiOutlineChatBubbleLeftEllipsis,
} from 'react-icons/hi2'
import { useApp } from '../context/AppContext'

const SUGGESTED_PROMPTS = [
  'What skills do I need to become an ML Engineer?',
  'Recommend projects for my portfolio',
  'How should I structure my learning this week?',
  'What certifications are most valuable?',
  'How do I transition from web dev to data science?',
]

function TypingIndicator() {
  return (
    <div className="flex items-center gap-1 px-4 py-3">
      <div className="w-2 h-2 rounded-full bg-gray-400 typing-dot" />
      <div className="w-2 h-2 rounded-full bg-gray-400 typing-dot" />
      <div className="w-2 h-2 rounded-full bg-gray-400 typing-dot" />
    </div>
  )
}

function ChatBubble({ msg }) {
  const isUser = msg.role === 'user'
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4`}
    >
      <div className={`max-w-[80%] sm:max-w-[70%] ${isUser ? 'order-2' : ''}`}>
        <div
          className={`px-4 py-3 rounded-2xl text-sm leading-relaxed ${
            isUser
              ? 'bg-primary-600 text-white rounded-br-md'
              : 'bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-bl-md'
          }`}
        >
          {isUser ? (
            <p>{msg.content}</p>
          ) : (
            <div className="prose prose-sm dark:prose-invert max-w-none prose-p:my-1 prose-pre:bg-gray-100 dark:prose-pre:bg-gray-900">
              <ReactMarkdown remarkPlugins={[remarkGfm]}>{msg.content || ''}</ReactMarkdown>
            </div>
          )}
        </div>
        {msg.ts && (
          <p className={`text-[10px] text-gray-400 mt-1 ${isUser ? 'text-right' : ''}`}>
            {new Date(msg.ts).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
          </p>
        )}
      </div>
    </motion.div>
  )
}

export default function Chat() {
  const { chatMessages, sendMessage, clearMessages, fetchChatHistory, loading, student } = useApp()
  const [input, setInput] = useState('')
  const messagesEnd = useRef(null)
  const inputRef = useRef(null)

  useEffect(() => {
    if (student?.student_id && chatMessages.length === 0) {
      fetchChatHistory()
    }
  }, [student, fetchChatHistory])

  useEffect(() => {
    messagesEnd.current?.scrollIntoView({ behavior: 'smooth' })
  }, [chatMessages, loading.chat])

  const handleSend = async () => {
    const text = input.trim()
    if (!text || loading.chat) return
    setInput('')
    try { await sendMessage(text) } catch {}
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); handleSend() }
  }

  return (
    <div className="flex flex-col h-[calc(100vh-4rem)]">
      {/* Header */}
      <div className="flex items-center justify-between px-4 sm:px-8 py-4 border-b border-gray-200 dark:border-gray-800">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl gradient-bg flex items-center justify-center">
            <HiOutlineChatBubbleLeftEllipsis className="w-5 h-5 text-white" />
          </div>
          <div>
            <h1 className="font-semibold">AI Mentor</h1>
            <p className="text-xs text-gray-500">{student?.name || 'Create a profile to start'}</p>
          </div>
        </div>
        {chatMessages.length > 0 && (
          <button onClick={clearMessages} className="btn-ghost text-sm text-red-500 hover:text-red-600 flex items-center gap-1">
            <HiOutlineTrash className="w-4 h-4" /> Clear
          </button>
        )}
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-4 sm:px-8 py-6">
        {chatMessages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-center">
            <div className="w-16 h-16 rounded-2xl gradient-bg flex items-center justify-center mb-4">
              <HiOutlineChatBubbleLeftEllipsis className="w-8 h-8 text-white" />
            </div>
            <h2 className="text-xl font-display font-bold mb-2">How can I help?</h2>
            <p className="text-gray-500 dark:text-gray-400 text-sm mb-8 max-w-sm">
              Ask me anything about your learning journey, career goals, or specific topics.
            </p>
            <div className="grid sm:grid-cols-2 gap-2 max-w-lg w-full">
              {SUGGESTED_PROMPTS.map((prompt) => (
                <button
                  key={prompt}
                  onClick={() => { setInput(prompt); inputRef.current?.focus() }}
                  className="text-left p-3 rounded-xl bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 text-sm hover:border-primary-300 dark:hover:border-primary-700 transition-colors"
                >
                  {prompt}
                </button>
              ))}
            </div>
          </div>
        ) : (
          <div className="max-w-3xl mx-auto space-y-2">
            {chatMessages.map((msg, i) => <ChatBubble key={i} msg={msg} />)}
            {loading.chat && (
              <div className="flex justify-start mb-4">
                <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-2xl rounded-bl-md">
                  <TypingIndicator />
                </div>
              </div>
            )}
            <div ref={messagesEnd} />
          </div>
        )}
      </div>

      {/* Input */}
      <div className="px-4 sm:px-8 py-4 border-t border-gray-200 dark:border-gray-800">
        <div className="max-w-3xl mx-auto flex items-end gap-3">
          <textarea
            ref={inputRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={student ? 'Ask your AI mentor...' : 'Create a profile first...'}
            disabled={!student}
            rows={1}
            className="input-field resize-none min-h-[48px] max-h-[120px] !py-3"
          />
          <button
            onClick={handleSend}
            disabled={!input.trim() || loading.chat || !student}
            className="btn-primary !p-3 !rounded-xl flex-shrink-0"
          >
            <HiOutlinePaperAirplane className="w-5 h-5" />
          </button>
        </div>
      </div>
    </div>
  )
}
