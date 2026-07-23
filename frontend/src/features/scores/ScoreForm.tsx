import { useState, type ChangeEvent, type FormEvent } from "react";
import FormField from "../../components/ui/FormField";
import {
  EMPTY_SCORE_FORM,
  SCORE_FIELDS,
  toScoreCreate,
} from "./scoreFormConfig";
import type { ScoreCreate, ScoreFormValues } from "./types";

type ScoreFormProps = {
  onSubmit: (score: ScoreCreate) => Promise<void>;
};

function ScoreForm({ onSubmit }: ScoreFormProps) {
  const [form, setForm] = useState<ScoreFormValues>(EMPTY_SCORE_FORM);
  const [submitting, setSubmitting] = useState(false);

  function handleChange(
    event: ChangeEvent<HTMLInputElement | HTMLSelectElement>,
  ) {
    const { name, value } = event.target;
    setForm((current) => ({ ...current, [name]: value }));
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSubmitting(true);
    try {
      await onSubmit(toScoreCreate(form));
      setForm(EMPTY_SCORE_FORM);
    } catch {
      alert("提交失败，请检查输入");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="form-grid">
      {SCORE_FIELDS.map((field) => (
        <FormField
          key={field.name}
          label={field.label}
          name={field.name}
          value={form[field.name]}
          onChange={handleChange}
          type={field.type}
          placeholder={field.placeholder}
          options={field.options}
        />
      ))}
      <button type="submit" disabled={submitting}>
        {submitting ? "提交中…" : "提交"}
      </button>
    </form>
  );
}

export default ScoreForm;
