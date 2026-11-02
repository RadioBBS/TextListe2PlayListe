"""
Werte muessen mit project_meta.py uebereinstimmen (eine Quelle der Wahrheit).
Styleguide 2.0.0 / Software-Standard 1.5.0 – Agent zuerst diese Datei lesen.

Projekt:     TextListe2PlayListe
Modul:       tests/test_meta.py
Version:     1.1.1
Stand:       2026-11-02
Abhaengig:   nur Python-Standardbibliothek (Python >= 3.11)
Bezug:       requirements.txt (leer – Stdlib only)
Lizenz:      –
Upstream:    –
Erstellt mit: Cursor Grok 4.6
Autor:       (FFHB) / RadioBBS

Historie
--------
Version 1.1.1 – 2026-11-02 – Startausgabe und Python 3.11 nach Styleguide 2.1.0.
"""

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class TestMeta(unittest.TestCase):
    """Prueft den Versionsabgleich ohne Fachlauf.

    Beschreibung: Liest PROJECT.yaml und pyproject.toml.
    Parameter: keine
    Rueckgabe: keine
    Fehlerfaelle: AssertionError bei abweichender Version oder fehlendem Zweck
    Beispiel: python -m unittest tests.test_meta
    """

    def test_version_und_zweck(self) -> None:
        """Version und Beschreibung von YAML und TOML sind dieselben."""
        yaml = (ROOT / "PROJECT.yaml").read_text(encoding="utf-8")
        toml = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
        version = re.search(r'(?m)^version:\s*"([^"]+)"', yaml)
        self.assertIsNotNone(version)
        self.assertIn(f'version = "{version.group(1)}"', toml)
        beschreibung = _beschreibung(yaml)
        self.assertTrue(beschreibung)
        self.assertIn(beschreibung, toml)


def _beschreibung(yaml: str) -> str:
    """Liest description aus PROJECT.yaml, auch bei gefaltetem Text.

    Beschreibung: Nimmt die erste description-Angabe.
    Parameter: yaml ist der Dateitext.
    Rueckgabe: Ein Satz oder ein leerer String.
    Fehlerfaelle: keine
    Beispiel: _beschreibung("description: Hallo.\n") == "Hallo."
    """
    zeilen = yaml.splitlines()
    for index, zeile in enumerate(zeilen):
        if not zeile.startswith("description:"):
            continue
        rest = zeile.split(":", 1)[1].strip()
        if rest in {">", ">-", "|", "|-"}:
            teile = []
            for folge in zeilen[index + 1:]:
                if folge.startswith("  "):
                    teile.append(folge.strip())
                elif not folge.strip():
                    if teile:
                        break
                else:
                    break
            return " ".join(teile).strip("\"'")
        return rest.strip("\"'")
    return ""


if __name__ == "__main__":
    unittest.main()
