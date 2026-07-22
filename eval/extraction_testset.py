# Goldstandard für die Extraktion: (Eingabe, Menge der erwarteten Typen)
# Bewusst mit Grenzfällen
TESTSET = [
    # === STABLE_FACT (Persönliche Daten, Equipment, Erfahrung) ===
    ("Ich bin 27 und mache seit 3 Jahren Triathlon.", {"STABLE_FACT"}),
    ("Ich bin 174cm groß und wiege aktuell 58kg.", {"STABLE_FACT"}),
    ("Ich ernähre mich vegan", {"STABLE_FACT"}),
    ("Ich habe eine Laktoseintoleranz.", {"STABLE_FACT"}),
    ("Ich fahre ein Cube Litening Air C:62 SLX als Rennrad und ein Cube Nuraod als Gravelbike.", {"STABLE_FACT"}),
    ("Mein Rollentrainer ist ein Elite Direto XRT mit Direktantrieb.", {"STABLE_FACT"}),
    ("Ich hatte 2025 eine Myokarditis und habe erst im Januar 2026 wieder angefangen zu trainieren.", {"STABLE_FACT"}),
    ("Mittwochs ist Vereinsschwimmen von 19 bis 20:30 Uhr mit Trainer.", {"STABLE_FACT"}),
    ("Montags sind alle Schwimmbäder in Stuttgart geschlossen.", {"STABLE_FACT"}),
    ("Meine Ruheherzfrequenz liegt bei etwa 45 bpm.", {"STABLE_FACT"}),

    # === DYNAMIC_STATE (Aktuelle Zustände, Verletzungen, Fitness) ===
    ("Ich habe mir beim Freiwasserschwimmen einen Wadenkrampf geholt und seitdem eine Gastrocnemius-Zerrung rechts.", {"DYNAMIC_STATE"}),
    ("Mein Physio hat mir grünes Licht für langsames Laufen gegeben.", {"DYNAMIC_STATE"}),
    ("Meine FTP liegt laut Diagnostik bei 174 Watt, aber nach Warsaw schätze ich sie auf 178 bis 182 Watt.", {"DYNAMIC_STATE"}),
    ("Meine VLaMax ist mit 0.80 viel zu hoch.", {"DYNAMIC_STATE"}),
    ("Ich habe meinen HR-Gurt verloren und mir einen neuen gekauft.", {"DYNAMIC_STATE"}),
    ("Ich fühle mich nach der chaotischen Trainingswoche frustriert und habe das Gefühl nur Rückschritte zu machen.", {"DYNAMIC_STATE"}),
    ("Die Hitze macht mir beim Training draußen gerade extrem zu schaffen, es hat 36 Grad.", {"DYNAMIC_STATE"}),
    ("Mein erster Lauf nach 4 Wochen Pause war komplett schmerzfrei.", {"DYNAMIC_STATE"}),
    ("Mein Gewicht ist von 60 auf 58 kg gefallen, mein Sportarzt hat moderates Gewichtsmanagement freigegeben.", {"DYNAMIC_STATE"}),

    # === PREFERENCE (Vorlieben, Abneigungen, Trainingsgewohnheiten) ===
    ("Ich fahre draußen lieber als auf der Rolle.", {"PREFERENCE"}),
    ("Ich möchte den Fokus auf Spaß setzen statt auf Ergebnisse.", {"PREFERENCE"}),
    ("Mir macht es mehr Spaß mit Freunden zu fahren als alleine Intervalle zu kloppen.", {"PREFERENCE"}),
    ("Ich fahre lieber Pässe als flach im Etschtal.", {"PREFERENCE"}),
    ("Ich möchte beim Schwimmen mehr an meiner Technik arbeiten.", {"PREFERENCE"}),
    ("Ich nutze neuerdings NRGY Gels mit 45g Carbs und das 90g Carbs Pulver für die Flaschen.", {"PREFERENCE"}),
    ("Morgens esse ich immer Brötchen oder Porridge.", {"PREFERENCE"}),
    ("Freitags um 21 Uhr schwimmen ist mir eigentlich zu spät.", {"PREFERENCE"}),

    # === EPISODE (Konkrete Trainingseinheiten, Wettkämpfe, Erlebnisse) ===
    ("In Warsaw bin ich die 1900m in 41 Minuten geschwommen, aber die erste 500m viel zu schnell.", {"EPISODE"}),
    ("Beim Radfahren in Warsaw hatte ich NP 162W bei IF 0.93 und nur 0.2 Prozent Decoupling über 2:42 Stunden.", {"EPISODE"}),
    ("Beim Duathlon in Echterdingen bin ich den ersten Lauf bei 4:49 gelaufen und dann im zweiten Lauf komplett eingebrochen.", {"EPISODE"}),
    ("Ich bin letzte Nacht 210km von Stuttgart nach Heidelberg und zurück gefahren, bei der zweiten Hälfte hatte es 40 Grad.", {"EPISODE"}),
    ("Im Camp am Kalterer See habe ich zweimal hintereinander IF 0.81 auf Pass-Touren geschafft.", {"EPISODE"}),
    ("Meine VO2max Intervalle draußen sind komplett schiefgelaufen, ich bin im ersten Intervall 239 Watt statt 225 Watt gefahren und musste dann abbrechen.", {"EPISODE"}),
    ("Beim Laktat-Stufentest auf der Bahn lag meine Schwelle bei 4:50 pro Kilometer mit 4.0 mmol Laktat.", {"EPISODE"}),
    ("Ich war mit einem Freund am Berg 3 mal 10 Minuten Sweetspot fahren, bin aber im ersten Block bei 196 Watt statt 165 Watt gefahren.", {"EPISODE"}),
    ("Heute habe ich meinen ersten Lauf nach der Wadenverletzung gemacht, 15 Minuten komplett schmerzfrei.", {"EPISODE"}),
    ("Im Trainingslager am Kalterer See haben wir Wasserschatten-Wechsel im Freiwasser geübt.", {"EPISODE"}),

    # === GOAL (Ziele, Pläne, Ambitionen) ===
    ("Ich möchte meine FTP auf 195 Watt steigern, Stretch-Ziel wären 200 Watt.", {"GOAL"}),
    ("Im Herbst will ich einen Halbmarathon unter 1:45 laufen, Stretch-Ziel wäre sub 1:40.", {"GOAL"}),
    ("Langfristig möchte ich 5km unter 20 Minuten laufen, das ist aber eher ein Ziel für 2027 oder 2028.", {"GOAL"}),
    ("Am 9. August fahre ich bei einer Staffel im Kraichgau den Radpart über 40km.", {"GOAL"}),
    ("Im August machen wir zwei Trainingslager, erst in Bad Säckingen und dann im Innsbrucker Land.", {"GOAL"}),

    # === NEGATIVE EXAMPLES (keine Kategorie, leeres Set) ===
    ("Danke, das hilft mir sehr weiter!", set()),
    ("Ja bitte, mach das so.", set()),
    ("Kannst du die Kalendereinträge auch noch anpassen?", set()),
    ("Ah sorry, hier das richtige File.", set()),
    ("Bist du schon fertig damit?", set()),
    ("Mache weiter.", set()),
    ("Okay, klingt gut.", set()),
    ("Wie soll ich verpflegen?", set()),
    ("Kann ich auch 2x400m statt 5min Stufen machen?", set()),
    ("Soll ich die VO2max Einheit heute auf der Rolle fahren?", set()),
    ("Gib mir nochmal die Tabelle mit dem Motto aus.", set()),
    ("Bist du sicher, dass ich solche Wattwerte so lange halten kann?", set()),
    ("Wo sind die .zwo Files?", set()),
    ("Du hast die Powerdaten falsch ausgelesen, die waren bei 223 Watt.", set()),
    ("Ja bitte, aktualisiere die Kalendereinträge.", set()),
]

