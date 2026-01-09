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
        """Clean text for Telegram display."""
        try:
            # Remove bold/italic Markdown
            # Telegram supports some HTML/Markdown but this tool follows the plan's requirement
            # to convert them to plain text or specific formats.
            
            # Remove bold: **bold** -> bold
            text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
            # Remove italic: *italic* -> italic
            text = re.sub(r'\*(.*?)\*', r'\1', text)
            # Remove __ (another bold/underline)
            text = re.sub(r'__(.*?)__', r'\1', text)

            # Replace math symbols as per plan
            # (Note: we use spaces to avoid mangling words)
            text = text.replace(' + ', ' plus ')
            text = text.replace(' - ', ' moins ')
            text = text.replace(' * ', ' fois ')
            text = text.replace(' / ', ' divisé par ')

            # Convert bullet lists (-, *) to numbered lists
            lines = text.split('\n')
            cleaned_lines = []
            list_counter = 1

            for line in lines:
                # Match line starting with - or * followed by space
                if re.match(r'^\s*[\-\*]\s+', line):
                    stripped_line = re.sub(r'^\s*[\-\*]\s+', '', line)
                    cleaned_lines.append(f"{list_counter}. {stripped_line}")
                    list_counter += 1
                else:
                    cleaned_lines.append(line)
                    # Optional: reset counter if line is empty or doesn't look like a list anymore
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
