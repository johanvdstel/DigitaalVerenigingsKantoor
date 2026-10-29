"""Dutch presentation of already calculated candidate priority; no policy decisions."""


def priority_explanation(proposal) -> str:
    parts = [f"Openstaande uren: {proposal.E}."]
    for rule in proposal.applied_priority_rules:
        if rule.startswith("achterstand vorig seizoen="):
            parts.append(f"Achterstallige uren uit vorig seizoen: {proposal.previous_season_backlog}. Deze tellen mee in de prioriteit.")
        elif rule == "achterstand vorig seizoen niet meegewogen vanaf 1 december":
            parts.append("Achterstallige uren uit vorig seizoen tellen vanaf 1 december niet mee.")
        elif rule == "achterstand vorig seizoen niet beschikbaar: BL-03":
            parts.append("Achterstallige uren uit vorig seizoen zijn nog niet beschikbaar en tellen niet mee.")
        elif rule.startswith("wedstrijdvoorkeur="):
            parts.append({
                "neutral": "Wedstrijdcontext geeft geen voorkeur.",
                "preferred": "Wedstrijdcontext geeft deze kandidaat voorrang bij gelijke urenprioriteit.",
                "avoid": "Wedstrijdcontext geeft deze kandidaat minder voorkeur bij gelijke urenprioriteit.",
            }[rule.split("=", 1)[1]])
    return " ".join(parts)
