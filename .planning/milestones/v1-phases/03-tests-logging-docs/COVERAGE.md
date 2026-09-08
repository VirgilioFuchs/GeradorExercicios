# API Coverage — Phase 3 (Tests, Logging & Docs)

> Full coverage by default. Opt-outs are explicit, reasoned decisions.
> Phase 3 does not add new LLM provider capabilities; it hardens regression tests,
> development logging/redaction, and root documentation on top of Phase 1–2 APIs.

| capability | decision | reason |
|---|---|---|
| structured_exercise_generation_openai | INTEGRATE | unchanged from Phase 2 — suite mocks only |
| structured_exercise_generation_gemini | INTEGRATE | unchanged from Phase 2 — suite mocks only |
| dual_provider_dispatch | INTEGRATE | unchanged — README documents LLM_PROVIDER |
| missing_api_key_diagnostics | INTEGRATE | durable ERR-01 tests in test_generators.py |
| timeout_error_mapping | INTEGRATE | durable mapper tests (mocked) |
| rate_limit_error_mapping | INTEGRATE | durable mapper tests (mocked) |
| connection_error_mapping | INTEGRATE | durable mapper tests (mocked) |
| authentication_error_mapping | INTEGRATE | durable mapper + anti-leakage tests |
| empty_refusal_unparseable_response_handling | INTEGRATE | covered via mocks; dumps redact env secrets |
| semantic_batch_validation | INTEGRATE | durable TEST-02 pytest suite |
| two_layer_stderr_diagnostics | INTEGRATE | LOG-01 events + sanitized [API:*] (LOG-02) |
| fail_fast_cli_stdout_json_only | INTEGRATE | durable test_main.py |
| pytest_suite | INTEGRATE | Phase 3 primary deliverable (TEST-*) |
| development_logging_no_secrets | INTEGRATE | LOG-01/LOG-02 |
| root_readme_setup_run | INTEGRATE | SCAF-04 |
| automatic_retry_on_validation_or_api_failure | OPT-OUT | deferred to RELY-* (v2) |
| provider_failover | OPT-OUT | deferred to v2 |
| github_actions_ci | OPT-OUT | deferred — D-10; document pytest only |
| structured_persistent_log_files | OPT-OUT | deferred — D-07; stderr only, no Phoenix |
| deep_math_answer_validation | OPT-OUT | deferred to MATH-01 (v2) |
| argparse_cli | OPT-OUT | deferred to CLI-04 (v2) |
