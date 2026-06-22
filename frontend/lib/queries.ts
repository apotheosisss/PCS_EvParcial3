"use client"

import { useQuery } from "@tanstack/react-query"

import { api } from "@/lib/api"

export const useHealth = () =>
  useQuery({ queryKey: ["health"], queryFn: api.health, refetchInterval: 30_000 })

export const useModelInfo = () =>
  useQuery({ queryKey: ["model-info"], queryFn: api.modelInfo })

export const useFeatures = () =>
  useQuery({ queryKey: ["features"], queryFn: api.features })

export const useThresholds = () =>
  useQuery({ queryKey: ["thresholds"], queryFn: api.thresholds })

export const useMetrics = () =>
  useQuery({ queryKey: ["metrics"], queryFn: api.metrics })

export const useCurves = () =>
  useQuery({ queryKey: ["curves"], queryFn: api.curves })

export const useModelComparison = () =>
  useQuery({ queryKey: ["model-comparison"], queryFn: api.modelComparison })

export const useConfusionMatrix = () =>
  useQuery({ queryKey: ["confusion-matrix"], queryFn: api.confusionMatrix })

export const useFeatureImportance = (top = 15) =>
  useQuery({ queryKey: ["feature-importance", top], queryFn: () => api.featureImportance(top) })

export const useSummary = () =>
  useQuery({ queryKey: ["summary"], queryFn: api.summary })

export const useDistribution = (by: string) =>
  useQuery({ queryKey: ["distribution", by], queryFn: () => api.distribution(by) })

export const usePredictions = (limit: number, offset: number) =>
  useQuery({ queryKey: ["predictions", limit, offset], queryFn: () => api.predictions(limit, offset) })
