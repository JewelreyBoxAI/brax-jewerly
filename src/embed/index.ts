import React from 'react';
import { createRoot } from 'react-dom/client';
import { ChatWidget } from '../components/ChatWidget';
import '../index.css';

export interface BraxChatConfig {
  apiUrl?: string;
  apiKey?: string;
  position?: 'bottom-right' | 'bottom-left';
  theme?: 'light' | 'dark';
  userId?: string;
  containerId?: string;
}

class BraxChatEmbed {
  private root: any = null;
  private container: HTMLElement | null = null;

  mount(config: BraxChatConfig = {}) {
    // Create container if not provided
    if (config.containerId) {
      this.container = document.getElementById(config.containerId);
      if (!this.container) {
        throw new Error(`Container with id "${config.containerId}" not found`);
      }
    } else {
      this.container = document.createElement('div');
      this.container.id = 'brax-chat-widget';
      document.body.appendChild(this.container);
    }

    // Create React root and render
    this.root = createRoot(this.container);
    this.root.render(
      React.createElement(ChatWidget, {
        apiUrl: config.apiUrl,
        apiKey: config.apiKey,
        position: config.position,
        theme: config.theme,
        userId: config.userId,
      })
    );

    return this;
  }

  unmount() {
    if (this.root) {
      this.root.unmount();
      this.root = null;
    }
    
    if (this.container && this.container.id === 'brax-chat-widget') {
      document.body.removeChild(this.container);
    }
    
    this.container = null;
  }

  updateConfig(config: Partial<BraxChatConfig>) {
    if (this.root && this.container) {
      this.root.render(
        React.createElement(ChatWidget, config)
      );
    }
  }
}

// Global object for embedding
declare global {
  interface Window {
    BraxChat: {
      mount: (config?: BraxChatConfig) => BraxChatEmbed;
    };
  }
}

// Export for UMD/IIFE builds
const BraxChat = {
  mount: (config?: BraxChatConfig) => {
    const embed = new BraxChatEmbed();
    return embed.mount(config);
  }
};

// Make available globally
if (typeof window !== 'undefined') {
  window.BraxChat = BraxChat;
}

export default BraxChat;
export { BraxChatEmbed };