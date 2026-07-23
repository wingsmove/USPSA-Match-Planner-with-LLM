import type { ReactNode } from "react";

type SectionCardProps = {
  title: ReactNode;
  children: ReactNode;
  eyebrow?: string;
  description?: string;
  className?: string;
};

function SectionCard({
  title,
  children,
  eyebrow,
  description,
  className = "",
}: SectionCardProps) {
  const classes = ["card", className].filter(Boolean).join(" ");

  return (
    <section className={classes}>
      <div className="card-heading">
        <div>
          {eyebrow ? <span className="eyebrow">{eyebrow}</span> : null}
          <h2>{title}</h2>
          {description ? <p>{description}</p> : null}
        </div>
      </div>
      {children}
    </section>
  );
}

export default SectionCard;
