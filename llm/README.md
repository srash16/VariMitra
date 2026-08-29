# VariMitra LLM

This folder is the **training and contract** side of VariMitra. The Android app runs the model on-device with `llama.cpp`. This repo does not ship runtime inference.

## Frozen contract

[`schemas/action.schema.json`](schemas/action.schema.json) is the TRD v2.0 allow-list.

- Strict JSON only.
- `GENERAL_QUESTION` is the only action that may carry free text.
- **SOS is not an LLM action.**
- Facility and Wari facts stay in the database. Do not put them in model weights.

## Dataset

Starter utterances (Marathi, Hindi, English; direct, indirect, short, follow-up, noisy):

```text
python llm/data/intents/generate_starter.py
python llm/eval/validate_actions.py
```

## Later (not in this pass)

1. Keep the action schema frozen.
2. Grow the dataset; keep examples as templates, not memorized places.
3. Fine-tune a 1B–3B instruct model with LoRA / QLoRA (Unsloth or PEFT) on Colab or Kaggle.
4. Benchmark **Qwen 3 1.7B**, **Llama 3.2 3B**, and **Gemma 3 1B** on real devices.
5. Export GGUF `Q4_K_M` (Q5/Q6 only for 8 GB+ RAM) and hand the artifact to Android.

Do not start fine-tuning until the schema is frozen. It is frozen.
