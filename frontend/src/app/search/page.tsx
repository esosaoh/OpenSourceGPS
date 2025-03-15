"use client";

import { useState, useCallback } from "react";
import InputForm from "../components/InputForm";
import SummaryWindow from "../components/SummaryWindow";
import Notification from "../components/Notification";

export default function Search() {
  const [url, setUrl] = useState<string>("");
  const [query, setQuery] = useState<string>("");
  const [showSummary, setShowSummary] = useState<boolean>(false);
  const [showNotification, setShowNotification] = useState<boolean>(false);
  const [notificationMessage, setNotificationMessage] = useState<string>("");

  // Handle form submission
  const handleSubmit = useCallback(() => {
    const trimmedUrl = url.trim();
    const trimmedQuery = query.trim();

    if (!trimmedUrl || !trimmedQuery) {
      setNotificationMessage("Please fill in both the URL and query fields.");
      setShowNotification(true);
      return;
    }

    try {
      new URL(trimmedUrl);
    } catch {
      setNotificationMessage("Please enter a valid URL.");
      setShowNotification(true);
      return;
    }

    setShowSummary(true);
  }, [url, query]);

  // Reset form
  const resetForm = useCallback(() => {
    setQuery("");
    setShowSummary(false);
    setShowNotification(false);
    setNotificationMessage("");
  }, []);

  return (
    <div className="min-h-screen bg-gray-950 text-gray-100 flex flex-col items-center justify-center p-4">
      {/* Input Form */}
      {!showSummary && (
        <InputForm
          url={url}
          setUrl={setUrl}
          query={query}
          setQuery={setQuery}
          onSubmit={handleSubmit}
        />
      )}

      {/* Summary Window */}
      {showSummary && <SummaryWindow onReset={resetForm} />}

      {/* Notification */}
      {showNotification && (
        <Notification
          message={notificationMessage}
          onClose={() => setShowNotification(false)}
        />
      )}
    </div>
  );
}
