from text_structuring.langgraph_pipeline import process_text
from text_structuring.llm.reader import reader


if __name__ == "__main__":
    raw_text = reader('./text_structuring/llm/testdox.docx')
    result = process_text(raw_text)
    
    print("\nPIPELINE EXECUTION COMPLETE")
    print("=" * 80)
    
    # Вывод каждого агента
    for response in result.responses:
        if response:
            print(f"\n{response.agent_name}:")
            print(f"  Confidence: {response.confidence:.0%}")
            print(f"  Status: {response.vote.name}")
            if response.reasons:
                print(f"  Reasons: {response.reasons[0]}")
    
    print("\n" + "=" * 80)
    print("\nFINAL OUTPUT:")
    print("-" * 80)
    print(result.final_text)
