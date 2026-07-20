import React from 'react'
import api from '../../utils/axios'

async function logOut() {
  try {
    const { data } = await api.post("/auth/logout")
    console.log(data)
  } catch (error) {
    console.log(error)
  }
}

export default logOut