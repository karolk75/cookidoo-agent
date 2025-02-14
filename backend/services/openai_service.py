from fastapi import logger
import openai
from ..config import settings

# Ustawienie klucza API
openai.api_key = settings.openai_api_key

client = openai.AsyncOpenAI()


async def get_openai_embedding(text: str) -> list[float]:
    try:
        response = await client.embeddings.create(
            input=text, model=settings.openai_model_embedding
        )
        return response.data[0].embedding
    except Exception as exc:
        logger.error(f"Error generating embedding: {exc}")
        return []


async def extract_query_criteria(query: str) -> str:
    prompt = (
        "Na podstawie poniższego zapytania wypunktuj najważniejsze kryteria, "
        "które będą użyte do wyszukania przepisu w bazie wektorowej przy pomocy embedding. "
        "Podaj je jako krótką listę oddzieloną przecinkami. "
        "Przykład: 'śniadanie, <500 kcal, bez jajka, <30 min'\n\n"
        f"Zapytanie: {query}"
    )
    messages = [
        {
            "role": "system",
            "content": "Jesteś asystentem do ekstrakcji kluczowych kryteriów z zapytań do bazy wektorowej.",
        },
        {"role": "user", "content": prompt},
    ]
    try:
        response = await client.chat.completions.create(
            model=settings.openai_criteria_extraction_model,
            messages=messages,
            temperature=0.3,
            max_tokens=100,
        )
        criteria = response.choices[0].message.content.strip()
        logger.info(f"Extracted criteria: {criteria}")
        return criteria
    except Exception as e:
        logger.error(f"Error extracting criteria: {e}")
        return query


def get_re_ranked_recipe(query: str, extracted_criteria: str, context: str) -> str:
    final_prompt = (
        "Na podstawie poniższych przepisów i zapytania, wybierz te, które najlepiej spełniają kryteria. "
        "Przepis powinien zawierać nazwę, składniki, kroki przygotowania, kaloryczność i czas przygotowania. "
        "Jeśli żaden przepis nie spełnia kryteriów, napisz, że nie znaleziono przepisu.\n\n"
        f"Zapytanie: {query}\n\n"
        f"Kryteria: {extracted_criteria}\n\n"
        f"Przepisy:\n{context}\n\n"
        "Wybierz i przedstaw najlepszy przepis lub przepisy."
    )
    messages = [
        {
            "role": "system",
            "content": "Jesteś asystentem wybierającym najlepsze przepisy na podstawie podanych kryteriów.",
        },
        {"role": "user", "content": final_prompt},
    ]
    try:
        response = client.chat.completions.create(
            model=settings.openai_recipe_ranking_model,
            messages=messages,
            temperature=0.5,
            max_tokens=500,
        )
        answer = response.choices[0].message.content.strip()
        return answer
    except Exception as e:
        logger.error(f"Error generating final answer: {e}")
        return "Error generating final answer."
