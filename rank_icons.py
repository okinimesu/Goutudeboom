# rank_icons.py

def get_rank_icon(tier, rank):
    """
    Devuelve la ruta correcta del icono basado en:
    - tier  (IRON, BRONZE, SILVER...)
    - rank  (I, II, III, IV)

    Las imágenes deben estar en /static/ranks/
    """

    tier = tier.upper()

    # Si no tiene rango
    if tier == "UNRANKED" or tier == "ERROR":
        return "/static/ranks/unranked.png"

    # Tier que tienen divisiones: I, II, III, IV
    divisions = {
        "I": "1",
        "II": "2",
        "III": "3",
        "IV": "4"
    }

    # Tier de una sola división
    no_division_tiers = ["MASTER", "GRANDMASTER", "CHALLENGER"]

    if tier in no_division_tiers:
        return f"/static/ranks/{tier.lower()}.png"

    # Tiers normales con divisiones
    div = divisions.get(rank, "1")
    return f"/static/ranks/{tier.lower()}_{div}.png"

