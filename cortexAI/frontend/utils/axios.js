import axios from "axios";

const api = axios.create({
  // Point this directly to your FastAPI Gateway port
  baseURL: import.meta.env.VITE_SERVER_URL || "http://localhost:8000",
  
  // CRUCIAL: This allows HTTP-only session cookies to pass back and forth
  withCredentials: true, 
  
  headers: {
    "Content-Type": "application/json",
  }
});

export default api;