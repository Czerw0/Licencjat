import pandas as pd
import torch

from src.config import NLI_HYPOTHESIS, NLI_THRESHOLD


def nli_probabilities(texts, terms, model, tokenizer, device, batch_size=16):
    """p_entail (softmax z entailment i contradiction) oraz p_entail_3 (softmax z trzech klas) dla par tekst–hipoteza"""
    labels = {label.lower(): index for index, label in model.config.id2label.items()}
    entailment, contradiction = labels["entailment"], labels["contradiction"]
    hypotheses = [NLI_HYPOTHESIS.format(term) for term in terms]
    rows = []
    for start in range(0, len(texts), batch_size):
        batch = tokenizer(texts[start:start + batch_size], hypotheses[start:start + batch_size], truncation="only_first",
                          max_length=512, padding=True, return_tensors="pt").to(device)
        with torch.no_grad():
            logits = model(**batch).logits.float().cpu()
        p_entail = torch.softmax(logits[:, [entailment, contradiction]], dim=1)[:, 0]
        p_entail_3 = torch.softmax(logits, dim=1)[:, entailment]
        rows.append(pd.DataFrame({"p_entail": p_entail.numpy(), "p_entail_3": p_entail_3.numpy()}))
    result = pd.concat(rows, ignore_index=True)
    result["critical"] = result["p_entail"] >= NLI_THRESHOLD
    result["critical_3"] = result["p_entail_3"] >= NLI_THRESHOLD
    return result
