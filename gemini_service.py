from google import genai
import os
import asyncio


# Get Gemini API key
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise RuntimeError(
        "GEMINI_API_KEY is not set. "
        "Set it in PowerShell before starting Uvicorn."
    )


# Create Gemini client
client = genai.Client(api_key=api_key)


# Gemini models to try
MODELS = [
    "gemini-3.7-flash",
    "gemini-3.6-flash",
    "gemini-3.5-flash",
    "gemini-3.5-flash-lite",
    "gemini-3.8-flash",
]


async def generate_response(prompt: str) -> str:

    errors = []

    for model in MODELS:

        try:
            print(f"Trying Gemini model: {model}")

            response = client.models.generate_content(
                model=model,
                contents=prompt
            )

            print(f"Success with model: {model}")

            return response.text

        except Exception as e:

            error_message = str(e)
            errors.append(f"{model}: {error_message}")

            # 429 = quota/rate limit
            if "429" in error_message or "RESOURCE_EXHAUSTED" in error_message:

                print(
                    f"{model} quota/rate limit reached. "
                    "Trying next model..."
                )

                continue

            # 503 = temporary Gemini server overload
            if "503" in error_message or "UNAVAILABLE" in error_message:

                print(
                    f"{model} is temporarily unavailable. "
                    "Trying next model..."
                )

                await asyncio.sleep(1)
                continue

            # Other errors
            print(f"Error with {model}: {error_message}")

            return "Gemini API error:\n\n" + error_message

    return (
        "EduGenie could not get a response from Gemini right now.\n\n"
        "The available Gemini models are currently "
        "unavailable or have reached their quota.\n\n"
        "Please try again later."
    )