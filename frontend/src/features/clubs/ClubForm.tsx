import { useState, type ChangeEvent, type FormEvent } from "react";
import FormField from "../../components/ui/FormField";
import type { ClubCreate } from "./types";

const EMPTY_CLUB: ClubCreate = {
  club_name: "",
  club_url: "",
};

type ClubFormProps = {
  onSubmit: (club: ClubCreate) => Promise<void>;
};

function ClubForm({ onSubmit }: ClubFormProps) {
  const [form, setForm] = useState<ClubCreate>(EMPTY_CLUB);
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
      await onSubmit(form);
      setForm(EMPTY_CLUB);
    } catch {
      alert("提交失败，请检查输入");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="form-flex-row">
      <FormField
        label="俱乐部名称"
        name="club_name"
        value={form.club_name}
        onChange={handleChange}
        placeholder="俱乐部名称"
      />
      <FormField
        label="俱乐部网址"
        name="club_url"
        value={form.club_url}
        onChange={handleChange}
        placeholder="俱乐部网址"
        className="url-label"
      />
      <button type="submit" disabled={submitting}>
        {submitting ? "提交中…" : "提交"}
      </button>
    </form>
  );
}

export default ClubForm;
