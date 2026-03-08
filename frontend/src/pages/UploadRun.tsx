import { useMemo, useState } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import type { ColDef } from "ag-grid-community";
import { AgGridReact } from "ag-grid-react";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { cardsGridTheme } from "@/src/styles/ag-grid-theme";
import { getRuns, uploadRunFiles } from "@/src/services/runsService";
import type { Run } from "@/src/types/runs";
import { Skeleton } from "@/components/ui/skeleton";

const DEFAULT_COL_DEF: ColDef<Run> = {
  sortable: true,
  filter: true,
  resizable: true,
};

const COLUMN_DEFS: ColDef<Run>[] = [
  {
    headerName: "ID",
    width: 180,
    valueGetter: (params) =>
      params.data ? `${params.data.start_time}_${params.data.seed}` : "",
  },
  {
    field: "character",
    headerName: "Character",
    width: 120,
    valueGetter: (params) =>
      params.data?.character?.replace("CHARACTER.", "") ?? "",
  },
  {
    field: "win",
    headerName: "Result",
    width: 90,
    valueGetter: (params) => (params.data?.win ? "Victory" : "Defeat"),
  },
  { field: "seed", headerName: "Seed", width: 110 },
  {
    field: "run_time",
    headerName: "Time",
    width: 80,
    valueGetter: (params) => {
      const s = params.data?.run_time ?? 0;
      const m = Math.floor(s / 60);
      const sec = s % 60;
      return `${m}:${sec.toString().padStart(2, "0")}`;
    },
  },
  { field: "floor_reached", headerName: "Floor", width: 80 },
  { field: "deck_size", headerName: "Deck", width: 80 },
  { field: "relic_count", headerName: "Relics", width: 80 },
  { field: "bosses_killed", headerName: "Bosses", width: 80 },
  {
    field: "killed_by_encounter",
    headerName: "Killed by",
    flex: 1,
    minWidth: 160,
    valueGetter: (params) => {
      const v = params.data?.killed_by_encounter ?? "";
      return v === "NONE.NONE" ? "" : v.replace("ENCOUNTER.", "");
    },
  },
  {
    field: "start_time",
    headerName: "Date",
    width: 160,
    valueGetter: (params) =>
      params.data?.start_time
        ? new Date(params.data.start_time * 1000).toLocaleString()
        : "",
  },
];

function UploadRunPage() {
  const [files, setFiles] = useState<File[]>([]);
  const [uploading, setUploading] = useState(false);
  const [quickFilterText, setQuickFilterText] = useState("");
  const queryClient = useQueryClient();

  const { data: runs, isLoading } = useQuery({
    queryKey: ["runs"],
    queryFn: () => getRuns(),
  });

  const defaultColDef = useMemo(() => DEFAULT_COL_DEF, []);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const chosen = Array.from(e.target.files ?? []);
    const valid = chosen.filter((f) => f.name.toLowerCase().endsWith(".run"));
    const rejected = chosen.length - valid.length;
    if (rejected > 0) {
      toast.error(`${rejected} file(s) skipped (only .run files are accepted)`);
    }
    setFiles(valid);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (files.length === 0) {
      toast.error("Select one or more .run files first");
      return;
    }
    setUploading(true);
    try {
      const { runs: uploadedRuns, errors: uploadErrors } = await uploadRunFiles(files);
      if (uploadedRuns.length > 0) {
        toast.success(`${uploadedRuns.length} run(s) uploaded`);
      }
      if (uploadErrors.length > 0) {
        const msg = uploadErrors
          .map((e) => `${e.filename}: ${e.detail}`)
          .slice(0, 2)
          .join("; ");
        toast.error(`${uploadErrors.length} failed: ${msg}${uploadErrors.length > 2 ? "…" : ""}`);
      }
      setFiles([]);
      const input = document.getElementById("run-file-input") as HTMLInputElement;
      if (input) input.value = "";
      await queryClient.invalidateQueries({ queryKey: ["runs"] });
    } catch (err: unknown) {
      const message =
        err && typeof err === "object" && "response" in err
          ? (err as { response?: { data?: { detail?: string } } }).response?.data?.detail
          : err instanceof Error
            ? err.message
            : "Upload failed";
      toast.error(String(message));
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="container mx-auto flex flex-col p-6">
      <h1 className="mb-6 text-2xl font-semibold">Upload run</h1>

      <details className="mb-6">
        <summary className="cursor-pointer text-sm font-medium text-muted-foreground hover:text-foreground">
          Where to find run files
        </summary>
        <p className="mt-2 text-sm text-muted-foreground">
          On <strong>Mac (Steam)</strong>:
        </p>
        <code className="mt-1 block break-all rounded bg-muted px-2 py-1.5 font-mono text-xs">
          ~/Library/Application Support/SlayTheSpire2/steam/&lt;steam_id&gt;/profile&lt;n&gt;/saves/history
        </code>
        <p className="mt-2 text-sm text-muted-foreground">
          <code className="rounded bg-muted px-1 font-mono text-xs">Library</code> is hidden in Finder — use Go → Go to Folder (⇧⌘G) and paste the path, or enable “Show Library” in your home folder’s View options.
        </p>
        <p className="mt-4 text-sm text-muted-foreground">
          On <strong>PC (Steam)</strong>:
        </p>
        <code className="mt-1 block break-all rounded bg-muted px-2 py-1.5 font-mono text-xs">
          %APPDATA%\SlayTheSpire2\steam\&lt;steam_id&gt;\profile1\saves\history
        </code>
        <p className="mt-2 text-sm text-muted-foreground">
          AppData is a hidden folder — you may need to enable hidden items in File Explorer.
        </p>
      </details>

      <form onSubmit={handleSubmit} className="flex flex-col gap-4">
        <div className="flex flex-col gap-2">
          <label htmlFor="run-file-input" className="text-sm font-medium">
            Run files
          </label>
          <Input
            id="run-file-input"
            type="file"
            accept=".run"
            multiple
            onChange={handleFileChange}
            disabled={uploading}
            className="cursor-pointer"
          />
          {files.length > 0 && (
            <span className="text-sm text-muted-foreground">
              {files.length} file(s) selected
            </span>
          )}
        </div>
        <Button type="submit" disabled={files.length === 0 || uploading}>
          {uploading ? "Uploading…" : "Upload"}
        </Button>
      </form>

      <h2 className="mb-3 mt-10 text-xl font-semibold">Runs</h2>
      {isLoading ? (
        <Skeleton className="h-[400px] w-full rounded-lg" />
      ) : (
        <>
          <Input
            type="search"
            placeholder="Search runs..."
            value={quickFilterText}
            onChange={(e) => setQuickFilterText(e.target.value)}
            className="mb-3"
          />
          <div className="size-full" style={{ height: 400 }}>
            <AgGridReact<Run>
              theme={cardsGridTheme}
              quickFilterText={quickFilterText}
              rowData={runs ?? []}
              columnDefs={COLUMN_DEFS}
              defaultColDef={defaultColDef}
              getRowId={(params) =>
                `${params.data?.start_time ?? ""}_${params.data?.seed ?? ""}`
              }
            />
          </div>
        </>
      )}
    </div>
  );
}

export default UploadRunPage;
