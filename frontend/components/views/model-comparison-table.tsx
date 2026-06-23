"use client"

import { useMetrics, useModelComparison } from "@/lib/queries"
import { pct } from "@/lib/format"
import { cn } from "@/lib/utils"
import { QueryBoundary } from "@/components/states"
import { Badge } from "@/components/ui/badge"
import { Card, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"

const COLS: {
  key: "accuracy" | "precision" | "recall" | "f1" | "roc_auc" | "pr_auc"
  label: string
}[] = [
  { key: "accuracy", label: "Accuracy" },
  { key: "precision", label: "Precision" },
  { key: "recall", label: "Recall" },
  { key: "f1", label: "F1" },
  { key: "roc_auc", label: "ROC-AUC" },
  { key: "pr_auc", label: "PR-AUC" },
]

export function ModelComparisonTable() {
  const { data, isLoading, error } = useModelComparison()
  const { data: metrics } = useMetrics()
  const best = metrics?.best_model

  return (
    <Card>
      <CardHeader>
        <CardTitle>Comparación de modelos</CardTitle>
        <CardDescription>Métricas sobre el conjunto de prueba (mejor modelo por PR-AUC, resaltado)</CardDescription>
      </CardHeader>
      <div className="px-6 pb-6">
        <QueryBoundary isLoading={isLoading} error={error} skeletonHeight={180}>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Modelo</TableHead>
                {COLS.map((c) => (
                  <TableHead key={c.key} className="text-right">
                    {c.label}
                  </TableHead>
                ))}
              </TableRow>
            </TableHeader>
            <TableBody>
              {(data?.models ?? []).map((row) => {
                const isBest = row.model === best
                return (
                  <TableRow key={row.model} className={cn(isBest && "bg-primary/5")}>
                    <TableCell className="font-medium">
                      <span className="flex items-center gap-2">
                        {row.model}
                        {isBest ? (
                          <Badge variant="secondary" className="text-[10px]">
                            mejor
                          </Badge>
                        ) : null}
                      </span>
                    </TableCell>
                    {COLS.map((c) => (
                      <TableCell key={c.key} className="text-right tabular-nums">
                        {pct(row[c.key])}
                      </TableCell>
                    ))}
                  </TableRow>
                )
              })}
            </TableBody>
          </Table>
        </QueryBoundary>
      </div>
    </Card>
  )
}
