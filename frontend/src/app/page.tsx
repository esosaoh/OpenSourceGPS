"use client";
import { motion } from "framer-motion";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { ArrowRight, Star } from "lucide-react"; // Import icons

export default function Home() {
  const [isMounted, setIsMounted] = useState(false);
  const router = useRouter();

  useEffect(() => {
    setIsMounted(true);
  }, []);

  if (!isMounted) return null;

  const redirectToGitHub = () => {
    window.location.href = "https://github.com/esosaoh/gitmentor";
  };

  const redirectToSearchPage = () => {
    router.push("/search");
  };

  return (
    <div className="min-h-screen bg-gray-900 flex flex-col items-center justify-center">
      {/* Content */}
      <motion.h1
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8 }}
        className="text-5xl font-bold text-blue-400 mb-4"
      >
        GitMentor
      </motion.h1>
      <motion.p
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8, delay: 0.2 }}
        className="text-lg text-blue-400/80 mb-8 text-center max-w-lg"
      >
        Effortlessly contribute to open source repositories with AI-driven guidance.
      </motion.p>

      {/* Start Contributing Button */}
      <motion.button
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.8, delay: 0.4 }}
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.95 }}
        className="flex items-center justify-center px-6 py-3 bg-blue-500 text-white rounded-lg shadow-lg hover:bg-blue-600 transition-colors"
        onClick={redirectToSearchPage}
      >
        Start Contributing
        <ArrowRight className="ml-2 h-5 w-5" />
      </motion.button>

      {/* Star Us on GitHub Button */}
      <motion.button
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.8, delay: 0.6 }}
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.95 }}
        className="fixed bottom-8 flex items-center justify-center px-6 py-3 bg-gray-700 text-white rounded-lg shadow-lg hover:bg-gray-800 transition-colors"
        onClick={redirectToGitHub}
      >
        Star Us on GitHub
        <Star className="ml-2 h-5 w-5" />
      </motion.button>
    </div>
  );
}