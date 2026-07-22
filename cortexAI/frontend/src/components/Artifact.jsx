import React, { useState } from 'react'
import { PanelRightClose, PanelRightOpen, Code2, Copy, Eye, Check } from 'lucide-react'
import { useSelector } from 'react-redux'
import { motion } from 'framer-motion'
import Editor from '@monaco-editor/react'

function Artifact() {
  const { artifacts } = useSelector(state => state.message)
  const [collapsed, setCollapsed] = useState(false)
  const [tab, setTab] = useState("code")
  const [activeFile, setActiveFile] = useState(0)
  const [copied, setCopied] = useState(false)

  if (!artifacts || artifacts.length === 0) return null;

  // 1. Separate file object and file string content properly
  const currentFile = artifacts[0]?.files?.[activeFile] || {}
  const fileContent = currentFile?.content || ""
  const fileName = currentFile?.name || ""

  const files = artifacts[0]?.files || []
  const htmlFile = files.find(f => f.name?.endsWith('.html'))?.content
  const cssFile = files.find(f => f.name?.endsWith('.css'))?.content
  const jsFile = files.find(f => f.name?.endsWith('.js'))?.content

  const canPreview = Boolean(htmlFile)

  const previewDoc = `<!DOCTYPE html>
                      <html lang="en">
                      <head>
                          <meta charset="UTF-8">
                          <meta name="viewport" content="width=device-width, initial-scale=1.0">
                          <style>
                              ${cssFile || ''}
                          </style>
                      </head>
                      <body>
                          ${htmlFile || ''}
                      <script>
                          ${jsFile || ''}
                      </script>
                      </body>
                      </html>`

  const handleCopyCode = async () => {
    await navigator.clipboard.writeText(file?.content)
    setCopied(true)
    setTimeout(() => setCopiedCode(false), 2000)
  }

  const detectLanguage = (name = "") => {
    const lowerName = name.toLowerCase();

    if (lowerName.endsWith(".html")) return "html";
    if (lowerName.endsWith(".css")) return "css";
    if (lowerName.endsWith(".js") || lowerName.endsWith(".jsx")) return "javascript";
    if (lowerName.endsWith(".ts") || lowerName.endsWith(".tsx")) return "typescript";
    if (lowerName.endsWith(".json")) return "json";
    if (lowerName.endsWith(".py")) return "python";
    if (lowerName.endsWith(".java")) return "java";
    if (lowerName.endsWith(".cpp")) return "cpp";
    if (lowerName.endsWith(".c")) return "c";

    return "plaintext";
  };

  const handleCopy = () => {
    if (fileContent) {
      navigator.clipboard.writeText(fileContent)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    }
  }

  return (
    <motion.div
      initial={{ width: "400px" }}
      animate={{ width: collapsed ? "48px" : "400px" }}
      transition={{ duration: 0.2, ease: "easeInOut" }}
      className='hidden lg:flex h-full border-l border-white/[0.06] flex-col overflow-hidden shrink-0'
    >
      {!collapsed ? (
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
                {artifacts[0]?.title || "Artifact"}
              </div>
            </div>

            <div className='flex items-center gap-1 shrink-0'>
              <button
                onClick={handleCopy}
                className='flex items-center gap-1.5 px-2.5 py-1.5 text-[11px] font-medium text-slate-400 hover:text-slate-200 hover:bg-white/[0.05] rounded-lg transition-colors duration-150 bg-transparent border-none cursor-pointer'
              >
                {copied ? <Check size={15} className="text-emerald-400" /> : <Copy size={15} />}
              </button>
            </div>

            {canPreview && (
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
            )}
          </div>

          {tab === "code" && (
            <div className='flex h-auto border-b border-white/[0.06] overflow-x-auto [scrollbar-width:none] [&::-webkit-scrollbar]:hidden shrink-0'>
              {artifacts[0]?.files?.map((f, index) => (
                <button
                  key={index}
                  onClick={() => setActiveFile(index)}
                  className={`px-4 py-2.5 text-[11px] font-medium whitespace-nowrap transition-colors duration-150 border-r border-white/[0.05] relative cursor-pointer bg-transparent ${activeFile === index ? "text-indigo-400" : "text-slate-500 hover:text-slate-300"
                    }`}
                >
                  {f?.name}
                  {activeFile === index && (
                    <div className='absolute bottom-0 left-0 right-0 h-[2px] bg-indigo-500 rounded-t-full' />
                  )}
                </button>
              ))}
            </div>
          )}

          <div className='flex-1 overflow-hidden relative'>
            {tab === "preview" && canPreview ? (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ duration: 0.3 }}
                className='w-full h-full'
              >
                <iframe
                  title='preview'
                  srcDoc={previewDoc}
                  sandbox='allow-scripts'
                  className='w-full h-full bg-white border-none'
                />
              </motion.div>
            ) : (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ duration: 0.3 }}
                className='w-full h-full'
              >
                <Editor
                  theme="vs-dark"
                  language={detectLanguage(fileName)}
                  value={fileContent}
                  options={{
                    readOnly: true,
                    minimap: { enabled: false },
                    fontSize: 13,
                    wordWrap: "on",
                    automaticLayout: true,
                    scrollBeyondLastLine: false,
                    padding: { top: 16 },
                    lineNumbers: "on",
                    renderLineHighlight: "none"
                  }}
                />
              </motion.div>
            )}
          </div>
        </div>
      ) : (
        <div className='hidden lg:flex flex-col h-full border-l border-white/[0.06] bg-[#0d0f14] items-center py-4 gap-3 shrink-0'>
          <button
            className='flex items-center justify-center w-7 h-7 rounded-lg text-slate-500 hover:text-slate-200 hover:bg-white/[0.05] transition-colors duration-150 bg-transparent border-none cursor-pointer shrink-0'
            onClick={() => setCollapsed(false)}
          >
            <PanelRightOpen size={16} />
          </button>

          <div className='flex items-center gap-2 flex-1 min-w-0'>
            <div
              className='text-[10px] font-medium text-slate-600 tracking-widest uppercase whitespace-nowrap'
              style={{
                writingMode: "vertical-lr",
                transform: "rotate(180deg)",
              }}
            >
              {artifacts[0]?.title || "Artifact"}
            </div>
          </div>
        </div>
      )}
    </motion.div>
  )
}

export default Artifact