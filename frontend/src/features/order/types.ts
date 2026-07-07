import { z } from 'zod'

export const orderFormSchema = z.object({
  customer: z.object({
    name: z.string().trim().min(2, 'Enter a valid name'),
    phone_number: z
      .string()
      .trim()
      .regex(/^[6-9]\d{9}$/, 'Enter a valid 10-digit Indian phone number'),
  }),
})

export type OrderFormValues = z.infer<typeof orderFormSchema>

export interface CartItem {
  menuItemId: string
  name: string
  category: string
  baseSelected: string
  toppingsSelected: string[]
  quantity: number
  unitPrice: number
}
