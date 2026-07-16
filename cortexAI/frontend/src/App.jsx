import React from 'react'
import { auth, googleProvider } from '../utils/firebase'
import { signInWithPopup } from 'firebase/auth'
import api from '../utils/axios'

function App() {

  const handleLogin = async (firebaseToken) => {
  try {
    const response = await api.post("/auth/login", { token: firebaseToken });
    console.log("Logged in user data:", response.data);
  } catch (error) {
    console.error("API Error:", error.response?.data?.detail || error.message);
  }
};
 
  const googleLogin= async () => {
    const data = await signInWithPopup(auth,googleProvider)
    const token = await data.user.getIdToken()
    console.log(token)
    await handleLogin(token)
    console.log(data)
  }

  return (
    <div>
      <button className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded" onClick={googleLogin}>
        Continue with Google
      </button>
    </div>
  )
}

export default App 

