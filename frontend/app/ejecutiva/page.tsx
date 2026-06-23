"use client"

import { RiGroupLine, RiHeartPulseLine, RiPulseLine } from "@remixicon/react"

import { useSummary } from "@/lib/queries"
import { num, pct } from "@/lib/format"
import { KpiCard } from "@/components/kpi-card"
import { QueryBoundary } from "@/components/states"
import { DistributionChart } from "@/components/views/distribution-chart"

export default function EjecutivaPage() {
  const { data, isLoading, error } = useSummary()

  return (
    <div className="space-y-6">
      <QueryBoundary isLoading={isLoading} error={error} skeletonHeight={120}>
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <KpiCard
            title="Participantes"
            value={num(data?.n_participants)}
            hint="Registros en el dataset de modelado"
            icon={<RiGroupLine className="size-4" />}
          />
          <KpiCard
            title="Prevalencia diabetes"
            value={pct(data?.positive_rate)}
            hint="Proporción con target positivo"
            icon={<RiHeartPulseLine className="size-4" />}
          />
          <KpiCard
            title="Casos positivos"
            value={num(data?.n_positive)}
            hint="diabetes_target = 1"
            icon={<RiPulseLine className="size-4" />}
          />
          <KpiCard
            title="Casos negativos"
            value={num(data?.n_negative)}
            hint="diabetes_target = 0"
            icon={<RiPulseLine className="size-4" />}
          />
        </div>
      </QueryBoundary>

      <DistributionChart />
    </div>
  )
}
