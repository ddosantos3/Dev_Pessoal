import { Send } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { useState, useRef, useEffect } from "react";

interface ChatInputProps {
  onSendMessage: (message: string) => void;
  disabled?: boolean;
}

export function ChatInput({ onSendMessage, disabled }: ChatInputProps) {
  const [message, setMessage] = useState("");
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const handleSubmit = () => {
    if (message.trim() && !disabled) {
      onSendMessage(message.trim());
      setMessage("");
      if (textareaRef.current) {
        textareaRef.current.style.height = "auto";
      }
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 200)}px`;
    }
  }, [message]);

  return (
    <div className="bg-transparent">
      <div className="mx-auto max-w-3xl px-4 py-5">
        <div className="relative flex items-end gap-3 rounded-3xl border border-white/20 bg-white/95 shadow-2xl">
          <Textarea
            ref={textareaRef}
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Descreva o site que deseja criar..."
            disabled={disabled}
            className="min-h-[64px] max-h-[260px] flex-1 resize-none border-0 bg-transparent px-5 py-5 pr-16 text-base text-slate-800 placeholder:text-slate-400 focus-visible:ring-0"
            rows={1}
          />
          <Button
            onClick={handleSubmit}
            disabled={!message.trim() || disabled}
            size="icon"
            className="absolute right-4 bottom-4 h-11 w-11 rounded-2xl bg-slate-900 text-white shadow hover:scale-105 hover:bg-slate-700 disabled:bg-slate-400/60"
          >
            <Send className="h-5 w-5" />
          </Button>
        </div>
        <p className="mt-2 text-center text-xs text-slate-500">
          Pressione Enter para enviar · Shift + Enter para quebrar linha
        </p>
      </div>
    </div>
  );
}
