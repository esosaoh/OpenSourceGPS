import { motion } from "framer-motion";
import { FormEvent } from "react";
import InputField from "./InputField";

interface InputFormProps {
  url: string;
  setUrl: (url: string) => void;
  query: string;
  setQuery: (query: string) => void;
  onSubmit: () => void;
  loading: boolean; // Add loading prop
}

export default function InputForm({ url, setUrl, query, setQuery, onSubmit, loading }: InputFormProps) {
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
          isTextArea
          rows={8}
        />

        {/* Submit Button */}
        <button
          type="submit"
          disabled={loading} // Disable button while loading
          className={`w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed`}
        >
          {loading ? (
            <div className="flex items-center justify-center">
              <svg
                className="animate-spin h-5 w-5 mr-3 text-white"
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
              >
                <circle
                  className="opacity-25"
                  cx="12"
                  cy="12"
                  r="10"
                  stroke="currentColor"
                  strokeWidth="4"
                ></circle>
                <path
                  className="opacity-75"
                  fill="currentColor"
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                ></path>
              </svg>
              Processing...
            </div>
          ) : (
            "Answer"
          )}
        </button>
      </form>
    </motion.div>
  );
}