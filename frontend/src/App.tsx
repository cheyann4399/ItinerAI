import { useEffect, useState } from 'react'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { ConfigProvider, theme } from 'antd'
import { useThemeStore } from './stores/themeStore'
import { MainLayout } from './components/layout/MainLayout'
import { useProfileStore } from './stores/profileStore'
import { NicknameSetup } from './components/profile/NicknameSetup'
import './styles/globals.css'

function App() {
  const { mode } = useThemeStore()
  const { nickname } = useProfileStore()
  const [showNicknameModal, setShowNicknameModal] = useState(false)

  useEffect(() => {
    if (!nickname) {
      setShowNicknameModal(true)
    }
  }, [nickname])

  return (
    <ConfigProvider
      theme={{
        algorithm:
          mode === 'dark' ? theme.darkAlgorithm : theme.defaultAlgorithm,
      }}
    >
      <>
        <BrowserRouter>
          <Routes>
            <Route path="*" element={<MainLayout />} />
          </Routes>
        </BrowserRouter>
        <NicknameSetup
          open={showNicknameModal}
          onFinished={() => setShowNicknameModal(false)}
        />
      </>
    </ConfigProvider>
  )
}

export default App
