# Rooster Omzetter ðŸ“…

Eenvoudige Streamlitâ€‘app die een **Excel-rooster (.xlsx)** omzet naar **agendaâ€‘afspraken (ICS)** per docent. Ideaal om lessen snel te importeren in Outlook, Google Calendar of Apple Calendar.

> Gebruik dit bestand als **README.md** in je GitHubâ€‘repository.

---

## âœ¨ Wat kun je ermee?
- Upload een Excelâ€‘bestand met je rooster
- App herkent kolommen automatisch (je kunt ze ook handmatig kiezen)
- Selecteer Ã©Ã©n of meerdere **docenten**
- Genereer **.ics** per docent of alles in **Ã©Ã©n ZIP**
- Optionele opname van afspraken voor **â€˜allenâ€™**
- **Debugâ€‘modus** om problemen sneller te vinden

---

## ðŸ§° Benodigdheden
- **Python 3.9 of hoger**
- Pakketten: `streamlit`, `pandas`, `icalendar`, `openpyxl`

---

## ðŸš€ Snel starten (lokaal)
1) **Kloon of download** deze repo en open een terminal in de map.
2) (Aanbevolen) Maak en activeer een virtual environment:
   ```bash
   # macOS / Linux
   python -m venv .venv
   source .venv/bin/activate

   # Windows (PowerShell)
   python -m venv .venv
   .venv\Scripts\Activate.ps1
   ```
3) **Installeer dependencies**:
   ```bash
   pip install -U streamlit pandas icalendar openpyxl
   ```
4) **Start de app**:
   ```bash
   streamlit run app.py
   ```
5) Open de link die Streamlit toont (meestal `http://localhost:8501`).

---

## ðŸ“‚ Excelâ€‘indeling (tips)
De app probeert kolommen automatisch te herkennen. Controleer ze in de UI en pas aan als dat nodig is. Handige kolomnamen (hoeven niet exact zo te heten):
- **Datum** â€“ datum van de les (NL formaat werkt, bijvoorbeeld `23-08-2025`)
- **Van** â€“ starttijd (`HH:MM`, bijv. `08:30`)
- **Tot** â€“ eindtijd (`HH:MM`, bijv. `10:15`)
- **Student groep** â€“ groep/klas
- **Zaal** â€“ lokaal/ruimte
- **Beschrijving NL** â€“ vak of omschrijving
- **Docenten** â€“ Ã©Ã©n of meerdere docenten, scheiden met spatie/komma/slash/semicolon (bijv. `Piet, Klaas/Anna`)

> Tip: tijdstippen moeten als `HH:MM` staan. Onbekende formaten worden als `00:00` gelezen.

---

## ðŸ§­ Werkstroom in 4 stappen
1. **Upload** je Excelâ€‘bestand (.xlsx).  
2. **Controleer kolommen** die automatisch zijn gedetecteerd.  
3. **Selecteer docent(en)** die je wilt exporteren.  
4. **Download ICS** per docent of **ZIP** met alles.

---

## âš™ï¸ Handige opties
- **Evenementen voor â€˜allenâ€™ opnemen**: zet dit aan in de sidebar als algemene afspraken ook gewenst zijn.
- **Debugâ€‘modus**: toont extra controles, tussenstappen en eventuele fouten.

---

## ðŸ†˜ Problemen oplossen
- **Tijdstippen vallen op 00:00** â†’ Controleer of tijden exact `HH:MM` zijn (bijv. `9:5` is fout; gebruik `09:05`).
- **Excel kan niet worden gelezen** â†’ Bestand moet `.xlsx` zijn. Installeer `openpyxl` en controleer of het juiste werkblad wordt gebruikt.
- **Frontend timeouts (AxiosError: timeout exceeded)** â†’ Verhoog de timeout in je frontend (bijv. `axios.defaults.timeout = 120000`) en controleer proxy/serverâ€‘timeouts (Nginx/Cloudflare).

---

## ðŸ“„ Licentie
Kies en voeg hier je licentie toe (bijv. MIT).

---

## ðŸ™Œ Credits
Gemaakt met **Streamlit**, **Pandas** en **iCalendar**.
