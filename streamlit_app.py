import streamlit as st
import pandas as pd
from datetime import datetime, time as dt_time
from icalendar import Calendar, Event
import zipfile
import re
import traceback
from time import perf_counter

# NL naam-mapping
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
# PAGINA-INSTELLINGEN
# ===============================================================
st.set_page_config(page_title="Rooster Omzetter", page_icon="📅", layout="wide")

# ===============================================================
# EIGEN STIJL (CSS)
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
# DEBUG FUNCTIES
# ===============================================================
st.sidebar.markdown("<div class='sidebar'><h3>Instellingen</h3></div>", unsafe_allow_html=True)
debug_mode = st.sidebar.checkbox("Debug-modus (aanbevolen bij problemen)", value=False)

def dbg(title, value=None):
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
    class _Section:
        def __enter__(self_inner):
            self_inner.t0 = perf_counter()
            if debug_mode: st.info(f"Start: {step_title}")
        def __exit__(self_inner, exc_type, exc, tb):
            dt = perf_counter() - self_inner.t0
            if exc:
                st.error(f"❌ Fout in '{step_title}': {exc}")
                if debug_mode and tb: st.exception(exc)
            else:
                if debug_mode: st.success(f"Klaar: {step_title} ({dt:.2f}s)")
    return _Section()

# ===============================================================
# HULPFUNCTIES DATA
# ===============================================================
def to_dt(date_val, dayfirst=True):
    return pd.to_datetime(date_val, dayfirst=True, errors="coerce").normalize()

def dutch_date_str(ts):
    if isinstance(ts, (pd.Timestamp, datetime)): d = ts
    else: d = to_dt(ts)
    if pd.isna(d): return "onbekende datum"
    s = d.strftime("%A %d %B %Y")
    for en, nl in NL_WEEKDAYS.items(): s = s.replace(en, nl)
    for en, nl in NL_MONTHS.items(): s = s.replace(en, nl)
    return s

def parse_time(time_str):
    if isinstance(time_str, str):
        try: return datetime.strptime(time_str.strip(), "%H:%M").time()
        except Exception:
            dbg("⚠️ Onverwacht tijdformaat aangetroffen", time_str)
            return dt_time(0, 0)
    elif isinstance(time_str, dt_time): return time_str
    else:
        dbg("⚠️ Tijdveld is geen tekst of tijdobject", str(type(time_str)))
        return dt_time(0, 0)

def split_docenten(docent_cell):
    if isinstance(docent_cell, str):
        parts = re.split(r'[\s,/;]+', docent_cell.strip())
        return [p for p in parts if p]
    return []

def is_allen_only(row, col):
    teachers = [t.lower() for t in split_docenten(row[col])]
    return "allen" in teachers and len(teachers) == 1

def sort_df_chronologically(df, column_vars):
    out = df.copy()
    out["orig_idx"] = df.index
    out["_dt"] = pd.to_datetime(out[column_vars["Datum"]], dayfirst=True, errors="coerce")
    out["_tstart"] = out[column_vars["Van"]].apply(parse_time)
    out["_tstart"] = out["_tstart"].apply(
        lambda t: pd.Timestamp.combine(pd.Timestamp("1900-01-01"), t) if pd.notna(t) else pd.NaT
    )
    out = out.sort_values(["_dt", "_tstart", column_vars["Beschrijving NL"]], kind="mergesort").reset_index(drop=True)
    return out

# ---- Serie-sleutel uit beschrijving (heuristisch) ----
_SERIES_RX = re.compile(r'\b([ivxlcdm]+|\d+)\b$', re.IGNORECASE)

def series_key_from_desc(desc: str) -> str:
    """
    Maak een serie-sleutel op basis van de beschrijving:
    - lowercase
    - verwijder eventueel trailing nummer of Romeins cijfer (I, II, III, IV, V, ...)
    - trim spaties
    Voorbeeld: "Anamnesetraining 5" -> "anamnesetraining"
    """
    if not isinstance(desc, str):
        return ""
    s = desc.strip().lower()
    # strip één trailing nummer/romeins cijfer
    s = _SERIES_RX.sub("", s).strip()
    # normaliseer dubbele spaties
    s = re.sub(r'\s+', ' ', s)
    return s

def get_future_series_teachers(row, df, column_vars):
    """
    Voor dezelfde SERIE (op basis van serie-sleutel) + zelfde groep:
    toon toekomstige lessen (na dit event), met datum, beschrijving en docent(en).
    """
    cur_dt = row.get("_dt")
    if pd.isna(cur_dt):
        cur_dt = pd.to_datetime(row[column_vars["Datum"]], dayfirst=True, errors="coerce")

    # serie-sleutel huidige rij
    cur_key = series_key_from_desc(row[column_vars["Beschrijving NL"]])

    # serie-sleutel voor alle rijen
    all_keys = df[column_vars["Beschrijving NL"]].astype(str).apply(series_key_from_desc)

    same_series = all_keys == cur_key
    same_grp    = df[column_vars["Student groep"]] == row[column_vars["Student groep"]]
    future      = df["_dt"] > cur_dt

    serie_rows = df[same_series & same_grp & future]

    lines, seen = [], set()
    for _, srow in serie_rows.iterrows():
        dt = srow.get("_dt")
        if pd.isna(dt):
            dt = pd.to_datetime(srow[column_vars["Datum"]], dayfirst=True, errors="coerce")
        date_txt = dutch_date_str(dt)
        besch    = str(srow[column_vars["Beschrijving NL"]]).strip()
        teacher_list = split_docenten(srow[column_vars["Docenten"]])
        teacher_str  = ", ".join(teacher_list) if teacher_list else "onbekend"
        zaal         = srow[column_vars["Zaal"]]
        line = f"{date_txt} – {besch} – {teacher_str} (lokaal: {zaal})"
        if line not in seen:
            seen.add(line)
            lines.append(line)
    return lines

def autodetect_date_column(df):
    for col in df.columns:
        for val in df[col].dropna().astype(str).head(10):
            try:
                pd.to_datetime(val, dayfirst=True)
                return col
            except: continue
    return None

def autodetect_time_columns(df):
    time_candidates = []
    for col in df.columns:
        vals = df[col].dropna().astype(str).head(10)
        count = sum(1 for val in vals if re.match(r'^\d{1,2}:\d{2}$', val.strip()))
        if count >= 3: time_candidates.append(col)
    if len(time_candidates) >= 2: return time_candidates[0], time_candidates[1]
    elif len(time_candidates) == 1: return time_candidates[0], None
    else: return None, None

def autodetect_studentgroep(df):
    for col in df.columns:
        if "groep" in col.lower(): return col
    return None

def autodetect_zaal(df):
    for col in df.columns:
        if "zaal" in col.lower(): return col
    return None

def autodetect_beschrijving(df):
    for col in df.columns:
        if "beschrijving" in col.lower(): return col
    return None

def autodetect_docenten(df):
    for col in df.columns:
        if "docent" in col.lower(): return col
    return None

def get_lesson_history(selected_columns, docent, group, current_pos, df_sorted, history_type, current_desc=None):
    """
    Vorige/toekomstige lessen voor dezelfde docent + groep, optioneel
    beperkt tot dezelfde beschrijving (current_desc).
    """
    lessons = []
    docent_l = (docent or "").strip().lower()
    rows = df_sorted.iloc[:current_pos] if history_type=="previous" else df_sorted.iloc[current_pos+1:]
    for _, row in rows.iterrows():
        teachers_in_row = [t.strip().lower() for t in split_docenten(row.get(selected_columns["Docenten"], ""))]
        same_teacher = docent_l in teachers_in_row
        same_group   = row.get(selected_columns["Student groep"]) == group
        same_desc    = (current_desc is None) or (row.get(selected_columns["Beschrijving NL"]) == current_desc)
        if same_teacher and same_group and same_desc:
            dt = row.get("_dt")
            besch = row.get(selected_columns["Beschrijving NL"], "")
            lessons.append(f"{besch} , {dutch_date_str(dt)}")
    seen, uniq = set(), []
    for x in lessons:
        if x not in seen:
            seen.add(x); uniq.append(x)
    return uniq

# ===============================================================
# ICS-GENERATIE
# ===============================================================
def generate_ics_bytes(docent, df_filtered, df_full, column_vars, include_allen_var):
    try:
        docent_lower = docent.lower()
        base_sorted = sort_df_chronologically(df_full, column_vars)

        teacher_df = base_sorted[base_sorted.apply(
            lambda row: docent_lower in [t.lower() for t in split_docenten(row[column_vars["Docenten"]])]
                        and not is_allen_only(row, column_vars["Docenten"]),
            axis=1
        )].reset_index(drop=True)

        cal = Calendar()
        cal.add("version", "2.0")
        cal.add("prodid", "-//Rooster Omzetter//NONSGML v1.0//NL")

        # Docent-specifiek
        for pos, row in teacher_df.iterrows():
            try:
                datum_parsed = to_dt(row[column_vars["Datum"]]).date()
                van_tijd, tot_tijd = parse_time(row[column_vars["Van"]]), parse_time(row[column_vars["Tot"]])
                dtstart, dtend = datetime.combine(datum_parsed, van_tijd), datetime.combine(datum_parsed, tot_tijd)

                event = Event()
                teacher_str = ", ".join(split_docenten(row[column_vars["Docenten"]]))
                event.add("summary", f"{row[column_vars['Beschrijving NL']]} - {teacher_str}")
                event.add("dtstart", dtstart); event.add("dtend", dtend)

                description = f"{row[column_vars['Beschrijving NL']]} - Groep: {row[column_vars['Student groep']]}"
                description += f"\nLokaal: {row[column_vars['Zaal']]}"

                current_desc = row[column_vars["Beschrijving NL"]]
                prev_lessons = get_lesson_history(column_vars, docent, row[column_vars["Student groep"]],
                                                  pos, teacher_df, "previous", current_desc)
                fut_lessons  = get_lesson_history(column_vars, docent, row[column_vars["Student groep"]],
                                                  pos, teacher_df, "future", current_desc)
                if prev_lessons: description += "\n\nVorige lessen:\n" + "\n".join(prev_lessons)
                if fut_lessons:  description += "\n\nToekomstige lessen:\n" + "\n".join(fut_lessons)

                serie_future = get_future_series_teachers(row, base_sorted, column_vars)
                if serie_future:
                    description += "\n\nAndere lessen in deze serie (komend, met docent):\n" + "\n".join(serie_future)

                event.add("description", description); cal.add_component(event)
            except Exception as inner_e:
                st.warning(f"Regel overgeslagen (pos={pos}) door fout: {inner_e}")
                if debug_mode: st.code(traceback.format_exc())

        # 'Allen'-regels (optioneel)
        if include_allen_var:
            allen_df = base_sorted[base_sorted.apply(
                lambda row: is_allen_only(row, column_vars["Docenten"]), axis=1
            )].reset_index(drop=True)

            for pos, row in allen_df.iterrows():
                try:
                    orig_idx = row.get("orig_idx", None)
                    if "allen_inclusion" in st.session_state and orig_idx is not None:
                        if not st.session_state.allen_inclusion.get(orig_idx, True):
                            continue

                    datum_parsed = to_dt(row[column_vars["Datum"]]).date()
                    van_tijd, tot_tijd = parse_time(row[column_vars["Van"]]), parse_time(row[column_vars["Tot"]])
                    dtstart, dtend = datetime.combine(datum_parsed, van_tijd), datetime.combine(datum_parsed, tot_tijd)

                    event = Event()
                    teacher_str = ", ".join(split_docenten(row[column_vars["Docenten"]]))
                    event.add("summary", f"{row[column_vars['Beschrijving NL']]} - {teacher_str}")
                    event.add("dtstart", dtstart); event.add("dtend", dtend)

                    description = f"{row[column_vars['Beschrijving NL']]} - Groep: {row[column_vars['Student groep']]}"
                    description += f"\nLokaal: {row[column_vars['Zaal']]}"

                    current_desc = row[column_vars["Beschrijving NL"]]
                    prev_lessons = get_lesson_history(column_vars, "allen", row[column_vars["Student groep"]],
                                                      pos, allen_df, "previous", current_desc)
                    fut_lessons  = get_lesson_history(column_vars, "allen", row[column_vars["Student groep"]],
                                                      pos, allen_df, "future", current_desc)
                    if prev_lessons: description += "\n\nVorige lessen:\n" + "\n".join(prev_lessons)
                    if fut_lessons:  description += "\n\nToekomstige lessen:\n" + "\n".join(fut_lessons)

                    serie_future = get_future_series_teachers(row, base_sorted, column_vars)
                    if serie_future:
                        description += "\n\nAndere lessen in deze serie (komend, met docent):\n" + "\n".join(serie_future)

                    event.add("description", description); cal.add_component(event)
                except Exception as inner_e:
                    st.warning(f"'Allen'-regel overgeslagen (pos={pos}) door fout: {inner_e}")
                    if debug_mode: st.code(traceback.format_exc())

        return cal.to_ical()

    except Exception as e:
        st.error(f"Er is een fout opgetreden voor docent {docent}:\n{e}")
        if debug_mode: st.code(traceback.format_exc())
        return None

# ===============================================================
# CACHE
# ===============================================================
@st.cache_data(show_spinner=False)
def load_excel(file): return pd.read_excel(file)

@st.cache_data(show_spinner=False)
def cached_generate_ics_bytes(docent, df, column_vars, include_allen_var):
    return generate_ics_bytes(docent, df, df, column_vars, include_allen_var)

# ===============================================================
# UI
# ===============================================================
st.title("Rooster Omzetter 📅")
st.markdown("""
**Welkom!**  
Deze tool zet een Excel-rooster om naar ICS-agendagegevens.
""")
st.markdown("---")

# Upload
with safe_section("Excel uploaden en inlezen"):
    with st.expander("Stap 1: Upload je Excel-bestand", expanded=True):
        uploaded_file = st.file_uploader("Kies je Excel-bestand", type="xlsx")
        df = None
        if uploaded_file:
            df = load_excel(uploaded_file)
            st.success("Excel-bestand succesvol geladen!")
            dbg("Eerste 5 rijen", df.head()); dbg("Kolommen", list(df.columns))

# Kolommen
column_vars, columns_set = {}, False
if df is not None:
    with safe_section("Kolommen"):
        detected_datum = autodetect_date_column(df)
        detected_van, detected_tot = autodetect_time_columns(df)
        detected_studentgroep, detected_zaal = autodetect_studentgroep(df), autodetect_zaal(df)
        detected_beschrijving, detected_docenten = autodetect_beschrijving(df), autodetect_docenten(df)
        available_columns = df.columns.tolist()
        with st.container():
            st.markdown('<div class="box">', unsafe_allow_html=True)
            column_vars["Datum"] = st.selectbox("Kolom Datum", available_columns,
                index=available_columns.index(detected_datum) if detected_datum in available_columns else 0)
            column_vars["Van"] = st.selectbox("Kolom Van (starttijd)", available_columns,
                index=available_columns.index(detected_van) if detected_van in available_columns else 0)
            column_vars["Tot"] = st.selectbox("Kolom Tot (eindtijd)", available_columns,
                index=available_columns.index(detected_tot) if detected_tot in available_columns else 0)
            column_vars["Student groep"] = st.selectbox("Kolom Student groep", available_columns,
                index=available_columns.index(detected_studentgroep) if detected_studentgroep in available_columns else 0)
            column_vars["Zaal"] = st.selectbox("Kolom Zaal", available_columns,
                index=available_columns.index(detected_zaal) if detected_zaal in available_columns else 0)
            column_vars["Beschrijving NL"] = st.selectbox("Kolom Beschrijving NL", available_columns,
                index=available_columns.index(detected_beschrijving) if detected_beschrijving in available_columns else 0)
            column_vars["Docenten"] = st.selectbox("Kolom Docenten", available_columns,
                index=available_columns.index(detected_docenten) if detected_docenten in available_columns else 0)
            st.markdown('</div>', unsafe_allow_html=True)
        if all(col in available_columns for col in column_vars.values()):
            st.success("Kolommen toegewezen!"); columns_set = True
        else:
            st.error("Niet alle kolommen zijn correct toegewezen. Controleer de kolominstellingen.")

# Extra instellingen
include_allen_var = st.sidebar.checkbox("Evenementen voor 'allen' opnemen", value=False, key="include_allen")

# 'Allen' selectie (op basis van originele df-indexen)
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

# Docenten kiezen
selected_docenten = []
if df is not None and columns_set:
    with safe_section("Docentenlijst opbouwen en selectie"):
        st.markdown("## Selecteer docent(en)")
        docenten_set = set()
        for cell in df[column_vars["Docenten"]].dropna().astype(str):
            for teacher in split_docenten(cell):
                docenten_set.add(teacher.strip().lower())
        docenten = sorted(docenten_set)
        st.write("Gevonden docenten:", ", ".join(docenten) if docenten else "— niets gevonden —")
        selected_docenten = st.multiselect("Kies docent(en)", docenten)
        if selected_docenten: st.success("Docenten geselecteerd!")

# Download
if df is not None and selected_docenten:
    with safe_section("ICS genereren en downloadknoppen tonen"):
        st.markdown("## Download agenda-bestanden")
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

        # Alles in een ZIP
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
            if debug_mode: st.code(traceback.format_exc())

# Tips
st.caption("""
Als je een **AxiosError: timeout exceeded** ziet in de front-end:
- Verhoog de timeout in je front-end (bijv. `axios.defaults.timeout = 120000`).
- Controleer ook eventuele timeouts in je reverse-proxy of server (bijv. Nginx/Cloudflare).
""")
