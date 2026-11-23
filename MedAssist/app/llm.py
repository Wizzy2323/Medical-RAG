
import ollama


def generate_answer(question: str, context: str):
    prompt = f"""
You are a medical document assistant.

Use only the provided context to answer the question.
If the answer is not present in the context,
say that the information is unavailable.
Do not diagnose the patient.

CONTEXT:
{context}

QUESTION:
{question}
"""

    print("Sending request to Ollama...")

    response = ollama.chat(
        model="llama3.2:3b",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    print("Ollama response received.")

    return response["message"]["content"]