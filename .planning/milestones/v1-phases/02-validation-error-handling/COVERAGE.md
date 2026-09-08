# API Coverage — OpenAI + Gemini

> Full coverage by default. Opt-outs are explicit, reasoned decisions.
> Phase 2 hardens structured exercise generation with semantic validation and typed API/config error handling.

| capability | decision | reason |
|---|---|---|
| structured_exercise_generation_openai | INTEGRATE | |
| structured_exercise_generation_gemini | INTEGRATE | |
| dual_provider_dispatch | INTEGRATE | |
| missing_api_key_diagnostics | INTEGRATE | |
| timeout_error_mapping | INTEGRATE | |
| rate_limit_error_mapping | INTEGRATE | |
| connection_error_mapping | INTEGRATE | |
| authentication_error_mapping | INTEGRATE | |
| empty_refusal_unparseable_response_handling | INTEGRATE | |
| semantic_batch_validation | INTEGRATE | |
| two_layer_stderr_diagnostics | INTEGRATE | |
| fail_fast_cli_stdout_json_only | INTEGRATE | |
| automatic_retry_on_validation_or_api_failure | OPT-OUT | deferred to RELY-* (v2) — Phase 2 abort exit 1 only |
| provider_failover | OPT-OUT | deferred to v2 — Phase 2 reports errors clearly without switching providers |
| progress_percent_ui | OPT-OUT | deferred — Phase 2 uses Gerando…/Validando… stderr labels only |
| pytest_suite | OPT-OUT | deferred to Phase 3 (TEST-*) |
| structured_persistent_log_files | OPT-OUT | deferred to Phase 3 (LOG-*) |
| deep_math_answer_validation | OPT-OUT | deferred to MATH-01 (v2) |
