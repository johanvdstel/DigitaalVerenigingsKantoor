"""Dutch presentation of already calculated candidate priority; no policy decisions."""


def priority_explanation(proposal) -> str:
    parts = [f"Openstaande uren: {proposal.E}."]
    for rule in proposal.applied_priority_rules:
        if rule.startswith("achterstand vorig seizoen="):
            if proposal.previous_season_backlog > 0:
                parts.append(f"Achterstallige uren uit vorig seizoen: {proposal.previous_season_backlog}. Deze tellen mee in de prioriteit.")
            else:
                parts.append("Geen historische achterstand: 0 uur.")
        elif rule == "achterstand vorig seizoen buiten juli tot en met december":
            parts.append("Historische achterstand telt voor deze dienst niet mee: dit geldt uitsluitend van juli tot en met december.")
        elif rule == "historische achterstand onbekend":
            parts.append("Historische achterstand is onbekend of onbetrouwbaar en telt niet mee; dit is geen vastgestelde nulachterstand.")
        elif rule == "geen positieve historische achterstand":
            parts.append("Geen positieve historische achterstand; er wordt geen krediet verrekend.")
        elif rule == "historische bron niet beschikbaar":
            parts.append("Achterstallige uren uit vorig seizoen zijn nog niet beschikbaar en tellen niet mee.")
        elif rule.startswith("wedstrijdvoorkeur="):
            parts.append({
                "same_day_emergency": "Noodkandidaat: al tijdelijk ingepland op dezelfde dag.",
                "neutral": "Noodgroep zonder wedstrijd; binnen de groep bepalen de uren de volgorde.",
                "youth_home": "Eerste voorkeursgroep: jeugdteam met een overlappende thuiswedstrijd, dienststart vóór 12:30.",
                "preferred": "Wedstrijdcontext geeft deze kandidaat voorrang vóór de noodgroepen; binnen de groep bepalen de uren de volgorde.",
                "avoid": "Wedstrijdcontext geeft deze kandidaat een plaats in de noodgroep uitwedstrijd zonder wedstrijdconflict.",
            }[rule.split("=", 1)[1]])
        elif rule == "jeugd thuis zonder overlap: noodgroep zonder wedstrijd":
            parts.append("Jeugdteam met een niet-overlappende thuiswedstrijd: ingedeeld in de prioriteringscategorie zonder wedstrijd; het team speelt wel thuis.")
        elif rule == "andere teamspeeldag: laatste noodgroep":
            parts.append("Andere teamspeeldag: laatste noodgroep, uitsluitend bij tekort aan minimumbezetting.")
    return " ".join(parts)
