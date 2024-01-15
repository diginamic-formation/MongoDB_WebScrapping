from urllib.parse import urlparse

def extraire_url_de_base(url):
    parsed_url = urlparse(url)
    base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
    return base_url

# Exemple d'utilisation
url_complet = "https://www.example.com/path/page.html?param=valeur"
url_de_base = extraire_url_de_base(url_complet)

print("URL de base:", url_de_base)
