# Rooster Omzetter 📅

Een simpele Streamlit-app die een Excel-rooster (`.xlsx`) omzet naar **ICS-agenda’s per persoon**.  
Importeer de bestanden daarna in **Outlook, Google Calendar** of **Apple Calendar**.

---

## Voor wie?

Deze README bevat twee stap-voor-stap handleidingen:

1. **Streamlit Community Cloud** (snel online gebruiken, geen installatie).  
2. **Windows Quickstart (Desktop)** (lokaal draaien via Python, zonder virtuele omgeving).

---

## ✨ Functies

- Excel (`.xlsx`) inlezen en kolommen automatisch herkennen (datum, tijden, groep, zaal, beschrijving, personen).
- Meerdere personen selecteren → per persoon één ICS.
- Optioneel: “allen”-events meenemen en per event aan/uit zetten.
- Slimme beschrijvingen in ICS: lokaal, groep, vorige/toekomstige lessen, en andere lessen uit dezelfde serie.
- Debug-modus met uitbreidbare logs en stap-tijden (handig bij problemen).
- ZIP-download om alle docenten in één keer te krijgen.

---

## 🧰 Benodigdheden

- Een Excel-bestand (`.xlsx`) met kolommen: **Datum, Van, Tot, Student groep, Zaal, Beschrijving NL, Docenten**.  
- Docenten kunnen in één cel staan, gescheiden door spatie/komma/slash/`;` (bijv. `Piet, Klaas/Anna`).  
- Gebruik **`allen`** (exact dit woord) als event voor iedereen.

---

##  Bestanden in deze repo

```text
.
├─ app.py                # De Streamlit-app
├─ requirements.txt      # Python packages
└─ README.md             # Deze handleiding
```

### requirements.txt

```text
streamlit>=1.33
pandas>=2.0
icalendar>=5.0
openpyxl>=3.1
```

**Waarom `openpyxl`?** Pandas gebruikt dit om `.xlsx` te lezen.

---

## 🚀 Windows Quickstart (Desktop)

Plaats de projectmap op je Bureaublad (Desktop).  
Probeer eerst de start_windows.bat
Werkt het niet? Volg dan de onderstaande stappen. 

### Stap 0: Download & installeer Python

1. Ga naar <https://www.python.org/downloads/>  
2. Klik op **Download Python 3.x** (3.10 of 3.11 aangeraden).  
3. **Belangrijk:** vink *“Add Python to PATH”* aan tijdens de installatie.  
4. Klik **Install Now** en wacht tot de installatie voltooid is.

### Stap 1: Download de projectbestanden

1. Klik in GitHub op **Code → Download ZIP**.  
2. Pak het ZIP-bestand uit op je Bureaublad (Desktop) → je krijgt de map **RoosterOmzetter** met o.a. `streamlit_app.py` en `requirements.txt`.

### Stap 2: Open de opdrachtprompt (CMD) en ga naar de map

```bat
cd %HOMEPATH%\Desktop\RoosterOmzetter
```

### Stap 3: Installeer de benodigdheden

```bat
pip install -r requirements.txt
```

### Stap 4: Start de app

```bat
streamlit run streamlit_app.py
```

De app opent automatisch in je browser. Zo niet, ga handmatig naar: <http://localhost:8501>.

---
## 🚀 Macos Quickstart (Desktop)

Plaats de projectmap op je Bureaublad (Desktop).  
Probeer eerst de start_macos.Command

## ☁️ Streamlit Community Cloud (géén install nodig)
[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://kpakakcrs2mjpkufkpk73d.streamlit.app/)


Dit is de makkelijkste manier: de app draait “in de cloud”, jij opent een link.

### Stap 1: Fork/Importeer de repo

- Maak (of gebruik) een GitHub-account.  
- Klik op **Fork** (of **Use this template**) om deze repo in jouw account te plaatsen.

### Stap 2: Deployen op Streamlit

1. Ga naar <https://share.streamlit.io> en log in met GitHub.  
2. Klik **New app** → kies jouw repo → branch (meestal `main`) → app file: `streamlit_app.py`.  
3. Klik **Deploy**.

### Stap 3: Gebruik de app

- Je krijgt een publieke URL. Deelbaar en direct bruikbaar.  
- Upload je Excel → controleer kolommen → kies docent(en) → **Download ICS of ZIP**.

**Belangrijke hints voor Streamlit Cloud**

- **Python-versie:** kies 3.10 of 3.11 in *Advanced settings* als nodig.  
- **Timeouts:** grote Excelbestanden kunnen langer duren. Zie ook de timeout-tips onderaan in de app.  
- **Secrets:** niet nodig voor deze app.

---

##  ICS importeren (korte uitleg)

**Google Calendar (web):**  
Instellingen tandwiel → **Instellingen** → links **Importeren en exporteren** → **Bestand importeren** → kies `.ics` → kies kalender → **Importeren**.

**Outlook (desktop):**  
Dubbelklik `.ics` → **Openen als nieuwe kalender** → sleep items naar je eigen kalender, of **Opslaan & sluiten**.  
(*Outlook web:* Agenda → **Toevoegen** → **Van bestand uploaden**.)

**Apple Calendar (macOS):**  
Dubbelklik `.ics` → kies kalender → **OK**.

---

## ⚙️ Sidebar-opties & debug

- **Debug-modus:** toont extra uitleg, tussenstappen en eventuele fouten (stacktrace).  
- **Evenementen voor `allen` opnemen:** voeg algemene events toe, met per event een checkbox om op te nemen/uit te sluiten.

---

## 📋 Voorbeeldrooster (Markdown-tabel)

**Formaatregels:**

- **Datum:** `DD-MM-JJJJ`  
- **Tijd:** `HH:MM` (24-uurs)  
- Meerdere docenten scheiden met komma/slash/semicolon  
- Gebruik `allen` (exact) als event voor iedereen  
- **Zaal** mag leeg blijven (wordt “Onbekend”)

| Datum      | Van   | Tot   | Student groep | Zaal  | Beschrijving NL                         | Docenten     |
|------------|-------|-------|---------------|-------|------------------------------------------|--------------|
| 02-09-2025 | 08:30 | 10:00 | CRIM-1A       | B.1.12| Inleiding Criminologie                   | Jan          |
| 02-09-2025 | 10:15 | 12:00 | CRIM-1A       | B.1.12| Werkgroep Daders & Slachtoffers          | Kees, Anna   |
| 02-09-2025 | 13:00 | 15:00 | CRIM-2B       |       | Intervisie                               | allen        |
| 03-09-2025 | 09:00 | 10:30 | MED-3C        | C.2.05| ABCDE                                    | Klaas/Anna   |
| 03-09-2025 | 10:45 | 12:15 | MED-3C        | C.2.05| Practicum ECG                            | Anna         |
| 03-09-2025 | 13:15 | 14:45 | CRIM-1A       | B.1.12| Gastcollege Forensische Psychiatrie      | Joost        |

---

##  Veelvoorkomende problemen & oplossingen

**“Engine openpyxl not found / Missing optional dependency 'openpyxl'”**  
Installeer `openpyxl`:
```bat
pip install openpyxl
```

**App start, maar browser opent niet automatisch**  
Ga handmatig naar <http://localhost:8501>.

**Fout bij het lezen van het Excel-bestand**  
- Is het echt `.xlsx` (geen `.csv`, `.xlsm`, etc.)?  
- Datumkolom aanwezig en geldig?  
- Tijden in `HH:MM` (bijv. `08:30`).

**Niets verschijnt bij “Docenten”**  
- Controleer of de docenten-kolom bestaat en is toegewezen.  
- Scheid meerdere docenten met spatie/komma/slash/`;`.  
- Voorbeeld: `Piet, Klaas/Anna`.

**“AxiosError: timeout exceeded” in de UI**  
- Zie tips in de app om timeouts te verhogen.  
- Probeer een kleiner Excel-bestand.

---

## 📄 Licentie

Dit project is gelicentieerd onder de **European Union Public License (EUPL)**.  
De EUPL is een door de Europese Commissie goedgekeurde open source licentie, ontworpen voor software die met publieke middelen ontwikkeld is en teruggegeven wordt aan de samenleving.

**Waarom EUPL?**

- ✅ Compatibel met andere open source licenties (zoals GPL).  
- ✅ Waarborgt dat software ontwikkeld met publiek geld ook publiek beschikbaar blijft.  
- ✅ Past bij Open Science en FAIR-principes (Findable, Accessible, Interoperable, Reusable).

**Wat betekent dit voor jou?**

- Je mag de software vrij gebruiken, delen en aanpassen (ook commercieel).  
- Verspreid je de software (met of zonder aanpassingen), dan gebeurt dit onder dezelfde EUPL.

**📖 Meer info:** Officiële EUPL-tekst: <https://joinup.ec.europa.eu/collection/eupl/eupl-text-11-12>

---

## ℹ️ Transparantieverklaring

Delen van deze documentatie en de software zijn mede opgesteld met behulp van ChatGPT (AI-taalmodel van OpenAI).  
De inhoud is door een menselijke beheerder gecontroleerd en waar nodig aangepast.
