#!/usr/bin/env python3
"""Erzeugt Skill-Referenz, Datenmodell und portable Anleitung aus content/.

Ausgaben:

* ``skills/vidis-selbstcheck/references/kriterien.md`` — Nachschlagequelle des Skills
* ``dist/selbstcheck.json``                           — Datenmodell für das Anbieterportal

Aufruf: ``python3 tools/build.py``. Benötigt nur PyYAML.
"""

from __future__ import annotations

import html
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
CRITERIA_PATH = REPO_ROOT / "content" / "kriterien-v0_2.yaml"
GUIDE_PATH = REPO_ROOT / "content" / "selbstcheck-guide-v0_2.yaml"
DEFAULT_GUIDE_JSON = REPO_ROOT / "dist" / "selbstcheck.json"
DEFAULT_SKILL_REFERENCE = REPO_ROOT / "skills" / "vidis-selbstcheck" / "references" / "kriterien.md"

STORAGE_KEY = "vidis.selbstcheck.v1"
GUIDE_TITLE = "VIDIS Selbstcheck für Anbieter"

# Authoritative sources on vidis.schule. Everything here paraphrases the first
# one, so it is linked wherever the criteria are named — a provider must be
# able to check this repo against FWU's document.
KRITERIEN_URL = "https://www.vidis.schule/wp-content/uploads/sites/10/2024/12/Pruefkriterien-VIDIS-V0.2.pdf"
TEILNAHMEPROZESS_URL = "https://www.vidis.schule/teilnahmeprozess/"
VIDIS_PRUEFUNG = (
    "Validieren der Erfüllung der Kriterien zur Teilnahme am VIDIS-Verfahren"
)

STATUS_OPTIONS: tuple[tuple[str, str], ...] = (
    ("offen", "offen"),
    ("erfuellt", "erfüllt"),
    ("nicht_erfuellt", "nicht erfüllt"),
    ("manuell", "Klärung nötig"),
    ("nicht_zutreffend", "nicht zutreffend"),
)

GUIDE_FIELDS: tuple[str, ...] = (
    "phase",
    "kurz",
    "automatisierung",
    "automatisch",
    "grenzen",
    "selbst_pruefen",
    "stolperfallen",
    "behebung",
    "nachweise",
)


@dataclass(frozen=True)
class Phase:
    key: str
    title: str
    lead: str
    steps: tuple[str, ...] = ()
    commands: tuple[tuple[str, str], ...] = ()
    holds_criteria: bool = True


PHASES: tuple[Phase, ...] = (
    Phase(
        key="vorbereitung",
        title="1. Vorbereitung",
        lead=(
            "Bevor geprüft wird, wird der Prüfgegenstand festgelegt. Ohne diese Festlegung "
            "sind Ergebnisse später nicht zuordenbar: Werbefreiheit kann in der kostenlosen "
            "Variante anders aussehen als in der bezahlten, und Cookies unterscheiden sich "
            "zwischen angemeldetem und öffentlichem Bereich."
        ),
        steps=(
            "Zielgruppe festlegen: richtet sich das Angebot an Schülerinnen und Schüler, an Lehrkräfte oder an beide? Die Zielgruppe entscheidet über den Maßstab bei Cookies, Tracking und Werbung.",
            "Produktvariante und Lizenz festhalten, die geprüft wird, inklusive Version oder Release-Stand.",
            "Alle Hostnamen des Angebots auflisten: Web, API, Assets, Login, Admin, Statusseite. Jeder Host wird einzeln geprüft.",
            "Rechtstexte zusammenstellen: Impressum, Datenschutzerklärung, AGB oder Nutzungsbedingungen, AVV mit Anlagen.",
            "Testzugänge für Schüler- und Lehrkräfteperspektive bereitstellen, ohne echte personenbezogene Daten.",
            "Verantwortliche Personen je Prüfbereich benennen: Technik, Datenschutz, Recht, Redaktion.",
        ),
        holds_criteria=False,
    ),
    Phase(
        key="erhebung",
        title="2. Technische Erhebung",
        lead=(
            "Diese Phase sammelt die messbaren Belege: Transportverschlüsselung, Weiterleitungen, "
            "Cookies, Browser-Speicher, Netzwerkaufrufe und die Erreichbarkeit der Rechtstexte. "
            "Die Befehle unten laufen auf jedem Rechner mit curl, openssl und einem Browser. "
            "Der Skill vidis-selbstcheck führt dieselbe Erhebung agentisch durch und trägt die "
            "Ergebnisse direkt in ein Dossier ein."
        ),
        steps=(
            "Erhebung je Hostname durchführen, nicht nur für die Hauptdomain.",
            "Transport prüfen: http-Aufruf, Weiterleitung, veraltete TLS-Versionen.",
            "Cookies und Browser-Speicher im Browser mit leerem Profil auslesen, ohne im Consent-Banner zuzustimmen.",
            "Netzwerkaufrufe aufzeichnen und als HAR-Datei sichern; sie belegen Tracking-, Werbe- und CDN-Aufrufe.",
            "Rechtstexte abrufen und als Datei mit Datum sichern.",
            "Erhebung im angemeldeten Bereich wiederholen, getrennt für Schüler- und Lehrkräfteperspektive.",
            "Alle Belege in einem Ordner je Prüfdatum ablegen, damit sie im Dossier referenzierbar sind.",
        ),
        commands=(
            (
                "Weiterleitung von http auf https prüfen (ITS-ENC-359, ITS-ENC-360)",
                "curl -sS -o /dev/null -w 'http  -> %{http_code} %{redirect_url}\\n' http://{HOST}\n"
                "curl -sS -o /dev/null -w 'https -> %{http_code}\\n' https://{HOST}\n"
                "curl -sSI https://{HOST} | grep -i 'strict-transport-security' || echo 'kein HSTS-Header'",
            ),
            (
                "Veraltete TLS-Protokolle prüfen (ITS-ENC-361)",
                "for proto in tls1 tls1_1; do\n"
                "  printf '%s: ' \"$proto\"\n"
                "  openssl s_client -connect {HOST}:443 -\"$proto\" </dev/null >/dev/null 2>&1 \\\n"
                "    && echo 'ANGENOMMEN — Befund' || echo 'abgelehnt — erwartet'\n"
                "done",
            ),
            (
                "Cookies und Browser-Speicher auslesen — im Browser-Konsolenfenster ausführen (RDS-CUC-371 bis 375, RDS-CUC-453)",
                "copy(JSON.stringify({\n"
                "  url: location.href,\n"
                "  cookies: document.cookie.split('; ').filter(Boolean),\n"
                "  localStorage: Object.fromEntries(Object.entries(localStorage)),\n"
                "  sessionStorage: Object.fromEntries(Object.entries(sessionStorage)),\n"
                "  serviceWorker: navigator.serviceWorker\n"
                "    ? (await navigator.serviceWorker.getRegistrations()).map((r) => r.scope)\n"
                "    : [],\n"
                "  indexedDB: indexedDB.databases ? (await indexedDB.databases()).map((d) => d.name) : [],\n"
                "}, null, 2));",
            ),
            (
                "Fremd-Domains aus einer HAR-Aufzeichnung auflisten (RDS-CUC-373, RDS-CDN-379, RDS-WER-384)",
                "jq -r '.log.entries[].request.url' aufzeichnung.har \\\n"
                "  | awk -F/ '{print $3}' | sort -u \\\n"
                "  | grep -v -e '{HOST}$'",
            ),
            (
                "Rechtstexte sichern (RDS-IPF-364 bis 367)",
                "mkdir -p belege\n"
                "for pfad in impressum datenschutz agb; do\n"
                "  curl -sS -o \"belege/$pfad.html\" -w \"$pfad: %{http_code}\\n\" \"{URL}/$pfad\"\n"
                "done",
            ),
        ),
        holds_criteria=False,
    ),
    Phase(
        key="technik",
        title="3. Technische Kriterien",
        lead=(
            "Diese Kriterien sind am Produkt selbst messbar. Die Erhebung aus Phase 2 liefert die "
            "Belege; zu klären bleiben Zweck und Notwendigkeit der gefundenen Cookies, Speicher "
            "und Signale sowie alle Bereiche, die ein öffentlicher Durchgang nicht erreicht."
        ),
    ),
    Phase(
        key="rechtstexte",
        title="4. Impressum, Datenschutzerklärung, Cookie-Beschreibung",
        lead=(
            "Hier geht es um Auffindbarkeit und Vollständigkeit der Pflichttexte. Automatisiert "
            "prüfbar ist, ob die Pflichtangaben im Text vorkommen. Ob sie inhaltlich zutreffen "
            "und zur tatsächlichen Verarbeitung passen, entscheidet eine fachlich "
            "verantwortliche Person."
        ),
    ),
    Phase(
        key="vertrag",
        title="5. Verträge, Dienstleister, Datenflüsse",
        lead=(
            "Diese Kriterien sind nicht am Produkt sichtbar, sondern in Verträgen, "
            "Verarbeitungsverzeichnis und Subunternehmerliste. Sie sind der häufigste Grund "
            "für Rückfragen in Prüfungen, weil Unterlagen fehlen oder veraltet sind."
        ),
    ),
    Phase(
        key="inhalte",
        title="6. Inhalte, Werbung, Jugendmedienschutz",
        lead=(
            "Inhaltliche Kriterien brauchen den Blick aus der Nutzerperspektive. Sie werden "
            "getrennt für Schülerinnen und Schüler sowie für Lehrkräfte durchlaufen, weil sich "
            "Sichtbarkeit und Zulässigkeit unterscheiden."
        ),
    ),
    Phase(
        key="abschluss",
        title="7. Abschluss und Nachweise",
        lead=(
            "Der Selbstcheck ist erst abgeschlossen, wenn jedes Kriterium einen begründeten "
            "Status hat und die Belege zusammengestellt sind. Offene Punkte sind kein Mangel "
            "des Selbstchecks, sondern das Arbeitsergebnis, das in die Prüfung eingeht."
        ),
        steps=(
            "Jedes Kriterium hat einen Status und, bei allem außer erfüllt, eine Notiz mit Begründung oder nächstem Schritt.",
            "Nachweise sind benannt und ablegbar: Erhebungsbelege, Screenshots, Verträge, Listen.",
            "Für jedes nicht erfüllte Kriterium ist eine Maßnahme mit Verantwortlicher Person und Termin festgehalten.",
            "Für jede Klärung nötig-Bewertung ist dokumentiert, wer entscheidet und woran die Entscheidung hängt.",
            "Selbstcheck als Datei exportieren und mit den Belegen gemeinsam ablegen.",
            "Wiederholungstermin festlegen; Cookies, Dienstleister und verlinkte Zielseiten ändern sich mit jedem Release.",
        ),
        holds_criteria=False,
    ),
)

PHASE_BY_KEY = {phase.key: phase for phase in PHASES}


def load_criteria(path: Path = CRITERIA_PATH) -> dict[str, dict[str, Any]]:
    """Read the criteria registry copy."""
    raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(raw, dict):
        raise ValueError(f"criteria registry must be a mapping: {path}")
    return raw


def load_selfcheck_guide(path: Path = GUIDE_PATH) -> dict[str, dict[str, Any]]:
    """Read the self-check guide content and validate its shape."""
    raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(raw, dict):
        raise ValueError(f"selfcheck guide must be a mapping: {path}")
    for code, entry in raw.items():
        if not isinstance(entry, dict):
            raise ValueError(f"selfcheck guide entry must be a mapping: {code}")
        missing = [field for field in GUIDE_FIELDS if field not in entry]
        if missing:
            raise ValueError(f"selfcheck guide entry {code} misses fields: {', '.join(missing)}")
        if entry["phase"] not in PHASE_BY_KEY:
            raise ValueError(f"selfcheck guide entry {code} uses unknown phase: {entry['phase']}")
        if not PHASE_BY_KEY[entry["phase"]].holds_criteria:
            raise ValueError(f"selfcheck guide entry {code} points to a phase without criteria: {entry['phase']}")
    return raw


def build_selfcheck_model(*, generated_at: str | None = None) -> dict[str, Any]:
    """Merge criteria registry and guide content into one model."""
    criteria = load_criteria()
    guide = load_selfcheck_guide()

    missing = sorted(set(criteria) - set(guide))
    if missing:
        raise ValueError(f"selfcheck guide misses registry criteria: {', '.join(missing)}")
    unknown = sorted(set(guide) - set(criteria))
    if unknown:
        raise ValueError(f"selfcheck guide has criteria outside the registry: {', '.join(unknown)}")

    entries: list[dict[str, Any]] = []
    for code, criterion in criteria.items():
        entry = guide[code]
        entries.append(
            {
                "code": code,
                "name": criterion["name"],
                "area": criterion["area"],
                "must": bool(criterion.get("must")),
                "phase": entry["phase"],
                "kurz": entry["kurz"],
                "automatisch": entry["automatisch"],
                "grenzen": entry["grenzen"],
                "selbst_pruefen": list(entry["selbst_pruefen"]),
                "stolperfallen": list(entry["stolperfallen"]),
                "behebung": list(entry["behebung"]),
                "nachweise": list(entry["nachweise"]),
                "kriterientext": str(criterion.get("description", "")).strip(),
                "automatisierung": entry["automatisierung"],
                "eingaben": entry.get("eingaben", ""),
                "artefakte": "",
            }
        )

    phase_order = [phase.key for phase in PHASES]
    entries.sort(key=lambda item: (phase_order.index(item["phase"]), item["code"]))

    return {
        "title": GUIDE_TITLE,
        "generated_at": generated_at or datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "criteria_registry": "content/kriterien-v0_2.yaml",
        "guide_source": "content/selbstcheck-guide-v0_2.yaml",
        "kriterien_url": KRITERIEN_URL,
        "teilnahmeprozess_url": TEILNAHMEPROZESS_URL,
        "vidis_pruefung": VIDIS_PRUEFUNG,
        "storage_key": STORAGE_KEY,
        "version_label": "V0.2",
        "status_options": [{"value": value, "label": label} for value, label in STATUS_OPTIONS],
        "phases": [
            {
                "key": phase.key,
                "title": phase.title,
                "lead": phase.lead,
                "steps": list(phase.steps),
                "commands": [{"title": title, "command": command} for title, command in phase.commands],
                "holds_criteria": phase.holds_criteria,
            }
            for phase in PHASES
        ],
        "criteria": entries,
    }


def write_selfcheck_outputs(
    *,
    json_path: Path = DEFAULT_GUIDE_JSON,
    reference_path: Path = DEFAULT_SKILL_REFERENCE,
) -> tuple[Path, Path]:
    """Write the JSON model and the skill reference."""
    model = build_selfcheck_model()
    for path in (json_path, reference_path):
        path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(model, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    reference_path.write_text(render_skill_reference(model), encoding="utf-8")
    return json_path, reference_path


def render_skill_reference(model: dict[str, Any]) -> str:
    """Render the Markdown criteria reference bundled with the skill."""
    lines: list[str] = [
        "# VIDIS Prüfkriterien V0.2 — Kriterienreferenz für den Selbstcheck",
        "",
        "> Erzeugt von `tools/build.py`. Nicht direkt bearbeiten — Inhalte stehen in "
        "`content/selbstcheck-guide-v0_2.yaml`.",
        "",
        f"Diese Datei deckt alle {len(model['criteria'])} aktiven Kriterien der VIDIS "
        "Prüfkriterien V0.2 ab. Sie ist die Nachschlagequelle des Skills "
        "`vidis-selbstcheck`: pro Kriterium steht dort, was automatisiert entscheidbar ist, "
        "wo die Automatik an ihre Grenzen kommt, wie selbst geprüft wird und welche "
        "Nachweise erwartet werden.",
        "",
        f"**Maßgeblich ist der Originalkatalog von FWU:** "
        f"[Prüfkriterienkatalog VIDIS {model['version_label']}]({model['kriterien_url']}). "
        "Alles hier ist eine Arbeitshilfe dazu, kein Ersatz.",
        "",
        f"Die VIDIS-Prüfung selbst bedeutet: {model['vidis_pruefung']} "
        f"(siehe [Teilnahmeprozess für Anbieter]({model['teilnahmeprozess_url']})).",
        "",
        f"Registry: `{model['criteria_registry']}`  ",
        f"Inhalte: `{model['guide_source']}`",
        "",
        "## Phasen",
        "",
    ]
    for phase in model["phases"]:
        codes = [item["code"] for item in model["criteria"] if item["phase"] == phase["key"]]
        detail = ", ".join(codes) if codes else "keine Kriterien, nur Arbeitsschritte"
        lines.append(f"- **{phase['title']}** — {detail}")
    lines.append("")

    for phase in model["phases"]:
        entries = [item for item in model["criteria"] if item["phase"] == phase["key"]]
        lines.extend([f"## {phase['title']}", "", phase["lead"], ""])
        for step in phase["steps"]:
            lines.append(f"- [ ] {step}")
        if phase["steps"]:
            lines.append("")
        for command in phase["commands"]:
            lines.extend([f"**{command['title']}**", "", "```bash", command["command"], "```", ""])
        for entry in entries:
            lines.extend(_reference_criterion_lines(entry))
    return "\n".join(lines).rstrip() + "\n"


def _reference_criterion_lines(entry: dict[str, Any]) -> list[str]:
    obligation = "MUSS" if entry["must"] else "SOLL"
    lines = [
        f"### {entry['code']} — {entry['name']}",
        "",
        f"*{obligation}-Kriterium, Bereich {entry['area']}, Automatisierung: {entry['automatisierung']}*",
        "",
        entry["kurz"],
        "",
        f"**Automatisiert prüfbar.** {entry['automatisch']}",
        "",
        f"**Grenzen der Automatik.** {entry['grenzen']}",
        "",
    ]
    if entry["eingaben"]:
        lines.extend([f"**Benötigte Eingaben.** {entry['eingaben']}", ""])
    for heading, key in (
        ("Selbst prüfen", "selbst_pruefen"),
        ("Stolperfallen", "stolperfallen"),
        ("Behebung", "behebung"),
        ("Nachweise", "nachweise"),
    ):
        lines.append(f"**{heading}**")
        lines.append("")
        for item in entry[key]:
            lines.append(f"- {item}")
        lines.append("")
    lines.extend(["<details><summary>Kriteriumstext V0.2</summary>", "", entry["kriterientext"], "", "</details>", ""])
    return lines


if __name__ == "__main__":
    for path in write_selfcheck_outputs():
        print(path)
