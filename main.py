from flask import Flask, render_template, jsonify
import requests
import urllib.parse

app = Flask(__name__)
# --- CONFIGURACIÓN ---
# RECUERDA: ¡Esta clave cambiará mañana! Si falla con error 403, pon la nueva aquí.
import os
# ...
# Busca la clave en las variables de entorno, si no está, usa una vacía o lanza error
RIOT_API_KEY = ("RGAPI-017490d3-dcd2-4285-b00f-b5ae93bfde65")

REGION_ACCOUNT = "americas"
REGION_LEAGUE = "la2"

PLAYERS = [{
    'name': 'Wower',
    'tag': '111'
}, {
    'name': 'cielopayaso',
    'tag': 'gtdbm'
}, {
    'name': 'Hide on bush',
    'tag': '422'
}, {
    'name': 'Gumayoshii',
    'tag': 'ranca'
}, {
    'name': 'Oguri Flan',
    'tag': 'emiya'
}]


def get_account_info(game_name, tag_line):
    # Obtenemos PUUID y el ID del Icono
    url = f"https://{REGION_ACCOUNT}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{urllib.parse.quote(game_name)}/{tag_line}?api_key={RIOT_API_KEY}"
    try:
        resp = requests.get(url)
        if resp.status_code == 200:
            data = resp.json()
            # Devolvemos PUUID, Nombre real y el ID del icono
            return data.get('puuid'), data.get('gameName'), data.get(
                'profileIconId')
        else:
            print(f"❌ Error buscando cuenta {game_name}: {resp.status_code}")
    except Exception as e:
        print(f"❌ Excepción buscando cuenta {game_name}: {e}")
    return None, game_name, None


def get_rank_data(puuid, player_name):
    # Usamos el endpoint directo via PUUID (el que sí funciona)
    league_url = f"https://{REGION_LEAGUE}.api.riotgames.com/lol/league/v4/entries/by-puuid/{puuid}?api_key={RIOT_API_KEY}"

    try:
        print(f"🔍 Consultando rango para {player_name}...")
        resp_league = requests.get(league_url)

        if resp_league.status_code == 200:
            data = resp_league.json()
            found_solo = False
            for entry in data:
                if entry['queueType'] == 'RANKED_SOLO_5x5':
                    print(f"   ✅ ¡ENCONTRADO! {entry['tier']} {entry['rank']}")
                    return {
                        'tier': entry['tier'],
                        'rank': entry['rank'],
                        'lp': entry['leaguePoints'],
                        'wins': entry['wins'],
                        'losses': entry['losses']
                    }
            if not found_solo:
                print(f"   ⚠️ {player_name} es Unranked en SoloQ.")
        else:
            print(f"   ❌ Error en API de Liga: {resp_league.status_code}")

    except Exception as e:
        print(f"Error conexión liga: {e}")

    return {'tier': 'UNRANKED', 'rank': '', 'lp': 0, 'wins': 0, 'losses': 0}


def calculate_score(player_data):
    tiers = {
        "CHALLENGER": 9000,
        "GRANDMASTER": 8000,
        "MASTER": 7000,
        "DIAMOND": 6000,
        "EMERALD": 5000,
        "PLATINUM": 4000,
        "GOLD": 3000,
        "SILVER": 2000,
        "BRONZE": 1000,
        "IRON": 0,
        "UNRANKED": -1
    }
    base = tiers.get(player_data['tier'], -1)
    if base == -1: return -1
    div_score = 0
    if player_data['rank'] == "I": div_score = 300
    elif player_data['rank'] == "II": div_score = 200
    elif player_data['rank'] == "III": div_score = 100
    return base + div_score + player_data['lp']


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/data')
def data():
    leaderboard = []
    print("\n--- ACTUALIZANDO TABLA CON ICONOS ---")

    for p in PLAYERS:
        # Ahora recibimos 3 cosas
        puuid, official_name, icon_id = get_account_info(p['name'], p['tag'])

        if puuid:
            stats = get_rank_data(puuid, official_name)
            total = stats['wins'] + stats['losses']
            winrate = round(
                (stats['wins'] / total * 100), 1) if total > 0 else 0
            tier_image = f"{stats['tier']}.png"

            leaderboard.append({
                'name': official_name,
                'tag': p['tag'],
                'icon_id': icon_id,  # Guardamos el ID del icono
                'tier': stats['tier'],
                'tier_image': tier_image,
                'rank': stats['rank'],
                'lp': stats['lp'],
                'wins': stats['wins'],
                'losses': stats['losses'],
                'winrate': winrate,
                'sort_score': calculate_score(stats)
            })
        else:
            leaderboard.append({
                'name': p['name'],
                'tag': p['tag'],
                'icon_id': None,
                'tier': 'ERROR',
                'rank': '',
                'lp': 0,
                'wins': 0,
                'losses': 0,
                'winrate': 0,
                'sort_score': -1
            })

    leaderboard.sort(key=lambda x: x['sort_score'], reverse=True)
    for i, player in enumerate(leaderboard):
        player['pos'] = i + 1

    return jsonify(leaderboard)


if __name__ == '__main__':
    # host='0.0.0.0' permite que ngrok vea tu servidor local
    app.run(debug=True, host='0.0.0.0')
