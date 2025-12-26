import { Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import ProjectsPage from './pages/ProjectsPage'
import ProjectDetail from './pages/ProjectDetail'
import RulesEditor from './pages/RulesEditor'
import MaterialsPage from './pages/MaterialsPage'
import OptimizationPage from './pages/OptimizationPage'

function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/projects" element={<ProjectsPage />} />
        <Route path="/projects/:id" element={<ProjectDetail />} />
        <Route path="/rules" element={<RulesEditor />} />
        <Route path="/materials" element={<MaterialsPage />} />
        <Route path="/optimization/:projectId" element={<OptimizationPage />} />
      </Routes>
    </Layout>
  )
}

export default App
