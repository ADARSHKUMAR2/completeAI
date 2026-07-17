import React, { useEffect } from 'react'
import Home from './pages/Home'
import getCurrentUser from './features/getCurrentUser'

function App() {
  useEffect(() => {
    const getUser = async () => {

      const user = await getCurrentUser();
      console.log(user)
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