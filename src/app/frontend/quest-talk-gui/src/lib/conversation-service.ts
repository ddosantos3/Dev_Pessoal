import { getApiBaseUrl, parseApiError } from "@/lib/chat-service";

export interface ConversationSummary {
  id: string;
  titulo: string;
  contexto?: string | null;
  arquivo: string;
  criado_em: string;
  atualizado_em: string;
}

export interface ConversationMessage {
  papel: "usuario" | "agente" | "sistema";
  conteudo: string;
  timestamp?: string | null;
}

export interface ConversationDetail extends ConversationSummary {
  mensagens: ConversationMessage[];
}

export const fetchConversations = async (): Promise<ConversationSummary[]> => {
  const response = await fetch(`${getApiBaseUrl()}/v1/conversas`, {
    method: "GET",
  });
  if (!response.ok) {
    const error = await parseApiError(response);
    throw new Error(error);
  }
  return (await response.json()) as ConversationSummary[];
};

export const fetchConversation = async (id: string): Promise<ConversationDetail> => {
  const response = await fetch(`${getApiBaseUrl()}/v1/conversas/${encodeURIComponent(id)}`, {
    method: "GET",
  });
  if (!response.ok) {
    const error = await parseApiError(response);
    throw new Error(error);
  }
  return (await response.json()) as ConversationDetail;
};

export const deleteConversation = async (id: string): Promise<void> => {
  const response = await fetch(`${getApiBaseUrl()}/v1/conversas/${encodeURIComponent(id)}`, {
    method: "DELETE",
  });
  if (!response.ok) {
    const error = await parseApiError(response);
    throw new Error(error);
  }
};
