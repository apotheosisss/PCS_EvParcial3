"use client"

import * as React from "react"
import { QueryClient, QueryClientProvider } from "@tanstack/react-query"

import { ApiError } from "@/lib/api"
import { Toaster } from "@/components/ui/sonner"

export function Providers({ children }: { children: React.ReactNode }) {
  const [client] = React.useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            staleTime: 30_000,
            refetchOnWindowFocus: false,
            retry: (failureCount, error) => {
              // No reintentar si el modelo aún no está listo (503) o no hay conexión.
              if (error instanceof ApiError && (error.modelNotReady || error.status === 0)) {
                return false
              }
              return failureCount < 2
            },
          },
        },
      }),
  )

  return (
    <QueryClientProvider client={client}>
      {children}
      <Toaster richColors position="top-right" />
    </QueryClientProvider>
  )
}
