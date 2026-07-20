// 成绩看板页：新增成绩 + 展示/删除历史成绩。

import { useEffect, useState } from "react";
import { API, type Score } from "../api";

// 表单的结构：输入框的值都是字符串，提交时再转成数字
type ScoreForm = {
  percent: string;
  points: string;
  time: string;
  percent_possible: string;
  division: string;
  shooter_class: string;
  power_factor: string;
  hits_a: string;
  hits_c: string;
  hits_d: string;
  misses_m: string;
  nopenaltymisses_npm: string;
  no_shoots: string;
  procedurals: string;
  additional_penalties_apen: string;
};

const EMPTY_FORM: ScoreForm = {
  percent: "",
  points: "",
  time: "",
  percent_possible: "",
  division: "CO",
  shooter_class: "C",
  power_factor: "MINOR",
  hits_a: "0",
  hits_c: "0",
  hits_d: "0",
  misses_m: "0",
  nopenaltymisses_npm: "0",
  no_shoots: "0",
  procedurals: "0",
  additional_penalties_apen: "0",
};

function ScoresPage() {
  const [scores, setScores] = useState<Score[]>([]);
  const [form, setForm] = useState<ScoreForm>(EMPTY_FORM);
  const [loading, setLoading] = useState<boolean>(false);
  const [report, setReport] = useState<string>("");         // 成绩分析结果
  const [analyzing, setAnalyzing] = useState<boolean>(false); // 是否正在分析

  async function loadScores() {
    setLoading(true);
    try {
      const res = await fetch(`${API}/scores`);
      const data: Score[] = await res.json();
      setScores(data);
    } catch (err) {
      console.error("加载失败：", err);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadScores();
  }, []);

  function handleChange(e: React.ChangeEvent<HTMLInputElement>) {
    const { name, value } = e.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  }

  async function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const payload = {
      ...form,
      hits_a: Number(form.hits_a),
      hits_c: Number(form.hits_c),
      hits_d: Number(form.hits_d),
      misses_m: Number(form.misses_m),
      nopenaltymisses_npm: Number(form.nopenaltymisses_npm),
      no_shoots: Number(form.no_shoots),
      procedurals: Number(form.procedurals),
      additional_penalties_apen: Number(form.additional_penalties_apen),
    };
    const res = await fetch(`${API}/scores`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    if (res.ok) {
      setForm(EMPTY_FORM);
      loadScores();
    } else {
      alert("提交失败，请检查输入");
    }
  }

  async function handleDelete(id: number) {
    const res = await fetch(`${API}/scores/${id}`, { method: "DELETE" });
    if (res.ok) {
      loadScores();
    } else {
      alert("删除失败，请检查输入");
    }
  }

  // 成绩分析：调用 /analyze，让 AI 教练根据数据库成绩生成报告
  async function analyze() {
    setAnalyzing(true);
    setReport("");
    try {
      const res = await fetch(`${API}/analyze`, { method: "POST" });
      const data = await res.json();
      if (res.ok) {
        setReport(data.report ?? "");
      } else {
        setReport(`分析失败：${data.detail ?? res.status}`);
      }
    } catch (err) {
      setReport(`请求失败：${err}`);
    } finally {
      setAnalyzing(false);
    }
  }

  return (
    <>
      <section className="card">
        <h2>新增成绩</h2>
        <form onSubmit={handleSubmit} className="form-grid">
          <label>% <input name="percent" value={form.percent} onChange={handleChange} placeholder="48.32%" /></label>
          <label>Pts <input name="points" value={form.points} onChange={handleChange} placeholder="289.1217" /></label>
          <label>Time <input name="time" value={form.time} onChange={handleChange} placeholder="196.59" /></label>
          <label>% psbl <input name="percent_possible" value={form.percent_possible} onChange={handleChange} placeholder="42.30%" /></label>
          <label>Div <input name="division" value={form.division} onChange={handleChange} /></label>
          <label>Class <input name="shooter_class" value={form.shooter_class} onChange={handleChange} /></label>
          <label>PF <input name="power_factor" value={form.power_factor} onChange={handleChange} /></label>
          <label>A <input name="hits_a" type="number" value={form.hits_a} onChange={handleChange} /></label>
          <label>C <input name="hits_c" type="number" value={form.hits_c} onChange={handleChange} /></label>
          <label>D <input name="hits_d" type="number" value={form.hits_d} onChange={handleChange} /></label>
          <label>M <input name="misses_m" type="number" value={form.misses_m} onChange={handleChange} /></label>
          <label>NPM <input name="nopenaltymisses_npm" type="number" value={form.nopenaltymisses_npm} onChange={handleChange} /></label>
          <label>NS <input name="no_shoots" type="number" value={form.no_shoots} onChange={handleChange} /></label>
          <label>Proc <input name="procedurals" type="number" value={form.procedurals} onChange={handleChange} /></label>
          <label>APen <input name="additional_penalties_apen" type="number" value={form.additional_penalties_apen} onChange={handleChange} /></label>
          <button type="submit">提交</button>
        </form>
      </section>

      <section className="card">
        <h2>历史成绩 {loading && "（加载中…）"}</h2>
        {scores.length === 0 ? (
          <p>暂无成绩，先在上方新增一条吧。</p>
        ) : (
          <table>
            <thead>
              <tr>
                <th>提交时间</th><th>%</th><th>Div</th><th>Class</th><th>PF</th>
                <th>A</th><th>C</th><th>D</th><th>M</th><th>NPM</th><th>NS</th><th>Proc</th><th>APen</th><th></th>
              </tr>
            </thead>
            <tbody>
              {scores.map((s) => (
                <tr key={s.id}>
                  <td>{new Date(s.created_at).toLocaleString()}</td>
                  <td>{s.percent}</td>
                  <td>{s.division}</td>
                  <td>{s.shooter_class}</td>
                  <td>{s.power_factor}</td>
                  <td>{s.hits_a}</td>
                  <td>{s.hits_c}</td>
                  <td>{s.hits_d}</td>
                  <td>{s.misses_m}</td>
                  <td>{s.nopenaltymisses_npm}</td>
                  <td>{s.no_shoots}</td>
                  <td>{s.procedurals}</td>
                  <td>{s.additional_penalties_apen}</td>
                  <td><button onClick={() => handleDelete(s.id)} className="delete-button">删除</button></td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </section>

      <section className="analyze-card">
        <h2>LLM 成绩分析</h2>
        <p>点击下方按钮，让 AI 教练根据数据库中已有的成绩，生成表现评价与训练建议。</p>
        <button className="analyze-button" onClick={analyze} disabled={analyzing}>
          {analyzing ? "分析中，请稍候…" : "开始分析"}
        </button>
        {report && <pre className="report">{report}</pre>}
      </section>
    </>
  );
}

export default ScoresPage;
