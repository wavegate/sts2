import { useMemo, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import type { ColDef } from "ag-grid-community";
import { AgGridReact } from "ag-grid-react";
import { cardsGridTheme } from "@/src/styles/ag-grid-theme";
import { getCards } from "@/src/services/cardsService";
import type { Card } from "@/src/types/cards";
import { Input } from "@/components/ui/input";
import { Skeleton } from "@/components/ui/skeleton";

const DEFAULT_COL_DEF: ColDef<Card> = {
  sortable: true,
  filter: true,
  resizable: true,
};

const COLUMN_DEFS: ColDef<Card>[] = [
  { field: "id", headerName: "ID", width: 140 },
  { field: "name", headerName: "Name", flex: 1, minWidth: 160 },
  { field: "type", headerName: "Type", width: 100 },
  { field: "rarity", headerName: "Rarity", width: 100 },
  { field: "color", headerName: "Color", width: 100 },
  { field: "cost", headerName: "Cost", width: 80 },
  {
    field: "description",
    headerName: "Description",
    flex: 2,
    minWidth: 200,
    wrapText: true,
    autoHeight: true,
    valueGetter: (params) =>
      params.data?.description?.replace(/\[.*?\]/g, "").trim() ?? "",
  },
];

function CardsPage() {
  const [quickFilterText, setQuickFilterText] = useState("");
  const { data: cards, isLoading } = useQuery({
    queryKey: ["cards"],
    queryFn: () => getCards(),
  });

  const defaultColDef = useMemo(() => DEFAULT_COL_DEF, []);

  return (
    <div className="container mx-auto flex flex-col p-6">
      <h1 className="mb-6 text-2xl font-semibold">Cards</h1>
      {isLoading ? (
        <Skeleton className="h-[500px] w-full rounded-lg" />
      ) : (
        <>
          <Input
            type="search"
            placeholder="Search cards..."
            value={quickFilterText}
            onChange={(e) => setQuickFilterText(e.target.value)}
            className="mb-3 max-w-sm"
          />
          <div className="size-full" style={{ height: 500 }}>
            <AgGridReact<Card>
              theme={cardsGridTheme}
              quickFilterText={quickFilterText}
              rowData={cards ?? []}
              columnDefs={COLUMN_DEFS}
              defaultColDef={defaultColDef}
              getRowId={(params) => params.data.id}
            />
          </div>
        </>
      )}
    </div>
  );
}

export default CardsPage;
