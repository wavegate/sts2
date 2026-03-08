import api from '@/lib/api'
import type { Run } from '@/src/types/runs'

const RUNS_BASE = '/api/runs'

/**
 * List all runs (newest first).
 * GET /api/runs
 */
export async function getRuns(): Promise<Run[]> {
  const res = await api.get<Run[]>(RUNS_BASE)
  return res.data
}

/**
 * Upload a .run file and ingest it into the database.
 * POST /api/runs/upload (multipart/form-data)
 */
export async function uploadRunFile(file: File): Promise<Run> {
  const formData = new FormData()
  formData.append('file', file)
  const res = await api.post<Run>(`${RUNS_BASE}/upload`, formData)
  return res.data
}
