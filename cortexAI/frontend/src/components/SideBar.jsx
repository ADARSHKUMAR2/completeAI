import { PanelLeftIcon, PenSquare, Plus, User, Coins, LogOut } from "lucide-react"
import React from 'react'
import { useState } from 'react'
import { useEffect } from "react";
import { useDispatch, useSelector } from "react-redux";
import { setConversations, addConversation, setSelectedConversation } from "../redux/conversationSlice";
import { getConversations } from "../features/getConversations";
import { createConversation } from "../features/createConversation";
import { MessageSquare } from "lucide-react";

function SideBar() {
  const [collapsed, setCollapsed] = React.useState(true)
  const dispatch = useDispatch()
  const [imageError, setImageError] = useState(false)
  const { conversations, selectedConversation } = useSelector(state => state.conversation)
  const { userData } = useSelector(state => state.user)

  useEffect(() => {
    const getConv = async () => {
      const data = await getConversations()
      dispatch(setConversations(data))
    }
    getConv()
  }, [])

  const handleCreateConversation = async () => {
    const data = await createConversation()
    dispatch(addConversation(data))
  }

  return (
    <div className='fixed lg:static inset-y-0 left-0 z-50 
      w-[270px] h-screen shrink-0 
      bg-[#0d0f14] border-r border-white/[0.06]
    '>
      <div className='flex flex-col h-full'>
        {/* Header section */}
        <div className='flex items-center gap-2.5 px-4 py-4 border-b border-white/[0.06]'>
          <div className='hidden lg:flex items-center justify-center w-7 h-7 rounded-lg text-slate-500 
            hover:text-slate-200 hover:bg-white/[0.05] transition-colors duration-150 bg-transparent 
            border-none cursor-pointer'
            onClick={() => setCollapsed(!collapsed)}
          >
            <PanelLeftIcon />
          </div>

          <span className='text-[16px] font-semibold text-slate-100 tracking-tight flex-1'>
            CortexAI
          </span>

          <span className='text-[10px] font-medium text-indigo-400 bg-indigo-500/10 border 
            border-indigo-500/20 px-2 py-0.5 rounded-full tracking-wide'>
            free
          </span>

          <button className='flex items-center justify-center w-7 h-7 rounded-lg text-slate-500 
            hover:text-slate-200 hover:bg-white/[0.05] transition-colors duration-150 bg-transparent 
            border-none cursor-pointer'
            onClick={handleCreateConversation}>
            <PenSquare size={14} />
          </button>
        </div>

        {/* Action button section */}
        <div className='px-4 pt-4 pb-1'>
          <button className='w-full flex items-center justify-center gap-2 text-sm font-medium text-white 
            bg-linear-to-br from-indigo-500 to-violet-700 rounded-xl py-[10px] border-none cursor-pointer 
            hover:opacity-90 transition-opacity duration-150'
            onClick={handleCreateConversation}>
            <Plus size={15} />
            New Chat
          </button>
        </div>

        {/* Header condition label */}
        <div className='px-5 pt-4 pb-1.5 text-[10.5px] font-semibold uppercase tracking-widest text-slate-600'>
          {conversations.length === 0 ? "No Recent Conversations" : "Recents"}
        </div>

        {/* Conversations List Matrix */}
        <div className='flex-1 overflow-y-auto px-2.5 pb-2 [scrollbar-width:none] [&::-webkit-scrollbar]:hidden'>
          {conversations.map((conv, i) => {
            const isActive = selectedConversation?._id === conv?._id
            return (
              <div
                key={conv?._id || i}
                onClick={() => dispatch(setSelectedConversation(conv))}
                className={`flex items-center gap-2.5 cursor-pointer mb-0.5 px-3 py-2.5 rounded-[10px] border transition-colors duration-150 ${isActive
                  ? "bg-indigo-500/10 border-indigo-500/[0.18]"
                  : "bg-transparent border-transparent"
                  }`}
              >
                <div
                  className={`flex items-center justify-center shrink-0 w-[28px] h-[28px] rounded-lg transition-colors duration-150 ${isActive
                    ? "bg-indigo-500/15 text-indigo-400"
                    : "bg-white/[0.05] text-slate-500"
                    }`}
                >
                  <MessageSquare size={13} />
                </div>

                <span
                  className={`text-[13px] font-medium truncate ${isActive ? "text-slate-100" : "text-slate-300"}`}
                >
                  {conv?.title || "New Chat"}
                </span>
              </div>
            )
          })}
        </div>

        {/* Footer profile container block */}
        <div className='mx-2.5 h-px bg-white/[0.06]' />
        <div className='px-3.5 py-3.5'>
          {userData ? (
            <div className='flex items-center gap-2.5 cursor-pointer rounded-xl px-3 py-2.5 hover:bg-white/[0.05] transition-colors duration-150'>
              <div className='relative shrink-0'>
                {userData?.avatar && !imageError ? (
                  <img
                    className='w-10 h-10 rounded-[10px] object-cover border-2 border-indigo-500/25'
                    src={userData?.avatar}
                    alt="User Avatar"
                    onError={() => setImageError(true)}
                  />
                ) : (
                  <div className='w-9 h-9 rounded-[10px] bg-white/[0.06] flex items-center justify-center'>
                    <User size={15} className='text-slate-400' />
                  </div>
                )}
              </div>

              <div className='flex-1 min-w-0'>
                <p className='text-[13.5px] font-semibold text-slate-100 truncate'>{userData?.name || "User"}</p>
                <p className='text-[11px] text-slate-600 mt-px'>{"Free Tier"}</p>
              </div>

              <div className='flex gap-1'>
                <button className='flex items-center justify-center w-7 h-7 rounded-[7px] border-none bg-transparent text-yellow-600 cursor-pointer hover:bg-white/[0.08] hover:text-slate-400 transition-all duration-150'>
                  <Coins size={16} />
                </button>

                <button className='flex items-center justify-center w-7 h-7 rounded-[7px] border-none bg-transparent text-slate-600 cursor-pointer hover:bg-white/[0.08] hover:text-slate-400 transition-all duration-150'>
                  <LogOut size={16} />
                </button>
              </div>

            </div>
          ) : (
            <button className='w-full text-center text-sm font-medium text-slate-300 bg-white/[0.05] hover:bg-white/[0.1] border border-white/[0.06] rounded-xl py-2 cursor-pointer transition-colors duration-150'>
              Login
            </button>
          )}
        </div>
      </div>
    </div>
  )
}

export default SideBar;