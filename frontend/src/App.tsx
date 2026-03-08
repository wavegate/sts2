import "./App.css";
import { Routes, Route, Navigate } from "react-router";
import { Toaster } from "@/components/ui/sonner";
import { AllCommunityModule } from "ag-grid-community";
import { AgGridProvider } from "ag-grid-react";
import CardsPage from "@/src/pages/Cards";

const gridModules = [AllCommunityModule];

function App() {
  return (
    <>
      <Toaster />
      <AgGridProvider modules={gridModules}>
        <Routes>
          <Route path="/" element={<Navigate to="/cards" replace />} />
          <Route path="/cards" element={<CardsPage />} />
        </Routes>
      </AgGridProvider>
    </>
  );
}

export default App;
