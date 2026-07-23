import { request } from "../api";
import AgentResultCard from "../components/ai/AgentResultCard";
import SectionCard from "../components/ui/SectionCard";
import ClubForm from "../features/clubs/ClubForm";
import ClubTable from "../features/clubs/ClubTable";
import type { Club, ClubCreate } from "../features/clubs/types";
import useCrudCollection from "../hooks/useCrudCollection";

function ClubsPage() {
  const { items, loading, error, create, remove } = useCrudCollection<
    Club,
    ClubCreate
  >("/clubs");

  async function addClub(club: ClubCreate) {
    await create(club);
  }

  async function deleteClub(id: number) {
    try {
      await remove(id);
    } catch {
      alert("删除失败，请稍后重试");
    }
  }

  return (
    <>
      <SectionCard
        title="新增俱乐部"
        eyebrow="想好要去哪个俱乐部了吗？"
        description="保存可信的俱乐部名称和网址，作为后续比赛规划的数据来源。"
      >
        <ClubForm onSubmit={addClub} />
      </SectionCard>
      <SectionCard
        title={`俱乐部列表${loading ? "（加载中…）" : ""}`}
        eyebrow="这里都保存了哪些俱乐部？"
        description="集中维护经常关注的俱乐部，保持规划输入清晰可查。"
      >
        {error ? <p className="error-message">{error}</p> : null}
        <ClubTable clubs={items} onDelete={deleteClub} />
      </SectionCard>
      <AgentResultCard
        title="LLM 比赛规划"
        description="根据俱乐部列表查找即将举行的比赛，并让 AI 教练生成可复核的参赛规划。"
        actionLabel="开始规划"
        pendingLabel="规划中，请稍候…"
        errorPrefix="规划失败"
        onRun={async () => {
          const result = await request<{ plan?: string }>("/plan", {
            method: "POST",
          });
          return result.plan ?? "";
        }}
      />
    </>
  );
}

export default ClubsPage;
