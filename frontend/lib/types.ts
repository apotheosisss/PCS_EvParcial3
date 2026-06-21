// Tipos espejo de api/schemas.py (FastAPI DiabetesNHANES).

export interface Health {
  status: string
  model_loaded: boolean
  metrics_loaded: boolean
  model_version: string | null
}

export interface ModelInfo {
  model_name: string | null
  model_version: string
  n_features: number
}

export interface FeatureMeta {
  name: string
  label: string
  dtype: string
  user_facing: boolean
  is_derived: boolean
  default: number | null
  min: number | null
  max: number | null
  unit: string | null
}

export interface FeaturesResponse {
  n_features: number
  feature_names: string[]
  features: FeatureMeta[]
}

export interface Threshold {
  variable: string
  op: string
  value: number
  description: string | null
}

export interface ModelScores {
  accuracy: number
  precision: number
  recall: number
  f1: number
  roc_auc: number
}

export interface Metrics {
  best_model: string
  metrics: ModelScores
  all_models: Record<string, ModelScores>
  n_features: number
}

export interface ModelComparisonRow extends ModelScores {
  model: string
}

export interface ConfusionMatrix {
  labels: string[]
  index: string[]
  columns: string[]
  matrix: number[][]
}

export interface FeatureImportance {
  feature: string
  importance: number
}

export interface Summary {
  n_participants: number
  n_positive: number | null
  n_negative: number | null
  positive_rate: number | null
}

export interface DistributionBucket {
  key: string
  count: number
  positive_rate: number | null
}

export interface DistributionResponse {
  by: string
  buckets: DistributionBucket[]
}

export type PredictPayload = Record<string, number | null>

export interface PredictResult {
  prediction: number
  label: string
  probability: number
  risk_band: string
  threshold: number
  model_version: string
}

export interface BatchPredictItem {
  prediction: number
  label: string
  probability: number
  risk_band: string
}

export interface BatchPredictResponse {
  n: number
  threshold: number
  model_version: string
  results: BatchPredictItem[]
}

export interface PredictionsResponse {
  total: number
  limit: number
  offset: number
  items: Record<string, number>[]
}
