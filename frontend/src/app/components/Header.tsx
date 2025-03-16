import Image from 'next/image'; // Import Image from Next.js

export default function Header() {
  return (
    <header className="flex items-center justify-between p-4 bg-gray-800">
      <Image src="/branch.svg" alt="Logo" width={100} height={40} />
    </header>
  );
} 