
import ollama
import os


def generate_answer(question: str, context: str):
    prompt = f"""
You are a medical document assistant.

Use only the provided context to answer the question.
If the answer is not present in the context,
say that the information is unavailable.
Do not diagnose the patient or recommend a treatment plan.
State that a qualified healthcare professional should confirm medical conclusions.

CONTEXT:
{context}

QUESTION:
{question}
"""

    print("Sending request to Ollama...")

    response = ollama.chat(
        model=os.getenv("OLLAMA_MODEL", "llama3.2:3b"),
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    print("Ollama response received.")

    return response["message"]["content"]