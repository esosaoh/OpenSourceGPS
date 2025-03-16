import { motion } from "framer-motion";
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
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
          GitMentor
        </h2>
      </div>

      {/* Content */}
      <div className="text-left flex-grow mb-4 bg-gray-800 p-5 rounded-lg border border-gray-700 overflow-auto">
        <ReactMarkdown 
          remarkPlugins={[remarkGfm]}
          components={{
            p: ({node, ...props}) => <p className="text-gray-400 leading-relaxed mb-4" {...props} />,
            h1: ({node, ...props}) => <h1 className="text-xl font-bold text-white mb-3" {...props} />,
            h2: ({node, ...props}) => <h2 className="text-lg font-semibold text-white mb-2" {...props} />,
            ul: ({node, ...props}) => <ul className="list-disc list-inside text-gray-400 mb-4" {...props} />,
            ol: ({node, ...props}) => <ol className="list-decimal list-inside text-gray-400 mb-4" {...props} />,
            li: ({node, ...props}) => <li className="mb-1" {...props} />,
            a: ({node, ...props}) => <a className="text-blue-400 hover:underline" {...props} />,
            code: ({ node, inline, className, children, ...props }) => {
              const match = /language-(\w+)/.exec(className || '');
              return !inline ? (
                <pre className="bg-gray-700 p-3 rounded text-sm overflow-auto">
                  <code className={`language-${match?.[1] || 'plaintext'}`} {...props}>
                    {children}
                  </code>
                </pre>
              ) : (
                <code className="bg-gray-700 px-1 py-0.5 rounded text-sm" {...props}>
                  {children}
                </code>
              );
            },            
          }}
        >
          {content}
        </ReactMarkdown>
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
