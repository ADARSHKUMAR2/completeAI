import React from 'react'
import api from '../../utils/axios'

async function sendMessage(payload) {
  try {

    console.log("FormData Contents:", Object.fromEntries(payload.entries()));
    const { data } = await api.post("/agent/chat", payload)
    return data
  } catch (error) {
    console.log(error)
    console.error("FastAPI Error Response:", error.response?.data);
    console.error("HTTP Status Code:", error.response?.status);
    return null
  }
}

export default sendMessage