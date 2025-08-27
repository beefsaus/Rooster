
@echo off
setlocal ENABLEEXTENSIONS ENABLEDELAYEDEXPANSION
title Rooster Omzetter - Super Simpele Starter (Windows)

REM ================================
REM 0) Intro
REM ================================
color 0A
echo.
echo #########################################################################
echo #                      ROOSTER OMZETTER - STARTER                       #
echo #########################################################################
echo # Dit script helpt je stap-voor-stap met:                               #
echo #  1) Controleren of Python aanwezig is                                  #
echo #  2) (Optioneel) Python installeren via winget                          #
echo #  3) Benodigdheden installeren (requirements.txt)                       #
echo #  4) De app starten                                                     #
echo #########################################################################
echo.
echo BELANGRIJK:
echo - Zorg dat deze file ^(start.bat^) in dezelfde map staat als streamlit_app.py en requirements.txt.
echo - Dit script gebruikt GEEN virtuele omgeving; alles is lokaal per gebruiker.
echo.

REM Bevestiging om door te gaan
choice /C YN /M "Wil je doorgaan? [Y/N]"
if errorlevel 2 (
  echo Gestopt op verzoek van de gebruiker.
  pause
  exit /b 0
)

REM ================================
REM 1) Basiscontroles
REM ================================
echo.
echo [Stap 1] Controleren of we in de juiste map staan...
if not exist "streamlit_app.py" (
  echo [FOUT] streamlit_app.py niet gevonden in deze map: %CD%
  echo Zet start.bat, streamlit_app.py en requirements.txt bij elkaar in dezelfde map.
  pause
  exit /b 1
)
if not exist "requirements.txt" (
  echo [FOUT] requirements.txt niet gevonden in deze map: %CD%
  echo Zet start.bat, streamlit_app.py en requirements.txt bij elkaar in dezelfde map.
  pause
  exit /b 1
)
echo [OK] Bestanden gevonden.

REM ================================
REM 2) Internet check (nodig voor installatie)
REM ================================
echo.
echo [Stap 2] Internetverbinding testen...
ping -n 1 pypi.org >nul 2>&1
if errorlevel 1 (
  echo [FOUT] Geen internetverbinding gedetecteerd. Controleer je netwerk en probeer opnieuw.
  pause
  exit /b 1
)
echo [OK] Internet lijkt te werken.

REM ================================
REM 3) Python vinden of installeren
REM ================================
set "PYTHON="

echo.
echo [Stap 3] Python zoeken...
where py >nul 2>&1 && set "PYTHON=py"
if not defined PYTHON (
  where python >nul 2>&1 && set "PYTHON=python"
)

if defined PYTHON (
  echo [OK] Python gevonden: %PYTHON%
) else (
  echo [INFO] Python is niet gevonden op dit systeem.
  echo Je kunt Python automatisch laten installeren met winget (aanbevolen).
  echo Als je geen winget hebt, installeer Python handmatig via: https://www.python.org/downloads/
  echo.
  choice /C YN /M "Wil je dat ik Python automatisch installeer met winget? [Y/N]"
  if errorlevel 2 (
    echo Je hebt gekozen om Python NIET automatisch te installeren.
    echo Installeer Python 3.10 of 3.11 handmatig (met 'Add Python to PATH') en start dit script opnieuw.
    pause
    exit /b 1
  )
  winget -v >nul 2>&1
  if errorlevel 1 (
    echo [FOUT] Winget is niet beschikbaar op dit systeem.
    echo Installeer Python handmatig via https://www.python.org/downloads/ en start dit script daarna opnieuw.
    pause
    exit /b 1
  )
  echo [INFO] Python 3.11 installeren via winget...
  winget install -e --id Python.Python.3.11
  if errorlevel 1 (
    echo [FOUT] Installatie via winget is mislukt of geannuleerd.
    echo Installeer Python handmatig en start dit script opnieuw.
    pause
    exit /b 1
  )
  echo.
  echo [BELANGRIJK] Sluit dit venster ^(X^) en dubbelklik daarna opnieuw op start.bat
  echo zodat de PATH-instellingen ververst zijn.
  pause
  exit /b 0
)

REM ================================
REM 4) Pip upgraden en packages installeren
REM ================================
echo.
echo [Stap 4] Pip upgraden (dit kan even duren)...
%PYTHON% -m pip install --upgrade pip --user
if errorlevel 1 (
  echo [WAARSCHUWING] Pip upgraden is niet gelukt. We gaan verder met de huidige versie.
)

echo.
echo We gaan nu de benodigde Python-pakketten installeren uit requirements.txt
echo Dit wordt lokaal voor jouw gebruiker geïnstalleerd (geen admin-rechten nodig).
choice /C YN /M "Doorgaan met installeren? [Y/N]"
if errorlevel 2 (
  echo Installatie geannuleerd op verzoek.
  pause
  exit /b 0
)

%PYTHON% -m pip install --user -r requirements.txt
if errorlevel 1 (
  echo [FOUT] Installatie van dependencies is mislukt.
  echo Mogelijke oorzaken: netwerkproblemen of verouderde pip.
  echo Tip: probeer dit commando handmatig in CMD:  %PYTHON% -m pip install --user -r requirements.txt
  pause
  exit /b 1
)
echo [OK] Dependencies geïnstalleerd.

REM ================================
REM 5) App starten
REM ================================
echo.
echo [Stap 5] De app wordt nu gestart. Er opent normaal gesproken een browservenster.
echo Als dat niet gebeurt, ga dan handmatig naar: http://localhost:8501
echo.
%PYTHON% -m streamlit run streamlit_app.py
if errorlevel 1 (
  echo [FOUT] Streamlit kon niet starten.
  echo Controleer eventuele foutmeldingen hierboven.
  pause
  exit /b 1
)

echo.
echo [KLAAR] Bedankt! Je kunt dit venster sluiten.
pause
endlocal
