import axios from "axios";

const API_URL = process.env.REACT_APP_API_URL || "http://127.0.0.1:8000";

export class ChatService {

    constructor() {}
  
    public async postQuestion(question: string) {
        const response = await axios.post(`${API_URL}/recipes/query`, {query: question});
        if (response.status != 200) {
          throw new Error("Failed to fetch answer");
        }
        return response.data;
    }
}