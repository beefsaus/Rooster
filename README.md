Rooster Omzetter 📅

Een gebruiksvriendelijke Streamlit-app die een Excel-rooster (.xlsx) automatisch omzet naar agenda-afspraken (ICS-bestanden) per docent.

Handig om snel en foutloos roosters te importeren in Outlook, Google Calendar of Apple Calendar.


---

✨ Functies

✅ Upload een Excel-bestand met je rooster
✅ Automatische herkenning van kolommen (handmatig aanpassen kan ook)
✅ Selecteer één of meerdere docenten
✅ Exporteer afspraken naar ICS (per docent of alles in één ZIP)
✅ Optioneel: voeg afspraken toe die gelden voor ‘allen’
✅ Debug-modus beschikbaar om fouten snel te vinden


---

🧰 Benodigdheden

Python 3.9 of hoger

Pakketten:

streamlit

pandas

icalendar

openpyxl



Installeer alles eenvoudig met:

pip install -U streamlit pandas icalendar openpyxl


---

🚀 Snel starten (lokaal draaien)

1. Download of kloon de repository en open een terminal in de map.

git clone <repository-url>
cd <repository-map>


2. Maak een virtuele omgeving (aanbevolen):

# macOS / Linux
python -m venv .venv
source .venv/bin/activate

# Windows (PowerShell)
python -m venv .venv
.venv\Scripts\Activate.ps1


3. Installeer alle vereisten:

pip install -U streamlit pandas icalendar openpyxl


4. Start de app:

streamlit run app.py


5. Open de link die Streamlit toont (meestal http://localhost:8501).




---

📂 Excel-indeling (tips)

De app probeert kolommen automatisch te herkennen. Controleer deze altijd in de interface en pas indien nodig aan.

Handige kolomnamen (hoeven niet exact zo te zijn):

Datum → datum van de les (bijv. 23-08-2025)

Van → starttijd (HH:MM, bijv. 08:30)

Tot → eindtijd (HH:MM, bijv. 10:15)

Student groep → groep/klas

Zaal → lokaal/ruimte

Beschrijving NL → vak of omschrijving

Docenten → docent(en), scheiden met spatie/komma/slash/semicolon (Piet, Klaas/Anna)


⚠️ Belangrijk: tijdstippen moeten exact HH:MM zijn. Bijvoorbeeld 09:05 is goed, 9:5 is fout.


---

🧭 Stappenplan gebruik

1. Upload je Excel-bestand (.xlsx)


2. Controleer kolomkoppeling (de app herkent dit vaak automatisch)


3. Kies docent(en) die je wilt exporteren


4. Download ICS (per docent of ZIP met alles)


5. Importeren in je agenda → klaar 🎉




---

⚙️ Extra opties

Evenementen voor ‘allen’ opnemen → handig voor gezamenlijke afspraken

Debug-modus → toont extra info en foutmeldingen



---

🆘 Problemen oplossen

🔹 Alle tijden vallen op 00:00
➡ Controleer of tijden in je Excel exact als HH:MM staan.

🔹 Excel kan niet worden gelezen
➡ Bestand moet .xlsx zijn en het juiste werkblad moet aanwezig zijn. Zorg dat openpyxl is geïnstalleerd.

🔹 Frontend timeouts (AxiosError: timeout exceeded)
➡ Verhoog timeout in je frontend (bijv. axios.defaults.timeout = 120000)
➡ Controleer ook instellingen van je proxy of server (bijv. Nginx, Cloudflare).


---

📦 Voorbeeld ICS importeren

Outlook: dubbelklik op het .ics bestand en klik op Toevoegen aan agenda.

Google Calendar: ga naar Instellingen > Importeren en kies het .ics bestand.

Apple Calendar: open het bestand met de Agenda-app en voeg toe.



---

📄 Licentie

Kies en voeg hier je licentie toe (bijv. MIT).


---

🙌 Credits

Gebouwd met:

Streamlit

Pandas

iCalendar



---

Wil je dat ik ook een Engelse versie van de README maak zodat je project internationaal aantrekkelijker is?

