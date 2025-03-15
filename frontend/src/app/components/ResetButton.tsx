interface ResetButtonProps {
  onReset: () => void;
}

export default function ResetButton({ onReset }: ResetButtonProps) {
  return (
    <button
      onClick={onReset}
      className="mt-4 px-4 py-2 bg-gray-700 text-white rounded-lg hover:bg-gray-800 transition-colors"
    >
      Ask Another Question
    </button>
  );
}
