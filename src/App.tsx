import { Routes, Route } from 'react-router-dom'
import TopNav from './components/TopNav'
import ErrorBoundary from './components/shared/ErrorBoundary'
import Overview from './pages/Overview'
import Events from './pages/Events'
import Registry from './pages/Registry'
import Alerts from './pages/Alerts'
import Trends from './pages/Trends'
import DataSources from './pages/DataSources'
import ModelInsights from './pages/ModelInsights'

function page(element: JSX.Element) {
  return <ErrorBoundary>{element}</ErrorBoundary>
}

export default function App() {
  return (
    <div className="min-h-screen bg-paper">
      <TopNav />
      <main className="pt-16 max-w-[1600px] mx-auto px-4 lg:px-6 py-6">
        <Routes>
          <Route path="/" element={page(<Overview />)} />
          <Route path="/events" element={page(<Events />)} />
          <Route path="/registry" element={page(<Registry />)} />
          <Route path="/alerts" element={page(<Alerts />)} />
          <Route path="/trends" element={page(<Trends />)} />
          <Route path="/data-sources" element={page(<DataSources />)} />
          <Route path="/model-insights" element={page(<ModelInsights />)} />
        </Routes>
      </main>
    </div>
  )
}
