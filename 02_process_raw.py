import json
import time
import tls_client
from bs4 import BeautifulSoup

RAW_FILE = "raw_infomoney.json"
OUTPUT_FILE = "noticias_processadas.json"

client = tls_client.Session(
    client_identifier="chrome_120",
    random_tls_extension_order=True
)

headers = {
    "User-Agent": "Mozilla/5.0",
}

# Palavras-chave por empresa (busca no corpo do texto)
CHAVES_EMPRESAS = {
    "TOTVS": ["totvs", "tots3"],
    "Locaweb": ["locaweb", "lwsa3"],
    "Sinqia": ["sinqia", "sqia3"],
    "Positivo Tecnologia": ["positivo", "positivo tecnologia", "posi3"]
}


def extrair_data(soup):
    """Extrai a data real de publicação do <time datetime="">"""
    time_tag = soup.select_one("div[data-ds-component='author-small'] time")
    if time_tag and time_tag.get("datetime"):
        return time_tag["datetime"]  # formato ISO
    return None


def extrair_texto(soup):
    """Coleta todo conteúdo em <p> do corpo da notícia"""
    article = soup.find("article")
    if not article:
        return ""

    paragraphs = article.find_all("p")
    texto = "\n".join(p.get_text(strip=True) for p in paragraphs)
    return texto


def noticia_relevante(conteudo, empresa):
    """Retorna True se o texto mencionar o nome ou ticker da empresa."""
    conteudo = conteudo.lower()

    for termo in CHAVES_EMPRESAS.get(empresa, []):
        if termo.lower() in conteudo:
            return True

    return False


def processar_noticias():
    print("\n📂 Carregando RAW:", RAW_FILE)

    with open(RAW_FILE, "r", encoding="utf-8") as f:
        raw_data = json.load(f)

    noticias_final = []

    for empresa, noticias in raw_data.items():
        print(f"\n🔍 Processando {empresa} ({len(noticias)} notícias)...")

        for item in noticias:
            url = item.get("post_permalink")
            titulo = item.get("post_title")

            if not url:
                continue

            print(f"  🌐 Acessando: {titulo[:50]}...")

            try:
                resp = client.get(url, headers=headers)
                soup = BeautifulSoup(resp.text, "html.parser")

                data_publicacao = extrair_data(soup)
                conteudo = extrair_texto(soup)

                # 🔎 aplicar filtro por conteúdo
                if noticia_relevante(conteudo, empresa):
                    print("    ✔ Relevante — salva.")
                    noticias_final.append({
                        "empresa": empresa,
                        "titulo": titulo,
                        "url": url,
                        "data_publicacao": data_publicacao,
                        "conteudo": conteudo
                    })
                else:
                    print("    ❌ Ignorada — não menciona a empresa.")

            except Exception as e:
                print(f"  ⚠ Erro ao acessar {url}: {e}")

            time.sleep(1)

    print("\n💾 Salvando resultado em:", OUTPUT_FILE)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(noticias_final, f, indent=2, ensure_ascii=False)

    print("\n🎉 PROCESSO CONCLUÍDO!")
    print(f"Total de notícias relevantes: {len(noticias_final)}")


if __name__ == "__main__":
    processar_noticias()
