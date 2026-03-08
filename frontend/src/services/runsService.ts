import api from "@/lib/api";
import type { Run } from "@/src/types/runs";

const RUNS_BASE = "/api/runs";

/**
 * List all runs (newest first).
 * GET /api/runs
 */
export async function getRuns(): Promise<Run[]> {
  const res = await api.get<Run[]>(RUNS_BASE);
  return res.data;
}

/** Response from POST /api/runs/upload (batch) */
export interface UploadRunsResponse {
  runs: Run[];
  errors: { filename: string; detail: string }[];
}

/**
 * Upload one or more .run files in a single request.
 * POST /api/runs/upload (multipart/form-data, multiple "files")
 */
export async function uploadRunFiles(
  files: File[],
): Promise<UploadRunsResponse> {
  const formData = new FormData();
  for (const file of files) {
    formData.append("files", file);
  }
  const res = await api.post<UploadRunsResponse>(
    `${RUNS_BASE}/upload`,
    formData,
  );
  return res.data;
}
