import { useState } from "react";
import "./App.css";
import Home from "./pages/Home";
import { ThemeProvider } from "@/components/theme-provider";
import { SidebarProvider, SidebarTrigger } from "@/components/ui/sidebar"
import { AppSidebar } from "@/components/app-sidebar"


function App() {
  return (
    <>
      <ThemeProvider defaultTheme="dark" storageKey="vite-ui-theme">
        <Home  />
      </ThemeProvider>
    </>
  );
}

export default App;
