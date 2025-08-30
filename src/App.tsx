import React from 'react';
import { ChatWidget } from './components/ChatWidget';

function App() {
  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center p-8">
      <div className="max-w-2xl mx-auto text-center">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">Brax Fine Jewelers</h1>
        <p className="text-xl text-gray-600 mb-8">AI Concierge Chat Widget</p>
        <p className="text-gray-500">The chat widget appears in the bottom right corner.</p>
        <div className="mt-8 p-6 bg-white rounded-lg shadow-sm border">
          <h2 className="text-lg font-semibold mb-4">Development Environment</h2>
          <p className="text-sm text-gray-600">
            This is the development preview of the Brax AI Concierge chat widget. 
            Click the chat button to test the interface and functionality.
          </p>
        </div>
      </div>
      <ChatWidget 
        apiUrl="http://localhost:8080"
        position="bottom-right"
        theme="light"
        userId="dev-user"
      />
    </div>
  );
}

export default App;
