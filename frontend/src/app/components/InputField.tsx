interface InputFieldProps {
  label: string;
  value: string;
  onChange: (value: string) => void;
  placeholder: string;
}

export default function InputField({ label, value, onChange, placeholder }: InputFieldProps) {
  return (
    <div className="space-y-2">
      <label className="text-sm text-gray-400">{label}</label>
      <input
        type="text"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        className="w-full p-2 bg-gray-900 rounded-lg border border-gray-800 focus:outline-none"
      />
    </div>
  );
}

