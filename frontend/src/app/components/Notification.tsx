"use client";

import { motion } from "framer-motion";

interface NotificationProps {
  message: string;
  onClose: () => void;
}

export default function Notification({ message, onClose }: NotificationProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: -50 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -50 }}
      transition={{ duration: 0.3 }}
      className="fixed top-4 left-1/2 transform -translate-x-1/2 bg-yellow-400 text-yellow-900 p-4 rounded-lg shadow-lg flex items-center justify-between w-full max-w-md"
    >
      <span>{message}</span>
      <button
        onClick={onClose}
        className="ml-4 hover:opacity-80 focus:outline-none"
      >
        ✕
      </button>
    </motion.div>
  );
}
