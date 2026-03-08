import { useMemo, useState } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import type { ColDef } from "ag-grid-community";
import { AgGridReact } from "ag-grid-react";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { cardsGridTheme } from "@/src/styles/ag-grid-theme";
import { getRuns, uploadRunFile } from "@/src/services/runsService";
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
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [quickFilterText, setQuickFilterText] = useState("");
  const queryClient = useQueryClient();

  const { data: runs, isLoading } = useQuery({
    queryKey: ["runs"],
    queryFn: () => getRuns(),
  });

  const defaultColDef = useMemo(() => DEFAULT_COL_DEF, []);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const chosen = e.target.files?.[0];
    if (chosen) {
      if (!chosen.name.toLowerCase().endsWith(".run")) {
        toast.error("Please select a .run file");
        setFile(null);
        return;
      }
      setFile(chosen);
    } else {
      setFile(null);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) {
      toast.error("Select a .run file first");
      return;
    }
    if (!file.name.toLowerCase().endsWith(".run")) {
      toast.error("Only .run files are accepted");
      return;
    }
    setUploading(true);
    try {
      const run = await uploadRunFile(file);
      const char = run.character.replace("CHARACTER.", "");
      toast.success(
        `Run ingested: ${char}, ${run.win ? "Victory" : "Defeat"} (floor ${run.floor_reached})`,
      );
      setFile(null);
      const input = document.getElementById(
        "run-file-input",
      ) as HTMLInputElement;
      if (input) input.value = "";
      await queryClient.invalidateQueries({ queryKey: ["runs"] });
    } catch (err: unknown) {
      const message =
        err && typeof err === "object" && "response" in err
          ? (err as { response?: { data?: { detail?: string } } }).response
              ?.data?.detail
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
      <form onSubmit={handleSubmit} className="flex flex-col gap-4">
        <div className="flex flex-col gap-2">
          <label htmlFor="run-file-input" className="text-sm font-medium">
            Run file
          </label>
          <Input
            id="run-file-input"
            type="file"
            accept=".run"
            onChange={handleFileChange}
            disabled={uploading}
            className="cursor-pointer"
          />
          {file && (
            <span className="text-sm text-muted-foreground">{file.name}</span>
          )}
        </div>
        <Button type="submit" disabled={!file || uploading}>
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
            className="mb-3 max-w-sm"
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
