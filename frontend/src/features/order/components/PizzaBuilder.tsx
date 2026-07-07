import { useState } from 'react'
import { Plus, Minus, ChevronDown, ChevronUp } from 'lucide-react'

import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { cn, formatCurrency } from '@/lib/utils'
import type { MenuItem } from '@/types'
import type { CartItem } from '../types'

interface PizzaBuilderProps {
  pizzas: MenuItem[]
  bases: MenuItem[]
  toppings: MenuItem[]
  onAdd: (cartItem: CartItem) => void
}

interface PizzaCardProps {
  pizza: MenuItem
  bases: MenuItem[]
  toppings: MenuItem[]
  onAdd: (cartItem: CartItem) => void
}

function PizzaCard({ pizza, bases, toppings, onAdd }: PizzaCardProps) {
  const [expanded, setExpanded] = useState(false)
  const [base, setBase] = useState<MenuItem | null>(bases[0] ?? null)
  const [selectedToppings, setSelectedToppings] = useState<MenuItem[]>([])
  const [qty, setQty] = useState(1)

  const toggleTopping = (topping: MenuItem) => {
    setSelectedToppings((prev) =>
      prev.some((t) => t.id === topping.id)
        ? prev.filter((t) => t.id !== topping.id)
        : [...prev, topping],
    )
  }

  const unitPrice =
    Number(pizza.price) +
    Number(base?.price ?? 0) +
    selectedToppings.reduce((sum, topping) => sum + Number(topping.price), 0)

  const handleAdd = () => {
    if (!base) return

    onAdd({
      menuItemId: pizza.id,
      name: pizza.name,
      category: pizza.category,
      baseSelected: base.name,
      toppingsSelected: selectedToppings.map((t) => t.name),
      quantity: qty,
      unitPrice,
    })

    setExpanded(false)
    setSelectedToppings([])
    setQty(1)
  }

  return (
    <div className="rounded-xl border bg-card p-4 shadow-sm">
      <button
        type="button"
        className="flex w-full items-center justify-between text-left"
        onClick={() => setExpanded((v) => !v)}
      >
        <div>
          <h3 className="font-semibold">{pizza.name}</h3>
          <Badge>{pizza.category}</Badge>
        </div>

        <div className="flex items-center gap-3">
          <span className="font-medium">{formatCurrency(Number(pizza.price))}</span>
          {expanded ? <ChevronUp /> : <ChevronDown />}
        </div>
      </button>

      {expanded && (
        <div className="mt-4 space-y-4">
          <div>
            <h4 className="mb-2 font-medium">Crust</h4>
            <div className="flex flex-wrap gap-2">
              {bases.map((b) => (
                <button
                  key={b.id}
                  type="button"
                  onClick={() => setBase(b)}
                  className={cn(
                    'rounded-full border px-3 py-1 text-sm transition-colors duration-100',
                    base?.id === b.id
                      ? 'border-primary bg-primary text-primary-foreground'
                      : 'border-border bg-card text-foreground hover:border-primary/50',
                  )}
                >
                  {b.name} + {formatCurrency(Number(b.price))}
                </button>
              ))}
            </div>
          </div>

          {toppings.length > 0 && (
            <div>
              <h4 className="mb-2 font-medium">Extra Toppings</h4>
              <div className="flex flex-wrap gap-2">
                {toppings.map((t) => (
                  <button
                    key={t.id}
                    type="button"
                    onClick={() => toggleTopping(t)}
                    className={cn(
                      'rounded-full border px-3 py-1 text-sm transition-colors duration-100',
                      selectedToppings.some((selected) => selected.id === t.id)
                        ? 'border-primary bg-primary text-primary-foreground'
                        : 'border-border bg-card text-foreground hover:border-primary/50',
                    )}
                  >
                    {t.name} + {formatCurrency(Number(t.price))}
                  </button>
                ))}
              </div>
            </div>
          )}

          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Button
                type="button"
                variant="outline"
                size="icon"
                onClick={() => setQty((q) => Math.max(1, q - 1))}
              >
                <Minus className="h-4 w-4" />
              </Button>

              <span>{qty}</span>

              <Button type="button" variant="outline" size="icon" onClick={() => setQty((q) => q + 1)}>
                <Plus className="h-4 w-4" />
              </Button>
            </div>

            <Button type="button" onClick={handleAdd}>
              Add to Order · {formatCurrency(unitPrice * qty)}
            </Button>
          </div>
        </div>
      )}
    </div>
  )
}

export function PizzaBuilder({ pizzas, bases, toppings, onAdd }: PizzaBuilderProps) {
  return (
    <div className="space-y-4">
      {pizzas.map((pizza) => (
        <PizzaCard
          key={pizza.id}
          pizza={pizza}
          bases={bases}
          toppings={toppings}
          onAdd={onAdd}
        />
      ))}
    </div>
  )
}
