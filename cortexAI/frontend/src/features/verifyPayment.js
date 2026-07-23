import api from "../../utils/axios"

export const verifyPayment = async (payload) => {
    try {
        const { data } = await api.post("/billing/verify", payload)
        console.log("🎉 verifyPayment API Response FE:", data)
        return data
    } catch (error) {
        console.log(error)
        return []
    }
}