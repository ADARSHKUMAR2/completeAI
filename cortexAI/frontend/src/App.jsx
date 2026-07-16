import React from 'react'
import { auth, googleProvider } from '../utils/firebase'
import { signInWithPopup } from 'firebase/auth'

function App() {

  const googleLogin= async () => {
    const data = await signInWithPopup(auth,googleProvider)
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

