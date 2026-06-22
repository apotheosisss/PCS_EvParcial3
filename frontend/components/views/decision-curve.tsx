"use client"

import { CartesianGrid, Line, LineChart, ReferenceLine, XAxis, YAxis } from "recharts"

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
  modelo: { label: "Usar el modelo", color: "var(--chart-1)" },
  tratar_todos: { label: "Derivar a todos", color: "var(--chart-5)" },
} satisfies ChartConfig

export function DecisionCurve() {
  const { data, isLoading, error } = useCurves()

  return (
    <Card>
      <CardHeader>
        <CardTitle>Curva de decisión (beneficio neto)</CardTitle>
        <CardDescription>
          Utilidad clínica del modelo vs. derivar a todos / a nadie (línea en 0)
        </CardDescription>
      </CardHeader>
      <CardContent>
        <QueryBoundary isLoading={isLoading} error={error} skeletonHeight={300}>
          <ChartContainer config={config} className="h-[300px] w-full">
            <LineChart data={data?.decision_curve ?? []} margin={{ left: 8, right: 16, top: 8, bottom: 8 }}>
              <CartesianGrid />
              <XAxis
                dataKey="threshold"
                type="number"
                domain={[0, 0.6]}
                tickLine={false}
                axisLine={false}
                tickFormatter={(v: number) => v.toFixed(2)}
                label={{ value: "Umbral de riesgo", position: "insideBottom", offset: -4, fontSize: 11 }}
              />
              <YAxis tickLine={false} axisLine={false} tickFormatter={(v: number) => v.toFixed(2)} />
              <ReferenceLine y={0} stroke="var(--muted-foreground)" strokeDasharray="4 4" />
              <ChartTooltip content={<ChartTooltipContent />} />
              <ChartLegend content={<ChartLegendContent />} />
              <Line dataKey="modelo" type="monotone" stroke="var(--color-modelo)" dot={false} strokeWidth={2} />
              <Line dataKey="tratar_todos" type="monotone" stroke="var(--color-tratar_todos)" dot={false} strokeWidth={1.5} strokeDasharray="5 3" />
            </LineChart>
          </ChartContainer>
        </QueryBoundary>
      </CardContent>
    </Card>
  )
}
