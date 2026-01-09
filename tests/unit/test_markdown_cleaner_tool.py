import pytest
from execution.tools.markdown_cleaner_tool import MarkdownCleanerTool

def test_clean_bold_italic():
    tool = MarkdownCleanerTool()
    text = "**Bold** and *Italic*"
    result = tool._run(text)
    assert result["cleaned_text"] == "Bold and Italic"

def test_clean_math_symbols():
    tool = MarkdownCleanerTool()
    text = "5 * 10 + 2 - 1 / 2"
    result = tool._run(text)
    assert result["cleaned_text"] == "5 fois 10 plus 2 moins 1 divisé par 2"

def test_clean_bullet_list():
    tool = MarkdownCleanerTool()
    text = "- Item A\n- Item B\n* Item C"
    result = tool._run(text)
    expected = "1. Item A\n2. Item B\n3. Item C"
    assert result["cleaned_text"] == expected

def test_clean_mixed_list_reset():
    tool = MarkdownCleanerTool()
    text = "- A\n- B\n\n- C"
    result = tool._run(text)
    expected = "1. A\n2. B\n\n1. C"
    assert result["cleaned_text"] == expected
