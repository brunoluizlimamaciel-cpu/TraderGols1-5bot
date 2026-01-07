import requests
import time
import os

API_KEY = os.getenv("API_KEY")
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

HEADERS = {
    "X-RapidAPI-Key": API_KEY,
    "X-RapidAPI-Host": "api-football-v1.p.rapidapi.com"
}

def enviar_alerta(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": msg
    }
    requests.post(url, json=payload)

def jogos_ao_vivo():
    url = "https://api-football-v1.p.rapidapi.com/v3/fixtures?live=all"
    r = requests.get(url, headers=HEADERS)
    return r.json()["response"]

def estatisticas(fixture_id):
    url = f"https://api-football-v1.p.rapidapi.com/v3/fixtures/statistics?fixture={fixture_id}"
    r = requests.get(url, headers=HEADERS)
    return r.json()["response"]

def analisar_pressao(stats):
    sinais = 0
    for time in stats:
        dados = {i["type"]: i["value"] for i in time["statistics"]}
        if dados.get("Shots Total", 0) >= 3:
            sinais += 1
        if dados.get("Shots on Goal", 0) >= 2:
            sinais += 1
        if dados.get("Corner Kicks", 0) >= 3:
            sinais += 1
        posse = dados.get("Ball Possession", "0%").replace("%","")
        if posse.isdigit() and int(posse) >= 60:
            sinais += 1
    return sinais

jogos_alertados = set()

while True:
    try:
        jogos = jogos_ao_vivo()
        for jogo in jogos:
            fixture_id = jogo["fixture"]["id"]
            minuto = jogo["fixture"]["status"]["elapsed"]
            gols = jogo["goals"]["home"] + jogo["goals"]["away"]

            if fixture_id in jogos_alertados:
                continue
            if minuto < 15 or minuto > 35 or gols > 1:
                continue

            stats = estatisticas(fixture_id)
            sinais = analisar_pressao(stats)

            if sinais >= 4:
                home = jogo["teams"]["home"]["name"]
                away = jogo["teams"]["away"]["name"]
                placar = f"{jogo['goals']['home']}x{jogo['goals']['away']}"

                msg = f"""
🚨 ALERTA OVER 1.5

🏟️ {home} x {away}
⏱️ {minuto}' | {placar}
📊 Pressão forte detectada

Avaliar entrada LIVE
"""
                enviar_alerta(msg)
                jogos_alertados.add(fixture_id)

        time.sleep(90)

    except Exception as e:
        print("Erro:", e)
        time.sleep(60)
