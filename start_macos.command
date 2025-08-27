#!/usr/bin/env bash
# Rooster Omzetter - Super Simpele Starter (macOS)
# Gebruik: dubbelklik dit bestand (start_macos_noob.command)
# Doel: stap-voor-stap begeleiden, toestemming vragen, duidelijke fouten tonen.
set -e

# Kleuren
GREEN="$(printf '\033[0;32m')"
RED="$(printf '\033[0;31m')"
YELLOW="$(printf '\033[0;33m')"
CYAN="$(printf '\033[0;36m')"
RESET="$(printf '\033[0m')"

echo
echo "#########################################################################"
echo "#                      ROOSTER OMZETTER - STARTER (macOS)               #"
echo "#########################################################################"
echo "# Dit script helpt je met:"
echo "#  1) Controleren of je in de juiste map zit"
echo "#  2) Internetverbinding checken"
echo "#  3) Python 3 controleren of (met jouw toestemming) installeren"
echo "#  4) Benodigde Python-pakketten installeren (requirements.txt)"
echo "#  5) De app starten in je browser"
echo "#########################################################################"
echo

read -p "Wil je doorgaan? [Y/N] " GO
if [[ ! "$GO" =~ ^[Yy]$ ]]; then
  echo "Gestopt op verzoek."
  exit 0
fi

echo
echo "[Stap 1] Controleren of 'app.py' en 'requirements.txt' in deze map staan..."
if [[ ! -f "app.py" ]]; then
  echo "${RED}[FOUT] 'app.py' niet gevonden in deze map: ${PWD}${RESET}"
  echo "Zorg dat dit script, 'app.py' en 'requirements.txt' in dezelfde map staan."
  read -p "Druk op Enter om af te sluiten..."
  exit 1
fi
if [[ ! -f "requirements.txt" ]]; then
  echo "${RED}[FOUT] 'requirements.txt' niet gevonden in deze map: ${PWD}${RESET}"
  echo "Zorg dat dit script, 'app.py' en 'requirements.txt' in dezelfde map staan."
  read -p "Druk op Enter om af te sluiten..."
  exit 1
fi
echo "${GREEN}[OK] Bestanden gevonden.${RESET}"

echo
echo "[Stap 2] Internetverbinding testen (pypi.org ping)..."
if ping -c 1 -W 2 pypi.org >/dev/null 2>&1; then
  echo "${GREEN}[OK] Internet lijkt te werken.${RESET}"
else
  echo "${RED}[FOUT] Geen internetverbinding gedetecteerd. Controleer je netwerk en probeer opnieuw.${RESET}"
  read -p "Druk op Enter om af te sluiten..."
  exit 1
fi

echo
echo "[Stap 3] Python 3 controleren..."
PYTHON=""
if command -v python3 >/dev/null 2>&1; then
  PYTHON="python3"
  echo "${GREEN}[OK] Python gevonden: ${PYTHON}${RESET}"
else
  echo "${YELLOW}[INFO] python3 is niet gevonden op dit systeem.${RESET}"
  echo "Je kunt Python automatisch laten installeren met Homebrew (aanbevolen)."
  echo "Als je geen Homebrew hebt, kun je dat eerst installeren via https://brew.sh/"
  read -p "Wil je dat ik Python 3.11 voor je installeer met Homebrew? [Y/N] " INSTALLPY
  if [[ "$INSTALLPY" =~ ^[Yy]$ ]]; then
    if ! command -v brew >/dev/null 2>&1; then
      echo "${RED}[FOUT] Homebrew is niet gevonden.${RESET}"
      echo "Open https://brew.sh/ in je browser om Homebrew te installeren."
      read -p "Wil je dat ik die pagina nu open? [Y/N] " OPENBREW
      if [[ "$OPENBREW" =~ ^[Yy]$ ]]; then open "https://brew.sh/"; fi
      echo "Installeer Homebrew en start dit script daarna opnieuw."
      read -p "Druk op Enter om af te sluiten..."
      exit 1
    fi
    echo "${CYAN}[INFO] Python 3.11 installeren via Homebrew (dit kan even duren)...${RESET}"
    brew update
    brew install python@3.11
    echo
    echo "${YELLOW}[BELANGRIJK] Sluit dit venster en dubbelklik daarna opnieuw op dit script,${RESET}"
    echo "${YELLOW}zodat de PATH-instellingen zijn ververst en 'python3' werkt.${RESET}"
    read -p "Druk op Enter om af te sluiten..."
    exit 0
  else
    echo "Installeer Python handmatig via https://www.python.org/downloads/ (kies 3.10 of 3.11) en start dit script opnieuw."
    read -p "Druk op Enter om af te sluiten..."
    exit 1
  fi
fi

echo
echo "[Stap 4] Pip upgraden en dependencies installeren..."
# Pip upgraden (fouten negeren)
$PYTHON -m pip install --upgrade pip --user || true

echo "We gaan nu de benodigde Python-pakketten installeren uit requirements.txt."
read -p "Doorgaan met installeren? [Y/N] " INSTALLDEPS
if [[ ! "$INSTALLDEPS" =~ ^[Yy]$ ]]; then
  echo "Installatie geannuleerd op verzoek."
  exit 0
fi

if ! $PYTHON -m pip install --user -r requirements.txt; then
  echo "${RED}[FOUT] Installatie van dependencies is mislukt.${RESET}"
  echo "Probeer in Terminal handmatig:  $PYTHON -m pip install --user -r requirements.txt"
  read -p "Druk op Enter om af te sluiten..."
  exit 1
fi
echo "${GREEN}[OK] Dependencies geïnstalleerd.${RESET}"

echo
echo "[Stap 5] App starten — er zou nu een browservenster moeten openen."
echo "Als dat niet gebeurt, ga naar: http://localhost:8501"
echo
exec $PYTHON -m streamlit run app.py
