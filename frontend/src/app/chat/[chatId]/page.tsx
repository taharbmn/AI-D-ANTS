"use client";

import { useParams, useRouter } from "next/navigation";
import { useEffect } from "react";
import { useChatContext } from "@/contexts/ChatContext";
import Home from "@/app/page";

export default function ChatPage() {
  const params = useParams();
  const router = useRouter();
  const { selectChat, selectedChatId } = useChatContext();
  const chatId = params.chatId as string;

  useEffect(() => {
    if (chatId && chatId !== selectedChatId) {
      selectChat(chatId).catch((error) => {
        console.error("Failed to load chat:", error);
        // Redirect to home if chat doesn't exist
        router.push("/");
      });
    }
  }, [chatId, selectedChatId, selectChat, router]);

  return <Home />;
}
