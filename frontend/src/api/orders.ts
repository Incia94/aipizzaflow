import client from './client'
import type { PendingOrderResponse, SubmitOrderRequest } from '@/types'

export async function submitOrder(request: SubmitOrderRequest): Promise<PendingOrderResponse> {
  const { data } = await client.post<PendingOrderResponse>('/orders', request)
  return data
}
