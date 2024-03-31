from openai import OpenAI
from typing import Dict, List

class LLM:
  error_message: str = "That query is unclear. Please rephrase."
  system_chat: Dict[str, str] = {
    "role": "system",
    "content": f"You are an assistant helping users to draw plotly plots. Always return single line plotly express expression that returns a plot. Never return a multi-line expression. Assume all imports are done already. If there is no clear way to return a plot, return '{error_message}'. The dataframe is at self.df."
  }

  def __init__(self, api_key) -> None:
    assert api_key, "API key is required"
    self.client = OpenAI(api_key=api_key)

  def chat(self, messages: List[Dict[str, str]]) -> str:
    messages = [self.system_chat] + messages
    response = self.client.chat.completions.create(
      messages=messages,
      model="gpt-3.5-turbo",
      temperature=1.0,
    )
    return response.choices[0].message.content
