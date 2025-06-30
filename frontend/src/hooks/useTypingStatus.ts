import { useQuery } from '@tanstack/react-query';

interface TypingUser {
  conversationId: number;
  userId: number;
  userName: string;
  isTyping: boolean;
}

/**
 * Hook to get typing status for a conversation
 */
export const useTypingStatus = (conversationId: number) => {
  return useQuery<TypingUser[]>({
    queryKey: ['chat', 'typing', conversationId],
    queryFn: () => [],
    staleTime: Infinity, // This data is managed by socket events
    gcTime: 0, // Don't cache when component unmounts
  });
};
