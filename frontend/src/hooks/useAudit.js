import { useState } from "react";

import { createAudit } from "../services/auditApi";

function getAuditErrorMessage(error) {
  const detail = error.response?.data?.detail;
  if (typeof detail === "string") {
    return detail;
  }
  if (detail && typeof detail.message === "string") {
    return detail.message;
  }
  if (Array.isArray(detail)) {
    return detail[0]?.msg || "Please enter a valid public website URL.";
  }
  if (error.message?.includes("not configured for this deployment")) {
    return error.message;
  }
  if (error.code === "ECONNABORTED") {
    return "The analysis took too long. Try again in a moment.";
  }
  if (!error.response) {
    return "WebPulse could not reach its analysis service. Check that the backend is running and try again.";
  }
  return "WebPulse could not analyze this website. Please try again.";
}

function useAudit() {
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [error, setError] = useState("");

  const analyze = async (url) => {
    setIsAnalyzing(true);
    setError("");

    try {
      const result = await createAudit(url);

      return result.data;
    } catch (error) {
      setError(getAuditErrorMessage(error));
      throw error;
    } finally {
      setIsAnalyzing(false);
    }
  };

  return {
    analyze,
    isAnalyzing,
    error,
    setError,
  };
}

export default useAudit;
