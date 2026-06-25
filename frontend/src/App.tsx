import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { Toaster } from 'sonner'
import Layout from './components/Layout'
import SubmitClaim from './pages/SubmitClaim'
import AdminDashboard from './pages/AdminDashboard'
import KnowledgeBase from './pages/KnowledgeBase'

export default function App() {
  return (
    <BrowserRouter>
      <Toaster position="top-right" theme="dark" />
      <Routes>
        <Route element={<Layout />}>
          <Route path="/"      element={<SubmitClaim />} />
          <Route path="/admin" element={<AdminDashboard />} />
          <Route path="/kb"    element={<KnowledgeBase />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}
