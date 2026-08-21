---
name: vidis-selbstcheck
description: Führt einen VIDIS-Selbstcheck für ein digitales Bildungsangebot durch — prüft die VIDIS Prüfkriterien V0.2 (Recht & Datenschutz, IT-Sicherheit) am eigenen Angebot und erstellt ein belegtes Prüf-Dossier. Nutze diesen Skill, wenn Anbieter ihr Angebot vor der VIDIS-Prüfung selbst bewerten wollen, wenn nach VIDIS-Kriterien, VIDIS-Konformität oder VIDIS-Prüfkriterien gefragt wird, oder wenn Cookies, Tracking, Werbefreiheit, Impressum, Datenschutzerklärung, AGB, AVV oder TLS eines Bildungsangebots gegen VIDIS-Anforderungen geprüft werden sollen.
---

# VIDIS Selbstcheck

Du führst einen Selbstcheck gegen die **VIDIS Prüfkriterien V0.2** durch: 26 Kriterien in den
Prüfbereichen Recht & Datenschutz (RDS, 23) und IT-Sicherheit (ITS, 3), alle als MUSS-Kriterien.

Maßgeblich ist der Originalkatalog von FWU:
[Prüfkriterienkatalog VIDIS V0.2](https://www.vidis.schule/wp-content/uploads/sites/10/2024/12/Pruefkriterien-VIDIS-V0.2.pdf).
Verlinke ihn, wenn du dem Anbieter gegenüber Kriterien benennst — was hier steht, ist eine
Arbeitshilfe, nicht die autoritative Fassung. Bei Zweifeln gilt das Original.

Die **VIDIS-Prüfung** bedeutet: *Validieren der Erfüllung der Kriterien zur Teilnahme am
VIDIS-Verfahren* ([Teilnahmeprozess für Anbieter](https://www.vidis.schule/teilnahmeprozess/)). Erkläre das dem Anbieter so, wenn
danach gefragt wird.

Das Ergebnis ist ein **Dossier**: pro Kriterium ein begründeter Status mit Belegen. Es ist eine
Selbstauskunft zur Vorbereitung der Prüfung, kein Prüfbescheid und keine Rechtsberatung.

## Grundregeln

Diese Regeln gelten für den gesamten Ablauf und haben Vorrang vor Vollständigkeit:

1. **Keine erfundenen Belege.** Jeder Status stützt sich auf etwas, das du tatsächlich beobachtet
   oder das der Anbieter dir vorgelegt hat. Was du nicht geprüft hast, wird nicht bewertet.
2. **`Klärung nötig` ist ein gültiges Ergebnis.** Mehrere Kriterien sind ohne Vertrags- oder
   Produktkontext grundsätzlich nicht maschinell entscheidbar. Rate nicht — frage, oder halte die
   offene Frage fest. Ein Dossier mit 8 ehrlichen Klärungspunkten ist brauchbar, eines mit 26
   geratenen `erfüllt` ist wertlos und fällt in der Prüfung auf.
3. **Verlinke die Quelle, statt sie zu ersetzen.** Wenn du ein Kriterium zitierst oder
   zusammenfasst, nenne den Originalkatalog. Der Anbieter muss dich gegenprüfen können.
4. **Keine rechtliche Bewertung.** Bei Impressum, Datenschutzerklärung, AGB, AVV, Werbung und
   Jugendmedienschutz stellst du fest, was vorhanden ist und was fehlt. Ob eine Klausel wirksam
   oder eine Angabe ausreichend ist, entscheidet eine fachlich verantwortliche Person. Sage das,
   statt es zu ersetzen.
5. **Nur Testdaten.** Für angemeldete Bereiche ausschließlich Testzugänge verwenden, nie echte
   Konten von Schülerinnen, Schülern oder Lehrkräften. Zugangsdaten erfragst du beim Anbieter und
   schreibst sie in kein Artefakt.
6. **Nur eigene Angebote.** Dieser Skill prüft das Angebot der Person, die ihn ausführt. Prüfe
   keine fremden Angebote ohne deren Auftrag. Ein Portal-Zugang aus dem Prompt gilt für genau
   ein Angebot — versuche nicht, damit andere Angebote zu erreichen.
7. **Zielgruppe entscheidet den Maßstab.** Bei Schülerinnen und Schülern gelten Cookies, Tracking
   und Werbung strenger als bei Lehrkräften. Bei `beide` gilt für alle von Schülerinnen und
   Schülern erreichbaren Bereiche der strengere Maßstab. Kläre die Zielgruppe zuerst — ohne sie
   sind mehrere Kriterien nicht bewertbar.

## Ablauf

### Phase 1 — Prüfgegenstand festlegen

Frage den Anbieter, bevor du etwas prüfst. Ohne diese Angaben sind Befunde später nicht zuordenbar:

- **Zielgruppe:** Schülerinnen und Schüler, Lehrkräfte oder beide?
- **Produkt-URL** und **alle weiteren Hostnamen**: Web, API, Assets, Login, Admin, Statusseite.
  Jeder Host wird einzeln geprüft — TLS- und Weiterleitungsfehler sitzen fast immer auf einem
  Nebenhost.
- **Produktvariante und Version:** Werbefreiheit und Cookies unterscheiden sich oft zwischen
  kostenloser und bezahlter Variante. Halte fest, welche geprüft wird.
- **Rechtstexte:** URLs oder Dateien für Impressum, Datenschutzerklärung, AGB, AVV mit Anlagen.
- **Testzugänge** für Schüler- und Lehrkräfteperspektive, falls angemeldete Bereiche geprüft werden.
- **Quellcode-Zugriff?** Falls ja, sind CDN-, Tracking- und Fingerprinting-Fundstellen zusätzlich
  im Code prüfbar.

Lege einen Belegordner an (`belege/<datum>/`) und halte diese Angaben dort als `pruefgegenstand.md`
fest. Alle späteren Nachweise verweisen darauf.

### Phase 2 — Technische Erhebung

Erhebe die messbaren Belege selbst. `references/erhebung.md` enthält die konkreten Befehle,
Konsolen-Snippets und die Auswertungslogik für jeden Signaltyp:

- Transport: http-Aufruf, Weiterleitung, HSTS, veraltete TLS-Versionen — **je Host**
- Cookies, Local Storage, Session Storage, IndexedDB, Cache Storage, Service Worker
- Netzwerkaufrufe als HAR-Aufzeichnung; daraus Fremd-Domains, Tracking-, Werbe- und CDN-Aufrufe
- Trackingpixel und Fingerprinting-Signale
- Erreichbarkeit und Inhalt der Rechtstexte

Führe jeden Durchgang **mit leerem Browserprofil** und **ohne Zustimmung im Consent-Banner** durch.
Was vor der Zustimmung gesetzt wird, ist der entscheidende Befund.

Wiederhole die Erhebung anschließend im **angemeldeten Bereich**, getrennt für Schüler- und
Lehrkräfteperspektive. Der öffentliche Durchgang übersieht sonst genau die Cookies und Tracker, die
im Produktkern sitzen.

### Phase 3 — Unterlagen erfragen

Neun Kriterien sind am Produkt nicht sichtbar. Sie stehen in Verträgen und internen Listen und du
kannst sie nicht durch Prüfen der Website ersetzen. Frage aktiv nach:

- Verarbeitungsverzeichnis-Auszug mit Zwecken je Verarbeitung (RDS-DEV-380)
- AVV mit Anlagen, insbesondere TOM und Subunternehmerliste (RDS-AGB-369, RDS-DEV-381)
- Subunternehmerliste **mit Verarbeitungsort und Mutterunternehmen** (RDS-DEV-466, RDS-CDN-379)
- Regelung zu Löschung und Herausgabe nach Vertragsende, inklusive Backup-Fristen (RDS-DEV-381)
- Bestellung des Datenschutzbeauftragten oder dokumentierte Prüfung der Bestellpflicht (RDS-DSO-383)
- Zweckdokumentation für pädagogisches Tracking (RDS-CUC-377)
- Sponsoring- und Partnerbeziehungen (RDS-SPE-370)

Liegt eine Unterlage nicht vor, ist das der Befund: `Klärung nötig` mit der offenen Frage, oder
`nicht erfüllt`, wenn das Fehlen selbst der Mangel ist.

### Phase 4 — Bewerten

Arbeite `references/kriterien.md` Kriterium für Kriterium durch. Dort steht pro Kriterium, was
automatisiert prüfbar ist, wo die Automatik endet, welche Schritte die eigene Prüfung umfasst,
welche Stolperfallen häufig auftreten und welche Nachweise erwartet werden.

Vergib je Kriterium genau einen Status:

| Status | Wert für die API | Wann |
|---|---|---|
| erfüllt | `ERFUELLT` | Beleg vorhanden, der die Anforderung deckt — für den festgelegten Prüfgegenstand |
| nicht erfüllt | `NICHT_ERFUELLT` | Konkreter Befund, der der Anforderung widerspricht |
| Klärung nötig | `KLAERUNG_NOETIG` | Fachliche oder rechtliche Entscheidung offen, oder Unterlage fehlt |
| nicht zutreffend | `NICHT_ZUTREFFEND` | Anforderung greift für dieses Angebot nachweislich nicht — mit Begründung |
| offen | `OFFEN` | Nicht geprüft. Nicht mitsenden, statt zu raten. |

Zu jedem Status gehören: **Beleg** (Datei, Fundstelle, Screenshot) und bei allem außer `erfüllt`
eine **Notiz** mit Begründung und nächstem Schritt.

Bei `nicht erfüllt` nenne die Behebung aus `references/kriterien.md`, konkret auf den Befund
bezogen — nicht als allgemeine Empfehlung.

### Phase 5 — Befund zurückschreiben und zusammenfassen

Enthält der Prompt einen Portal-Zugang (Basis-URL und Token), dann:

1. Lies zuerst `GET /agent/selbstcheck` — der Kriterienkatalog von dort ist
   maßgeblich, und `kriterien` zeigt, was ein früherer Durchgang schon eingetragen
   hat.
2. Schreibe die Befunde über `PUT /agent/selbstcheck/befund` zurück. Sende nur
   Kriterien, die du geprüft hast; nicht übermittelte behalten ihren Stand, du
   kannst also in mehreren Durchgängen berichten.
3. Halte in `testgrenzen` fest, was du nicht prüfen konntest und warum.

Der Zugang gilt nur für dieses eine Angebot und läuft nach kurzer Zeit ab. Bei
HTTP 401 bitte den Anbieter um einen neuen Zugang im Portal — versuche es nicht
erneut mit demselben Token.

Lege zusätzlich `dossier.md` im Belegordner ab: die lesbare Fassung samt
Erhebungskontext, die zu den Belegen gehört.

Ohne Portal-Zugang legst du den Befund als `befund.json` ab, damit er später
nachgetragen werden kann.

Format und Statuswerte stehen in `references/dossier.md`.

Schließe mit einer **Zusammenfassung im Klartext**: wie viele Kriterien erfüllt,
was blockiert eine Freigabe, welche drei Punkte sind zuerst anzugehen, und welche
Entscheidungen brauchen eine fachlich verantwortliche Person.

## Referenzen

Lade diese Dateien, wenn du sie brauchst — nicht vorab alle:

| Datei | Wann |
|---|---|
| `references/kriterien.md` | Immer in Phase 4. Alle 26 Kriterien im Detail. |
| `references/erhebung.md` | In Phase 2. Befehle, Konsolen-Snippets, Auswertung je Signaltyp. |
| `references/dossier.md` | In Phase 5. Portal-Endpunkte, Statuswerte, Dossier-Aufbau. |

## Häufigster Fehler

Der Selbstcheck wird nur öffentlich und nur auf der Hauptdomain durchgeführt. Damit bleiben die
Befunde unentdeckt, die in der Prüfung auffallen: Cookies, die erst nach dem Login gesetzt werden,
ein API-Host ohne TLS-Erzwingung, Werbung in der kostenlosen Variante, und Rechtstexte, die im
angemeldeten Bereich nicht verlinkt sind. Prüfe **jeden Host** und **beide Perspektiven**.
