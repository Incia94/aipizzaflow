import { Outlet } from 'react-router-dom'
import { AdminNavigation } from './AdminNavigation'

export function AdminLayout() {
  return (
    <div className="min-h-screen bg-background">
      <AdminNavigation />
      <main className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8 animate-fade-in">
        <Outlet />
      </main>
    </div>
  )
}
