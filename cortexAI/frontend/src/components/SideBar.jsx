import { PanelLeftIcon, PenSquare, Plus, User, Coins, LogOut, PanelRight, MessageSquare, Menu, X } from "lucide-react"
import React, { useState, useEffect } from 'react'
import { useDispatch, useSelector } from "react-redux"
import { setConversations, addConversation, setSelectedConversation } from "../redux/conversationSlice"
import { setUserData } from "../redux/userSlice"
import { getConversations } from "../features/getConversations"
import { createConversation } from "../features/createConversation"
import logOut from "../features/logout"
import BillingDrawer from "./BillingDrawer"

function SideBar() {
  const [collapsed, setCollapsed] = useState(false)
  const [imageError, setImageError] = useState(false)
  const [showBilling, setShowBilling] = useState(false)
  const [mobileOpen, setMobileOpen] = useState(false)

  const dispatch = useDispatch()
  const { conversations, selectedConversation } = useSelector(state => state.conversation)
  const { userData } = useSelector(state => state.user)

  useEffect(() => {
    const getConv = async () => {
      const data = await getConversations()
      dispatch(setConversations(data))
      if (!selectedConversation && data?.length > 0) {
        dispatch(setSelectedConversation(data[0]))
      }
    }
    getConv()
  }, [userData?._id])

  const handleCreateConversation = async () => {
    const data = await createConversation()
    if (data) {
      dispatch(addConversation(data))
      dispatch(setSelectedConversation(data))
      setMobileOpen(false)
    }
  }

  const handleLogOut = async () => {
    await logOut()
    dispatch(setUserData(null))
  }

  // Reusable Sidebar Content Component (Used for both Desktop Expanded & Mobile Drawer)
  const SidebarContent = ({ isMobile = false }) => (
    <div className='flex flex-col h-full bg-[#0d0f14]'>
      {/* Header section */}
      <div className='flex items-center gap-2.5 px-4 py-4 border-b border-white/[0.06]'>
        {!isMobile && (
          <button
            className='hidden lg:flex items-center justify-center w-7 h-7 rounded-lg text-slate-500 
            hover:text-slate-200 hover:bg-white/[0.05] transition-colors duration-150 bg-transparent 
            border-none cursor-pointer'
            onClick={() => setCollapsed(!collapsed)}
          >
            <PanelLeftIcon size={16} />
          </button>
        )}

        <span className='text-[16px] font-semibold text-slate-100 tracking-tight flex-1'>
          CortexAI
        </span>

        <span className='text-[10px] font-medium text-indigo-400 bg-indigo-500/10 border 
        border-indigo-500/20 px-2 py-0.5 rounded-full tracking-wide'>
          {userData?.plan || 'Free'}
        </span>

        <button
          className='flex items-center justify-center w-7 h-7 rounded-lg text-slate-500 
          hover:text-slate-200 hover:bg-white/[0.05] transition-colors duration-150 bg-transparent 
          border-none cursor-pointer'
          onClick={() => {
            dispatch(setSelectedConversation(null))
            if (isMobile) setMobileOpen(false)
          }}
        >
          <PenSquare size={14} />
        </button>

        {isMobile && (
          <button
            className='lg:hidden flex items-center justify-center w-7 h-7 rounded-lg text-slate-500 hover:text-white'
            onClick={() => setMobileOpen(false)}
          >
            <X size={16} />
          </button>
        )}
      </div>

      {/* Action button section */}
      <div className='px-4 pt-4 pb-1'>
        <button
          className='w-full flex items-center justify-center gap-2 text-sm font-medium text-white 
          bg-linear-to-br from-indigo-500 to-violet-700 rounded-xl py-[10px] border-none cursor-pointer 
          hover:opacity-90 transition-opacity duration-150'
          onClick={() => {
            dispatch(setSelectedConversation(null))
            if (isMobile) setMobileOpen(false)
          }}
        >
          <Plus size={15} />
          New Chat
        </button>
      </div>

      {/* Recents Label */}
      <div className='px-5 pt-4 pb-1.5 text-[10.5px] font-semibold uppercase tracking-widest text-slate-600'>
        {conversations.length === 0 ? "No Recent Conversations" : "Recents"}
      </div>

      {/* Conversations List */}
      <div className='flex-1 overflow-y-auto px-2.5 pb-2 [scrollbar-width:none] [&::-webkit-scrollbar]:hidden'>
        {conversations.map((conv, i) => {
          const isActive = selectedConversation?._id === conv?._id
          return (
            <div
              key={conv?._id || i}
              onClick={() => {
                dispatch(setSelectedConversation(conv))
                if (isMobile) setMobileOpen(false)
              }}
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

              <span className={`text-[13px] font-medium truncate ${isActive ? "text-slate-100" : "text-slate-300"}`}>
                {conv?.title || "New Chat"}
              </span>
            </div>
          )
        })}
      </div>

      {/* Footer Profile Section */}
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
              <p className='text-[11px] text-slate-600 mt-px'> {userData.plan} Tier</p>
            </div>

            <div className='flex gap-1'>
              <button
                onClick={() => setShowBilling(true)}
                className='flex items-center justify-center w-7 h-7 rounded-[7px] border-none bg-transparent text-yellow-600 cursor-pointer hover:bg-white/[0.08] transition-all duration-150'
              >
                <Coins size={16} />
              </button>

              <button
                onClick={handleLogOut}
                className='flex items-center justify-center w-7 h-7 rounded-[7px] border-none bg-transparent text-slate-600 cursor-pointer hover:bg-white/[0.08] hover:text-slate-400 transition-all duration-150'
              >
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
  )

  return (
    <>
      {/* 📱 1. Mobile Menu Trigger Button (Always visible on mobile) */}
      <button
        className='lg:hidden fixed top-3.5 left-4 z-50 flex items-center justify-center w-8 h-7 rounded-xl bg-[#0d0f14] border border-white/10 text-slate-300 hover:text-white shadow-lg cursor-pointer'
        onClick={() => setMobileOpen(true)}
      >
        <Menu size={14} />
      </button>

      {/* 📱 2. Mobile Backdrop Overlay */}
      {mobileOpen && (
        <div
          onClick={() => setMobileOpen(false)}
          className='lg:hidden fixed inset-0 z-40 bg-black/60 backdrop-blur-sm'
        />
      )}

      {/* 📱 3. Mobile Sidebar Drawer */}
      <aside
        className={`lg:hidden fixed top-0 left-0 bottom-0 z-50 w-[270px] bg-[#0d0f14] border-r border-white/10 transition-transform duration-300 ease-in-out ${mobileOpen ? 'translate-x-0' : '-translate-x-full'
          }`}
      >
        <SidebarContent isMobile={true} />
      </aside>

      {/* 🖥️ 4. Desktop Collapsed Sidebar */}
      {collapsed ? (
        <div className='hidden lg:flex flex-col items-center w-[56px] h-screen bg-[#0d0f14] border-r border-white/[0.06] py-4 gap-1 shrink-0'>
          <button
            className='flex items-center justify-center w-9 h-9 rounded-xl text-slate-500 hover:text-slate-200 hover:bg-white/[0.05] transition-colors duration-150 bg-transparent border-none cursor-pointer mb-1'
            onClick={() => setCollapsed(false)}
          >
            <PanelRight size={18} />
          </button>

          <button
            className='flex items-center justify-center w-9 h-9 rounded-xl text-slate-500 hover:text-slate-200 hover:bg-white/[0.05] transition-colors duration-150 bg-transparent border-none cursor-pointer'
            onClick={() => dispatch(setSelectedConversation(null))}
          >
            <Plus size={17} />
          </button>

          <div className='flex-1 overflow-y-auto px-2.5 pb-2 [scrollbar-width:none] [&::-webkit-scrollbar]:hidden pt-5'>
            {conversations.map((conv, i) => {
              const isActive = selectedConversation?._id === conv?._id
              return (
                <div
                  key={conv?._id || i}
                  onClick={() => dispatch(setSelectedConversation(conv))}
                  className={`flex items-center gap-2.5 cursor-pointer mb-0.5 px-2 py-2 rounded-[10px] border transition-colors duration-150 ${isActive
                    ? "bg-indigo-500/10 border-indigo-500/[0.18]"
                    : "bg-transparent border-transparent"
                    }`}
                >
                  <div
                    className={`flex items-center justify-center shrink-0 w-[20px] h-[20px] rounded-lg transition-colors duration-150 ${isActive
                      ? "bg-indigo-500/15 text-indigo-400"
                      : "bg-white/[0.05] text-slate-500"
                      }`}
                  >
                    <MessageSquare size={13} />
                  </div>
                </div>
              )
            })}
          </div>

          <div className='relative shrink-0'>
            {userData?.avatar && !imageError ? (
              <img
                className='w-9 h-9 rounded-[10px] object-cover border-2 border-indigo-500/25'
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
        </div>
      ) : (
        /* 🖥️ 5. Desktop Expanded Sidebar */
        <div className='hidden lg:block w-[270px] h-screen shrink-0 border-r border-white/[0.06] bg-[#0d0f14]'>
          <SidebarContent isMobile={false} />
        </div>
      )}

      {/* Billing Modal Drawer */}
      <BillingDrawer
        open={showBilling}
        onClose={() => setShowBilling(false)}
      />
    </>
  )
}

export default SideBar