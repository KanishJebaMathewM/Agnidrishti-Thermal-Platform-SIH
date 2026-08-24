import { Routes, Route } from 'react-router-dom'
import TopNav from './components/TopNav'
import Overview from './pages/Overview'
import Events from './pages/Events'
import Registry from './pages/Registry'
import Alerts from './pages/Alerts'
import Trends from './pages/Trends'
import DataSources from './pages/DataSources'
import ModelInsights from './pages/ModelInsights'

export default function App() {
  return (
    <div className="min-h-screen bg-paper">
      <TopNav />
      <main className="pt-16 max-w-[1600px] mx-auto px-4 lg:px-6 py-6">
        <Routes>
          <Route path="/" element={<Overview />} />
          <Route path="/events" element={<Events />} />
          <Route path="/registry" element={<Registry />} />
          <Route path="/alerts" element={<Alerts />} />
          <Route path="/trends" element={<Trends />} />
          <Route path="/data-sources" element={<DataSources />} />
          <Route path="/model-insights" element={<ModelInsights />} />
        </Routes>
      </main>
    </div>
  )
}
