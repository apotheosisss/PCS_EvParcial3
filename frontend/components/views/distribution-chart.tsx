"use client"

import * as React from "react"
import { Bar, BarChart, CartesianGrid, XAxis, YAxis } from "recharts"

import { useDistribution } from "@/lib/queries"
import { pct } from "@/lib/format"
import { QueryBoundary } from "@/components/states"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import {
  ChartContainer,
  ChartTooltip,
  type ChartConfig,
} from "@/components/ui/chart"
import type { DistributionBucket } from "@/lib/types"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"

const OPTIONS = [
  { value: "age_group", label: "Grupo de edad" },
  { value: "bmi_category", label: "Categoría IMC" },
  { value: "RIAGENDR", label: "Sexo" },
]

const config = {
  count: { label: "Participantes", color: "var(--chart-1)" },
} satisfies ChartConfig

function BucketTooltip({
  active,
  payload,
}: {
  active?: boolean
  payload?: { payload: DistributionBucket }[]
}) {
  if (!active || !payload?.length) return null
  const bucket = payload[0].payload
  return (
    <div className="bg-popover text-popover-foreground border px-3 py-2 text-xs shadow-md">
      <p className="font-medium">{bucket.key}</p>
      <p className="text-muted-foreground">Participantes: {bucket.count}</p>
      <p className="text-muted-foreground">% diabetes: {pct(bucket.positive_rate)}</p>
    </div>
  )
}

export function DistributionChart() {
  const [by, setBy] = React.useState("age_group")
  const { data, isLoading, error } = useDistribution(by)

  return (
    <Card>
      <CardHeader className="flex flex-row items-start justify-between gap-4">
        <div>
          <CardTitle>Distribución poblacional</CardTitle>
          <CardDescription>Conteo por categoría y prevalencia de diabetes</CardDescription>
        </div>
        <Select value={by} onValueChange={setBy}>
          <SelectTrigger className="w-44">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            {OPTIONS.map((o) => (
              <SelectItem key={o.value} value={o.value}>
                {o.label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </CardHeader>
      <CardContent>
        <QueryBoundary isLoading={isLoading} error={error} skeletonHeight={280}>
          <ChartContainer config={config} className="h-[280px] w-full">
            <BarChart accessibilityLayer data={data?.buckets ?? []}>
              <CartesianGrid vertical={false} />
              <XAxis dataKey="key" tickLine={false} axisLine={false} tickMargin={8} />
              <YAxis tickLine={false} axisLine={false} width={36} />
              <ChartTooltip content={<BucketTooltip />} />
              <Bar dataKey="count" fill="var(--color-count)" radius={2} />
            </BarChart>
          </ChartContainer>
        </QueryBoundary>
      </CardContent>
    </Card>
  )
}
