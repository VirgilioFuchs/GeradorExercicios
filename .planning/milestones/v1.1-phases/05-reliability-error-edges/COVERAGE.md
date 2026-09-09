# API / Capability Coverage — Phase 5

> Reliability loop + unified API edges. Opt-outs are explicit.
> Phase 5 adds bounded regeneration and aggregate LLM duration logging over the existing dual-provider pipeline; no new provider SDKs.

| capability | decision | reason |
|---|---|---|
| bounded_regen_after_structural_validation | INTEGRATE | RELY-01; D-05; reliability.py hook |
| bounded_regen_after_invalid_llm_response | INTEGRATE | D-05; D-19; ERR-05 typed edges |
| max_retries_cli_and_env | INTEGRATE | D-01..D-04; `--max-retries` + `RELY_MAX_RETRIES` |
| aggregate_llm_duration_log | INTEGRATE | RELY-02; D-16; D-17 |
| empty_openai_choices_typed_error | INTEGRATE | ERR-05 / WR-03 |
| gemini_non_apierror_mapped_path | INTEGRATE | ERR-05 / WR-04 |
| permanent_api_errors_no_retry | INTEGRATE | D-06 auth/timeout/rate-limit/connection |
| phase4_dual_output_preserved | INTEGRATE | D-14; D-22 text stdout + `--out` |
| phase6_math_regen_hook | INTEGRATE | D-07 document `generate_validated_batch` only |
| same_prompt_on_regeneration | INTEGRATE | D-10; no prompts.py edits |
| prompt_repair_on_retry | OPT-OUT | D-11 deferred to future milestone |
| provider_failover | OPT-OUT | out of v1.1 / deferred |
| math_answer_validation | OPT-OUT | Phase 6 MATH-01/02 only |
| per_call_intermediate_duration | OPT-OUT | D-16 aggregate only this phase |
| tenacity_backoff_packages | OPT-OUT | YAGNI; hand loop 0..3 |
| new_pip_dependencies | OPT-OUT | stdlib + existing stack only |
