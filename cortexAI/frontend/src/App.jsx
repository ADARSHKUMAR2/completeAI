import React, { useEffect } from 'react'
import Home from './pages/Home'
import getCurrentUser from './features/getCurrentUser'
import { useDispatch } from 'react-redux'
import { setUserData } from './redux/userSlice'

function App() {

  const dispatch = useDispatch()

  useEffect(() => {
    const getUser = async () => {

      const data = await getCurrentUser();
      console.log(data)
      dispatch(setUserData(data))
    }
    getUser();
  }, [])

  return (
    <>
      <Home/>
    </>
  )
}

export default App