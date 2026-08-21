# Befund zurückschreiben und Dossier ausgeben

> Maßgeblich ist der [Prüfkriterienkatalog VIDIS V0.2](https://www.vidis.schule/wp-content/uploads/sites/10/2024/12/Pruefkriterien-VIDIS-V0.2.pdf).

Phase 5 des Skills hat zwei Teile: den Befund in das Anbieterportal zurückschreiben
(wenn der Prompt einen Zugang enthält) und ein lesbares Dossier ablegen.

## 1. Befund ins Portal schreiben

Der Prompt aus dem Portal enthält Basis-URL und Token. Beides gilt **nur für das
eine Angebot**, für das es ausgestellt wurde — es gibt keinen Pfadparameter und
keinen Weg zu einem anderen Angebot.

### Kontext lesen

```bash
curl -sS "$BASIS_URL/agent/selbstcheck" \
  -H "Authorization: Bearer $TOKEN" | jq .
```

Antwort: Angebotsdaten (`angebotName`, `produktwebsite`, `datenschutzerklaerung`,
`agb`), der vollständige `katalog` mit Prüfanleitung je Kriterium, und `kriterien`
mit dem bisherigen Stand. Lies das **zuerst** — der Katalog dort ist maßgeblich,
nicht eine Kopie aus dem Gedächtnis.

### Befund schreiben

```bash
curl -sS -X PUT "$BASIS_URL/agent/selbstcheck/befund" \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{
    "kriterien": [
      {
        "code": "ITS-ENC-359",
        "status": "NICHT_ERFUELLT",
        "nachweis": "belege/2026-08-21/transport.txt, Zeile 4",
        "notiz": "api.beispiel.de antwortet auf http mit 200 statt einer Weiterleitung. Behebung: https auf dem API-Host erzwingen."
      },
      {
        "code": "RDS-DEV-466",
        "status": "KLAERUNG_NOETIG",
        "nachweis": "Subunternehmerliste liegt nicht vor",
        "notiz": "Verarbeitungsorte nicht belegt. Offene Frage an den Datenschutz: greift der Support aus einem Drittland zu?"
      }
    ],
    "testgrenzen": "Angemeldeter Bereich nicht geprueft — kein Testzugang erhalten."
  }' | jq .
```

Antwort: `uebernommen` (Anzahl geänderter Kriterien) und `statusVerteilung` über
alle 26 Kriterien.

### Statuswerte

| Wert | Wann |
|---|---|
| `OFFEN` | Nicht geprüft. Der Ausgangszustand — nicht mitsenden, statt zu raten. |
| `ERFUELLT` | Beleg vorhanden, der die Anforderung für den festgelegten Prüfgegenstand deckt |
| `NICHT_ERFUELLT` | Konkreter Befund, der der Anforderung widerspricht |
| `KLAERUNG_NOETIG` | Fachliche oder rechtliche Entscheidung offen, oder Unterlage fehlt |
| `NICHT_ZUTREFFEND` | Anforderung greift für dieses Angebot nachweislich nicht — mit Begründung |

`KLAERUNG_NOETIG` ist ein gültiges Ergebnis, kein Platzhalter.

### Regeln für das Schreiben

- **Nur senden, was du geprüft hast.** Nicht übermittelte Kriterien behalten ihren
  Stand — du kannst also in mehreren Durchgängen berichten, während du die Phasen
  abarbeitest. Ein Kriterium ohne Befund lässt du weg, statt `OFFEN` zu schicken.
- **`nachweis` verweist auf etwas, das existiert.** Keine erfundenen Dateinamen.
- **Bei `NICHT_ERFUELLT`** enthält `notiz` den konkreten Befund *und* die Behebung,
  bezogen auf diesen Befund — nicht die allgemeine Empfehlung aus der
  Kriterienreferenz.
- **Bei `KLAERUNG_NOETIG`** enthält `notiz` die offene Frage und wer sie entscheidet.
- **`testgrenzen`** hält fest, was du nicht prüfen konntest und warum.
- **Keine Passwörter, Tokens oder echten personenbezogenen Daten** in `nachweis`
  oder `notiz`. Sie landen in einem Prüfartefakt.
- Ein unbekannter Code wird mit HTTP 400 und `selbstcheck_kriterium_unknown`
  abgelehnt. Prüfe die Codes gegen den `katalog` aus dem Kontext.
- HTTP 401 heißt: Token unbekannt, widerrufen oder abgelaufen. Bitte den Anbieter,
  im Portal einen neuen Zugang zu erzeugen — versuche es nicht erneut mit demselben
  Token.

## 2. Dossier ablegen

Schreibe zusätzlich `dossier.md` in den Belegordner. Das Portal hält den Stand je
Kriterium; das Dossier ist die lesbare Fassung samt Erhebungskontext, die zu den
Belegen gehört.

```markdown
# VIDIS Selbstcheck — <Anbieter>, <Angebot>

## Prüfgegenstand
- Angebot, URL, geprüfte Hostnamen
- Zielgruppe und Produktvariante
- Durchgeführt von, Datum
- Kriterienstand: VIDIS Prüfkriterien V0.2, 26 Kriterien

## Ergebnis auf einen Blick
| Status | Anzahl |
|---|---|
| erfüllt | n |
| nicht erfüllt | n |
| Klärung nötig | n |
| nicht zutreffend | n |
| offen | n |

## Was eine Freigabe blockiert
Die `NICHT_ERFUELLT`-Befunde, nach Aufwand oder Risiko sortiert, mit Behebung und
verantwortlicher Person.

## Offene Klärungen
Die `KLAERUNG_NOETIG`-Bewertungen mit der offenen Frage und wer sie entscheidet.

## Befunde je Prüfbereich
### IT-Sicherheit (ITS)
### Recht & Datenschutz (RDS)
Je Kriterium: Code, Name, Status, Beleg, Notiz.

## Testgrenzen
Was nicht geprüft werden konnte und warum.
```

Die Abschnitte „Was eine Freigabe blockiert" und „Offene Klärungen" stehen **vor**
der Kriterienliste. Sie sind der Teil, den Entscheidende lesen; die vollständige
Liste ist der Anhang.

## 3. Abschluss im Chat

Fasse im Klartext zusammen:

- Verteilung der Status über die 26 Kriterien
- Was eine Freigabe blockiert
- Die drei Punkte, die zuerst anzugehen sind
- Welche Entscheidungen eine fachlich verantwortliche Person brauchen — Recht,
  Datenschutz, Redaktion
- Was nicht geprüft werden konnte

Verkaufe das Ergebnis nicht besser, als es ist. Ein Selbstcheck, der Lücken
benennt, ist der Zweck der Übung.

## Ohne Portal-Zugang

Enthält der Prompt keinen Zugang, entfällt Schritt 1. Lege den Befund dann als
`befund.json` im selben Format wie der Request-Body oben ab (`kriterien`,
`testgrenzen`), damit er später im Portal nachgetragen werden kann.
