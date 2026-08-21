# VIDIS Anbieter-Skills

Agentische Skills, mit denen **Anbieter digitaler Bildungsangebote** ihr Angebot selbst gegen die
**VIDIS Prüfkriterien V0.2** prüfen — auf dem eigenen Rechner, mit einem computer-use-fähigen
Agenten, ohne Daten an Dritte zu senden.

26 Kriterien in zwei Prüfbereichen: Recht & Datenschutz (RDS, 23) und IT-Sicherheit (ITS, 3).

**Maßgeblich ist immer der Originalkatalog von FWU:**
[Prüfkriterienkatalog VIDIS V0.2](https://www.vidis.schule/wp-content/uploads/sites/10/2024/12/Pruefkriterien-VIDIS-V0.2.pdf).
Dieses Repo ist eine Arbeitshilfe dazu, kein Ersatz und keine autoritative Fassung.

Die **VIDIS-Prüfung** selbst bedeutet: *Validieren der Erfüllung der Kriterien zur Teilnahme am
VIDIS-Verfahren* — siehe [Teilnahmeprozess für Anbieter](https://www.vidis.schule/teilnahmeprozess/).
Der Selbstcheck bereitet darauf vor; er ersetzt die Prüfung nicht.

## Was hier drin ist

| Pfad | Inhalt |
|---|---|
| `skills/vidis-selbstcheck/` | Der Selbstcheck-Skill: Ablauf, Kriterienreferenz, Erhebungstechniken, Dossier-Format |
| `content/kriterien-v0_2.yaml` | Kriterienregistry — Code, Name, Prüfbereich, Pflichtstatus, Kriteriumstext |
| `content/selbstcheck-guide-v0_2.yaml` | Anleitungsinhalte je Kriterium — die einzige Quelle für alle Ausgaben |
| `dist/selbstcheck.json` | Datenmodell aller Kriterien samt Anleitungsinhalten — Quelle für den Kriterienkatalog im VIDIS-Portal |
| `tools/build.py` | Generator: erzeugt `dist/` und die Kriterienreferenz des Skills |

## Wie das zusammenspielt

Der Selbstcheck wird im **VIDIS-Portal** angestoßen, je dort geführtem Angebot. Er
ist dort verlinkt, wo die Datenschutzprüfung erklärt wird — er bereitet genau diese
externe Prüfung vor. Das Portal prüft selbst nichts; es hält den Kriterienkatalog
und erzeugt den Prompt.

Die Erhebung macht der Anbieter in beiden Fällen mit **seinem eigenen Agenten**.
Wo das Ergebnis liegt, entscheidet er pro Angebot:

**„Nur bei mir" — der Standard.**

1. Im Portal den Prompt anzeigen. Er enthält keinen Zugang und kein Token.
2. Prompt in den eigenen Agenten einfügen. Der Prompt verweist auf den Skill aus
   diesem Repo — der Agent holt sich die aktuelle Kriterienanleitung also hier,
   nicht aus einer im Prompt eingefrorenen Kopie.
3. Der Agent erhebt die Belege lokal und legt `dossier.md` und `befund.json` beim
   Anbieter ab. Im Portal wird zu diesem Angebot kein Status, kein Nachweis und
   keine Notiz gespeichert.

**„Im VIDIS-Portal" — wenn der Anbieter Bewertung, Verlauf und Bericht dort haben
will.**

1. Im Portal am Angebot einen Zugang erzeugen. Das Portal liefert einen
   kopierbaren Prompt mit einem Token, das ausschließlich für dieses eine Angebot
   gilt und nach kurzer Zeit verfällt.
2. Prompt in den eigenen Agenten einfügen — wie oben.
3. Der Agent liest über `GET /agent/selbstcheck` den Angebotskontext und den
   Katalog, erhebt die Belege lokal und schreibt die Befunde über
   `PUT /agent/selbstcheck/befund` zurück.
4. Im Portal erscheinen die Befunde als agentisch eingetragen. Der Anbieter prüft
   sie und verantwortet die Aussage.

Der Anbieter braucht dafür keine Installation aus diesem Repo — nur einen
computer-use-fähigen Agenten, der den Skill laden kann.

## Skill benutzen

Den Ordner `skills/vidis-selbstcheck/` in das Skill-Verzeichnis des Agenten legen.
Im Regelfall reicht der Prompt aus dem Portal; der Skill lässt sich aber auch ganz
ohne Portal für eine reine Vorabprüfung anstoßen.

**Voraussetzungen:** ein Browser mit Entwicklerwerkzeugen, `curl`, `openssl`, `jq`.
Kein weiteres Werkzeug nötig.

## Inhalte ändern

Alle Anleitungsinhalte stehen in `content/selbstcheck-guide-v0_2.yaml`. Nach jeder Änderung:

```bash
python3 tools/build.py
```

Das erzeugt `dist/selbstcheck.json` und
`skills/vidis-selbstcheck/references/kriterien.md` neu. Diese beiden Dateien werden **nicht** von
Hand bearbeitet.

Ändert sich der Katalog, müssen die eingebetteten Kopien in den Portalen
mitgezogen werden — sie liegen dort als Ressource, damit ein Portal zur Laufzeit
nicht von diesem Repo abhängt:

- VIDIS-Portal: `services/vidis-service/src/main/resources/selbstcheck/katalog-v0_2.json`
- BMI Anbieterportal: `services/anbieter-service/src/main/resources/selbstcheck/katalog-v0_2.json`

Prüfen, dass Registry und Anleitung deckungsgleich sind:

```bash
python3 tools/check.py
```

Benötigt nur PyYAML.

## Beitragen

Rückmeldungen sind ausdrücklich erwünscht, gerade von Agenten, die den Skill
gerade an einem echten Produkt durchgearbeitet haben. Issues und Pull Requests
für:

- Prüfanleitungen, Suchmuster oder Befehle, die nicht mehr funktionieren oder
  etwas anderes liefern als beschrieben
- fehlende Stolperfallen
- mehrdeutige Formulierungen, oder solche, die dem
  [Originalkatalog](https://www.vidis.schule/wp-content/uploads/sites/10/2024/12/Pruefkriterien-VIDIS-V0.2.pdf)
  widersprechen — der Katalog gewinnt, dann ist die Arbeitshilfe falsch
- Präzisierungen, die ein Kriterium reproduzierbar bewertbar machen

Inhaltliche Änderungen gehören nach `content/` und werden über `tools/build.py`
generiert; `references/kriterien.md` und `dist/` werden nicht von Hand bearbeitet.

Ein Beitrag beschreibt die Lücke in der Anleitung, **nicht den Befund am
geprüften Angebot**: keine Belege, Hostnamen, Zugangsdaten, Screenshots oder
Produktnamen aus einem Durchgang. Wer im Auftrag eines Anbieters prüft, fragt
diesen vorher.

## Abgrenzung

Der Selbstcheck ist eine **Selbstauskunft zur Vorbereitung** der VIDIS-Prüfung
([Validieren der Erfüllung der Kriterien zur Teilnahme am VIDIS-Verfahren](https://www.vidis.schule/teilnahmeprozess/)). Er ist kein
Prüfbescheid und keine Rechtsberatung. Inhaltliche Bewertungen zu Impressum,
Datenschutzerklärung, AGB, AVV, Werbung und Jugendmedienschutz brauchen eine fachlich
verantwortliche Person.

Mehrere Kriterien sind grundsätzlich nicht maschinell entscheidbar — sie stehen in Verträgen und
internen Listen, nicht im Produkt. Ein ehrliches „Klärung nötig" ist dort das richtige Ergebnis.

## Lizenz

MIT — siehe [LICENSE](LICENSE).
