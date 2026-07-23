import { useState } from "react";
import SectionCard from "../ui/SectionCard";

type AgentResultCardProps = {
  title: string;
  description: string;
  actionLabel: string;
  pendingLabel: string;
  errorPrefix: string;
  onRun: () => Promise<string>;
};

function AgentResultCard({
  title,
  description,
  actionLabel,
  pendingLabel,
  errorPrefix,
  onRun,
}: AgentResultCardProps) {
  const [result, setResult] = useState("");
  const [pending, setPending] = useState(false);

  async function run() {
    setPending(true);
    setResult("");

    try {
      setResult(await onRun());
    } catch (error) {
      const message = error instanceof Error ? error.message : String(error);
      setResult(`${errorPrefix}：${message}`);
    } finally {
      setPending(false);
    }
  }

  return (
    <SectionCard
      title={title}
      eyebrow="AI 教练"
      description={description}
      className="agent-card"
    >
      <button className="analyze-button" onClick={run} disabled={pending}>
        {pending ? pendingLabel : actionLabel}
      </button>
      {result ? <pre className="report">{result}</pre> : null}
    </SectionCard>
  );
}

export default AgentResultCard;
