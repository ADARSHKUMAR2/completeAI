import React from 'react'
import { PanelRightClose, PanelRightOpen } from 'lucide-react'
import { useSelector } from 'react-redux'
import { Code2 } from 'lucide-react'
import { motion } from 'motion/react'
import { Copy, Eye } from 'lucide-react'


function Artifact() {
  const { artifacts } = useSelector(state => state.message)
  const [collapsed, setCollapsed] = React.useState(false)
  const [tab, setTab] = React.useState("code")
  const [activeFile, setActiveFile] = React.useState(0)

  if (artifacts.length === 0) return;

  return (
    <motion.div
      initial={{ width: "350px" }}
      animate={{ width: collapsed ? "48px" : "350px" }}
      transition={{ duration: 0.2, ease: "easeInOut" }}
      className='hidden lg:flex h-full border-l border-white/[0.06] flex-col overflow-hidden shrink-0'
    >
      {!collapsed ?
        <div className='flex flex-col h-full bg-[#0d0f14]'>
          <div className='h-14 px-4 border-b border-white/[0.06] flex items-center gap-3 shrink-0'>
            <button
              className='flex items-center justify-center w-7 h-7 rounded-lg text-slate-500 hover:text-slate-200 hover:bg-white/[0.05] transition-colors duration-150 bg-transparent border-none cursor-pointer shrink-0'
              onClick={() => setCollapsed(true)}
            >
              <PanelRightClose size={16} />
            </button>

            <div className='flex items-center gap-2 flex-1 min-w-0'>
              <div className='flex items-center justify-center w-6 h-6 rounded-md bg-indigo-500/10 border border-indigo-500/20 shrink-0'>
                <Code2 className="text-indigo-400" size={12} />
              </div>
              <div className='text-[13px] font-medium text-slate-200 truncate'>
                {artifacts[0]?.title}
              </div>
            </div>

            <div className='flex items-center gap-1 shrink-0'>
              <button
                className='flex items-center gap-1.5 px-2.5 py-1.5 text-[11px] font-medium text-slate-400 hover:text-slate-200 hover:bg-white/[0.05] rounded-lg transition-colors duration-150 bg-transparent border-none cursor-pointer'
              >
                <Copy size={15} />
              </button>
            </div>

            <div className='flex items-center gap-1 bg-white/[0.04] border border-white/[0.06] p-1 rounded-lg'>
              <button
                onClick={() => setTab("code")}
                className={`flex items-center gap-1.5 px-2.5 py-1 text-[11px] font-medium rounded-md transition-colors duration-150 ${tab === "code" ? "bg-indigo-500 text-white" : "text-slate-500 hover:text-slate-200"
                  }`}
              >
                <Code2 size={11} /> Code
              </button>
              <button
                onClick={() => setTab("preview")}
                className={`flex items-center gap-1.5 px-2.5 py-1 text-[11px] font-medium rounded-md transition-colors duration-150 ${tab === "preview" ? "bg-indigo-500 text-white" : "text-slate-500 hover:text-slate-200"
                  }`}
              >
                <Eye size={11} /> Preview
              </button>
            </div>

          </div>



        </div>

        :

        <div className='hidden lg:flex flex-col h-full border-1 border-white/[0.06] bg-[#0d0f14] items-center py-4 gap-3 shrink-0'>
          <button
            className='flex items-center justify-center w-7 h-7 rounded-lg text-slate-500 hover:text-slate-200 hover:bg-white/[0.05] transition-colors duration-150 bg-transparent border-none cursor-pointer shrink-0'
            onClick={() => setCollapsed(false)}
          >
            <PanelRightOpen size={16} />
          </button>

          <div className='flex items-center gap-2 flex-1 min-w-0'>

            <div className='text-[10px] font-medium text-slate-600 tracking-widest uppercase whitespace-nowrap'
              style={{
                writingMode: "vertical-lr",
                transform: "rotate(180deg)",
              }}>
              {artifacts[0]?.title}
            </div>
          </div>
        </div>}

    </motion.div>
  )
}
export default Artifact 