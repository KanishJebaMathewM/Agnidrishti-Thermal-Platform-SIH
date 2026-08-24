import { NavLink } from 'react-router-dom'
import { Bell, ChevronDown, Radio } from 'lucide-react'
import { useState } from 'react'

const navItems = [
  { to: '/', label: 'Overview' },
  { to: '/events', label: 'Events' },
  { to: '/registry', label: 'Registry' },
  { to: '/alerts', label: 'Alerts & Routing' },
  { to: '/trends', label: 'Trends' },
  { to: '/data-sources', label: 'Data Sources' },
  { to: '/model-insights', label: 'Model Insights' },
]

export default function TopNav() {
  const [menuOpen, setMenuOpen] = useState(false)
  const [profileOpen, setProfileOpen] = useState(false)

  return (
    <header className="fixed top-0 left-0 right-0 z-50 bg-paper/95 backdrop-blur-sm border-b border-border">
      <div className="max-w-[1600px] mx-auto px-4 lg:px-6">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <div className="flex items-center gap-3 shrink-0">
            <div className="w-9 h-9 rounded-md bg-teal-mid flex items-center justify-center">
              <svg viewBox="0 0 32 32" className="w-6 h-6">
                <path fill="#DCEEEC" d="M16 3C9 5 6 10 6 16c0 8 6 13 10 13s10-5 10-13c0-6-3-11-10-13z" />
                <circle cx="16" cy="16" r="3" fill="#F7DCD1" />
              </svg>
            </div>
            <div className="hidden sm:block">
              <div className="font-display font-semibold text-ink text-lg leading-none tracking-tight">AGNIDRISHTI</div>
              <div className="text-[11px] text-muted leading-tight mt-0.5">Thermal Anomaly Intelligence</div>
            </div>
          </div>

          {/* Desktop nav */}
          <nav className="hidden lg:flex items-center gap-1">
            {navItems.map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                end={item.to === '/'}
                className={({ isActive }) =>
                  `nav-link ${isActive ? 'nav-link-active' : ''}`
                }
              >
                {({ isActive }) => (
                  <>
                    {item.label}
                    {isActive && (
                      <span className="absolute bottom-0 left-3 right-3 h-0.5 bg-teal-mid rounded-full" />
                    )}
                  </>
                )}
              </NavLink>
            ))}
          </nav>

          {/* Right side */}
          <div className="flex items-center gap-3 lg:gap-4 shrink-0">
            <div className="hidden md:flex items-center gap-2 text-xs">
              <span className="relative flex w-2 h-2">
                <span className="absolute inset-0 rounded-full bg-moss-mid animate-ping opacity-75" />
                <span className="relative w-2 h-2 rounded-full bg-moss-mid" />
              </span>
              <span className="text-muted font-mono">Live · last sync 2m ago</span>
            </div>

            <button className="relative p-2 rounded-md hover:bg-panel transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-teal-mid" aria-label="Notifications">
              <Bell className="w-5 h-5 text-ink" />
              <span className="absolute top-1 right-1 w-4 h-4 rounded-full bg-ember-mid text-white text-[10px] font-semibold flex items-center justify-center font-mono">23</span>
            </button>

            <div className="relative">
              <button
                onClick={() => setProfileOpen(!profileOpen)}
                className="flex items-center gap-2 px-2 py-1.5 rounded-md hover:bg-panel transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-teal-mid"
              >
                <div className="w-7 h-7 rounded-md bg-teal-deep text-white text-xs font-semibold flex items-center justify-center font-display">OC</div>
                <span className="hidden md:block text-sm text-ink font-medium">Ops Center — Delhi</span>
                <ChevronDown className="w-4 h-4 text-muted" />
              </button>
              {profileOpen && (
                <div className="absolute right-0 mt-2 w-56 card shadow-lg py-2 z-50">
                  <div className="px-4 py-2 border-b border-border">
                    <div className="text-sm font-medium text-ink">Ops Center — Delhi</div>
                    <div className="text-xs text-muted">NTRO · Tier-1 Access</div>
                  </div>
                  <button className="w-full text-left px-4 py-2 text-sm text-ink hover:bg-panel">Profile Settings</button>
                  <button className="w-full text-left px-4 py-2 text-sm text-ink hover:bg-panel">Notification Preferences</button>
                  <button className="w-full text-left px-4 py-2 text-sm text-ink hover:bg-panel">Data Export</button>
                  <div className="border-t border-border mt-1 pt-1">
                    <button className="w-full text-left px-4 py-2 text-sm text-ember-deep hover:bg-panel">Sign Out</button>
                  </div>
                </div>
              )}
            </div>

            {/* Mobile menu toggle */}
            <button
              onClick={() => setMenuOpen(!menuOpen)}
              className="lg:hidden p-2 rounded-md hover:bg-panel transition-colors"
              aria-label="Menu"
            >
              <svg className="w-6 h-6 text-ink" fill="none" stroke="currentColor" strokeWidth={2} viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" d={menuOpen ? 'M6 18L18 6M6 6l12 12' : 'M4 6h16M4 12h16M4 18h16'} />
              </svg>
            </button>
          </div>
        </div>

        {/* Mobile nav */}
        {menuOpen && (
          <nav className="lg:hidden pb-4 flex flex-col gap-1">
            {navItems.map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                end={item.to === '/'}
                onClick={() => setMenuOpen(false)}
                className={({ isActive }) =>
                  `nav-link ${isActive ? 'bg-teal-light text-ink' : ''}`
                }
              >
                {item.label}
              </NavLink>
            ))}
            <div className="flex items-center gap-2 px-3 py-2 text-xs text-muted">
              <Radio className="w-3 h-3" />
              <span className="font-mono">Live · last sync 2m ago</span>
            </div>
          </nav>
        )}
      </div>
    </header>
  )
}
