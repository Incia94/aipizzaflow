import { useQuery } from '@tanstack/react-query'
import {
  AreaChart, Area, BarChart, Bar, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend,
} from 'recharts'
import { TrendingUp, TrendingDown, ShoppingBag, Users, DollarSign, ArrowUpRight } from 'lucide-react'
import { fetchAnalytics } from '@/api/analytics'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { Badge } from '@/components/ui/badge'
import { formatCurrency, cn } from '@/lib/utils'

const CHART_RED = 'hsl(0, 72%, 34%)'
const CHART_MUTED = 'hsl(30, 15%, 78%)'
const PIE_COLORS = [
  'hsl(0, 72%, 34%)',
  'hsl(0, 55%, 50%)',
  'hsl(0, 40%, 65%)',
  'hsl(30, 50%, 55%)',
]

// ── KPI Card ─────────────────────────────────────────────────────────────────

interface KPICardProps {
  title: string
  value: string
  subtitle?: string
  change?: number
  icon: React.ElementType
}

function KPICard({ title, value, subtitle, change, icon: Icon }: KPICardProps) {
  const isPositive = (change ?? 0) >= 0
  return (
    <Card className="hover:shadow-card-hover transition-shadow duration-200">
      <CardContent className="p-5">
        <div className="flex items-start justify-between">
          <div className="flex-1 min-w-0">
            <p className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">
              {title}
            </p>
            <p className="kpi-number mt-1.5 text-foreground">{value}</p>
            {subtitle && (
              <p className="mt-1 text-xs text-muted-foreground">{subtitle}</p>
            )}
            {change !== undefined && (
              <div
                className={cn(
                  'mt-2 inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-xs font-medium',
                  isPositive ? 'bg-success/10 text-success' : 'bg-destructive/10 text-destructive',
                )}
              >
                {isPositive ? (
                  <TrendingUp className="h-3 w-3" />
                ) : (
                  <TrendingDown className="h-3 w-3" />
                )}
                {isPositive ? '+' : ''}{change.toFixed(1)}% WoW
              </div>
            )}
          </div>
          <div className="ml-3 flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-accent">
            <Icon className="h-5 w-5 text-primary" />
          </div>
        </div>
      </CardContent>
    </Card>
  )
}

// ── Skeletons ──────────────────────────────────────────────────────────────────

function DashboardSkeleton() {
  return (
    <div className="space-y-6">
      <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
        {[1, 2, 3, 4].map((i) => <Skeleton key={i} className="h-28 rounded-xl" />)}
      </div>
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <Skeleton className="lg:col-span-2 h-64 rounded-xl" />
        <Skeleton className="h-64 rounded-xl" />
      </div>
    </div>
  )
}

// ── Main ───────────────────────────────────────────────────────────────────────

export function AnalyticsPage() {
  const { data, isLoading, error } = useQuery({
    queryKey: ['analytics'],
    queryFn: () => fetchAnalytics(),
    refetchInterval: 30_000,
  })

  if (isLoading) return (
    <div className="space-y-6">
      <div>
        <h1 className="font-display text-2xl font-semibold">Analytics</h1>
        <p className="mt-1 text-sm text-muted-foreground">Business intelligence dashboard</p>
      </div>
      <DashboardSkeleton />
    </div>
  )

  if (error || !data) return (
    <div className="flex flex-col items-center gap-4 pt-20 text-center">
      <p className="text-muted-foreground">Failed to load analytics. Please refresh.</p>
    </div>
  )

  const { intelligence: bi } = data

  // Payment pie data
  const paymentPieData = Object.entries(bi.payments.revenue_by_payment_method).map(
    ([method, amount]) => ({ name: method.charAt(0).toUpperCase() + method.slice(1), value: amount }),
  )

  // Top selling items bar data
  const topItemsData = Object.entries(bi.products.top_selling_items)
    .slice(0, 5)
    .map(([id, qty]) => ({ name: `Pizza #${id}`, sold: qty }))

  // Growth trend data (synthetic from growth metrics for visual)
  const growthData = [
    { period: 'Prev Month', revenue: bi.revenue.total_revenue / (1 + bi.growth.month_over_month_revenue_change / 100) },
    { period: 'Prev Week', revenue: bi.revenue.total_revenue / (1 + bi.growth.week_over_week_revenue_change / 100) },
    { period: 'Current', revenue: bi.revenue.total_revenue },
  ]

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <h1 className="font-display text-2xl font-semibold">Analytics</h1>
          <p className="mt-1 text-sm text-muted-foreground">
            Business intelligence dashboard — auto-refreshes every 30s
          </p>
        </div>
        <Badge variant="secondary" className="gap-1">
          <ArrowUpRight className="h-3 w-3" />
          Live
        </Badge>
      </div>

      {/* KPI row */}
      <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
        <KPICard
          title="Total Revenue"
          value={formatCurrency(bi.revenue.total_revenue)}
          subtitle={`GST: ${formatCurrency(bi.revenue.total_gst_collected)}`}
          change={bi.growth.week_over_week_revenue_change}
          icon={DollarSign}
        />
        <KPICard
          title="Total Orders"
          value={String(bi.sales.total_orders)}
          subtitle={`Avg ${bi.sales.average_items_per_order} items/order`}
          icon={ShoppingBag}
        />
        <KPICard
          title="Avg Order Value"
          value={formatCurrency(bi.revenue.average_order_value)}
          icon={TrendingUp}
        />
        <KPICard
          title="Customers"
          value={String(bi.customers.total_customers)}
          subtitle={`${bi.customers.new_customers} new · ${bi.customers.returning_customers} returning`}
          icon={Users}
        />
      </div>

      {/* Charts row */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        {/* Revenue trend */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle>Revenue Trend</CardTitle>
            <CardDescription>Period-over-period comparison</CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={220}>
              <AreaChart data={growthData}>
                <defs>
                  <linearGradient id="revenueGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor={CHART_RED} stopOpacity={0.15} />
                    <stop offset="95%" stopColor={CHART_RED} stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="hsl(30,15%,92%)" />
                <XAxis dataKey="period" tick={{ fontSize: 12, fill: 'hsl(0,0%,42%)' }} axisLine={false} tickLine={false} />
                <YAxis tick={{ fontSize: 12, fill: 'hsl(0,0%,42%)' }} axisLine={false} tickLine={false} tickFormatter={(v) => `₹${(v/1000).toFixed(0)}k`} />
                <Tooltip
                  formatter={(v: number) => [formatCurrency(v), 'Revenue']}
                  contentStyle={{ borderRadius: 8, border: '1px solid hsl(30,15%,88%)', fontSize: 12 }}
                />
                <Area type="monotone" dataKey="revenue" stroke={CHART_RED} strokeWidth={2} fill="url(#revenueGradient)" />
              </AreaChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Payment distribution */}
        <Card>
          <CardHeader>
            <CardTitle>Payment Methods</CardTitle>
            <CardDescription>Revenue by payment type</CardDescription>
          </CardHeader>
          <CardContent className="flex flex-col items-center">
            {paymentPieData.length > 0 ? (
              <ResponsiveContainer width="100%" height={180}>
                <PieChart>
                  <Pie
                    data={paymentPieData}
                    cx="50%"
                    cy="50%"
                    innerRadius={50}
                    outerRadius={80}
                    paddingAngle={3}
                    dataKey="value"
                  >
                    {paymentPieData.map((_, index) => (
                      <Cell key={index} fill={PIE_COLORS[index % PIE_COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip formatter={(v: number) => [formatCurrency(v), 'Revenue']} contentStyle={{ borderRadius: 8, border: '1px solid hsl(30,15%,88%)', fontSize: 12 }} />
                  <Legend iconType="circle" iconSize={8} wrapperStyle={{ fontSize: 12 }} />
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <p className="py-10 text-sm text-muted-foreground">No payment data yet</p>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Top selling items */}
      {topItemsData.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Top Selling Items</CardTitle>
            <CardDescription>
              Units sold · Most popular base: <span className="font-medium text-foreground">{bi.products.most_popular_base || '—'}</span>
            </CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={180}>
              <BarChart data={topItemsData} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="hsl(30,15%,92%)" />
                <XAxis type="number" tick={{ fontSize: 12, fill: 'hsl(0,0%,42%)' }} axisLine={false} tickLine={false} />
                <YAxis type="category" dataKey="name" tick={{ fontSize: 12, fill: 'hsl(0,0%,42%)' }} axisLine={false} tickLine={false} width={70} />
                <Tooltip contentStyle={{ borderRadius: 8, border: '1px solid hsl(30,15%,88%)', fontSize: 12 }} />
                <Bar dataKey="sold" fill={CHART_RED} radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
