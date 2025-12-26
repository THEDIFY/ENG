import { ReactNode } from 'react'
import { Link, useLocation } from 'react-router-dom'

interface LayoutProps {
  children: ReactNode
}

const navigation = [
  { name: 'Dashboard', href: '/' },
  { name: 'Projects', href: '/projects' },
  { name: 'Rules', href: '/rules' },
  { name: 'Materials', href: '/materials' },
]

export default function Layout({ children }: LayoutProps) {
  const location = useLocation()

  return (
    <div className="flex h-screen bg-gray-100">
      {/* Sidebar */}
      <div className="w-64 bg-secondary-800 text-white">
        <div className="p-4">
          <h1 className="text-xl font-bold">Trophy Truck</h1>
          <p className="text-sm text-secondary-400">Topology Optimizer</p>
        </div>
        <nav className="mt-8">
          {navigation.map((item) => {
            const isActive = location.pathname === item.href
            return (
              <Link
                key={item.name}
                to={item.href}
                className={`block px-4 py-2 text-sm ${
                  isActive
                    ? 'bg-primary-600 text-white'
                    : 'text-secondary-300 hover:bg-secondary-700'
                }`}
              >
                {item.name}
              </Link>
            )
          })}
        </nav>
        
        <div className="absolute bottom-0 left-0 w-64 p-4 text-xs text-secondary-400">
          <p>Baja 1000 Chassis Design</p>
          <p>Version 0.1.0</p>
        </div>
      </div>

      {/* Main content */}
      <div className="flex-1 overflow-auto">
        {children}
      </div>
    </div>
  )
}
