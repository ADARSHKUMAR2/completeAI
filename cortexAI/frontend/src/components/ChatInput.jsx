import React, { useState } from 'react'
import { Paperclip, Mic, Send } from 'lucide-react'
import { useSelector } from 'react-redux'
import sendMessage from '../features/sendMessage'
import { addMessage } from '../redux/messageSlice'
import { useDispatch } from 'react-redux'

function ChatInput() {
    const [value, setValue] = useState("")
    const { selectedConversation } = useSelector(state => state.conversation)
    const dispatch = useDispatch()

    const handleSendMessage = async () => {
        // 1. Create textPayload variable
        const textPayload = value.trim()
        if (!textPayload) return

        // 2. Dispatch user message to UI state immediately
        dispatch(addMessage({
            role: "user",
            content: textPayload
        }))

        // Clear input text field
        setValue("")

        // 3. Fire a SINGLE request to the Agent
        try {
            const payloadData = await sendMessage({
                prompt: textPayload,
                conversationId: selectedConversation?._id || ""
            })

            // 4. Dispatch AI response to UI state once received
            if (payloadData?.response) {
                dispatch(addMessage({
                    role: "assistant",
                    content: payloadData.response
                }))
            }
        } catch (error) {
            console.error("Failed to send message:", error)
        }
    }

    return (
        <div className='w-full overflow-hidden px-3 md:px-5 py-4 border-t border-white/[0.06] bg-[#0d0f14]'>
            <div className='flex flex-col gap-2 bg-white/[0.03] border border-white/[0.07] rounded-2xl px-4 pt-3.5 pb-3'>
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