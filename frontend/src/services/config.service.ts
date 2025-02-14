import axios from "axios";

const API_URL = process.env.REACT_APP_API_URL || "http://127.0.0.1:8000";

export class ConfigService {

    constructor() {}
    // TODO
    // public async saveConfiguration(configData: string) {
    //     const response = await axios.post(`${API_URL}/recipes/load-db`, {
    //         method: "POST",
    //         headers: {
    //           "Content-Type": "application/json"
    //         },
    //         // body: JSON.stringify({ query: question })
    //       });
    //       if (response.status != 200) {
    //         throw new Error("Failed to save configuration");
    //       }
    //       const data = await response.data.json();
    // }

    public async runInitialLoad() {
        const response = await axios.post(`${API_URL}/recipes/load-db`)
        if (response.status != 200) {
            throw new Error("Failed to start database initial load");
        }
        return response.data
    }
}