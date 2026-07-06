import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { Bot, Sparkles, AlertCircle, ChevronDown, ChevronUp } from 'lucide-react'
import { queryAdvisor } from '@/api/ai'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Textarea } from '@/components/ui/textarea'
import { Label } from '@/components/ui/label'
import { Separator } from '@/components/ui/separator'
import { Skeleton } from '@/components/ui/skeleton'
import { formatCurrency } from '@/lib/utils'
import type { AIQueryResponse } from '@/types'

const schema = z.object({
  question: z.string().min(1, 'Please enter a question'),
})

type FormValues = z.infer<typeof schema>

const EXAMPLE_QUESTIONS = [
  'Which payment method generates the most revenue?',
  'Are my returning customers increasing?',
  'What is my busiest sales period?',
  'How is my revenue trending this month?',
]

function IntelligenceSnapshot({ data }: { data: AIQueryResponse['intelligence_snapshot'] }) {
  const [open, setOpen] = useState(false)

  return (
    <div className="rounded-lg border border-border">
      <button
        type="button"
        className="flex w-full items-center justify-between px-4 py-3 text-left text-sm font-medium text-muted-foreground hover:text-foreground transition-colors"
        onClick={() => setOpen((v) => !v)}
      >
        <span>View Business Intelligence Snapshot</span>
        {open ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
      </button>

      {open && (
        <div className="border-t border-border px-4 pb-4 pt-3 animate-fade-in">
          <div className="grid grid-cols-2 gap-x-8 gap-y-2 text-sm sm:grid-cols-3">
            <div>
              <p className="text-xs font-semibold uppercase tracking-wide text-muted-foreground mb-1">Revenue</p>
              <p className="font-mono-numbers">{formatCurrency(data.revenue.total_revenue)}</p>
              <p className="text-xs text-muted-foreground">Avg order: {formatCurrency(data.revenue.average_order_value)}</p>
            </div>
            <div>
              <p className="text-xs font-semibold uppercase tracking-wide text-muted-foreground mb-1">Sales</p>
              <p className="font-mono-numbers">{data.sales.total_orders} orders</p>
              <p className="text-xs text-muted-foreground">{data.sales.total_items_sold} items sold</p>
            </div>
            <div>
              <p className="text-xs font-semibold uppercase tracking-wide text-muted-foreground mb-1">Customers</p>
              <p className="font-mono-numbers">{data.customers.total_customers}</p>
              <p className="text-xs text-muted-foreground">{data.customers.new_customers} new</p>
            </div>
            <div>
              <p className="text-xs font-semibold uppercase tracking-wide text-muted-foreground mb-1">Popular Base</p>
              <p className="text-sm font-medium">{data.products.most_popular_base || '—'}</p>
            </div>
            <div>
              <p className="text-xs font-semibold uppercase tracking-wide text-muted-foreground mb-1">WoW Growth</p>
              <p className={`font-mono-numbers text-sm font-medium ${data.growth.week_over_week_revenue_change >= 0 ? 'text-success' : 'text-destructive'}`}>
                {data.growth.week_over_week_revenue_change >= 0 ? '+' : ''}{data.growth.week_over_week_revenue_change.toFixed(1)}%
              </p>
            </div>
            <div>
              <p className="text-xs font-semibold uppercase tracking-wide text-muted-foreground mb-1">MoM Growth</p>
              <p className={`font-mono-numbers text-sm font-medium ${data.growth.month_over_month_revenue_change >= 0 ? 'text-success' : 'text-destructive'}`}>
                {data.growth.month_over_month_revenue_change >= 0 ? '+' : ''}{data.growth.month_over_month_revenue_change.toFixed(1)}%
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export function AIAdvisorPage() {
  const [result, setResult] = useState<AIQueryResponse | null>(null)

  const { register, handleSubmit, setValue, formState: { errors } } = useForm<FormValues>({
    resolver: zodResolver(schema),
  })

  const { mutate: ask, isPending, error } = useMutation({
    mutationFn: queryAdvisor,
    onSuccess: (data) => setResult(data),
  })

  const onSubmit = (values: FormValues) => {
    ask({ question: values.question })
  }

  return (
    <div className="mx-auto max-w-2xl space-y-6">
      {/* Header */}
      <div className="flex items-start gap-4">
        <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl bg-accent">
          <Bot className="h-6 w-6 text-primary" />
        </div>
        <div>
          <h1 className="font-display text-2xl font-semibold">AI Restaurant Advisor</h1>
          <p className="mt-1 text-sm text-muted-foreground">
            Ask any business question. Answers are grounded in your actual business intelligence data.
          </p>
        </div>
      </div>

      {/* Question form */}
      <Card>
        <CardContent className="pt-5 space-y-4">
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            <div className="space-y-1.5">
              <Label htmlFor="question">Ask a business question</Label>
              <Textarea
                id="question"
                placeholder="e.g. Which pizza generates the most revenue? Should I add more payment options?"
                className="min-h-[100px]"
                {...register('question')}
              />
              {errors.question && (
                <p className="text-xs text-destructive">{errors.question.message}</p>
              )}
            </div>

            <Button type="submit" className="w-full" size="lg" disabled={isPending}>
              {isPending ? (
                <>
                  <Sparkles className="h-4 w-4 animate-pulse" />
                  Analysing your data…
                </>
              ) : (
                <>
                  <Sparkles className="h-4 w-4" />
                  Ask Advisor
                </>
              )}
            </Button>
          </form>

          {/* Example questions */}
          <div>
            <p className="mb-2 text-xs font-medium text-muted-foreground">Try asking:</p>
            <div className="flex flex-wrap gap-2">
              {EXAMPLE_QUESTIONS.map((q) => (
                <button
                  key={q}
                  type="button"
                  onClick={() => setValue('question', q)}
                  className="rounded-full border border-border bg-muted/40 px-3 py-1 text-xs text-foreground hover:border-primary/40 hover:bg-accent transition-colors"
                >
                  {q}
                </button>
              ))}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Loading state */}
      {isPending && (
        <Card>
          <CardContent className="pt-5 space-y-3">
            <Skeleton className="h-4 w-1/3" />
            <Skeleton className="h-4 w-full" />
            <Skeleton className="h-4 w-5/6" />
            <Skeleton className="h-4 w-4/6" />
          </CardContent>
        </Card>
      )}

      {/* Error */}
      {error && (
        <div className="flex items-start gap-2 rounded-lg border border-destructive/30 bg-destructive/5 px-4 py-3 text-sm text-destructive">
          <AlertCircle className="mt-0.5 h-4 w-4 shrink-0" />
          {error.message}
        </div>
      )}

      {/* Answer */}
      {result && !isPending && (
        <div className="space-y-4 animate-fade-in">
          <Card>
            <CardHeader className="pb-2">
              <CardDescription className="text-xs uppercase tracking-wide font-semibold">
                Your question
              </CardDescription>
              <CardTitle className="font-display text-base font-medium text-foreground">
                {result.question}
              </CardTitle>
            </CardHeader>
            <Separator />
            <CardContent className="pt-4">
              <div className="flex items-start gap-3">
                <div className="flex h-7 w-7 shrink-0 items-center justify-center rounded-lg bg-accent mt-0.5">
                  <Bot className="h-4 w-4 text-primary" />
                </div>
                <div>
                  <p className="text-xs font-semibold uppercase tracking-wide text-muted-foreground mb-2">
                    Advisor Response
                  </p>
                  <p className="text-sm leading-relaxed text-foreground whitespace-pre-wrap">
                    {result.answer}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          <IntelligenceSnapshot data={result.intelligence_snapshot} />
        </div>
      )}
    </div>
  )
}
