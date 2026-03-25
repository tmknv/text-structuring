from typing import List, Optional

# @dataclass, pedantic BaseModel. Чек че я писал саве и лехе
class TextState:
    """
    Центральный объект состояния, который проходит через весь pipeline.

    Использование:
    - создаётся в main.py
    - передаётся в pipeline
    - каждый агент модифицирует его
    """
    def __init__(self, raw_text: str):
        # исходный текст (используется Segmenter)
        self.raw_text: str = raw_text
        # список сегментов текста (заполняется Segmenter)
        self.segments: List[str] = []

        # структурированное представление (заполняется StructureBuilder)
        self.structure: Optional[dict] = None
        # пример:
        # {
        #     "title": "...",
        #     "sections": [...]
        # }

        # текст после стилизации (заполняется Styler)
        self.styled_text: Optional[str] = None
        # финальный текст после исправлений (заполняется Proofreader)
        self.final_text: Optional[str] = None

    def __repr__(self):
        """
        Удобный вывод для дебага (будет использоваться в main.py)
        """
        return (
            f"TextState(\n"
            f"  raw_text={self.raw_text[:30]}...\n"
            f"  segments={len(self.segments)} items\n"
            f"  structure={'yes' if self.structure else 'no'}\n"
            f"  styled_text={'yes' if self.styled_text else 'no'}\n"
            f"  final_text={'yes' if self.final_text else 'no'}\n"
            f")"
        )