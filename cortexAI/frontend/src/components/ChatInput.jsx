import React, { useState } from 'react'
import { Paperclip, Mic, Send, Code2, Globe, Zap, MessageSquare, FileText, Presentation, ImageIcon } from 'lucide-react'
import { useSelector } from 'react-redux'
import sendMessage from '../features/sendMessage'
import { addMessage, setArtifacts, setMessages } from '../redux/messageSlice'
import { useDispatch } from 'react-redux'
import { setSelectedConversation, addConversation } from '../redux/conversationSlice'
import { createConversation } from '../features/createConversation'
import { setConvTitle } from '../redux/conversationSlice'
import { updateConversation } from '../features/updateConversation'

function ChatInput() {
    const [value, setValue] = useState("")
    const [selectedAgent, setSelectedAgent] = useState("Auto")
    const { selectedConversation } = useSelector(state => state.conversation)
    const { messages } = useSelector(state => state.message)
    const dispatch = useDispatch()

    const handleSendMessage = async () => {
        const textPayload = value.trim()
        if (!textPayload)
            return

        // 1. Auto-create conversation if no active conversation exists
        let conversation = selectedConversation
        if (!conversation) {
            try {
                const conv = await createConversation()
                dispatch(setSelectedConversation(conv))
                dispatch(addConversation(conv))
                conversation = conv
            } catch (err) {
                console.error("Failed to create conversation:", err)
                return
            }
        }

        if (conversation.title === "New Chat") {
            const conv = await updateConversation({
                id: conversation?._id,
                title: value.trim()
            })
            dispatch(setConvTitle({
                conversationId: conversation?._id,
                title: value.slice(0, 20)
            }))
        }

        // 2. Prepare payload targeting the resolved conversation ID
        const payload = {
            prompt: textPayload,
            conversationId: conversation?._id || "",
            agent: selectedAgent.toLowerCase()
        }

        // 3. Dispatch user message to UI immediately & clear input
        dispatch(addMessage({
            role: "user",
            content: textPayload
        }))
        setValue("")

        // 4. Send request to Agent and update UI on response
        try {
            const data = await sendMessage(payload)
            console.log(data)

            const assistantContent = data?.answer || data?.aiResponse || ""
            const artifacts = data?.artifacts || []

            // 1. Append assistant response to messages list
            dispatch(addMessage({
                role: "assistant",
                content: assistantContent,
                images: data?.images,
                artifacts: artifacts
            }))

            // 2. Set artifacts state if present in the response
            if (artifacts.length > 0) {
                dispatch(setArtifacts(artifacts))
            }
        } catch (error) {
            console.error("Failed to send message:", error)
        }
    }

    const agents = [
        {
            id: "auto",
            icon: Zap,
            label: "Auto"
        },
        {
            id: "chat",
            icon: MessageSquare,
            label: "Chat"
        },
        {
            id: "search",
            icon: Globe,
            label: "Search"
        },
        {
            id: "coding",
            icon: Code2,
            label: "Coding"
        },
        {
            id: "pdf",
            icon: FileText,
            label: "PDF"
        },
        {
            id: "ppt",
            icon: Presentation,
            label: "PPT"
        },
        {
            id: "image_gen",
            icon: ImageIcon,
            label: "Image"
        }
    ]

    return (
        <div className='w-full overflow-hidden px-3 md:px-5 py-4 border-t border-white/[0.06] bg-[#0d0f14]'>
            <div className='flex flex-col gap-2 bg-white/[0.03] border border-white/[0.07] rounded-2xl px-4 pt-3.5 pb-3'>

                <div className='flex w-[80%] gap-2 pr-2 flex-wrap'>
                    {agents.map((agent) => {
                        const isActive = selectedAgent === agent.id
                        const Icon = agent.icon
                        return (
                            <div
                                onClick={() => setSelectedAgent(agent.id)}
                                className={`
    shrink-0
    cursor-pointer
    inline-flex
    items-center
    gap-1.5
    px-3
    py-2
    rounded-full
    text-xs
    font-medium
    border
    transition-all
    ${isActive
                                        ? "bg-gradient-to-r from-indigo-500 to-violet-600 text-white border-transparent shadow-[0_1px_8px_rgba(99,102,241,.35)]"
                                        : "bg-white/[0.03] text-slate-400 border-white/[0.06] hover:bg-white/[0.07]"
                                    }
  `}
                            >
                                <Icon size={14} className={
                                    isActive
                                        ? "text-white"
                                        : "text-slate-500"
                                } />

                                {agent.label}

                            </div>
                        )
                    })}
                </div>

                <textarea
                    placeholder='Ask Anything...'

                    onChange={(e) => setValue(e.target.value)}
                    value={value}

                    className='w-full bg-transparent outline-none resize-none text-[14px] text-slate-200 placeholder:text-slate-600 leading-relaxed [scrollbar-width:none] [&::-webkit-scrollbar]:hidden disabled:opacity-50'
                    rows={3}
                />

                <div className='flex items-center justify-between'>
                    <div className='flex items-center gap-1'>
                        <button className='flex items-center justify-center w-8 h-8 rounded-lg text-slate-600 hover:text-slate-400 hover:bg-white/[0.05] border border-transparent hover:border-white/[0.06] transition-all duration-150 bg-transparent cursor-pointer'>
                            <Paperclip size={16} />
                        </button>

                        <button className='flex items-center justify-center w-8 h-8 rounded-lg text-slate-600 hover:text-slate-400 hover:bg-white/[0.05] border border-transparent hover:border-white/[0.06] transition-all duration-150 bg-transparent cursor-pointer'>
                            <Mic size={16} />
                        </button>
                    </div>
                    <button
                        disabled={!value}
                        onClick={handleSendMessage}
                        className={`flex items-center justify-center w-8 h-8 rounded-lg border-none cursor-pointer transition-all duration-150 ${value.trim() ? "bg-linear-to-br from-indigo-500 to-violet-700 hover:opacity-90 text-white" : "bg-white/[0.05] text-slate-600 cursor-not-allowed"}`}
                    >
                        <Send size={15} />
                    </button>

                </div>
            </div>
        </div >
    )
}

export default ChatInput