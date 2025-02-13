import json
import asyncio
import openai
from typing import List
from pymilvus import connections, Collection
from .config import MILVUS_HOST, MILVUS_PORT, logger
from .utils import get_openai_embedding

def extract_query_criteria(query: str) -> str:
    prompt = (
        "W bazie wektorowej jest przykładowy obiekt: "
        "Category: Śniadanie. Title: Naleśniki z mąki kukurydzianej. Ingredients: mąki kukurydzianej, mleka, wody mineralnej, gazowanej, jajka, proszku do pieczenia, soli, olej. Nutrition: kJ 586 kJ, kcal 140.1 kcal, g 5.3 protein, g 22.2 carb2, g 3.7 fat, g 0.9 saturatedFat, g 2.4 dietaryFibre, mg 79.6 sodium. Total times: ['activeTime TimeQuantity(value=1500)', 'totalTime TimeQuantity(value=1800)']."
        "Na podstawie poniższego zapytania wypunktuj najważniejsze kryteria, "
        "które będą użyte do wyszukania przepisu w bazie wektorowej przy pomocy embedding. "
        "Podaj je jako krótką listę oddzieloną przecinkami. "
        "Podaj tylko kluczowe kryteria, czyli kategorie, tytuł, składniki, kaloryczność i czas przygotowania. "
        "(możesz pominąć coś, jeżeli nie jest ważne). "
        "Przykład: 'śniadanie, <500 kcal, bez jajka, <30 min'\n\n"
        f"Zapytanie: {query}"
    )
    messages = [
        {"role": "system", "content": "Jesteś asystentem do ekstrakcji kluczowych kryteriów z zapytań do bazy wektorowej."},
        {"role": "user", "content": prompt}
    ]
    try:
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.3,
            max_completion_tokens=2048
        )
        criteria = response.choices[0].message.content.strip()
        logger.info(f"Extracted criteria: {criteria}")
        return criteria
    except Exception as exc:
        logger.error(f"Error extracting criteria: {exc}")
        return query

async def query_recipe_with_chatgpt(query: str, top_k: int = 20) -> str:
    extracted_criteria = extract_query_criteria(query)
    condensed_query = f"{query}. Kryteria: {extracted_criteria}."
    
    query_embedding = get_openai_embedding(condensed_query)
    if not query_embedding:
        return "Nie udało się obliczyć embeddingu zapytania."
    
    connections.connect("default", host=MILVUS_HOST, port=MILVUS_PORT)
    collection = Collection("recipes_collection")
    collection.load()
    
    search_params = {"metric_type": "L2", "params": {"nprobe": 10}}
    results = collection.search(
        data=[query_embedding],
        anns_field="embedding",
        param=search_params,
        limit=top_k,
        expr=None,
        output_fields=["recipe_id", "title", "condensed_text"]
    )
    
    retrieved_recipes: List[str] = []
    for hits in results:
        for hit in hits:
            text = hit.entity.get("condensed_text")
            if text:
                retrieved_recipes.append(text)
    
    if not retrieved_recipes:
        return "Nie znaleziono przepisów pasujących do zapytania."
    
    context = "\n\n".join(retrieved_recipes)
    
    # Save the retrieved recipes for further inspection.
    # recipes_data = [recipe for recipe in retrieved_recipes if recipe is not None]
    # with open('data.json', 'w', encoding='utf-8') as f:
    #     json.dump(recipes_data, f, ensure_ascii=False, indent=4)
    
    final_prompt = (
        "Na podstawie poniższych przepisów z Cookidoo, wybierz i ułóż najbardziej odpowiednią odpowiedź, "
        "która spełnia poniższe kryteria.\n\n"
        "Oryginalne zapytanie:\n"
        f"{query}\n\n"
        "Wyekstrahowane kryteria:\n"
        f"{extracted_criteria}\n\n"
        "Przepisy:\n"
        f"{context}\n\n"
        "Odpowiedz, podając nazwę przepisu, składniki, kroki przygotowania oraz informacje o kaloryczności i czasie przygotowania. "
        "Nie łącz przepisów, każdy przepis powinien być przedstawiony osobno. "
        "Nie wymyślaj przepisów, jeżeli nie ma przepisu spełniającego kryteria, to napisz, że nie znaleziono przepisu."
    )
    
    messages = [
        {"role": "assistant", "content": "Jesteś pomocnym asystentem, który na podstawie podanych danych wybiera i przedstawia przepisy."},
        {"role": "user", "content": final_prompt}
    ]
    
    try:
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.7,
            max_completion_tokens=2048
        )
        answer = response.choices[0].message.content.strip()
        return answer
    except Exception as exc:
        logger.error(f"Error generating answer: {exc}")
        return "Błąd podczas generowania odpowiedzi."

async def main(query: str):
    query = "Wyszukaj mi trzy przepisy na obiad, które zawierają kurczaka i całkowity czas przygotowania jest krótszy niz godzina"
    answer = await query_recipe_with_chatgpt(query, top_k=10)
    print("Odpowiedź:")
    print(answer)

if __name__ == "__main__":
    asyncio.run(main())
