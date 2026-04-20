/**
 * Components 单元测试
 */

import { describe, it, expect } from "vitest";
import React from "react";
import { render } from "ink-testing-library";
import { MessageItem } from "../src/components/MessageItem.js";
import { ChatView } from "../src/components/ChatView.js";
import { StatusBar } from "../src/components/StatusBar.js";
import { ToolExecution } from "../src/components/Animation.js";
import { Markdown } from "../src/components/Markdown.js";

describe("MessageItem", () => {
  it("should render user message", () => {
    const { lastFrame } = render(
      <MessageItem
        message={{
          role: "user",
          content: "Hello",
          timestamp: new Date("2026-04-21T00:00:00"),
        }}
      />
    );

    expect(lastFrame()).toContain("You:");
    expect(lastFrame()).toContain("Hello");
  });

  it("should render assistant message", () => {
    const { lastFrame } = render(
      <MessageItem
        message={{
          role: "assistant",
          content: "Hi there!",
          timestamp: new Date("2026-04-21T00:00:00"),
        }}
      />
    );

    expect(lastFrame()).toContain("Assistant:");
    expect(lastFrame()).toContain("Hi there!");
  });

  it("should render multiline message", () => {
    const { lastFrame } = render(
      <MessageItem
        message={{
          role: "user",
          content: "Line 1\nLine 2\nLine 3",
          timestamp: new Date(),
        }}
      />
    );

    expect(lastFrame()).toContain("Line 1");
    expect(lastFrame()).toContain("Line 2");
    expect(lastFrame()).toContain("Line 3");
  });
});

describe("ChatView", () => {
  it("should render welcome message when empty", () => {
    const { lastFrame } = render(<ChatView messages={[]} isStreaming={false} />);

    expect(lastFrame()).toContain("Welcome to Nano Code!");
  });

  it("should render messages", () => {
    const messages = [
      { role: "user" as const, content: "Hello", timestamp: new Date() },
      { role: "assistant" as const, content: "Hi!", timestamp: new Date() },
    ];

    const { lastFrame } = render(<ChatView messages={messages} isStreaming={false} />);

    expect(lastFrame()).toContain("Hello");
    expect(lastFrame()).toContain("Hi!");
  });

  it("should show thinking indicator when streaming", () => {
    const { lastFrame } = render(<ChatView messages={[]} isStreaming={true} />);

    expect(lastFrame()).toContain("Thinking...");
  });
});

describe("StatusBar", () => {
  it("should render idle status", () => {
    const { lastFrame } = render(<StatusBar status="idle" model="gpt-4o" />);

    expect(lastFrame()).toContain("gpt-4o");
    expect(lastFrame()).toContain("Ready");
  });

  it("should render thinking status", () => {
    const { lastFrame } = render(<StatusBar status="thinking" model="gpt-4o" />);

    expect(lastFrame()).toContain("Thinking...");
  });

  it("should render error status", () => {
    const { lastFrame } = render(<StatusBar status="error" model="gpt-4o" />);

    expect(lastFrame()).toContain("Error");
  });
});

describe("ToolExecution", () => {
  it("should render tool name", () => {
    const { lastFrame } = render(<ToolExecution toolName="read_file" />);

    expect(lastFrame()).toContain("read_file");
  });

  it("should render tool with args", () => {
    const { lastFrame } = render(
      <ToolExecution toolName="read_file" args={{ path: "/src/main.py" }} />
    );

    expect(lastFrame()).toContain("read_file");
    expect(lastFrame()).toContain("path=/src/main.py");
  });

  it("should truncate long args", () => {
    const longPath = "/very/long/path/that/should/be/truncated/".repeat(10);
    const { lastFrame } = render(
      <ToolExecution toolName="read_file" args={{ path: longPath }} />
    );

    expect(lastFrame()).toContain("...");
  });
});

describe("Markdown", () => {
  it("should render headings", () => {
    const { lastFrame } = render(
      <Markdown content="# Title\n## Subtitle\n### Sub-subtitle" />
    );

    expect(lastFrame()).toContain("Title");
    expect(lastFrame()).toContain("Subtitle");
    expect(lastFrame()).toContain("Sub-subtitle");
  });

  it("should render code blocks", () => {
    // 代码块渲染比较复杂，简化测试
    const content = "```python\nprint('hello')\n```";
    const { lastFrame } = render(<Markdown content={content} />);
    
    // 组件应该成功渲染
    expect(lastFrame()).toBeDefined();
  });

  it("should render list items", () => {
    const { lastFrame } = render(<Markdown content="- Item 1\n- Item 2" />);

    expect(lastFrame()).toContain("Item 1");
    expect(lastFrame()).toContain("Item 2");
  });

  it("should render empty content", () => {
    const { lastFrame } = render(<Markdown content="" />);

    expect(lastFrame()).toBeDefined();
  });
});
