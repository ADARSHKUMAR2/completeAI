import React from 'react'
import { signInWithPopup } from 'firebase/auth'
import { auth, googleProvider } from "../../utils/firebase";
// Import BOTH the default client and the AUTH_URL string
import api from "../../utils/axios";
import { FcGoogle } from 'react-icons/fc'
import { useSelector, useDispatch } from 'react-redux'
import { setUserData } from '../redux/userSlice'
import ChatArea from '../components/ChatArea'
import SideBar from '../components/SideBar'
import Artifact from '../components/Artifact'

function Home() {

  const { userData } = useSelector(state => state.user)
  // console.log("User data:", userData)

  const dispatch = useDispatch()

  const handleLogin = async (firebaseToken) => {
    try {
      // Direct this call straight to port 8001
      const response = await api.post("/auth/login", { token: firebaseToken });
      console.log("Logged in user data:", response.data);
      dispatch(setUserData(response.data))

    } catch (error) {
      console.error("API Error:", error.response?.data?.detail || error.message);
    }
  };

  const googleLogin = async () => {
    const data = await signInWithPopup(auth, googleProvider)
    const token = await data.user.getIdToken()
    console.log(token)
    await handleLogin(token)
    console.log(data)
  }

  return (
    <div>
      <div className='h-screen min-w-0 flex bg-[#0d0f14] text-white overflow-hidden'>

        <SideBar />
        <ChatArea />
        <Artifact />

        {!userData && <div className='fixed inset-0 z-50 flex flex-col justify-center items-center'>
          <div className='w-[340px] bg-[#13151c] border border-white/10 rounded-2xl p-7 flex flex-col gap-5'>
            <div className='flex flex-col gap-1'>
              <h2 className='text-[17px] font-semibold text-slate-100 tracking-tight'>Welcome to CortexAI</h2>
              <p className='text-[13px] text-slate-500'>Please login to continue using the app.</p>
            </div>

            <button className='flex items-center justify-center w-full bg-[#1e1f25] text-white text-[14px] font-semibold py-3 rounded-2xl' onClick={googleLogin}>
              <FcGoogle className='mr-2' size={20} />
              Continue with Google
            </button>
          </div>
        </div>}

      </div>
    </div>
  )
}

export default Home