import React from 'react';

export default function DebugTest() {
  console.log("Debug component mounted - visible in browser console");
  return (
    <div className="p-4 bg-red-500 text-white text-2xl font-bold">
      DEBUG COMPONENT VISIBLE
    </div>
  );
}
