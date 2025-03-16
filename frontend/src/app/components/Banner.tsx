"use client";
import { motion } from "framer-motion";
import { useRouter } from "next/navigation";
import Image from "next/image";

export default function Banner() {
  const router = useRouter();

  const redirectToHome = () => {
    router.push("/");
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="fixed top-0 left-0 right-0 bg-gray-800/50 backdrop-blur-md p-4 flex items-center justify-center cursor-pointer hover:bg-gray-800/70 transition-colors"
      onClick={redirectToHome}
    >
      <div className="flex items-center space-x-2">
        <Image
          src="/branch.svg"
          alt="GitMentor Logo"
          width={24}
          height={24}
          className="h-6 w-6"
        />
        <span className="text-lg font-semibold text-blue-400">gitmentor.co</span>
      </div>
    </motion.div>
  );
}