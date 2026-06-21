"use client"

import { Bar, BarChart, CartesianGrid, XAxis, YAxis } from "recharts"

import { useFeatureImportance } from "@/lib/queries"
import { QueryBoundary } from "@/components/states"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import {
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent,
  type ChartConfig,
} from "@/components/ui/chart"

const config = {
  importance: { label: "Importancia", color: "var(--chart-2)" },
} satisfies ChartConfig

export function ImportanceChart() {
  const { data, isLoading, error } = useFeatureImportance(15)
  const rows = data?.importances ?? []

  return (
    <Card>
      <CardHeader>
        <CardTitle>Importancia de variables</CardTitle>
        <CardDescription>Contribución de cada feature al modelo (top 15)</CardDescription>
      </CardHeader>
      <CardContent>
        <QueryBoundary isLoading={isLoading} error={error} skeletonHeight={380}>
          <ChartContainer config={config} className="h-[380px] w-full">
            <BarChart accessibilityLayer data={rows} layout="vertical" margin={{ left: 12, right: 16 }}>
              <CartesianGrid horizontal={false} />
              <XAxis type="number" tickLine={false} axisLine={false} />
              <YAxis
                type="category"
                dataKey="feature"
                tickLine={false}
                axisLine={false}
                width={150}
                tick={{ fontSize: 11 }}
              />
              <ChartTooltip content={<ChartTooltipContent />} />
              <Bar dataKey="importance" fill="var(--color-importance)" radius={2} />
            </BarChart>
          </ChartContainer>
        </QueryBoundary>
      </CardContent>
    </Card>
  )
}
