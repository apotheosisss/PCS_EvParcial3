"use client"

import { CartesianGrid, Line, LineChart, ReferenceLine, XAxis, YAxis } from "recharts"

import { useCurves } from "@/lib/queries"
import { pct } from "@/lib/format"
import { QueryBoundary } from "@/components/states"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import {
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent,
  type ChartConfig,
} from "@/components/ui/chart"

const config = {
  tpr: { label: "Sensibilidad", color: "var(--chart-1)" },
} satisfies ChartConfig

export function RocCurve() {
  const { data, isLoading, error } = useCurves()

  return (
    <Card>
      <CardHeader>
        <CardTitle>Curva ROC</CardTitle>
        <CardDescription>
          Sensibilidad vs. 1−especificidad · AUC {data ? pct(data.roc_auc) : "—"}
        </CardDescription>
      </CardHeader>
      <CardContent>
        <QueryBoundary isLoading={isLoading} error={error} skeletonHeight={300}>
          <ChartContainer config={config} className="h-[300px] w-full">
            <LineChart data={data?.roc ?? []} margin={{ left: 8, right: 16, top: 8, bottom: 8 }}>
              <CartesianGrid />
              <XAxis
                dataKey="fpr"
                type="number"
                domain={[0, 1]}
                tickLine={false}
                axisLine={false}
                tickFormatter={(v: number) => v.toFixed(1)}
                label={{ value: "1 − especificidad", position: "insideBottom", offset: -4, fontSize: 11 }}
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
              <Line dataKey="tpr" type="monotone" stroke="var(--color-tpr)" dot={false} strokeWidth={2} />
            </LineChart>
          </ChartContainer>
        </QueryBoundary>
      </CardContent>
    </Card>
  )
}
