import requests


OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "qwen2.5:3b"


def generate_answer(query, retrieved_chunks):
    if not retrieved_chunks:
        raise ValueError("Không có tài liệu được phép để trả lời.")

    context_parts = []

    for row in retrieved_chunks:
        document_id = row[1]
        title = row[2]
        classification = row[3]
        content = row[5]

        context_parts.append(
            f"[Document #{document_id}] "
            f"{title} | Classification: {classification}\n"
            f"{content}"
        )

    context = "\n\n".join(context_parts)

    prompt = f"""
Bạn là trợ lý hỏi đáp dựa trên tài liệu được cung cấp.

Chỉ sử dụng thông tin có trong CONTEXT để trả lời câu hỏi.
Nếu CONTEXT không chứa thông tin cần thiết, hãy nói rằng
không có đủ thông tin để trả lời.

Không tự suy đoán hoặc bổ sung thông tin ngoài CONTEXT.
YÊU CẦU NGÔN NGỮ:
- Luôn trả lời hoàn toàn bằng tiếng Việt tự nhiên.
- Không trộn tiếng Việt với tiếng Anh, tiếng Indonesia hoặc ngôn ngữ khác.
- Giữ nguyên tên riêng, tên công ty, thuật ngữ kỹ thuật và mã định danh khi cần thiết.
- Nếu CONTEXT có nhiều ngôn ngữ, vẫn trình bày câu trả lời bằng tiếng Việt.
- Chỉ đưa ra câu trả lời, không giải thích về các quy tắc trên.
CONTEXT:
{context}

QUESTION:
{query}

ANSWER:
"""

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0,
                "seed": 42,
            },
        },
        timeout=120,
    )

    response.raise_for_status()

    return response.json()["response"]

