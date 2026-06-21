"use client"

import { useConfusionMatrix } from "@/lib/queries"
import { cn } from "@/lib/utils"
import { QueryBoundary } from "@/components/states"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"

export function ConfusionMatrixCard() {
  const { data, isLoading, error } = useConfusionMatrix()

  const matrix = data?.matrix ?? []
  const max = Math.max(1, ...matrix.flat())

  return (
    <Card>
      <CardHeader>
        <CardTitle>Matriz de confusión</CardTitle>
        <CardDescription>Real (filas) vs. predicho (columnas)</CardDescription>
      </CardHeader>
      <CardContent>
        <QueryBoundary isLoading={isLoading} error={error} skeletonHeight={220}>
          {data ? (
            <div className="flex justify-center">
              <div
                className="grid gap-1"
                style={{ gridTemplateColumns: `auto repeat(${data.labels.length}, 64px)` }}
              >
                <div />
                {data.labels.map((l) => (
                  <div key={`col-${l}`} className="text-center text-xs text-muted-foreground">
                    pred {l}
                  </div>
                ))}
                {matrix.map((row, i) => (
                  <Row key={`row-${i}`} label={`real ${data.labels[i]}`} row={row} max={max} />
                ))}
              </div>
            </div>
          ) : null}
        </QueryBoundary>
      </CardContent>
    </Card>
  )
}

function Row({ label, row, max }: { label: string; row: number[]; max: number }) {
  return (
    <>
      <div className="flex items-center justify-end pr-2 text-xs text-muted-foreground">{label}</div>
      {row.map((value, j) => {
        const intensity = value / max
        return (
          <div
            key={j}
            className={cn(
              "flex h-16 items-center justify-center text-sm font-semibold tabular-nums",
              intensity > 0.5 ? "text-primary-foreground" : "text-foreground",
            )}
            style={{ backgroundColor: `color-mix(in oklab, var(--primary) ${Math.round(intensity * 100)}%, var(--muted))` }}
          >
            {value}
          </div>
        )
      })}
    </>
  )
}
