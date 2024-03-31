import ast
import importlib.metadata
import pathlib

import anywidget
import traitlets
import pandas as pd
import plotly.express as px

from bs4 import BeautifulSoup
from enum import Enum
from markdown import markdown
from markdown.extensions.codehilite import CodeHiliteExtension
from markdown.extensions.extra import ExtraExtension
from plotly.graph_objs._figurewidget import FigureWidget
from typing import Dict, List

from .llm import LLM

try:
    __version__ = importlib.metadata.version("justplotme")
except importlib.metadata.PackageNotFoundError:
    __version__ = "unknown"


class Role(Enum):
  USER: str = "user"
  ASSISTANT: str = "assistant"


class PlotMe(anywidget.AnyWidget):
  _esm = pathlib.Path(__file__).parent / "static" / "widget.js"
  _css = pathlib.Path(__file__).parent / "static" / "widget.css"
  chat = traitlets.List().tag(sync=True)
  plot_html = traitlets.Unicode().tag(sync=True)

  def __init__(self, df: pd.DataFrame, api_key:str, *args, **kwargs) -> None:
    super().__init__(*args, **kwargs)
    self.df = df
    self.llm = LLM(api_key=api_key)
    self.on_msg(self._handle_custom_msg)
    self.append_chats([{
      'role': Role.ASSISTANT.value,
      'content': f"The dataframe (shape: {self.df.shape}) has columns: {self.df.columns.tolist()}"
    }])

  def _handle_custom_msg(self, data: Dict, buffers: List) -> None:
    if data["type"] == "chat":
      content = data["content"]
      self.get_user_msg(content)
      self.get_response_msg()

  def get_user_msg(self, content: str) -> None:
    self.append_chats([{'role': Role.USER.value, 'content': content}])

  def get_response_msg(self) -> None:
    chat_to_oai = [{k: v for k, v in chat.items() if k != "html"} for chat in self.chat]
    response = self.llm.chat(chat_to_oai)
    if response != LLM.error_message:
      try:
        if self.is_valid_expression(response):
          fig = eval(response)
          self.plot(fig)
        else:
          raise Exception("Invalid expression")
      except Exception as e:
        self.error = str(e)
        response = f"{response}\n\n This LLM response is invalid. Please rephrase."
    self.append_chats([{'role': Role.ASSISTANT.value, 'content': response}])

  def is_valid_expression(self, expression: str) -> bool:
    try:
      ast.parse(expression)
      return True
    except SyntaxError:
      return False

  def append_chats(self, chats: List[Dict[str, str]]) -> None:
    self.chat = self.chat + [
      {"role": chat['role'], "content": chat['content'], "html": self.get_html(chat['content'])}
    for chat in chats]

  def get_html(self, txt : str) -> str:
    html = markdown(
      txt,
      extensions=[CodeHiliteExtension(css_class="highlight"), ExtraExtension()],
      output_format="html5"
    )
    return html
  
  def plot(self, fig: FigureWidget) -> None:
    plot_html = fig.to_html(full_html=False, include_plotlyjs='cdn', div_id="plot-container")
    soup = BeautifulSoup(plot_html, 'html.parser')
    self.plot_html = soup.findAll("script")[-1].text
