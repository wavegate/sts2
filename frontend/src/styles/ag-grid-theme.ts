/**
 * AG Grid theme: light palette with warm amber accent.
 * Use on any grid via theme={cardsGridTheme}.
 */
import { themeBalham } from "ag-grid-community";

export const cardsGridTheme = themeBalham.withParams({
  backgroundColor: "#fafaf9",
  foregroundColor: "#1c1917",
  accentColor: "#d4a84b",
  chromeBackgroundColor: "#f5f5f4",
  headerBackgroundColor: "#f5f5f4",
  dataBackgroundColor: "#ffffff",
  headerTextColor: "#1c1917",
  cellTextColor: "#44403c",
  borderColor: "rgba(0, 0, 0, 0.08)",
  spacing: 8,
});
