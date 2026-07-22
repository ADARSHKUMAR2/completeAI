import React from 'react'
import { Bot, User } from 'lucide-react'
import Markdown from 'react-markdown'
import { useState } from 'react'
import { X } from 'lucide-react'
import remarkGfm from 'remark-gfm'
import { ExternalLink } from 'lucide-react'
import SyntaxHighlighter from 'react-syntax-highlighter'
import { Copy, Check } from 'lucide-react'
import { Prism as SyntaxHighlighterBase } from 'react-syntax-highlighter'

// 🚀 Destructure { role, content } from props
function MessageBubble({ role, content, images }) {
    const isUser = role === 'user'
    const [lightBox, setLightBox] = useState(null)
    const [copiedCode, setCopiedCode] = useState("")

    const copyCode = async (code) => {
        await navigator.clipboard.writeText(code)
        setCopiedCode(code)
        setTimeout(() => setCopiedCode(""), 2000)
    }


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

                {images?.length > 0 && (
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

                <Markdown
                    remarkPlugins={[remarkGfm]}
                    components={{
                        h1: ({ children }) => (
                            <h1 className="text-2xl font-bold mt-5 mb-3">{children}</h1>
                        ),
                        h2: ({ children }) => (
                            <h2 className="text-xl font-semibold mt-4 mb-2">{children}</h2>
                        ),
                        h3: ({ children }) => (
                            <h3 className="text-lg font-semibold mt-3 mb-2">{children}</h3>
                        ),
                        p: ({ children }) => (
                            <p className="mb-3 whitespace-pre-wrap break-words">{children}</p>
                        ),
                        ul: ({ children }) => (
                            <ul className="list-disc pl-5 space-y-1 my-2">{children}</ul>
                        ),
                        ol: ({ children }) => (
                            <ol className='list-decimal pl-5 space-y-1 my-2'>{children}</ol>
                        ),
                        table: ({ children }) => (
                            <div className='overflow-x-auto my-4'>
                                <table className='min-w-full border border-white/10'>
                                    {children}
                                </table>
                            </div>
                        ),
                        th: ({ children }) => (
                            <th className='border border-white/10 bg-white/5 px-3 py-2 text-left'>
                                {children}
                            </th>
                        ),
                        td: ({ children }) => (
                            <td className='border border-white/10 px-3 py-2'>{children}</td>
                        ),
                        a: ({ href, children }) => (
                            <a
                                href={href}
                                target="_blank"
                                rel="noreferrer"
                                className="text-indigo-400 underline inline-flex items-center gap-1"
                            >
                                {children}
                                <ExternalLink size={14} />
                            </a>
                        ),
                        code: ({ className, children }) => {
                            const value = String(children).trim();

                            if (!className) {
                                return (
                                    <code className='px-1.5 py-0.5 rounded bg-white/10 text-indigo-200'>
                                        {value}
                                    </code>
                                )
                            }

                            const language = className?.replace("language-", "")

                            return (
                                <div className='my-4 overflow-hidden rounded-xl border border-white/10 bg-[#111318]'>
                                    <div className='flex items-center justify-between bg-[#1b1d24] border-b border-white/10 px-4 py-2'>
                                        <span className='uppercase text-xs text-slate-400'>
                                            {language}
                                        </span>
                                        <button className='flex items-center gap-1 text-xs'
                                            onClick={() => copyCode(value)}
                                        >
                                            {
                                                copiedCode == value ?
                                                    <>
                                                        <Check size={14} />
                                                        Copied
                                                    </> :
                                                    <><Copy size={14} />Copy</>
                                            }
                                        </button>
                                    </div>

                                    <SyntaxHighlighter
                                        language={language}
                                        style={vs}
                                        customStyle={{
                                            backgroundColor: "#1b1d24",
                                            padding: "1rem",
                                            borderRadius: "0.5rem",
                                            fontSize: "0.9rem",
                                            lineHeight: "1.5rem",
                                            overflow: "auto",
                                            whiteSpace: "pre-wrap",
                                            wordBreak: "break-word",
                                            wordWrap: "break-word",
                                        }}
                                    >
                                        {value}
                                    </SyntaxHighlighter>

                                </div>
                            )
                        }


                    }}
                >
                    {content}
                </Markdown>
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