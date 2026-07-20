// 应用外壳：顶部标签导航 + 根据当前页切换内容。
//
// 这里用一个 page 状态来记录"当前在哪一页"，点击标签就切换。
// （这是最简单的多页做法；更正式的多 URL 方案是 React Router，可后续升级。）

import { useState } from "react";
import "./App.css";
import ScoresPage from "./pages/ScoresPage";
import ClubsPage from "./pages/ClubsPage";
type Page = "scores" | "clubs";

function App() {
  const [page, setPage] = useState<Page>("scores" );

  function renderPage() {
    switch (page) {
      case "scores":
        return <ScoresPage />;
      case "clubs":
        return <ClubsPage />;
    }
  }

  return (
    <div className="container">
      <h1>USPSA 成绩看板</h1>

      <nav className="tabs">
        <button
          className={page === "scores" ? "tab active" : "tab"}
          onClick={() => setPage("scores")}
        >
          成绩看板
        </button>
        <button
          className={page === "clubs" ? "tab active" : "tab"}
          onClick={() => setPage("clubs")}
        >
          俱乐部看板
        </button>
      </nav>
      {renderPage()}
    </div>
  );
}

export default App;
