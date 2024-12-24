#!/usr/bin/env python3

import argparse
import yt_dlp
import re
import os
import shutil
import pickle

from openai import OpenAI
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

def download_hook(d):
    if d['status'] == 'downloading':
        print(f"Pobieranie... {d['_percent_str']} zakończono, "
              f"prędkość: {d['_speed_str']}, pozostały czas: {d['_eta_str']}", flush=True)
    elif d['status'] == 'finished':
        print(f"\nPobieranie zakończone: {d['filename']}", flush=True)

# Nazwy języków w języku polskim, aby były spójne w YouTube
LANG_MAP = {
    'pl': 'Polski',
    'en': 'Angielski',
    'de': 'Niemiecki',
    'zh': 'Chiunski',
    'ja': 'Japonski',
    'es': 'Hiszpański',
    'pt': 'Portugalski',
    'hi': 'Hindi',
    'fr': 'Francuski',
    'ru': 'Rosyjski'
}

def translate_srt(file_path, target_langs, client):
    """Tłumaczenie pliku SRT na wybrane języki."""
    for target_lang in target_langs:
        if target_lang not in LANG_MAP:
            print(f"Nieobsługiwany język: {target_lang}")
            continue

        with open(file_path, "r", encoding="utf-8") as f:
            srt_content = f.read()

        print(f"Tłumaczenie pliku {file_path} na język {LANG_MAP[target_lang]}...")

        prompt = (
            f"Przetłumacz poniższy plik SRT na język {LANG_MAP[target_lang]}. "
            f"Proszę odpowiedzieć bez dodawania wstępu, komentarza ani dodatkowych oznaczeń. "
            f"Odpowiedź powinna zawierać wyłącznie tłumaczenie w tym samym formacie, co oryginał. "
            f"Nie dodawaj żadnych znaczników kodu, takich jak ``` lub innych formatów. "
            f"Odpowiedź powinna zawierać wyłącznie tłumaczenie w formacie SRT.\n\n"
            f"Oto treść:\n\n{srt_content}"
        )

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}]
        )
        translated_text = response.choices[0].message.content

        translated_file_path = f"{os.path.splitext(file_path)[0]}.{target_lang}.srt"
        with open(translated_file_path, "w", encoding="utf-8") as f:
            f.write(translated_text)

        print(f"Przetłumaczony plik zapisany jako: {translated_file_path}")

def translate_text_ignoring_urls(text, target_lang, client):
    """Tłumaczenie zwykłego tekstu z pominięciem adresów URL."""
    if target_lang not in LANG_MAP:
        print(f"Nieobsługiwany język: {target_lang}")
        return text

    prompt = (
        f"Przetłumacz poniższy tekst na język {LANG_MAP[target_lang]}, "
        "ale nie tłumacz żadnych adresów URL (zostaw je niezmienione). Tekst:\n\n"
        f"{text}"
    )
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

def get_existing_captions(youtube, video_id):
    response = youtube.captions().list(part="snippet", videoId=video_id).execute()
    return response.get("items", [])

def delete_caption(youtube, caption_id):
    youtube.captions().delete(id=caption_id).execute()
    print(f"Napisy o ID {caption_id} zostały usunięte.")

def upload_caption(youtube, video_id, language, caption_file):
    """
    Przesyłanie lub nadpisanie napisów w danym języku.
    UWAGA: Najważniejsza zmiana polega na tym, że 'language' i 'name' są spójne,
    aby uniknąć zdublowanych oznaczeń języka typu „Angielski–English”.
    """
    lang_name = LANG_MAP.get(language, language)

    print(f"Przesyłanie napisów z pliku {caption_file} dla filmu {video_id} w języku {lang_name}...")

    existing_captions = get_existing_captions(youtube, video_id)

    # Sprawdź, czy istnieją napisy w danym języku i ewentualnie je usuń
    for caption in existing_captions:
        if caption["snippet"]["language"] == language:
            print(f"Napisy w języku {language} ({lang_name}) już istnieją. Usuwanie...")
            delete_caption(youtube, caption["id"])

    # Ustawiamy w request_body spójne wartości dla 'language' i 'name'
    request_body = {
        "snippet": {
            "videoId": video_id,
            "language": language,  # np. 'en', 'pl'
            "name": lang_name,     # np. 'Angielski', 'Polski' itp.
            "isDraft": False,
        }
    }

    media = MediaFileUpload(caption_file, mimetype="application/octet-stream")
    youtube.captions().insert(
        part="snippet",
        body=request_body,
        media_body=media
    ).execute()

    print(f"Napisy z pliku {caption_file} w języku {lang_name} ({language}) zostały przesłane pomyślnie.")

def update_video_localizations(youtube, video_id, language, translated_title, translated_description):
    """
    Dodaje (lub modyfikuje) lokalizacje (title, description) w wybranym języku.
    """
    video_response = youtube.videos().list(
        part="snippet,localizations",
        id=video_id
    ).execute()

    if "items" not in video_response or not video_response["items"]:
        print("Nie znaleziono filmu o podanym ID.")
        return

    video = video_response["items"][0]

    if "snippet" not in video:
        video["snippet"] = {}

    # Jeśli defaultLanguage nie jest ustawiony, ustawiamy go np. na 'pl'
    if "defaultLanguage" not in video["snippet"]:
        video["snippet"]["defaultLanguage"] = "pl"

    if "localizations" not in video:
        video["localizations"] = {}

    # Dodajemy/modyfikujemy lokalizację dla podanego języka
    video["localizations"][language] = {
        "title": translated_title,
        "description": translated_description
    }

    youtube.videos().update(
        part="snippet,localizations",
        body=video
    ).execute()

    print(f"Zaktualizowano tytuł i opis w języku {language} ({LANG_MAP.get(language, language)}).")

def get_authenticated_service(client_secrets_file):
    scopes = ["https://www.googleapis.com/auth/youtube.force-ssl"]
    credentials = None

    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token:
            credentials = pickle.load(token)

    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(client_secrets_file, scopes)
            credentials = flow.run_local_server(port=0)

        with open("token.pickle", "wb") as token:
            pickle.dump(credentials, token)

    return build("youtube", "v3", credentials=credentials)

def main():
    parser = argparse.ArgumentParser(
        description='Pobieranie audio z YouTube, transkrypcja, tłumaczenia napisów/tytułu/opisu i publikacja w YouTube.'
    )
    parser.add_argument('--url', required=True, help='URL do filmu na YouTube')
    parser.add_argument('--api', required=True, help='OpenAI API key')
    parser.add_argument('--lang', required=True, help='Lista kodów języków do tłumaczenia (np. en,de,zh)')
    parser.add_argument('--client_secrets', required=False, help='Ścieżka do pliku client_secrets.json')
    # Dodana opcja --upload
    parser.add_argument('--upload', action='store_true',
                        help='Jeśli podane, to przesyłaj napisy i lokalizacje do YouTube.')
    args = parser.parse_args()

    client = OpenAI(api_key=args.api)
    target_langs = args.lang.split(',')

    print("Pobieranie informacji o filmie (tytuł, opis) za pomocą yt_dlp...", flush=True)
    with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
        info = ydl.extract_info(args.url, download=False)
        raw_title = info.get('title', 'unknown_title')
        raw_description = info.get('description', '')

    # Uporządkowana nazwa (bez znaków specjalnych)
    safe_title = re.sub(r'[^\w\s-]', '', raw_title).replace(' ', '_')

    # Zapis oryginalnego tytułu i opisu (polski)
    title_file_pl = f"{safe_title}.title.pl"
    desc_file_pl = f"{safe_title}.description.pl"

    with open(title_file_pl, "w", encoding="utf-8") as f:
        f.write(raw_title)
    with open(desc_file_pl, "w", encoding="utf-8") as f:
        f.write(raw_description)

    # Pobranie i zapis audio
    output_template = f"{safe_title}.%(ext)s"
    ydl_opts = {
        'format': '140',
        'outtmpl': output_template,
        'noplaylist': True,
        'progress_hooks': [download_hook]
    }

    print("Rozpoczynanie pobierania pliku audio z YouTube...", flush=True)
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        new_info = ydl.extract_info(args.url, download=True)
        audio_file_name = ydl.prepare_filename(new_info)

    print("\nPobieranie zakończone. Przechodzenie do transkrypcji...\n", flush=True)
    srt_file_name = f"{safe_title}.srt.pl"
    with open(audio_file_name, "rb") as audio_file:
        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
            response_format="srt"
        )
    with open(srt_file_name, "w", encoding="utf-8") as f:
        f.write(transcript)

    print(f"Transkrypcja zapisana w pliku: {srt_file_name}")

    # Przeniesienie pliku audio do osobnego katalogu
    audio_dir = "audio"
    if not os.path.exists(audio_dir):
        os.makedirs(audio_dir)
    destination_path = os.path.join(audio_dir, os.path.basename(audio_file_name))
    shutil.move(audio_file_name, destination_path)
    print(f"Plik audio został przeniesiony do katalogu: {destination_path}")

    # Tłumaczenie pliku SRT
    translate_srt(srt_file_name, target_langs, client)

    # Tłumaczenie tytułu i opisu na wybrane języki (POMIJAMY 'pl')
    translated_titles = {}
    translated_descriptions = {}

    for lang in target_langs:
        if lang == 'pl':  # Pomijamy polski
            continue
        
        translated_title = translate_text_ignoring_urls(raw_title, lang, client)
        translated_description = translate_text_ignoring_urls(raw_description, lang, client)

        # Zapis do plików
        title_file_lang = f"{safe_title}.title.{lang}"
        desc_file_lang = f"{safe_title}.description.{lang}"

        with open(title_file_lang, "w", encoding="utf-8") as f:
            f.write(translated_title)
        with open(desc_file_lang, "w", encoding="utf-8") as f:
            f.write(translated_description)

        translated_titles[lang] = translated_title
        translated_descriptions[lang] = translated_description

    # Jeśli nie ma parametru --upload, kończymy tylko na zapisie plików
    if not args.upload:
        print("Zakończono przetwarzanie (tryb bez przesyłania do YouTube).")
        return

    # Poniżej sekcja wysyłania napisów i aktualizacji tytułów/opisów w YouTube
    if "v=" in args.url:
        video_id = args.url.split("v=")[-1]
    else:
        video_id = args.url.split("/")[-1]

    youtube = get_authenticated_service(args.client_secrets)

    # Najpierw publikujemy (lub nadpisujemy) napisy w języku polskim (oryginalne SRT).
    upload_caption(youtube, video_id, "pl", srt_file_name)

    # Następnie napisy w pozostałych językach (i ewentualnie ich lokalizacje)
    for lang in target_langs:
        if lang != "pl":
            caption_file = f"{os.path.splitext(srt_file_name)[0]}.{lang}.srt"
            if os.path.exists(caption_file):
                upload_caption(youtube, video_id, lang, caption_file)
    
    # Dodajemy lokalizacje tytułu i opisu TYLKO dla języków innych niż polski
    for lang in target_langs:
        if lang == 'pl':
            continue  # Pomijamy polskie localizations
        if lang in translated_titles and lang in translated_descriptions:
            update_video_localizations(
                youtube,
                video_id,
                lang,
                translated_titles[lang],
                translated_descriptions[lang]
            )

    print("Zakończono przetwarzanie (tryb z przesyłaniem do YouTube).")

if __name__ == '__main__':
    main()
