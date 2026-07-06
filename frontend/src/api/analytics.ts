import client from './client'
import type { AnalyticsFilters, AnalyticsResponse } from '@/types'

export async function fetchAnalytics(filters?: AnalyticsFilters): Promise<AnalyticsResponse> {
  const { data } = await client.get<AnalyticsResponse>('/analytics', { params: filters })
  return data
}
