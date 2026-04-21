import { describe, it, expect } from 'vitest';
import React from 'react';
import { render } from 'ink-testing-library';
import { ChatView } from '../src/components/ChatView.js';

describe('ChatView', () => {
  it('shows empty state', () => {
    const { lastFrame } = render(<ChatView messages={[]} isLoading={false} />);
    expect(lastFrame()).toContain('输入你的问题');
  });

  it('shows loading state', () => {
    const { lastFrame } = render(<ChatView messages={[]} isLoading={true} />);
    expect(lastFrame()).toContain('思考中');
  });

  it('displays messages', () => {
    const messages = [
      {
        id: '1',
        role: 'user' as const,
        content: 'Hello',
        timestamp: new Date(),
      },
      {
        id: '2',
        role: 'assistant' as const,
        content: 'Hi there!',
        timestamp: new Date(),
      },
    ];
    
    const { lastFrame } = render(<ChatView messages={messages} isLoading={false} />);
    expect(lastFrame()).toContain('Hello');
    expect(lastFrame()).toContain('Hi there!');
  });
});
