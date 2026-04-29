import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.figure_factory as ff
from datetime import datetime, date
import json
import io
import os

# ─── Configuration de la page ───────────────────────────────────────────────
st.set_page_config(
    page_title="AgriData Analytics",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── CSS personnalisé ────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=DM+Sans:wght@300;400;500;600;700&display=swap');

/* Base */
html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

/* Fond principal */
.main .block-container {
    padding: 1.5rem 2rem 3rem;
    background: #0d1117;
}
.stApp {
    background: #0d1117;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: #0a0f1a;
    border-right: 1px solid #1e3a2f;
}
[data-testid="stSidebar"] .block-container {
    padding-top: 2rem;
}

/* Titres */
h1, h2, h3 {
    font-family: 'Space Mono', monospace;
    color: #4ade80;
}
h1 { font-size: 2rem; letter-spacing: -0.5px; }
h2 { font-size: 1.4rem; }
h3 { font-size: 1.1rem; }

/* Cards KPI */
.kpi-card {
    background: linear-gradient(135deg, #111827 0%, #1a2535 100%);
    border: 1px solid #1e3a2f;
    border-radius: 12px;
    padding: 1.2rem 1.5rem;
    text-align: center;
    transition: border-color 0.2s;
    margin-bottom: 0.5rem;
}
.kpi-card:hover { border-color: #4ade80; }
.kpi-value {
    font-family: 'Space Mono', monospace;
    font-size: 2rem;
    font-weight: 700;
    color: #4ade80;
    line-height: 1;
}
.kpi-label {
    font-size: 0.78rem;
    color: #6b7280;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-top: 0.4rem;
}
.kpi-sub {
    font-size: 0.82rem;
    color: #9ca3af;
    margin-top: 0.2rem;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    background: #111827;
    border-radius: 10px;
    padding: 4px;
    gap: 4px;
    border: 1px solid #1e3a2f;
}
.stTabs [data-baseweb="tab"] {
    color: #6b7280;
    font-family: 'DM Sans', sans-serif;
    font-weight: 500;
    border-radius: 8px;
    padding: 0.5rem 1.2rem;
}
.stTabs [aria-selected="true"] {
    background: #166534 !important;
    color: #4ade80 !important;
}

/* Inputs */
.stTextInput input, .stNumberInput input, .stSelectbox select,
.stDateInput input, .stTextArea textarea {
    background: #111827 !important;
    border: 1px solid #1e3a2f !important;
    color: #e5e7eb !important;
    border-radius: 8px !important;
}
.stTextInput input:focus, .stNumberInput input:focus {
    border-color: #4ade80 !important;
    box-shadow: 0 0 0 2px rgba(74,222,128,0.15) !important;
}

/* Boutons */
.stButton > button {
    background: linear-gradient(135deg, #166534, #15803d);
    color: #fff;
    border: none;
    border-radius: 8px;
    font-weight: 600;
    padding: 0.5rem 1.5rem;
    font-family: 'DM Sans', sans-serif;
    transition: all 0.2s;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #15803d, #16a34a);
    transform: translateY(-1px);
    box-shadow: 0 4px 15px rgba(74,222,128,0.25);
}

/* Dataframe */
.dataframe {
    background: #111827 !important;
    color: #e5e7eb !important;
}

/* Info/Warning/Success */
.stAlert {
    border-radius: 10px;
}

/* Divider */
hr { border-color: #1e3a2f; }

/* Label couleur */
label, .stSelectbox label, .stNumberInput label, .stTextInput label {
    color: #9ca3af !important;
    font-size: 0.85rem !important;
    font-weight: 500 !important;
}

/* Radio */
.stRadio label { color: #e5e7eb !important; }

/* Section header */
.section-header {
    display: flex;
    align-items: center;
    gap: 0.6rem;
    margin: 1.5rem 0 1rem;
    padding-bottom: 0.6rem;
    border-bottom: 1px solid #1e3a2f;
}
.section-icon {
    font-size: 1.3rem;
}
.section-title {
    font-family: 'Space Mono', monospace;
    font-size: 1rem;
    color: #4ade80;
    margin: 0;
}

/* Badge */
.badge {
    display: inline-block;
    background: #166534;
    color: #4ade80;
    padding: 2px 10px;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 600;
    font-family: 'Space Mono', monospace;
}

/* Empty state */
.empty-state {
    text-align: center;
    padding: 3rem;
    color: #4b5563;
    border: 2px dashed #1e3a2f;
    border-radius: 14px;
    margin: 2rem 0;
}
.empty-state .icon { font-size: 3rem; margin-bottom: 1rem; }
</style>
""", unsafe_allow_html=True)

# ─── Données de session ──────────────────────────────────────────────────────
if "records" not in st.session_state:
    st.session_state.records = []

CULTURES = [
    "Maïs", "Manioc", "Cacao", "Café", "Plantain", "Arachide",
    "Tomate", "Sorgho", "Mil", "Riz", "Haricot", "Igname",
    "Patate douce", "Palmier à huile", "Ananas", "Autre"
]

REGIONS_CM = [
    "Centre", "Littoral", "Ouest", "Nord-Ouest", "Sud-Ouest",
    "Est", "Sud", "Adamaoua", "Nord", "Extrême-Nord"
]

SAISONS = ["Grande saison sèche", "Grande saison des pluies",
           "Petite saison sèche", "Petite saison des pluies", "Annuel"]

SOLS = ["Argileux", "Sableux", "Limoneux", "Latéritique", "Volcanique", "Tourbeux", "Mixte"]

IRRIGATION = ["Pluviale (naturelle)", "Irrigation gravitaire", "Goutte-à-goutte",
              "Aspersion", "Submersion", "Mixte"]

# ─── Helpers ─────────────────────────────────────────────────────────────────
def section(icon, title):
    st.markdown(f"""
    <div class="section-header">
      <span class="section-icon">{icon}</span>
      <p class="section-title">{title}</p>
    </div>""", unsafe_allow_html=True)

def kpi(value, label, sub=""):
    st.markdown(f"""
    <div class="kpi-card">
      <div class="kpi-value">{value}</div>
      <div class="kpi-label">{label}</div>
      {"<div class='kpi-sub'>" + sub + "</div>" if sub else ""}
    </div>""", unsafe_allow_html=True)

def get_df():
    if not st.session_state.records:
        return pd.DataFrame()
    return pd.DataFrame(st.session_state.records)

def plotly_theme():
    return dict(
        plot_bgcolor="#0d1117",
        paper_bgcolor="#0d1117",
        font=dict(color="#9ca3af", family="DM Sans"),
        xaxis=dict(gridcolor="#1e3a2f", zerolinecolor="#1e3a2f"),
        yaxis=dict(gridcolor="#1e3a2f", zerolinecolor="#1e3a2f"),
    )

GREEN_PALETTE = ["#4ade80", "#86efac", "#166534", "#22c55e", "#15803d",
                 "#16a34a", "#bbf7d0", "#dcfce7", "#052e16", "#14532d"]

# ─── Sidebar ─────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="text-align:center; padding: 0 0 1.5rem;">
      <div style="font-size:3rem;"></div>
      <div style="font-family:'Space Mono',monospace; color:#4ade80; font-size:1.1rem; font-weight:700;">AgriData</div>
      <div style="color:#6b7280; font-size:0.78rem; margin-top:4px;">Analytics • Cameroun</div>
    </div>
    """, unsafe_allow_html=True)

    nav = st.radio("Navigation", [
        " Saisie des données",
        " Tableau de bord",
        " Analyses statistiques",
        " Analyse spatiale",
        " Export & Import",
    ], label_visibility="collapsed")

    st.divider()

    df_all = get_df()
    n = len(df_all)
    st.markdown(f"""
    <div style="text-align:center;">
      <span class="badge">{n} enregistrement{'s' if n != 1 else ''}</span>
    </div>
    """, unsafe_allow_html=True)

    if n > 0:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button(" Vider toutes les données", use_container_width=True):
            st.session_state.records = []
            st.rerun()

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 1 — SAISIE DES DONNÉES
# ═══════════════════════════════════════════════════════════════════════════════
if nav == " Saisie des données":
    st.markdown("#  Saisie des données agricoles")
    st.markdown("<p style='color:#6b7280; margin-top:-0.5rem;'>Renseignez les informations de votre parcelle / campagne agricole</p>", unsafe_allow_html=True)

    with st.form("saisie_form", clear_on_submit=True):
        # ── Identification ──
        section("", "Identification")
        c1, c2, c3 = st.columns(3)
        with c1:
            nom_agriculteur = st.text_input("Nom de l'agriculteur", placeholder="Ex : Jean Mbarga")
        with c2:
            region = st.selectbox("Région", REGIONS_CM)
        with c3:
            localite = st.text_input("Localité / Village", placeholder="Ex : Obala")

        # ── Parcelle ──
        section("", "Informations sur la parcelle")
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            culture = st.selectbox("Culture principale", CULTURES)
        with c2:
            superficie = st.number_input("Superficie (ha)", min_value=0.01, max_value=10000.0, value=1.0, step=0.1)
        with c3:
            type_sol = st.selectbox("Type de sol", SOLS)
        with c4:
            irrigation_type = st.selectbox("Mode d'irrigation", IRRIGATION)

        c1, c2 = st.columns(2)
        with c1:
            saison = st.selectbox("Saison agricole", SAISONS)
        with c2:
            date_semis = st.date_input("Date de semis", value=date.today())

        # ── Production ──
        section("", "Données de production")
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            rendement = st.number_input("Rendement (kg/ha)", min_value=0.0, max_value=50000.0, value=1000.0, step=50.0)
        with c2:
            production_totale = st.number_input("Production totale (kg)", min_value=0.0, value=0.0, step=10.0)
        with c3:
            cout_production = st.number_input("Coût de production (FCFA)", min_value=0.0, value=50000.0, step=1000.0)
        with c4:
            prix_vente = st.number_input("Prix de vente moyen (FCFA/kg)", min_value=0.0, value=300.0, step=10.0)

        # ── Intrants ──
        section("", "Intrants et ressources")
        c1, c2, c3 = st.columns(3)
        with c1:
            engrais = st.number_input("Engrais utilisé (kg)", min_value=0.0, value=0.0, step=5.0)
            pesticides = st.number_input("Pesticides (litres)", min_value=0.0, value=0.0, step=0.5)
        with c2:
            main_oeuvre = st.number_input("Main-d'œuvre (jours/ha)", min_value=0, value=10, step=1)
            semences = st.number_input("Semences utilisées (kg)", min_value=0.0, value=0.0, step=0.5)
        with c3:
            pluviometrie = st.number_input("Pluviométrie estimée (mm)", min_value=0.0, value=0.0, step=10.0)
            temperature_moy = st.number_input("Température moyenne (°C)", min_value=0.0, max_value=50.0, value=25.0, step=0.5)

        # ── Notes ──
        section("", "Observations")
        notes = st.text_area("Remarques / Observations", placeholder="Conditions particulières, maladies observées, qualité de récolte...", height=80)

        st.markdown("<br>", unsafe_allow_html=True)
        submitted = st.form_submit_button(" Enregistrer la donnée", use_container_width=True)

        if submitted:
            prod = production_totale if production_totale > 0 else rendement * superficie
            revenu_brut = prod * prix_vente
            marge = revenu_brut - cout_production
            record = {
                "Agriculteur": nom_agriculteur or "Anonyme",
                "Région": region,
                "Localité": localite or "-",
                "Culture": culture,
                "Superficie_ha": superficie,
                "Type_sol": type_sol,
                "Irrigation": irrigation_type,
                "Saison": saison,
                "Date_semis": str(date_semis),
                "Rendement_kg_ha": rendement,
                "Production_kg": round(prod, 2),
                "Coût_FCFA": cout_production,
                "Prix_vente_kg": prix_vente,
                "Revenu_brut_FCFA": round(revenu_brut, 2),
                "Marge_FCFA": round(marge, 2),
                "Engrais_kg": engrais,
                "Pesticides_L": pesticides,
                "Main_oeuvre_jours": main_oeuvre,
                "Semences_kg": semences,
                "Pluviometrie_mm": pluviometrie,
                "Temperature_moy_C": temperature_moy,
                "Notes": notes,
                "Enregistré_le": datetime.now().strftime("%Y-%m-%d %H:%M"),
            }
            st.session_state.records.append(record)
            st.success(f" Donnée pour **{culture}** ({region}) enregistrée avec succès !")
            st.balloons()

    # Aperçu rapide
    if st.session_state.records:
        st.divider()
        section("", "Dernières entrées")
        df_preview = pd.DataFrame(st.session_state.records[-5:][::-1])
        cols_show = ["Agriculteur", "Culture", "Région", "Superficie_ha", "Rendement_kg_ha", "Marge_FCFA", "Enregistré_le"]
        st.dataframe(df_preview[cols_show], use_container_width=True, hide_index=True)

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 2 — TABLEAU DE BORD
# ═══════════════════════════════════════════════════════════════════════════════
elif nav == " Tableau de bord":
    st.markdown("#  Tableau de bord")

    df = get_df()
    if df.empty:
        st.markdown("""
        <div class="empty-state">
          <div class="icon"></div>
          <p style="color:#4b5563; font-size:1.1rem;">Aucune donnée disponible</p>
          <p style="color:#374151; font-size:0.85rem;">Commencez par saisir des données agricoles dans l'onglet <strong>Saisie</strong>.</p>
        </div>""", unsafe_allow_html=True)
        st.stop()

    # Filtres sidebar
    with st.sidebar:
        st.divider()
        st.markdown("<p style='color:#9ca3af; font-size:0.8rem; font-weight:600;'>FILTRES</p>", unsafe_allow_html=True)
        f_region = st.multiselect("Région", df["Région"].unique(), default=list(df["Région"].unique()))
        f_culture = st.multiselect("Culture", df["Culture"].unique(), default=list(df["Culture"].unique()))

    dff = df[df["Région"].isin(f_region) & df["Culture"].isin(f_culture)]
    if dff.empty:
        st.warning("Aucun résultat pour les filtres sélectionnés.")
        st.stop()

    # KPIs
    section("", "Indicateurs clés")
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1: kpi(len(dff), "Enregistrements")
    with c2: kpi(f"{dff['Superficie_ha'].sum():.1f}", "Hectares totaux")
    with c3: kpi(f"{dff['Rendement_kg_ha'].mean():.0f}", "Rendement moy. (kg/ha)")
    with c4: kpi(f"{dff['Marge_FCFA'].sum()/1e6:.2f}M", "Marge totale (FCFA)")
    with c5: kpi(dff["Culture"].nunique(), "Cultures distinctes")

    st.markdown("<br>", unsafe_allow_html=True)

    # Charts row 1
    c1, c2 = st.columns(2)
    with c1:
        section("", "Répartition par culture")
        cult_count = dff["Culture"].value_counts().reset_index()
        cult_count.columns = ["Culture", "Nb"]
        fig = px.pie(cult_count, values="Nb", names="Culture",
                     color_discrete_sequence=GREEN_PALETTE, hole=0.45)
        fig.update_layout(**plotly_theme(), showlegend=True, height=300, margin=dict(t=10, b=10))
        fig.update_traces(textposition="inside", textinfo="percent+label",
                          marker=dict(line=dict(color="#0d1117", width=2)))
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        section("", "Superficie par région")
        reg_surf = dff.groupby("Région")["Superficie_ha"].sum().reset_index().sort_values("Superficie_ha", ascending=True)
        fig = px.bar(reg_surf, x="Superficie_ha", y="Région", orientation="h",
                     color="Superficie_ha", color_continuous_scale=["#052e16", "#4ade80"],
                     text="Superficie_ha")
        fig.update_layout(**plotly_theme(), height=300, margin=dict(t=10, b=10), coloraxis_showscale=False)
        fig.update_traces(texttemplate="%{text:.1f} ha", textposition="outside",
                          marker_line_color="#0d1117", marker_line_width=1)
        st.plotly_chart(fig, use_container_width=True)

    # Charts row 2
    c1, c2 = st.columns(2)
    with c1:
        section("", "Rendement moyen par culture")
        rend_cult = dff.groupby("Culture")["Rendement_kg_ha"].mean().reset_index().sort_values("Rendement_kg_ha", ascending=False)
        fig = px.bar(rend_cult, x="Culture", y="Rendement_kg_ha",
                     color="Rendement_kg_ha", color_continuous_scale=["#052e16", "#4ade80"],
                     text="Rendement_kg_ha")
        fig.update_layout(**plotly_theme(), height=300, margin=dict(t=10, b=10), coloraxis_showscale=False)
        fig.update_traces(texttemplate="%{text:.0f}", textposition="outside")
        fig.update_xaxes(tickangle=30)
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        section("", "Marge vs Coût de production")
        fig = px.scatter(dff, x="Coût_FCFA", y="Marge_FCFA",
                         color="Culture", size="Superficie_ha",
                         hover_data=["Agriculteur", "Région"],
                         color_discrete_sequence=GREEN_PALETTE)
        fig.update_layout(**plotly_theme(), height=300, margin=dict(t=10, b=10))
        fig.add_hline(y=0, line_dash="dash", line_color="#ef4444", line_width=1)
        st.plotly_chart(fig, use_container_width=True)

    # Tableau complet
    section("", "Données complètes")
    st.dataframe(dff, use_container_width=True, hide_index=True,
                 column_config={
                     "Marge_FCFA": st.column_config.NumberColumn("Marge (FCFA)", format="%,.0f"),
                     "Coût_FCFA": st.column_config.NumberColumn("Coût (FCFA)", format="%,.0f"),
                     "Revenu_brut_FCFA": st.column_config.NumberColumn("Revenu brut (FCFA)", format="%,.0f"),
                 })

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 3 — ANALYSES STATISTIQUES
# ═══════════════════════════════════════════════════════════════════════════════
elif nav == " Analyses statistiques":
    st.markdown("#  Analyses statistiques descriptives")

    df = get_df()
    if df.empty:
        st.markdown('<div class="empty-state"><div class="icon"></div><p>Aucune donnée à analyser.</p></div>', unsafe_allow_html=True)
        st.stop()

    tab1, tab2, tab3, tab4 = st.tabs([" Distributions", " Corrélations", " Box Plots", " Stats détaillées"])

    num_cols = ["Superficie_ha", "Rendement_kg_ha", "Production_kg",
                "Coût_FCFA", "Marge_FCFA", "Engrais_kg", "Pluviometrie_mm", "Temperature_moy_C"]
    num_cols = [c for c in num_cols if c in df.columns]

    with tab1:
        section("", "Distribution des variables clés")
        col_sel = st.selectbox("Variable à analyser", num_cols,
                               format_func=lambda x: x.replace("_", " "))
        group_by = st.selectbox("Grouper par", ["Aucun", "Culture", "Région", "Type_sol", "Saison"])

        if group_by == "Aucun":
            fig = px.histogram(df, x=col_sel, nbins=20,
                               color_discrete_sequence=["#4ade80"],
                               marginal="box")
        else:
            fig = px.histogram(df, x=col_sel, color=group_by,
                               nbins=20, barmode="overlay",
                               color_discrete_sequence=GREEN_PALETTE,
                               marginal="box", opacity=0.75)

        fig.update_layout(**plotly_theme(), height=400)
        st.plotly_chart(fig, use_container_width=True)

        # Stats rapides
        vals = df[col_sel].dropna()
        c1, c2, c3, c4, c5, c6 = st.columns(6)
        with c1: kpi(f"{vals.mean():.1f}", "Moyenne")
        with c2: kpi(f"{vals.median():.1f}", "Médiane")
        with c3: kpi(f"{vals.std():.1f}", "Écart-type")
        with c4: kpi(f"{vals.min():.1f}", "Minimum")
        with c5: kpi(f"{vals.max():.1f}", "Maximum")
        with c6: kpi(f"{vals.skew():.2f}", "Asymétrie")

    with tab2:
        section("", "Matrice de corrélation")
        df_num = df[num_cols].dropna()
        if len(df_num) >= 2:
            corr = df_num.corr()
            fig = px.imshow(corr, text_auto=".2f",
                            color_continuous_scale=["#052e16", "#0d1117", "#166534", "#4ade80"],
                            aspect="auto", zmin=-1, zmax=1)
            fig.update_layout(**plotly_theme(), height=500)
            fig.update_coloraxes(colorbar_tickfont_color="#9ca3af")
            st.plotly_chart(fig, use_container_width=True)

            st.markdown("<br>", unsafe_allow_html=True)
            section("", "Nuage de points croisé")
            c1, c2 = st.columns(2)
            with c1: x_ax = st.selectbox("Axe X", num_cols, index=0)
            with c2: y_ax = st.selectbox("Axe Y", num_cols, index=1)
            fig2 = px.scatter(df, x=x_ax, y=y_ax, color="Culture",
                              trendline="ols", color_discrete_sequence=GREEN_PALETTE,
                              hover_data=["Agriculteur", "Région"])
            fig2.update_layout(**plotly_theme(), height=380)
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("Il faut au moins 2 enregistrements pour calculer les corrélations.")

    with tab3:
        section("", "Boîtes à moustaches")
        y_var = st.selectbox("Variable", num_cols, format_func=lambda x: x.replace("_", " "))
        x_var = st.selectbox("Catégorie (X)", ["Culture", "Région", "Type_sol", "Saison", "Irrigation"])

        fig = px.box(df, x=x_var, y=y_var, color=x_var,
                     color_discrete_sequence=GREEN_PALETTE,
                     points="all", notched=False)
        fig.update_layout(**plotly_theme(), height=420, showlegend=False)
        fig.update_xaxes(tickangle=25)
        st.plotly_chart(fig, use_container_width=True)

        # Violin
        section("", "Graphe en violon")
        fig2 = px.violin(df, x=x_var, y=y_var, color=x_var,
                         color_discrete_sequence=GREEN_PALETTE,
                         box=True, points="outliers")
        fig2.update_layout(**plotly_theme(), height=380, showlegend=False)
        fig2.update_xaxes(tickangle=25)
        st.plotly_chart(fig2, use_container_width=True)

    with tab4:
        section("", "Statistiques descriptives complètes")
        stats = df[num_cols].describe().T
        stats["variance"] = df[num_cols].var()
        stats["skewness"] = df[num_cols].skew()
        stats["kurtosis"] = df[num_cols].kurtosis()
        stats = stats.round(3)
        stats.index = [i.replace("_", " ") for i in stats.index]
        st.dataframe(stats, use_container_width=True)

        section("", "Analyse par groupe")
        group_col = st.selectbox("Grouper par", ["Culture", "Région", "Type_sol", "Saison"])
        agg_col = st.selectbox("Agréger", num_cols, format_func=lambda x: x.replace("_", " "))
        agg_func = st.radio("Fonction", ["mean", "sum", "median", "std"], horizontal=True)

        grouped = df.groupby(group_col)[agg_col].agg(agg_func).reset_index().sort_values(agg_col, ascending=False)
        grouped.columns = [group_col, f"{agg_func}({agg_col})"]

        c1, c2 = st.columns([3, 2])
        with c1:
            fig = px.bar(grouped, x=group_col, y=f"{agg_func}({agg_col})",
                         color=f"{agg_func}({agg_col})",
                         color_continuous_scale=["#052e16", "#4ade80"],
                         text=f"{agg_func}({agg_col})")
            fig.update_layout(**plotly_theme(), height=320, coloraxis_showscale=False)
            fig.update_traces(texttemplate="%{text:.2f}", textposition="outside")
            st.plotly_chart(fig, use_container_width=True)
        with c2:
            st.dataframe(grouped, use_container_width=True, hide_index=True)

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 4 — ANALYSE SPATIALE
# ═══════════════════════════════════════════════════════════════════════════════
elif nav == " Analyse spatiale":
    st.markdown("#  Analyse par région")

    df = get_df()
    if df.empty:
        st.markdown('<div class="empty-state"><div class="icon"></div><p>Aucune donnée disponible.</p></div>', unsafe_allow_html=True)
        st.stop()

    # Agrégation par région
    num_cols = ["Superficie_ha", "Rendement_kg_ha", "Production_kg",
                "Coût_FCFA", "Marge_FCFA", "Engrais_kg"]
    num_cols = [c for c in num_cols if c in df.columns]

    agg_dict = {c: "mean" for c in num_cols}
    agg_dict["Superficie_ha"] = "sum"
    agg_dict["Production_kg"] = "sum"

    reg_df = df.groupby("Région").agg(agg_dict).reset_index()
    reg_df["Nb_agriculteurs"] = df.groupby("Région").size().values

    section("", "Performance par région")
    metric = st.selectbox("Indicateur", num_cols + ["Nb_agriculteurs"],
                          format_func=lambda x: x.replace("_", " "))

    # Treemap
    fig = px.treemap(reg_df, path=["Région"], values=metric,
                     color=metric,
                     color_continuous_scale=["#052e16", "#166534", "#4ade80"],
                     hover_data=num_cols)
    fig.update_layout(**plotly_theme(), height=400, margin=dict(t=20, b=10))
    st.plotly_chart(fig, use_container_width=True)

    # Radar chart
    section("", "Profil radar multi-régions")
    radar_metrics = [c for c in ["Rendement_kg_ha", "Superficie_ha", "Marge_FCFA", "Engrais_kg"] if c in reg_df.columns]

    if len(radar_metrics) >= 3:
        selected_regs = st.multiselect("Régions à comparer",
                                       reg_df["Région"].tolist(),
                                       default=reg_df["Région"].tolist()[:4])
        if selected_regs:
            sub = reg_df[reg_df["Région"].isin(selected_regs)]
            # Normaliser
            sub_norm = sub.copy()
            for m in radar_metrics:
                mx = sub_norm[m].max()
                if mx > 0:
                    sub_norm[m] = sub_norm[m] / mx * 100

            fig = go.Figure()
            for i, row in sub_norm.iterrows():
                vals = [row[m] for m in radar_metrics] + [row[radar_metrics[0]]]
                cats = [m.replace("_", " ") for m in radar_metrics] + [radar_metrics[0].replace("_", " ")]
                fig.add_trace(go.Scatterpolar(
                    r=vals, theta=cats,
                    name=row["Région"],
                    fill="toself",
                    line_color=GREEN_PALETTE[i % len(GREEN_PALETTE)],
                    fillcolor=GREEN_PALETTE[i % len(GREEN_PALETTE)],
                    opacity=0.35,
                ))
            fig.update_layout(
                **plotly_theme(),
                polar=dict(
                    bgcolor="#111827",
                    radialaxis=dict(visible=True, range=[0, 100], gridcolor="#1e3a2f", color="#6b7280"),
                    angularaxis=dict(gridcolor="#1e3a2f", color="#9ca3af"),
                ),
                height=450,
            )
            st.plotly_chart(fig, use_container_width=True)

    # Distribution cultures par région
    section("", "Cultures par région")
    cult_reg = df.groupby(["Région", "Culture"]).size().reset_index(name="Nb")
    fig = px.bar(cult_reg, x="Région", y="Nb", color="Culture",
                 color_discrete_sequence=GREEN_PALETTE, barmode="stack")
    fig.update_layout(**plotly_theme(), height=380)
    fig.update_xaxes(tickangle=20)
    st.plotly_chart(fig, use_container_width=True)

    # Table régions
    section("", "Tableau récapitulatif par région")
    display_df = reg_df.copy()
    display_df.columns = [c.replace("_", " ") for c in display_df.columns]
    st.dataframe(display_df.round(2), use_container_width=True, hide_index=True)

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 5 — EXPORT & IMPORT
# ═══════════════════════════════════════════════════════════════════════════════
elif nav == " Export & Import":
    st.markdown("#  Export & Import des données")

    tab_exp, tab_imp, tab_gen = st.tabs([" Exporter", " Importer", " Générer des données test"])

    with tab_exp:
        df = get_df()
        if df.empty:
            st.markdown('<div class="empty-state"><div class="icon"></div><p>Aucune donnée à exporter.</p></div>', unsafe_allow_html=True)
        else:
            section("", "Télécharger les données")
            c1, c2, c3 = st.columns(3)

            with c1:
                csv_data = df.to_csv(index=False, sep=";", encoding="utf-8-sig")
                st.download_button(" Télécharger CSV", data=csv_data,
                                   file_name=f"agridata_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                                   mime="text/csv", use_container_width=True)
            with c2:
                json_data = json.dumps(st.session_state.records, ensure_ascii=False, indent=2)
                st.download_button(" Télécharger JSON", data=json_data,
                                   file_name=f"agridata_{datetime.now().strftime('%Y%m%d_%H%M')}.json",
                                   mime="application/json", use_container_width=True)
            with c3:
                buf = io.BytesIO()
                with pd.ExcelWriter(buf, engine="openpyxl") as writer:
                    df.to_excel(writer, index=False, sheet_name="Données agricoles")
                buf.seek(0)
                st.download_button(" Télécharger Excel", data=buf,
                                   file_name=f"agridata_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
                                   mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                   use_container_width=True)

            section("", "Aperçu complet")
            st.dataframe(df, use_container_width=True, hide_index=True)

    with tab_imp:
        section("", "Importer des données")
        st.markdown("<p style='color:#9ca3af;'>Importez un fichier CSV ou JSON précédemment exporté depuis AgriData.</p>", unsafe_allow_html=True)

        uploaded = st.file_uploader("Choisir un fichier", type=["csv", "json"])
        if uploaded:
            try:
                if uploaded.name.endswith(".csv"):
                    df_imp = pd.read_csv(uploaded, sep=";", encoding="utf-8-sig")
                else:
                    data = json.load(uploaded)
                    df_imp = pd.DataFrame(data)

                st.success(f" {len(df_imp)} enregistrement(s) détecté(s)")
                st.dataframe(df_imp.head(10), use_container_width=True, hide_index=True)

                c1, c2 = st.columns(2)
                with c1:
                    if st.button(" Ajouter aux données existantes", use_container_width=True):
                        for _, row in df_imp.iterrows():
                            st.session_state.records.append(row.to_dict())
                        st.success("Données ajoutées !")
                        st.rerun()
                with c2:
                    if st.button(" Remplacer toutes les données", use_container_width=True):
                        st.session_state.records = df_imp.to_dict("records")
                        st.success("Données remplacées !")
                        st.rerun()
            except Exception as e:
                st.error(f"Erreur lors de l'import : {e}")

    with tab_gen:
        section("", "Générer des données de démonstration")
        st.markdown("<p style='color:#9ca3af;'>Générez des données fictives réalistes pour tester l'application.</p>", unsafe_allow_html=True)

        n_gen = st.slider("Nombre d'enregistrements à générer", 10, 200, 50)
        if st.button(" Générer les données", use_container_width=True):
            np.random.seed(42)
            records_gen = []
            noms = ["Mbarga", "Nkoa", "Eto'o", "Biya", "Fon", "Nana", "Kamga", "Fouda", "Nlend", "Abega"]
            for i in range(n_gen):
                culture = np.random.choice(CULTURES[:-1])
                region = np.random.choice(REGIONS_CM)
                superficie = round(np.random.lognormal(0.5, 0.8), 2)
                rendement_base = {"Maïs": 2000, "Manioc": 8000, "Cacao": 500, "Café": 400,
                                  "Plantain": 5000, "Arachide": 1000, "Tomate": 15000}.get(culture, 2000)
                rendement = max(100, round(np.random.normal(rendement_base, rendement_base * 0.25)))
                prod = round(rendement * superficie, 1)
                cout = round(superficie * np.random.uniform(30000, 120000), 0)
                prix = round(np.random.uniform(150, 800), 0)
                revenu = round(prod * prix, 0)
                records_gen.append({
                    "Agriculteur": f"{np.random.choice(noms)} {chr(65+i%26)}",
                    "Région": region,
                    "Localité": f"Village {i+1}",
                    "Culture": culture,
                    "Superficie_ha": superficie,
                    "Type_sol": np.random.choice(SOLS),
                    "Irrigation": np.random.choice(IRRIGATION),
                    "Saison": np.random.choice(SAISONS),
                    "Date_semis": f"2024-0{np.random.randint(1,9)}-{np.random.randint(10,28)}",
                    "Rendement_kg_ha": rendement,
                    "Production_kg": prod,
                    "Coût_FCFA": cout,
                    "Prix_vente_kg": prix,
                    "Revenu_brut_FCFA": revenu,
                    "Marge_FCFA": revenu - cout,
                    "Engrais_kg": round(np.random.uniform(0, 100) * superficie, 1),
                    "Pesticides_L": round(np.random.uniform(0, 10), 1),
                    "Main_oeuvre_jours": int(np.random.randint(5, 60)),
                    "Semences_kg": round(np.random.uniform(1, 30), 1),
                    "Pluviometrie_mm": round(np.random.uniform(500, 2000), 0),
                    "Temperature_moy_C": round(np.random.uniform(18, 35), 1),
                    "Notes": "",
                    "Enregistré_le": datetime.now().strftime("%Y-%m-%d %H:%M"),
                })
            st.session_state.records.extend(records_gen)
            st.success(f" {n_gen} enregistrements générés avec succès !")
            st.rerun()
