import "./App.css";
import { Routes, Route, Navigate } from "react-router";
import { Toaster } from "@/components/ui/sonner";
import { AllCommunityModule } from "ag-grid-community";
import { AgGridProvider } from "ag-grid-react";
import { AppLayout } from "@/src/components/AppLayout";
import CardsPage from "@/src/pages/Cards";
import UploadRunPage from "@/src/pages/UploadRun";

const gridModules = [AllCommunityModule];

function App() {
  return (
    <>
      <Toaster />
      <AgGridProvider modules={gridModules}>
        <Routes>
          <Route element={<AppLayout />}>
            <Route path="/" element={<Navigate to="/runs" replace />} />
            <Route path="/cards" element={<CardsPage />} />
            <Route path="/runs" element={<UploadRunPage />} />
          </Route>
        </Routes>
      </AgGridProvider>
    </>
  );
}

export default App;
