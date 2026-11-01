# pyrefly: ignore[missing-import]
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import streamlit.components.v1 as components
import json
import random
import os
import textwrap

# -----------------------------------------------------------------------------
# CONFIGURAÇÃO DA PÁGINA
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Minha Biblioteca",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------------------------------------------------------
# CARREGAMENTO E TRATAMENTO DOS DADOS
# -----------------------------------------------------------------------------
@st.cache_data
def load_data():
    file_path = os.path.join(os.path.dirname(__file__), "Biblioteca.xlsx")
    if not os.path.exists(file_path):
        # Fallback to parent dir if running from different working directory
        file_path = r"c:\CesarSchool\04 - ANÁLISE E VISUALIZAÇÃO DE DADOS\Biblioteca.xlsx"
        
    df = pd.read_excel(file_path)
    # Limpeza dos nomes das colunas (removendo espaços extras)
    df.columns = [str(c).strip() for c in df.columns]

    # Tratamento de Título (garantir string)
    df['Título'] = df['Título'].apply(lambda x: str(x) if not pd.isna(x) else 'Sem Título')
    # Ajuste para caso específico de data no título da linha 117
    df['Título'] = df['Título'].replace({'2026-04-03 00:00:00': 'Obra Especial (Maria Nogueira)'})

    # Tratamento do Status
    df['Status_Clean'] = df['Status'].astype(str).str.strip().str.capitalize()
    df['Status_Clean'] = df['Status_Clean'].apply(lambda x: 'Lido' if 'lido' in x.lower() and 'não' not in x.lower() else 'Não Lido')

    # Tratamento do Tipo (Físico vs Ebook)
    df['Tipo_Clean'] = df['Tipo'].astype(str).str.strip()
    df['Tipo_Clean'] = df['Tipo_Clean'].apply(lambda x: 'Físico' if 'f' in str(x).lower() else 'Ebook')

    # Padronização de Categorias
    cat_map = {
        'fantasia': 'Fantasia',
        'Romance ': 'Romance',
        'Ficção Cienctífica': 'Ficção Científica',
        'Ficção Romantica': 'Ficção Romântica',
        'Fantasia/Romance': 'Romantasia',
        'Romance / Drama': 'Drama'
    }
    df['Categoria_Clean'] = df['Categoria'].astype(str).str.strip().replace(cat_map)

    # Conversão de Valor e Páginas para numérico
    df['Valor'] = pd.to_numeric(df['Valor'], errors='coerce').fillna(0.0)
    df['Número de páginas'] = pd.to_numeric(df['Número de páginas'], errors='coerce').fillna(0).astype(int)
    df['Nota'] = pd.to_numeric(df['Nota'], errors='coerce')

    return df

if 'df_raw' not in st.session_state:
    st.session_state.df_raw = load_data()

df_raw = st.session_state.df_raw

def update_book_status(titulo_alvo, novo_status, nova_nota=None):
    """Atualiza o status e nota de um livro no session_state e persiste nos arquivos Excel."""
    df_curr = st.session_state.df_raw
    mask = df_curr['Título'] == titulo_alvo
    if mask.any():
        st.session_state.df_raw.loc[mask, 'Status'] = novo_status
        st.session_state.df_raw.loc[mask, 'Status_Clean'] = novo_status
        if nova_nota is not None:
            st.session_state.df_raw.loc[mask, 'Nota'] = float(nova_nota)
        
        # Persistência em disco (Biblioteca.xlsx)
        excel_paths = [
            os.path.join(os.path.dirname(__file__), "Biblioteca.xlsx"),
            r"c:\CesarSchool\04 - ANÁLISE E VISUALIZAÇÃO DE DADOS\Biblioteca.xlsx"
        ]
        for p in excel_paths:
            if os.path.exists(p):
                try:
                    f_df = pd.read_excel(p)
                    col_titulo = next((c for c in f_df.columns if 'título' in c.lower() or 'titulo' in c.lower()), None)
                    col_status = next((c for c in f_df.columns if 'status' in c.lower()), None)
                    col_nota = next((c for c in f_df.columns if 'nota' in c.lower()), None)
                    
                    if col_titulo and col_status:
                        m = f_df[col_titulo].astype(str).str.strip() == str(titulo_alvo).strip()
                        if m.any():
                            f_df.loc[m, col_status] = novo_status
                            if nova_nota is not None and col_nota:
                                f_df.loc[m, col_nota] = float(nova_nota)
                            f_df.to_excel(p, index=False)
                except Exception as err:
                    print(f"Aviso ao persistir em {p}: {err}")
        
        # Limpar cache para garantir integridade
        load_data.clear()

# -----------------------------------------------------------------------------
# FUNÇÕES DE FORMATAÇÃO (PADRÃO BRASILEIRO: PONTO NO MILHAR, VÍRGULA NO DECIMAL)
# -----------------------------------------------------------------------------
def fmt_milhar(val):
    """Formata número inteiro com ponto como separador de milhar (ex: 87617 -> 87.617)."""
    if pd.isna(val) or val is None:
        return "0"
    try:
        return f"{int(round(float(val))):,}".replace(",", ".")
    except (ValueError, TypeError):
        return str(val)

def fmt_moeda(val):
    """Formata valor monetário no padrão brasileiro: R$ 1.234,56."""
    if pd.isna(val) or val is None:
        return "R$ 0,00"
    try:
        s = f"{float(val):,.2f}"
        return "R$ " + s.replace(",", "X").replace(".", ",").replace("X", ".")
    except (ValueError, TypeError):
        return f"R$ {val}"

def fmt_pct(val):
    """Formata percentual com vírgula decimal (ex: 34.6 -> 34,6%)."""
    if pd.isna(val) or val is None:
        return "0,0%"
    try:
        return f"{float(val):.1f}%".replace(".", ",")
    except (ValueError, TypeError):
        return str(val)
# CSS CUSTOMIZADO - DESIGN ESCURO PREMIUM (IDÊNTICO À IMAGEM DE REFERÊNCIA)
# -----------------------------------------------------------------------------
custom_css = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Outfit', 'Inter', -apple-system, sans-serif;
}

/* Background geral escuro */
.stApp {
    background-color: #171926;
    color: #e2e8f0;
}

/* Sidebar elegante */
[data-testid="stSidebar"] {
    background-color: #12141f !important;
    border-right: 1px solid rgba(255, 255, 255, 0.06);
}

/* Cards estilizados usando containers nativos */
div[data-testid="stVerticalBlockBorderWrapper"],
div[data-testid="stContainer"],
[data-testid="stVerticalBlock"] > div[style*="border"] {
    background: #212538 !important;
    border: 1px solid rgba(255, 255, 255, 0.12) !important;
    border-radius: 18px !important;
    padding: 18px 20px !important;
    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.25) !important;
    height: 100% !important;
    transition: transform 0.2s ease, border-color 0.2s ease !important;
}

div[data-testid="stVerticalBlockBorderWrapper"]:hover {
    border-color: rgba(255, 255, 255, 0.25) !important;
}

div[data-testid="stVerticalBlockBorderWrapper"] > div {
    background: transparent !important;
}

/* Segmented Control estilizado e contido 100% dentro da caixa */
div[data-testid="stSegmentedControl"] {
    background-color: #161826 !important;
    border-radius: 12px !important;
    padding: 4px !important;
    border: 1px solid rgba(255, 255, 255, 0.12) !important;
    margin-top: 10px !important;
    width: 100% !important;
}

div[data-testid="stSegmentedControl"] button {
    background-color: transparent !important;
    color: #f1f5f9 !important;
    border: none !important;
    border-radius: 8px !important;
    font-size: 13.5px !important;
    font-weight: 700 !important;
    padding: 7px 12px !important;
    transition: all 0.2s ease !important;
}

div[data-testid="stSegmentedControl"] button:hover {
    color: #ffffff !important;
    background-color: rgba(255, 255, 255, 0.1) !important;
}

div[data-testid="stSegmentedControl"] button[aria-checked="true"],
div[data-testid="stSegmentedControl"] button[data-state="on"],
div[data-testid="stSegmentedControl"] [aria-selected="true"] {
    background: linear-gradient(135deg, #f72585, #4361ee) !important;
    color: #ffffff !important;
    box-shadow: 0 2px 10px rgba(247, 37, 133, 0.45) !important;
}

.metric-card {
    position: relative;
    overflow: hidden;
    height: 100%;
}

/* Quadrado de destaque gradiente no canto superior esquerdo */
.card-badge {
    display: inline-block;
    width: 14px;
    height: 14px;
    border-radius: 4px;
    margin-right: 8px;
    vertical-align: middle;
}

.badge-pink-blue {
    background: linear-gradient(135deg, #f72585, #4361ee);
}

.badge-cyan {
    background: linear-gradient(135deg, #4cc9f0, #4361ee);
}

.badge-purple {
    background: linear-gradient(135deg, #7209b7, #f72585);
}

.badge-emerald {
    background: linear-gradient(135deg, #00f5d4, #00b4d8);
}

.card-title {
    color: #f8fafc;
    font-size: 13.5px;
    font-weight: 700;
    letter-spacing: 0.6px;
    text-transform: uppercase;
    display: inline-block;
}

.card-value {
    color: #ffffff;
    font-size: 34px;
    font-weight: 700;
    margin-top: 14px;
    margin-bottom: 6px;
    line-height: 1.1;
}

.card-subtext {
    color: #f1f5f9;
    font-size: 13.5px;
    font-weight: 600;
}

.highlight-read {
    color: #00f5d4;
    font-weight: 700;
}

.highlight-unread {
    color: #f72585;
    font-weight: 700;
}

/* Right column card container */
.side-summary-card {
    background: #212538;
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 18px;
    padding: 24px;
    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.25);
}

/* User header styling */
.header-container {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 24px;
    padding-bottom: 12px;
}

.user-profile {
    display: flex;
    align-items: center;
    gap: 14px;
}

.user-avatar {
    width: 48px;
    height: 48px;
    border-radius: 50%;
    background: linear-gradient(135deg, #f72585, #4361ee);
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 700;
    color: white;
    font-size: 18px;
    box-shadow: 0 4px 12px rgba(247, 37, 133, 0.3);
}

.user-greeting {
    font-size: 19px;
    font-weight: 600;
    color: #ffffff;
}

.page-title {
    font-size: 28px;
    font-weight: 700;
    color: #ffffff;
    margin-bottom: 20px;
    letter-spacing: -0.5px;
}

/* Custom interactive pill styling */
div.stRadio > div {
    display: flex;
    gap: 8px;
}

/* Botões com estilo moderno */
.stButton>button {
    background: linear-gradient(135deg, #4361ee, #3a0ca3);
    color: white;
    border: none;
    border-radius: 12px;
    font-weight: 600;
    padding: 10px 20px;
    transition: all 0.2s ease;
}

.stButton>button:hover {
    background: linear-gradient(135deg, #4cc9f0, #4361ee);
    color: white;
    box-shadow: 0 4px 15px rgba(67, 97, 238, 0.4);
    transform: translateY(-1px);
}

/* =========================================================================
   ESTILOS DE WIDGETS, MULTISELECT, SELECTBOX E CONTRASTE DE TEXTOS
   ========================================================================= */

/* Radio buttons no Sidebar */
div[data-testid="stRadio"] label {
    background-color: transparent !important;
    padding: 6px 10px !important;
    border-radius: 10px !important;
    transition: all 0.2s ease !important;
    cursor: pointer !important;
}

div[data-testid="stRadio"] label:hover {
    background-color: rgba(255, 255, 255, 0.06) !important;
}

div[data-testid="stRadio"] label p,
div[data-testid="stRadio"] [data-testid="stMarkdownContainer"] p,
div[data-testid="stRadio"] span {
    color: #e2e8f0 !important;
    font-size: 14px !important;
    font-weight: 600 !important;
}

div[data-testid="stRadio"] label:has(input:checked) p,
div[data-testid="stRadio"] label[data-checked="true"] p {
    color: #00f5d4 !important;
    font-weight: 700 !important;
}

/* Rótulos de formulário e inputs com contraste excelente */
label[data-testid="stWidgetLabel"],
div[data-testid="stWidgetLabel"] label,
div[data-testid="stWidgetLabel"] p,
div[data-testid="stWidgetLabel"] span {
    color: #f8fafc !important;
    font-size: 14px !important;
    font-weight: 700 !important;
    letter-spacing: 0.3px !important;
    margin-bottom: 6px !important;
}

/* Legendas e textos auxiliares */
[data-testid="stCaptionContainer"] p,
.stCaption, caption {
    color: #cbd5e1 !important;
    font-size: 13.5px !important;
    font-weight: 600 !important;
}

/* Caixas de seleção (multiselect e selectbox) no tom escuro do dashboard */
div[data-baseweb="select"] {
    background-color: transparent !important;
}

div[data-baseweb="select"] > div,
div[data-baseweb="select"] div[role="combobox"],
div[data-baseweb="base-input"] {
    background-color: #212538 !important;
    border: 1px solid rgba(255, 255, 255, 0.18) !important;
    border-radius: 12px !important;
    color: #ffffff !important;
    min-height: 44px !important;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.25) !important;
    transition: all 0.2s ease !important;
}

div[data-baseweb="select"] > div:hover,
div[data-baseweb="select"] > div:focus-within {
    border-color: #4361ee !important;
    box-shadow: 0 0 0 1px #4361ee, 0 4px 18px rgba(67, 97, 238, 0.35) !important;
}

/* Valores e textos dentro do select */
div[data-baseweb="select"] span,
div[data-baseweb="select"] input,
div[data-baseweb="select"] [data-testid="stMarkdownContainer"] p {
    color: #ffffff !important;
    font-size: 14px !important;
    font-weight: 500 !important;
}

/* Placeholder nos selects com alta legibilidade */
div[data-baseweb="select"] div[aria-hidden="true"],
div[data-baseweb="select"] [class*="placeholder"],
div[data-baseweb="input"] input::placeholder {
    color: #cbd5e1 !important;
    font-size: 14px !important;
    font-weight: 500 !important;
}

div[data-baseweb="select"] svg {
    fill: #cbd5e1 !important;
}

/* Tags selecionadas no Multiselect */
div[data-baseweb="tag"] {
    background: linear-gradient(135deg, #2b324a, #1f2337) !important;
    border: 1px solid rgba(0, 245, 212, 0.5) !important;
    border-radius: 8px !important;
    color: #ffffff !important;
    padding: 3px 10px !important;
    font-weight: 600 !important;
}

div[data-baseweb="tag"] span {
    color: #ffffff !important;
    font-size: 13px !important;
    font-weight: 600 !important;
}

div[data-baseweb="tag"] svg {
    fill: #00f5d4 !important;
}

div[data-baseweb="tag"] svg:hover {
    fill: #f72585 !important;
}

/* Menus suspensos / Dropdown listbox */
div[data-baseweb="popover"],
ul[role="listbox"],
div[data-baseweb="menu"] {
    background-color: #1c1f30 !important;
    border: 1px solid rgba(255, 255, 255, 0.18) !important;
    border-radius: 12px !important;
    box-shadow: 0 14px 40px rgba(0, 0, 0, 0.6) !important;
    padding: 6px !important;
}

li[role="option"] {
    background-color: transparent !important;
    color: #f1f5f9 !important;
    font-size: 14px !important;
    font-weight: 500 !important;
    padding: 10px 14px !important;
    border-radius: 8px !important;
    transition: all 0.15s ease !important;
}

li[role="option"]:hover,
li[role="option"][aria-selected="true"] {
    background-color: rgba(67, 97, 238, 0.35) !important;
    color: #00f5d4 !important;
    font-weight: 700 !important;
}

/* Caixa de pesquisa / Text Input */
div[data-baseweb="input"] > div {
    background-color: #212538 !important;
    border: 1px solid rgba(255, 255, 255, 0.18) !important;
    border-radius: 12px !important;
    color: #ffffff !important;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.25) !important;
}

div[data-baseweb="input"] input {
    color: #ffffff !important;
}

div[data-baseweb="input"] input::placeholder {
    color: #cbd5e1 !important;
}

/* Expander nos tons do dashboard */
div[data-testid="stExpander"] {
    background-color: #212538 !important;
    border: 1px solid rgba(255, 255, 255, 0.12) !important;
    border-radius: 14px !important;
    margin-top: 10px !important;
}

details summary {
    color: #ffffff !important;
    font-weight: 600 !important;
}

details summary:hover {
    color: #4cc9f0 !important;
}

/* Dataframe nativo com fundo integrado ao tema */
div[data-testid="stDataFrame"] {
    background-color: #212538 !important;
    border: 1px solid rgba(255, 255, 255, 0.12) !important;
    border-radius: 12px !important;
    overflow: hidden !important;
}

div[data-testid="stDataFrame"] canvas {
    filter: invert(0.92) hue-rotate(180deg) contrast(1.1) brightness(1.05) !important;
    border-radius: 10px !important;
}
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# GERENCIAMENTO DE ESTADO E NAVEGAÇÃO LATERAL
# -----------------------------------------------------------------------------
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'dashboard'

if 'tipo_filter' not in st.session_state:
    st.session_state.tipo_filter = 'Todos'

with st.sidebar:
    st.markdown("""
        <div style="display: flex; align-items: center; gap: 10px; padding: 12px 0 20px 0;">
            <div style="background: linear-gradient(135deg, #f72585, #4361ee); padding: 8px; border-radius: 12px; font-size: 22px;">📚</div>
            <div>
                <div style="font-size: 18px; font-weight: 700; color: #fff;">Minha Biblioteca</div>
                <div style="font-size: 13px; color: #cbd5e1; font-weight: 600;">M. E. Fernandes</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("<p style='color:#a5b4fc; font-size: 11.5px; font-weight: 700; letter-spacing: 1px; text-transform: uppercase;'>Navegação</p>", unsafe_allow_html=True)

    nav_selection = st.radio(
        "Selecione a página:",
        options=["📊 Visão Geral da Biblioteca", "🎡 Roleta de Leitura Virtual", "📖 Catálogo Completo"],
        index=0 if st.session_state.current_page == 'dashboard' else (1 if st.session_state.current_page == 'roleta' else 2),
        label_visibility="collapsed"
    )

    if "Visão Geral" in nav_selection:
        st.session_state.current_page = 'dashboard'
    elif "Roleta" in nav_selection:
        st.session_state.current_page = 'roleta'
    else:
        st.session_state.current_page = 'catalogo'

    st.markdown("---")
    st.markdown("<p style='color:#a5b4fc; font-size: 11.5px; font-weight: 700; letter-spacing: 1px; text-transform: uppercase;'>Resumo Rápido</p>", unsafe_allow_html=True)
    
    total_livros = len(df_raw)
    total_lidos = len(df_raw[df_raw['Status_Clean'] == 'Lido'])
    pct_total = (total_lidos / total_livros * 100) if total_livros > 0 else 0
    
    st.markdown(f"""
        <div style="background: #1c1f30; padding: 16px; border-radius: 14px; border: 1px solid rgba(255,255,255,0.08); margin-bottom: 12px;">
            <div style="font-size: 12px; color: #cbd5e1; font-weight: 600;">Progresso Anual</div>
            <div style="font-size: 20px; font-weight: 700; color: #00f5d4; margin: 4px 0;">{fmt_milhar(total_lidos)} / {fmt_milhar(total_livros)}</div>
            <div style="font-size: 12.5px; color: #e2e8f0; font-weight: 500;">{fmt_pct(pct_total)} da biblioteca concluída</div>
        </div>
    """, unsafe_allow_html=True)
    st.progress(pct_total / 100.0)

# =============================================================================
# PÁGINA 1: DASHBOARD / VISÃO GERAL
# =============================================================================
if st.session_state.current_page == 'dashboard':
    
    # ------------------ TOP HEADER ------------------
    col_head_left, col_head_right = st.columns([7, 3])
    with col_head_left:
        st.markdown("""
            <div class="user-profile">
                <div class="user-avatar">📚</div>
                <div>
                    <div class="user-greeting">Olá, Leitor(a)!</div>
                    <div style="color: #cbd5e1; font-size: 13.5px; font-weight: 500;">Bem-vindo(a) ao painel de performance da sua biblioteca</div>
                </div>
            </div>
        """, unsafe_allow_html=True)
    with col_head_right:
        search_query = st.text_input("🔍 Buscar livro ou autor...", placeholder="Digite para filtrar...", label_visibility="collapsed")

    st.markdown("<div class='page-title'>Performance Overview da Biblioteca</div>", unsafe_allow_html=True)

    # ------------------ LINHA DE CARDS DE MÉTRICAS ------------------
    # Caixa 1, Caixa 2, Caixa 3 e Card Lateral Direito
    col_c1, col_c2, col_c3, col_side = st.columns([2.6, 2.9, 2.7, 2.8])

    # Caixa 2 (INTERATIVA): Seleção de Formato (Físicos ou Ebooks)
    with col_c2:
        with st.container(border=True):
            total_fisico = len(df_raw[df_raw['Tipo_Clean'] == 'Físico'])
            total_ebook = len(df_raw[df_raw['Tipo_Clean'] == 'Ebook'])
            
            st.markdown(f"""
                <div>
                    <span class="card-badge badge-cyan"></span>
                    <span class="card-title">2. Formato: Físicos x Ebooks</span>
                </div>
                <div class="card-value" style="font-size: 26px; margin: 8px 0 2px 0;">
                    {fmt_milhar(total_fisico)} <span style="font-size: 14px; font-weight: 600; color: #cbd5e1;">Físicos</span> 
                    &nbsp;|&nbsp; 
                    {fmt_milhar(total_ebook)} <span style="font-size: 14px; font-weight: 600; color: #cbd5e1;">E-books</span>
                </div>
                <div class="card-subtext" style="margin-bottom: 2px;">
                    Clique para alternar as métricas da Caixa 1:
                </div>
            """, unsafe_allow_html=True)
            
            # Seletor interativo embutido DENTRO da Caixa 2
            tipo_selecionado = st.segmented_control(
                "Filtrar por Formato:",
                options=["Todos", "Físico", "Ebook"],
                default=st.session_state.tipo_filter,
                label_visibility="collapsed",
                width="stretch"
            )
            if tipo_selecionado is None:
                tipo_selecionado = "Todos"
            st.session_state.tipo_filter = tipo_selecionado

    # Filtragem do dataset baseada na seleção interativa da Caixa 2
    if st.session_state.tipo_filter == "Todos":
        df_filtered = df_raw.copy()
        filtro_label = "Todos os Formatos"
    elif st.session_state.tipo_filter == "Físico":
        df_filtered = df_raw[df_raw['Tipo_Clean'] == 'Físico'].copy()
        filtro_label = "Apenas Livros Físicos"
    else:
        df_filtered = df_raw[df_raw['Tipo_Clean'] == 'Ebook'].copy()
        filtro_label = "Apenas E-books Kindle"

    # Cálculos reativos para Caixa 1 e Caixa 3
    qnt_total_filtrado = len(df_filtered)
    qnt_lidos_filtrado = len(df_filtered[df_filtered['Status_Clean'] == 'Lido'])
    qnt_nao_lidos_filtrado = qnt_total_filtrado - qnt_lidos_filtrado
    pct_lidos_filtrado = (qnt_lidos_filtrado / qnt_total_filtrado * 100) if qnt_total_filtrado > 0 else 0

    valor_total_filtrado = df_filtered['Valor'].sum()
    valor_lidos_filtrado = df_filtered[df_filtered['Status_Clean'] == 'Lido']['Valor'].sum()
    pct_valor_lidos = (valor_lidos_filtrado / valor_total_filtrado * 100) if valor_total_filtrado > 0 else 0

    # Caixa 1: Quantidade de Livros na Biblioteca x Lidos (Reativa à Caixa 2)
    with col_c1:
        with st.container(border=True):
            st.markdown(f"""
                <div>
                    <span class="card-badge badge-pink-blue"></span>
                    <span class="card-title">1. Total x Livros Lidos</span>
                </div>
                <div class="card-value">{fmt_milhar(qnt_total_filtrado)}</div>
                <div class="card-subtext">
                    <span class="highlight-read">{fmt_milhar(qnt_lidos_filtrado)} Lidos</span> ({fmt_pct(pct_lidos_filtrado)}) &nbsp;•&nbsp; 
                    <span class="highlight-unread">{fmt_milhar(qnt_nao_lidos_filtrado)} Não lidos</span>
                </div>
                <div style="font-size: 12px; color: #4cc9f0; margin-top: 14px; font-weight: 600;">
                    👁️ Exibindo: <b>{filtro_label}</b>
                </div>
            """, unsafe_allow_html=True)

    # Caixa 3: Valor da Biblioteca x Valor de Livros Lidos
    with col_c3:
        with st.container(border=True):
            st.markdown(f"""
                <div>
                    <span class="card-badge badge-purple"></span>
                    <span class="card-title">3. Valor Total x Lidos</span>
                </div>
                <div class="card-value" style="font-size: 27px;">{fmt_moeda(valor_total_filtrado)}</div>
                <div class="card-subtext">
                    <span class="highlight-read">{fmt_moeda(valor_lidos_filtrado)}</span> em lidos ({fmt_pct(pct_valor_lidos)})
                </div>
                <div style="font-size: 12px; color: #cbd5e1; margin-top: 14px; font-weight: 500;">
                    Preço médio: {fmt_moeda(valor_total_filtrado / qnt_total_filtrado if qnt_total_filtrado else 0)} / livro
                </div>
            """, unsafe_allow_html=True)

    # Card Lateral Direito (Estatísticas de Páginas & Avaliações)
    with col_side:
        with st.container(border=True):
            paginas_totais = df_filtered['Número de páginas'].sum()
            paginas_lidas = df_filtered[df_filtered['Status_Clean'] == 'Lido']['Número de páginas'].sum()
            media_paginas = df_filtered['Número de páginas'].mean() if qnt_total_filtrado > 0 else 0
            nota_media = df_filtered[df_filtered['Status_Clean'] == 'Lido']['Nota'].mean()

            st.markdown(f"""
                <div style="margin-bottom: 6px;">
                    <span class="card-badge badge-emerald"></span>
                    <span class="card-title">Páginas & Avaliação</span>
                </div>
                <div style="display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 6px;">
                    <span style="font-size: 13.5px; color: #cbd5e1; font-weight: 600;">Total de Páginas</span>
                    <span style="font-size: 17px; font-weight: 700; color: #fff;">{fmt_milhar(paginas_totais)}</span>
                </div>
                <div style="display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 6px;">
                    <span style="font-size: 13.5px; color: #cbd5e1; font-weight: 600;">Páginas Lidas</span>
                    <span style="font-size: 15px; font-weight: 600; color: #00f5d4;">{fmt_milhar(paginas_lidas)}</span>
                </div>
                <div style="display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 6px;">
                    <span style="font-size: 13.5px; color: #cbd5e1; font-weight: 600;">Média p/ Livro</span>
                    <span style="font-size: 14px; font-weight: 600; color: #fff;">{fmt_milhar(round(media_paginas))} págs</span>
                </div>
                <div style="display: flex; justify-content: space-between; align-items: baseline;">
                    <span style="font-size: 13.5px; color: #cbd5e1; font-weight: 600;">Nota Média</span>
                    <span style="font-size: 14px; font-weight: 600; color: #f72585;">⭐ {nota_media:.1f} / 5.0</span>
                </div>
            """, unsafe_allow_html=True)

    # ------------------ GRÁFICO PRINCIPAL POR CATEGORIA ------------------
    st.markdown("<br>", unsafe_allow_html=True)
    
    st.markdown("""
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
            <div>
                <span class="card-badge badge-pink-blue"></span>
                <span style="font-size: 18px; font-weight: 700; color: #ffffff;">Livros por Categoria: Total da Biblioteca x Lidos</span>
                <div style="font-size: 13px; color: #cbd5e1; margin-left: 22px; font-weight: 500;">Comparativo de leitura por gênero literário</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Agregação por categoria usando o dataframe (respeitando o filtro de formato se aplicado)
    cat_summary = df_filtered.groupby('Categoria_Clean').agg(
        Total=('Título', 'count'),
        Lidos=('Status_Clean', lambda s: (s == 'Lido').sum()),
        Nao_Lidos=('Status_Clean', lambda s: (s == 'Não Lido').sum()),
        Valor=('Valor', 'sum')
    ).sort_values(by='Total', ascending=False).reset_index()

    # Criação do gráfico interativo Plotly estilizado no tema escuro neon
    fig_cat = go.Figure()

    # Barra 1: Total de Livros da Categoria (Cyan / Eletric Blue)
    fig_cat.add_trace(go.Bar(
        x=cat_summary['Categoria_Clean'],
        y=cat_summary['Total'],
        name='Total de Livros',
        marker=dict(
            color='#00b4d8',
            line=dict(color='rgba(0, 180, 216, 0.4)', width=1)
        ),
        hovertemplate='<b>%{x}</b><br>📚 Total de Livros: %{y}<extra></extra>'
    ))

    # Barra 2: Livros Lidos (Neon Hot Pink)
    fig_cat.add_trace(go.Bar(
        x=cat_summary['Categoria_Clean'],
        y=cat_summary['Lidos'],
        name='Livros Já Lidos',
        marker=dict(
            color='#f72585',
            line=dict(color='rgba(247, 37, 133, 0.4)', width=1)
        ),
        hovertemplate='<b>%{x}</b><br>✅ Livros Lidos: %{y}<extra></extra>'
    ))

    fig_cat.update_layout(
        barmode='group',
        bargap=0.25,
        bargroupgap=0.1,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(33, 37, 56, 0.85)',
        font=dict(family='Outfit, sans-serif', color='#cbd5e1'),
        margin=dict(l=20, r=20, t=30, b=50),
        height=380,
        separators=",.",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(size=12, color='#ffffff')
        ),
        xaxis=dict(
            showgrid=False,
            tickangle=-25,
            tickfont=dict(size=12, color='#cbd5e1')
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='rgba(255, 255, 255, 0.06)',
            title=dict(text="Quantidade de Livros", font=dict(size=13, color='#cbd5e1')),
            tickfont=dict(size=11, color='#cbd5e1')
        )
    )

    st.plotly_chart(fig_cat, use_container_width=True)

    # ------------------ SEÇÃO INFERIOR COM 3 CARDS COMPLEMENTARES ------------------
    col_b1, col_b2, col_b3 = st.columns(3)

    # Card B1: Donut Chart de Status (como na imagem)
    with col_b1:
        st.markdown("""
            <div style="background: #212538; border-radius: 18px; padding: 18px; border: 1px solid rgba(255,255,255,0.08);">
                <div style="font-size: 13px; font-weight: 700; color: #cbd5e1; text-transform: uppercase;">
                    <span class="card-badge badge-pink-blue"></span> Status Geral da Biblioteca
                </div>
        """, unsafe_allow_html=True)
        
        fig_donut = go.Figure(data=[go.Pie(
            labels=['Livros Lidos', 'Não Lidos'],
            values=[qnt_lidos_filtrado, qnt_nao_lidos_filtrado],
            hole=0.68,
            marker=dict(colors=['#00f5d4', '#2a2f45']),
            hoverinfo='label+value+percent',
            textinfo='none'
        )])
        fig_donut.update_layout(
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5, font=dict(size=11, color='#cbd5e1')),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=10, r=10, t=10, b=10),
            height=200,
            separators=",.",
            annotations=[dict(
                text=f"<b>{fmt_pct(pct_lidos_filtrado)}</b><br><span style='font-size:10px; color:#cbd5e1; font-weight:600;'>LIDOS</span>",
                x=0.5, y=0.5, font_size=19, font_family="Outfit", font_color="#ffffff", showarrow=False
            )]
        )
        st.plotly_chart(fig_donut, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # Card B2: Top 5 Categorias Mais Valiosas
    with col_b2:
        st.markdown("""
            <div style="background: #212538; border-radius: 18px; padding: 18px; border: 1px solid rgba(255,255,255,0.08);">
                <div style="font-size: 13px; font-weight: 700; color: #cbd5e1; text-transform: uppercase;">
                    <span class="card-badge badge-purple"></span> Top Categorias por Valor
                </div>
        """, unsafe_allow_html=True)
        
        top_val = cat_summary.head(5).copy()
        fig_val = go.Figure(go.Bar(
            x=top_val['Valor'],
            y=top_val['Categoria_Clean'],
            orientation='h',
            marker=dict(
                color=top_val['Valor'],
                colorscale=[[0, '#4361ee'], [1, '#f72585']]
            ),
            hovertemplate='<b>%{y}</b><br>Investimento: R$ %{x:,.2f}<extra></extra>'
        ))
        fig_val.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=10, r=10, t=10, b=10),
            height=200,
            separators=",.",
            yaxis=dict(autorange="reversed", tickfont=dict(size=11, color='#cbd5e1')),
            xaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.06)', tickfont=dict(size=10, color='#cbd5e1'))
        )
        st.plotly_chart(fig_val, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # Card B3: Distribuição de Avaliações / Estrelas
    with col_b3:
        st.markdown("""
            <div style="background: #212538; border-radius: 18px; padding: 18px; border: 1px solid rgba(255,255,255,0.08);">
                <div style="font-size: 13px; font-weight: 700; color: #cbd5e1; text-transform: uppercase;">
                    <span class="card-badge badge-cyan"></span> Distribuição das Avaliações
                </div>
        """, unsafe_allow_html=True)
        
        notas_series = df_filtered[df_filtered['Status_Clean'] == 'Lido']['Nota'].dropna().value_counts().sort_index().reset_index()
        notas_series.columns = ['Nota', 'Quantidade']
        
        fig_notas = go.Figure(go.Bar(
            x=[f"{n:.1f}★" for n in notas_series['Nota']],
            y=notas_series['Quantidade'],
            marker=dict(color='#7209b7'),
            hovertemplate='Nota %{x}: %{y} livros<extra></extra>'
        ))
        fig_notas.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=10, r=10, t=10, b=10),
            height=200,
            separators=",.",
            xaxis=dict(tickfont=dict(size=11, color='#cbd5e1')),
            yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.06)', tickfont=dict(size=10, color='#cbd5e1'))
        )
        st.plotly_chart(fig_notas, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # ------------------ CALL TO ACTION PARA ROLETA ------------------
    st.markdown("<br>", unsafe_allow_html=True)
    col_cta1, col_cta2 = st.columns([8, 2])
    with col_cta1:
        st.markdown("""
            <div style="background: linear-gradient(135deg, rgba(67, 97, 238, 0.2), rgba(247, 37, 133, 0.2)); border: 1px solid rgba(247, 37, 133, 0.3); border-radius: 16px; padding: 18px 24px; display: flex; align-items: center; justify-content: space-between;">
                <div>
                    <span style="font-size: 18px; font-weight: 700; color: #ffffff;">🎯 Em dúvida sobre o que ler a seguir?</span>
                    <p style="margin: 4px 0 0 0; color: #cbd5e1; font-size: 13px;">Gire a Roleta Virtual na aba lateral para sortear seu próximo livro entre os 121 títulos não lidos!</p>
                </div>
            </div>
        """, unsafe_allow_html=True)
    with col_cta2:
        st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
        if st.button("🎡 Abrir Roleta ➔", use_container_width=True):
            st.session_state.current_page = 'roleta'
            st.rerun()

# =============================================================================
# PÁGINA 2: ROLETA VIRTUAL (SORTEIO DE LIVROS NÃO LIDOS)
# =============================================================================
elif st.session_state.current_page == 'roleta':
    
    st.markdown("""
        <div style="display: flex; align-items: center; gap: 14px; margin-bottom: 20px;">
            <div style="font-size: 34px;">🎡</div>
            <div>
                <div class="page-title" style="margin-bottom: 2px;">Roleta Virtual de Livros Não Lidos</div>
                <div style="color: #cbd5e1; font-size: 14px; font-weight: 500;">Sorteie sua próxima grande leitura entre todos os títulos pendentes da sua biblioteca</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Livros não lidos disponíveis
    df_nao_lidos = df_raw[df_raw['Status_Clean'] == 'Não Lido'].copy()
    
    # Filtros para personalizar a roleta (opcional)
    col_rf1, col_rf2 = st.columns([1, 1])
    
    with col_rf1:
        categorias_nao_lidas = ["Todas as Categorias"] + sorted(df_nao_lidos['Categoria_Clean'].unique().tolist())
        cat_escolhida = st.selectbox("🎯 Filtrar por Categoria na Roleta:", options=categorias_nao_lidas)
        
    with col_rf2:
        tipo_escolhido = st.selectbox("📦 Filtrar por Formato:", options=["Todos", "Físico", "Ebook"])

    # Aplicação dos filtros
    df_roleta = df_nao_lidos.copy()
    if cat_escolhida != "Todas as Categorias":
        df_roleta = df_roleta[df_roleta['Categoria_Clean'] == cat_escolhida]
    if tipo_escolhido != "Todos":
        df_roleta = df_roleta[df_roleta['Tipo_Clean'] == tipo_escolhido]

    total_elegiveis = len(df_roleta)

    if total_elegiveis == 0:
        st.warning("⚠️ Nenhum livro não lido encontrado com os filtros selecionados. Tente selecionar outra categoria ou formato!")
    else:
        st.markdown(f"""
            <div style="background: rgba(67, 97, 238, 0.12); border: 1px solid rgba(67, 97, 238, 0.3); border-radius: 12px; padding: 10px 18px; margin: 8px 0 16px 0; display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 8px;">
                <div style="color: #4cc9f0; font-size: 14px; font-weight: 600;">
                    ✨ <b>Todos os {fmt_milhar(total_elegiveis)} livros não lidos</b> estão carregados na roleta!
                </div>
                <div style="color: #cbd5e1; font-size: 12.5px; font-weight: 500;">
                    🎯 100% dos títulos participam com chances iguais de sorteio
                </div>
            </div>
        """, unsafe_allow_html=True)

        # TODOS os livros não lidos participam da roleta (embaralhados para disposição aleatória)
        sample_books = df_roleta.to_dict('records')
        random.shuffle(sample_books)

        # Formatação JSON para passar ao componente Canvas HTML5
        books_json_data = json.dumps([
            {
                "titulo": b['Título'],
                "autor": b['Autor'],
                "categoria": b['Categoria_Clean'],
                "tipo": b['Tipo_Clean'],
                "valor": fmt_moeda(b['Valor']),
                "paginas": fmt_milhar(int(b['Número de páginas']))
            }
            for b in sample_books
        ], ensure_ascii=False)

        # ------------------ COMPONENTE HTML5 / CANVAS WHEEL ------------------
        roulette_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;600;700;800&display=swap');
                * {{ box-sizing: border-box; margin: 0; padding: 0; }}
                body {{
                    background: transparent;
                    font-family: 'Outfit', sans-serif;
                    color: white;
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    overflow: hidden;
                    padding-top: 4px;
                }}
                /* Indicador destacado do livro sob o ponteiro em posição favorável */
                .pointer-indicator-box {{
                    width: 95%;
                    max-width: 620px;
                    background: linear-gradient(135deg, rgba(33, 37, 56, 0.95), rgba(20, 23, 38, 0.98));
                    border: 1px solid rgba(247, 37, 133, 0.4);
                    border-radius: 16px;
                    padding: 12px 24px;
                    margin-bottom: 12px;
                    text-align: center;
                    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.35), 0 0 15px rgba(247, 37, 133, 0.2);
                    transition: all 0.2s ease;
                }}
                .indicator-tag {{
                    font-size: 11px;
                    font-weight: 700;
                    color: #4cc9f0;
                    letter-spacing: 1.5px;
                    text-transform: uppercase;
                    margin-bottom: 4px;
                }}
                .indicator-title {{
                    font-size: 19px;
                    font-weight: 700;
                    color: #ffffff;
                    min-height: 26px;
                    white-space: nowrap;
                    overflow: hidden;
                    text-overflow: ellipsis;
                }}
                .indicator-sub {{
                    font-size: 12px;
                    color: #8e95ab;
                    margin-top: 3px;
                }}
                .wheel-wrapper {{
                    position: relative;
                    width: 480px;
                    height: 480px;
                    margin: 8px auto;
                }}
                canvas#wheel {{
                    width: 480px;
                    height: 480px;
                    border-radius: 50%;
                    box-shadow: 0 0 35px rgba(247, 37, 133, 0.35), 0 0 15px rgba(67, 97, 238, 0.4);
                }}
                .pointer {{
                    position: absolute;
                    top: -12px;
                    left: 50%;
                    transform: translateX(-50%);
                    width: 0;
                    height: 0;
                    border-left: 18px solid transparent;
                    border-right: 18px solid transparent;
                    border-top: 32px solid #ffd166;
                    filter: drop-shadow(0 4px 8px rgba(0,0,0,0.6));
                    z-index: 10;
                }}
                .center-button {{
                    position: absolute;
                    top: 50%;
                    left: 50%;
                    transform: translate(-50%, -50%);
                    width: 92px;
                    height: 92px;
                    border-radius: 50%;
                    background: linear-gradient(135deg, #f72585, #7209b7);
                    border: 4px solid #ffffff;
                    color: #ffffff;
                    font-size: 16px;
                    font-weight: 800;
                    cursor: pointer;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    box-shadow: 0 0 25px rgba(247, 37, 133, 0.65);
                    z-index: 5;
                    transition: transform 0.15s, box-shadow 0.2s;
                    user-select: none;
                }}
                .center-button:hover {{
                    transform: translate(-50%, -50%) scale(1.08);
                    box-shadow: 0 0 35px rgba(247, 37, 133, 0.9);
                }}
                .center-button:active {{
                    transform: translate(-50%, -50%) scale(0.95);
                }}
                .result-card {{
                    display: none;
                    margin-top: 14px;
                    background: linear-gradient(135deg, rgba(33, 37, 56, 0.98), rgba(24, 27, 42, 0.99));
                    border: 2px solid #00f5d4;
                    border-radius: 18px;
                    padding: 18px 28px;
                    text-align: center;
                    max-width: 650px;
                    width: 95%;
                    box-shadow: 0 10px 40px rgba(0, 245, 212, 0.35);
                    animation: popIn 0.4s ease forwards;
                }}
                @keyframes popIn {{
                    0% {{ opacity: 0; transform: scale(0.85); }}
                    100% {{ opacity: 1; transform: scale(1); }}
                }}
                .confetti-canvas {{
                    position: fixed;
                    top: 0;
                    left: 0;
                    width: 100%;
                    height: 100%;
                    pointer-events: none;
                    z-index: 100;
                }}
            </style>
        </head>
        <body>
            <canvas id="confetti" class="confetti-canvas"></canvas>

            <!-- Indicador destacado em posição favorável -->
            <div class="pointer-indicator-box" id="indicatorBox">
                <div class="indicator-tag">🎯 LIVRO EM FOCO NA ROLETA</div>
                <div class="indicator-title" id="indicatorTitle">Clique em <b>GIRAR!</b> no centro da roleta para sortear</div>
                <div class="indicator-sub" id="indicatorSub">Sorteando entre todos os {fmt_milhar(total_elegiveis)} livros não lidos</div>
            </div>

            <div class="wheel-wrapper">
                <div class="pointer"></div>
                <canvas id="wheel" width="960" height="960"></canvas>
                <div class="center-button" id="spinBtn">GIRAR!</div>
            </div>

            <div class="result-card" id="resultModal">
                <div style="font-size: 13px; font-weight: 700; color: #00f5d4; text-transform: uppercase; letter-spacing: 1.5px;">
                    🎉 LIVRO SORTEADO PARA SUA PRÓXIMA LEITURA!
                </div>
                <div id="resTitle" style="font-size: 24px; font-weight: 800; color: #ffffff; margin: 8px 0;"></div>
                <div id="resAuthor" style="font-size: 15px; color: #cbd5e1; margin-bottom: 12px;"></div>
                <div style="display: flex; justify-content: center; gap: 10px; flex-wrap: wrap;">
                    <span id="resCat" style="background: rgba(247, 37, 133, 0.25); border: 1px solid #f72585; color: #ff70a6; padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: 600;"></span>
                    <span id="resTipo" style="background: rgba(67, 97, 238, 0.25); border: 1px solid #4361ee; color: #4cc9f0; padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: 600;"></span>
                    <span id="resPages" style="background: rgba(0, 245, 212, 0.2); border: 1px solid #00f5d4; color: #00f5d4; padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: 600;"></span>
                    <span id="resPrice" style="background: rgba(114, 9, 183, 0.3); border: 1px solid #7209b7; color: #e0aaff; padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: 600;"></span>
                </div>
            </div>

            <script>
                const books = {books_json_data};
                const canvas = document.getElementById('wheel');
                const ctx = canvas.getContext('2d');
                const spinBtn = document.getElementById('spinBtn');
                const resultModal = document.getElementById('resultModal');
                const indicatorTitle = document.getElementById('indicatorTitle');
                const indicatorSub = document.getElementById('indicatorSub');

                const colors = [
                    '#f72585', '#7209b7', '#3a0ca3', '#4361ee', 
                    '#4cc9f0', '#00f5d4', '#e63946', '#fb8500', 
                    '#8338ec', '#06d6a0', '#118ab2', '#ff006e'
                ];

                let startAngle = 0;
                const arc = (Math.PI * 2) / books.length;
                let spinTimeout = null;
                let spinAngleStart = 0;
                let spinTime = 0;
                let spinTimeTotal = 0;
                let isSpinning = false;
                let lastTickAngle = 0;
                let lastTickTime = 0;

                // Audio sintetizado (Web Audio API) para efeitos sonoros offline
                const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
                function playTick() {{
                    try {{
                        const osc = audioCtx.createOscillator();
                        const gain = audioCtx.createGain();
                        osc.type = 'triangle';
                        osc.frequency.setValueAtTime(520, audioCtx.currentTime);
                        gain.gain.setValueAtTime(0.06, audioCtx.currentTime);
                        gain.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + 0.04);
                        osc.connect(gain);
                        gain.connect(audioCtx.destination);
                        osc.start();
                        osc.stop(audioCtx.currentTime + 0.04);
                    }} catch (e) {{}}
                }}

                function playWin() {{
                    try {{
                        [523.25, 659.25, 783.99, 1046.50].forEach((freq, idx) => {{
                            setTimeout(() => {{
                                const osc = audioCtx.createOscillator();
                                const gain = audioCtx.createGain();
                                osc.type = 'sine';
                                osc.frequency.setValueAtTime(freq, audioCtx.currentTime);
                                gain.gain.setValueAtTime(0.12, audioCtx.currentTime);
                                gain.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + 0.3);
                                osc.connect(gain);
                                gain.connect(audioCtx.destination);
                                osc.start();
                                osc.stop(audioCtx.currentTime + 0.3);
                            }}, idx * 90);
                        }});
                    }} catch (e) {{}}
                }}

                function getBookUnderPointer() {{
                    // O ponteiro fica no topo (270 graus)
                    const deg = (270 - ((startAngle * 180 / Math.PI) % 360) + 360) % 360;
                    const arcd = 360 / books.length;
                    let idx = Math.floor(deg / arcd) % books.length;
                    if (idx < 0) idx += books.length;
                    return {{ book: books[idx], index: idx }};
                }}

                function drawWheel() {{
                    const outsideRadius = 460;
                    const textRadius = 310;
                    const insideRadius = 80;

                    ctx.clearRect(0, 0, canvas.width, canvas.height);

                    ctx.save();
                    ctx.shadowColor = 'rgba(0, 0, 0, 0.6)';
                    ctx.shadowBlur = 15;

                    for (let i = 0; i < books.length; i++) {{
                        const angle = startAngle + i * arc;
                        let colIdx = i % colors.length;
                        if (i === books.length - 1 && colIdx === 0) colIdx = 1;
                        ctx.fillStyle = colors[colIdx];

                        ctx.beginPath();
                        ctx.arc(480, 480, outsideRadius, angle, angle + arc, false);
                        ctx.arc(480, 480, insideRadius, angle + arc, angle, true);
                        ctx.fill();

                        // Linha divisória fina e limpa
                        ctx.strokeStyle = "rgba(255, 255, 255, 0.16)";
                        ctx.lineWidth = 1;
                        ctx.stroke();

                        // Se houver poucos livros (ex: <= 16), o texto cabe nas fatias
                        // Se houver muitos livros (ex: todos os 121), não sobrepomos textos:
                        // o livro é exibido com clareza total na caixa de destaque no topo!
                        if (books.length <= 16) {{
                            ctx.save();
                            ctx.fillStyle = "#ffffff";
                            ctx.translate(480 + Math.cos(angle + arc / 2) * textRadius, 
                                          480 + Math.sin(angle + arc / 2) * textRadius);
                            ctx.rotate(angle + arc / 2 + Math.PI / 2);
                            
                            let text = books[i].titulo;
                            if (text.length > 20) text = text.substring(0, 18) + "...";
                            
                            ctx.font = 'bold 20px Outfit, sans-serif';
                            ctx.textAlign = 'center';
                            ctx.fillText(text, 0, 0);
                            ctx.restore();
                        }} else {{
                            // Desenha um elegante pino na extremidade de cada fatia
                            ctx.save();
                            ctx.fillStyle = "#ffffff";
                            ctx.beginPath();
                            ctx.arc(
                                480 + Math.cos(angle + arc / 2) * (outsideRadius - 12),
                                480 + Math.sin(angle + arc / 2) * (outsideRadius - 12),
                                books.length > 60 ? 2 : 3,
                                0,
                                Math.PI * 2
                            );
                            ctx.fill();
                            ctx.restore();
                        }}
                    }}

                    // Aro externo elegante
                    ctx.beginPath();
                    ctx.arc(480, 480, outsideRadius, 0, Math.PI * 2);
                    ctx.lineWidth = 14;
                    ctx.strokeStyle = '#1b1e2f';
                    ctx.stroke();

                    // Borda neon externa
                    ctx.beginPath();
                    ctx.arc(480, 480, outsideRadius + 6, 0, Math.PI * 2);
                    ctx.lineWidth = 3;
                    ctx.strokeStyle = '#f72585';
                    ctx.stroke();

                    ctx.restore();
                }}

                function rotateWheel() {{
                    spinTime += 30;
                    if (spinTime >= spinTimeTotal) {{
                        stopRotateWheel();
                        return;
                    }}
                    const spinAngle = spinAngleStart - easeOut(spinTime, 0, spinAngleStart, spinTimeTotal);
                    startAngle += (spinAngle * Math.PI / 180);
                    
                    const now = Date.now();
                    if (Math.abs(startAngle - lastTickAngle) > Math.max(arc, 0.05) && (now - lastTickTime > 40)) {{
                        playTick();
                        lastTickAngle = startAngle;
                        lastTickTime = now;
                    }}

                    // Atualização em tempo real do livro sob o ponteiro na posição de destaque
                    const under = getBookUnderPointer();
                    if (under && under.book) {{
                        indicatorTitle.innerText = "📖 " + under.book.titulo;
                        indicatorSub.innerText = under.book.autor + " • " + under.book.categoria + " (" + under.book.tipo + ") • " + under.book.paginas + " págs";
                    }}

                    drawWheel();
                    spinTimeout = requestAnimationFrame(rotateWheel);
                }}

                function stopRotateWheel() {{
                    isSpinning = false;
                    const winnerData = getBookUnderPointer();
                    const winner = winnerData.book;
                    
                    playWin();
                    launchConfetti();

                    // Atualizar indicador destacado no topo com o título vencedor
                    indicatorTitle.innerHTML = "🎉 <span style='color:#00f5d4;'>" + winner.titulo + "</span>";
                    indicatorSub.innerText = "Vencedor do sorteio! " + winner.autor + " • " + winner.categoria;

                    // Exibir modal detalhado com todas as informações
                    document.getElementById('resTitle').innerText = winner.titulo;
                    document.getElementById('resAuthor').innerText = "por " + winner.autor;
                    document.getElementById('resCat').innerText = "🏷️ " + winner.categoria;
                    document.getElementById('resTipo').innerText = "📦 " + winner.tipo;
                    document.getElementById('resPages').innerText = "📄 " + winner.paginas + " páginas";
                    document.getElementById('resPrice').innerText = "💰 " + winner.valor;
                    
                    resultModal.style.display = 'block';
                }}

                function easeOut(t, b, c, d) {{
                    const ts = (t /= d) * t;
                    const tc = ts * t;
                    return b + c * (tc + -3 * ts + 3 * t);
                }}

                spinBtn.addEventListener('click', () => {{
                    if (isSpinning) return;
                    resultModal.style.display = 'none';
                    isSpinning = true;
                    spinAngleStart = Math.random() * 20 + 25;
                    spinTime = 0;
                    spinTimeTotal = Math.random() * 2000 + 4000;
                    rotateWheel();
                }});

                // Confetti Animation
                function launchConfetti() {{
                    const confCanvas = document.getElementById('confetti');
                    confCanvas.width = window.innerWidth;
                    confCanvas.height = window.innerHeight;
                    const cctx = confCanvas.getContext('2d');
                    const pieces = [];
                    const confettiColors = ['#f72585', '#4cc9f0', '#00f5d4', '#ffd166', '#7209b7'];
                    
                    for (let i = 0; i < 90; i++) {{
                        pieces.push({{
                            x: confCanvas.width / 2,
                            y: confCanvas.height / 2,
                            vx: (Math.random() - 0.5) * 16,
                            vy: (Math.random() - 0.7) * 16,
                            color: confettiColors[Math.floor(Math.random() * confettiColors.length)],
                            size: Math.random() * 8 + 4,
                            gravity: 0.25
                        }});
                    }}
                    
                    let frame = 0;
                    function anim() {{
                        cctx.clearRect(0, 0, confCanvas.width, confCanvas.height);
                        pieces.forEach(p => {{
                            p.x += p.vx;
                            p.y += p.vy;
                            p.vy += p.gravity;
                            cctx.fillStyle = p.color;
                            cctx.fillRect(p.x, p.y, p.size, p.size);
                        }});
                        frame++;
                        if (frame < 90) requestAnimationFrame(anim);
                        else cctx.clearRect(0, 0, confCanvas.width, confCanvas.height);
                    }}
                    anim();
                }}

                // Inicializar roleta com o livro sob o ponteiro
                drawWheel();
                const initUnder = getBookUnderPointer();
                if (initUnder && initUnder.book) {{
                    indicatorSub.innerText = "Sorteando entre todos os " + books.length + " livros não lidos disponíveis";
                }}
            </script>
        </body>
        </html>
        """
        
        components.html(roulette_html, height=840, scrolling=False)

        # Transparência: Tabela com todos os livros que estão concorrendo
        st.markdown("<br>", unsafe_allow_html=True)
        with st.expander(f"📋 Ver lista completa dos {fmt_milhar(total_elegiveis)} livros não lidos concorrendo ao sorteio"):
            expander_rows = []
            for _, r in df_roleta.iterrows():
                expander_rows.append(f"""
                    <tr style="border-bottom: 1px solid rgba(255, 255, 255, 0.05);">
                        <td style="padding: 9px 12px; font-weight: 600; color: #ffffff; font-size: 13px;">{r['Título']}</td>
                        <td style="padding: 9px 12px; color: #e2e8f0; font-size: 12.5px;">{r['Autor']}</td>
                        <td style="padding: 9px 12px; color: #a5b4fc; font-size: 12px; font-weight: 600;">{r['Categoria_Clean']}</td>
                        <td style="padding: 9px 12px; color: #4cc9f0; font-size: 12px; text-align: center;">{r['Tipo_Clean']}</td>
                        <td style="padding: 9px 12px; color: #ffffff; font-size: 12.5px; font-weight: 700; text-align: right;">{fmt_moeda(r['Valor'])}</td>
                        <td style="padding: 9px 12px; color: #e2e8f0; font-size: 12px; text-align: right;">{fmt_milhar(r['Número de páginas'])} págs</td>
                    </tr>
                """)
            st.html(textwrap.dedent(f"""
                <div style="background: #1c1f30; border-radius: 12px; overflow: hidden; max-height: 420px; overflow-y: auto;">
                    <table style="width: 100%; border-collapse: collapse; font-family: 'Outfit', sans-serif; text-align: left;">
                        <thead style="position: sticky; top: 0; background: #161826; z-index: 5;">
                            <tr style="border-bottom: 2px solid rgba(67, 97, 238, 0.4);">
                                <th style="padding: 10px 12px; color: #f8fafc; font-size: 12px; font-weight: 700;">Título</th>
                                <th style="padding: 10px 12px; color: #f8fafc; font-size: 12px; font-weight: 700;">Autor</th>
                                <th style="padding: 10px 12px; color: #f8fafc; font-size: 12px; font-weight: 700;">Categoria</th>
                                <th style="padding: 10px 12px; color: #f8fafc; font-size: 12px; font-weight: 700; text-align: center;">Formato</th>
                                <th style="padding: 10px 12px; color: #f8fafc; font-size: 12px; font-weight: 700; text-align: right;">Valor</th>
                                <th style="padding: 10px 12px; color: #f8fafc; font-size: 12px; font-weight: 700; text-align: right;">Páginas</th>
                            </tr>
                        </thead>
                        <tbody>
                            {''.join(expander_rows)}
                        </tbody>
                    </table>
                </div>
            """))

    # Backup / Sorteio Instantâneo via Streamlit
    st.markdown("<br>", unsafe_allow_html=True)
    with st.expander("🎲 Não consegue ver a roleta interativa? Sorteio Rápido Instantâneo"):
        if st.button("Sortear Próximo Livro Agora! 🚀", key="quick_spin"):
            if len(df_roleta) > 0:
                sorteado = df_roleta.sample(1).iloc[0]
                st.balloons()
                st.success(f"### 🎉 Livro Sorteado: **{sorteado['Título']}**")
                col_s1, col_s2, col_s3, col_s4 = st.columns(4)
                col_s1.metric("Autor", sorteado['Autor'])
                col_s2.metric("Categoria", sorteado['Categoria_Clean'])
                col_s3.metric("Formato", sorteado['Tipo_Clean'])
                col_s4.metric("Páginas / Valor", f"{fmt_milhar(sorteado['Número de páginas'])} págs | {fmt_moeda(sorteado['Valor'])}")

# =============================================================================
# PÁGINA 3: CATÁLOGO COMPLETO & EXPLORAÇÃO
# =============================================================================
elif st.session_state.current_page == 'catalogo':
    st.markdown("""
        <div class="page-title">Catálogo Completo da Biblioteca</div>
        <div style="color: #f1f5f9; font-size: 14.5px; margin-bottom: 20px; font-weight: 500;">
            Consulte todos os 185 títulos cadastrados, filtre por categoria, formato e status de leitura.
        </div>
    """, unsafe_allow_html=True)

    # Caixa de Filtros no tom escuro do Dashboard
    with st.container(border=True):
        st.markdown("""
            <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 10px;">
                <span class="card-badge badge-cyan"></span>
                <span style="font-size: 14px; font-weight: 700; color: #ffffff; text-transform: uppercase; letter-spacing: 0.6px;">Painel de Filtros e Segmentação</span>
            </div>
        """, unsafe_allow_html=True)
        col_f1, col_f2, col_f3 = st.columns(3)
        with col_f1:
            cat_filter = st.multiselect("Filtrar por Categoria:", options=sorted(df_raw['Categoria_Clean'].unique().tolist()), placeholder="Todas as categorias")
        with col_f2:
            status_filter = st.multiselect("Filtrar por Status:", options=["Lido", "Não Lido"], placeholder="Todos os status")
        with col_f3:
            tipo_filter = st.multiselect("Filtrar por Tipo:", options=["Físico", "Ebook"], placeholder="Todos os formatos")

    df_view = df_raw.copy()
    if cat_filter:
        df_view = df_view[df_view['Categoria_Clean'].isin(cat_filter)]
    if status_filter:
        df_view = df_view[df_view['Status_Clean'].isin(status_filter)]
    if tipo_filter:
        df_view = df_view[df_view['Tipo_Clean'].isin(tipo_filter)]

    # Linha de 4 Cartões de KPI integrados ao tema escuro
    st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
    col_m1, col_m2, col_m3, col_m4 = st.columns(4)
    with col_m1:
        with st.container(border=True):
            st.markdown(f"""
                <div style="font-size: 12.5px; color: #f1f5f9; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px;">Títulos Selecionados</div>
                <div style="font-size: 28px; font-weight: 700; color: #ffffff; margin: 4px 0;">{fmt_milhar(len(df_view))}</div>
                <div style="font-size: 13px; color: #e2e8f0; font-weight: 600;">de {fmt_milhar(len(df_raw))} livros no acervo</div>
            """, unsafe_allow_html=True)
    with col_m2:
        with st.container(border=True):
            lidos_view = len(df_view[df_view['Status_Clean'] == 'Lido'])
            pct_view = (lidos_view / len(df_view) * 100) if len(df_view) > 0 else 0
            st.markdown(f"""
                <div style="font-size: 12.5px; color: #f1f5f9; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px;">Livros Lidos</div>
                <div style="font-size: 28px; font-weight: 700; color: #00f5d4; margin: 4px 0;">{fmt_milhar(lidos_view)}</div>
                <div style="font-size: 13px; color: #e2e8f0; font-weight: 600;">{fmt_pct(pct_view)} do filtro concluído</div>
            """, unsafe_allow_html=True)
    with col_m3:
        with st.container(border=True):
            valor_view = df_view['Valor'].sum()
            st.markdown(f"""
                <div style="font-size: 12.5px; color: #f1f5f9; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px;">Investimento</div>
                <div style="font-size: 25px; font-weight: 700; color: #ffffff; margin: 4px 0;">{fmt_moeda(valor_view)}</div>
                <div style="font-size: 13px; color: #e2e8f0; font-weight: 600;">méd. {fmt_moeda(valor_view / len(df_view) if len(df_view) else 0)} / livro</div>
            """, unsafe_allow_html=True)
    with col_m4:
        with st.container(border=True):
            pags_view = df_view['Número de páginas'].sum()
            st.markdown(f"""
                <div style="font-size: 12.5px; color: #f1f5f9; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px;">Total de Páginas</div>
                <div style="font-size: 28px; font-weight: 700; color: #f72585; margin: 4px 0;">{fmt_milhar(pags_view)}</div>
                <div style="font-size: 13px; color: #e2e8f0; font-weight: 600;">média {fmt_milhar(round(pags_view / len(df_view) if len(df_view) else 0))} págs/livro</div>
            """, unsafe_allow_html=True)

    # ------------------ SEÇÃO: BUSCAR LIVRO NA COLEÇÃO E MARCAR COMO LIDO ------------------
    st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
    with st.container(border=True):
        st.markdown("""
            <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px; flex-wrap: wrap; gap: 8px;">
                <div style="display: flex; align-items: center; gap: 8px;">
                    <span class="card-badge badge-emerald"></span>
                    <span style="font-size: 14px; font-weight: 700; color: #ffffff; text-transform: uppercase; letter-spacing: 0.6px;">Gerenciar Leitura: Buscar Título e Atualizar Status</span>
                </div>
                <div style="font-size: 12px; color: #00f5d4; font-weight: 600; background: rgba(0,245,212,0.12); padding: 4px 10px; border-radius: 12px; border: 1px solid rgba(0,245,212,0.3);">
                    ⚡ Atualização Instantânea no Dashboard
                </div>
            </div>
        """, unsafe_allow_html=True)

        # Preparar opções de busca: Não Lidos primeiro (com ícone ⏳), depois Lidos (com ícone ✓)
        df_nao_lidos_opts = df_raw[df_raw['Status_Clean'] == 'Não Lido'].sort_values('Título')
        df_lidos_opts = df_raw[df_raw['Status_Clean'] == 'Lido'].sort_values('Título')

        titulos_dict = {}
        for _, r in df_nao_lidos_opts.iterrows():
            titulos_dict[f"⏳ {r['Título']}  —  {r['Autor']} (Pendente)"] = r['Título']
        for _, r in df_lidos_opts.iterrows():
            titulos_dict[f"✓ {r['Título']}  —  {r['Autor']} (Já Lido)"] = r['Título']

        col_find, col_action = st.columns([6, 4])
        
        with col_find:
            st.markdown("<label style='color: #f8fafc; font-size: 13.5px; font-weight: 700;'>🔍 Digite ou selecione o título do livro:</label>", unsafe_allow_html=True)
            book_selection = st.selectbox(
                "Buscar livro para marcar como lido:",
                options=["— Selecione um livro para gerenciar leitura —"] + list(titulos_dict.keys()),
                label_visibility="collapsed",
                key="reader_book_picker",
                help="Comece a digitar o título ou autor para filtrar a lista."
            )

            if book_selection and book_selection != "— Selecione um livro para gerenciar leitura —":
                sel_title = titulos_dict[book_selection]
                book_info = df_raw[df_raw['Título'] == sel_title].iloc[0]

                is_lido = book_info['Status_Clean'] == 'Lido'
                status_tag = '<span style="background: rgba(0, 245, 212, 0.15); color: #00f5d4; border: 1px solid rgba(0, 245, 212, 0.5); padding: 3px 10px; border-radius: 12px; font-weight: 700; font-size: 12px;">✓ Status: Lido</span>' if is_lido else '<span style="background: rgba(247, 37, 133, 0.15); color: #ff70a6; border: 1px solid rgba(247, 37, 133, 0.5); padding: 3px 10px; border-radius: 12px; font-weight: 700; font-size: 12px;">⏳ Status: Não Lido</span>'
                tipo_tag = f'<span style="background: rgba(67, 97, 238, 0.2); color: #93c5fd; padding: 3px 9px; border-radius: 6px; font-size: 12px; font-weight: 600;">{book_info["Tipo_Clean"]}</span>'
                cat_tag = f'<span style="background: rgba(165, 180, 252, 0.2); color: #a5b4fc; padding: 3px 9px; border-radius: 6px; font-size: 12px; font-weight: 600;">{book_info["Categoria_Clean"]}</span>'
                pags_tag = f'<span style="background: rgba(255, 255, 255, 0.08); color: #f1f5f9; padding: 3px 9px; border-radius: 6px; font-size: 12px; font-weight: 600;">{fmt_milhar(book_info["Número de páginas"])} págs</span>'
                preco_tag = f'<span style="background: rgba(255, 255, 255, 0.08); color: #f1f5f9; padding: 3px 9px; border-radius: 6px; font-size: 12px; font-weight: 600;">{fmt_moeda(book_info["Valor"])}</span>'

                st.markdown(f"""
                    <div style="background: #1c1f30; padding: 14px 18px; border-radius: 12px; border: 1px solid rgba(255,255,255,0.08); margin-top: 10px;">
                        <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 6px;">
                            <div style="font-size: 16.5px; font-weight: 700; color: #ffffff;">{book_info['Título']}</div>
                            <div>{status_tag}</div>
                        </div>
                        <div style="font-size: 13.5px; color: #cbd5e1; margin-bottom: 10px;">Autor(a): <b style="color: #fff;">{book_info['Autor']}</b></div>
                        <div style="display: flex; gap: 8px; flex-wrap: wrap;">
                            {tipo_tag} {cat_tag} {pags_tag} {preco_tag}
                        </div>
                    </div>
                """, unsafe_allow_html=True)

        with col_action:
            if book_selection and book_selection != "— Selecione um livro para gerenciar leitura —":
                sel_title = titulos_dict[book_selection]
                book_info = df_raw[df_raw['Título'] == sel_title].iloc[0]
                is_lido = book_info['Status_Clean'] == 'Lido'

                if not is_lido:
                    st.markdown("<label style='color: #f8fafc; font-size: 13.5px; font-weight: 700;'>⭐ Atribuir Avaliação (Opcional):</label>", unsafe_allow_html=True)
                    nota_sel = st.select_slider(
                        "Avaliação:",
                        options=[1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0],
                        value=4.5,
                        format_func=lambda x: f"⭐ {x:.1f}",
                        label_visibility="collapsed",
                        key="read_grade_slider"
                    )
                    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
                    if st.button(f"✅ Marcar '{sel_title[:24]}...' como Lido!", type="primary", use_container_width=True, key="btn_confirm_read"):
                        update_book_status(sel_title, "Lido", nova_nota=nota_sel)
                        st.balloons()
                        st.toast(f"🎉 Parabéns pela leitura! '{sel_title}' foi marcado como Lido!")
                        st.rerun()
                else:
                    nota_atual = float(book_info['Nota']) if pd.notna(book_info['Nota']) and book_info['Nota'] > 0 else 4.5
                    st.markdown(f"""
                        <div style="background: rgba(0, 245, 212, 0.08); border: 1px solid rgba(0, 245, 212, 0.25); border-radius: 12px; padding: 12px 16px; margin-top: 2px;">
                            <div style="color: #00f5d4; font-weight: 700; font-size: 14px;">🎉 Este livro já foi lido!</div>
                            <div style="color: #cbd5e1; font-size: 12.5px; margin-top: 2px;">Avaliação registrada: <b style="color: #ffd166;">⭐ {nota_atual:.1f}</b></div>
                        </div>
                    """, unsafe_allow_html=True)
                    col_act1, col_act2 = st.columns(2)
                    with col_act1:
                        st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
                        nova_nota_update = st.select_slider(
                            "Alterar Nota:",
                            options=[1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0],
                            value=nota_atual,
                            format_func=lambda x: f"⭐ {x:.1f}",
                            key="slider_change_grade"
                        )
                        if st.button("⭐ Salvar Nova Nota", use_container_width=True, key="btn_update_grade"):
                            update_book_status(sel_title, "Lido", nova_nota=nova_nota_update)
                            st.toast("Nota atualizada com sucesso!")
                            st.rerun()
                    with col_act2:
                        st.markdown("<div style='height: 38px;'></div>", unsafe_allow_html=True)
                        if st.button("↩️ Desmarcar Lido", use_container_width=True, key="btn_undo_read"):
                            update_book_status(sel_title, "Não Lido", nova_nota=None)
                            st.toast(f"'{sel_title}' voltou para Não Lido.")
                            st.rerun()
            else:
                st.markdown("""
                    <div style="background: #1c1f30; padding: 22px; border-radius: 12px; border: 1px dashed rgba(255,255,255,0.15); text-align: center; height: 100%; display: flex; flex-direction: column; justify-content: center; align-items: center; min-height: 125px;">
                        <div style="font-size: 26px; margin-bottom: 6px;">📖</div>
                        <div style="color: #f8fafc; font-size: 14px; font-weight: 700;">Selecione um título ao lado</div>
                        <div style="color: #cbd5e1; font-size: 12.5px; margin-top: 4px;">Você poderá marcar como lido, atribuir notas ou gerenciar o status da sua coleção.</div>
                    </div>
                """, unsafe_allow_html=True)

    # Busca instantânea no catálogo
    st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
    with st.container(border=True):
        col_t_head, col_t_search = st.columns([6, 4])
        with col_t_head:
            st.markdown("""
                <div style="display: flex; align-items: center; gap: 8px; margin-top: 4px;">
                    <span class="card-badge badge-purple"></span>
                    <span style="font-size: 14px; font-weight: 700; color: #ffffff; text-transform: uppercase; letter-spacing: 0.6px;">Catálogo Completo dos Títulos</span>
                </div>
            """, unsafe_allow_html=True)
        with col_t_search:
            cat_query = st.text_input("Buscar:", placeholder="🔍 Buscar por título ou autor...", label_visibility="collapsed", key="cat_search_input")

        df_table = df_view.copy()
        if cat_query:
            q = cat_query.lower().strip()
            df_table = df_table[
                df_table['Título'].str.lower().str.contains(q, na=False) |
                df_table['Autor'].str.lower().str.contains(q, na=False) |
                df_table['Categoria_Clean'].str.lower().str.contains(q, na=False)
            ]

        # Renderização da Tabela HTML estilizada exatamente no tom escuro do Dashboard
        table_rows_html = []
        if len(df_table) == 0:
            table_rows_html.append("""
                <tr>
                    <td colspan="8" style="padding: 36px 20px; text-align: center; color: #cbd5e1; font-size: 14.5px; font-weight: 500;">
                        🔍 Nenhum título encontrado com o filtro atual ou termo de busca.
                    </td>
                </tr>
            """)
        else:
            for idx_row, (_, r) in enumerate(df_table.iterrows()):
                # Badge de Status
                if r['Status_Clean'] == 'Lido':
                    s_badge = '<span style="background: rgba(0, 245, 212, 0.15); color: #00f5d4; border: 1px solid rgba(0, 245, 212, 0.5); padding: 3px 9px; border-radius: 20px; font-weight: 700; font-size: 11.5px; white-space: nowrap;">✓ Lido</span>'
                else:
                    s_badge = '<span style="background: rgba(247, 37, 133, 0.15); color: #ff70a6; border: 1px solid rgba(247, 37, 133, 0.5); padding: 3px 9px; border-radius: 20px; font-weight: 700; font-size: 11.5px; white-space: nowrap;">⏳ Pendente</span>'
                
                # Badge de Formato
                if r['Tipo_Clean'] == 'Físico':
                    t_badge = '<span style="background: rgba(67, 97, 238, 0.2); color: #93c5fd; border: 1px solid rgba(67, 97, 238, 0.4); padding: 3px 8px; border-radius: 8px; font-weight: 600; font-size: 11.5px; white-space: nowrap;">📘 Físico</span>'
                else:
                    t_badge = '<span style="background: rgba(76, 201, 240, 0.2); color: #67e8f9; border: 1px solid rgba(76, 201, 240, 0.4); padding: 3px 8px; border-radius: 8px; font-weight: 600; font-size: 11.5px; white-space: nowrap;">📱 E-book</span>'

                # Avaliação
                n_val = r['Nota']
                if pd.isna(n_val) or n_val == 0:
                    nota_str = '<span style="color: #94a3b8; font-size: 12px; font-weight: 500;">—</span>'
                else:
                    nota_str = f'<span style="color: #ffd166; font-weight: 700; font-size: 12.5px;">⭐ {float(n_val):.1f}</span>'

                val_str = fmt_moeda(r['Valor'])
                pags_num = int(r['Número de páginas'])
                pags_str = f"{fmt_milhar(pags_num)} págs" if pags_num > 0 else "—"

                row_bg = "#212538" if idx_row % 2 == 0 else "#1c2033"
                table_rows_html.append(f"""
                    <tr style="background-color: {row_bg}; border-bottom: 1px solid rgba(255, 255, 255, 0.05);">
                        <td style="padding: 11px 14px; font-weight: 600; color: #ffffff; font-size: 13.5px; max-width: 280px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;" title="{r['Título']}">{r['Título']}</td>
                        <td style="padding: 11px 14px; color: #e2e8f0; font-size: 13px; font-weight: 500; white-space: nowrap;">{r['Autor']}</td>
                        <td style="padding: 11px 14px; color: #a5b4fc; font-size: 12.5px; font-weight: 600; white-space: nowrap;">{r['Categoria_Clean']}</td>
                        <td style="padding: 11px 14px; text-align: center;">{s_badge}</td>
                        <td style="padding: 11px 14px; text-align: center;">{t_badge}</td>
                        <td style="padding: 11px 14px; text-align: center;">{nota_str}</td>
                        <td style="padding: 11px 14px; text-align: right; color: #ffffff; font-weight: 700; font-size: 13px; white-space: nowrap;">{val_str}</td>
                        <td style="padding: 11px 14px; text-align: right; color: #e2e8f0; font-size: 12.5px; font-weight: 600; white-space: nowrap;">{pags_str}</td>
                    </tr>
                """)

        rows_joined = "".join(table_rows_html)
        catalog_table_markup = f"""
        <div style="background: #212538; border: 1px solid rgba(255, 255, 255, 0.12); border-radius: 14px; overflow: hidden; box-shadow: 0 8px 24px rgba(0,0,0,0.3); margin-top: 8px;">
            <div style="max-height: 540px; overflow-y: auto; overflow-x: auto;">
                <table style="width: 100%; border-collapse: collapse; font-family: 'Outfit', -apple-system, sans-serif; text-align: left;">
                    <thead style="position: sticky; top: 0; background: #161826; z-index: 10; box-shadow: 0 2px 8px rgba(0,0,0,0.4);">
                        <tr style="border-bottom: 2px solid rgba(67, 97, 238, 0.4);">
                            <th style="padding: 13px 14px; color: #f8fafc; font-size: 12.5px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.6px;">Título da Obra</th>
                            <th style="padding: 13px 14px; color: #f8fafc; font-size: 12.5px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.6px;">Autor(a)</th>
                            <th style="padding: 13px 14px; color: #f8fafc; font-size: 12.5px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.6px;">Categoria</th>
                            <th style="padding: 13px 14px; color: #f8fafc; font-size: 12.5px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.6px; text-align: center;">Status</th>
                            <th style="padding: 13px 14px; color: #f8fafc; font-size: 12.5px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.6px; text-align: center;">Formato</th>
                            <th style="padding: 13px 14px; color: #f8fafc; font-size: 12.5px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.6px; text-align: center;">Avaliação</th>
                            <th style="padding: 13px 14px; color: #f8fafc; font-size: 12.5px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.6px; text-align: right;">Valor</th>
                            <th style="padding: 13px 14px; color: #f8fafc; font-size: 12.5px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.6px; text-align: right;">Páginas</th>
                        </tr>
                    </thead>
                    <tbody>
                        {rows_joined}
                    </tbody>
                </table>
            </div>
        </div>
        """
        st.html(textwrap.dedent(catalog_table_markup))

        # Rodapé com contagem e exportação CSV
        col_foot_left, col_foot_right = st.columns([7, 3])
        with col_foot_left:
            st.markdown(f"<div style='color: #e2e8f0; font-size: 13px; font-weight: 600; margin-top: 12px;'>📊 Exibindo <b>{fmt_milhar(len(df_table))}</b> de <b>{fmt_milhar(len(df_raw))}</b> livros cadastrados no acervo.</div>", unsafe_allow_html=True)
        with col_foot_right:
            st.markdown("<div style='height: 4px;'></div>", unsafe_allow_html=True)
            display_cols = ['Título', 'Autor', 'Categoria_Clean', 'Status_Clean', 'Tipo_Clean', 'Nota', 'Valor', 'Número de páginas']
            rename_cols = {
                'Categoria_Clean': 'Categoria',
                'Status_Clean': 'Status',
                'Tipo_Clean': 'Tipo',
                'Valor': 'Valor (R$)',
                'Número de páginas': 'Nº Páginas'
            }
            csv_data = df_table[display_cols].rename(columns=rename_cols).to_csv(index=False).encode('utf-8-sig')
            st.download_button(
                label="📥 Exportar Tabela (CSV)",
                data=csv_data,
                file_name="catalogo_biblioteca.csv",
                mime="text/csv",
                use_container_width=True
            )
