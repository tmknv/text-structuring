# ========= SEGMENTER PROMPT =========
# промпты так же разделить на user и system части. Перенести их в .yaml файл
def build_segment_prompt(text: str) -> str:
    return f"""
You are a text processing system.

Task:
Split the given text into sentences.

Rules:
- Each sentence must be on a new line
- Do not add numbering
- Do not add explanations
- Return only the result

Text:
{text}

Output:
Return plain text where each line is a sentence.
"""


def build_structure_prompt(segments: list[str]) -> str:
    joined = "\n".join(segments)

    return f"""
You are a document structuring system.

Task:
Organize the following text segments into a structured JSON format.

Rules:
- Group related segments into sections
- Each section must have a title
- Use the exact JSON structure shown below
- Do not add any text outside JSON
- Do not explain anything

JSON format:
{{
  "sections": [
    {{
      "title": "string",
      "content": ["string"]
    }}
  ]
}}

Example:
Input:
Hello world
Hi there

Output:
{{
  "sections": [
    {{
      "title": "Introduction",
      "content": ["Hello world", "Hi there"]
    }}
  ]
}}

Segments:
{joined}

Output:
Return ONLY valid JSON.
"""
import json

def build_style_prompt(structure: dict) -> str:
    json_structure = json.dumps(structure, ensure_ascii=False, indent=2)

    return f"""
You are a professional text formatter.

Task:
Convert the given structured JSON into a clean, readable text.

Rules:
- Preserve the original meaning
- Do NOT add new information
- Do NOT remove important information
- Keep all content from the input
- Use simple and clear formatting
- Do NOT be creative
- Follow the structure exactly

Formatting rules:
- Each section title on a new line
- Content lines follow under the title
- Separate sections with a blank line

JSON input:
{json_structure}

Output:
Return plain text only.
"""
def build_proofread_prompt(text: str) -> str:
    """
    Промпт для проверки текста.

    Используется:
    - в Proofreader

    Цель:
    - исправить ошибки
    - НЕ менять смысл и структуру
    """

    return f"""
You are a proofreading system.

Task:
Fix grammar, punctuation, and formatting issues in the text.

Rules:
- Do NOT change the meaning
- Do NOT rewrite sentences
- Do NOT change structure
- Do NOT add new content
- Only fix clear errors
- Keep original wording as much as possible

Text:
{text}

Output:
Return corrected text only.
"""