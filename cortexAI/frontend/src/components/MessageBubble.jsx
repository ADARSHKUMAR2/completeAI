import React from 'react'
import { Bot, User } from 'lucide-react'
import Markdown from 'react-markdown'
import { useState } from 'react'
import { X } from 'lucide-react'

// 🚀 Destructure { role, content } from props
function MessageBubble({ role, content, images }) {
    const isUser = role === 'user'
    const [lightBox, setLightBox] = useState(null)

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

                {images.length > 0 && (
                    <div className='flex flex-wrap gap-3 mt-4'>
                        {images.map((img, i) => (
                            <img
                                key={i}
                                src={img}
                                onClick={() => setLightBox(img)}
                                loading="lazy"
                                onError={(e) => e.currentTarget.remove()}
                                className="w-40 h-28 rounded-xl object-cover border border-white/10 cursor-zoom-in hover:opacity-90 transition"
                            />
                        ))}
                    </div>
                )}

                <Markdown>{content}</Markdown>
            </div>

            {lightBox && (
                <div className='fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-6'>
                    <button
                        className='absolute top-5 right-5 text-white/80 hover:text-white bg-white/10 rounded-full p-2'
                        onClick={() => setLightBox(null)}
                    >
                        <X />
                    </button>
                    <img
                        src={lightBox}
                        className="max-w-[90vw] max-h-[85vh] rounded-2xl border border-white/10 shadow-2xl object-contain"
                    />
                </div>
            )}

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