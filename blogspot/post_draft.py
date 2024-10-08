import argparse
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import os
import googleapiclient.discovery
import glob

# Określ uprawnienia
SCOPES = ['https://www.googleapis.com/auth/blogger']

# Funkcja do uwierzytelnienia
def authenticate():
    creds = None
    # Sprawdź, czy istnieją zapisane poświadczenia
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # Jeśli nie ma poświadczeń, przeprowadź autoryzację
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # Uruchamia proces logowania OAuth
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Zapisz poświadczenia na przyszłość
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return creds

# Funkcja do wczytania zawartości z pliku i zamiany nowych linii na <br>
def load_file_content(file_path):
    with open(file_path, 'r') as file:
        content = file.read().strip()
        # Zamiana nowych linii na <br> w HTML
        content = content.replace('\n', '<br>')
    return content

# Funkcja do zamiany ID wideo w szablonie
def replace_video_id(template, video_url):
    # Wyciągnięcie identyfikatora wideo z linku YouTube
    video_id = video_url.split('/')[-1]
    return template.replace('TU_ID', video_id)

# Funkcja do zamiany składników w szablonie
def replace_ingredients(template, ingredients):
    return template.replace('TU SKLADNIKI', ingredients)

# Funkcja do publikacji posta jako szkic
def publish_post(blog_id, title, content, is_draft=True):
    service = googleapiclient.discovery.build('blogger', 'v3', credentials=authenticate())
    post = {
        'title': title,
        'content': content,
        'status': 'DRAFT' if is_draft else 'LIVE'  # Ustaw status na DRAFT lub LIVE
    }
    response = service.posts().insert(blogId=blog_id, body=post, isDraft=is_draft).execute()
    print(f"Post '{title}' zapisany jako szkic." if is_draft else f"Post '{title}' opublikowany.")
    return response

# Funkcja do znalezienia pliku z danym rozszerzeniem
def find_file(extension):
    files = glob.glob(f"*.{extension}")
    if len(files) == 1:
        return files[0]
    else:
        raise FileNotFoundError(f"Nie znaleziono pliku {extension} lub znaleziono więcej niż jeden.")

# Główna funkcja skryptu
def main(blog_id, youtube_url):
    # Wczytanie szablonu HTML
    html_template = '''
    <p>&nbsp;</p><h2><b>🛒 Składniki:</b></h2><p>TU SKLADNIKI</p><h2>🔪 Przygotowanie:</h2><p>TU PRZYGOTOWANIE</p><h2>🔗&nbsp;Linki:</h2><div><div>Facebook:&nbsp; &nbsp;<a href="https://www.facebook.com/KulinarneePrzygody/" target="_blank">https://www.facebook.com/KulinarneePrzygody/</a></div><div>Instagram:&nbsp;&nbsp;<a href="https://www.instagram.com/kulinarneprzygody_/" target="_blank">https://www.instagram.com/kulinarneprzygody_/</a></div><div>&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp;</div><div>Blog:&nbsp; &nbsp; &nbsp; &nbsp; &nbsp;&nbsp;<a href="https://kulinarneeprzygody.blogspot.com/" target="_blank">https://kulinarneeprzygody.blogspot.com/</a></div><div><span>&nbsp;&nbsp; &nbsp;</span><span>&nbsp;&nbsp; &nbsp;</span><span>&nbsp;&nbsp; &nbsp;</span><span>&nbsp;&nbsp; &nbsp;</span><span>&nbsp; &nbsp;</span><a href="https://www.kulinarneprzygody.com/" target="_blank">https://www.kulinarneprzygody.com/</a>&nbsp; &nbsp; &nbsp; &nbsp; &nbsp;&nbsp;</div><div>Pinterest&nbsp; &nbsp; &nbsp;<a href="https://pl.pinterest.com/mnawrolska/kulinarne-przygody/" target="_blank">https://pl.pinterest.com/mnawrolska/kulinarne-przygody/</a></div></div><div><br /></div><h2>&nbsp;📺&nbsp;Obejrzyj:</h2><div class="separator" style="clear: both; text-align: center;"><iframe allowfullscreen="" class="BLOG_video_class" height="380" src="https://www.youtube.com/embed/TU_ID" width="551" youtube-src-id="TU_ID"></iframe></div><br /><p><br /></p>
    '''

    # Znalezienie plików z tytułem i składnikami
    ingredients_file = find_file('description.pl')
    title_file = find_file('title.pl')

    # Wczytanie składników i tytułu z plików
    ingredients = load_file_content(ingredients_file)
    title = load_file_content(title_file)

    # Zamiana składników i wideo w szablonie
    html_content = replace_ingredients(html_template, ingredients)
    html_content = replace_video_id(html_content, youtube_url)

    # Publikacja posta jako szkic
    publish_post(blog_id, title, html_content, is_draft=True)

if __name__ == "__main__":
    # Ustawienia argumentów
    parser = argparse.ArgumentParser(description="Automatyczna publikacja posta na Bloggerze.")
    parser.add_argument("blog_id", type=str, help="Identyfikator bloga.")
    parser.add_argument("youtube_url", type=str, help="URL filmu na YouTube.")
    
    # Parsowanie argumentów
    args = parser.parse_args()

    # Uruchomienie głównej funkcji
    main(args.blog_id, args.youtube_url)
