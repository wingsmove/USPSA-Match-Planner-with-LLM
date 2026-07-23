import type { ChangeEventHandler, HTMLInputTypeAttribute } from "react";

type FormFieldProps = {
  label: string;
  name: string;
  value: string;
  onChange: ChangeEventHandler<HTMLInputElement | HTMLSelectElement>;
  type?: HTMLInputTypeAttribute;
  placeholder?: string;
  className?: string;
  options?: string[]; // 提供 options 时渲染为下拉选择
};

function FormField({
  label,
  name,
  value,
  onChange,
  type = "text",
  placeholder,
  className = "",
  options,
}: FormFieldProps) {
  return (
    <label className={className}>
      {label}
      {options ? (
        <select name={name} value={value} onChange={onChange}>
          {options.map((option) => (
            <option key={option} value={option}>
              {option}
            </option>
          ))}
        </select>
      ) : (
        <input
          name={name}
          value={value}
          onChange={onChange}
          type={type}
          placeholder={placeholder}
        />
      )}
    </label>
  );
}

export default FormField;
