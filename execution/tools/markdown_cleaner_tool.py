"""Tool for cleaning Markdown text for Telegram."""

from typing import Dict, Any
from langchain_core.tools import BaseTool
import re
import logging

logger = logging.getLogger(__name__)

class MarkdownCleanerTool(BaseTool):
    name: str = "markdown_cleaner"
    description: str = """
    Clean LLM output for Telegram by removing Markdown and math symbols.
    Useful for ensuring compatibility with Telegram's message format.
    """

    def _run(self, text: str) -> Dict[str, str]:
        """Clean text and convert to simple HTML for Telegram display."""
        try:
            # Escape HTML special characters first
            text = text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            
            # Convert basic Markdown to HTML
            # Bold: **bold** -> <b>bold</b>
            text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
            # Italic: *italic* -> <i>italic</i>
            text = re.sub(r'\*(.*?)\*', r'<i>\1</i>', text)
            
            # Support numbered lists from bullet points
            lines = text.split('\n')
            cleaned_lines = []
            list_counter = 1

            for line in lines:
                if re.match(r'^\s*[\-\*]\s+', line):
                    stripped_line = re.sub(r'^\s*[\-\*]\s+', '', line)
                    cleaned_lines.append(f"{list_counter}. {stripped_line}")
                    list_counter += 1
                else:
                    cleaned_lines.append(line)
                    if not line.strip():
                        list_counter = 1

            cleaned_text = '\n'.join(cleaned_lines)
            return {"cleaned_text": cleaned_text}

        except Exception as e:
            logger.error(f"Markdown cleaner error: {e}")
            return {"cleaned_text": text}

    async def _arun(self, text: str) -> Dict[str, str]:
        """Async version of run."""
        return self._run(text)
