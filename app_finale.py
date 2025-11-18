import streamlit as st
from datetime import datetime
from pathlib import Path
import json
import pandas as pd
import os # Necessario per la distribuzione, non per il funzionamento base

# --- config ---
# Usa la cartella data locale (necessaria per il salvataggio locale)
DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)
DATA_FILE = DATA_DIR / "chiusure.json"

st.set_page_config(page_title="Chiusura Conti - Web App", layout="wide")

# Utility: load / save
def load_data():
    """Carica i dati dal file JSON locale."""
    if not DATA_FILE.exists():
        return []
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        # Se il file è vuoto o corrotto
        return []

def save_data(records):
    """Salva i dati nel file JSON locale."""
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)

# Dati base
consumi_items = ["Drink", "Birre", "Analcolico", "Acqua", "Cicchetti"]

# App title
st.title("💰 Chiusura Conti — Web & Condivisione")
st.markdown("Applicazione per registrare la chiusura di serata. Dati salvati localmente (chiusure.json).")

# Inizializzazione per evitare NameError
consumi_data = {item: {"valore": 0.0, "quantita": 0, "totale": 0.0} for item in consumi_items}
note_input = ""

# Form for input
with st.form("form_chiusura"):
    
    # -------------------------------------------------------------------------
    # 1) INCASSI
    st.subheader("1) Incassi (Ingressi, Bar & Guardaroba)")
    
    col_ing1, col_ing2, col_bar, col_guard = st.columns(4)

    with col_ing1:
        st.markdown("**Ingressi Contanti**")
        ing_pren_cont = st.number_input("Prenotati Contanti", min_value=0.0, step=1.0, format="%.2f", key="ing_pren_cont")
        ing_nonpren_cont = st.number_input("Non Prenotati Contanti", min_value=0.0, step=1.0, format="%.2f", key="ing_nonpren_cont")
    
    with col_ing2:
        st.markdown("**Ingressi POS**")
        ing_pos_totale = st.number_input("POS Totale Ingressi", min_value=0.0, step=1.0, format="%.2f", key="ing_pos_totale")

    with col_bar:
        st.markdown("**Bar**")
        bar_cont = st.number_input("Bar Contanti", min_value=0.0, step=1.0, format="%.2f", key="bar_cont")
        bar_pos = st.number_input("Bar POS", min_value=0.0, step=1.0, format="%.2f", key="bar_pos")

    with col_guard:
        st.markdown("**Guardaroba**")
        guard_cont = st.number_input("Guardaroba Contanti", min_value=0.0, step=1.0, format="%.2f", key="guard_cont")
        
    st.markdown("---")

    # -------------------------------------------------------------------------
    # 2) COSTI - LOCALE
    st.subheader("2) Costi Locale (Personale & Fissi)")
    cost_loc_col1, cost_loc_col2 = st.columns(2)
    with cost_loc_col1:
        barman = st.number_input("Barman", min_value=0.0, step=1.0, format="%.2f", key="barman")
        back = st.number_input("Back", min_value=0.0, step=1.0, format="%.2f", key="back")
        cassiera = st.number_input("Cassiera", min_value=0.0, step=1.0, format="%.2f", key="cassiera")
        cassiera_extra = st.number_input("Cassiera Extra", min_value=0.0, step=1.0, format="%.2f", key="cassiera_extra")
    with cost_loc_col2:
        r_sicurezza = st.number_input("R. Sicurezza", min_value=0.0, step=1.0, format="%.2f", key="r_sicurezza")
        siae = st.number_input("SIAE", min_value=0.0, step=1.0, format="%.2f", key="siae")
        tecnico_audio_luci = st.number_input("Tecnico Audio Luci", min_value=0.0, step=1.0, format="%.2f", key="tecnico_audio_luci")
        pulizia = st.number_input("Pulizia", min_value=0.0, step=1.0, format="%.2f", key="pulizia")
        
    st.markdown("---")
    
    # -------------------------------------------------------------------------
    # 3) COSTI - CONSUMI BAR
    st.subheader("3) Consumi Bar (da conteggiare: Valore * Quantità)")
    
    consumato_totale = 0.0
    
    for item in consumi_items:
        cols = st.columns([1, 1, 1, 1])
        with cols[0]:
            st.write(item)
        with cols[1]:
            valore = st.number_input(f"Valore - {item}", min_value=0.0, step=0.01, format="%.2f", key=f"valore_{item.lower()}", label_visibility="collapsed")
        with cols[2]:
            quantita = st.number_input(f"Quantità - {item}", min_value=0, step=1, key=f"quantita_{item.lower()}", label_visibility="collapsed")
        
        totale_riga = valore * quantita
        consumi_data[item] = {"valore": valore, "quantita": quantita, "totale": totale_riga}
        consumato_totale += totale_riga
        
        with cols[3]:
            st.markdown(f"**€ {totale_riga:,.2f}**")

    st.markdown(f"#### Totale Consumi Bar: € {consumato_totale:,.2f}")
    st.markdown("---")

    # -------------------------------------------------------------------------
    # 4) EXTRA COSTI E NOTE
    st.subheader("4) Extra Costi & Note")
    cost_extra_col1, cost_extra_col2 = st.columns(2)
    with cost_extra_col1:
        iva = st.number_input("IVA", min_value=0.0, step=0.01, format="%.2f", key="iva")
        affitto = st.number_input("Affitto", min_value=0.0, step=1.0, format="%.2f", key="affitto")
    with cost_extra_col2:
        note_input = st.text_area("Note (facoltative)", key="note_input")


    submitted = st.form_submit_button("✅ Calcola e Salva Chiusura")

# -----------------------------------------------------------------------------
# CALCULATIONS
# -----------------------------------------------------------------------------

# Totali Incassi
ing_cont_tot = ing_pren_cont + ing_nonpren_cont
tot_ingressi = ing_cont_tot + ing_pos_totale
bar_tot = bar_cont + bar_pos
guard_tot = guard_cont 
incasso_totale = tot_ingressi + bar_tot + guard_tot

# Totale Costi Locale
costi_locale_tot = barman + back + cassiera + cassiera_extra + r_sicurezza + siae + tecnico_audio_luci + pulizia

# Totale Costi Complessivo
costi_totali = costi_locale_tot + consumato_totale + iva + affitto

# Totale dovuto a Vittorio
totale_vittorio = consumato_totale + iva + affitto

# -----------------------------------------------------------------------------
# SHOW RESULTS & SAVE RECORD
# -----------------------------------------------------------------------------

if submitted:
    # 1. Salva Record
    record = {
        "timestamp": datetime.now().isoformat(),
        "incasso_totale": float(incasso_totale),
        "costi_totali": float(costi_totali),
        "totale_vittorio": float(totale_vittorio),
        "ingressi": {
            "pren_cont": float(ing_pren_cont), "nonpren_cont": float(ing_nonpren_cont),
            "pos_totale": float(ing_pos_totale), "tot_ingressi": float(tot_ingressi)
        },
        "bar": {"cont": float(bar_cont), "pos": float(bar_pos), "tot": float(bar_tot)},
        "guardaroba": {"cont": float(guard_cont), "tot": float(guard_tot)},
        "costi_locale": {
            "barman": float(barman), "back": float(back), "cassiera": float(cassiera), "cassiera_extra": float(cassiera_extra),
            "r_sicurezza": float(r_sicurezza), "siae": float(siae), "tecnico_audio_luci": float(tecnico_audio_luci), "pulizia": float(pulizia)
        },
        "consumi_bar": {k: {k2: float(v2) for k2, v2 in v.items()} for k, v in consumi_data.items()},
        "extra_costi": {"iva": float(iva), "affitto": float(affitto)},
        "consumato_totale": float(consumato_totale),
        "note": note_input
    }

    records = load_data()
    records.append(record)
    save_data(records)
    st.success("✅ Chiusura salvata localmente con successo. Ricarica la pagina per vedere i dati aggiornati.")

# 2. Mostra Riepilogo
st.subheader("Riepilogo Calcoli")
colA, colB, colC = st.columns(3)
with colA:
    st.metric("Incasso Totale", f"€ {incasso_totale:,.2f}", delta_color="off")
with colB:
    st.metric("Costi Totali", f"€ {costi_totali:,.2f}", delta_color="off")
with colC:
    st.metric("Totale dovuto a Vittorio", f"€ {totale_vittorio:,.2f}", delta_color="off")

# -----------------------------------------------------------------------------
# SIDEBAR: HISTORY & EXPORT
# -----------------------------------------------------------------------------
st.sidebar.header("Cronologia & Esportazione")
records = load_data()

if records:
    df = pd.json_normalize(records)
    
    df_display = df[['timestamp', 'incasso_totale', 'costi_totali', 'totale_vittorio']].copy()
    df_display.columns = ['Data', 'Incasso Tot', 'Costi Tot', 'TOT. VITTORIO']
    
    df_display["Data"] = pd.to_datetime(df_display["Data"]).dt.strftime('%d/%m %H:%M')
    df_display = df_display.sort_values("Data", ascending=False)
    
    st.sidebar.write(f"Record totali: **{len(df_display)}**")
    st.sidebar.dataframe(df_display.head(5).set_index('Data'))

    # Export options
    csv = df.to_csv(index=False, sep=';', decimal=',')
    json_str = json.dumps(records, ensure_ascii=False, indent=2)
    st.sidebar.download_button("Esporta CSV Completo", csv, file_name="chiusure_complete.csv", mime="text/csv")
    st.sidebar.download_button("Esporta JSON Raw", json_str, file_name="chiusure.json", mime="application/json")
    
    # Clear button
    st.sidebar.markdown("---")
    if st.sidebar.button("🗑️ ELIMINA CRONOLOGIA (ATTENZIONE)"):
        st.sidebar.warning("Sei sicuro? Questa azione è irreversibile.")
        if st.sidebar.checkbox("Confermo di voler eliminare TUTTI i record"):
            save_data([])
            st.rerun()
            
else:
    st.sidebar.info("Nessun record salvato ancora.")