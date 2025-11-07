const DEFAULT_CHAT_PATH = "/v1/chat";

type ChatRole = "user" | "assistant" | "system";

const ROLE_TO_SERVER: Record<ChatRole, "usuario" | "agente" | "sistema"> = {
  user: "usuario",
  assistant: "agente",
  system: "sistema",
};

const normalizeBaseUrl = (value?: string | null) => {
  if (!value) {
    return null;
  }
  const trimmed = value.trim();
  if (!trimmed) {
    return null;
  }
  try {
    if (/^https?:\/\//i.test(trimmed)) {
      const url = new URL(trimmed);
      return url.origin + url.pathname.replace(/\/$/, "");
    }
    if (typeof window !== "undefined") {
      const url = new URL(trimmed, window.location.origin);
      return url.origin + url.pathname.replace(/\/$/, "");
    }
  } catch {
    // fallback abaixo
  }
  return trimmed.replace(/\/$/, "");
};

const inferDefaultApiBaseUrl = () => {
  if (typeof window === "undefined") {
    return "http://127.0.0.1:8000";
  }
  if (window.location.port && window.location.port !== "8000") {
    return `${window.location.protocol}//${window.location.hostname}:8000`;
  }
  return window.location.origin;
};

const apiBaseUrl =
  normalizeBaseUrl(import.meta.env.VITE_API_BASE_URL) ?? inferDefaultApiBaseUrl();

const chatPath = import.meta.env.VITE_API_CHAT_PATH?.trim() || DEFAULT_CHAT_PATH;

export interface ChatMessagePayload {
  role: ChatRole;
  content: string;
}

export interface SendChatOptions {
  context?: string | null;
  conversationId?: string | null;
  signal?: AbortSignal;
}

export interface ChatResponsePayload {
  resposta: string;
  conversa_id: string;
  arquivo: string;
  contexto?: string | null;
}

export const parseApiError = async (response: Response) => {
  try {
    const data = await response.json();
    if (Array.isArray(data.detail)) {
      return data.detail
        .map((item) => {
          if (typeof item === "string") {
            return item;
          }
          if (item?.msg) {
            return item.msg;
          }
          if (item?.detail) {
            return item.detail;
          }
          return JSON.stringify(item);
        })
        .join("\n");
    }
    if (typeof data.detail === "string") {
      return data.detail;
    }
    if (data.message) {
      return data.message;
    }
    if (typeof data === "string") {
      return data;
    }
  } catch {
    // Swallow parse errors and fallback to generic message below
  }
  return `Erro ${response.status} ao contatar a API.`;
};

export const sendChat = async (
  messages: ChatMessagePayload[],
  options: SendChatOptions = {},
): Promise<ChatResponsePayload> => {
  if (!messages.length) {
    throw new Error("Nenhuma mensagem foi informada.");
  }

  const payload = {
    mensagens: messages.map((message) => ({
      papel: ROLE_TO_SERVER[message.role],
      conteudo: message.content,
    })),
    contexto: options.context?.trim() || null,
    conversa_id: options.conversationId?.trim() || null,
  };

  const response = await fetch(`${apiBaseUrl}${chatPath}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
    signal: options.signal,
  });

  if (!response.ok) {
    const errorMessage = await parseApiError(response);
    throw new Error(errorMessage);
  }

  let data: ChatResponsePayload;
  try {
    data = (await response.json()) as ChatResponsePayload;
  } catch {
    throw new Error("Falha ao interpretar a resposta do servidor.");
  }

  if (!data?.resposta) {
    throw new Error("A API retornou uma resposta vazia.");
  }

  if (!data?.conversa_id) {
    throw new Error("A API não retornou o identificador da conversa.");
  }

  return data;
};

export const getApiBaseUrl = () => apiBaseUrl;
