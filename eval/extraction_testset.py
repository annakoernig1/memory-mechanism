# Goldstandard für die Extraktion: (Eingabe, Menge der erwarteten Typen)
# Bewusst mit Grenzfällen. Erweitere diese Liste - je mehr Fälle, desto belastbarer.
TESTSET = [
    ("Ich bin 34 und mache seit 10 Jahren Triathlon.", {"STABLE_FACT"}),
    ("Mein Knie zwickt seit dem Wochenende.", {"DYNAMIC_STATE"}),
    ("Ich laufe am liebsten früh morgens.", {"PREFERENCE"}),
    ("Ich hasse Intervalltraining.", {"PREFERENCE"}),
    ("Letzten Sonntag hatte ich einen super langen Lauf über 30 km.", {"EPISODE"}),
    ("Nächstes Jahr will ich die Challenge Roth finishen.", {"GOAL"}),
    ("Ich habe chronische Achillessehnenprobleme.", {"STABLE_FACT"}),
    ("Diese Woche fühle ich mich richtig stark.", {"DYNAMIC_STATE"}),
    ("Im Oktober will ich meinen Marathon unter 3:30 laufen.", {"GOAL"}),
    ("Ich vertrage keine Gels während des Laufs.", {"PREFERENCE"}),
    ("Danke, das hilft mir sehr weiter!", set()),
    ("Ich wohne in München und arbeite Vollzeit.", {"STABLE_FACT"}),
]
