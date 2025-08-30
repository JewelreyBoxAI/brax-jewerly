import React from 'react';
import { ChatWidget } from './components/ChatWidget';
import { createRoot } from 'react-dom/client';
import './styles/global.css';

// Development mode - render directly to root
const App = () => {
  return (
    <>
      <ChatWidget 
        apiUrl="http://localhost:8080"
        position="bottom-right"
        theme="light"
        userId="dev-user"
      />
    </>
  );
};

const root = createRoot(document.getElementById('root')!);
root.render(<App />);