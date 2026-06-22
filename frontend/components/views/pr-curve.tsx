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
  precision: { label: "Precisión", color: "var(--chart-2)" },
} satisfies ChartConfig

export function PrCurve() {
  const { data, isLoading, error } = useCurves()

  return (
    <Card>
      <CardHeader>
        <CardTitle>Curva Precision-Recall</CardTitle>
        <CardDescription>
          Más informativa con clases desbalanceadas · PR-AUC {data ? pct(data.pr_auc) : "—"}
        </CardDescription>
      </CardHeader>
      <CardContent>
        <QueryBoundary isLoading={isLoading} error={error} skeletonHeight={300}>
          <ChartContainer config={config} className="h-[300px] w-full">
            <LineChart data={data?.pr ?? []} margin={{ left: 8, right: 16, top: 8, bottom: 8 }}>
              <CartesianGrid />
              <XAxis
                dataKey="recall"
                type="number"
                domain={[0, 1]}
                tickLine={false}
                axisLine={false}
                tickFormatter={(v: number) => v.toFixed(1)}
                label={{ value: "Recall", position: "insideBottom", offset: -4, fontSize: 11 }}
              />
              <YAxis
                type="number"
                domain={[0, 1]}
                tickLine={false}
                axisLine={false}
                tickFormatter={(v: number) => v.toFixed(1)}
              />
              {data ? (
                <ReferenceLine
                  y={data.prevalence}
                  stroke="var(--muted-foreground)"
                  strokeDasharray="4 4"
                  label={{ value: "azar", fontSize: 10, position: "insideTopRight" }}
                />
              ) : null}
              <ChartTooltip content={<ChartTooltipContent />} />
              <Line dataKey="precision" type="monotone" stroke="var(--color-precision)" dot={false} strokeWidth={2} />
            </LineChart>
          </ChartContainer>
        </QueryBoundary>
      </CardContent>
    </Card>
  )
}
