# VIDIS Prüfkriterien V0.2 — Kriterienreferenz für den Selbstcheck

> Erzeugt von `tools/build.py`. Nicht direkt bearbeiten — Inhalte stehen in `content/selbstcheck-guide-v0_2.yaml`.

Diese Datei deckt alle 26 aktiven Kriterien der VIDIS Prüfkriterien V0.2 ab. Sie ist die Nachschlagequelle des Skills `vidis-selbstcheck`: pro Kriterium steht dort, was automatisiert entscheidbar ist, wo die Automatik an ihre Grenzen kommt, wie selbst geprüft wird und welche Nachweise erwartet werden.

**Maßgeblich ist der Originalkatalog von FWU:** [Prüfkriterienkatalog VIDIS V0.2](https://www.vidis.schule/wp-content/uploads/sites/10/2024/12/Pruefkriterien-VIDIS-V0.2.pdf). Alles hier ist eine Arbeitshilfe dazu, kein Ersatz.

Die VIDIS-Prüfung selbst bedeutet: Validieren der Erfüllung der Kriterien zur Teilnahme am VIDIS-Verfahren (siehe [Teilnahmeprozess für Anbieter](https://www.vidis.schule/teilnahmeprozess/)).

Registry: `content/kriterien-v0_2.yaml`  
Inhalte: `content/selbstcheck-guide-v0_2.yaml`

## Phasen

- **1. Vorbereitung** — keine Kriterien, nur Arbeitsschritte
- **2. Technische Erhebung** — keine Kriterien, nur Arbeitsschritte
- **3. Technische Kriterien** — ITS-ENC-359, ITS-ENC-360, ITS-ENC-361, RDS-CDN-379, RDS-CUC-371, RDS-CUC-372, RDS-CUC-373, RDS-CUC-374, RDS-CUC-375, RDS-CUC-376, RDS-CUC-377
- **4. Impressum, Datenschutzerklärung, Cookie-Beschreibung** — RDS-CUC-453, RDS-DSO-383, RDS-IPF-364, RDS-IPF-365, RDS-IPF-366, RDS-IPF-367
- **5. Verträge, Dienstleister, Datenflüsse** — RDS-AGB-368, RDS-AGB-369, RDS-DEV-380, RDS-DEV-381, RDS-DEV-466
- **6. Inhalte, Werbung, Jugendmedienschutz** — RDS-SPE-370, RDS-VIN-354, RDS-WER-384, RDS-WER-385
- **7. Abschluss und Nachweise** — keine Kriterien, nur Arbeitsschritte

## 1. Vorbereitung

Bevor geprüft wird, wird der Prüfgegenstand festgelegt. Ohne diese Festlegung sind Ergebnisse später nicht zuordenbar: Werbefreiheit kann in der kostenlosen Variante anders aussehen als in der bezahlten, und Cookies unterscheiden sich zwischen angemeldetem und öffentlichem Bereich.

- [ ] Zielgruppe festlegen: richtet sich das Angebot an Schülerinnen und Schüler, an Lehrkräfte oder an beide? Die Zielgruppe entscheidet über den Maßstab bei Cookies, Tracking und Werbung.
- [ ] Produktvariante und Lizenz festhalten, die geprüft wird, inklusive Version oder Release-Stand.
- [ ] Alle Hostnamen des Angebots auflisten: Web, API, Assets, Login, Admin, Statusseite. Jeder Host wird einzeln geprüft.
- [ ] Rechtstexte zusammenstellen: Impressum, Datenschutzerklärung, AGB oder Nutzungsbedingungen, AVV mit Anlagen.
- [ ] Testzugänge für Schüler- und Lehrkräfteperspektive bereitstellen, ohne echte personenbezogene Daten.
- [ ] Verantwortliche Personen je Prüfbereich benennen: Technik, Datenschutz, Recht, Redaktion.

## 2. Technische Erhebung

Diese Phase sammelt die messbaren Belege: Transportverschlüsselung, Weiterleitungen, Cookies, Browser-Speicher, Netzwerkaufrufe und die Erreichbarkeit der Rechtstexte. Die Befehle unten laufen auf jedem Rechner mit curl, openssl und einem Browser. Der Skill vidis-selbstcheck führt dieselbe Erhebung agentisch durch und trägt die Ergebnisse direkt in ein Dossier ein.

- [ ] Erhebung je Hostname durchführen, nicht nur für die Hauptdomain.
- [ ] Transport prüfen: http-Aufruf, Weiterleitung, veraltete TLS-Versionen.
- [ ] Cookies und Browser-Speicher im Browser mit leerem Profil auslesen, ohne im Consent-Banner zuzustimmen.
- [ ] Netzwerkaufrufe aufzeichnen und als HAR-Datei sichern; sie belegen Tracking-, Werbe- und CDN-Aufrufe.
- [ ] Rechtstexte abrufen und als Datei mit Datum sichern.
- [ ] Erhebung im angemeldeten Bereich wiederholen, getrennt für Schüler- und Lehrkräfteperspektive.
- [ ] Alle Belege in einem Ordner je Prüfdatum ablegen, damit sie im Dossier referenzierbar sind.

**Weiterleitung von http auf https prüfen (ITS-ENC-359, ITS-ENC-360)**

```bash
curl -sS -o /dev/null -w 'http  -> %{http_code} %{redirect_url}\n' http://{HOST}
curl -sS -o /dev/null -w 'https -> %{http_code}\n' https://{HOST}
curl -sSI https://{HOST} | grep -i 'strict-transport-security' || echo 'kein HSTS-Header'
```

**Veraltete TLS-Protokolle prüfen (ITS-ENC-361)**

```bash
for proto in tls1 tls1_1; do
  printf '%s: ' "$proto"
  openssl s_client -connect {HOST}:443 -"$proto" </dev/null >/dev/null 2>&1 \
    && echo 'ANGENOMMEN — Befund' || echo 'abgelehnt — erwartet'
done
```

**Cookies und Browser-Speicher auslesen — im Browser-Konsolenfenster ausführen (RDS-CUC-371 bis 375, RDS-CUC-453)**

```bash
copy(JSON.stringify({
  url: location.href,
  cookies: document.cookie.split('; ').filter(Boolean),
  localStorage: Object.fromEntries(Object.entries(localStorage)),
  sessionStorage: Object.fromEntries(Object.entries(sessionStorage)),
  serviceWorker: navigator.serviceWorker
    ? (await navigator.serviceWorker.getRegistrations()).map((r) => r.scope)
    : [],
  indexedDB: indexedDB.databases ? (await indexedDB.databases()).map((d) => d.name) : [],
}, null, 2));
```

**Fremd-Domains aus einer HAR-Aufzeichnung auflisten (RDS-CUC-373, RDS-CDN-379, RDS-WER-384)**

```bash
jq -r '.log.entries[].request.url' aufzeichnung.har \
  | awk -F/ '{print $3}' | sort -u \
  | grep -v -e '{HOST}$'
```

**Rechtstexte sichern (RDS-IPF-364 bis 367)**

```bash
mkdir -p belege
for pfad in impressum datenschutz agb; do
  curl -sS -o "belege/$pfad.html" -w "$pfad: %{http_code}\n" "{URL}/$pfad"
done
```

## 3. Technische Kriterien

Diese Kriterien sind am Produkt selbst messbar. Die Erhebung aus Phase 2 liefert die Belege; zu klären bleiben Zweck und Notwendigkeit der gefundenen Cookies, Speicher und Signale sowie alle Bereiche, die ein öffentlicher Durchgang nicht erreicht.

### ITS-ENC-359 — Website nur über https:// aufrufbar

*MUSS-Kriterium, Bereich ITS, Automatisierung: automatisiert*

Alle Seiten des Angebots sind ausschließlich über https erreichbar.

**Automatisiert prüfbar.** Die automatisierte Prüfung ruft die Zielseiten über http und https auf und bewertet, ob Inhalte unverschlüsselt ausgeliefert werden.

**Grenzen der Automatik.** Die automatisierte Prüfung prüft die erreichten Seiten. Weitere Hosts, Subdomains und APIs sind nur enthalten, wenn sie im Crawl auftauchen.

**Benötigte Eingaben.** Produkt-URL.

**Selbst prüfen**

- Alle Hostnamen des Angebots auflisten: Web, API, Assets, Login, Statusseite, Admin.
- Je Host die http-Variante aufrufen und prüfen, ob Inhalte ausgeliefert werden statt einer Weiterleitung.
- Prüfen, ob Mixed Content auftritt: in den Entwicklerwerkzeugen auf Warnungen zu unverschlüsselten Ressourcen achten.
- Prüfen, ob HSTS gesetzt ist und mit welcher Laufzeit.
- Zertifikat prüfen: Gültigkeit, Kette, Abdeckung aller Hostnamen.

**Stolperfallen**

- Asset- oder API-Subdomain ohne https-Erzwingung.
- Mixed Content durch eine einzelne http-Ressource.
- Zertifikat deckt www ab, die Apex-Domain aber nicht.

**Behebung**

- https auf allen Hosts erzwingen und http nur für die Weiterleitung offen halten.
- HSTS mit ausreichender Laufzeit setzen.
- Alle Ressourcen auf https umstellen.

**Nachweise**

- Hostliste mit Prüfergebnis je Host.
- Zertifikats- und HSTS-Nachweis.

<details><summary>Kriteriumstext V0.2</summary>

Seiten des Angebots sind ausschließlich über https abrufbar.

</details>

### ITS-ENC-360 — Es sind Umleitungen von http auf https konfiguriert.

*MUSS-Kriterium, Bereich ITS, Automatisierung: automatisiert*

Aufrufe über http werden auf https umgeleitet.

**Automatisiert prüfbar.** Die automatisierte Prüfung ruft die http-Variante auf und prüft Statuscode und Ziel der Weiterleitung.

**Grenzen der Automatik.** Die automatisierte Prüfung prüft die im Crawl erreichten Hosts, nicht zwingend alle Subdomains.

**Benötigte Eingaben.** Produkt-URL.

**Selbst prüfen**

- Je Host die http-Variante aufrufen und den Statuscode prüfen. Erwartet wird 301 auf die https-Adresse.
- Prüfen, ob die Weiterleitung direkt auf https führt und nicht über weitere http-Zwischenstationen.
- Prüfen, ob der Pfad bei der Weiterleitung erhalten bleibt.
- Prüfen, ob auch Unterseiten und nicht nur die Startseite weitergeleitet werden.
- Weiterleitung für alle Subdomains prüfen.

**Stolperfallen**

- Weiterleitung nur auf der Startseite konfiguriert.
- 302 statt 301, dadurch keine dauerhafte Weiterleitung.
- Weiterleitungskette mit einem http-Zwischenschritt.

**Behebung**

- Dauerhafte Weiterleitung von http auf https für alle Hosts und Pfade konfigurieren.
- Weiterleitungsketten auf einen Schritt reduzieren.

**Nachweise**

- Aufzeichnung der Weiterleitung je Host, etwa als curl-Ausgabe.

<details><summary>Kriteriumstext V0.2</summary>

Es sind Umleitungen von http auf https konfiguriert.

</details>

### ITS-ENC-361 — Ablehnen veralteter TLS/SSL-Protokolle

*MUSS-Kriterium, Bereich ITS, Automatisierung: automatisiert*

Veraltete TLS- und SSL-Protokolle werden abgelehnt.

**Automatisiert prüfbar.** Die automatisierte Prüfung versucht Verbindungen mit SSLv3, TLS 1.0 und TLS 1.1 und bewertet, ob der Server sie ablehnt.

**Grenzen der Automatik.** Die automatisierte Prüfung prüft Protokollversionen. Cipher-Suiten, Schlüssellängen und Konfigurationsdetails prüft er nicht abschließend.

**Benötigte Eingaben.** Produkt-URL.

**Selbst prüfen**

- Je Host prüfen, ob Verbindungen mit TLS 1.0 und TLS 1.1 abgelehnt werden.
- Prüfen, ob TLS 1.2 und TLS 1.3 verfügbar sind.
- Cipher-Suiten prüfen und veraltete Verfahren ausschließen.
- Prüfen, ob alle Hosts dieselbe Konfiguration haben, auch API und Assets.
- Prüfen, ob eingesetzte Load Balancer oder CDNs eigene TLS-Konfigurationen mitbringen.

**Stolperfallen**

- TLS 1.2 nur auf dem Webhost erzwungen, API-Host bleibt offen.
- CDN erlaubt ältere Protokolle, obwohl der Origin sie ablehnt.
- Alte Konfiguration bleibt aktiv, weil sie nur an einer Stelle geändert wurde.

**Behebung**

- TLS 1.0 und 1.1 auf allen Hosts und Terminierungspunkten abschalten.
- Konfiguration zentral verwalten und wiederkehrend prüfen.

**Nachweise**

- TLS-Prüfergebnis je Host.
- Konfigurationsauszug des TLS-Terminierungspunkts.

<details><summary>Kriteriumstext V0.2</summary>

Veraltete TLS/SSL-Protokolle werden abgelehnt.

</details>

### RDS-CDN-379 — CDN nur zur Bereitstellung von Inhalten

*MUSS-Kriterium, Bereich RDS, Automatisierung: automatisiert*

Ein eingesetztes CDN dient ausschließlich der Bereitstellung von Inhalten und erfüllt die Anforderungen an Dienstleister.

**Automatisiert prüfbar.** Die automatisierte Prüfung prüft den Quellcode auf CDN-Einbindungen und externe Auslieferungsdomains.

**Grenzen der Automatik.** Der Funktionsumfang und die vertragliche Ausgestaltung des CDN sind nur aus Konfiguration und Vertrag zu belegen; dafür ist ein Quellcode-Pfad und interne Dokumentation nötig.

**Benötigte Eingaben.** Quellcode-Pfad.

**Selbst prüfen**

- Alle CDN- und Edge-Dienste auflisten, inklusive Bild-, Font- und Skript-Hosts.
- Je Dienst prüfen, welche Funktionen aktiv sind: reine Auslieferung, oder zusätzlich Bot-Schutz, Analytics, A/B-Test, Edge-Personalisierung?
- Prüfen, ob TLS am Edge terminiert und ob dabei Inhalte einsehbar sind.
- Prüfen, ob Zugriffsprotokolle beim CDN entstehen, wie lange sie bleiben und wer sie sieht.
- Prüfen, ob AVV und Verarbeitungsort für den CDN-Anbieter dokumentiert sind.
- Externe Fonts und Skripte prüfen: sie übertragen IP-Adressen an Dritte und lassen sich meist selbst hosten.

**Stolperfallen**

- CDN-Analytics oder Bot-Schutz aktiv, dadurch mehr als reine Auslieferung.
- Google Fonts oder Skripte direkt von Drittanbieter-Domains geladen.
- CDN-Anbieter nicht in der Subunternehmerliste.

**Behebung**

- CDN-Zusatzfunktionen abschalten, die über die Auslieferung hinausgehen.
- Fonts und Skripte selbst hosten.
- CDN in Subunternehmerliste und AVV aufnehmen, Verarbeitungsort dokumentieren.

**Nachweise**

- CDN-Konfigurationsübersicht mit aktiven Funktionen.
- AVV des CDN-Anbieters und Verarbeitungsort.

<details><summary>Kriteriumstext V0.2</summary>

Es wird kein CDN genutzt, das nicht ausschließlich der reinen Bereitstellung von Inhalten dient.
Darüber hinaus erfüllt das CDN die Voraussetzungen des Prüfunterbereichs Dienstleister.

</details>

### RDS-CUC-371 — Nicht essenzielle Cookies

*MUSS-Kriterium, Bereich RDS, Automatisierung: automatisiert*

Bei einem Angebot für Schülerinnen und Schüler werden keine Cookies gesetzt, die für den Betrieb nicht erforderlich sind.

**Automatisiert prüfbar.** Die automatisierte Prüfung öffnet die Seiten mit einem echten Browser, liest alle gesetzten Cookies aus und stuft sie anhand der Open Cookie Database EDPB und ergänzender Heuristiken als essenziell, nicht essenziell oder prüfpflichtig ein.

**Grenzen der Automatik.** Cookies, die erst nach Login, nach Zustimmung oder in bestimmten Produktbereichen gesetzt werden, sieht der öffentliche Durchgang nicht. Unbekannte Cookie-Namen bleiben prüfpflichtig.

**Benötigte Eingaben.** Produkt-URL und Quellcode-Pfad.

**Selbst prüfen**

- Browser mit leerem Profil öffnen, Entwicklerwerkzeuge starten und die Seite laden, ohne im Consent-Banner zuzustimmen.
- Unter Anwendung bzw. Application die Cookies auflisten und jeden Eintrag notieren: Name, Domain, Laufzeit, Zweck.
- Für jeden Cookie die Frage beantworten: Bricht das Produkt ohne ihn? Nur dann ist er erforderlich.
- Typische nicht erforderliche Cookies gezielt suchen: Analyse, A/B-Test, Marketing, Social Media, externe Video-Player.
- Denselben Durchgang im angemeldeten Bereich und in mindestens einer Kernfunktion wiederholen.
- Ergebnis mit der Cookie-Liste in der Datenschutzerklärung abgleichen.

**Stolperfallen**

- Analyse-Cookie schon vor der Zustimmung gesetzt.
- Eingebetteter Video-Player setzt Marketing-Cookies mit dem Seitenaufruf.
- Consent-Banner blockiert nichts, sondern protokolliert nur die Auswahl.
- Cookies erst nach Login gesetzt und deshalb im öffentlichen Durchgang unsichtbar.

**Behebung**

- Nicht erforderliche Cookies für die Zielgruppe Schülerinnen und Schüler vollständig abschalten.
- Externe Einbettungen entfernen oder durch datenschutzfreundliche Varianten mit Klick-vor-Laden ersetzen.
- Sicherstellen, dass Skripte tatsächlich erst nach Zustimmung geladen werden, wo Einwilligung zulässig ist.

**Nachweise**

- Cookie-Inventar aus capture.json oder als Screenshot der Entwicklerwerkzeuge.
- Begründung je Cookie, warum er erforderlich ist.

<details><summary>Kriteriumstext V0.2</summary>

Es werden keine Cookies gesetzt, die für den Betrieb der Webseite nicht erforderlich sind, sofern sich diese an die Nutzergruppe der Schülerinnen und Schüler richten.
Richtet sich das Angebot an Lehrkräfte, wird dafür eine entsprechende Einwilligung eingeholt.

</details>

### RDS-CUC-372 — Cookies allgemein

*MUSS-Kriterium, Bereich RDS, Automatisierung: automatisiert*

Für Schülerinnen und Schüler werden keine einwilligungsbedürftigen Cookies gesetzt; bei Lehrkräften ist eine Einwilligung möglich.

**Automatisiert prüfbar.** Die automatisierte Prüfung bewertet das Cookie-Inventar gegen die gewählte Zielgruppe. Die Zielgruppe steuert die Bewertung, deshalb muss --audience korrekt gesetzt sein.

**Grenzen der Automatik.** Ob eine vorhandene Einwilligung wirksam ist, bewertet die automatisierte Prüfung nicht.

**Benötigte Eingaben.** Produkt-URL und Quellcode-Pfad.

**Selbst prüfen**

- Zielgruppe des Angebots festlegen: SuS, Lehrkraefte oder beide. Bei beide gilt der strengere Maßstab für die Bereiche, die Schülerinnen und Schüler nutzen.
- Cookie-Inventar aus dem vorigen Schritt heranziehen und je Cookie prüfen, ob er einwilligungsbedürftig ist.
- Für Lehrkräftebereiche prüfen, ob eine Einwilligung eingeholt wird, bevor der Cookie gesetzt wird.
- Consent-Dialog prüfen: Ablehnen muss gleich einfach erreichbar sein wie Zustimmen, Vorauswahl auf ablehnen.
- Widerruf prüfen: Ist die Einstellung jederzeit erreichbar und wirksam?

**Stolperfallen**

- Consent-Dialog mit vorausgewählten Häkchen.
- Ablehnen nur über einen zweiten Dialog erreichbar.
- Kein Widerruf im Produkt vorgesehen.
- Gleiche Cookie-Konfiguration für Schüler- und Lehrkräftebereich.

**Behebung**

- Einwilligungsbedürftige Cookies in Schülerbereichen deaktivieren.
- Consent-Dialog gleichwertig gestalten und Widerruf dauerhaft anbieten.
- Cookie-Konfiguration je Zielgruppe trennen.

**Nachweise**

- Screenshots des Consent-Dialogs, erster Aufruf und Widerruf.
- Cookie-Inventar je Zielgruppe.

<details><summary>Kriteriumstext V0.2</summary>

Es werden keine Cookies gesetzt, für die eine Einwilligung erforderlich ist, sofern sich das Angebot an die Nutzergruppe der Schülerinnen und Schüler richtet.
Richtet sich das Angebot an Lehrkräfte, kann die Einwilligung eingeholt werden.

</details>

### RDS-CUC-373 — Trackingpixel

*MUSS-Kriterium, Bereich RDS, Automatisierung: automatisiert*

Für Schülerinnen und Schüler werden keine Trackingpixel verwendet.

**Automatisiert prüfbar.** Die automatisierte Prüfung beobachtet die Netzwerkanfragen der Seiten und erkennt bekannte Tracking- und Werbe-Endpunkte, Zählpixel und Pixelmuster in Requests und Markup.

**Grenzen der Automatik.** Selbst gehostete oder unbekannte Pixel-Endpunkte erkennt die automatisierte Prüfung nicht zuverlässig.

**Benötigte Eingaben.** Produkt-URL und Quellcode-Pfad.

**Selbst prüfen**

- Entwicklerwerkzeuge auf dem Netzwerk-Tab öffnen, Filter auf Bilder setzen und die Seite neu laden.
- Nach Anfragen mit sehr kleinen Bildantworten suchen und deren Zielhost prüfen.
- Im Markup nach img-Elementen mit 1 Pixel Größe oder mit Query-Parametern suchen.
- Nach bekannten Endpunkten suchen, etwa facebook.com/tr, Werbenetzwerke und Analyse-Endpunkte.
- Prüfen, ob Pixel über Tag-Manager nachgeladen werden, und die Tag-Manager-Konfiguration einsehen.
- Durchgang im angemeldeten Bereich wiederholen.

**Stolperfallen**

- Pixel über einen Tag-Manager eingebunden und deshalb im Code nicht sichtbar.
- Pixel nur auf Marketing-Landingpages, die aber vom Produkt verlinkt sind.
- Selbst gehostete Zählpixel, die als eigene Technik ausgeblendet werden.

**Behebung**

- Trackingpixel in allen von Schülerinnen und Schülern erreichbaren Bereichen entfernen.
- Tag-Manager-Container für Bildungsbereiche leeren oder nicht ausliefern.

**Nachweise**

- Netzwerk-Export aus der automatisierten Prüfung oder HAR-Datei.
- Screenshot der Tag-Manager-Konfiguration.

<details><summary>Kriteriumstext V0.2</summary>

Es werden keine Trackingpixel verwendet, wenn sich ein Angebot an Schülerinnen und Schüler richtet.
Richtet sich das Angebot an Lehrkräfte, wird dafür eine entsprechende Einwilligung eingeholt.

</details>

### RDS-CUC-374 — Local Browser Storage

*MUSS-Kriterium, Bereich RDS, Automatisierung: teilautomatisiert*

Im Local Storage oder Session Storage liegen keine einwilligungsbedürftigen Daten, wenn das Angebot an Schülerinnen und Schüler gerichtet ist.

**Automatisiert prüfbar.** Die automatisierte Prüfung liest Local Storage und Session Storage aus, listet alle Schlüssel und stuft sie ein. Keine oder nur erlaubte Schlüssel führen zu einer automatischen Bewertung, unbekannte Schlüssel bleiben prüfpflichtig.

**Grenzen der Automatik.** Der Zweck eines Schlüssels ist aus dem Namen nicht sicher ableitbar. Die Bewertung unbekannter Schlüssel bleibt beim Anbieter.

**Benötigte Eingaben.** Produkt-URL, Quellcode-Pfad sowie eine fachliche Bewertung.

**Selbst prüfen**

- Entwicklerwerkzeuge öffnen, Local Storage und Session Storage einsehen und alle Schlüssel notieren.
- Je Schlüssel Zweck, Inhalt und Notwendigkeit dokumentieren. Enthält er personenbezogene Daten?
- Prüfen, ob der Schlüssel für den Betrieb erforderlich ist, etwa Sitzung, Spracheinstellung, Formularzwischenstand.
- Prüfen, ob Analyse- oder Kennungswerte abgelegt werden, etwa dauerhafte Geräte- oder Nutzerkennungen.
- Durchgang im angemeldeten Bereich wiederholen.
- Sprechende Schlüsselnamen einführen, damit die Zuordnung nachvollziehbar bleibt.

**Stolperfallen**

- Analyse-Bibliothek legt eine dauerhafte Kennung im Local Storage ab, um Cookie-Regeln zu umgehen.
- Unklare Schlüsselnamen wie a1 oder tmp, deren Zweck niemand belegen kann.
- Personenbezogene Inhalte dauerhaft im Local Storage, obwohl Session Storage genügt.

**Behebung**

- Nicht erforderliche Schlüssel entfernen.
- Von Local Storage auf Session Storage wechseln, wo Persistenz nicht nötig ist.
- Schlüsselinventar mit Zweck und Notwendigkeit dokumentieren und im Produkt pflegen.

**Nachweise**

- Storage-Inventar aus dem Lauf, im Report als Klassifikationsliste enthalten.
- Zweckdokumentation je Schlüssel.

<details><summary>Kriteriumstext V0.2</summary>

Es werden keine Daten im Local Browser Storage oder Session Storage abgelegt, sofern dafür eine Einwilligung erforderlich ist und sich das Angebot an die Nutzergruppe der Schülerinnen und Schüler richtet.
Richtet sich das Angebot an Lehrkräfte, darf die Einwilligung eingeholt werden.
Dies schützt die Privatsphäre der Schülerinnen und Schüler und gewährleistet die Einhaltung datenschutzrechtlicher Anforderungen.

</details>

### RDS-CUC-375 — Informationen auf der Endeinrichtung des Endnutzers

*MUSS-Kriterium, Bereich RDS, Automatisierung: teilautomatisiert*

Auf dem Endgerät werden keine weiteren einwilligungsbedürftigen Informationen gespeichert oder ausgelesen.

**Automatisiert prüfbar.** Die automatisierte Prüfung sammelt Signale zu IndexedDB, Cache Storage und Service Workern. Die rechtliche Zweckbewertung bleibt manuell.

**Grenzen der Automatik.** Die automatisierte Prüfung erkennt die Nutzung dieser Speicher, nicht ihren Zweck. Deshalb bleibt das Kriterium bei vorhandenen Signalen prüfpflichtig.

**Benötigte Eingaben.** Produkt-URL, Quellcode-Pfad sowie eine fachliche Bewertung.

**Selbst prüfen**

- Entwicklerwerkzeuge öffnen und IndexedDB, Cache Storage und Service Worker einsehen.
- Je Datenbank oder Cache erfassen, welche Daten darin liegen und wozu.
- Prüfen, ob Offline-Funktion oder Performance die Speicherung wirklich erfordert.
- Prüfen, ob personenbezogene Inhalte offline verbleiben und wie sie gelöscht werden.
- Prüfen, ob Geräteinformationen ausgelesen werden, etwa Schriftarten, Sensoren, Media Devices.
- Prüfen, ob ein Service Worker auch nach Abmeldung weiterläuft und Daten behält.

**Stolperfallen**

- Service Worker bleibt nach Logout aktiv und hält Inhalte im Cache.
- IndexedDB mit Lerndaten ohne Löschmechanismus.
- Berechtigungsabfragen für Sensoren ohne Zweckbezug.

**Behebung**

- Speicher auf das für die Funktion Notwendige begrenzen.
- Löschung beim Logout implementieren, inklusive Service-Worker-Caches.
- Zweck je Speicher dokumentieren.

**Nachweise**

- Screenshots von IndexedDB, Cache Storage und Service Workern.
- Zweck- und Löschkonzept für Gerätespeicher.

<details><summary>Kriteriumstext V0.2</summary>

Es werden keine sonstigen Informationen auf der Endeinrichtung des Endnutzers gespeichert und es erfolgt kein Zugriff auf Informationen, die bereits in der Endeinrichtung gespeichert sind, sofern dafür eine Einwilligung erforderlich ist und sich das Angebot an die Nutzergruppe der Schülerinnen und Schüler richtet.
Richtet sich das Angebot an Lehrkräfte, darf die Einwilligung eingeholt werden.

</details>

### RDS-CUC-376 — Browserfingerprints

*MUSS-Kriterium, Bereich RDS, Automatisierung: teilautomatisiert*

Es werden keine Browserfingerprints gebildet, wenn sich das Angebot an Schülerinnen und Schüler richtet.

**Automatisiert prüfbar.** Die automatisierte Prüfung erkennt typische Fingerprinting-Signale im Code und im Laufzeitverhalten, etwa Canvas-, WebGL-, Font- und Audio-Abfragen sowie bekannte Fingerprinting-Bibliotheken.

**Grenzen der Automatik.** Ob eine erkannte Abfrage der Fingerprint-Bildung oder einer legitimen Funktion dient, bleibt eine Bewertung mit Produktkontext.

**Benötigte Eingaben.** Produkt-URL, Quellcode-Pfad sowie eine fachliche Bewertung.

**Selbst prüfen**

- Im Quellcode und in den ausgelieferten Bundles nach Fingerprinting-Bibliotheken suchen, etwa fingerprintjs.
- Nach Aufrufen suchen, die typischerweise zur Fingerprint-Bildung dienen: canvas toDataURL, WebGL-Parameter, AudioContext, Schriftartenlisten, enumerateDevices.
- Je Fund prüfen, ob eine Produktfunktion diese Abfrage erfordert, etwa Kameraauswahl in einer Videofunktion.
- Betrugserkennungs- oder Bot-Schutzdienste prüfen; sie bilden häufig Fingerprints.
- Prüfen, ob ein Gerätemerkmal serverseitig gespeichert und zur Wiedererkennung genutzt wird.

**Stolperfallen**

- Bot-Schutz oder Fraud-Detection bildet Fingerprints, wird aber nicht als Tracking betrachtet.
- Fingerprinting in einer Drittanbieter-Bibliothek versteckt.
- Geräteerkennung zur Sitzungsabsicherung ohne Dokumentation und Rechtsgrundlage.

**Behebung**

- Fingerprinting-Bibliotheken in Schülerbereichen entfernen.
- Bot-Schutz auf serverseitige Verfahren ohne Fingerprint umstellen.
- Für notwendige Gerätemerkmale Zweck, Umfang und Rechtsgrundlage dokumentieren.

**Nachweise**

- Code-Fundstellen aus code_capture.json.
- Bewertung je Fundstelle mit Produktbezug.

<details><summary>Kriteriumstext V0.2</summary>

Es werden keine Browserfingerprints gebildet, wenn sich ein Angebot an Schülerinnen und Schüler richtet.
Richtet sich das Angebot an Lehrkräfte, wird dafür eine entsprechende Einwilligung eingeholt

</details>

### RDS-CUC-377 — Trackingmechanismen zu nicht pädagogischen Zwecken

*MUSS-Kriterium, Bereich RDS, Automatisierung: teilautomatisiert*

Für Schülerinnen und Schüler wird nicht getrackt, außer das Tracking dient pädagogischen Zwecken, etwa in adaptiven Lernsystemen.

**Automatisiert prüfbar.** Die automatisierte Prüfung fasst Tracking-Signale aus Browser, Code und Dokumenten zusammen. PASS oder FAIL entstehen nur, wenn entweder kein Tracker vorhanden ist, ein bekanntes nicht pädagogisches Tracking erkannt wird oder der pädagogische Zweck durch übergebene Dokumente belegt ist.

**Grenzen der Automatik.** Der pädagogische Zweck ist aus Browsersignalen nicht ableitbar. Ohne Produktkontext bleibt das Kriterium prüfpflichtig.

**Benötigte Eingaben.** Produkt-URL sowie Produktkontext als Dokument oder AGB-, Datenschutz- und AVV-URL; bleibt der Zweck unklar, ist eine fachliche Bewertung nötig.

**Selbst prüfen**

- Alle Tracking- und Analysemechanismen des Produkts auflisten, auch selbst gebaute Telemetrie.
- Je Mechanismus den Zweck bestimmen: pädagogische Auswertung im Lernprozess oder Produkt-, Marketing- oder Reichweitenanalyse?
- Für pädagogisches Tracking dokumentieren, welche Lernfunktion darauf beruht und wer die Daten sieht.
- Prüfen, ob die Datenmenge auf die pädagogische Funktion begrenzt ist.
- Prüfen, ob nicht pädagogische Telemetrie deaktiviert oder anonymisiert ist.
- Die Zweckdokumentation der automatisierten Prüfung als Dokument übergeben, damit die Bewertung nicht prüfpflichtig bleibt.

**Stolperfallen**

- Produktanalyse als pädagogisches Tracking bezeichnet.
- Pädagogisches Tracking erhebt mehr Daten als die Lernfunktion benötigt.
- Fehlerprotokolle mit vollständigen Nutzungsprofilen.

**Behebung**

- Tracking auf pädagogisch begründete Datenpunkte reduzieren.
- Produkt-Telemetrie anonymisieren oder abschalten.
- Zweckdokumentation erstellen und mit der Datenschutzerklärung abgleichen.

**Nachweise**

- Zweckdokumentation je Tracking-Mechanismus.
- Datenfeldliste des pädagogischen Trackings.

<details><summary>Kriteriumstext V0.2</summary>

Es werden keine Trackingmechanismen eingesetzt, wenn sich ein Angebot an Schülerinnen und Schüler richtet, es sei denn, das Nutzerverhalten wird aus pädagogischen Gründen getrackt, wie z. B. bei adaptiven Lernsystemen notwendig.
Richtet sich das Angebot an Lehrkräfte, wird dafür eine entsprechende Einwilligung eingeholt.

</details>

## 4. Impressum, Datenschutzerklärung, Cookie-Beschreibung

Hier geht es um Auffindbarkeit und Vollständigkeit der Pflichttexte. Automatisiert prüfbar ist, ob die Pflichtangaben im Text vorkommen. Ob sie inhaltlich zutreffen und zur tatsächlichen Verarbeitung passen, entscheidet eine fachlich verantwortliche Person.

### RDS-CUC-453 — Beschreibung aller Cookies

*MUSS-Kriterium, Bereich RDS, Automatisierung: teilautomatisiert*

Alle Cookies des Angebots und ihre Zwecke sind in der Datenschutzerklärung beschrieben.

**Automatisiert prüfbar.** Die automatisierte Prüfung gleicht das erhobene Cookie-Inventar mit den Cookie-Beschreibungen in der übergebenen Datenschutzerklärung ab. Fehlt der Text oder ist er unklar, bleibt das Kriterium prüfpflichtig.

**Grenzen der Automatik.** Ob eine Beschreibung inhaltlich zutrifft, bewertet die automatisierte Prüfung nicht.

**Benötigte Eingaben.** Produkt-URL, AGB, Datenschutzerklärung und AVV als Datei oder URL sowie eine fachliche Bewertung.

**Selbst prüfen**

- Cookie-Inventar aus dem technischen Durchgang heranziehen, inklusive Local Storage und Session Storage.
- Datenschutzerklärung öffnen und je Eintrag prüfen, ob er dort genannt ist.
- Je Eintrag prüfen, ob Zweck, Anbieter, Speicherdauer und Einstufung als erforderlich oder einwilligungsbedürftig angegeben sind.
- Prüfen, ob die Erklärung auch die Cookies des angemeldeten Bereichs abdeckt.
- Prüfen, ob die Liste aktuell ist; ein Deployment kann neue Cookies eingeführt haben.
- Datenschutzerklärung als Dokument oder URL in den Lauf geben, damit der Abgleich automatisch erfolgt.

**Stolperfallen**

- Cookie-Tabelle veraltet, weil sie nicht Teil des Release-Prozesses ist.
- Cookies von Drittanbietern nur pauschal als externe Dienste erwähnt.
- Local Storage und Session Storage fehlen in der Beschreibung.

**Behebung**

- Cookie-Tabelle in der Datenschutzerklärung vervollständigen, inklusive Browser-Speicher.
- Aktualisierung der Tabelle in die Release-Checkliste aufnehmen.

**Nachweise**

- Gegenüberstellung Cookie-Inventar zu Cookie-Tabelle.
- Datum der letzten Aktualisierung der Tabelle.

<details><summary>Kriteriumstext V0.2</summary>

Bei der Nutzung von Web-Browsern, als auch bei der Nutzung von Mobile Apps (Webansichten, integrierte Browserumgebungen) können sog. "Cookies" genutzt werden.
Der Anbieter beschreibt alle "Cookies" seines Angebots und deren Zwecke in der Datenschutzerklärung

</details>

### RDS-DSO-383 — Benennung eines Datenschutzbeauftragten

*MUSS-Kriterium, Bereich RDS, Automatisierung: automatisiert*

Die Kontaktdaten des Datenschutzbeauftragten sind bereitgestellt, oder es ist ein DSB zu benennen.

**Automatisiert prüfbar.** Die automatisierte Prüfung sucht in der Datenschutzerklärung nach Kontaktdaten eines Datenschutzbeauftragten und erkennt auch die ausdrückliche Erklärung, dass kein DSB bestellt ist.

**Grenzen der Automatik.** Ob eine Bestellpflicht besteht, ist eine rechtliche Bewertung, die die automatisierte Prüfung nicht trifft.

**Benötigte Eingaben.** AGB, Datenschutzerklärung und AVV als Datei oder URL.

**Selbst prüfen**

- Datenschutzerklärung öffnen und prüfen, ob Name oder Funktion und ein eigener Kontaktweg des DSB genannt sind.
- Prüfen, ob der Kontaktweg ein direkter ist, etwa datenschutz@ oder eine Postadresse mit Zusatz, und nicht nur die allgemeine Info-Adresse.
- Falls kein DSB bestellt ist: prüfen, ob die Bestellpflicht nach Artikel 37 DSGVO und Paragraf 38 BDSG geprüft und die Prüfung dokumentiert wurde.
- Prüfen, ob die Angaben aktuell sind, insbesondere nach Wechsel eines externen DSB.

**Stolperfallen**

- Nur die allgemeine Unternehmensadresse als DSB-Kontakt.
- Veralteter externer DSB weiterhin genannt.
- Bestellpflicht nie geprüft und nicht dokumentiert.

**Behebung**

- DSB bestellen, sofern erforderlich, und Kontaktdaten in die Datenschutzerklärung aufnehmen.
- Eigenen Kontaktkanal für Datenschutzanfragen einrichten.
- Prüfung der Bestellpflicht schriftlich festhalten.

**Nachweise**

- Abschnitt der Datenschutzerklärung mit DSB-Kontaktdaten.
- Bestellurkunde oder dokumentierte Prüfung der Bestellpflicht.

<details><summary>Kriteriumstext V0.2</summary>

Der Anbieter stellt die Kontaktdaten des Datenschutzbeauftragten bereit.
Falls noch kein Datenschutzbeauftragter existiert, benennt der Anbieter den DSB.

</details>

### RDS-IPF-364 — Leicht auffindbares Impressum

*MUSS-Kriterium, Bereich RDS, Automatisierung: automatisiert*

Das Impressum ist von jeder Seite des Angebots aus mit einem Klick erreichbar.

**Automatisiert prüfbar.** Die automatisierte Prüfung crawlt die Startseite und weitere Seiten, sucht Links mit Beschriftungen wie Impressum, Imprint oder Anbieterkennzeichnung und prüft, ob die Zielseite mit HTTP 2xx/3xx antwortet.

**Grenzen der Automatik.** Die automatisierte Prüfung sieht nur den unangemeldeten Seitenstand. Bereiche hinter Login, in Apps oder in eingebetteten Webviews prüft er nur mit --agentic.

**Benötigte Eingaben.** Produkt-URL und Quellcode-Pfad.

**Selbst prüfen**

- Startseite im Browser öffnen und ganz nach unten scrollen. Ist ein Link mit der Bezeichnung Impressum sichtbar?
- Denselben Test auf mindestens drei weiteren Seitentypen wiederholen: einer Inhaltsseite, einer Formular- oder Login-Seite und einer Seite im angemeldeten Bereich.
- Browserfenster auf Mobilbreite verkleinern (etwa 375 Pixel). Der Link muss auch dort erreichbar bleiben, auch wenn er in einem Menü liegt.
- Den Link anklicken und prüfen, ob die Impressumsseite ohne Zwischenschritt, ohne Login und ohne Cookie-Zustimmung lädt.
- In der App oder im Webview denselben Weg gehen: Impressum muss dort ebenfalls in maximal zwei Schritten erreichbar sein.

**Stolperfallen**

- Impressum nur auf der Startseite verlinkt, nicht im angemeldeten Bereich.
- Link nur im Desktop-Footer, im mobilen Layout ausgeblendet.
- Impressum erst nach Zustimmung zum Cookie-Banner erreichbar.
- Beschriftung wie Über uns oder Kontakt ohne das Wort Impressum, dadurch nicht leicht erkennbar.

**Behebung**

- Impressumslink in das globale Layout aufnehmen, nicht in eine einzelne Seitenvorlage.
- Link im mobilen Layout sichtbar halten oder in ein dauerhaft erreichbares Menü legen.
- Beschriftung auf Impressum setzen; zusätzliche Bezeichnungen dürfen ergänzen, nicht ersetzen.
- Impressumsseite vom Cookie-Consent und vom Login ausnehmen.

**Nachweise**

- URL der Impressumsseite.
- Screenshots des Links in Desktop- und Mobilansicht sowie im angemeldeten Bereich.

<details><summary>Kriteriumstext V0.2</summary>

Ein stets verfügbares und leicht erkennbares Impressum ist von allen Seiten erreichbar.
Dies gilt insbesondere bei Angeboten mit responsiven Designs

</details>

### RDS-IPF-365 — Leicht auffindbare Datenschutzerklärung

*MUSS-Kriterium, Bereich RDS, Automatisierung: automatisiert*

Die Datenschutzerklärung ist von jeder Seite des Angebots aus mit einem Klick erreichbar.

**Automatisiert prüfbar.** Die automatisierte Prüfung sucht Links mit Beschriftungen wie Datenschutzerklärung, Datenschutz oder Privacy Policy und prüft die Erreichbarkeit der Zielseite.

**Grenzen der Automatik.** Wie beim Impressum sieht die automatisierte Prüfung ohne --agentic nur öffentliche Seiten.

**Benötigte Eingaben.** Produkt-URL und Quellcode-Pfad.

**Selbst prüfen**

- Startseite öffnen und prüfen, ob ein Link mit der Bezeichnung Datenschutzerklärung oder Datenschutz sichtbar ist.
- Denselben Test in Registrierung, Login, Formularen und im angemeldeten Bereich wiederholen. Genau dort wird die Erklärung gebraucht.
- Mobilansicht prüfen, wie beim Impressum.
- Prüfen, dass die Erklärung ohne Login und ohne Cookie-Zustimmung lädt.
- Prüfen, ob die verlinkte Fassung aktuell ist und zum tatsächlich genutzten Produkt gehört, nicht zur Konzern-Webseite.

**Stolperfallen**

- Nur die Konzern-Datenschutzerklärung verlinkt, nicht die des Produkts.
- Datenschutzerklärung ausschließlich als PDF-Download hinterlegt.
- Im Registrierungsformular kein Link, obwohl dort Daten erhoben werden.

**Behebung**

- Produktspezifische Datenschutzerklärung als HTML-Seite bereitstellen und global verlinken.
- Link zusätzlich direkt an jedem Erhebungsformular platzieren.

**Nachweise**

- URL der Datenschutzerklärung.
- Screenshots des Links an Startseite, Registrierung und angemeldetem Bereich.

<details><summary>Kriteriumstext V0.2</summary>

Eine stets verfügbare und leicht erkennbare Datenschutzerklärung ist von allen Seiten erreichbar.
Dies gilt insbesondere bei Angeboten mit responsiven Designs.

</details>

### RDS-IPF-366 — Vollständiges Impressum

*MUSS-Kriterium, Bereich RDS, Automatisierung: automatisiert*

Das Impressum enthält alle Pflichtangaben nach den Paragrafen 5 und 6 DDG.

**Automatisiert prüfbar.** Die automatisierte Prüfung liest den Text der Impressumsseite und prüft Signale für Name und Anschrift, Rechtsform und Vertretung, Kontaktweg, Registereintrag, Umsatzsteuer- oder Wirtschafts-Identifikationsnummer sowie den aktuellen Rechtsverweis auf das DDG statt auf das TMG. Fehlende Punkte listet der Report namentlich auf.

**Grenzen der Automatik.** Die automatisierte Prüfung prüft das Vorhandensein von Textmerkmalen, nicht deren inhaltliche Richtigkeit. Ob die genannte Vertretung tatsächlich vertretungsberechtigt ist, kann er nicht bewerten.

**Benötigte Eingaben.** Produkt-URL.

**Selbst prüfen**

- Impressum öffnen und die Pflichtangaben einzeln abgleichen: vollständiger Name des Anbieters, Rechtsform, Ladungsfähige Anschrift mit Straße und Hausnummer, Vertretungsberechtigte Person.
- Kontaktweg prüfen: E-Mail-Adresse und ein zweiter schneller Kontaktweg, üblicherweise Telefonnummer oder Kontaktformular.
- Registereintrag prüfen: Registergericht und Registernummer, sofern das Unternehmen eingetragen ist.
- Umsatzsteuer-Identifikationsnummer oder Wirtschafts-Identifikationsnummer prüfen, sofern vorhanden.
- Rechtsverweise prüfen: Verweise müssen auf das DDG lauten. Verweise auf das TMG sind veraltet.
- Sonderfälle prüfen: Bei zulassungspflichtiger Tätigkeit die Aufsichtsbehörde nennen, bei audiovisuellen Mediendiensten Sitzland und zuständige Landesmedienanstalt.

**Stolperfallen**

- Postfach statt ladungsfähiger Anschrift.
- Verweis auf Paragraf 5 TMG, obwohl das DDG gilt.
- Nur ein Kontaktformular ohne E-Mail-Adresse.
- Registernummer fehlt, obwohl die Gesellschaft eingetragen ist.

**Behebung**

- Fehlende Pflichtangaben laut Report ergänzen; der Report nennt die fehlenden Punkte einzeln.
- Rechtsverweise auf DDG umstellen.
- Angaben mit dem aktuellen Handelsregisterauszug abgleichen.

**Nachweise**

- Impressumstext als PDF oder HTML-Export mit Datum.
- Handelsregisterauszug zur Prüfung der Angaben, intern.

<details><summary>Kriteriumstext V0.2</summary>

Das Impressum enthält alle nach § § 5 und 6 DDG vorgeschriebenen Informationen.

</details>

### RDS-IPF-367 — Vollständige Datenschutzerklärung

*MUSS-Kriterium, Bereich RDS, Automatisierung: automatisiert*

Die Datenschutzerklärung enthält alle Pflichtinformationen nach Artikel 13 und 14 DSGVO.

**Automatisiert prüfbar.** Die automatisierte Prüfung prüft die Datenschutzerklärung auf Signale für Verantwortlichen, Datenschutzbeauftragten, Verarbeitungszwecke, Rechtsgrundlagen, Empfänger, Speicherdauer, Betroffenenrechte inklusive Beschwerde und Widerruf, Folgen der Nichtbereitstellung sowie automatisierte Entscheidungsfindung und Profiling.

**Grenzen der Automatik.** Die automatisierte Prüfung erkennt, ob die Themen adressiert sind, nicht ob die Angaben rechtlich zutreffend, vollständig und zur tatsächlichen Verarbeitung passend sind. Diese Bewertung bleibt bei einer qualifizierten Person.

**Benötigte Eingaben.** Produkt-URL.

**Selbst prüfen**

- Datenschutzerklärung öffnen und Artikel 13 DSGVO Punkt für Punkt abgleichen.
- Verantwortlicher: Name, Anschrift und Kontaktdaten vorhanden?
- Datenschutzbeauftragter: Kontaktdaten vorhanden oder begründet, dass keiner bestellt werden muss?
- Zwecke und Rechtsgrundlagen: Ist jede Verarbeitung einem Zweck und einer Rechtsgrundlage nach Artikel 6 DSGVO zugeordnet?
- Empfänger: Sind Auftragsverarbeiter und weitere Empfänger benannt, mindestens nach Kategorien?
- Drittlandtransfer: Ist er benannt und mit Garantien nach Artikel 44 ff. DSGVO belegt?
- Speicherdauer: Sind konkrete Fristen oder nachvollziehbare Kriterien angegeben?
- Betroffenenrechte: Auskunft, Berichtigung, Löschung, Einschränkung, Datenübertragbarkeit, Widerspruch, Widerruf der Einwilligung und Beschwerderecht bei einer Aufsichtsbehörde.
- Automatisierte Entscheidungsfindung und Profiling: Ist eine Aussage getroffen, auch wenn sie lautet, dass beides nicht stattfindet?
- Abschließend gegen die eigene Realität prüfen: Steht jede tatsächlich eingesetzte Verarbeitung, jedes Tool und jeder Dienstleister in der Erklärung?

**Stolperfallen**

- Keine Aussage zu automatisierter Entscheidungsfindung, weil das Thema als nicht relevant übersprungen wurde.
- Speicherdauer nur als soweit erforderlich formuliert, ohne Kriterien.
- Verarbeitungen im Produkt, die in der Erklärung fehlen, etwa Analyse-Tools oder Support-Systeme.
- Erklärung nennt Dienstleister, die längst ausgetauscht wurden.

**Behebung**

- Verarbeitungsverzeichnis und Datenschutzerklärung gegeneinander abgleichen und Lücken schließen.
- Fehlende Pflichtinformationen laut Report ergänzen.
- Erklärung mit Datenschutzbeauftragtem oder Fachjuristin abstimmen und mit Datum versionieren.

**Nachweise**

- Datenschutzerklärung als Export mit Datum und Version.
- Zuordnungstabelle Artikel-13-Pflichtangabe zu Textabschnitt.

<details><summary>Kriteriumstext V0.2</summary>

Die Datenschutzerklärung enthält alle Informationen, die nach Art. 13 und 14 DSGVO vorgeschrieben sind.

</details>

## 5. Verträge, Dienstleister, Datenflüsse

Diese Kriterien sind nicht am Produkt sichtbar, sondern in Verträgen, Verarbeitungsverzeichnis und Subunternehmerliste. Sie sind der häufigste Grund für Rückfragen in Prüfungen, weil Unterlagen fehlen oder veraltet sind.

### RDS-AGB-368 — Nutzungsbedingungen/AGB: Datenschutzkonform

*MUSS-Kriterium, Bereich RDS, Automatisierung: automatisiert*

Die AGB oder Nutzungsbedingungen enthalten keine Klauseln, die gegen Datenschutzgrundsätze verstoßen.

**Automatisiert prüfbar.** Die automatisierte Prüfung analysiert übergebene AGB-Dokumente oder die AGB-URL auf Textmuster, die auf datenschutzwidrige Klauseln hindeuten, und legt Belegstellen in document_capture.json ab.

**Grenzen der Automatik.** Klauselbewertung ist eine juristische Wertung. Die automatisierte Prüfung liefert Fundstellen und Hinweise, keine Rechtsprüfung. Ohne AGB-Eingabe bleibt das Kriterium MANUELL.

**Benötigte Eingaben.** AGB, Datenschutzerklärung und AVV als Datei oder URL.

**Selbst prüfen**

- AGB oder Nutzungsbedingungen als Dokument oder URL bereitstellen und in den Lauf geben.
- Klauseln zur Datennutzung suchen und prüfen, ob eine Nutzung über die Leistungserbringung hinaus eingeräumt wird, etwa zu Werbe-, Analyse- oder Trainingszwecken.
- Prüfen, ob Einwilligungen über AGB-Zustimmung mitverpackt werden. Einwilligung muss getrennt, freiwillig und widerrufbar sein.
- Prüfen, ob Nutzungsrechte an Inhalten von Schülerinnen und Schülern eingeräumt werden, die über den Betrieb hinausgehen.
- Prüfen, ob Haftungs- und Änderungsklauseln datenschutzrelevante Pflichten aushöhlen, etwa einseitige Änderung der Datenverarbeitung.
- Prüfen, ob die AGB zur Datenschutzerklärung widerspruchsfrei sind.

**Stolperfallen**

- Pauschale Einwilligung in Datenverarbeitung als Teil der AGB-Zustimmung.
- Recht zur Nutzung von Nutzerinhalten für Produktverbesserung oder KI-Training ohne Rechtsgrundlage.
- AGB in englischer Fassung maßgeblich, deutsche Fassung nur informativ.
- Widersprüche zwischen AGB und Datenschutzerklärung zur Datennutzung.

**Behebung**

- Datenschutzrelevante Klauseln aus den AGB herauslösen und in die Datenschutzerklärung bzw. den AVV überführen.
- Einwilligungen als eigenen, getrennten Vorgang gestalten.
- AGB juristisch gegen die Datenschutzgrundsätze prüfen lassen und Ergebnis dokumentieren.

**Nachweise**

- AGB-Fassung mit Datum und Version.
- Kurze Klauselbewertung mit Verantwortlicher Person und Datum.

<details><summary>Kriteriumstext V0.2</summary>

Die Nutzungsbedingungen oder AGB des Angebots enthalten keine Klauseln, die gegen die Grundsätze des Datenschutzes verstoßen.

</details>

### RDS-AGB-369 — Nutzungsbedingungen/AGB: AVV-konform

*MUSS-Kriterium, Bereich RDS, Automatisierung: automatisiert*

Die AGB enthalten keine Klauseln, die den Vorschriften zur Auftragsverarbeitung widersprechen.

**Automatisiert prüfbar.** Die automatisierte Prüfung analysiert AGB und AVV auf Muster zu Weisungsbindung, Subunternehmern, Löschung und Kontrollrechten und legt Belegstellen ab.

**Grenzen der Automatik.** Ob die Klauseln Artikel 28 DSGVO tatsächlich genügen, ist eine juristische Wertung.

**Benötigte Eingaben.** AGB, Datenschutzerklärung und AVV als Datei oder URL.

**Selbst prüfen**

- AVV oder die auftragsverarbeitungsrelevanten AGB-Teile bereitstellen und in den Lauf geben.
- Gegen Artikel 28 Absatz 3 DSGVO abgleichen: Gegenstand und Dauer, Art und Zweck, Art der Daten, Kategorien betroffener Personen.
- Weisungsbindung prüfen: Verarbeitung nur auf dokumentierte Weisung des Auftraggebers.
- Vertraulichkeit und Verpflichtung der eingesetzten Personen prüfen.
- Technische und organisatorische Maßnahmen prüfen: sind sie beschrieben und anlagenfähig?
- Subunternehmer prüfen: Genehmigungspflicht, Liste, Informationspflicht bei Wechsel, Weitergabe derselben Pflichten.
- Unterstützungspflichten prüfen: Betroffenenrechte, Meldung von Datenschutzverletzungen, Datenschutz-Folgenabschätzung.
- Kontrollrechte prüfen: Auditrechte des Auftraggebers, Nachweise, Zertifikate.
- Beendigung prüfen: Löschung oder Rückgabe nach Wahl des Auftraggebers.

**Stolperfallen**

- Anbieter behält sich vor, Subunternehmer ohne Information zu wechseln.
- Auditrechte auf Selbstauskunft des Anbieters reduziert.
- Kein AVV vorhanden, weil die Rolle fälschlich als eigene Verantwortlichkeit eingeordnet wird.
- AVV verweist auf Anlagen, die nicht mitgeliefert werden.

**Behebung**

- AVV nach Artikel 28 DSGVO vervollständigen, inklusive TOM-Anlage und Subunternehmerliste.
- Widersprüche zwischen AGB und AVV auflösen, Vorrangregel für den AVV aufnehmen.

**Nachweise**

- AVV-Fassung mit Anlagen.
- Aktuelle Subunternehmerliste mit Verarbeitungsort.

<details><summary>Kriteriumstext V0.2</summary>

Die Nutzungsbedingungen oder AGB des Angebots enthalten keine Klauseln, die gegen die Vorschriften zur Auftragsverarbeitung verstoßen.

</details>

### RDS-DEV-380 — Datenerhebung und -verarbeitung

*MUSS-Kriterium, Bereich RDS, Automatisierung: automatisiert*

Daten werden nur für die Nutzung des Angebots verarbeitet, Werbezwecke sind ausgeschlossen.

**Automatisiert prüfbar.** Die automatisierte Prüfung prüft Dokumente auf Zweckbindungs- und Werbeaussagen und ergänzend den Quellcode auf Werbe- und Tracking-Integrationen.

**Grenzen der Automatik.** Die tatsächliche Zweckbindung im Betrieb ist aus Text und Code allein nicht vollständig belegbar.

**Benötigte Eingaben.** Quellcode-Pfad sowie AGB, Datenschutzerklärung und AVV als Datei oder URL.

**Selbst prüfen**

- Verarbeitungsverzeichnis öffnen und je Verarbeitung den Zweck prüfen. Gibt es einen Zweck außerhalb der Leistungserbringung?
- Datenschutzerklärung und AGB prüfen: Wird Werbung, Profilbildung oder Weitergabe zu Werbezwecken erwähnt oder eingeräumt?
- Eingesetzte Dienste prüfen: Analyse, A/B-Tests, Marketing-Automation, CRM-Anbindung, Newsletter, Push-Kampagnen.
- Prüfen, ob Produktdaten von Schülerinnen und Schülern in Systeme fließen, die auch für Marketing genutzt werden.
- Prüfen, ob Nutzerdaten für Modelltraining verwendet werden und auf welcher Rechtsgrundlage.

**Stolperfallen**

- Marketing-Tool im Produkt aktiv, obwohl die Erklärung Werbefreiheit zusagt.
- Gemeinsame Datenbank für Schulprodukt und Marketing ohne Trennung.
- Produktverbesserung als Sammelzweck ohne Abgrenzung zu Werbung.

**Behebung**

- Werbe- und Marketing-Integrationen aus dem Bildungsangebot entfernen.
- Zwecke im Verarbeitungsverzeichnis eng und einzeln formulieren.
- Datenflüsse zwischen Produkt und Marketing-Systemen technisch trennen.

**Nachweise**

- Auszug Verarbeitungsverzeichnis mit Zwecken.
- Liste eingesetzter Dienste und Integrationen.

<details><summary>Kriteriumstext V0.2</summary>

Daten werden ausschließlich für die Nutzung des Angebots verarbeitet.
Insbesondere eine Nutzung zu Werbezwecken ist ausgeschlossen.

</details>

### RDS-DEV-381 — Umgang mit Daten nach Beendigung der Zusammenarbeit

*MUSS-Kriterium, Bereich RDS, Automatisierung: automatisiert*

Nach Vertragsende werden die Daten des Auftraggebers nach dessen Wahl gelöscht und auf Wunsch herausgegeben.

**Automatisiert prüfbar.** Die automatisierte Prüfung prüft AVV und AGB auf Regelungen zu Löschung, Rückgabe und Fristen nach Vertragsende.

**Grenzen der Automatik.** Ob der Prozess in der Praxis funktioniert, zeigt nur ein durchgeführter Test oder ein dokumentierter Prozess.

**Benötigte Eingaben.** AGB, Datenschutzerklärung und AVV als Datei oder URL.

**Selbst prüfen**

- AVV-Abschnitt zur Beendigung öffnen: Ist Löschung und Herausgabe nach Wahl des Auftraggebers geregelt?
- Prüfen, ob eine Frist genannt ist und ob sie realistisch ist.
- Prüfen, in welchem Format Daten herausgegeben werden und ob das Format nutzbar ist.
- Backups prüfen: Wann fallen Daten aus Backups heraus, und ist das dokumentiert?
- Prüfen, ob es einen dokumentierten, geübten Prozess gibt, nicht nur eine Klausel.
- Prüfen, ob Protokoll- und Log-Daten mit erfasst sind.

**Stolperfallen**

- Löschung zugesagt, aber Backups laufen 12 Monate weiter, ohne dass das benannt ist.
- Export nur als PDF, wodurch die Daten praktisch nicht weiterverwendbar sind.
- Kein Löschnachweis vorgesehen.

**Behebung**

- Beendigungsprozess dokumentieren, inklusive Backup-Fristen und Löschprotokoll.
- Maschinenlesbaren Export bereitstellen.
- Löschnachweis als Standardartefakt einführen.

**Nachweise**

- AVV-Abschnitt zur Beendigung.
- Prozessdokumentation Löschung und Herausgabe, inklusive Beispiel-Löschnachweis.

<details><summary>Kriteriumstext V0.2</summary>

Nach Beendigung der Zusammenarbeit mit dem Auftraggeber werden die Daten des Auftraggebers (also beispielsweise die Daten sämtlicher Schülerinnen und Schüler sowie Lehrkräfte einer Schule, mit der ein Vertrag zur Auftragsverarbeitung geschlossen wurde) nach Wahl des Auftraggebers gelöscht und, wenn gewünscht, an diesen herausgegeben.

</details>

### RDS-DEV-466 — Sichere Datenverarbeitung

*MUSS-Kriterium, Bereich RDS, Automatisierung: automatisiert*

Es werden keine Server oder Verarbeitungen in unsicheren Drittländern eingesetzt, auch nicht bei Sub- oder Mutterunternehmen.

**Automatisiert prüfbar.** Die automatisierte Prüfung prüft Dokumente auf Aussagen zu Verarbeitungsorten, Drittlandtransfers und Garantien.

**Grenzen der Automatik.** Die tatsächliche Infrastruktur- und Konzernstruktur ist nur aus internen Unterlagen belastbar zu belegen.

**Benötigte Eingaben.** AGB, Datenschutzerklärung und AVV als Datei oder URL.

**Selbst prüfen**

- Liste aller Verarbeitungsorte erstellen: eigene Rechenzentren, Cloud-Regionen, Backup-Standorte.
- Liste aller Subunternehmer erstellen, inklusive Support, Monitoring, Mail-Versand, CDN und KI-Diensten.
- Je Eintrag das Land der Verarbeitung und das Land des Mutterunternehmens erfassen.
- Prüfen, ob Fernzugriff aus Drittländern möglich ist, etwa durch Support-Teams oder Administratoren.
- Für jeden verbleibenden Drittlandbezug die Garantien nach Artikel 44 ff. DSGVO dokumentieren.
- Prüfen, ob eine Transfer Impact Assessment vorliegt, wo sie erforderlich ist.

**Stolperfallen**

- EU-Region gewählt, Support greift aber aus einem Drittland zu.
- CDN oder Fehler-Monitoring als technische Nebensache übersehen.
- Mutterunternehmen im Drittland mit Zugriffsmöglichkeit nicht betrachtet.

**Behebung**

- Verarbeitungen in EU/EWR verlagern oder Zugriffe technisch und organisatorisch auf EU/EWR begrenzen.
- Subunternehmerliste mit Verarbeitungsort führen und aktuell halten.
- Für unvermeidbare Transfers Garantien und Zusatzmaßnahmen dokumentieren.

**Nachweise**

- Subunternehmerliste mit Verarbeitungsort und Mutterunternehmen.
- Architektur- oder Hostingnachweis mit Regionen.

<details><summary>Kriteriumstext V0.2</summary>

Es werden keine Server in unsicheren Drittländern eingesetzt und/oder Datenverarbeitungen in unsicheren Drittländern durchgeführt.
Dies gilt auch für Sub- oder Mutterunternehmen.

</details>

## 6. Inhalte, Werbung, Jugendmedienschutz

Inhaltliche Kriterien brauchen den Blick aus der Nutzerperspektive. Sie werden getrennt für Schülerinnen und Schüler sowie für Lehrkräfte durchlaufen, weil sich Sichtbarkeit und Zulässigkeit unterscheiden.

### RDS-SPE-370 — Sponsoring

*MUSS-Kriterium, Bereich RDS, Automatisierung: automatisiert*

Sponsoring, Produktplatzierungen und wirtschaftliche Interessen sind transparent gekennzeichnet.

**Automatisiert prüfbar.** Die automatisierte Prüfung klassifiziert Dokumente auf Sponsoring-Hinweise und wertet Kennzeichnungsbegriffe im Seiteninhalt aus. Ohne belastbare Hinweise bleibt das Kriterium prüfpflichtig.

**Grenzen der Automatik.** Ob eine Platzierung als Sponsoring einzuordnen ist, ist eine inhaltliche Bewertung.

**Benötigte Eingaben.** AGB, Datenschutzerklärung und AVV als Datei oder URL.

**Selbst prüfen**

- Alle wirtschaftlichen Beziehungen auflisten, die im Angebot sichtbar werden: Sponsoren, Partner, Förderer, Lizenzgeber.
- Je Beziehung prüfen, wo sie im Produkt sichtbar wird und wie sie gekennzeichnet ist.
- Prüfen, ob Logos oder Nennungen mit Verlinkung als Werbung wirken können.
- Prüfen, ob gesponserte Inhalte redaktionell von neutralen Inhalten unterscheidbar sind.
- Prüfen, ob die Kennzeichnung für Schülerinnen und Schüler verständlich ist.

**Stolperfallen**

- Sponsorenlogo auf Lerninhaltsseiten ohne Kennzeichnung.
- Gefördert von im Footer, während Sponsoren im Inhalt wiederholt auftauchen.
- Verlinkte Partnerlogos, die zu Produktseiten führen.

**Behebung**

- Sponsoring eindeutig kennzeichnen und von Lerninhalten trennen.
- Verlinkungen aus Schülerbereichen entfernen.
- Sponsoring-Konzept dokumentieren und dem Prüfbericht beilegen.

**Nachweise**

- Liste der Sponsoring- und Partnerbeziehungen.
- Screenshots der Kennzeichnung im Produkt.

<details><summary>Kriteriumstext V0.2</summary>

Sponsoring, Produktplatzierungen und sonstige wirtschaftliche Interessen sind transparent zu kennzeichnen; fehlen belastbare Dokumenthinweise, ist eine manuelle Prüfung erforderlich.

</details>

### RDS-VIN-354 — Jugendmedienschutz

*MUSS-Kriterium, Bereich RDS, Automatisierung: automatisiert*

Das Angebot ist jugendmedienschutzrechtlich unbedenklich.

**Automatisiert prüfbar.** Die automatisierte Prüfung prüft Seiteninhalte auf Altersgrenzen-Hinweise, jugendschutzrelevante Begriffe und Einbettungen von Plattformen mit ungefiltertem Fremdinhalt.

**Grenzen der Automatik.** Eine jugendmedienschutzrechtliche Bewertung von Inhalten ist eine fachliche Einschätzung; Text- und Linksignale sind nur Anhaltspunkte.

**Benötigte Eingaben.** Produkt-URL.

**Selbst prüfen**

- Alle Inhaltsquellen auflisten: eigene Inhalte, Inhalte Dritter, nutzergenerierte Inhalte, eingebettete Plattformen.
- Prüfen, ob nutzergenerierte Inhalte moderiert werden und wie.
- Eingebettete Plattformen prüfen: führt eine Einbettung zu Empfehlungen mit Fremdinhalt?
- Externe Links aus Schülerbereichen stichprobenartig aufrufen und Zielinhalte bewerten.
- Prüfen, ob Kommunikationsfunktionen Kontaktrisiken erzeugen und wie sie abgesichert sind.
- Prüfen, ob ein Melde- und Beschwerdeweg vorhanden und erreichbar ist.
- Prüfen, ob Alterskennzeichnung und Zielgruppenzuschnitt zusammenpassen.

**Stolperfallen**

- Eingebettetes Video mit anschließenden Empfehlungen aus dem allgemeinen Plattformbestand.
- Chat- oder Kommentarfunktion ohne Moderation und ohne Meldefunktion.
- Externe Links auf Seiten mit altersbeschränkten Inhalten.

**Behebung**

- Einbettungen auf jugendschutzkonforme Modi umstellen oder Inhalte selbst hosten.
- Moderation und Meldefunktion einführen.
- Externe Verlinkungen aus Schülerbereichen prüfen und einschränken.

**Nachweise**

- Inhaltsquellen- und Moderationskonzept.
- Liste externer Links aus Schülerbereichen mit Bewertung.

<details><summary>Kriteriumstext V0.2</summary>

Das Angebot ist jugendmedienschutzrechtlich unbedenklich.

</details>

### RDS-WER-384 — Werbefreiheit

*MUSS-Kriterium, Bereich RDS, Automatisierung: automatisiert*

Das Bildungsangebot ist werbefrei, soweit nicht eine Ausnahme für Lehr- und Lernmittel greift.

**Automatisiert prüfbar.** Die automatisierte Prüfung erkennt Werbenetzwerke und Werbepfade in Netzwerkanfragen und Markup, außerdem Kennzeichnungsbegriffe wie Anzeige, Werbung oder Sponsored und Affiliate-Parameter in Links.

**Grenzen der Automatik.** Eigenwerbung, Upselling und produktinterne Empfehlungen sind inhaltlich zu bewerten und nicht allein aus Signalen erkennbar.

**Benötigte Eingaben.** Produkt-URL.

**Selbst prüfen**

- Produkt mit leerem Browserprofil durchklicken und auf Werbeflächen, Banner, Interstitials und gesponserte Kacheln achten.
- Prüfen, ob Werbe- oder Affiliate-Netzwerke eingebunden sind.
- Eigenwerbung prüfen: Upgrade-Hinweise, Upselling, Cross-Selling in Schülerbereichen.
- Prüfen, ob kostenlose und kostenpflichtige Varianten unterschiedlich werbebehaftet sind, und die geprüfte Variante festhalten.
- Prüfen, ob eine Ausnahme für Lehr- und Lernmittel greift, und die Begründung dokumentieren.
- Durchgang für Schüler- und Lehrkräfteperspektive getrennt durchführen.

**Stolperfallen**

- Kostenlose Variante mit Werbung, geprüft wurde aber die bezahlte Variante.
- Upgrade-Werbung in Schülerbereichen als Produktinformation eingeordnet.
- Affiliate-Links in Materialempfehlungen.

**Behebung**

- Werbung aus allen von Schülerinnen und Schülern erreichbaren Bereichen entfernen.
- Upselling auf Verwaltungs- und Lehrkräftebereiche begrenzen.
- Affiliate-Parameter aus Links entfernen.

**Nachweise**

- Screenshots der geprüften Bereiche je Perspektive.
- Angabe der geprüften Produktvariante und Lizenz.

<details><summary>Kriteriumstext V0.2</summary>

Das digitale Bildungsangebot ist werbefrei, es sei denn, eine konkrete Werbung ist nach den einschlägigen Bestimmungen für Lehr- und Lernmittel ausnahmsweise zulässig

</details>

### RDS-WER-385 — Verweise auf Werbeinhalte

*MUSS-Kriterium, Bereich RDS, Automatisierung: automatisiert*

Aus Schülerbereichen wird nicht auf Zielseiten verlinkt, die Werbung enthalten.

**Automatisiert prüfbar.** Die automatisierte Prüfung sammelt ausgehende Links und prüft Zielhosts sowie Werbe- und Affiliate-Muster.

**Grenzen der Automatik.** Die automatisierte Prüfung bewertet nicht jede Zielseite inhaltlich. Zielseiten können sich zudem jederzeit ändern.

**Benötigte Eingaben.** Produkt-URL.

**Selbst prüfen**

- Alle externen Links auflisten, die Schülerinnen und Schüler erreichen können, inklusive Links in Lerninhalten und Materialien.
- Zielseiten stichprobenartig mit leerem Browserprofil aufrufen und auf Werbung prüfen.
- Prüfen, ob Links auf Plattformen führen, die Werbung ausspielen, etwa Videoplattformen oder Nachrichtenportale.
- Prüfen, ob Links Tracking- oder Affiliate-Parameter tragen.
- Prüfen, ob es einen Prozess gibt, der verlinkte Zielseiten wiederkehrend überprüft.

**Stolperfallen**

- Verlinkung auf Videoplattform mit Werbung vor dem Inhalt.
- Redaktionell gepflegte Materiallisten ohne wiederkehrende Prüfung.
- Weiterleitungsdienste, die die eigentliche Zielseite verdecken.

**Behebung**

- Werbebehaftete Ziele durch werbefreie Alternativen ersetzen oder Inhalte selbst bereitstellen.
- Wiederkehrende Linkprüfung einführen und dokumentieren.

**Nachweise**

- Linkliste mit Zielbewertung und Prüfdatum.
- Beschreibung des Prozesses zur Linkpflege.

<details><summary>Kriteriumstext V0.2</summary>

Aus dem Angebot wird für Nutzende der Benutzergruppe Schülerinnen und Schüler nicht auf Zielseiten verlinkt werden, die Werbung enthalten.

</details>

## 7. Abschluss und Nachweise

Der Selbstcheck ist erst abgeschlossen, wenn jedes Kriterium einen begründeten Status hat und die Belege zusammengestellt sind. Offene Punkte sind kein Mangel des Selbstchecks, sondern das Arbeitsergebnis, das in die Prüfung eingeht.

- [ ] Jedes Kriterium hat einen Status und, bei allem außer erfüllt, eine Notiz mit Begründung oder nächstem Schritt.
- [ ] Nachweise sind benannt und ablegbar: Erhebungsbelege, Screenshots, Verträge, Listen.
- [ ] Für jedes nicht erfüllte Kriterium ist eine Maßnahme mit Verantwortlicher Person und Termin festgehalten.
- [ ] Für jede Klärung nötig-Bewertung ist dokumentiert, wer entscheidet und woran die Entscheidung hängt.
- [ ] Selbstcheck als Datei exportieren und mit den Belegen gemeinsam ablegen.
- [ ] Wiederholungstermin festlegen; Cookies, Dienstleister und verlinkte Zielseiten ändern sich mit jedem Release.
