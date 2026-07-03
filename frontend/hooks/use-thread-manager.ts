import {
  unstable_useRemoteThreadListRuntime as useRemoteThreadListRuntime,
  type unstable_RemoteThreadListAdapter as RemoteThreadListAdapter,
  type ThreadHistoryAdapter,
} from "@assistant-ui/react";
import { useChatRuntime } from "@assistant-ui/react-ai-sdk";
import { createAssistantStream } from "assistant-stream";

const generateUUID = () => {
  return "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".replace(/[xy]/g, (c) => {
    const r = (Math.random() * 16) | 0;
    const v = c === "x" ? r : (r & 0x3) | 0x8;
    return v.toString(16);
  });
};

export const myThreadListAdapter: RemoteThreadListAdapter = {
  async list() {
    try {
      const res = await fetch("/api/threads", { cache: "no-store" });
      if (!res.ok) throw new Error("Failed to list threads");
      const threads = await res.json();
      return {
        threads: threads.map((t: any) => ({
          remoteId: t.id,
          title: t.title,
          status: "regular",
        })),
      };
    } catch (error) {
      console.error("Error listing remote threads:", error);
      return { threads: [] };
    }
  },
  
  async initialize(threadId) {
    try {
      const remoteUUID = generateUUID();
      const res = await fetch("/api/threads", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          id: remoteUUID,
          title: "New Chat Session",
        }),
      });
      if (!res.ok) throw new Error("Failed to initialize remote thread");
      const data = await res.json();
      return { remoteId: data.id, externalId: undefined };
    } catch (error) {
      console.error("Error initializing remote thread:", error);
      throw error;
    }
  },
  
  async delete(remoteId) {
    try {
      const res = await fetch(`/api/threads/${remoteId}`, {
        method: "DELETE",
      });
      if (!res.ok) throw new Error("Failed to delete thread");
    } catch (error) {
      console.error("Error deleting remote thread:", error);
      throw error;
    }
  },
  
  async rename(remoteId, newTitle) {
    console.log(`Renaming thread ${remoteId} to ${newTitle}`);
  },
  
  async archive(remoteId) {
    console.log(`Archiving thread ${remoteId}`);
  },
  
  async unarchive(remoteId) {
    console.log(`Unarchiving thread ${remoteId}`);
  },
  
  async generateTitle(remoteId, unstable_messages) {
    return createAssistantStream(async (controller) => {
      const firstUserMsg = unstable_messages.find((m) => m.role === "user");
      let title = "Chat Session";
      if (firstUserMsg && Array.isArray(firstUserMsg.content)) {
        const textContent = firstUserMsg.content.find((item: any) => item.type === "text")?.text;
        if (textContent) {
          title = textContent.substring(0, 30);
          if (textContent.length > 30) title += "...";
        }
      }
      controller.appendText(title);
    });
  },
};

export const makeHistoryAdapter = (threadId: string): ThreadHistoryAdapter => ({
  async load() {
    try {
      const res = await fetch(`/api/threads/${threadId}/messages`, {
        cache: "no-store",
      });
      if (!res.ok) throw new Error("Failed to load thread messages");
      const messages = await res.json();
      
      return {
        messages: messages.map((m: any) => ({
          id: m.id || generateUUID(),
          role: m.role,
          content: [{ type: "text", text: m.content }],
          createdAt: new Date(m.createdAt),
        })),
      };
    } catch (error) {
      console.error(`Error loading messages for thread ${threadId}:`, error);
      return { messages: [] };
    }
  },
  
  async append() {
    // No-op: Saved on the backend during chat completions loop
  },
});
