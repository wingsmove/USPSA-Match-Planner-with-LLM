import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import "./index.css";
import App from "./App.tsx";

// getElementById 可能返回 null，用 ! 断言它一定存在（index.html 里有 #root）
createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <title>USPSA小工具</title>
    <App />
  </StrictMode>,
);
