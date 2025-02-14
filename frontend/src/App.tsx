import React from "react";
import { BrowserRouter as Router, Routes, Route, NavLink } from "react-router-dom";
import Chat from "./components/Chat";
import Config from "./components/Config";

const App: React.FC = () => {
  return (
    <Router>
      <div className="min-h-screen bg-gray-100">

        <nav className="bg-white shadow">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between h-16">
              <div className="flex">
                <div className="flex-shrink-0 flex items-center">
                  <h1 className="text-xl font-bold text-gray-800">Cookidoo Chatbot</h1>
                </div>
                <div className="hidden sm:ml-6 sm:flex sm:space-x-8">

                  <NavLink
                    to="/chat"
                    className={({ isActive }) =>
                      isActive
                        ? "border-indigo-500 text-gray-900 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium"
                        : "border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium"
                    }
                  >
                    Chat
                  </NavLink>

                  <NavLink
                    to="/config"
                    className={({ isActive }) =>
                      isActive
                        ? "border-indigo-500 text-gray-900 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium"
                        : "border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium"
                    }
                  >
                    Configuration
                  </NavLink>

                </div>
              </div>
            </div>
          </div>
        </nav>

        <main className="max-w-7xl mx-auto py-10 px-4">
          <Routes>
            <Route path="/" element={<Chat />} />
            <Route path="/chat" element={<Chat />} />
            <Route path="/config" element={<Config />} />
          </Routes>
        </main>
        
      </div>
    </Router>
  );
};

export default App;
