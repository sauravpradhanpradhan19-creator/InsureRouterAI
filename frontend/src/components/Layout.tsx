import { NavLink, Outlet } from 'react-router-dom'
import { clsx } from 'clsx'
import { FileText, LayoutDashboard, Database, Shield } from 'lucide-react'

const links = [
  { to: '/',          label: 'Submit Claim',  icon: FileText },
  { to: '/admin',     label: 'Dashboard',     icon: LayoutDashboard },
  { to: '/kb',        label: 'Knowledge Base', icon: Database },
]

export default function Layout() {
  return (
    <div className="min-h-screen bg-bg-primary">
      {/* Top nav */}
      <nav className="border-b border-border bg-bg-secondary sticky top-0 z-50">
        <div className="max-w-6xl mx-auto px-4 h-14 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Shield className="w-5 h-5 text-accent-primary" />
            <span className="font-semibold text-text-primary">InsurRoute AI</span>
          </div>
          <div className="flex items-center gap-1">
            {links.map(({ to, label, icon: Icon }) => (
              <NavLink
                key={to}
                to={to}
                end={to === '/'}
                className={({ isActive }) => clsx(
                  'flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm transition-colors',
                  isActive
                    ? 'bg-accent-primary/20 text-accent-primary'
                    : 'text-text-secondary hover:text-text-primary hover:bg-bg-tertiary'
                )}
              >
                <Icon className="w-4 h-4" />
                {label}
              </NavLink>
            ))}
          </div>
        </div>
      </nav>

      {/* Page content */}
      <main>
        <Outlet />
      </main>
    </div>
  )
}
