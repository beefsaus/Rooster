# Rooster Omzetter 📅

Een simpele Streamlit-app die een Excel-rooster (.xlsx) omzet naar ICS-agenda’s per docent.  
Importeer de bestanden daarna in Outlook, Google Calendar of Apple Calendar.

---

## Voor wie?

Voor gebruikers met nul technische kennis. Deze README bevat twee stap-voor-stap handleidingen:

1. **Streamlit Community Cloud** (snel online gebruiken, geen installatie).  
2. **Handmatige Windows-installatie** (lokaal draaien via Python).

---

## ✨ Functies

- Excel (.xlsx) inlezen en kolommen automatisch herkennen (datum, tijden, groep, zaal, beschrijving, docenten).
- Meerdere docenten selecteren → per docent één ICS.
- Optioneel: “allen”-events meenemen en per event aan/uit zetten.
- Slimme beschrijvingen in ICS: lokaal, groep, vorige/toekomstige lessen, en andere lessen uit dezelfde serie.
- Debug-modus met uitbreidbare logs en stap-tijden (handig bij problemen).
- ZIP-download om alle docenten in één keer te krijgen.

---

## 🧰 Benodigdheden

- Een Excel-bestand (.xlsx) met kolommen voor o.a. **Datum, Van, Tot, Student groep, Zaal, Beschrijving NL, Docenten**.  
- Docenten kunnen in één cel staan, gescheiden door spatie/komma/slash/`;` (bijv. `Piet, Klaas/Anna`).  
- Gebruik **“allen”** (exact dit woord) als event voor iedereen.

---

## 📦 Bestanden in deze repo

├─ app.py # De Streamlit-app (de code uit deze README-opdracht)
├─ requirements.txt # Python packages
└─ README.md # Deze handleiding

### requirements.txt (voorgesteld)
streamlit>=1.33
pandas>=2.0
icalendar>=5.0
openpyxl>=3.1


> **Waarom openpyxl?** Pandas gebruikt dit om `.xlsx` te lezen.

---

## 🚀 Snel starten (als je al Python hebt)

```bash
pip install -r requirements.txt
streamlit run app.py
Je browser opent (of ga naar):
👉 http://localhost:8501

# Handleiding – Rooster Omzetter 📅

---

## Handleiding 1 – Streamlit Community Cloud (géén install nodig)

Dit is de makkelijkste manier: app draait “in de cloud”, jij opent een link.

### Stap 1: Fork/Importeer de repo
- Maak (of gebruik) een GitHub-account.  
- Klik op **Fork** (of “Use this template”) om deze repo in jouw account te plaatsen.

### Stap 2: Deployen op Streamlit
- Ga naar [https://share.streamlit.io](https://share.streamlit.io) en log in met GitHub.  
- Klik **New app** → kies jouw repo → branch (meestal main) → app file: `app.py`.  
- Klik **Deploy**.

### Stap 3: Gebruik de app
- Je krijgt een publieke URL. Deelbaar en direct bruikbaar.  
- Upload je Excel → controleer kolommen → kies docent(en) → Download ICS of ZIP.

### Belangrijke hints voor Streamlit Cloud
- **Python-versie**: kies 3.10 of 3.11 in *Advanced settings* als nodig.  
- **Timeouts**: grote Excelbestanden kunnen langer duren. Zie ook de timeout-tips onderaan in de app.  
- Geen secrets nodig voor deze app.  

---

## Handleiding 2 – Handmatige Windows-installatie (nul voorkennis)

Volg dit precies; je hoeft niets te weten over programmeren.


---

## 🚀 Snel starten (Windows)

Volg deze stappen precies. Geen programmeerkennis nodig.  

---

### Stap 0: Download & installeer Python
1. Ga naar [https://www.python.org/downloads/](https://www.python.org/downloads/).  
2. Klik op **Download Python 3.x** (versie 3.10 of 3.11 wordt aangeraden).  
3. **Belangrijk:** vink het vakje **“Add Python to PATH”** aan tijdens de installatie.  
4. Klik op **Install Now** en wacht tot de installatie voltooid is.  

---

### Stap 1: Download de projectbestanden
1. Klik in GitHub op **Code → Download ZIP**.  
2. Pak het ZIP-bestand uit op je **Bureaublad (Desktop)**.  
3. Je krijgt een map `RoosterOmzetter` met daarin o.a.:
   - `app.py`  
   - `requirements.txt`  

---

### Stap 2: Open de opdrachtprompt (CMD)
1. Druk op **Start** → typ `cmd` → open **Opdrachtprompt**.  
2. Ga naar de map op je Bureaublad:  

```bash
cd %HOMEPATH%\Desktop\RoosterOmzetter

###Stap 3: Installeer de benodigdheden

In dezelfde opdrachtprompt:

pip install -r requirements.txt



###Stap 4: Start de app

Start de Streamlit-app met:

streamlit run app.py

📥 ICS importeren (korte uitleg)

Google Calendar (web):
Instellingen tandwiel → Instellingen → links Importeren en exporteren → Bestand importeren → kies .ics → kies kalender → Importeren.

Outlook (desktop):
Dubbelklik .ics → Openen als nieuwe kalender → sleep items naar je eigen kalender, of Opslaan & sluiten.
(Outlook web: Agenda → Toevoegen → Van bestand uploaden.)

Apple Calendar (macOS):
Dubbelklik .ics → kies kalender → OK.

⚙️ Sidebar-opties & debug

Debug-modus: toont extra uitleg, tussenstappen en eventuele fouten met stacktrace.

Evenementen voor “allen” opnemen: voeg algemene events toe, met per event een checkbox om op te nemen/uitsluiten.



📋 Voorbeeldrooster 
Datum	Van	Tot	Student groep	Zaal	Beschrijving NL	Docenten
02-09-2025	08:30	10:00	CRIM-1A	B.1.12	Inleiding Criminologie	Jan
02-09-2025	10:15	12:00	CRIM-1A	B.1.12	Werkgroep Daders & Slachtoffers	Kees, Anna
02-09-2025	13:00	15:00	CRIM-2B		Intervisie	allen
03-09-2025	09:00	10:30	MED-3C	C.2.05	ABCDE	Klaas/Anna
03-09-2025	10:45	12:15	MED-3C	C.2.05	Practicum ECG	Anna
03-09-2025	13:15	14:45	CRIM-1A	B.1.12	Gastcollege Forensische Psychiatrie	Joost


## 📄 Licentie

Dit project is gelicentieerd onder de **European Union Public License (EUPL)**.  
De EUPL is een door de Europese Commissie goedgekeurde open source licentie, speciaal ontworpen voor software die met **publieke middelen** ontwikkeld is en teruggegeven wordt aan de samenleving.

### Waarom EUPL?
- ✅ Juridisch waterdicht binnen de Europese Unie.  
- ✅ Compatibel met andere open source licenties (zoals GPL).  
- ✅ Waarborgt dat software ontwikkeld met publiek geld ook publiek beschikbaar blijft.  
- ✅ Sluit naadloos aan bij de principes van **Open Science** en **FAIR data/software** (Findable, Accessible, Interoperable, Reusable).  

### Wat betekent dit voor jou?
- Je mag de software **vrij gebruiken, delen en aanpassen**, zowel voor persoonlijke als commerciële doeleinden.  
- Als je de software verder verspreidt (met of zonder aanpassingen), moet dit onder dezelfde EUPL-licentie gebeuren.  
- Zo blijft kennis die met **publieke middelen** is gemaakt ook **publiek eigendom**.  

### Open Science 🌍
Dit project is onderdeel van de bredere beweging naar **Open Science**:  
- Onderzoek, data en software ontwikkeld met publieke middelen zijn vrij toegankelijk.  
- Bevordert transparantie, samenwerking en hergebruik.  
- Stimuleert innovatie doordat iedereen kan leren, bijdragen en verbeteren.  

📖 Meer info over de licentie: [EUPL officiële tekst](https://joinup.ec.europa.eu/collection/eupl/eupl-text-eupl-12)  

## ℹ️ Transparantieverklaring

Delen van deze documentatie zijn mede opgesteld met behulp van **ChatGPT (AI-taalmodel van OpenAI)**.  
De inhoud is door een menselijke beheerder gecontroleerd en aangepast waar nodig.  
