"""Dünner LLM-Wrapper. Kapselt Anbieter (Anthropic/OpenAI) und einen 'dryrun'-Modus,
damit das walking skeleton ohne API-Schlüssel lauffähig ist. temperature=0 fix."""
from __future__ import annotations
import os, json
from config import MemoryConfig


class LLMClient:
    def __init__(self, cfg: MemoryConfig):
        self.cfg = cfg
        self.provider = cfg.llm_provider

    def complete(self, system: str, user: str, json_mode: bool = False) -> str:
        if self.provider == "dryrun":
            return self._dryrun(user, json_mode)
        if self.provider == "anthropic":
            import anthropic
            client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
            msg = client.messages.create(
                model=self.cfg.llm_model, max_tokens=1024,
                temperature=self.cfg.temperature, system=system,
                messages=[{"role": "user", "content": user}],
            )
            return msg.content[0].text
        if self.provider == "openai":
            from openai import OpenAI
            client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
            kwargs = {"response_format": {"type": "json_object"}} if json_mode else {}
            r = client.chat.completions.create(
                model=self.cfg.llm_model, temperature=self.cfg.temperature,
                messages=[{"role": "system", "content": system},
                          {"role": "user", "content": user}], **kwargs)
            return r.choices[0].message.content
        raise ValueError(self.provider)

    def embed(self, text: str) -> list[float]:
        if self.provider == "dryrun":
            # deterministisches Pseudo-Embedding nur fürs Skeleton
            import hashlib, struct
            h = hashlib.sha256(text.encode()).digest()
            return [b / 255.0 for b in h][:16]
        from openai import OpenAI
        client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
        return client.embeddings.create(
            model=self.cfg.embedding_model, input=text).data[0].embedding

    def _dryrun(self, user: str, json_mode: bool) -> str:
        if json_mode:
            return json.dumps({"memories": []})
        return "[DRYRUN] Antwort des LLM auf Basis des injizierten Kontexts."
