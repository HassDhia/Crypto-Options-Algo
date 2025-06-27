import React from "react";
import Dashboard from "./Dashboard";
import "./index.css";  // Tailwind base & styles (assumes Tailwind is set up)

/** Root application component with global styling */
const App: React.FC = () => {
  return (
    <div className="min-h-screen bg-gray-100 text-gray-900">
      {/* App Header */}
      <header className="p-6 text-2xl font-bold">Crypto Options Dashboard</header>
      {/* Main Dashboard Content */}
      <main className="p-6">
        <Dashboard />
      </main>
    </div>
  );
};

export default App;
