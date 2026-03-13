import { ZodSchema } from "zod";

export function parseStructuredResponse<T>(
  responseText: string,
  schema: ZodSchema<T>,
  stage: string
): T {
  const candidate = extractJsonCandidate(responseText);
  try {
    return schema.parse(JSON.parse(candidate));
  } catch (error: any) {
    const message = String(error?.message ?? error);
    throw new Error(`[${stage}] structured response did not match the required schema: ${message}`);
  }
}

function extractJsonCandidate(responseText: string): string {
  const trimmed = responseText.trim();
  if (!trimmed) {
    throw new Error("empty response");
  }
  const fenceMatch = trimmed.match(/```(?:json)?\s*([\s\S]*?)```/i);
  if (fenceMatch?.[1]) {
    return fenceMatch[1].trim();
  }
  return trimmed;
}
