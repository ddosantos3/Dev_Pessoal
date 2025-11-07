import {
  Loader2,
  Menu,
  MessageSquare,
  Plus,
  Search,
  Trash2,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { ScrollArea } from "@/components/ui/scroll-area";
import { useMemo, useState } from "react";
import { cn } from "@/lib/utils";
import type { ConversationSummary } from "@/lib/conversation-service";

interface ChatSidebarProps {
  collapsed: boolean;
  onToggle: () => void;
  conversations: ConversationSummary[];
  activeConversationId?: string | null;
  onSelectConversation: (conversationId: string) => void;
  onCreateConversation: () => void;
  onDeleteConversation: (conversationId: string) => void;
  isLoading?: boolean;
}

const formatDate = (value: string) => {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return "";
  }
  return date.toLocaleString("pt-BR", {
    day: "2-digit",
    month: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  });
};

export function ChatSidebar({
  collapsed,
  onToggle,
  conversations,
  activeConversationId,
  onSelectConversation,
  onCreateConversation,
  onDeleteConversation,
  isLoading,
}: ChatSidebarProps) {
  const [searchQuery, setSearchQuery] = useState("");

  const filteredConversations = useMemo(() => {
    const query = searchQuery.trim().toLowerCase();
    if (!query) {
      return conversations;
    }
    return conversations.filter((conversation) => {
      const titulo = conversation.titulo.toLowerCase();
      const contexto = conversation.contexto?.toLowerCase() ?? "";
      return titulo.includes(query) || contexto.includes(query);
    });
  }, [conversations, searchQuery]);

  const handleSelect = (conversationId: string) => {
    if (conversationId === activeConversationId) {
      return;
    }
    onSelectConversation(conversationId);
  };

  return (
    <aside
      className={cn(
        "flex flex-col bg-sidebar border-r border-sidebar-border transition-all duration-300 ease-in-out",
        collapsed ? "w-0 md:w-16" : "w-72 lg:w-80",
      )}
    >
      <div className="flex items-center justify-between p-3 border-b border-sidebar-border">
        {!collapsed && (
          <Button
            variant="ghost"
            size="sm"
            className="w-full justify-start gap-2 rounded-xl border border-white/5 bg-white/5 text-sidebar-foreground shadow-sm transition-all duration-200 hover:-translate-y-0.5 hover:bg-white/10 hover:shadow-md"
            onClick={onCreateConversation}
          >
            <Plus className="h-4 w-4 mr-2" />
            Nova conversa
          </Button>
        )}
        <Button
          variant="ghost"
          size="icon"
          onClick={onToggle}
          className="text-sidebar-foreground hover:bg-sidebar-accent shrink-0"
        >
          <Menu className="h-5 w-5" />
        </Button>
      </div>

      {!collapsed ? (
        <>
          <div className="p-3">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-sidebar-foreground/50" />
              <Input
                type="text"
                placeholder="Buscar conversas..."
                value={searchQuery}
                onChange={(event) => setSearchQuery(event.target.value)}
                className="pl-9 bg-sidebar-accent border-sidebar-border text-sidebar-foreground placeholder:text-sidebar-foreground/50"
              />
            </div>
          </div>

          <div className="px-3 pb-2 text-xs text-muted-foreground uppercase tracking-wide">
            Histórico
          </div>

          <ScrollArea className="flex-1">
            <div className="p-2 space-y-1">
              {isLoading && conversations.length === 0 ? (
                <div className="py-8 text-center text-sm text-muted-foreground">
                  <Loader2 className="h-4 w-4 mx-auto mb-2 animate-spin" />
                  Carregando conversas...
                </div>
              ) : filteredConversations.length === 0 ? (
                <div className="py-8 text-center text-sm text-muted-foreground">
                  Nenhuma conversa encontrada.
                </div>
              ) : (
                filteredConversations.map((conversation) => {
                  const isActive = activeConversationId === conversation.id;
                  return (
                    <div
                      key={conversation.id}
                      className={cn(
                        "group relative w-full rounded-xl transition-all duration-150 ease-out",
                        isActive
                          ? "bg-white/10 shadow-lg shadow-black/20"
                          : "hover:bg-white/5 hover:shadow-md hover:shadow-black/20 hover:scale-[1.01]",
                      )}
                    >
                      <button
                        type="button"
                        onClick={() => handleSelect(conversation.id)}
                        className="flex w-full items-start gap-3 rounded-xl p-3 text-left"
                      >
                        <MessageSquare className="h-4 w-4 mt-1 text-sidebar-foreground/70 shrink-0" />
                        <div className="flex-1 min-w-0">
                          <h3 className="text-sm font-medium leading-snug text-sidebar-foreground line-clamp-2">
                            {conversation.titulo}
                          </h3>
                          {conversation.contexto && (
                            <p className="text-xs text-sidebar-foreground/60 mt-1 line-clamp-2">
                              {conversation.contexto}
                            </p>
                          )}
                          <p className="text-xs text-sidebar-foreground/50 mt-1">
                            {formatDate(conversation.atualizado_em)}
                          </p>
                        </div>
                      </button>
                      <div className="absolute right-2 top-1/2 -translate-y-1/2 opacity-0 transition-opacity group-hover:opacity-100">
                        <Button
                          type="button"
                          variant="ghost"
                          size="icon"
                          onClick={(event) => {
                            event.stopPropagation();
                            onDeleteConversation(conversation.id);
                          }}
                          className="h-8 w-8 rounded-full text-red-500 transition hover:bg-red-500/15"
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </div>
                    </div>
                  );
                })
              )}
            </div>
          </ScrollArea>

          <div className="p-3 text-xs text-muted-foreground">
            {isLoading ? (
              <span className="inline-flex items-center gap-2">
                <Loader2 className="h-3 w-3 animate-spin" />
                Sincronizando...
              </span>
            ) : (
              <span>{conversations.length} conversa(s) salvas</span>
            )}
          </div>
        </>
      ) : (
        <div className="flex flex-col items-center gap-4 py-4">
          <Button
            variant="ghost"
            size="icon"
            className="text-sidebar-foreground hover:bg-sidebar-accent"
            onClick={onCreateConversation}
          >
            <Plus className="h-5 w-5" />
          </Button>
        </div>
      )}
    </aside>
  );
}
