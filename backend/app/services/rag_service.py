"""Offline RAG service for the medical knowledge agent.

Production path: LangChain + ChromaDB + a quantized local LLM
(Llama-3-8B-Instruct or similar), as described in docs/BLUEPRINT.md
section 8. Those packages need network access to install and a GPU/
NPU to run at usable speed, so this file ships a fully-working,
dependency-light fallback: TF-IDF retrieval (scikit-learn, already
available offline) over a small curated knowledge base, plus a
template-based explanation generator. Swap `LocalLLM.generate()` for
a real llama.cpp / transformers call in production -- the retrieval
interface (`RAGService.explain`) doesn't need to change.
"""
from __future__ import annotations
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

KNOWLEDGE_BASE = [
    {
        "id": "resp_distress_1",
        "condition": "respiratory_distress",
        "text": ("Rising respiratory rate combined with falling oxygen saturation "
                  "and reduced activity often precedes acute respiratory distress. "
                  "Sustained trends over several hours are more significant than "
                  "single readings."),
    },
    {
        "id": "resp_distress_2",
        "condition": "respiratory_distress",
        "text": ("In patients with COPD, a gradual rise in resting respiratory rate "
                  "over hours can indicate an oncoming exacerbation; early caregiver "
                  "awareness allows time for bronchodilator use or a clinic visit "
                  "before an emergency room visit becomes necessary."),
    },
    {
        "id": "tremor_1",
        "condition": "tremor_escalation",
        "text": ("An increase in resting tremor amplitude and a shift toward the "
                  "4-6 Hz frequency band is consistent with Parkinsonian tremor "
                  "escalation, which can precede a fall or freezing episode."),
    },
    {
        "id": "tremor_2",
        "condition": "tremor_escalation",
        "text": ("New tremor onset accompanied by irregular breathing can indicate "
                  "an overlap condition and warrants closer caregiver attention "
                  "than either symptom alone."),
    },
    {
        "id": "cardiac_1",
        "condition": "cardiac_abnormality",
        "text": ("A sustained elevated heart rate at rest, especially paired with "
                  "reduced activity level, can indicate cardiac strain and should "
                  "be reviewed against the patient's personal baseline rather than "
                  "a generic population threshold."),
    },
    {
        "id": "general_1",
        "condition": "general",
        "text": ("This is decision support for a caregiver, not a diagnosis. "
                  "Persistent or worsening symptoms should be confirmed with a "
                  "clinician or emergency services."),
    },
]


class RAGService:
    def __init__(self, knowledge_base=None):
        self.kb = knowledge_base or KNOWLEDGE_BASE
        self.vectorizer = TfidfVectorizer(stop_words="english")
        self._matrix = self.vectorizer.fit_transform([d["text"] for d in self.kb])

    def retrieve(self, query: str, condition: str | None = None, k: int = 2) -> list[dict]:
        candidates = self.kb
        indices = list(range(len(self.kb)))
        if condition:
            filtered = [(i, d) for i, d in enumerate(self.kb)
                        if d["condition"] in (condition, "general")]
            if filtered:
                indices, candidates = zip(*filtered)
                indices = list(indices)

        query_vec = self.vectorizer.transform([query])
        sims = cosine_similarity(query_vec, self._matrix[indices]).flatten()
        ranked = sorted(zip(indices, sims), key=lambda x: -x[1])[:k]
        return [self.kb[i] for i, _ in ranked]

    def explain(self, condition: str, tier: str, hours_ahead: float | None) -> str:
        query = f"{condition} risk tier {tier}"
        context = self.retrieve(query, condition=condition, k=2)
        context_text = " ".join(c["text"] for c in context)

        horizon_phrase = f"within approximately {hours_ahead} hours" if hours_ahead else "currently"
        # Template-based generation standing in for the local LLM call.
        # A production LocalLLM.generate(prompt) call would combine this
        # same context + patient history into a fluent paragraph.
        return (
            f"Risk tier: {tier}. The system projects {condition.replace('_', ' ')} "
            f"{horizon_phrase}, based on the patient's own trend versus their personal "
            f"baseline. Relevant context: {context_text}"
        )
