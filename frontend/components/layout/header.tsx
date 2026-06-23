"use client"

import { usePathname } from "next/navigation"
import { RiCheckboxCircleLine, RiErrorWarningLine } from "@remixicon/react"

import { useHealth, useModelInfo } from "@/lib/queries"
import { Badge } from "@/components/ui/badge"

const TITLES: Record<string, { title: string; subtitle: string }> = {
  "/ejecutiva": { title: "Vista Ejecutiva", subtitle: "Indicadores poblacionales de riesgo de diabetes" },
  "/tecnica": { title: "Vista Técnica", subtitle: "Desempeño y explicabilidad del modelo" },
  "/operativa": { title: "Vista Operativa", subtitle: "Simulador de predicción y resultados" },
}

export function Header() {
  const pathname = usePathname()
  const { data: health } = useHealth()
  const { data: info } = useModelInfo()

  const meta = TITLES[pathname] ?? {
    title: "NHANES Diabetes Risk",
    subtitle: "Dashboard analítico",
  }
  const online = health?.model_loaded ?? false

  return (
    <header className="flex h-16 items-center justify-between border-b px-5">
      <div className="leading-tight">
        <h1 className="text-base font-semibold">{meta.title}</h1>
        <p className="text-xs text-muted-foreground">{meta.subtitle}</p>
      </div>
      <div className="flex items-center gap-2">
        {info?.model_name ? (
          <Badge variant="secondary" className="font-mono text-[11px]">
            {info.model_name} · {info.model_version}
          </Badge>
        ) : null}
        <Badge
          variant="outline"
          className="flex items-center gap-1 text-[11px]"
          title={online ? "Modelo cargado" : "Modelo no disponible"}
        >
          {online ? (
            <RiCheckboxCircleLine className="size-3.5 text-chart-1" />
          ) : (
            <RiErrorWarningLine className="size-3.5 text-destructive" />
          )}
          {online ? "API lista" : "Modelo no listo"}
        </Badge>
      </div>
    </header>
  )
}
