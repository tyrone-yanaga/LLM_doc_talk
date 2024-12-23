import { z } from "zod";
import { ocrResponse } from "~/constants";
import { VectorDB } from "imvectordb";
import { OpenAI } from "openai";

import { createTRPCRouter, publicProcedure } from "~/server/api/trpc";

const oai = new OpenAI();

export const questionsRouter = createTRPCRouter({
  askQuestion: publicProcedure
    .input(z.object({ question: z.string().min(1) }))
    .mutation(async ({ input }) => {
      console.log({ input, ocrResponse });
      // 1. for each chunk in the embedding reponse, embed it and store it in the vector DB
      // along with the chunk informatino (content, bounding box)

      // 2. embed the input.question
      // 3. search for the chunk via cosine similarity to the embedded input question, choose the top k chunks
      // 4. Pass that context into a chat.completions call from OAI
      // 5. Return the answer as well as any sources!
      return "answer";
    }),
});
