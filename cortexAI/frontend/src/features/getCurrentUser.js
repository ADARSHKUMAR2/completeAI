import api from "../../utils/axios";

const getCurrentUser = async () => {

    try {
        const response = await api.get("/me");
        console.log("Current user data:", response.data);
        return response.data;
    } catch (error) {
        console.error("API Error:", error.response?.data?.detail || error.message);
        return null;
    }
};

export default getCurrentUser;