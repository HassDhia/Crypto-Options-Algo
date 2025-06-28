import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App";

// Import Tailwind CSS
import "./index.css";

console.log('React application mounting');
const rootElement = document.getElementById("root");
console.log('Root element:', rootElement);

if (!rootElement) {
  throw new Error("Failed to find root element");
}

try {
  ReactDOM.createRoot(rootElement).render(
    <React.StrictMode>
      <App />
    </React.StrictMode>
  );
} catch (error) {
  console.error('Failed to mount React app:', error);
}
