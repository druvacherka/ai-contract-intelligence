const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ||
  "http://localhost:8000";

export const api = {
  async healthCheck() {
    const response = await fetch(
      `${API_BASE_URL}/health`
    );

    return response.json();
  },

  async uploadContract(file) {
    const formData = new FormData();

    formData.append(
      "file",
      file
    );

    const response = await fetch(
      `${API_BASE_URL}/analyze-file`,
      {
        method: "POST",
        body: formData,
      }
    );

    if (!response.ok) {
      throw new Error(
        "Contract analysis failed"
      );
    }

    return response.json();
  },
};

export default api;