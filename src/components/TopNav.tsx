import { NavLink } from 'react-router-dom'
import { Bell, ChevronDown, Eye, ListFilter, Archive, AlertTriangle, TrendingUp, Database, Cpu } from 'lucide-react'
import { useState } from 'react'

const navItems = [
  { to: '/', label: 'Overview', icon: Eye },
  { to: '/events', label: 'Events', icon: ListFilter },
  { to: '/registry', label: 'Registry', icon: Archive },
  { to: '/alerts', label: 'Alerts & Routing', icon: AlertTriangle },
  { to: '/trends', label: 'Trends', icon: TrendingUp },
  { to: '/data-sources', label: 'Data Sources', icon: Database },
  { to: '/model-insights', label: 'Model Insights', icon: Cpu },
]

export default function TopNav() {
  const [profileOpen, setProfileOpen] = useState(false)

  return (
    <header className="fixed top-0 left-0 right-0 z-50 bg-white/95 backdrop-blur-md border-b border-slate-200/80 shadow-2xs">
      <div className="max-w-[1700px] mx-auto px-4 lg:px-6">
        <div className="flex items-center justify-between h-16">
          {/* Logo & Subtitle */}
          <div className="flex items-center gap-3 shrink-0">
            <div className="w-9 h-9 rounded-full bg-[#00695C] flex items-center justify-center shadow-xs shrink-0">
              <svg viewBox="0 0 32 32" className="w-5 h-5">
                <path fill="#E0F2F1" d="M16 3C9 5 6 10 6 16c0 8 6 13 10 13s10-5 10-13c0-6-3-11-10-13z" />
                <circle cx="16" cy="16" r="3.5" fill="#EF4444" />
              </svg>
            </div>
            <div>
              <div className="font-display font-bold text-slate-900 text-lg leading-tight tracking-tight">AGNIDRISHTI</div>
              <div className="text-[11px] font-medium text-slate-500 leading-tight">Thermal Anomaly Intelligence</div>
            </div>
          </div>

          {/* Center Navigation Tabs */}
          <nav className="hidden lg:flex items-center gap-1 xl:gap-2">
            {navItems.map((item) => {
              const Icon = item.icon
              return (
                <NavLink
                  key={item.to}
                  to={item.to}
                  end={item.to === '/'}
                  className={({ isActive }) =>
                    `relative inline-flex items-center gap-2 px-3 py-2 text-xs xl:text-sm font-semibold transition-all rounded-[14px] ${
                      isActive
                        ? 'bg-[#E4F2F0] text-[#005A52]'
                        : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100/70'
                    }`
                  }
                >
                  {({ isActive }) => (
                    <>
                      <Icon className={`w-4 h-4 shrink-0 ${isActive ? 'text-[#005A52]' : 'text-slate-500'}`} />
                      <span>{item.label}</span>
                      {isActive && (
                        <span className="absolute bottom-0 left-3 right-3 h-[2.5px] bg-[#00897B] rounded-full" />
                      )}
                    </>
                  )}
                </NavLink>
              )
            })}
          </nav>

          {/* Right Status & Profile Controls */}
          <div className="flex items-center gap-3 shrink-0">
            {/* Live Sync Status */}
            <div className="hidden md:flex items-center gap-2 text-xs bg-slate-50 border border-slate-200/90 px-3 py-1.5 rounded-full">
              <span className="relative flex w-2 h-2">
                <span className="absolute inset-0 rounded-full bg-emerald-500 animate-ping opacity-75" />
                <span className="relative w-2 h-2 rounded-full bg-emerald-600" />
              </span>
              <span className="text-slate-600 font-medium font-mono text-[11px]">
                Live <span className="text-slate-300">·</span> Last sync 2m ago
              </span>
            </div>

            {/* Notification Bell */}
            <button className="relative p-2 rounded-xl text-slate-700 hover:bg-slate-100 transition-colors focus:outline-none" aria-label="Notifications">
              <Bell className="w-5 h-5" />
              <span className="absolute top-1 right-1 w-4 h-4 rounded-full bg-rose-600 text-white text-[10px] font-bold flex items-center justify-center font-mono shadow-2xs">23</span>
            </button>

            {/* User Profile Pill */}
            <div className="relative">
              <button
                onClick={() => setProfileOpen(!profileOpen)}
                className="flex items-center gap-2 px-2.5 py-1.5 rounded-xl border border-slate-200 bg-white hover:bg-slate-50 transition-colors shadow-2xs focus:outline-none"
              >
                <div className="w-7 h-7 rounded-lg bg-[#00695C] text-white text-xs font-bold flex items-center justify-center font-display shadow-2xs">OC</div>
                <span className="hidden md:block text-xs font-semibold text-slate-800">Ops Center — Delhi</span>
                <ChevronDown className="w-3.5 h-3.5 text-slate-400" />
              </button>

              {profileOpen && (
                <div className="absolute right-0 mt-2 w-56 card shadow-lg py-2 z-50">
                  <div className="px-4 py-2 border-b border-slate-100">
                    <div className="text-xs font-bold text-slate-900">Ops Center — Delhi</div>
                    <div className="text-[11px] text-slate-500">NTRO · Tier-1 Access</div>
                  </div>
                  <button className="w-full text-left px-4 py-2 text-xs font-medium text-slate-700 hover:bg-slate-50">Profile Settings</button>
                  <button className="w-full text-left px-4 py-2 text-xs font-medium text-slate-700 hover:bg-slate-50">Notification Preferences</button>
                  <button className="w-full text-left px-4 py-2 text-xs font-medium text-slate-700 hover:bg-slate-50">Data Export</button>
                  <div className="border-t border-slate-100 mt-1 pt-1">
                    <button className="w-full text-left px-4 py-2 text-xs font-medium text-rose-600 hover:bg-rose-50">Sign Out</button>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </header>
  )
}
