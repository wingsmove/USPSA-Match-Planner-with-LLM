// 前端共享的 API 配置与数据类型。

// 后端地址（FastAPI 默认跑在 8000 端口）
export const API = "http://127.0.0.1:8000";

// 后端返回的成绩结构（对应 schemas.ScoreRead）
export interface Score {
  id: number;
  percent: string;
  points: string;
  time: string;
  percent_possible: string;
  division: string;
  shooter_class: string;
  power_factor: string;
  hits_a: number;
  hits_c: number;
  hits_d: number;
  misses_m: number;
  nopenaltymisses_npm: number;
  no_shoots: number;
  procedurals: number;
  additional_penalties_apen: number;
  created_at: string;
}
