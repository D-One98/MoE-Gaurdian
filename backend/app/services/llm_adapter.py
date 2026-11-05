from abc import ABC, abstractmethod
from typing import Optional, Tuple
from app.schemas.contracts import ExecutionState


class LLMProviderAdapter(ABC):
    @abstractmethod
    def is_configured(self) -> bool:
        pass

    @abstractmethod
    def propose_rewrite(self, span_text: str, rule_description: str) -> Tuple[Optional[str], ExecutionState]:
        pass


class NullDeterministicAdapter(LLMProviderAdapter):
    def is_configured(self) -> bool:
        return False

    def propose_rewrite(self, span_text: str, rule_description: str) -> Tuple[Optional[str], ExecutionState]:
        return None, ExecutionState.NOT_APPLICABLE