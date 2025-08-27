import streamlit as st
import pandas as pd
from datetime import datetime, time as dt_time
from icalendar import Calendar, Event
import zipfile
import re
import traceback
from time import perf_counter

NL_WEEKDAYS = {
    "Monday":"maandag","Tuesday":"dinsdag","Wednesday":"woensdag",
    "Thursday":"donderdag","Friday":"vrijdag","Saturday":"zaterdag","Sunday":"zondag"
}
NL_MONTHS = {
    "January":"januari","February":"februari","March":"maart","April":"april",
    "May":"mei","June":"juni","July":"juli","August":"augustus",
    "September":"september","October":"oktober","November":"november","December":"december"
}

# ===============================================================
# PAGINA-INSTELLINGEN (altijd helemaal bovenaan laten staan)
# ===============================================================
st.set_page_config(page_title="Rooster Omzetter", page_icon="📅", layout="wide")

# ===============================================================
# EIGEN STIJL (CSS) – uiterlijk van de app
# ===============================================================
st.markdown("""
    <style>
    .main { background-color: #f5f7fa; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
    h1 { color: #2c3e50; text-align: center; }
    h2 { color: #34495e; }
    .box { background-color: #fff; padding: 1.5rem; margin-bottom: 1.5rem; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
    .sidebar .sidebar-content { background-color: #ecf0f1; padding: 1rem; border-radius: 8px; }
    .stDownloadButton button { background-color: #3498db; color: #fff; border: none; padding: 0.5rem 1rem; border-radius: 5px; }
    pre, code { white-space: pre-wrap; }
    </style>
""", unsafe_allow_html=True)

# ===============================================================
# HULPFUNCTIES VOOR DEBUG / LOGGING
# ===============================================================

# Simpele "aan/uit"-schakelaar voor extra debug-teksten
st.sidebar.markdown("<div class='sidebar'><h3>Instellingen</h3></div>", unsafe_allow_html=True)
debug_mode = st.sidebar.checkbox("Debug-modus (aanbevolen bij problemen)", value=False, help="Toon extra uitleg, tussenstappen en controles.")

def dbg(title, value=None):
    """Toon extra debug-info als de debug-modus aan staat."""
    if debug_mode:
        with st.expander(f"🔎 {title}", expanded=False):
            if value is not None:
                if isinstance(value, (pd.DataFrame, pd.Series)):
                    st.write(value)
                else:
                    st.code(str(value))
            else:
                st.write("OK")

def safe_section(step_title):
    """Contextmanager-achtig patroon voor nette stap-timing in debug."""
    class _Section:
        def __enter__(self_inner):
            self_inner.t0 = perf_counter()
            if debug_mode:
                st.info(f"Start: {step_title}")
        def __exit__(self_inner, exc_type, exc, tb):
            dt = perf_counter() - self_inner.t0
            if exc:
                st.error(f"❌ Fout in '{step_title}': {exc}")
                if debug_mode and tb:
                    st.exception(exc)
            else:
                if debug_mode:
                    st.success(f"Klaar: {step_title} ({dt:.2f}s)")
    return _Section()

# ===============================================================
# HULPFUNCTIES – DATA BEWERKEN (met NL-uitleg in comments)
# ===============================================================
# ---------- NIEUW: sorteren + NL-datum ----------

def to_dt(date_val, dayfirst=True):
    """Altijd robuust naar pandas.Timestamp (datum, geen tijd)."""
    return pd.to_datetime(date_val, dayfirst=dayfirst, errors="coerce").normalize()

def dutch_date_str(ts):
    """Maak 'woensdag 14 maart 2024' van een Timestamp/Date."""
    if isinstance(ts, (pd.Timestamp, datetime)):
        d = ts
    else:
        d = to_dt(ts)
    if pd.isna(d):
        return "onbekende datum"
    s = d.strftime("%A %d %B %Y")
    for en_nl in NL_WEEKDAYS.items():
        s = s.replace(en_nl[0], en_nl[1])
    for en_nl in NL_MONTHS.items():
        s = s.replace(en_nl[0], en_nl[1])
    return s

def sort_df_chronologically(df, column_vars):
    """
    Geef een *kopie* terug die is gesorteerd op datum + starttijd, met hulpkolommen:
    _dt (Timestamp datum), _tstart (datetime tijd, op 1900-01-01).
    """
    out = df.copy()
    out["_dt"] = pd.to_datetime(out[column_vars["Datum"]], dayfirst=True, errors="coerce")
    out["_tstart"] = out[column_vars["Van"]].apply(parse_time)
    # zet _tstart om naar vergelijkbare objecten (Timestamp) voor sort
    out["_tstart"] = out["_tstart"].apply(lambda t: pd.Timestamp.combine(pd.Timestamp("1900-01-01"), t) if pd.notna(t) else pd.NaT)
    out = out.sort_values(["_dt", "_tstart", column_vars["Beschrijving NL"]], kind="mergesort").reset_index(drop=True)
    return out


def split_docenten(docent_cell):
    """
    Doel: maak van één tekstveld met docenten (bijv. 'Piet, Klaas/Anna')
    een lijst met losse docentcodes/namen.
    Scheidingstekens die we herkennen: spatie, komma, slash en puntkomma.
    """
    if isinstance(docent_cell, str):
        parts = re.split(r'[\s,/;]+', docent_cell.strip())
        return [p for p in parts if p]
    return []

def is_allen_only(row, col):
    """
    Controleer of in de docenten-kolom alléén 'allen' staat.
    Waarom belangrijk? 'allen' betekent vaak: geldt voor iedereen.
    """
    teachers = [t.lower() for t in split_docenten(row[col])]
    return "allen" in teachers and len(teachers) == 1

def get_serie_info(row, df, column_vars):
    """
    Zoek in dezelfde dataset naar andere regels met:
    - Dezelfde beschrijving
    - Dezelfde studentengroep
    Handig om in de afspraak-beschrijving te tonen.
    """
    serie_rows = df[(df[column_vars["Beschrijving NL"]] == row[column_vars["Beschrijving NL"]]) &
                    (df[column_vars["Student groep"]] == row[column_vars["Student groep"]])]
    info_lines = []
    for _, srow in serie_rows.iterrows():
        if srow.name != row.name:
            teacher_list = split_docenten(srow[column_vars["Docenten"]])
            teacher_str = ", ".join(teacher_list)
            zaal = srow[column_vars["Zaal"]]
            info_lines.append(f"{teacher_str} (lokaal: {zaal})")
    return info_lines

def autodetect_date_column(df):
    """
    Probeer automatisch te raden welke kolom de datum bevat.
    We testen een paar waardes en kijken of die als datum te parsen zijn.
    """
    for col in df.columns:
        for val in df[col].dropna().astype(str).head(10):
            try:
                pd.to_datetime(val, dayfirst=True)
                return col
            except Exception:
                continue
    return None

def autodetect_time_columns(df):
    """
    Probeer automatisch de tijd-kolommen te vinden.
    We zoeken naar waardes in HH:MM formaat.
    """
    time_candidates = []
    for col in df.columns:
        vals = df[col].dropna().astype(str).head(10)
        count = sum(1 for val in vals if re.match(r'^\d{1,2}:\d{2}$', val.strip()))
        if count >= 3:
            time_candidates.append(col)
    if len(time_candidates) >= 2:
        return time_candidates[0], time_candidates[1]
    elif len(time_candidates) == 1:
        return time_candidates[0], None
    else:
        return None, None

def autodetect_studentgroep(df):
    """Zoek naar een kolomnaam met het woord 'groep'."""
    for col in df.columns:
        if "groep" in col.lower():
            return col
    return None

def autodetect_zaal(df):
    """Zoek naar een kolomnaam met het woord 'zaal'."""
    for col in df.columns:
        if "zaal" in col.lower():
            return col
    return None

def autodetect_beschrijving(df):
    """Zoek naar een kolomnaam met het woord 'beschrijving'."""
    for col in df.columns:
        if "beschrijving" in col.lower():
            return col
    return None

def autodetect_docenten(df):
    """Zoek naar een kolomnaam met het woord 'docent'."""
    for col in df.columns:
        if "docent" in col.lower():
            return col
    return None

def parse_time(time_str):
    """
    Zet tekst zoals '08:30' om naar een tijdobject.
    Als het niet lukt, geven we 00:00 terug en melden we in debug-modus een waarschuwing.
    """
    if isinstance(time_str, str):
        try:
            return datetime.strptime(time_str.strip(), "%H:%M").time()
        except Exception:
            dbg("⚠️ Onverwacht tijdformaat aangetroffen", time_str)
            return dt_time(0, 0)
    elif isinstance(time_str, dt_time):
        return time_str
    else:
        dbg("⚠️ Tijdveld is geen tekst of tijdobject", str(type(time_str)))
        return dt_time(0, 0)

def get_lesson_history(selected_columns, docent, group, current_pos, df_sorted, history_type):
    """
    Bouw een lijst met eerdere/komende lessen voor deze docent + groep.
    LET OP: df_sorted moet al chronologisch gesorteerd en 'vlak' zijn (reset_index).
    current_pos is de *positionele* index (0..n-1) binnen df_sorted.
    """
    lessons = []
    docent_l = (docent or "").strip().lower()

    if history_type == "previous":
        rows = df_sorted.iloc[:current_pos]
    else:
        rows = df_sorted.iloc[current_pos + 1:]

    for _, row in rows.iterrows():
        # Filter op docent + groep
        teachers_in_row = [t.strip().lower() for t in split_docenten(row.get(selected_columns["Docenten"], ""))]
        if docent_l in teachers_in_row and row.get(selected_columns["Student groep"]) == group:
            dt = row.get("_dt")
            besch = row.get(selected_columns["Beschrijving NL"], "")
            lessons.append(f"{besch} , {dutch_date_str(dt)}")

    # Uniek + volgorde behouden
    seen = set()
    uniq = []
    for x in lessons:
        if x not in seen:
            seen.add(x)
            uniq.append(x)
    return uniq


# ===============================================================
# ICS-GENERATIE (als bytes teruggeven) – met extra checks
# ===============================================================
def generate_ics_bytes(docent, df_filtered, df_full, column_vars, include_allen_var):
    """
    Maak één agenda-bestand (ICS) voor een docent.
    - df_filtered: gefilterde rijen (hier gelijk aan df_full, maar laten staan voor later)
    - df_full: hele dataset (gebruiken we om serie-informatie te zoeken)
    - column_vars: kolomnamen die de gebruiker heeft gekozen
    - include_allen_var: of we 'allen'-events ook willen toevoegen
    Geeft bytes terug (inhoud van het ICS-bestand) of None als er iets misgaat.
    """
    try:
        docent_lower = docent.lower()

        base_sorted = sort_df_chronologically(df_full, column_vars)
        
        teacher_df = base_sorted[base_sorted.apply(
            lambda row: docent_lower in [t.lower() for t in split_docenten(row[column_vars["Docenten"]])]
                        and not is_allen_only(row, column_vars["Docenten"]),
            axis=1
        )].reset_index(drop=True)


        dbg(f"Docentfilter toegepast voor '{docent}'", f"Aantal regels: {len(teacher_df)}")

        cal = Calendar()
        cal.add("version", "2.0")
        cal.add("prodid", "-//Rooster Omzetter//NONSGML v1.0//NL")

        # --- Docent-specifieke regels verwerken
        for pos, row in teacher_df.iterrows():
            try:
                datum_parsed = to_dt(row[column_vars["Datum"]]).date()
                van_tijd = parse_time(row[column_vars["Van"]])
                tot_tijd = parse_time(row[column_vars["Tot"]])
                dtstart = datetime.combine(datum_parsed, van_tijd)
                dtend = datetime.combine(datum_parsed, tot_tijd)
        
                event = Event()
                teacher_list = split_docenten(row[column_vars["Docenten"]])
                teacher_str = ", ".join(teacher_list)
                event_summary = f"{row[column_vars['Beschrijving NL']]} - {teacher_str}"
                event.add("summary", event_summary)
                event.add("dtstart", dtstart)
                event.add("dtend", dtend)
        
                description = f"{row[column_vars['Beschrijving NL']]} - Groep: {row[column_vars['Student groep']]}"
                description += f"\nLokaal: {row[column_vars['Zaal']]}"
        
                prev_lessons = get_lesson_history(column_vars, docent, row[column_vars["Student groep"]], pos, teacher_df, "previous")
                fut_lessons  = get_lesson_history(column_vars, docent, row[column_vars["Student groep"]], pos, teacher_df, "future")
                if prev_lessons:
                    description += "\n\nVorige lessen:\n" + "\n".join(prev_lessons)
                if fut_lessons:
                    description += "\n\nToekomstige lessen:\n" + "\n".join(fut_lessons)
        
                serie_info = get_serie_info(row, base_sorted, column_vars)
                if serie_info:
                    description += "\n\nAndere lessen in deze serie:\n" + "\n".join(serie_info)
        
                event.add("description", description)
                cal.add_component(event)
        
            except Exception as inner_e:
                st.warning(f"Regel overgeslagen (pos={pos}) door fout: {inner_e}")
                if debug_mode:
                    st.code(traceback.format_exc())


        # --- Eventuele 'allen'-regels meenemen (alleen als gebruiker dat wil)
        if include_allen_var:
            allen_df = base_sorted[base_sorted.apply(
                lambda row: is_allen_only(row, column_vars["Docenten"]),
                axis=1
            )].reset_index(drop=True)
            dbg("Aantal 'allen'-regels", len(allen_df))
        
            for pos, row in allen_df.iterrows():
                try:
                    # Als gebruiker in de sidebar een regel heeft uitgezet, overslaan
                    if "allen_inclusion" in st.session_state and not st.session_state.allen_inclusion.get(idx, True):
                        dbg("Allen-regel uitgesloten door gebruiker", idx)
                        continue

                    datum = row[column_vars["Datum"]]
                    van_tijd = parse_time(row[column_vars["Van"]])
                    tot_tijd = parse_time(row[column_vars["Tot"]])
                    datum_parsed = pd.to_datetime(datum, dayfirst=True).date()
                    dtstart = datetime.combine(datum_parsed, van_tijd)
                    dtend = datetime.combine(datum_parsed, tot_tijd)

                    event = Event()
                    teacher_list = split_docenten(row[column_vars["Docenten"]])
                    teacher_str = ", ".join(teacher_list)
                    event_summary = f"{row[column_vars['Beschrijving NL']]} - {teacher_str}"
                    event.add("summary", event_summary)
                    event.add("dtstart", dtstart)
                    event.add("dtend", dtend)

                    description = f"{row[column_vars['Beschrijving NL']]} - Groep: {row[column_vars['Student groep']]}"
                    description += f"\nLokaal: {row[column_vars['Zaal']]}"

                     prev_lessons = get_lesson_history(column_vars, "allen", row[column_vars["Student groep"]], pos, allen_df, "previous")
                     fut_lessons  = get_lesson_history(column_vars, "allen", row[column_vars["Student groep"]], pos, allen_df, "future")
                                # ... (rest ongewijzigd)
                    if prev_lessons:
                        description += "\n\nVorige lessen:\n" + "\n".join(prev_lessons)
                    if fut_lessons:
                        description += "\n\nToekomstige lessen:\n" + "\n".join(fut_lessons)
                    serie_info = get_serie_info(row, df_full, column_vars)
                    if serie_info:
                        description += "\n\nAndere lessen in deze serie:\n" + "\n".join(serie_info)

                    event.add("description", description)
                    cal.add_component(event)

                except Exception as inner_e:
                    st.warning(f"'Allen'-regel overgeslagen (idx={idx}) door fout: {inner_e}")
                    if debug_mode:
                        st.code(traceback.format_exc())

        # Geef de ICS-inhoud als bytes terug
        ics_bytes = cal.to_ical()
        dbg("ICS-bytes gegenereerd (lengte)", len(ics_bytes))
        return ics_bytes

    except Exception as e:
        st.error(f"Er is een fout opgetreden voor docent {docent}:\n{e}")
        if debug_mode:
            st.code(traceback.format_exc())
        return None

# ===============================================================
# CACHES – om sneller te werken bij herhaald uitvoeren
# ===============================================================
@st.cache_data(show_spinner=False)
def load_excel(file):
    """Lees het Excel-bestand in als DataFrame."""
    return pd.read_excel(file)

@st.cache_data(show_spinner=False)
def cached_generate_ics_bytes(docent, df, column_vars, include_allen_var):
    """Cache per docent de gegenereerde ICS-bytes."""
    return generate_ics_bytes(docent, df, df, column_vars, include_allen_var)

# ===============================================================
# HOOFD-INTERFACE VAN DE APP
# ===============================================================
st.title("Rooster Omzetter 📅")
st.markdown("""
**Welkom!**  
Deze tool zet een Excel-rooster om naar agenda-afspraken (ICS-bestanden) die je kunt importeren in je agenda (Outlook, Google Calendar, Apple Calendar, etc.).
Volg de stappen hieronder.
""")
st.markdown("---")

# ---------- Stap 1: Upload ----------
with safe_section("Excel uploaden en inlezen"):
    with st.expander("Stap 1: Upload je Excel-bestand", expanded=True):
        st.info("Upload een Excel-bestand (.xlsx) met het rooster.")
        uploaded_file = st.file_uploader("Kies je Excel-bestand", type="xlsx")
        df = None
        if uploaded_file:
            with st.spinner("Excel-bestand laden..."):
                df = load_excel(uploaded_file)
            st.success("Excel-bestand succesvol geladen!")
            dbg("Eerste 5 rijen van de data", df.head())
            dbg("Kolomnamen", list(df.columns))
            dbg("Vorm (rows, columns)", df.shape)

# ---------- Stap 2: Kolommen ----------
column_vars = {}
columns_set = False
if df is not None:
    with safe_section("Kolommen herkennen en kiezen"):
        st.markdown("## Stap 2: Kolominstellingen")
        st.write("We proberen de kolommen automatisch te herkennen. Controleer en pas aan indien nodig.")

        detected_datum       = autodetect_date_column(df)
        detected_van, detected_tot = autodetect_time_columns(df)
        detected_studentgroep = autodetect_studentgroep(df)
        detected_zaal         = autodetect_zaal(df)
        detected_beschrijving = autodetect_beschrijving(df)
        detected_docenten     = autodetect_docenten(df)

        dbg("Automatisch gedetecteerd", {
            "Datum": detected_datum,
            "Van": detected_van,
            "Tot": detected_tot,
            "Student groep": detected_studentgroep,
            "Zaal": detected_zaal,
            "Beschrijving NL": detected_beschrijving,
            "Docenten": detected_docenten
        })

        available_columns = df.columns.tolist()
        with st.container():
            st.markdown('<div class="box">', unsafe_allow_html=True)
            column_vars["Datum"] = st.selectbox("Kolom voor **Datum**", options=available_columns,
                index=available_columns.index(detected_datum) if detected_datum in available_columns else 0)
            column_vars["Van"] = st.selectbox("Kolom voor **Van** (starttijd)", options=available_columns,
                index=available_columns.index(detected_van) if detected_van in available_columns else 0)
            column_vars["Tot"] = st.selectbox("Kolom voor **Tot** (eindtijd)", options=available_columns,
                index=available_columns.index(detected_tot) if detected_tot in available_columns else 0)
            column_vars["Student groep"] = st.selectbox("Kolom voor **Student groep**", options=available_columns,
                index=available_columns.index(detected_studentgroep) if detected_studentgroep in available_columns else 0)
            column_vars["Zaal"] = st.selectbox("Kolom voor **Zaal**", options=available_columns,
                index=available_columns.index(detected_zaal) if detected_zaal in available_columns else 0)
            column_vars["Beschrijving NL"] = st.selectbox("Kolom voor **Beschrijving NL**", options=available_columns,
                index=available_columns.index(detected_beschrijving) if detected_beschrijving in available_columns else 0)
            column_vars["Docenten"] = st.selectbox("Kolom voor **Docenten**", options=available_columns,
                index=available_columns.index(detected_docenten) if detected_docenten in available_columns else 0)
            st.markdown('</div>', unsafe_allow_html=True)

        if all(col in available_columns for col in column_vars.values()):
            st.success("Alle benodigde kolommen zijn toegewezen!")
            columns_set = True
        else:
            st.error("Niet alle kolommen zijn correct toegewezen. Controleer de kolominstellingen.")

# ---------- Extra instellingen ----------
# Locatie en vorige/toekomstige lessen worden standaard meegenomen; aparte toggles kun je later toevoegen.
include_allen_var = st.sidebar.checkbox("Evenementen voor 'allen' opnemen", value=False, key="include_allen",
                                        help="Zet aan om algemene ('allen') afspraken ook te maken.")

# Toon en laat individuele 'allen'-rigen aan/uit zetten
if include_allen_var and df is not None and columns_set:
    with safe_section("'Allen'-evenementen voorbereiden"):
        allen_rows = df[df.apply(lambda row: is_allen_only(row, column_vars["Docenten"]), axis=1)]
        with st.sidebar.expander("Evenementen voor 'allen' – selecteer welke je wil opnemen"):
            st.write(f"Gevonden {allen_rows.shape[0]} evenementen voor 'allen'.")
            allen_inclusion = {}
            for idx, row in allen_rows.iterrows():
                corrected_location = row[column_vars["Zaal"]]
                if pd.isna(corrected_location) or corrected_location == "":
                    corrected_location = "Onbekend"
                label = f"{row[column_vars['Datum']]} {row[column_vars['Van']]}-{row[column_vars['Tot']]} - {row[column_vars['Beschrijving NL']]}"
                allen_inclusion[idx] = st.checkbox(label, value=True, key=f"allen_inclusion_{idx}")
                st.text_input("Locatie", value=corrected_location, key=f"allen_loc_{idx}")
            st.session_state.allen_inclusion = allen_inclusion
        dbg("'Allen' voorbeeldregels (max 5)", allen_rows.head())

# ---------- Stap 3: Docenten kiezen ----------
selected_docenten = []
if df is not None and columns_set:
    with safe_section("Docentenlijst opbouwen en selectie"):
        st.markdown("## Stap 3: Selecteer de docent(en)")
        st.write("Kies voor welke docent(en) je een agenda-bestand wilt maken.")
        docenten_set = set()
        for cell in df[column_vars["Docenten"]].dropna().astype(str):
            for teacher in split_docenten(cell):
                docenten_set.add(teacher.strip().lower())
        docenten = sorted(docenten_set)
        st.write("Gevonden docenten:", ", ".join(docenten) if docenten else "— niets gevonden —")
        selected_docenten = st.multiselect("Kies docent(en)", docenten)
        if selected_docenten:
            st.success("Docenten geselecteerd!")
        else:
            dbg("Geen docenten geselecteerd", None)

# ---------- Stap 4: ICS downloaden ----------
if df is not None and selected_docenten:
    with safe_section("ICS genereren en downloadknoppen tonen"):
        st.markdown("## Stap 4: Download agenda-bestanden")
        st.write("Download losse bestanden per docent of alles samen als ZIP.")

        ics_dict = {}
        for docent in selected_docenten:
            with st.spinner(f"Genereer ICS voor {docent}..."):
                ics_bytes = cached_generate_ics_bytes(docent, df, column_vars, include_allen_var)
            if ics_bytes:
                ics_dict[docent] = ics_bytes
                st.download_button(
                    label=f"Download agenda voor {docent}",
                    data=ics_bytes,
                    file_name=f"{docent}.ics",
                    mime="application/ics"
                )
            else:
                st.warning(f"Geen ICS gegenereerd voor {docent}. Check de debug-info hierboven.")

        # Alles in één ZIP
        try:
            zip_file_path = "/tmp/docenten_ics.zip"
            with zipfile.ZipFile(zip_file_path, "w") as zipf:
                for docent, ics_bytes in ics_dict.items():
                    zipf.writestr(f"{docent}.ics", ics_bytes)
            with open(zip_file_path, "rb") as f:
                st.download_button(
                    label="Download alle agenda-bestanden als ZIP",
                    data=f.read(),
                    file_name="alle_docenten.ics.zip",
                    mime="application/zip"
                )
            dbg("ZIP samengesteld met docenten", list(ics_dict.keys()))
        except Exception as e:
            st.error(f"Er is een fout opgetreden bij het maken van het ZIP-bestand:\n{e}")
            if debug_mode:
                st.code(traceback.format_exc())

# ===============================================================
# TIPS BIJ TIMEOUTS / SERVER-INSTELLINGEN
# ===============================================================
st.caption("""
Als je een **AxiosError: timeout exceeded** ziet in de front-end:
- Verhoog de timeout in je front-end (bijv. `axios.defaults.timeout = 120000` voor 2 min).
- Controleer ook eventuele timeouts in je reverse-proxy of server (bijv. Nginx/Cloudflare).
""")
