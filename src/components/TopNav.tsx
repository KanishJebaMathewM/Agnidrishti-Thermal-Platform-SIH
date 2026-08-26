import { NavLink } from 'react-router-dom'
import { Bell, ChevronDown, Eye, ListFilter, Archive, AlertTriangle, TrendingUp, Database, Cpu, Menu, X } from 'lucide-react'
import { useEffect, useState } from 'react'
import { pingApi } from '../api/client'
import { formatDistanceToNow } from './Badges'

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
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)
  const [isLive, setIsLive] = useState(false)
  const [lastSync, setLastSync] = useState<Date>(new Date())

  useEffect(() => {
    let isMounted = true
    async function check() {
      const ok = await pingApi()
      if (isMounted) {
        setIsLive(ok)
        setLastSync(new Date())
      }
    }
    check()
    const interval = setInterval(check, 30000)
    return () => {
      isMounted = false
      clearInterval(interval)
    }
  }, [])

  return (
    <header className="fixed top-0 left-0 right-0 z-50 bg-white/95 backdrop-blur-md border-b border-slate-200/80 shadow-2xs">
      <div className="max-w-[1700px] mx-auto px-4 xl:px-6">
        <div className="flex items-center justify-between h-16 gap-2">
          {/* Logo & Subtitle */}
          <div className="flex items-center gap-3 shrink-0">
            <div className="w-9 h-9 rounded-full bg-[#00695C] flex items-center justify-center shadow-xs shrink-0">
              <svg viewBox="0 0 32 32" className="w-5 h-5">
                <path fill="#E0F2F1" d="M16 3C9 5 6 10 6 16c0 8 6 13 10 13s10-5 10-13c0-6-3-11-10-13z" />
                <circle cx="16" cy="16" r="3.5" fill="#EF4444" />
              </svg>
            </div>
            <div className="shrink-0">
              <div className="font-display font-bold text-slate-900 text-lg leading-tight tracking-tight">AGNIDRISHTI</div>
              <div className="text-[11px] font-medium text-slate-500 leading-tight">Thermal Anomaly Intelligence</div>
            </div>
          </div>

          {/* Desktop Navigation Tabs (Visible on XL screens and above: >= 1280px).
              min-w-0 + overflow-x-auto let this strip shrink and internally
              scroll instead of pushing the always-visible profile/bell
              controls off the right edge of the viewport on narrower
              (xl but not 2xl, e.g. 1280-1535px) laptop widths. */}
          <nav className="hidden xl:flex items-center gap-1 2xl:gap-2 min-w-0 overflow-x-auto scrollbar-none">
            {navItems.map((item) => {
              const Icon = item.icon
              return (
                <NavLink
                  key={item.to}
                  to={item.to}
                  end={item.to === '/'}
                  className={({ isActive }) =>
                    `relative inline-flex items-center gap-1.5 2xl:gap-2 px-2 2xl:px-3 py-2 text-xs 2xl:text-sm font-semibold transition-all rounded-[14px] whitespace-nowrap shrink-0 ${
                      isActive
                        ? 'bg-[#E4F2F0] text-[#005A52]'
                        : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100/70'
                    }`
                  }
                >
                  {({ isActive }) => (
                    <>
                      <Icon className={`w-4 h-4 shrink-0 ${isActive ? 'text-[#005A52]' : 'text-slate-500'}`} />
                      <span className="whitespace-nowrap">{item.label}</span>
                      {isActive && (
                        <span className="absolute bottom-0 left-3 right-3 h-[2.5px] bg-[#00897B] rounded-full" />
                      )}
                    </>
                  )}
                </NavLink>
              )
            })}
          </nav>

          {/* Right Status & Profile Controls — never shrinks, always visible */}
          <div className="flex items-center gap-2 sm:gap-3 shrink-0">
            {/* Notification Bell */}
            <button className="relative p-2 rounded-xl text-slate-700 hover:bg-slate-100 transition-colors focus:outline-none shrink-0" aria-label="Notifications">
              <Bell className="w-5 h-5" />
              <span className="absolute top-1 right-1 w-4 h-4 rounded-full bg-rose-600 text-white text-[10px] font-bold flex items-center justify-center font-mono shadow-2xs">23</span>
            </button>

            {/* User Profile Pill */}
            <div className="relative shrink-0">
              <button
                onClick={() => {
                  setProfileOpen(!profileOpen)
                  if (mobileMenuOpen) setMobileMenuOpen(false)
                }}
                className="flex items-center gap-2 px-2.5 py-1.5 rounded-xl border border-slate-200 bg-white hover:bg-slate-50 transition-colors shadow-2xs focus:outline-none shrink-0"
              >
                <div className="w-7 h-7 rounded-lg bg-[#00695C] text-white text-xs font-bold flex items-center justify-center font-display shadow-2xs shrink-0">OC</div>
                <span className="hidden sm:block text-xs font-semibold text-slate-800 whitespace-nowrap">Ops Center — Delhi</span>
                <ChevronDown className="w-3.5 h-3.5 text-slate-400 shrink-0" />
              </button>

              {profileOpen && (
                <div className="absolute right-0 mt-2 w-56 card shadow-lg py-2 z-50 bg-white rounded-xl border border-slate-200">
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

            {/* Mobile / Tablet Hamburger Toggle Button (Visible below XL breakpoint: < 1280px) */}
            <button
              onClick={() => {
                setMobileMenuOpen(!mobileMenuOpen)
                if (profileOpen) setProfileOpen(false)
              }}
              className="xl:hidden p-2 rounded-xl text-slate-700 hover:bg-slate-100 transition-colors focus:outline-none shrink-0"
              aria-label="Toggle Navigation Menu"
            >
              {mobileMenuOpen ? <X className="w-6 h-6 text-slate-800" /> : <Menu className="w-6 h-6 text-slate-800" />}
            </button>
          </div>
        </div>

        {/* Mobile & Tablet Navigation Drawer */}
        {mobileMenuOpen && (
          <div className="xl:hidden border-t border-slate-200/80 bg-white/95 backdrop-blur-md py-3 px-2 shadow-lg rounded-b-2xl">
            <nav className="flex flex-col gap-1">
              {navItems.map((item) => {
                const Icon = item.icon
                return (
                  <NavLink
                    key={item.to}
                    to={item.to}
                    end={item.to === '/'}
                    onClick={() => setMobileMenuOpen(false)}
                    className={({ isActive }) =>
                      `flex items-center gap-3 px-4 py-2.5 text-sm font-semibold transition-all rounded-xl ${
                        isActive
                          ? 'bg-[#E4F2F0] text-[#005A52]'
                          : 'text-slate-700 hover:text-slate-900 hover:bg-slate-100/80'
                      }`
                    }
                  >
                    {({ isActive }) => (
                      <>
                        <Icon className={`w-5 h-5 shrink-0 ${isActive ? 'text-[#005A52]' : 'text-slate-500'}`} />
                        <span>{item.label}</span>
                      </>
                    )}
                  </NavLink>
                )
              })}
            </nav>
            {/* Live Sync Status indicator inside Mobile/Tablet Drawer */}
            <div className="mt-3 pt-3 border-t border-slate-100 px-4 flex items-center justify-between text-xs">
              <div className="flex items-center gap-2">
                <span className="relative flex w-2 h-2">
                  {isLive && <span className="absolute inset-0 rounded-full bg-emerald-500 animate-ping opacity-75" />}
                  <span className={`relative w-2 h-2 rounded-full ${isLive ? 'bg-emerald-600' : 'bg-slate-400'}`} />
                </span>
                <span className="text-slate-600 font-medium font-mono text-xs">
                  {isLive ? 'Live System Sync Active' : 'Offline / Demo Mode'}
                </span>
              </div>
              <span className="text-[11px] text-slate-400 font-mono">{formatDistanceToNow(lastSync)}</span>
            </div>
          </div>
        )}
      </div>
    </header>
  )
}


