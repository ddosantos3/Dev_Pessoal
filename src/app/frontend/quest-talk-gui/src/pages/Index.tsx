import { useCallback, useEffect, useState } from "react";
import { ChatSidebar } from "@/components/ChatSidebar";
import { ChatMessage } from "@/components/ChatMessage";
import { ChatInput } from "@/components/ChatInput";
import { ScrollArea } from "@/components/ui/scroll-area";
import { useToast } from "@/components/ui/use-toast";
import { Loader2, Sparkles } from "lucide-react";
import { sendChat } from "@/lib/chat-service";
import {
  deleteConversation,
  fetchConversation,
  fetchConversations,
  type ConversationDetail,
  type ConversationSummary,
} from "@/lib/conversation-service";
import { NewConversationDialog } from "@/components/NewConversationDialog";

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
}

const createAssistantMessage = (content: string): Message => ({
  id: `assistant-${Date.now().toString()}`,
  role: "assistant",
  content,
  timestamp: new Date(),
});

const buildWelcomeMessage = (context?: string | null) => {
  if (context && context.trim().length > 0) {
    return createAssistantMessage(
      `Contexto registrado: "${context.trim()}". Como posso ajudar você com isso?`,
    );
  }
  return createAssistantMessage("Olá! Sou seu assistente de IA. Como posso ajudar você hoje?");
};

const mapConversationMessages = (detail: ConversationDetail): Message[] => {
  const fallbackDate = new Date();
  return detail.mensagens.map((mensagem, index) => {
    const timestamp =
      mensagem.timestamp && !Number.isNaN(Date.parse(mensagem.timestamp))
        ? new Date(mensagem.timestamp)
        : new Date(fallbackDate.getTime() + index);
    const role = mensagem.papel === "usuario" ? "user" : "assistant";
    return {
      id: `${detail.id}-${index}-${mensagem.papel}`,
      role,
      content: mensagem.conteudo,
      timestamp,
    };
  });
};

const Index = () => {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [messages, setMessages] = useState<Message[]>([buildWelcomeMessage()]);
  const [isTyping, setIsTyping] = useState(false);
  const [isNewConversationOpen, setIsNewConversationOpen] = useState(false);
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [conversationContext, setConversationContext] = useState<string | null>(null);
  const [conversationFile, setConversationFile] = useState<string | null>(null);
  const [conversations, setConversations] = useState<ConversationSummary[]>([]);
  const [isConversationsLoading, setIsConversationsLoading] = useState(false);
  const [isConversationLoading, setIsConversationLoading] = useState(false);
  const { toast } = useToast();

  const loadConversations = useCallback(async () => {
    setIsConversationsLoading(true);
    try {
      const data = await fetchConversations();
      setConversations(data);
    } catch (error) {
      toast({
        title: "Falha ao carregar o histórico",
        description: error instanceof Error ? error.message : "Tente novamente mais tarde.",
        variant: "destructive",
      });
    } finally {
      setIsConversationsLoading(false);
    }
  }, [toast]);

  useEffect(() => {
    loadConversations();
  }, [loadConversations]);

  const resetConversationState = useCallback(
    (context?: string | null) => {
      setConversationId(null);
      setConversationFile(null);
      setConversationContext(context?.trim() || null);
      setMessages([buildWelcomeMessage(context)]);
      setIsTyping(false);
    },
    [],
  );

  const handleSendMessage = async (content: string) => {
    const sanitizedMessage = content.trim();
    if (!sanitizedMessage) {
      return;
    }

    const userMessage: Message = {
      id: `user-${Date.now().toString()}`,
      role: "user",
      content: sanitizedMessage,
      timestamp: new Date(),
    };

    const previousMessages = [...messages];
    const conversation = [...previousMessages, userMessage];

    setMessages(conversation);
    setIsTyping(true);

    try {
      const response = await sendChat(
        conversation.map((message) => ({
          role: message.role,
          content: message.content,
        })),
        {
          context: conversationContext ?? undefined,
          conversationId: conversationId ?? undefined,
        },
      );

      const assistantMessage = createAssistantMessage(response.resposta);

      setMessages([...conversation, assistantMessage]);
      setConversationId(response.conversa_id);
      setConversationContext(response.contexto ?? conversationContext ?? null);
      setConversationFile(response.arquivo);

      await loadConversations();
    } catch (error) {
      setMessages(previousMessages);
      toast({
        title: "Não consegui falar com o agente",
        description:
          error instanceof Error ? error.message : "Tente novamente em instantes.",
        variant: "destructive",
      });
    } finally {
      setIsTyping(false);
    }
  };

  const handleSelectConversation = async (id: string) => {
    setIsConversationLoading(true);
    try {
      const detail = await fetchConversation(id);
      setConversationId(detail.id);
      setConversationContext(detail.contexto ?? null);
      setConversationFile(detail.arquivo);
      setMessages(mapConversationMessages(detail));
    } catch (error) {
      toast({
        title: "Não foi possível abrir o histórico",
        description:
          error instanceof Error ? error.message : "Tente novamente em instantes.",
        variant: "destructive",
      });
    } finally {
      setIsConversationLoading(false);
      setIsTyping(false);
    }
  };

  const handleCreateConversation = (context: string) => {
    resetConversationState(context);
  };

  const handleDeleteConversation = async (id: string) => {
    const confirmou = window.confirm(
      "Remover esta conversa? Essa ação apagará o arquivo salvo em disco.",
    );
    if (!confirmou) {
      return;
    }
    try {
      await deleteConversation(id);
      toast({
        title: "Conversa removida",
        description: "O histórico foi excluído da pasta de dados.",
      });
      if (id === conversationId) {
        resetConversationState(conversationContext);
      }
      await loadConversations();
    } catch (error) {
      toast({
        title: "Não consegui apagar o histórico",
        description:
          error instanceof Error ? error.message : "Verifique permissões e tente novamente.",
        variant: "destructive",
      });
    }
  };

  const isEmpty = messages.length === 0;
  const showSkeleton = isConversationLoading && messages.length === 0;

  return (
    <>
      <div className="flex h-screen w-full overflow-hidden bg-[#343541] text-slate-50">
        <ChatSidebar
          collapsed={sidebarCollapsed}
          onToggle={() => setSidebarCollapsed(!sidebarCollapsed)}
          conversations={conversations}
          activeConversationId={conversationId}
          onSelectConversation={handleSelectConversation}
          onCreateConversation={() => setIsNewConversationOpen(true)}
          onDeleteConversation={handleDeleteConversation}
          isLoading={isConversationsLoading}
        />

        <main className="flex-1 flex flex-col bg-gradient-to-b from-[#343541] to-[#202123]">
          <div className="border-b border-white/5 px-6 py-4">
            <h1 className="text-xl font-semibold">
              {conversationContext && conversationContext.length > 0
                ? conversationContext
                : "Crie experiências web inesquecíveis"}
            </h1>
            <p className="mt-1 text-sm text-slate-200/80">
              {conversationFile
                ? `Histórico salvo em: ${conversationFile}`
                : "Descreva a landing page e eu gero o HTML, CSS e JS, salvando tudo em data/conversas."}
            </p>
          </div>

          <div className="flex-1 overflow-hidden">
            {showSkeleton ? (
              <div className="flex h-full flex-col items-center justify-center gap-3 text-slate-200">
                <Sparkles className="h-10 w-10 animate-pulse" />
                <p>Carregando histórico...</p>
              </div>
            ) : isEmpty ? (
              <div className="flex h-full flex-col items-center justify-center gap-4 px-6 text-center text-slate-200">
                <div className="inline-flex h-16 w-16 items-center justify-center rounded-full border border-white/10">
                  <Sparkles className="h-8 w-8" />
                </div>
                <div className="max-w-md space-y-2">
                  <h2 className="text-2xl font-semibold">Pronto para começar?</h2>
                  <p>Conte o tema, as seções e o clima visual. Eu entrego a estrutura completa, pronta para editar.</p>
                </div>
              </div>
            ) : (
              <ScrollArea className="h-full">
                <div className="pb-28 pt-2">
                  {messages.map((message) => (
                    <ChatMessage
                      key={message.id}
                      role={message.role}
                      content={message.content}
                      timestamp={message.timestamp}
                    />
                  ))}
                  {isTyping && (
                    <div className="px-4 pb-6">
                      <div className="mx-auto max-w-3xl rounded-2xl border border-white/10 bg-white/10 px-5 py-4 text-sm text-white shadow">
                        <div className="flex items-center gap-3 font-medium">
                          <Loader2 className="h-4 w-4 animate-spin" />
                          Modelando layout, aplicando Tailwind e salvando arquivos...
                        </div>
                        <p className="mt-1 text-xs text-white/80">
                          Estruturando seções, compondo animações e escrevendo os arquivos no diretório da conversa.
                        </p>
                      </div>
                    </div>
                  )}
                </div>
              </ScrollArea>
            )}
          </div>

          <ChatInput
            onSendMessage={handleSendMessage}
            disabled={isTyping || isConversationLoading}
          />
        </main>
      </div>

      <NewConversationDialog
        open={isNewConversationOpen}
        onOpenChange={setIsNewConversationOpen}
        onCreate={handleCreateConversation}
      />
    </>
  );
};

export default Index;
