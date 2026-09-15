# API Coverage — OpenAI / Gemini / xAI (Grok) usage extraction

> Phase 9 reads usage metadata from existing provider response objects.
> Full coverage by default. Opt-outs are explicit, reasoned decisions.
> No new provider SDKs; no Admin billing APIs.

| capability | decision | reason |
|---|---|---|
| openai_completion_usage_prompt_tokens | INTEGRATE | D-11; TOKEN-01; `completion.usage.prompt_tokens` |
| openai_completion_usage_completion_tokens | INTEGRATE | D-11; TOKEN-01; `completion.usage.completion_tokens` |
| openai_completion_usage_total_tokens | INTEGRATE | D-11; TOKEN-01; `completion.usage.total_tokens` |
| gemini_usage_metadata_prompt_token_count | INTEGRATE | D-11; TOKEN-01; `response.usage_metadata.prompt_token_count` |
| gemini_usage_metadata_candidates_token_count | INTEGRATE | D-11; TOKEN-01; maps to completion/output tokens |
| gemini_usage_metadata_total_token_count | INTEGRATE | D-11; TOKEN-01; `total_token_count` |
| grok_openai_compatible_usage_tokens | INTEGRATE | D-10; D-11; same `usage` shape as OpenAI-compatible |
| grok_cost_in_usd_ticks | INTEGRATE | D-11; D-14; `usage.cost_in_usd_ticks / 1e10` when present |
| openai_gemini_local_rate_table_usd | INTEGRATE | D-14; D-17; USD/1M input+output by model string |
| missing_usage_fields_as_indisponivel | INTEGRATE | D-09; never fabricate numeric zero |
| ndjson_day_provider_persist | INTEGRATE | D-01; D-02; D-03; TOKEN-02 |
| stderr_usage_tag | INTEGRATE | D-07; D-08; TOKEN-03 |
| openai_admin_usage_billing_api | OPT-OUT | D-15 deferred — live Admin/org billing out of scope |
| google_cloud_billing_admin_api | OPT-OUT | D-15 deferred — live Admin billing out of scope |
| xai_account_billing_dashboard_api | OPT-OUT | D-15 deferred — live Admin billing out of scope |
| public_pricing_page_scrape | OPT-OUT | D-17 deferred — no runtime scrape of pricing pages |
| streaming_token_deltas | OPT-OUT | CONTEXT deferred — non-streaming pipeline only |
| multi_currency_brl_fx | OPT-OUT | CONTEXT deferred — USD only (D-15) |
| phoenix_observability_platform | OPT-OUT | CONTEXT deferred — KISS collector only (D-20) |
