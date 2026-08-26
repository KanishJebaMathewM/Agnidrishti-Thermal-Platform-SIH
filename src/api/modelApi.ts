import { fetchApi } from './client'

export interface ModelMetadataResponse {
  version_tag: string
  status: string
  is_active: boolean
  feature_set_version: string
  dataset_version: string
  evaluation_unit: string
  metrics: {
    accuracy: number
    macro_f1: number
    macro_precision: number
    macro_recall: number
  }
  temporal_split: {
    train_years: string
    val_year: number
    test_year: number
    train_unique_observations: number
    train_unique_events: number
    val_unique_observations: number
    val_unique_events: number
    test_unique_observations: number
    test_unique_events: number
  }
  storage_provenance: {
    raw_nasa_archive_files: number
    total_raw_observations: number
    canonical_processed_records: number
    aggregated_physical_events: number
  }
  label_provenance: {
    weak_supervised_pct: number
    human_verified_pct: number
    layer_a_evidence: string
    layer_b_resolution: string
  }
  confusion_matrix: number[][]
  feature_importance: Array<{
    feature: string
    importance: number
    code: string
  }>
  created_at: string
}

export async function getCurrentModel(): Promise<ModelMetadataResponse> {
  return await fetchApi<ModelMetadataResponse>('/model/current')
}
