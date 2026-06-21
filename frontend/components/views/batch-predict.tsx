"use client"

import * as React from "react"
import { useMutation } from "@tanstack/react-query"
import { RiDownloadLine, RiUploadLine } from "@remixicon/react"
import { toast } from "sonner"

import { api } from "@/lib/api"
import type { BatchPredictResponse, PredictPayload } from "@/lib/types"
import { pct, downloadCsv } from "@/lib/format"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"

const PLACEHOLDER = `[
  {"RIDAGEYR": 55, "RIAGENDR": 1, "BMXBMI": 31.5, "LBXGH": 6.8, "LBXGLU": 130},
  {"RIDAGEYR": 30, "RIAGENDR": 2, "BMXBMI": 22.0, "LBXGH": 5.1, "LBXGLU": 90}
]`

/** Parsea un CSV simple (primera fila = headers) a registros numéricos. */
function parseCsv(text: string): PredictPayload[] {
  const lines = text.trim().split(/\r?\n/)
  if (lines.length < 2) return []
  const headers = lines[0].split(",").map((h) => h.trim())
  return lines.slice(1).map((line) => {
    const cells = line.split(",")
    const row: PredictPayload = {}
    headers.forEach((h, i) => {
      const n = Number(cells[i])
      row[h] = Number.isFinite(n) ? n : null
    })
    return row
  })
}

export function BatchPredict() {
  const [raw, setRaw] = React.useState("")

  const mutation = useMutation<BatchPredictResponse, Error, PredictPayload[]>({
    mutationFn: (items) => api.predictBatch(items),
    onError: (e) => toast.error(e.message),
    onSuccess: (d) => toast.success(`${d.n} predicciones generadas`),
  })

  const runJson = () => {
    try {
      const items = JSON.parse(raw || PLACEHOLDER) as PredictPayload[]
      if (!Array.isArray(items) || items.length === 0) throw new Error("Debe ser un arreglo no vacío")
      mutation.mutate(items)
    } catch (e) {
      toast.error(`JSON inválido: ${(e as Error).message}`)
    }
  }

  const onFile = async (file: File) => {
    const text = await file.text()
    const items = parseCsv(text)
    if (items.length === 0) {
      toast.error("CSV vacío o sin filas de datos")
      return
    }
    mutation.mutate(items)
  }

  const results = mutation.data?.results ?? []

  return (
    <Card>
      <CardHeader>
        <CardTitle>Predicción por lote</CardTitle>
        <CardDescription>Pega un arreglo JSON o sube un CSV (encabezados = nombres de feature).</CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <textarea
          value={raw}
          onChange={(e) => setRaw(e.target.value)}
          placeholder={PLACEHOLDER}
          rows={6}
          className="w-full resize-y border bg-transparent p-3 font-mono text-xs outline-none focus-visible:ring-[3px] focus-visible:ring-ring/50"
        />

        <div className="flex flex-wrap items-center gap-3">
          <Button onClick={runJson} disabled={mutation.isPending}>
            {mutation.isPending ? "Procesando…" : "Predecir JSON"}
          </Button>

          <Button variant="outline" asChild>
            <label className="cursor-pointer">
              <RiUploadLine className="size-4" />
              Subir CSV
              <input
                type="file"
                accept=".csv,text/csv"
                className="hidden"
                onChange={(e) => {
                  const f = e.target.files?.[0]
                  if (f) void onFile(f)
                  e.target.value = ""
                }}
              />
            </label>
          </Button>

          {results.length ? (
            <Button
              variant="ghost"
              onClick={() =>
                downloadCsv("predicciones_lote.csv", results as unknown as Record<string, unknown>[])
              }
            >
              <RiDownloadLine className="size-4" />
              Descargar CSV
            </Button>
          ) : null}
        </div>

        {results.length ? (
          <div className="max-h-80 overflow-auto border">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead className="w-12">#</TableHead>
                  <TableHead>Predicción</TableHead>
                  <TableHead>Banda</TableHead>
                  <TableHead className="text-right">Probabilidad</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {results.map((r, i) => (
                  <TableRow key={i}>
                    <TableCell className="text-muted-foreground">{i + 1}</TableCell>
                    <TableCell>{r.label}</TableCell>
                    <TableCell>
                      <Badge variant="outline">{r.risk_band}</Badge>
                    </TableCell>
                    <TableCell className="text-right tabular-nums">{pct(r.probability)}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        ) : null}
      </CardContent>
    </Card>
  )
}
