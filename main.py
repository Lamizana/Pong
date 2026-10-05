"""Point d'entrée du jeu.

Lancement : `python main.py`
"""

import sys
from pathlib import Path

from pong.app import App

LOG_NAME = "pong-error.log"


def report_startup_error(message, log_dir=None):
    """Signale une erreur de démarrage là où l'utilisateur peut la voir.

    L'exécutable `--windowed` n'a pas de console : un plantage silencieux
    fermerait la fenêtre sans explication. On écrit donc toujours un journal
    (`pong-error.log`) et, sous Windows, on affiche une boîte de dialogue.
    Renvoie le chemin du journal (ou None s'il n'a pas pu être écrit).
    """
    print(message, file=sys.stderr)

    log_path = Path(log_dir) if log_dir else Path.cwd()
    log_path = log_path / LOG_NAME
    try:
        log_path.write_text(message + "\n", encoding="utf-8")
    except OSError:
        log_path = None
    else:
        print(f"Détail écrit dans {log_path}", file=sys.stderr)

    if sys.platform == "win32":
        try:
            import ctypes

            ctypes.windll.user32.MessageBoxW(
                None, message, "Pong — démarrage impossible", 0x10)
        except Exception:  # boîte indisponible : le journal reste la trace
            pass

    return log_path


def main():
    """Lance le jeu ; renvoie le code de sortie du processus."""
    try:
        app = App()
    except Exception as error:  # mieux vaut un message qu'une fermeture muette
        report_startup_error(f"Pong n'a pas pu démarrer :\n{error}")
        return 1
    app.run()
    return 0


if __name__ == "__main__":
    sys.exit(main())
