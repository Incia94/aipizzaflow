import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { AuthProvider } from './contexts/AuthContext'
import { AdminRoute } from './components/AdminRoute'
import { Layout } from './components/Layout'
import { AdminLayout } from './components/AdminLayout'
import { OrderPage } from './features/order'
import { CheckoutPage } from './features/checkout'
import { AnalyticsPage } from './features/analytics'
import { AIAdvisorPage } from './features/ai'
import { LoginPage } from './features/admin/Login'

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60,
      retry: 1,
    },
  },
})

export function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <AuthProvider>
          <Routes>
            {/* Customer Portal — public */}
            <Route path="/" element={<Layout />}>
              <Route index element={<Navigate to="/order" replace />} />
              <Route path="order" element={<OrderPage />} />
              <Route path="checkout/:orderId" element={<CheckoutPage />} />
              <Route path="checkout" element={<CheckoutPage />} />
            </Route>

            {/* Admin Login — public */}
            <Route path="/admin/login" element={<LoginPage />} />

            {/* Admin Portal — JWT protected */}
            <Route path="/admin" element={<AdminRoute />}>
              <Route element={<AdminLayout />}>
                <Route index element={<Navigate to="/admin/analytics" replace />} />
                <Route path="analytics" element={<AnalyticsPage />} />
                <Route path="ai" element={<AIAdvisorPage />} />
              </Route>
            </Route>
          </Routes>
        </AuthProvider>
      </BrowserRouter>
    </QueryClientProvider>
  )
}
