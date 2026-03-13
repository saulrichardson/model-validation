import { Codex } from "@openai/codex-sdk";

const transientPatterns = ["stream disconnected", "ECONNRESET", "ENETDOWN", "ETIMEDOUT"];

export async function runWithRetries(
  thread: ReturnType<Codex["startThread"]>,
  prompt: string,
  events: unknown[],
  maxAttempts = 3
) {
  let attempt = 0;
  while (true) {
    attempt += 1;
    try {
      const result = await thread.run(prompt, {
        onEvent: (event: unknown) => {
          events.push(event);
        },
      } as any);
      return result;
    } catch (error: any) {
      const message = String(error?.message ?? error);
      const transient = transientPatterns.some((pattern) => message.includes(pattern));
      if (!transient || attempt >= maxAttempts) {
        throw error;
      }
      const backoffMs = 500 * attempt;
      console.warn(`[codex] transient error (${message}); retry ${attempt}/${maxAttempts} after ${backoffMs}ms`);
      await new Promise((resolve) => setTimeout(resolve, backoffMs));
      events.length = 0;
    }
  }
}
