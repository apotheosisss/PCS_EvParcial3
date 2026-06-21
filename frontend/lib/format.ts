// Utilidades de formato y exportación CSV.

export function pct(value: number | null | undefined, digits = 1): string {
  if (value === null || value === undefined || Number.isNaN(value)) return "—"
  return `${(value * 100).toFixed(digits)}%`
}

export function num(value: number | null | undefined, digits = 0): string {
  if (value === null || value === undefined || Number.isNaN(value)) return "—"
  return value.toLocaleString("es-MX", { maximumFractionDigits: digits })
}

export function decimal(value: number | null | undefined, digits = 4): string {
  if (value === null || value === undefined || Number.isNaN(value)) return "—"
  return value.toFixed(digits)
}

/** Convierte un arreglo de objetos a CSV (UTF-8, separador coma). */
export function toCsv(rows: Record<string, unknown>[]): string {
  if (rows.length === 0) return ""
  const headers = Object.keys(rows[0])
  const escape = (v: unknown) => {
    const s = v === null || v === undefined ? "" : String(v)
    return /[",\n]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s
  }
  const lines = [headers.join(",")]
  for (const row of rows) lines.push(headers.map((h) => escape(row[h])).join(","))
  return lines.join("\n")
}

/** Descarga un CSV en el navegador. */
export function downloadCsv(filename: string, rows: Record<string, unknown>[]): void {
  const blob = new Blob([toCsv(rows)], { type: "text/csv;charset=utf-8;" })
  const url = URL.createObjectURL(blob)
  const a = document.createElement("a")
  a.href = url
  a.download = filename
  a.click()
  URL.revokeObjectURL(url)
}

/** Etiqueta y color (token chart) por banda de riesgo. */
export function riskBandStyle(band: string): { label: string; className: string } {
  switch (band) {
    case "alto":
      return { label: "Riesgo alto", className: "bg-destructive/15 text-destructive border-destructive/30" }
    case "medio":
      return { label: "Riesgo medio", className: "bg-chart-2/20 text-foreground border-chart-2/40" }
    default:
      return { label: "Riesgo bajo", className: "bg-chart-1/20 text-foreground border-chart-1/40" }
  }
}
