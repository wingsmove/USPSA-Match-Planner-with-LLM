import { useState } from "react";
import "./App.css";
import DashboardTabs, {
  type DashboardPage,
} from "./components/layout/DashboardTabs";
import ClubsPage from "./pages/ClubsPage";
import ScoresPage from "./pages/ScoresPage";

const PAGE_META: Record<
  DashboardPage,
  { label: string; description: string }
> = {
  scores: {
    label: "成绩分析",
    description: "记录比赛结果，查看趋势，将成绩历史转化为有针对性的训练决策。",
  },
  clubs: {
    label: "比赛规划工作空间",
    description: "维护俱乐部列表，并让 AI 教练生成有用的即将举行的比赛选项。",
  },
};

function App() {
  const [page, setPage] = useState<DashboardPage>("scores");
  const pageMeta = PAGE_META[page];

  return (
    <main className="app-shell">
      <header className="hero">
        <div className="hero-copy">
          <span className="eyebrow">USPSA · SQL · AI AGENT</span>
          <h1>USPSA比赛助手</h1>
          <p>
            一个专注于比赛记录、俱乐部研究和 AI 辅助准备的综合工作空间。
          </p>
        </div>
        <div className="hero-mark" aria-hidden="true">
          <span>USPSA</span>
        </div>
      </header>

      <section className="dashboard-frame">
        <div className="dashboard-toolbar">
          <div>
            <span className="eyebrow">{pageMeta.label}</span>
            <p>{pageMeta.description}</p>
          </div>
          <DashboardTabs activePage={page} onChange={setPage} />
        </div>

        <div className="page-content">
          {page === "scores" ? <ScoresPage /> : <ClubsPage />}
        </div>
      </section>

      <footer>
        个人比赛规划工作空间 · 查看建议并训练
      </footer>
    </main>
  );
}

export default App;
