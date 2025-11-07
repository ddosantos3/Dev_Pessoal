import { Bot, User } from "lucide-react";
import { cn } from "@/lib/utils";

interface ChatMessageProps {
  role: "user" | "assistant";
  content: string;
  timestamp?: Date;
}

export function ChatMessage({ role, content, timestamp }: ChatMessageProps) {
  const isUser = role === "user";

  const renderContent = () => {
    const linhas = content.split("\n");
    return linhas.map((linha, index) => {
      const texto = linha.trim();
      if (!texto) {
        return <div key={`gap-${index}`} className="h-2" />;
      }
      if (texto.startsWith("• ")) {
        return (
          <div key={`bullet-${index}`} className="flex items-start gap-2 text-sm">
            <span className="text-base leading-5">•</span>
            <span>{texto.slice(2)}</span>
          </div>
        );
      }
      if (/^[✨📁🧩🚀]/u.test(texto)) {
        return (
          <p key={`icon-${index}`} className="text-sm font-medium">
            {texto}
          </p>
        );
      }
      return (
        <p key={`text-${index}`} className="text-sm leading-relaxed">
          {texto}
        </p>
      );
    });
  };

  return (
    <div className="px-4 py-2 md:px-6">
      <div className={cn("flex w-full", isUser ? "justify-end" : "justify-start")}>
        <div
          className={cn(
            "flex max-w-3xl items-end gap-3",
            isUser ? "flex-row-reverse" : "flex-row",
          )}
        >
          <div
            className={cn(
              "flex h-9 w-9 shrink-0 items-center justify-center rounded-full border shadow-sm",
              isUser ? "border-slate-300 bg-white text-slate-900" : "border-slate-400/60 bg-slate-900 text-white",
            )}
          >
            {isUser ? <User className="h-4 w-4" /> : <Bot className="h-4 w-4" />}
          </div>
          <div
            className={cn(
              "rounded-3xl border px-5 py-4 text-left shadow-lg backdrop-blur",
              isUser
                ? "border-slate-200 bg-white text-slate-900"
                : "border-slate-200 bg-[#f6f7fb] text-slate-900",
            )}
          >
            <div className="space-y-2">{renderContent()}</div>
            {timestamp && (
              <span className="mt-3 block text-xs text-slate-400">
                {timestamp.toLocaleTimeString("pt-BR", {
                  hour: "2-digit",
                  minute: "2-digit",
                })}
              </span>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
