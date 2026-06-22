// Cliente HTTP tipado para la API FastAPI DiabetesNHANES.

import type {
  BatchPredictResponse,
  ConfusionMatrix,
  Curves,
  DistributionResponse,
  FeatureImportance,
  FeaturesResponse,
  Health,
  Metrics,
  ModelComparisonRow,
  ModelInfo,
  PredictionsResponse,
  PredictPayload,
  PredictResult,
  Summary,
  Threshold,
} from "./types"

export const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000"

/** Error de API con el status HTTP; `modelNotReady` marca el caso 503. */
export class ApiError extends Error {
  status: number
  modelNotReady: boolean

  constructor(message: string, status: number) {
    super(message)
    this.name = "ApiError"
    this.status = status
    this.modelNotReady = status === 503
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  let res: Response
  try {
    res = await fetch(`${API_BASE_URL}${path}`, {
      headers: { "Content-Type": "application/json", ...(init?.headers ?? {}) },
      ...init,
    })
  } catch {
    throw new ApiError(
      `No se pudo conectar con la API en ${API_BASE_URL}. ¿Está corriendo 'uvicorn api.main:app'?`,
      0,
    )
  }

  if (!res.ok) {
    let detail: string = res.statusText
    try {
      const body = (await res.json()) as { detail?: unknown }
      if (body?.detail) {
        detail = typeof body.detail === "string" ? body.detail : JSON.stringify(body.detail)
      }
    } catch {
      /* respuesta sin cuerpo JSON */
    }
    throw new ApiError(detail, res.status)
  }

  return (await res.json()) as T
}

export const api = {
  health: () => request<Health>("/health"),
  modelInfo: () => request<ModelInfo>("/model-info"),
  features: () => request<FeaturesResponse>("/features"),
  thresholds: () => request<{ thresholds: Threshold[] }>("/thresholds"),
  metrics: () => request<Metrics>("/metrics"),
  curves: () => request<Curves>("/curves"),
  modelComparison: () => request<{ models: ModelComparisonRow[] }>("/model-comparison"),
  confusionMatrix: () => request<ConfusionMatrix>("/confusion-matrix"),
  featureImportance: (top = 15) =>
    request<{ importances: FeatureImportance[] }>(`/feature-importance?top=${top}`),
  summary: () => request<Summary>("/stats/summary"),
  distribution: (by: string) =>
    request<DistributionResponse>(`/stats/distribution?by=${encodeURIComponent(by)}`),
  predict: (payload: PredictPayload) =>
    request<PredictResult>("/predict", { method: "POST", body: JSON.stringify(payload) }),
  predictBatch: (items: PredictPayload[]) =>
    request<BatchPredictResponse>("/predict/batch", {
      method: "POST",
      body: JSON.stringify({ items }),
    }),
  predictions: (limit = 100, offset = 0) =>
    request<PredictionsResponse>(`/predictions?limit=${limit}&offset=${offset}`),
}
