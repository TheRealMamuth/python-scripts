from openai import OpenAI
import sys

def translate_file(api_key, source_file_path, output_file_path, model="gpt-3.5-turbo", source_language="auto", target_language="English"):
    client = OpenAI(api_key=api_key)

    # Wczytaj zawartość pliku źródłowego
    with open(source_file_path, 'r', encoding='utf-8') as file:
        file_content = file.read()

    # Przygotuj prompt do tłumaczenia
    translation_prompt = f"Translate the following text from {source_language} to {target_language}:\n\n{file_content}"

    # Wyślij zapytanie do OpenAI używając endpointu dla chatu
    response = client.ChatCompletion.create(
        model=model,
        messages=[{"role": "system", "content": "Translate the following text:"},
                  {"role": "user", "content": file_content}],
        temperature=0.5
    )

    # Przetłumaczony tekst
    translated_text = response.choices[0].message['content'].strip()

    # Zapisz przetłumaczony tekst do pliku wynikowego
    with open(output_file_path, 'w', encoding='utf-8') as output_file:
        output_file.write(translated_text)

    print(f"Translated text saved to {output_file_path}")

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python script.py <API_KEY> <SOURCE_FILE_PATH> <OUTPUT_FILE_PATH>")
        sys.exit(1)

    api_key = sys.argv[1]
    source_file_path = sys.argv[2]
    output_file_path = sys.argv[3]

    translate_file(api_key, source_file_path, output_file_path)
