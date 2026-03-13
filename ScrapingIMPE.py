import requests
import csv
import time

BASE_API = "https://api.pnipe.mcti.gov.br"

headers = {
    "accept": "application/json, text/plain, */*",
    "accept-language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
    "content-type": "application/json;charset=UTF-8",
    "origin": "https://pnipe.mcti.gov.br",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-site",
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36"
}

session = requests.Session()
session.headers.update(headers)

# gerar cookies
session.get("https://pnipe.mcti.gov.br")

labs = []

search_url = f"{BASE_API}/assets/lab"

params = {
    "page": 0,
    "size": 12,
    "term": "computação"
}

# primeira requisição para descobrir total de páginas
response = session.post(search_url, params=params, json={})
data = response.json()

total_pages = data["totalPages"]

print("Total de páginas:", total_pages)

for page in range(total_pages):

    params["page"] = page

    response = session.post(search_url, params=params, json={})
    data = response.json()

    for lab in data["content"]:

        lab_id = lab["idAsset"]

        detail_url = f"{BASE_API}/assets/laboratory/{lab_id}"

        r = session.get(detail_url)

        if r.status_code != 200:
            continue

        d = r.json()
        address = d.get("address", {})
        contact = d.get("contact", {})
        registro = {
            "id": lab_id,
            "titulo": d.get("name", ""),
            "instituicao": d.get("institutionInitials", ""),
            "principais_técnicas": ", ".join([t["name"] for t in d.get("techniqueList", [])]),
            "areas_atuacao": ", ".join([t["name"] for t in d.get("areaExpertiseList", [])]),
            "Nome contato": contact.get("name", ""),
            "email": d.get("emaillab", ""),
            "Telefone contato": contact.get("phone", ""),
            "cidade": address.get("district", ""),
            "estado": address.get("city", ""),
            "url PNIPE": f"https://pnipe.mcti.gov.br/laboratory/{lab_id}"
        }

        labs.append(registro)

        print("Coletado:", registro["titulo"])

        time.sleep(0.2)


# salvar CSV
with open("laboratorios_computacao_pnipe.csv", "w", newline="", encoding="utf-8") as f:

    writer = csv.DictWriter(
        f,
        fieldnames=[
            "id",
            "titulo",
            "instituicao",
            "principais_técnicas",
            "areas_atuacao",
            "Nome contato",
            "email",
            "Telefone contato",
            "cidade",
            "estado",
            "url PNIPE"
        ]
    )

    writer.writeheader()
    writer.writerows(labs)

print("Arquivo gerado: laboratorios_computacao_pnipe.csv")