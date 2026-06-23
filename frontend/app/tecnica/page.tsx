"use client"

import { useMetrics } from "@/lib/queries"
import { pct } from "@/lib/format"
import { KpiCard } from "@/components/kpi-card"
import { QueryBoundary } from "@/components/states"
import { ModelComparisonTable } from "@/components/views/model-comparison-table"
import { ConfusionMatrixCard } from "@/components/views/confusion-matrix"
import { ImportanceChart } from "@/components/views/importance-chart"
import { RocCurve } from "@/components/views/roc-curve"
import { PrCurve } from "@/components/views/pr-curve"
import { CalibrationCurve } from "@/components/views/calibration-curve"
import { ScoreDistribution } from "@/components/views/score-distribution"
import { DecisionCurve } from "@/components/views/decision-curve"

export default function TecnicaPage() {
  const { data, isLoading, error } = useMetrics()
  const m = data?.metrics

  return (
    <div className="space-y-6">
      <QueryBoundary isLoading={isLoading} error={error} skeletonHeight={120}>
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-5">
          <KpiCard title="Accuracy" value={pct(m?.accuracy)} />
          <KpiCard title="Precision" value={pct(m?.precision)} />
          <KpiCard title="Recall" value={pct(m?.recall)} />
          <KpiCard title="F1" value={pct(m?.f1)} />
          <KpiCard title="ROC-AUC" value={pct(m?.roc_auc)} />
        </div>
      </QueryBoundary>

      <ModelComparisonTable />

      <div className="grid gap-6 lg:grid-cols-2">
        <ConfusionMatrixCard />
        <ImportanceChart />
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <RocCurve />
        <PrCurve />
        <CalibrationCurve />
        <ScoreDistribution />
        <DecisionCurve />
      </div>
    </div>
  )
}
