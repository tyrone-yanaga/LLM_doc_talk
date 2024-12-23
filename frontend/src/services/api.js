import axios from "axios";

const API_BASE_URL = "http://127.0.0.1:8000"; // Update to your backend's URL

export const askQuestion = async (/** @type {String} */ question) => {
  try {
    const response = await axios.post(`${API_BASE_URL}/questions`, {
      question,
    });
    return response.data;
  } catch (error) {
    console.error("Error in axios call:", error);
    console.error(error);
    
    throw error;
  }
};