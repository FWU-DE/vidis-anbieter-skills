#!/usr/bin/env python3
"""Prüft Konsistenz von Inhalten und erzeugten Dateien.

Aufruf: ``python3 tools/check.py``. Exit-Code 1, wenn eine Prüfung fehlschlägt.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import build  # noqa: E402

TIMESTAMP = re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\+\d{2}:\d{2}|Z)?")

FAILURES: list[str] = []


def _normalise(text: str) -> str:
    """Erzeugungszeitpunkte ausblenden — sie unterscheiden sich bei jedem Lauf."""
    return TIMESTAMP.sub("<zeitstempel>", text)


def check(condition: bool, message: str) -> None:
    if condition:
        print(f"  ok    {message}")
    else:
        print(f"  FEHLT {message}")
        FAILURES.append(message)


def main() -> int:
    print("Inhalte")
    criteria = build.load_criteria()
    guide = build.load_selfcheck_guide()
    check(len(criteria) == 26, f"Registry enthält 26 Kriterien (gefunden: {len(criteria)})")
    check(set(criteria) == set(guide), "Registry und Anleitung deckungsgleich")
    check(
        all(entry.get("kriterientext") != "" for entry in [
            {"kriterientext": str(value.get("description", "")).strip()} for value in criteria.values()
        ]),
        "jedes Kriterium hat einen Kriteriumstext",
    )
    for field in ("selbst_pruefen", "stolperfallen", "behebung", "nachweise"):
        empty = [code for code, entry in guide.items() if not entry.get(field)]
        check(not empty, f"{field} überall gefüllt" + (f" — leer: {', '.join(empty)}" if empty else ""))

    print("Modell")
    # ISO-Zeitstempel, damit _normalise ihn wie den echten ausblendet.
    model = build.build_selfcheck_model(generated_at="2000-01-01T00:00:00+00:00")
    check(len(model["criteria"]) == len(criteria), "Modell enthält alle Kriterien")
    phases_with_criteria = {item["phase"] for item in model["criteria"]}
    declared = {phase["key"] for phase in model["phases"] if phase["holds_criteria"]}
    check(phases_with_criteria == declared, "jede Kriterienphase ist belegt")

    print("Erzeugte Dateien aktuell")
    reference = build.render_skill_reference(model)
    for path, rendered, label in (
        (build.DEFAULT_SKILL_REFERENCE, reference, "kriterien.md"),
    ):
        if not path.exists():
            check(False, f"{label} existiert")
            continue
        current = path.read_text(encoding="utf-8")
        check(_normalise(current) == _normalise(rendered), f"{label} ist auf dem Stand der Inhalte")

    print("Skill")
    skill = build.REPO_ROOT / "skills" / "vidis-selbstcheck" / "SKILL.md"
    check(skill.exists(), "SKILL.md vorhanden")
    if skill.exists():
        text = skill.read_text(encoding="utf-8")
        check(text.startswith("---\nname: vidis-selbstcheck\n"), "SKILL.md hat Frontmatter mit name")
        check("description:" in text.split("---")[1], "SKILL.md hat eine description")
        for reference_file in ("references/kriterien.md", "references/erhebung.md", "references/dossier.md"):
            check((skill.parent / reference_file).exists(), f"{reference_file} vorhanden")
            check(reference_file in text, f"{reference_file} ist in SKILL.md verlinkt")

    print()
    if FAILURES:
        print(f"{len(FAILURES)} Prüfung(en) fehlgeschlagen.")
        return 1
    print("Alle Prüfungen bestanden.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
