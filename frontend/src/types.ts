export interface ChatMessage {
  role: 'assistant' | 'user';
  content: string;
}

export interface DocMeta {
  page?: number;
  source?: string;
}

export interface ChatMeta {
  docs?: DocMeta[];
}
