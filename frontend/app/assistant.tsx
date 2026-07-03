"use client";

import { 
  AssistantRuntimeProvider, 
  unstable_useRemoteThreadListRuntime as useRemoteThreadListRuntime,
  useThreadListItem,
} from "@assistant-ui/react";
import { useChatRuntime } from "@assistant-ui/react-ai-sdk";
import { Thread } from "@/components/assistant-ui/thread";
import { SidebarInset, SidebarProvider, SidebarTrigger } from "@/components/ui/sidebar";
import { AppSidebar } from "@/components/app-sidebar";
import { Separator } from "@/components/ui/separator";
import { Breadcrumb, BreadcrumbItem, BreadcrumbLink, BreadcrumbList, BreadcrumbPage, BreadcrumbSeparator } from "@/components/ui/breadcrumb";
import { Heart, Brain } from "lucide-react";
import { myThreadListAdapter, makeHistoryAdapter } from "@/hooks/use-thread-manager";

export const Assistant = () => {
  const runtime = useRemoteThreadListRuntime({
    adapter: myThreadListAdapter,
    runtimeHook: () => {
      // Fetch the thread ID for the currently mounted thread from the assistant-ui context
      // eslint-disable-next-line react-hooks/rules-of-hooks
      const { id: threadId } = useThreadListItem();
      
      // eslint-disable-next-line react-hooks/rules-of-hooks
      return useChatRuntime({
        api: "/api/chat",
        headers: {
          "x-session-id": threadId,
        },
        adapters: {
          history: makeHistoryAdapter(threadId),
        },
        initialMessages: [
          {
            id: "welcome-msg",
            role: "assistant",
            content: "Hello! I'm **Calmindra**, your compassionate mental health companion. 🌸\n\nI'm here to provide a safe, non-judgmental space where you can:\n\n- 💙 Share your thoughts and feelings\n- 🌿 Explore coping strategies  \n- 💜 Find emotional support\n- 🧘‍♀️ Practice mindfulness techniques\n- 🌟 Work through daily challenges\n\nTake a deep breath, and know that whatever you're going through, you don't have to face it alone. \n\n**How are you feeling today?** Feel free to share as much or as little as you'd like - I'm here to listen. 💕",
            createdAt: new Date(),
          },
        ],
      });
    },
  });

  return (
    <AssistantRuntimeProvider runtime={runtime}>
      <SidebarProvider>
        <AppSidebar />
        <SidebarInset>
          <header className="flex h-16 shrink-0 items-center gap-2 border-b px-4 bg-gradient-to-r from-blue-50 to-purple-50">
            <SidebarTrigger />
            <Separator orientation="vertical" className="mr-2 h-4" />
            <div className="flex items-center gap-2">
              <div className="flex items-center gap-2">
                <Brain className="h-6 w-6 text-blue-600" />
                <Heart className="h-5 w-5 text-purple-600" />
              </div>
              <Breadcrumb>
                <BreadcrumbList>
                  <BreadcrumbItem>
                    <BreadcrumbLink href="#" className="text-blue-800 font-semibold">
                      Calmindra
                    </BreadcrumbLink>
                  </BreadcrumbItem>
                  <BreadcrumbSeparator />
                  <BreadcrumbItem>
                    <BreadcrumbPage className="text-purple-700">
                      Mental Health Companion
                    </BreadcrumbPage>
                  </BreadcrumbItem>
                </BreadcrumbList>
              </Breadcrumb>
            </div>
          </header>
          <Thread />
        </SidebarInset>
      </SidebarProvider>
    </AssistantRuntimeProvider>
  );
};
