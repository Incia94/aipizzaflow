import client from './client'
import type { AIQueryRequest, AIQueryResponse } from '@/types'

export async function queryAdvisor(request: AIQueryRequest): Promise<AIQueryResponse> {
  const { data } = await client.post<AIQueryResponse>('/ai/query', request)
  return data
}
