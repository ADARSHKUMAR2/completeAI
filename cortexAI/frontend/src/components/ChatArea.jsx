import getMessages from '../features/getMessages'
import { setMessages, setArtifacts } from '../redux/messageSlice'
import React, { useEffect } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import Nav from './Nav'
import MessageList from './MessageList'
import ChatInput from './ChatInput'
import Artifact from './Artifact'

function ChatArea() {
  const { selectedConversation } = useSelector(state => state.conversation)
  const dispatch = useDispatch()

  useEffect(() => {
    const getMesg = async () => {
      if (selectedConversation) {
        if (selectedConversation.title === "New Chat") return
        const data = await getMessages(selectedConversation._id)
        dispatch(setMessages(data))

        const latestArtifactMessage = [...data].reverse().find(msg => msg.artifacts && msg.artifacts.length > 0)
        dispatch(setArtifacts(latestArtifactMessage?.artifacts || []))
      }
    }

    getMesg()
  }, [selectedConversation?._id])

  return (
    <div className='flex-1 flex flex-col min-w-0'>
      <Nav />
      <MessageList />
      <ChatInput />
    </div>
  )
}

export default ChatArea