import api from '../../utils/axios'

export const getMessages = async (conversationId) => {
  try {
    const { data } = await api.get(`/chat/message/get/${conversationId}`)
    return data
  } catch (error) {
    console.error("Error fetching messages:", error)
    return []
  }
}

export default getMessages