import { motion } from "framer-motion";
import ResetButton from "./ResetButton";

interface SummaryWindowProps {
  onReset: () => void;
  content: string;
}

export default function SummaryWindow({ onReset, content }: SummaryWindowProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="w-full max-w-2xl bg-gray-900 p-8 rounded-lg shadow-lg flex flex-col"
    >
      {/* Header */}
      <div className="text-center mb-4">
        <h2 className="text-2xl font-bold text-white">
          Analysis Result
        </h2>
      </div>

      {/* Content */}
      <div className="text-left flex-grow mb-4 bg-gray-800 p-5 rounded-lg border border-gray-700">
        <p className="text-gray-400 leading-relaxed">
          {content}
        </p>
      </div>

      {/* Footer */}
      <div className="flex justify-center">
        <ResetButton 
          onReset={onReset} 
          className="w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50"
        />
      </div>
    </motion.div>
  );
}
