# Technische Erhebung — Befehle, Snippets, Auswertung

> Maßgeblich ist der [Prüfkriterienkatalog VIDIS V0.2](https://www.vidis.schule/wp-content/uploads/sites/10/2024/12/Pruefkriterien-VIDIS-V0.2.pdf).

Diese Referenz gehört zu Phase 2 des Skills `vidis-selbstcheck`. Sie ersetzt ein installiertes
Prüfwerkzeug: alles hier läuft mit `curl`, `openssl`, `jq` und einem Browser mit
Entwicklerwerkzeugen.

**Zwei Regeln für jeden Durchgang:**

1. **Leeres Browserprofil.** Ein privates Fenster oder ein frisches Profil. Ein aufgewärmtes
   Profil enthält Cookies aus früheren Besuchen und macht den Befund unbrauchbar.
2. **Nicht zustimmen.** Führe den ersten Durchgang ohne jede Interaktion mit dem Consent-Banner
   durch. Entscheidend ist, was *vor* der Zustimmung passiert.

Führe alles **je Hostname** aus, nicht nur für die Hauptdomain. Setze `HOST` und `URL` einmal:

```bash
HOST=app.beispiel.de
URL=https://app.beispiel.de
mkdir -p "belege/$(date +%F)" && cd "belege/$(date +%F)"
```

---

## 1. Transport und Weiterleitung — ITS-ENC-359, ITS-ENC-360

```bash
# http muss mit 301 auf https weiterleiten, nicht mit Inhalt antworten
curl -sS -o /dev/null -w 'http  -> %{http_code} %{redirect_url}\n' "http://$HOST"

# https muss antworten
curl -sS -o /dev/null -w 'https -> %{http_code}\n' "https://$HOST"

# Weiterleitungskette vollständig verfolgen — jeder Zwischenschritt muss https sein
curl -sSL -o /dev/null -w '%{url_effective} %{http_code}\n' "http://$HOST"

# HSTS
curl -sSI "https://$HOST" | grep -i 'strict-transport-security' || echo 'kein HSTS-Header'
```

**Auswertung**

| Beobachtung | Bewertung |
|---|---|
| `http -> 301 https://…` | erwartet |
| `http -> 200` mit Inhalt | **nicht erfüllt** (ITS-ENC-359 und 360) |
| `http -> 302` | Befund zu ITS-ENC-360: keine dauerhafte Weiterleitung |
| Weiterleitungskette mit http-Zwischenschritt | Befund zu ITS-ENC-360 |
| Weiterleitung nur auf Startseite, nicht auf Unterpfaden | Befund — deshalb auch einen tiefen Pfad testen |

Teste zusätzlich einen Unterpfad, nicht nur die Wurzel:

```bash
curl -sS -o /dev/null -w '%{http_code} %{redirect_url}\n' "http://$HOST/login"
```

## 2. Veraltete TLS-Protokolle — ITS-ENC-361

TLS 1.0 und TLS 1.1 müssen abgelehnt werden. SSLv3 unterstützt modernes OpenSSL oft nicht mehr;
lässt sich SSLv3 nicht testen, halte das als Testgrenze fest statt es als erfüllt zu bewerten.

```bash
for proto in tls1 tls1_1; do
  printf '%s: ' "$proto"
  openssl s_client -connect "$HOST:443" -"$proto" </dev/null >/dev/null 2>&1 \
    && echo 'ANGENOMMEN — Befund' || echo 'abgelehnt — erwartet'
done

# Gegenprobe: TLS 1.2 und 1.3 müssen funktionieren
for proto in tls1_2 tls1_3; do
  printf '%s: ' "$proto"
  openssl s_client -connect "$HOST:443" -"$proto" </dev/null >/dev/null 2>&1 \
    && echo 'ok' || echo 'FEHLT'
done

# Zertifikat: Gültigkeit und abgedeckte Namen
echo | openssl s_client -connect "$HOST:443" -servername "$HOST" 2>/dev/null \
  | openssl x509 -noout -dates -subject -ext subjectAltName
```

**Häufigster Befund:** TLS 1.2 ist auf dem Webhost erzwungen, der API- oder Asset-Host nimmt aber
noch TLS 1.0 an. Ein CDN vor dem Origin bringt außerdem seine eigene TLS-Konfiguration mit — prüfe
beide Terminierungspunkte.

## 3. Cookies und Browser-Speicher — RDS-CUC-371 bis 375, RDS-CUC-453

Im Browser mit leerem Profil die Seite laden, **nicht zustimmen**, dann in der Konsole:

```js
copy(JSON.stringify({
  url: location.href,
  cookies: document.cookie.split('; ').filter(Boolean),
  localStorage: Object.fromEntries(Object.entries(localStorage)),
  sessionStorage: Object.fromEntries(Object.entries(sessionStorage)),
  serviceWorker: navigator.serviceWorker
    ? (await navigator.serviceWorker.getRegistrations()).map((r) => r.scope)
    : [],
  cacheStorage: window.caches ? await caches.keys() : [],
  indexedDB: indexedDB.databases ? (await indexedDB.databases()).map((d) => d.name) : [],
}, null, 2));
```

`document.cookie` zeigt keine `HttpOnly`-Cookies. Die vollständige Liste mit Laufzeit und Flags
steht in den Entwicklerwerkzeugen unter *Application → Cookies* — sichere sie als Screenshot.

**Auswertung je Eintrag.** Für jeden Cookie und jeden Storage-Schlüssel diese Kette beantworten:

1. Wozu dient er? Wenn niemand das beantworten kann, ist er nicht als erforderlich belegbar.
2. Bricht das Produkt ohne ihn? Nur dann ist er technisch erforderlich.
3. Ist er einwilligungsbedürftig? Dann darf er bei Zielgruppe SuS nicht ohne Weiteres gesetzt werden.
4. Steht er in der Datenschutzerklärung, mit Zweck, Anbieter und Speicherdauer? (RDS-CUC-453)

**Einstufung.** Lass die Namen einstufen, statt selbst zu raten.

*Mit Portal-Zugang* — der Endpunkt kennt die Datenbank und liefert je Name eine Begründung:

```bash
curl -sS -X POST "$BASIS_URL/agent/selbstcheck/cookie-einstufung" \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{"namen":["_ga","PHPSESSID","lernwelt_fortschritt"]}' | jq .
```

Antwort je Name: `einstufung` (`TECHNISCH_ERFORDERLICH`, `EINWILLIGUNGSBEDUERFTIG`,
`PRUEFPFLICHTIG`), `begruendung`, und bei Datenbanktreffern Plattform, Kategorie, Zweck und
Speicherdauer. Nimm die Begründung in die Notiz auf — sie ist der Teil, den die Prüfung lesen kann.

*Ohne Portal-Zugang* — dieselben Regeln von Hand, Datengrundlage
[Open Cookie Database (EDPB)](https://github.com/jkwakman/Open-Cookie-Database) (Apache-2.0):

| Kategorie der Datenbank | Einstufung |
|---|---|
| `Functional`, `Security` | meist technisch erforderlich |
| `Analytics`, `Marketing`, `Personalization` | meist einwilligungsbedürftig |
| kein Treffer | prüfpflichtig |

Greift die Datenbank nicht, hilft der Name: Präfixe wie `_ga`, `_gid`, `_gat`, `_hj`, `fbp`,
`fbc`, `mp_`, `amplitude_`, `ajs_` deuten auf Tracking; `session`, `csrf`, `xsrf`, `phpsessid`,
`jsessionid`, `consent`, `cookieconsent` auf betrieblich Erforderliches.

**Drei Dinge, die du dabei nicht verwechseln darfst:**

1. **Ein Treffer ist ein Hinweis, keine Bewertung.** Die Datenbank sagt, wie ein Name im Web
   üblicherweise genutzt wird — nicht, ob der Cookie in *diesem* Angebot erforderlich ist.
2. **„Prüfpflichtig" heißt nicht harmlos.** Es heißt: der Zweck ist unbelegt. Setze dafür
   `KLAERUNG_NOETIG` und frage den Anbieter, wozu der Cookie dient.
3. **Setze aus einer Einstufung allein kein `ERFUELLT`.** Dass alle Cookies als funktional
   gelten, belegt nicht, dass keine anderen gesetzt werden — nur dass die gefundenen unauffällig
   sind.

Typisch nicht erforderlich: Analyse, A/B-Test, Marketing, Social Media, externe Video-Player,
Tag-Manager.

**Wiederholen nach Zustimmung.** Ein zweiter Durchgang *mit* Zustimmung zeigt, ob das Banner
tatsächlich blockiert oder nur die Auswahl protokolliert. Ist die Cookie-Liste vor und nach der
Zustimmung identisch, blockiert das Banner nichts — Befund zu RDS-CUC-371 und 372.

**Consent-Dialog selbst prüfen** (RDS-CUC-372): Ist „Ablehnen" gleich einfach erreichbar wie
„Zustimmen"? Sind Häkchen vorausgewählt? Ist der Widerruf später erreichbar? Screenshots sichern.

## 4. Netzwerkaufrufe, Tracking, Werbung, CDN — RDS-CUC-373, RDS-CUC-377, RDS-CDN-379, RDS-WER-384

Entwicklerwerkzeuge → *Network* → Seite neu laden → Rechtsklick → *Save all as HAR*.
Dann:

```bash
# Alle Fremd-Domains, die die Seite kontaktiert
jq -r '.log.entries[].request.url' aufzeichnung.har \
  | awk -F/ '{print $3}' | sort -u | grep -v -e "$HOST\$"

# Verdächtige Endpunkte gezielt suchen
jq -r '.log.entries[].request.url' aufzeichnung.har | grep -Ei \
  'doubleclick|googlesyndication|googletagservices|googleadservices|adsystem|adnxs|criteo|taboola|outbrain|facebook\.com/tr|/ads/|/pagead/|adsbygoogle|google-analytics|googletagmanager|matomo|hotjar|segment|mixpanel'

# Sehr kleine Bildantworten — typische Zählpixel (RDS-CUC-373)
jq -r '.log.entries[]
  | select(.response.content.mimeType != null and (.response.content.mimeType | startswith("image")))
  | select(.response.content.size < 200)
  | "\(.response.content.size)B \(.request.url)"' aufzeichnung.har
```

**Auswertung.** Jede Fremd-Domain braucht eine Zuordnung: technisch notwendig (z. B. eigenes CDN),
pädagogisch begründet, oder Befund. Für CDN und Fonts gilt: extern geladene Fonts und Skripte
übertragen die IP-Adresse an Dritte und lassen sich fast immer selbst hosten (RDS-CDN-379).

Pixel werden häufig über einen Tag-Manager nachgeladen und sind deshalb im Quellcode nicht
sichtbar — verlange die Tag-Manager-Konfiguration als Screenshot.

## 5. Fingerprinting — RDS-CUC-376

Mit Quellcode-Zugriff:

```bash
grep -rniE 'fingerprintjs|fpjs|clientjs|canvas.*todataurl|getimagedata|audiocontext|enumeratedevices|webglrenderingcontext.*getparameter|document\.fonts' \
  --include='*.js' --include='*.ts' --include='*.jsx' --include='*.tsx' --include='*.vue' . \
  | grep -v node_modules
```

Ohne Quellcode: in den Entwicklerwerkzeugen unter *Sources* die geladenen Bundles nach denselben
Begriffen durchsuchen (`Cmd/Ctrl+Shift+F`).

**Auswertung.** Jeder Fund braucht eine Produktbegründung. `enumerateDevices` in einer
Videofunktion zur Kameraauswahl ist legitim; dieselbe Abfrage auf der Startseite ist ein Befund.
Bot-Schutz- und Fraud-Detection-Dienste bilden regelmäßig Fingerprints — sie zählen mit, auch wenn
sie nicht als Tracking gedacht sind.

## 6. Rechtstexte abrufen und prüfen — RDS-IPF-364 bis 367, RDS-DSO-383

```bash
for pfad in impressum imprint datenschutz datenschutzerklaerung privacy agb nutzungsbedingungen; do
  code=$(curl -sS -o "seite-$pfad.html" -w '%{http_code}' "$URL/$pfad")
  echo "$pfad: $code"
done
```

**Auffindbarkeit** (RDS-IPF-364, 365) ist nicht per curl prüfbar, sondern nur im Browser:
Ist der Link im Footer **jeder** Seite sichtbar — auch in der Mobilansicht (Fenster auf ~375 px),
auch im angemeldeten Bereich, auch auf Formular- und Login-Seiten, und **ohne** vorherige
Cookie-Zustimmung? Screenshots je Ansicht sichern.

**Vollständigkeit Impressum** (RDS-IPF-366, §§ 5 und 6 DDG) — diese Punkte einzeln abhaken:

- Vollständiger Name des Anbieters und Rechtsform
- Ladungsfähige Anschrift mit Straße und Hausnummer (ein Postfach genügt nicht)
- Vertretungsberechtigte Person
- E-Mail-Adresse **und** ein zweiter schneller Kontaktweg
- Registergericht und Registernummer, sofern eingetragen
- Umsatzsteuer- oder Wirtschafts-Identifikationsnummer, sofern vorhanden
- Rechtsverweise auf das **DDG** — ein Verweis auf das TMG ist veraltet
- Aufsichtsbehörde bei zulassungspflichtiger Tätigkeit
- Bei audiovisuellen Mediendiensten: Sitzland und zuständige Landesmedienanstalt

**Vollständigkeit Datenschutzerklärung** (RDS-IPF-367, Art. 13 und 14 DSGVO):

- Name und Kontaktdaten des Verantwortlichen
- Kontaktdaten des Datenschutzbeauftragten (RDS-DSO-383) — ein eigener Kanal, nicht die
  allgemeine Info-Adresse; oder eine dokumentierte Prüfung, dass keine Bestellpflicht besteht
- Verarbeitungszwecke und Rechtsgrundlagen je Verarbeitung
- Empfänger oder Empfängerkategorien, inklusive Auftragsverarbeiter
- Drittlandtransfer mit Garantien
- Speicherdauer oder nachvollziehbare Kriterien — „soweit erforderlich" allein genügt nicht
- Betroffenenrechte: Auskunft, Berichtigung, Löschung, Einschränkung, Datenübertragbarkeit,
  Widerspruch, Widerruf der Einwilligung, Beschwerde bei einer Aufsichtsbehörde
- Folgen der Nichtbereitstellung
- Automatisierte Entscheidungsfindung und Profiling — eine Aussage ist auch dann nötig, wenn
  beides nicht stattfindet

Textsuche findet die Themen, nicht ihre Richtigkeit:

```bash
for begriff in verantwortlich datenschutzbeauftrag rechtsgrundlage empfänger speicherdauer \
               betroffenenrechte beschwerde widerruf profiling drittland; do
  printf '%-24s ' "$begriff"
  grep -qi "$begriff" seite-datenschutz.html && echo 'erwähnt' || echo 'FEHLT'
done
```

**Der entscheidende Abgleich** bleibt manuell: Steht jede tatsächlich eingesetzte Verarbeitung,
jedes Tool und jeder Dienstleister in der Erklärung? Vergleiche die Liste der Fremd-Domains aus
Schritt 4 mit den in der Erklärung genannten Empfängern. Differenzen sind Befunde.

## 7. Angemeldeter Bereich

Wiederhole Schritte 3 bis 6 nach dem Login, **getrennt** für Schüler- und Lehrkräfteperspektive.
Nutze nur Testzugänge. Klicke dabei mindestens eine Kernfunktion durch, nicht nur das Dashboard —
Tracker sitzen oft in Lern- und Auswertungsansichten.

Halte je Perspektive fest, welche Bereiche du erreicht hast. Was du nicht erreicht hast, wird nicht
bewertet, sondern als Testgrenze notiert.

## 8. Belege ablegen

```
belege/<datum>/
  pruefgegenstand.md      Zielgruppe, Hosts, Variante, Testzugänge (ohne Passwörter)
  transport.txt           Ausgaben aus Schritt 1 und 2, je Host
  storage-oeffentlich.json  Schritt 3, vor Zustimmung
  storage-nach-consent.json Schritt 3, nach Zustimmung
  storage-sus.json          Schritt 3, angemeldet als Schülerperspektive
  aufzeichnung.har          Schritt 4
  seite-*.html              Schritt 6
  screenshots/              Consent-Dialog, Footer je Ansicht, Cookie-Liste
  testgrenzen.md            Was nicht geprüft werden konnte und warum
```

`testgrenzen.md` ist kein Eingeständnis, sondern Teil des Ergebnisses. Eine Prüfung, die ihre
Grenzen benennt, ist belastbarer als eine, die sie verschweigt.
