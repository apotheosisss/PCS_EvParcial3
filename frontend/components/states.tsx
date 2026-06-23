"use client"

import { RiErrorWarningLine, RiInformationLine } from "@remixicon/react"

import { ApiError } from "@/lib/api"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { Skeleton } from "@/components/ui/skeleton"

interface QueryBoundaryProps {
  isLoading: boolean
  error: unknown
  children: React.ReactNode
  /** Altura del skeleton de carga. */
  skeletonHeight?: number
}

/** Renderiza skeleton mientras carga, una alerta clara ante error/503, o el contenido. */
export function QueryBoundary({
  isLoading,
  error,
  children,
  skeletonHeight = 160,
}: QueryBoundaryProps) {
  if (isLoading) {
    return <Skeleton style={{ height: skeletonHeight }} className="w-full" />
  }

  if (error) {
    const apiError = error instanceof ApiError ? error : null
    const modelNotReady = apiError?.modelNotReady

    return (
      <Alert variant={modelNotReady ? "default" : "destructive"}>
        {modelNotReady ? (
          <RiInformationLine className="size-4" />
        ) : (
          <RiErrorWarningLine className="size-4" />
        )}
        <AlertTitle>
          {modelNotReady ? "Modelo aún no disponible" : "No se pudieron cargar los datos"}
        </AlertTitle>
        <AlertDescription>
          {modelNotReady
            ? "Genera los artefactos ejecutando 'kedro run' (o el script de muestra) y vuelve a intentarlo."
            : apiError?.message ?? "Error inesperado al consultar la API."}
        </AlertDescription>
      </Alert>
    )
  }

  return <>{children}</>
}
