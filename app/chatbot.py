from openai import OpenAI

# ✅ Define the OpenRouter client properly
client = OpenAI(
    api_key="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",
    base_url="https://openrouter.ai/api/v1"  # Required for OpenRouter
)

# ✅ VitaminBot response function
def get_vitaminbot_response(user_input):
    try:
        response = client.chat.completions.create(
            model="openai/gpt-3.5-turbo",  # ✅ Valid model ID for OpenRouter
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are VitaminBot, an assistant that answers questions about "
                        "vitamin deficiencies, symptoms, treatments, and food sources. Be clear and helpful."
                    )
                },
                {
                    "role": "user",
                    "content": user_input
                }
            ]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"❌ Error: {e}"