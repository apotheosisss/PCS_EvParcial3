"use client"

import * as React from "react"
import { useMutation } from "@tanstack/react-query"
import { RiPulseLine } from "@remixicon/react"

import { api } from "@/lib/api"
import { useFeatures, useThresholds } from "@/lib/queries"
import type { FeatureMeta, PredictResult } from "@/lib/types"
import { pct, riskBandStyle } from "@/lib/format"
import { cn } from "@/lib/utils"
import { QueryBoundary } from "@/components/states"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"

export function PredictForm() {
  const { data: featuresData, isLoading, error } = useFeatures()
  const { data: thresholds } = useThresholds()

  const userFeatures = React.useMemo(
    () => (featuresData?.features ?? []).filter((f) => f.user_facing),
    [featuresData],
  )

  // Solo se guardan los campos editados; el resto usa el default de la feature.
  const [overrides, setOverrides] = React.useState<Record<string, number>>({})
  const [result, setResult] = React.useState<PredictResult | null>(null)

  const valueOf = React.useCallback(
    (f: FeatureMeta): number => overrides[f.name] ?? f.default ?? 0,
    [overrides],
  )

  const mutation = useMutation({
    mutationFn: () => {
      const payload = Object.fromEntries(
        userFeatures.map((f) => {
          const v = valueOf(f)
          // RIAGENDR es entero (1/2) en el contrato; el default inferido puede ser la media.
          return [f.name, f.name === "RIAGENDR" ? (v === 2 ? 2 : 1) : v]
        }),
      )
      return api.predict(payload)
    },
    onSuccess: setResult,
  })

  const setField = (name: string, value: number) =>
    setOverrides((prev) => ({ ...prev, [name]: value }))

  return (
    <Card>
      <CardHeader>
        <CardTitle>Simulador de predicción</CardTitle>
        <CardDescription>
          Ingresa valores y estima el riesgo. Los campos no provistos se imputan con la media del entrenamiento.
        </CardDescription>
      </CardHeader>
      <CardContent>
        <QueryBoundary isLoading={isLoading} error={error} skeletonHeight={320}>
          <form
            onSubmit={(e) => {
              e.preventDefault()
              mutation.mutate()
            }}
            className="space-y-6"
          >
            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
              {userFeatures.map((f) => (
                <Field key={f.name} feature={f} value={valueOf(f)} onChange={setField} />
              ))}
            </div>

            <div className="flex flex-wrap items-center gap-3">
              <Button type="submit" disabled={mutation.isPending}>
                <RiPulseLine className="size-4" />
                {mutation.isPending ? "Calculando…" : "Estimar riesgo"}
              </Button>
              {mutation.isError ? (
                <span className="text-sm text-destructive">
                  {(mutation.error as Error).message}
                </span>
              ) : null}
            </div>

            {result ? <ResultPanel result={result} /> : null}
          </form>

          {thresholds?.thresholds?.length ? (
            <div className="mt-6 border-t pt-4">
              <p className="mb-2 text-xs font-medium text-muted-foreground uppercase">
                Referencias clínicas (educativas)
              </p>
              <ul className="grid gap-1 text-xs text-muted-foreground sm:grid-cols-2">
                {thresholds.thresholds.map((t) => (
                  <li key={t.variable}>
                    <span className="font-mono">{t.variable}</span> {t.op} {t.value}
                    {t.description ? ` — ${t.description}` : ""}
                  </li>
                ))}
              </ul>
            </div>
          ) : null}
        </QueryBoundary>
      </CardContent>
    </Card>
  )
}

function Field({
  feature,
  value,
  onChange,
}: {
  feature: FeatureMeta
  value: number | undefined
  onChange: (name: string, value: number) => void
}) {
  const label = `${feature.label}${feature.unit ? ` (${feature.unit})` : ""}`

  if (feature.name === "RIAGENDR") {
    // El default inferido puede ser la media (no entera); se normaliza a 1/2.
    const sex = value === 2 ? "2" : "1"
    return (
      <div className="space-y-1.5">
        <Label>Sexo</Label>
        <Select value={sex} onValueChange={(v) => onChange(feature.name, Number(v))}>
          <SelectTrigger>
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="1">Hombre</SelectItem>
            <SelectItem value="2">Mujer</SelectItem>
          </SelectContent>
        </Select>
      </div>
    )
  }

  return (
    <div className="space-y-1.5">
      <Label htmlFor={feature.name}>{label}</Label>
      <Input
        id={feature.name}
        type="number"
        step="any"
        min={feature.min ?? undefined}
        max={feature.max ?? undefined}
        value={Number.isFinite(value) ? value : ""}
        onChange={(e) => onChange(feature.name, e.target.value === "" ? 0 : Number(e.target.value))}
      />
    </div>
  )
}

function ResultPanel({ result }: { result: PredictResult }) {
  const band = riskBandStyle(result.risk_band)
  return (
    <div className={cn("flex flex-wrap items-center justify-between gap-4 border p-4", band.className)}>
      <div>
        <p className="text-xs uppercase opacity-80">Resultado</p>
        <p className="text-lg font-semibold">{band.label}</p>
        <p className="text-xs opacity-80">
          Clasificación: {result.label} · umbral {result.threshold}
        </p>
      </div>
      <div className="text-right">
        <p className="text-xs uppercase opacity-80">Probabilidad</p>
        <p className="text-3xl font-bold tabular-nums">{pct(result.probability)}</p>
      </div>
    </div>
  )
}
