"use client"

import { Area, AreaChart, CartesianGrid, ReferenceLine, XAxis, YAxis } from "recharts"

import { useCurves } from "@/lib/queries"
import { QueryBoundary } from "@/components/states"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import {
  ChartContainer,
  ChartLegend,
  ChartLegendContent,
  ChartTooltip,
  ChartTooltipContent,
  type ChartConfig,
} from "@/components/ui/chart"

const config = {
  sin_diabetes: { label: "Sin diabetes", color: "var(--chart-1)" },
  con_diabetes: { label: "Con diabetes", color: "var(--chart-4)" },
} satisfies ChartConfig

export function ScoreDistribution() {
  const { data, isLoading, error } = useCurves()

  return (
    <Card>
      <CardHeader>
        <CardTitle>Distribución del riesgo por grupo</CardTitle>
        <CardDescription>
          Score de riesgo en sanos vs. diabéticos · la línea marca el umbral de decisión
        </CardDescription>
      </CardHeader>
      <CardContent>
        <QueryBoundary isLoading={isLoading} error={error} skeletonHeight={300}>
          <ChartContainer config={config} className="h-[300px] w-full">
            <AreaChart data={data?.distribution ?? []} margin={{ left: 8, right: 16, top: 8, bottom: 8 }}>
              <CartesianGrid vertical={false} />
              <XAxis
                dataKey="score"
                type="number"
                domain={[0, 1]}
                tickLine={false}
                axisLine={false}
                tickFormatter={(v: number) => v.toFixed(1)}
                label={{ value: "Riesgo predicho", position: "insideBottom", offset: -4, fontSize: 11 }}
              />
              <YAxis tickLine={false} axisLine={false} tickFormatter={(v: number) => `${(v * 100).toFixed(0)}%`} />
              {data ? (
                <ReferenceLine x={data.threshold} stroke="var(--destructive)" strokeDasharray="4 4" />
              ) : null}
              <ChartTooltip content={<ChartTooltipContent />} />
              <ChartLegend content={<ChartLegendContent />} />
              <Area
                dataKey="sin_diabetes"
                type="monotone"
                stroke="var(--color-sin_diabetes)"
                fill="var(--color-sin_diabetes)"
                fillOpacity={0.3}
              />
              <Area
                dataKey="con_diabetes"
                type="monotone"
                stroke="var(--color-con_diabetes)"
                fill="var(--color-con_diabetes)"
                fillOpacity={0.3}
              />
            </AreaChart>
          </ChartContainer>
        </QueryBoundary>
      </CardContent>
    </Card>
  )
}
