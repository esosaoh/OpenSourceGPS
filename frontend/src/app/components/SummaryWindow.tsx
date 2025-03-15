import { motion } from "framer-motion";
import ResetButton from "./ResetButton";

interface SummaryWindowProps {
  onReset: () => void; // Add onReset prop
}

export default function SummaryWindow({ onReset }: SummaryWindowProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="w-full max-w-2xl bg-gray-900 p-8 rounded-lg shadow-lg text-center border border-gray-800"
    >
      {/* Title */}
      <h2 className="text-3xl font-bold mb-6 bg-gradient-to-r from-blue-500 to-purple-500 bg-clip-text text-transparent">
        Analysis Result
      </h2>

      {/* Summary Content */}
      <div className="text-left mb-8 bg-gray-800 p-5 rounded-lg border border-gray-700">
        <p className="text-gray-300 leading-relaxed">
          This is some preset text which will answer the query.
        </p>
      </div>

      {/* Reset Button */}
      <ResetButton onReset={onReset} />
    </motion.div>
  );
}
