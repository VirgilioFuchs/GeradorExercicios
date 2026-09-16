"""Host-callable embed seam for exercise batch generation."""

from __future__ import annotations

import logging

from models import ExerciseBatch, GenerationRequest
from failover import generate_with_failover
from reliability import resolve_max_retries
from token_usage import begin_run, flush_token_usage

logger = logging.getLogger("exercise_ai.service")


def generate_batch(request: GenerationRequest) -> ExerciseBatch:
    """Run the generation pipeline and return a validated batch.

    Library path only: no exercise dump, ``--out`` write, fail-log, or process exit.
    Token lifecycle (begin/flush) is owned here; callers may flush again idempotently.
    """
    begin_run()
    try:
        n = resolve_max_retries(None)
        return generate_with_failover(request, max_retries=n)
    finally:
        flush_token_usage()
