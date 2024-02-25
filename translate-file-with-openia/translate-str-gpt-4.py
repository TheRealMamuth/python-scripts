from openai import OpenAI
import sys

def translate_file(api_key, source_file_path, output_file_path, model="gpt-4", source_language="auto", target_language="English"):
    client = OpenAI(api_key=api_key)
    # Load the content of the source file
    with open(source_file_path, 'r', encoding='utf-8') as file:
        file_content = file.read()

    # Prepare the structured input for translation
    messages = [
        {"role": "system", "content": f"Translate the following text from {source_language} to {target_language}."},
        {"role": "user", "content": file_content}
    ]

    # Send the request to OpenAI
    response = client.chat.completions.create(model=model, messages=messages)

    # Extract the translated text
    translated_text = response.choices[0].message.content.strip()


    # Save the translated text to the output file
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
