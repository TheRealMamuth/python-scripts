import youtube_dl
import sys
import re

def get_video_info(url):
    ydl_opts = {
        'quiet': True,
        'skip_download': True,
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=False)
    return info_dict

def save_tags_to_file(tags, title):
    # Usunięcie niedozwolonych znaków z tytułu
    safe_title = re.sub(r'[\\/*?:"<>|]', '', title)
    filename = f"{safe_title}.tags"
    with open(filename, 'w', encoding='utf-8') as file:
        for tag in tags:
            file.write(tag + "\n")
    return filename

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Użycie: script.py [URL_YOUTUBE]")
        sys.exit(1)

    video_url = sys.argv[1]
    info_dict = get_video_info(video_url)
    tags = info_dict.get('tags', [])
    title = info_dict.get('title', 'video')

    print("Tagi wideo:", tags)
    filename = save_tags_to_file(tags, title)
    print(f"Tagi zostały zapisane do pliku {filename}.")
