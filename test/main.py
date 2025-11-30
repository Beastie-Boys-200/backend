import asyncio
from ollama import Client
import json
from typing import Tuple, List

ollama = Client(host="http://localhost:11434")

with open('/home/oleg/proga/Projects/Hackathon2025/chats/chat1.json', 'r', encoding='utf-8') as f:
    data = json.load(f)['messages']

MODELS = [
    "phi3:mini",
    "phi3:medium",
    "qwen2:7b",
    "mistral:7b",
    "llama3.1:8b",
]

def chat_to_text(messages):
    """Конвертация JSON чата в нормальный текст."""
    lines = []
    for m in messages:
        sender = m.get("from", "unknown")
        text = m.get("text", "")
        lines.append(f"{sender}: {text}")
    return "\n".join(lines)

def summary(chat_text: str) -> str:
    """Создание summary чата."""
    system_prompt = """
    Ты — система, которая делает summary чатов.
    Твой формат ответа:
    - Краткое описание темы
    - Основные события
    - Итоги
    - Задачи/планы (если есть)
    """

    request = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Вот чат:\n{chat_text}"}
    ]
    
    response = ollama.chat(
        model="llama3.1:8b",
        messages=request
    )
    return response["message"]["content"]

async def run_model(model: str, chat_text: str, answer: str) -> Tuple[str, str]:
    """Оценка summary judge-моделью."""
    system_prompt = """
    Ты — экспертная модель для оценки качества summary.
    Критерии:
    1. Полнота
    2. Точность
    3. Краткость
    4. Структура
    5. Пропущенная информация

    Выводи:
    - Сильные стороны
    - Слабые стороны
    - Пропущенное
    - Оценка по критериям (0–10)
    - Итог (0–10)
    """

    request = [
        {"role": "system", "content": system_prompt},
        {
            "role": "user",
            "content":
                f"Исходный текст чата:\n{chat_text}\n\n"
                f"Summary для оценки:\n{answer}"
        }
    ]

    def call():
        return ollama.chat(
            model=model,
            messages=request
        )
    
    response = await asyncio.to_thread(call)
    return model, response["message"]["content"]

async def test_all_models(chat_text: str, summary_text: str) -> List[Tuple[str, str]]:
    tasks = [run_model(model, chat_text, summary_text) for model in MODELS]
    return await asyncio.gather(*tasks)

async def main():

    chat_messages = data[0:10]
    chat_text = chat_to_text(chat_messages)

    # 1) summary
    chat_summary = summary(chat_text)

    print("\n=== SUMMARY ===\n")
    print(chat_summary)

    # # 2) judge оценки
    # print(f"\nЗапускаем асинхронное тестирование {len(MODELS)} моделей...\n")
    # results = await test_all_models(chat_text, chat_summary)

    # print("\n=== РЕЗУЛЬТАТЫ ОЦЕНКИ ===\n")
    # for model, output in results:
    #     print(f"\n--- {model} ---\n{output}\n")

if __name__ == "__main__":
    asyncio.run(main())
