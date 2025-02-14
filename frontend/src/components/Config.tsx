import React, { useState, ChangeEvent, FormEvent } from "react";
import { ConfigService } from "../services/config.service";

interface ConfigState {
  openai_api_key: string;
  openai_model_embedding: string;
  openai_criteria_extraction_model: string;
  openai_recipe_ranking_model: string;
  embedding_dim: number;
  milvus_host: string;
  milvus_port: string;
  collection_name: string;
}

const Config: React.FC = () => {
  const [config, setConfig] = useState<ConfigState>({
    openai_api_key: "",
    openai_model_embedding: "text-embedding-3-small",
    openai_criteria_extraction_model: "gpt-4o-mini",
    openai_recipe_ranking_model: "gpt-4o-mini",
    embedding_dim: 1536,
    milvus_host: "127.0.0.1",
    milvus_port: "19530",
    collection_name: "recipes_collection"
  });
  const [message, setMessage] = useState<string>("");

  const configService = new ConfigService()


  const handleChange = (e: ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setConfig((prev) => ({
      ...prev,
      [name]: name === "embedding_dim" ? Number(value) : value
    }));
  };

  const handleSave = (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    localStorage.setItem("fastapiConfig", JSON.stringify(config));
    setMessage("Configuration saved locally.");
  };

  const handleRunDatabaseLoad = async () => {
    setMessage("");
    configService.runInitialLoad()
      .then((data) => setMessage(data?.message || "Database load started."))
      .catch((err) => setMessage("Error: " + err.message))
  };

  return (
    <div className="bg-white shadow rounded-lg p-6">
      <h2 className="text-2xl font-bold mb-4">Configuration</h2>
      <form onSubmit={handleSave} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700">
            OpenAI API Key
          </label>
          <input
            type="text"
            name="openai_api_key"
            value={config.openai_api_key}
            onChange={handleChange}
            placeholder="Enter OpenAI API Key"
            className="mt-1 block w-full p-2 border border-gray-300 rounded-md"
          />
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700">
              OpenAI Embedding Model
            </label>
            <input
              type="text"
              name="openai_model_embedding"
              value={config.openai_model_embedding}
              onChange={handleChange}
              className="mt-1 block w-full p-2 border border-gray-300 rounded-md"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">
              OpenAI Criteria Extraction Model
            </label>
            <input
              type="text"
              name="openai_criteria_extraction_model"
              value={config.openai_criteria_extraction_model}
              onChange={handleChange}
              className="mt-1 block w-full p-2 border border-gray-300 rounded-md"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">
              OpenAI Recipe Ranking Model
            </label>
            <input
              type="text"
              name="openai_recipe_ranking_model"
              value={config.openai_recipe_ranking_model}
              onChange={handleChange}
              className="mt-1 block w-full p-2 border border-gray-300 rounded-md"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">
              Embedding Dimension
            </label>
            <input
              type="number"
              name="embedding_dim"
              value={config.embedding_dim}
              onChange={handleChange}
              className="mt-1 block w-full p-2 border border-gray-300 rounded-md"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">
              Milvus Host
            </label>
            <input
              type="text"
              name="milvus_host"
              value={config.milvus_host}
              onChange={handleChange}
              className="mt-1 block w-full p-2 border border-gray-300 rounded-md"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">
              Milvus Port
            </label>
            <input
              type="text"
              name="milvus_port"
              value={config.milvus_port}
              onChange={handleChange}
              className="mt-1 block w-full p-2 border border-gray-300 rounded-md"
            />
          </div>
          <div className="md:col-span-2">
            <label className="block text-sm font-medium text-gray-700">
              Collection Name
            </label>
            <input
              type="text"
              name="collection_name"
              value={config.collection_name}
              onChange={handleChange}
              className="mt-1 block w-full p-2 border border-gray-300 rounded-md"
            />
          </div>
        </div>
        <div className="flex items-center space-x-4">
          <button
            type="submit"
            className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition-colors"
          >
            Save Configuration
          </button>
          <button
            type="button"
            onClick={handleRunDatabaseLoad}
            className="bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700 transition-colors"
          >
            Run Database Load
          </button>
        </div>
      </form>
      {message && (
        <div className="mt-4 p-4 bg-gray-50 border border-gray-200 rounded text-gray-700">
          {message}
        </div>
      )}
    </div>
  );
};

export default Config;
