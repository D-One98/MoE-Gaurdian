from typing import Tuple, Optional
from app.schemas.contracts import AnchorResolutionStatus


def resolve_block_text_anchor(
    block_text: str,
    matched_text: str,
    occ_start: Optional[int] = None,
    context_window: int = 32,
) -> Tuple[Optional[str], Optional[str], AnchorResolutionStatus]:
    if not matched_text or matched_text not in block_text:
        return None, None, AnchorResolutionStatus.UNRESOLVED_SIDEBAR_ONLY

    occurrences = []
    start_idx = 0
    while True:
        idx = block_text.find(matched_text, start_idx)
        if idx == -1:
            break
        occurrences.append(idx)
        start_idx = idx + 1

    if not occurrences:
        return None, None, AnchorResolutionStatus.UNRESOLVED_SIDEBAR_ONLY

    target_idx = occ_start if (occ_start is not None and occ_start in occurrences) else occurrences[0]
    p_start = max(0, target_idx - context_window)
    s_end = min(len(block_text), target_idx + len(matched_text) + context_window)

    prefix_context = block_text[p_start:target_idx]
    suffix_context = block_text[target_idx + len(matched_text) : s_end]

    if len(occurrences) == 1:
        return prefix_context, suffix_context, AnchorResolutionStatus.RESOLVED_UNIQUE

    composite = f"{prefix_context}{matched_text}{suffix_context}"
    first_comp = block_text.find(composite)
    second_comp = block_text.find(composite, first_comp + 1) if first_comp != -1 else -1

    if second_comp == -1:
        return prefix_context, suffix_context, AnchorResolutionStatus.RESOLVED_UNIQUE

    return prefix_context, suffix_context, AnchorResolutionStatus.AMBIGUOUS_FALLBACK_TO_BLOCK