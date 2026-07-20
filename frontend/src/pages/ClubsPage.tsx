// 俱乐部看板页：新增俱乐部 + 展示/删除俱乐部。

import { useEffect, useState } from "react";
import { API } from "../api";

// 俱乐部表单的结构
type ClubForm = {
  id: number;
  club_name: string;
  club_url: string;
};

const EMPTY_FORM: ClubForm = {
  id: 0,
  club_name: "",
  club_url: "",
};

function ClubsPage() {
  const [clubs, setClubs] = useState<ClubForm[]>([]);
  const [form, setForm] = useState<ClubForm>(EMPTY_FORM);
  const [loading, setLoading] = useState<boolean>(false);
  const [plan, setPlan] = useState<string>("");        // 比赛规划结果
  const [planning, setPlanning] = useState<boolean>(false); // 是否正在规划

  async function loadClubs() {
    setLoading(true);
    try {
      const res = await fetch(`${API}/clubs`);
      const data: ClubForm[] = await res.json();
      setClubs(data);
    } catch (err) {
      console.error("加载失败：", err);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadClubs();
  }, []);

  function handleChange(e: React.ChangeEvent<HTMLInputElement>) {
    const { name, value } = e.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  }

  async function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const payload = form;
    const res = await fetch(`${API}/clubs`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    if (res.ok) {
      setForm(EMPTY_FORM);
      loadClubs();
    } else {
      alert("提交失败，请检查输入");
    }
  }

  async function handleDelete(id: number) {
    const res = await fetch(`${API}/clubs/${id}`, { method: "DELETE" });
    if (res.ok) {
      loadClubs();
    } else {
      alert("删除失败，请检查输入");
    }
  }

  // 生成比赛规划：调用 /plan（会实时爬取 + 调用大模型，较慢）
  async function generatePlan() {
    setPlanning(true);
    setPlan("");
    try {
      const res = await fetch(`${API}/plan`, { method: "POST" });
      const data = await res.json();
      if (res.ok) {
        setPlan(data.plan ?? "");
      } else {
        setPlan(`规划失败：${data.detail ?? res.status}`);
      }
    } catch (err) {
      setPlan(`请求失败：${err}`);
    } finally {
      setPlanning(false);
    }
  }

  return (
    <>
      <section className="card">
        <h2>新增俱乐部</h2>
        <form onSubmit={handleSubmit} className="form-flex-row">
          <label>Club Name <input name="club_name" value={form.club_name} onChange={handleChange} className="club-name-input" placeholder="Club Name" /></label>
          <label className="url-label">Club URL <input name="club_url" value={form.club_url} onChange={handleChange} className="url-input" placeholder="Club URL" /></label>
          <button type="submit">提交</button>
        </form>
      </section>

      <section className="card">
        <h2>俱乐部列表 {loading && "（加载中…）"}</h2>
        {clubs.length === 0 ? (
          <p>暂无俱乐部，先在上方新增一条吧。</p>
        ) : (
          <table>
            <thead>
              <tr>
                <th>Club Name</th><th>Club URL</th><th></th>
              </tr>
            </thead>
            <tbody>
              {clubs.map((c) => (
                <tr key={c.id}>
                  <td>{c.club_name}</td>
                  <td>{c.club_url}</td>
                  <td><button onClick={() => handleDelete(c.id)} className="delete-button">删除</button></td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </section>

      <section className="analyze-card">
        <h2>LLM 比赛规划</h2>
        <p>根据上面的俱乐部，实时抓取即将进行的比赛，让 AI 教练生成参赛规划（较慢，请耐心等待）。</p>
        <button className="analyze-button" onClick={generatePlan} disabled={planning}>
          {planning ? "规划中，请稍候…" : "开始规划"}
        </button>
        {plan && <pre className="report">{plan}</pre>}
      </section>
    </>
  );
}

export default ClubsPage;
