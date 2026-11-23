"""
RAG evaluation over 30+ medical queries.

Measures retrieval accuracy, answer accuracy and end-to-end latency, and
sweeps chunk size / top-k to pick the best settings.

Run from the project root:
    python -m app.evaluate            # retrieval sweep only (fast)
    python -m app.evaluate --llm      # also answer accuracy + latency with Ollama
"""
import sys
import time

from app.chunker import chunk_text
from app.retrieval import embed_texts, build_index, search_index

REPORT = """
Patient Ravi Sharma is a 45-year-old male. He is a non-smoker and drinks alcohol occasionally.
Chief complaint: occasional headaches for the past 3 weeks.
Vitals: blood pressure 130/85 mmHg, heart rate 78 beats per minute, temperature 98.4 F, oxygen saturation 98 percent.
Weight is 82 kg and height is 175 cm, giving a BMI of 26.8.
Complete blood count: hemoglobin 11.2 g/dL, WBC 7,200 per microliter, platelets 250,000 per microliter.
Ferritin was 15 ng/mL and vitamin D was 18 ng/mL.
Fasting blood glucose was 112 mg/dL and HbA1c was 6.1 percent.
Lipid profile: total cholesterol 218 mg/dL, LDL 140 mg/dL, HDL 42 mg/dL, triglycerides 180 mg/dL.
Serum creatinine was 0.9 mg/dL. TSH was 2.4 mIU/L.
ECG showed normal sinus rhythm. Chest X-ray was clear.
The patient is allergic to penicillin. Past surgical history includes an appendectomy in 2015.
Family history: father has type 2 diabetes.
Prescribed ferrous sulfate 325 mg once daily for iron deficiency anemia.
Prescribed atorvastatin 10 mg at night for elevated cholesterol.
Advised a low-sodium diet and a 30 minute walk every day.
Follow-up visit scheduled in 6 weeks.
"""

# (question, keyword that must appear in the retrieved chunks / the answer)
QUERIES = [
    ("How old is the patient?", "45-year-old"),
    ("Does the patient smoke?", "non-smoker"),
    ("What is the chief complaint?", "headaches"),
    ("What is the blood pressure?", "130/85"),
    ("What is the heart rate?", "78 beats"),
    ("What is the body temperature?", "98.4"),
    ("What is the oxygen saturation?", "98 percent"),
    ("What is the patient's weight?", "82 kg"),
    ("What is the patient's height?", "175 cm"),
    ("What is the BMI?", "26.8"),
    ("What was the hemoglobin level?", "11.2"),
    ("What is the WBC count?", "7,200"),
    ("What is the platelet count?", "250,000"),
    ("What was the ferritin level?", "15 ng/mL"),
    ("What was the vitamin D level?", "18 ng/mL"),
    ("What was the fasting blood glucose?", "112"),
    ("What is the HbA1c?", "6.1"),
    ("What is the total cholesterol?", "218"),
    ("What is the LDL value?", "140"),
    ("What is the HDL value?", "42 mg/dL"),
    ("What are the triglycerides?", "180"),
    ("What is the serum creatinine?", "0.9"),
    ("What is the TSH level?", "2.4"),
    ("What did the ECG show?", "sinus rhythm"),
    ("What did the chest X-ray show?", "clear"),
    ("Is the patient allergic to any drug?", "penicillin"),
    ("Has the patient had any surgery?", "appendectomy"),
    ("Is there a family history of diabetes?", "father"),
    ("Which iron medicine was prescribed?", "ferrous sulfate"),
    ("Which medicine was prescribed for cholesterol?", "atorvastatin"),
    ("What diet advice was given?", "low-sodium"),
    ("When is the follow-up visit?", "6 weeks"),
]

CHUNK_SIZES = [30, 50, 100, 200]
TOP_KS = [1, 2, 3, 5]


def retrieval_accuracy(chunk_size, top_k):
    overlap = chunk_size // 5
    chunks = chunk_text(REPORT, chunk_size, overlap)
    index = build_index(embed_texts(chunks))

    hits = 0
    start = time.time()

    for question, keyword in QUERIES:
        retrieved = search_index(index, chunks, question, top_k)
        if any(keyword.lower() in c.lower() for c in retrieved):
            hits += 1

    avg_ms = (time.time() - start) / len(QUERIES) * 1000

    return hits / len(QUERIES), avg_ms, len(chunks)


def answer_eval(chunk_size, top_k):
    from app.llm import generate_answer

    overlap = chunk_size // 5
    chunks = chunk_text(REPORT, chunk_size, overlap)
    index = build_index(embed_texts(chunks))

    correct = 0
    total_latency = 0.0

    for question, keyword in QUERIES:
        start = time.time()
        context = "\n\n".join(search_index(index, chunks, question, top_k))
        answer = generate_answer(question, context)
        total_latency += time.time() - start

        if keyword.lower() in answer.lower():
            correct += 1

    return correct / len(QUERIES), total_latency / len(QUERIES)


if __name__ == "__main__":
    print(f"Evaluating {len(QUERIES)} medical queries\n")
    print(f"{'chunk':>6} {'top_k':>6} {'#chunks':>8} {'retrieval acc':>14} {'ms/query':>9}")

    results = []

    for size in CHUNK_SIZES:
        for k in TOP_KS:
            acc, ms, n = retrieval_accuracy(size, k)
            results.append((acc, -k, -ms, size, k))
            print(f"{size:>6} {k:>6} {n:>8} {acc:>13.0%} {ms:>9.1f}")

    # best accuracy; ties -> smaller top_k (less context), then faster
    best = max(results)
    best_size, best_k = best[3], best[4]
    print(f"\nBest config: chunk_size={best_size}, top_k={best_k} "
          f"(retrieval accuracy {best[0]:.0%})")

    if "--llm" in sys.argv:
        acc, latency = answer_eval(best_size, best_k)
        print(f"Answer accuracy: {acc:.0%}")
        print(f"Avg end-to-end latency: {latency:.2f}s per query")
