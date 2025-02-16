import React, { useState, FormEvent } from "react";
import { ChatService } from "../services/chat.service";

const Chat: React.FC = () => {
  const [question, setQuestion] = useState<string>("");
  const [answer, setAnswer] = useState<string>("");
  const [loading, setLoading] = useState<boolean>(false);

  const chatService = new ChatService()

  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (!question.trim()) return;
    setLoading(true);
    setAnswer("");
    chatService
        .postQuestion(question)
        .then((data) => {
          setAnswer(data?.answer)
        })
        .catch((err) => setAnswer("Error: " + err.message));
    setLoading(false);
  };

  return (
    <div className="bg-white shadow rounded-lg p-6">
      <h2 className="text-2xl font-bold mb-4">Ask a Recipe Question</h2>
      <form onSubmit={handleSubmit}>
        <div className="mb-4">
          <textarea
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="Type your question here..."
            className="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
            rows={4}
            required
          ></textarea>
        </div>
        <button
          type="submit"
          className="bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700 transition-colors"
          disabled={loading}
        >
          {loading ? "Loading..." : "Ask"}
        </button>
      </form>
      {answer && (
        <div className="mt-6 bg-gray-50 p-4 border border-gray-200 rounded">
          <h3 className="font-semibold mb-2">Answer:</h3>
          <p className="text-gray-700 whitespace-pre-line">{answer}</p>
        </div>
      )}
    </div>
  );
};

export default Chat;
