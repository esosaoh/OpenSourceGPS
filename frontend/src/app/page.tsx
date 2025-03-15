"use client";
import { motion } from "framer-motion";
import { useEffect, useState } from "react";
import { useRouter } from 'next/navigation';

export default function Home() {
  const [isMounted, setIsMounted] = useState(false);
  const router = useRouter();

  useEffect(() => {
    setIsMounted(true);
  }, []);

  if (!isMounted) return null;

  const redirectToGitHub = () => {
    window.location.href = "https://github.com/esosaoh/opensourcegps";
  };

  const redirectToSearchPage = () => {
    router.push("/search");
  };

  return (
    <div className="min-h-screen bg-gray-900 flex flex-col items-center justify-center">
      {/* Content */}
      <motion.h1
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.5, delay: 0.2 }}
        className="text-5xl font-bold text-blue-400 mb-4"
      >
        OpenSourceGPS
      </motion.h1>
      <motion.p
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.5, delay: 0.4 }}
        className="text-lg text-blue-400/80 mb-8 text-center max-w-lg"
      >
        Get started with contributing to GitHub repositories effortlessly.
      </motion.p>
      <motion.button
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.5, delay: 0.6 }}
        className="px-6 py-3 bg-blue-500 text-white rounded-lg shadow-lg hover:bg-blue-600 transition-colors"
        onClick={redirectToSearchPage} // Redirect to the new page
      >
        Learn about a Repository
      </motion.button>

      {/* GitHub Button at the Very Bottom */}
      <motion.button
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.5, delay: 0.8 }}
        className="fixed bottom-8 px-6 py-3 bg-gray-700 text-white rounded-lg shadow-lg hover:bg-gray-800 transition-colors"
        onClick={redirectToGitHub}
      >
        Visit GitHub
      </motion.button>
    </div>
  );
}
