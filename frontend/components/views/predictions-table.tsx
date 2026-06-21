"use client"

import * as React from "react"
import { RiArrowLeftLine, RiArrowRightLine, RiDownloadLine } from "@remixicon/react"

import { usePredictions } from "@/lib/queries"
import { downloadCsv } from "@/lib/format"
import { QueryBoundary } from "@/components/states"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"

const PAGE_SIZE = 20

export function PredictionsTable() {
  const [offset, setOffset] = React.useState(0)
  const { data, isLoading, error } = usePredictions(PAGE_SIZE, offset)

  const items = data?.items ?? []
  const columns = items.length ? Object.keys(items[0]) : []
  const total = data?.total ?? 0
  const hasPrev = offset > 0
  const hasNext = offset + PAGE_SIZE < total

  return (
    <Card>
      <CardHeader className="flex flex-row items-start justify-between gap-4">
        <div>
          <CardTitle>Predicciones del conjunto de prueba</CardTitle>
          <CardDescription>
            {total ? `${total} registros` : "Muestra real vs. predicho"}
          </CardDescription>
        </div>
        {items.length ? (
          <Button variant="ghost" size="sm" onClick={() => downloadCsv("predicciones_test.csv", items)}>
            <RiDownloadLine className="size-4" />
            CSV
          </Button>
        ) : null}
      </CardHeader>
      <CardContent className="space-y-4">
        <QueryBoundary isLoading={isLoading} error={error} skeletonHeight={300}>
          <div className="overflow-auto border">
            <Table>
              <TableHeader>
                <TableRow>
                  {columns.map((c) => (
                    <TableHead key={c} className="text-right first:text-left">
                      {c}
                    </TableHead>
                  ))}
                </TableRow>
              </TableHeader>
              <TableBody>
                {items.map((row, i) => (
                  <TableRow key={offset + i}>
                    {columns.map((c, j) => (
                      <TableCell
                        key={c}
                        className={j === 0 ? "" : "text-right tabular-nums"}
                      >
                        {row[c]}
                      </TableCell>
                    ))}
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>

          <div className="flex items-center justify-between text-sm text-muted-foreground">
            <span>
              {total ? `${offset + 1}–${Math.min(offset + PAGE_SIZE, total)} de ${total}` : "—"}
            </span>
            <div className="flex gap-2">
              <Button
                variant="outline"
                size="sm"
                disabled={!hasPrev}
                onClick={() => setOffset((o) => Math.max(0, o - PAGE_SIZE))}
              >
                <RiArrowLeftLine className="size-4" />
                Anterior
              </Button>
              <Button
                variant="outline"
                size="sm"
                disabled={!hasNext}
                onClick={() => setOffset((o) => o + PAGE_SIZE)}
              >
                Siguiente
                <RiArrowRightLine className="size-4" />
              </Button>
            </div>
          </div>
        </QueryBoundary>
      </CardContent>
    </Card>
  )
}
