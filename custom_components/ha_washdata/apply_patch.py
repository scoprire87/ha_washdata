"""
Script da eseguire UNA VOLTA nella directory del fork per applicare la modifica
a manager.py: aggiunge il metodo async_force_active_profile dopo clear_manual_program.

Uso:
    cd /path/to/custom_components/ha_washdata
    python3 apply_patch.py
"""

import sys
from pathlib import Path

TARGET = Path("manager.py")

NEW_METHOD = '''
    async def async_force_active_profile(self, profile_name: str) -> None:
        """Force a profile on the active cycle from external early-recognition logic.

        Designed to be called by automations that identify the program before
        WashData's own shape-matcher does (e.g. lavastoviglie_v4.yaml).
        Gives WashData an immediate time-remaining estimate without waiting
        for the full cycle to complete.

        Pass an empty string to clear the override and return to auto-detection.
        """
        if not profile_name:
            self.clear_manual_program()
            self._logger.info("force_active_profile: override cleared, reverting to auto-detection")
        else:
            self.set_manual_program(profile_name)
            self._logger.info("force_active_profile: forced profile '%s'", profile_name)
        self._notify_update()

'''

ANCHOR = "    async def _run_post_cycle_processing(self) -> None:"

if not TARGET.exists():
    print(f"ERRORE: {TARGET} non trovato. Esegui lo script dalla directory ha_washdata.")
    sys.exit(1)

content = TARGET.read_text(encoding="utf-8")

if "async_force_active_profile" in content:
    print("NIENTE DA FARE: async_force_active_profile esiste già in manager.py")
    sys.exit(0)

if ANCHOR not in content:
    print(f"ERRORE: anchor '{ANCHOR}' non trovato in manager.py.")
    print("Il file potrebbe essere una versione diversa da quella attesa.")
    sys.exit(1)

patched = content.replace(ANCHOR, NEW_METHOD + ANCHOR, 1)
TARGET.write_text(patched, encoding="utf-8")
print(f"OK: async_force_active_profile aggiunto a manager.py")
print(f"    Righe prima: {content.count(chr(10))}")
print(f"    Righe dopo:  {patched.count(chr(10))}")
