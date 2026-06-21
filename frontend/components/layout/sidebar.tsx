"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import {
  RiBarChartBoxLine,
  RiDashboardLine,
  RiHeartPulseLine,
} from "@remixicon/react"

import { cn } from "@/lib/utils"

const NAV = [
  { href: "/ejecutiva", label: "Ejecutiva", icon: RiDashboardLine, hint: "KPIs y distribuciones" },
  { href: "/tecnica", label: "Técnica", icon: RiBarChartBoxLine, hint: "Métricas del modelo" },
  { href: "/operativa", label: "Operativa", icon: RiHeartPulseLine, hint: "Simulador y predicciones" },
]

export function Sidebar() {
  const pathname = usePathname()

  return (
    <aside className="hidden w-64 shrink-0 flex-col border-r bg-sidebar text-sidebar-foreground md:flex">
      <div className="flex h-16 items-center gap-2 border-b px-5">
        <span className="flex size-8 items-center justify-center bg-sidebar-primary text-sidebar-primary-foreground">
          <RiHeartPulseLine className="size-5" />
        </span>
        <div className="leading-tight">
          <p className="text-sm font-semibold">NHANES</p>
          <p className="text-xs text-muted-foreground">Diabetes Risk</p>
        </div>
      </div>

      <nav className="flex flex-1 flex-col gap-1 p-3">
        {NAV.map((item) => {
          const active = pathname === item.href || pathname.startsWith(`${item.href}/`)
          const Icon = item.icon
          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "flex items-center gap-3 px-3 py-2.5 text-sm transition-colors",
                active
                  ? "bg-sidebar-primary text-sidebar-primary-foreground"
                  : "text-sidebar-foreground hover:bg-sidebar-accent hover:text-sidebar-accent-foreground",
              )}
            >
              <Icon className="size-4 shrink-0" />
              <span className="flex flex-col">
                <span className="font-medium">{item.label}</span>
                <span
                  className={cn(
                    "text-[11px]",
                    active ? "text-sidebar-primary-foreground/70" : "text-muted-foreground",
                  )}
                >
                  {item.hint}
                </span>
              </span>
            </Link>
          )
        })}
      </nav>

      <p className="border-t p-4 text-[11px] leading-relaxed text-muted-foreground">
        Uso educativo basado en datos NHANES. No reemplaza un diagnóstico clínico.
      </p>
    </aside>
  )
}
