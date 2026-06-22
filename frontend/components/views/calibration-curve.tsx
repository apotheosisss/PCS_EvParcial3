"use client"

import { CartesianGrid, Line, LineChart, ReferenceLine, XAxis, YAxis } from "recharts"

import { useCurves } from "@/lib/queries"
import { QueryBoundary } from "@/components/states"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import {
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent,
  type ChartConfig,
} from "@/components/ui/chart"

const config = {
  observed: { label: "Frecuencia observada", color: "var(--chart-3)" },
} satisfies ChartConfig

export function CalibrationCurve() {
  const { data, isLoading, error } = useCurves()

  return (
    <Card>
      <CardHeader>
        <CardTitle>Calibración</CardTitle>
        <CardDescription>
          Probabilidad predicha vs. frecuencia real (ideal = diagonal)
        </CardDescription>
      </CardHeader>
      <CardContent>
        <QueryBoundary isLoading={isLoading} error={error} skeletonHeight={300}>
          <ChartContainer config={config} className="h-[300px] w-full">
            <LineChart data={data?.calibration ?? []} margin={{ left: 8, right: 16, top: 8, bottom: 8 }}>
              <CartesianGrid />
              <XAxis
                dataKey="predicted"
                type="number"
                domain={[0, 1]}
                tickLine={false}
                axisLine={false}
                tickFormatter={(v: number) => v.toFixed(1)}
                label={{ value: "Riesgo predicho", position: "insideBottom", offset: -4, fontSize: 11 }}
              />
              <YAxis
                type="number"
                domain={[0, 1]}
                tickLine={false}
                axisLine={false}
                tickFormatter={(v: number) => v.toFixed(1)}
              />
              <ReferenceLine
                segment={[{ x: 0, y: 0 }, { x: 1, y: 1 }]}
                stroke="var(--muted-foreground)"
                strokeDasharray="4 4"
              />
              <ChartTooltip content={<ChartTooltipContent />} />
              <Line dataKey="observed" type="monotone" stroke="var(--color-observed)" strokeWidth={2} />
            </LineChart>
          </ChartContainer>
        </QueryBoundary>
      </CardContent>
    </Card>
  )
}
