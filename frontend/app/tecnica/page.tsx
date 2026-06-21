"use client"

import { useMetrics } from "@/lib/queries"
import { decimal } from "@/lib/format"
import { KpiCard } from "@/components/kpi-card"
import { QueryBoundary } from "@/components/states"
import { ModelComparisonTable } from "@/components/views/model-comparison-table"
import { ConfusionMatrixCard } from "@/components/views/confusion-matrix"
import { ImportanceChart } from "@/components/views/importance-chart"

export default function TecnicaPage() {
  const { data, isLoading, error } = useMetrics()
  const m = data?.metrics

  return (
    <div className="space-y-6">
      <QueryBoundary isLoading={isLoading} error={error} skeletonHeight={120}>
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-5">
          <KpiCard title="Accuracy" value={decimal(m?.accuracy)} />
          <KpiCard title="Precision" value={decimal(m?.precision)} />
          <KpiCard title="Recall" value={decimal(m?.recall)} />
          <KpiCard title="F1" value={decimal(m?.f1)} />
          <KpiCard title="ROC-AUC" value={decimal(m?.roc_auc)} />
        </div>
      </QueryBoundary>

      <ModelComparisonTable />

      <div className="grid gap-6 lg:grid-cols-2">
        <ConfusionMatrixCard />
        <ImportanceChart />
      </div>
    </div>
  )
}
