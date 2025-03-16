import { motion, FormEvent } from "framer-motion";
import InputField from "./InputField";

interface InputFormProps {
  url: string;
  setUrl: (url: string) => void;
  query: string;
  setQuery: (query: string) => void;
  onSubmit: () => void;
}

export default function InputForm({ url, setUrl, query, setQuery, onSubmit }: InputFormProps) {
  // Handle form submission
  const handleSubmit = (e: FormEvent) => {
    e.preventDefault(); // Prevent page reload
    onSubmit(); // Call the onSubmit function
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="w-full max-w-2xl space-y-4"
    >
      {/* Title and Description */}
      <div className="text-center">
        <h1 className="text-2xl font-bold mb-2">Welcome</h1>
        <p className="text-gray-400">Start by providing a repository URL and a query.</p>
      </div>

      {/* Form */}
      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Input Fields */}
        <InputField
          label="GitHub Repository link"
          value={url}
          onChange={setUrl}
          placeholder="https://www.github.com/user/repo"
        />
        <InputField
          label="Query"
          value={query}
          onChange={setQuery}
          placeholder="How can I...?"
        />

        {/* Submit Button */}
        <button
          type="submit" // Make this button submit the form
          className="w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 hover:cursor-pointer hover:bg-sky-700"
        >
          Answer
        </button>
      </form>
    </motion.div>
  );
}
