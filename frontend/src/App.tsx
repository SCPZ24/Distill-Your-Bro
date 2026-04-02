import { BrowserRouter, Routes, Route } from 'react-router-dom'
import HomePage from './pages/HomePage'
import SoulCreatePage from './pages/SoulCreatePage'
import SessionManagePage from './pages/SessionManagePage'
import ChatPage from './pages/ChatPage'

function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen bg-gray-50">
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/souls/create" element={<SoulCreatePage />} />
          <Route path="/sessions" element={<SessionManagePage />} />
          <Route path="/sessions/:id" element={<ChatPage />} />
        </Routes>
      </div>
    </BrowserRouter>
  )
}

export default App