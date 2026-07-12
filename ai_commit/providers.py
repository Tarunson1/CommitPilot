import os
import sys
from dataclasses import dataclass

from ai_commit import cli_args as args
from ai_commit.utils import get_model, parse_host


@dataclass
class Provider:
    name: str
    model: str | None
    base_url: str | None


providers_mapping = {
    "ollama": Provider(
        name="ollama",
        model=None,
        base_url=parse_host(os.getenv("OLLAMA_HOST")) + "/v1",
    ),
    "openai": Provider(name="openai", model="gpt-4o", base_url=None),
    "groq": Provider(
        name="groq",
        model="llama-3.2-3b-preview",
        base_url="https://api.groq.com/openai/v1",
    ),
    "gemini": Provider(
        name="gemini",
        model="gemini-2.0-flash-exp",
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
    ),
    "togetherai": Provider(
        name="togetherai",
        model="google/gemma-2-9b-it",
        base_url="https://api.together.xyz/v1",
    ),
    "deepseek": Provider(
        name="deepseek",
        model="deepseek-chat",
        base_url="https://api.deepseek.com",
    ),
    "qwen": Provider(
        name="qwen",
        model="qwen2.5-7b-instruct",
        base_url="https://dashscope-intl.aliyuncs.com/compatible-mode/v1",
    ),
    "mistral": Provider(
        name="mistral", model="ministral-3b-2410", base_url="https://api.mistral.ai/v1"
    ),
    "custom": Provider(
        name=os.environ.get("AI_COMMIT_PROVIDER"),
        model=os.environ.get("AI_COMMIT_MODEL"),
        base_url=os.environ.get("AI_COMMIT_PROVIDER_BASE_URL"),
    ),
}


provider_names = list(providers_mapping.keys())


def get_ai_provider() -> Provider | None:
    if not args.remote:
        provider = providers_mapping["ollama"]
        if provider.model is None:
            provider.model = get_model()
        return provider

    ai_provider = os.environ.get("AI_COMMIT_PROVIDER")
    if not ai_provider:
        print(
            f"""
🔑 No Provider set to use a remote model.

Set one of these providers:
> export AI_COMMIT_PROVIDER={provider_names}
> export AI_COMMIT_PROVIDER=groq

# Optional
> export AI_COMMIT_MODEL=<model-from-provider>
> export AI_COMMIT_MODEL=qwen-2.5-32b

Get API Keys from one of the these providers and export them to use a remote model:
> export OPENAI_API_KEY=<your-api-key>
"""
        )
        sys.exit(1)

    provider = providers_mapping.get(ai_provider.lower())
    if provider is None:
        print(
            f"""
❌ Unknown provider: "{ai_provider}"

Set AI_COMMIT_PROVIDER to one of: {provider_names}
> export AI_COMMIT_PROVIDER=groq
"""
        )
        sys.exit(1)

    if provider.name == "custom" and not provider.base_url:
        print(
            """
❌ No base URL set for the custom provider.

Set the base URL for your OpenAI-compatible endpoint:
    export AI_COMMIT_PROVIDER_BASE_URL=http://localhost:11434/v1
"""
        )
        sys.exit(1)

    if not provider.model:
        print(
            f"""
❌ No model name set for the provider: {provider.name}

Set model name using:
    export AI_COMMIT_MODEL=<model-from-provider>
OR 
    aic -m <model-from-provider>
                    """
        )
        sys.exit(1)

    return provider
