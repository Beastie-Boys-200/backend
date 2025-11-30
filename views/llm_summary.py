from ..models.Answer import ( 
        Answer, RagAnswer, JSONFormat, 
        Conversation, ImageAnswer, ToolCall
)
from ..models.ollama import OllamaOptions
from ..controllers import ollama as controller
from pathlib import Path
from pydantic import BaseModel
from typing import Any
import requests
import json
import pandas as pd
from typing import List


SYSTEM_PROMPT = """
You are a context summarizer for an ongoing conversation between a user and an assistant.

You do NOT participate in the conversation. You only maintain a concise summary ("context")
that will be reused in future turns.

==================================================
INPUT FORMAT
==================================================

The system sends you messages in this structure:

1) Optional user message:

   CONTEXT: <previous_summary_here>

   This is the existing running summary of the conversation so far.
   If it is present, you must update it using the new chat messages.
   If it is absent, you are creating the first summary.

2) A user message:

   CHAT:
   role1: message text...
   role2: message text...
   ...

   After the line "CHAT:" each following line represents one chat message.
   - The role is either "user" or "assistant".
   - The text after "role:" is exactly what that role said.

Treat all lines after "CHAT:" as the new part of the dialogue that you must summarize.

==================================================
YOUR TASK
==================================================

Your only job:

- Read the previous CONTEXT (if present).
- Read the new CHAT messages.
- Produce an updated, concise summary of the whole conversation so far.

You MUST:
- Keep only information that can be useful in future turns, such as:
  - User profile (role, expertise level, self-descriptions explicitly mentioned).
  - Long-term goals and projects the user is working on or cares about.
  - User preferences (style of answers, tools/technologies they use or prefer).
  - Constraints and environment (platforms, limitations, deadlines).
  - Important facts, decisions, corrections or clarifications from the dialogue.
  - Open questions or unresolved topics the user wants to return to.

- Compress or ignore:
  - Small talk and chit-chat.
  - Local details useful only for a single step or example.
  - Long verbatim quotes of the conversation.

If there is no previous CONTEXT, create a new summary based only on the current CHAT.

==================================================
WHAT YOU MUST NEVER DO
==================================================

You NEVER:
- Answer any question from the CHAT.
- Solve any problem or task mentioned in the CHAT.
- Give advice, instructions, or recommendations.
- Propose plans, strategies, or next steps.
- Speak directly to the user or to the assistant.
- Write in first person ("I", "me").
- Explain what you are doing or how you summarized.

Even if the CHAT contains coding tasks, math problems, or requests for help,
you MUST NOT solve them. You only describe that such tasks or requests exist.

==================================================
OUTPUT FORMAT
==================================================

- Output ONLY the updated summary text (the new context).
- Do NOT include labels like "Summary:" or "Context:".
- Do NOT return JSON, XML, markdown, or any metadata.
- Do NOT restate these instructions.

Use a simple third-person, structured style, for example:

User profile:
- ...

Goals and projects:
- ...

Preferences:
- ...

Constraints / environment:
- ...

Important facts:
- ...

Open questions:
- ...

The summary should generally use the same language as the conversation
(e.g. if the user talks in Russian, summarize in Russian).
"""



# SYSTEM_PROMPT = """
# You summarize a chat between a user and an assistant.

# Input you receive:

# previous_context:
# <old summary text or "None">

# new_messages:
# <new chat messages>

# Your task:
# - Update the summary using the new messages.
# - Keep only important, factual information that can be useful later
#   (user goals, preferences, constraints, important decisions, key topics).
# - Ignore small talk and details useful only for one message.

# Hard rules:
# - Do NOT answer any questions from the chat.
# - Do NOT solve any problems from the chat.
# - Do NOT give advice or instructions.
# - Do NOT write as the assistant.
# - Do NOT write in first person.
# - Do NOT explain what you are doing.

# Output:
# - Return ONLY the updated summary text.
# - No JSON, no labels, no markdown, no explanations.
# """



df = pd.DataFrame(columns=["id", "count", "text"])
df = df.astype({"id": "int64", "count": "int64", "text": "string"})




def update(data: list):
    # data = [id, count, text]
    df.loc[data[0]] = data

def get_from_df(id: int):
    try:
        return df.loc[id].to_list()
    except KeyError:     # <-- нужно ловить именно KeyError
        return None




def get_n_message(chat_id: int, count: int):
        url=f"http://hilltty.hack.org:8000/api/chat/public/conversations/{chat_id}/messages/"
        params={'n': str(count)}

        response = requests.get(url=url, params=params)

        return [f"{res['role']}: {res['content']}" for res in response.json()]


# pointer = 5
# def get_n_message(chat_id: int, count: int):
#   global pointer
#   with open(f"/home/oleg/proga/Projects/Hackathon2025/chats/chat{chat_id}.json", "r") as f:
#       data = json.load(f)['messages']

#   result = data[:pointer]
#   pointer += 1
#   return [f"{res['role']}: {res['text']}" for res in result]


def summary(query: Answer, model: str , id: int, options: OllamaOptions | None = None):

        other_dict=[{"role": "system", "content": SYSTEM_PROMPT}]
        n = 4
        cache = get_from_df(id)
        print("log: start process...")
        if cache is None or cache[1] == n:
              print("log: make summary...")

              messages = get_n_message(id, n)
              query = f"CHAT: \n{"\n".join(messages)}"
              if cache is not None:
                # query = query+f"\nCONTEXT: {cache[2]}"
                other_dict.append({"role": "user", "content" : f"CONTEXT: {cache[2]}"})


              request=Answer(
                    query=query, 
                    other_dict=other_dict
                    )
                

              response = controller.answer(
                        request.answer_dict,
                        model=model,
                        options=options.get_dict if options else None
                        )
              
              context = response["content"]
              print("log: save cache...")
              update(list([id, 2, context]))
        else:
             print("log: skip summary...")
             messages = get_n_message(id, 2+cache[1])
             context = cache[2]
             update(list([id, cache[1]+2, context]))

        print("return answer...")
        messages.append(context)
        print(messages)
        return messages, query





if __name__ == "__main__": 
        while True:
          query=Answer(query=input(), query_role="user")
          summary(query=query, model='llama3.2:1b', id=1, options=OllamaOptions(temperature=0))
          input()

