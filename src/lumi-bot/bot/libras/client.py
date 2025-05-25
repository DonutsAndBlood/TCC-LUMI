import requests

BASE_URL = "https://vlibras.gov.br/api"

def traduzir_para_glosa(texto):
    response = requests.get(f"{BASE_URL}/translate", params={"text": texto})
    response.raise_for_status()
    return response.text  # glosa retornada como string

def requisitar_video(glosa):
    response = requests.post(f"{BASE_URL}/video", data={"gloss": glosa})
    response.raise_for_status()
    return response.text  # retorna o ID da requisição

def checar_status(id_video):
    response = requests.get(f"{BASE_URL}/video/status/{id_video}")
    response.raise_for_status()
    return response.json()

def baixar_video(id_video, output_path):
    response = requests.get(f"{BASE_URL}/video/{id_video}")
    response.raise_for_status()
    with open(output_path, "wb") as f:
        f.write(response.content)
    return output_path
