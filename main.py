# main.py — Тестовый скрипт для сравнения подходов

from text_structuring.llm.reader import reader
from text_structuring.schemas.text import TextState
import json

# Импортируем агентов
from text_structuring.agents import (
    Segmenter,
    StructureBuilder,
    Styler,
    Proofreader
)

from text_structuring.llm.baseline import Baseline
from text_structuring.llm.judge import Evaluator

def main():
    raw_text = reader('./text_structuring/artifacts/data/testdox.docx')
    # ====================== МУЛЬТИАГЕНТНЫЙ ПОДХОД ======================
    multi_state = TextState(raw_text=raw_text)
    
    pipeline = [Segmenter(), StructureBuilder(), Styler(), Proofreader()]
    
    for agent in pipeline:
        multi_state = agent.run(multi_state)

    # ====================== BASELINE (ОДИН ПРОМПТ) ======================
    baseline = Baseline()
    baseline_state = baseline.run(raw_text)
    
    # ====================== СРАВНЕНИЕ ======================
    evaluator = Evaluator()
    evaluation = evaluator.run_comparison(
        original_text=raw_text,
        multi_agent_text=multi_state.final_text,
        baseline_text=baseline_state.final_text
    )

    # ====================== ВЫВОД РЕЗУЛЬТАТОВ ======================
    print("\n" + "=" * 60)
    print("РЕЗУЛЬТАТЫ СРАВНЕНИЯ")
    print("=" * 60)

    if "error" in evaluation:
        print("Ошибка оценки:", evaluation["error"])
    else:
        print(f"Победитель: {evaluation.get('winner', 'Не определён')}")
        print(f"Краткий вывод: {evaluation.get('summary', '')}")
        print(f"Рекомендация: {evaluation.get('recommendation', '')}")

        print("\nПодробные оценки:")
        print(json.dumps(evaluation, ensure_ascii=False, indent=2))

    print("\nТестирование завершено.")


if __name__ == "__main__":
    main()