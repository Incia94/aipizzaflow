import { useFormContext } from 'react-hook-form'
import { User, Phone } from 'lucide-react'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import type { OrderFormValues } from '../types'

export function CustomerForm() {
  const { register, formState: { errors } } = useFormContext<OrderFormValues>()

  return (
    <div className="space-y-4">
      <div className="space-y-1.5">
        <Label htmlFor="customer-name">
          <span className="flex items-center gap-1.5">
            <User className="h-3.5 w-3.5 text-muted-foreground" />
            Customer Name
          </span>
        </Label>
        <Input
          id="customer-name"
          placeholder="e.g. Rajan Sharma"
          {...register('customer.name')}
          aria-invalid={!!errors.customer?.name}
        />
        {errors.customer?.name && (
          <p className="text-xs text-destructive">{errors.customer.name.message}</p>
        )}
      </div>

      <div className="space-y-1.5">
        <Label htmlFor="customer-phone">
          <span className="flex items-center gap-1.5">
            <Phone className="h-3.5 w-3.5 text-muted-foreground" />
            Phone Number
          </span>
        </Label>
        <Input
          id="customer-phone"
          placeholder="10-digit mobile number"
          inputMode="tel"
          {...register('customer.phone_number')}
          aria-invalid={!!errors.customer?.phone_number}
        />
        {errors.customer?.phone_number && (
          <p className="text-xs text-destructive">{errors.customer.phone_number.message}</p>
        )}
      </div>
    </div>
  )
}
