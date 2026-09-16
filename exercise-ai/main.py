"""CLI entry point and pipeline orchestrator for exercise generation."""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

# Ensure local package path resolution
current_dir = Path(__file__).resolve().parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

# Multi-path .env resolution (exercise-ai/.env or root/.env)
env_path = current_dir / ".env"
if not env_path.exists():
    env_path = current_dir.parent / ".env"
load_dotenv(dotenv_path=env_path)

from models import MAX_QUANTIDADE, DificuldadeEnum, ExerciseBatch, GenerationRequest
from output_paths import resolve_success_out_path, write_fail_error_log
import reliability
from service import ConfigError, generate_batch
from token_usage import flush_token_usage

logger = logging.getLogger("exercise_ai")

_DEFAULT_MATERIA = "Matemática"
_DEFAULT_TOPICO = "Equação do primeiro grau"
_DEFAULT_DIFICULDADE = "facil"
_DEFAULT_QUANTIDADE = 3
_MAX_QUANTIDADE = MAX_QUANTIDADE


class _StderrStream:
    """Always write to the current sys.stderr (works under redirect_stderr)."""

    def write(self, msg: str) -> int:
        return sys.stderr.write(msg)

    def flush(self) -> None:
        sys.stderr.flush()


def _configure_logging() -> None:
    """Send development LOG-01 events to stderr (no log files)."""
    if logger.handlers:
        return
    handler = logging.StreamHandler(_StderrStream())
    handler.setFormatter(logging.Formatter("%(levelname)s %(name)s: %(message)s"))
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    logger.propagate = False


def format_batch_text(batch: ExerciseBatch) -> str:
    """Render D-15 human-readable stdout layout for a validated batch."""
    blocks: list[str] = []
    for i, ex in enumerate(batch.exercicios, start=1):
        blocks.append(
            "\n".join(
                [
                    f"### Exercício {i}",
                    f"Enunciado: {ex.enunciado}",
                    f"Resposta: {ex.resposta}",
                    f"Explicação: {ex.explicacao}",
                ]
            )
        )
    return "\n\n".join(blocks)


def _ensure_provider_key(provider: str) -> None:
    """Fail with a provider-specific PT message when the chosen key is missing (D-11)."""
    if provider == "openai":
        if not os.getenv("LLM_API_KEY", "").strip():
            raise ConfigError(
                "Chave ausente para o provedor openai. Defina LLM_API_KEY no arquivo .env.",
                kind="missing_key",
            )
    elif provider == "gemini":
        if not os.getenv("GEMINI_API_KEY", "").strip():
            raise ConfigError(
                "Chave ausente para o provedor gemini. Defina GEMINI_API_KEY no arquivo .env.",
                kind="missing_key",
            )
    elif provider == "grok":
        if not os.getenv("GROK_API_KEY", "").strip():
            raise ConfigError(
                "Chave ausente para o provedor grok. Defina GROK_API_KEY no arquivo .env.",
                kind="missing_key",
            )


def _positive_quantidade(value: str) -> int:
    """Parse --quantidade; reject non-int, <=0, and >40 before any LLM call."""
    try:
        qty = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(
            f"quantidade inválida '{value}': informe um inteiro entre 1 e {_MAX_QUANTIDADE}."
        ) from exc
    if qty <= 0 or qty > _MAX_QUANTIDADE:
        raise argparse.ArgumentTypeError(
            f"quantidade inválida '{qty}': o máximo 40 exercícios é permitido (1–{_MAX_QUANTIDADE})."
        )
    return qty


def _max_retries_type(value: str) -> int:
    """Parse --max-retries; allow only 0|1|2|3 before any LLM call (D-04)."""
    try:
        n = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(
            f"max-retries inválido '{value}': use um inteiro 0, 1, 2 ou 3."
        ) from exc
    if n not in {0, 1, 2, 3}:
        raise argparse.ArgumentTypeError(
            f"max-retries inválido '{n}': use um inteiro 0, 1, 2 ou 3."
        )
    return n


def build_parser() -> argparse.ArgumentParser:
    """Portuguese argparse surface for CLI-04 (D-01..D-20)."""
    parser = argparse.ArgumentParser(
        prog="main.py",
        description=(
            "Gera exercícios de matemática via LLM. "
            f"Defaults da demo quando omitidos: matéria={_DEFAULT_MATERIA}; "
            f"tópico={_DEFAULT_TOPICO}; dificuldade={_DEFAULT_DIFICULDADE}; "
            f"quantidade={_DEFAULT_QUANTIDADE}."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--materia",
        default=_DEFAULT_MATERIA,
        help=f"Matéria dos exercícios (padrão: {_DEFAULT_MATERIA})",
    )
    parser.add_argument(
        "--topico",
        default=_DEFAULT_TOPICO,
        help=f"Tópico específico (padrão: {_DEFAULT_TOPICO})",
    )
    parser.add_argument(
        "--dificuldade",
        choices=["facil", "medio", "dificil"],
        default=_DEFAULT_DIFICULDADE,
        help=f"Nível de dificuldade: facil|medio|dificil (padrão: {_DEFAULT_DIFICULDADE})",
    )
    parser.add_argument(
        "--quantidade",
        type=_positive_quantidade,
        default=_DEFAULT_QUANTIDADE,
        help=f"Quantidade de exercícios (1–{_MAX_QUANTIDADE}; padrão: {_DEFAULT_QUANTIDADE})",
    )
    parser.add_argument(
        "--provider",
        choices=["openai", "gemini", "grok"],
        default=None,
        help="Provedor LLM para esta execução: openai|gemini|grok (opcional)",
    )
    parser.add_argument(
        "--reasoning",
        choices=["none", "low", "medium", "high"],
        default=None,
        help=(
            "Esforço de raciocínio/thinking: none|low|medium|high "
            "(padrão: medium via LLM_REASONING_EFFORT ou default)"
        ),
    )
    parser.add_argument(
        "--out",
        required=True,
        help=(
            "Arquivo JSON de saída. Caminho relativo → "
            "exercicios-gerados/success/<nome>; absoluto permanece como informado"
        ),
    )
    parser.add_argument(
        "--max-retries",
        type=_max_retries_type,
        default=None,
        help=(
            "Regenerações após a primeira tentativa (0–3). "
            "Se omitido, usa RELY_MAX_RETRIES ou padrão 1"
        ),
    )
    return parser


def run(
    request: GenerationRequest,
    out_path: Path | str,
    max_retries: int | None = None,
) -> None:
    """CLI adapter: delegate pipeline to service, then present / write / exit."""
    _configure_logging()

    logger.info("Início da geração de exercícios")
    logger.info(
        "Parâmetros: materia=%s topico=%s dificuldade=%s quantidade=%s",
        request.materia,
        request.topico,
        request.dificuldade.value,
        request.quantidade,
    )

    # Bridge CLI --max-retries via env so generate_batch stays kwargs-free (D-01).
    _env_key = "RELY_MAX_RETRIES"
    _had_key = _env_key in os.environ
    _prior = os.environ.get(_env_key)

    try:
        if max_retries is not None:
            os.environ[_env_key] = str(max_retries)
        try:
            validated_batch = generate_batch(request)

            print(format_batch_text(validated_batch))
            out = resolve_success_out_path(out_path)
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(
                json.dumps(
                    validated_batch.model_dump(),
                    indent=2,
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )
            logger.info("Geração concluída com sucesso → %s", out)
        finally:
            if max_retries is not None:
                if _had_key:
                    os.environ[_env_key] = _prior  # type: ignore[assignment]
                else:
                    os.environ.pop(_env_key, None)

    except ValueError as val_err:
        logger.error("Falha de validação ou configuração: %s", val_err)
        print(str(val_err), file=sys.stderr)
        try:
            reliability._write_postmortem(reliability.POSTMORTEM_PATH)
        except OSError:
            pass
        try:
            write_fail_error_log(str(val_err))
        except OSError:
            pass
        sys.exit(1)
    except RuntimeError as run_err:
        logger.error("Falha na geração: %s", run_err)
        print(str(run_err), file=sys.stderr)
        try:
            write_fail_error_log(str(run_err))
        except OSError:
            pass
        sys.exit(1)
    except Exception as exc:
        logger.error("Falha inesperada: %s", exc)
        print(str(exc), file=sys.stderr)
        try:
            write_fail_error_log(str(exc))
        except OSError:
            pass
        sys.exit(1)
    finally:
        # Safety-net flush (service already flushes); SystemExit still runs finally —
        # buffer cleared so a second flush is a no-op (idempotent).
        try:
            flush_token_usage()
        except OSError:
            pass


def main(argv: list[str] | None = None) -> None:
    """Parse CLI args and run the generation pipeline."""
    if argv is None:
        argv = sys.argv[1:]

    # Interactive wizard: first token `gerar` (D-01); argparse unchanged otherwise (D-02).
    if argv and argv[0] == "gerar":
        if len(argv) > 1:
            from wizard import _EXTRA_ARGS_MSG

            print(_EXTRA_ARGS_MSG, file=sys.stderr)
            sys.exit(2)
        from wizard import run_wizard

        run_wizard()
        return

    parser = build_parser()
    args = parser.parse_args(argv)

    if args.provider:
        os.environ["LLM_PROVIDER"] = args.provider
        try:
            _ensure_provider_key(args.provider)
        except ValueError as err:
            print(str(err), file=sys.stderr)
            sys.exit(1)

    if args.reasoning is not None:
        os.environ["LLM_REASONING_EFFORT"] = args.reasoning

    request = GenerationRequest(
        materia=args.materia,
        topico=args.topico,
        dificuldade=DificuldadeEnum(args.dificuldade),
        quantidade=args.quantidade,
    )
    run(request, out_path=args.out, max_retries=args.max_retries)


if __name__ == "__main__":
    main()
