import { describe, it, expect } from 'vitest';
import React from 'react';
import { render } from 'ink-testing-library';
import { StatusBar } from '../src/components/StatusBar.js';

describe('StatusBar', () => {
  it('renders correctly', () => {
    const { lastFrame } = render(
      <StatusBar 
        mode="build" 
        model="gpt-4o-mini" 
        messages={0} 
        tools={0} 
        duration={0} 
      />
    );
    
    expect(lastFrame()).toContain('BUILD');
    expect(lastFrame()).toContain('gpt-4o-mini');
  });

  it('shows plan mode', () => {
    const { lastFrame } = render(
      <StatusBar 
        mode="plan" 
        model="gpt-4o-mini" 
        messages={5} 
        tools={3} 
        duration={120} 
      />
    );
    
    expect(lastFrame()).toContain('PLAN');
  });
});
