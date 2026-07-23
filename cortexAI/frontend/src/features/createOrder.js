// src/features/createOrder.js
import api from "../../utils/axios";

export const createOrder = async (plan, userId) => {
    try {
        const response = await api.post(
            "/billing/create-order",
            { plan },
            {
                headers: {
                    "x-user-id": userId,
                },
            }
        );
        return response.data;
    } catch (error) {
        console.error("❌ createOrder API Error:", error);
        throw error;
    }
};