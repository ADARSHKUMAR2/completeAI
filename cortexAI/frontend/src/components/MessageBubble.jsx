import React from 'react'
import { Bot, User } from 'lucide-react'
import Markdown from 'react-markdown'

// 🚀 Destructure { role, content } from props
function MessageBubble({ role, content }) {
    const isUser = role === 'user'

    return (
        <div className={`flex gap-3 max-w-3xl mx-auto py-3 ${isUser ? 'justify-end' : 'justify-start'}`}>
            {/* AI Avatar */}
            {!isUser && (
                <div className='w-8 h-8 rounded-lg bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center shrink-0 text-indigo-400 mt-1'>
                    <Bot size={16} />
                </div>
            )}

            {/* Message Bubble Content */}
            <div
                className={`px-4 py-3 rounded-2xl text-[14px] leading-relaxed max-w-[85%] whitespace-pre-wrap ${isUser
                    ? 'bg-gradient-to-br from-indigo-500 to-violet-700 text-white rounded-tr-xs'
                    : 'bg-white/[0.04] border border-white/[0.08] text-slate-200 rounded-tl-xs'
                    }`}
            >
                <Markdown>{content}</Markdown>
            </div>

            {/* User Avatar */}
            {isUser && (
                <div className='w-8 h-8 rounded-lg bg-white/[0.06] border border-white/[0.08] flex items-center justify-center shrink-0 text-slate-400 mt-1'>
                    <User size={16} />
                </div>
            )}
        </div>
    )
}

export default MessageBubble