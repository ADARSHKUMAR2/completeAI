import api from "../../utils/axios"

export const updateConversation = async (payload) => {
    try {
        const { data } = await api.put("/chat/update", payload)
        console.log(data)
        return data
    } catch (error) {
        console.log(error)
        return []
    }
}