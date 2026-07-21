import api from '../../utils/axios'

async function getMessages(id) {
  try {
    const { data } = await api.post("/chat/message/get", { conversationId: id })
    console.log(data)
    return data
  } catch (error) {
    console.log(error)
    return []
  }
}

export default getMessages