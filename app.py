import streamlit as st

@st.cache_data
def load_data():
    """Carrega e processa os dados dos arquivos Excel"""
    try:
        emissoes_df = pd.read_excel("EMISSOES_KM.xlsx")
        emissoes_df.columns = emissoes_df.columns.str.strip().str.upper()
        emissoes_df['DATA_EMISSÃO'] = pd.to_datetime(emissoes_df['DATA_EMISSÃO'])

        cancelamentos_df = pd.read_excel("CANCELAMENTOS_KM.xlsx")
        cancelamentos_df.columns = cancelamentos_df.columns.str.strip().str.upper()
        cancelamentos_df['DATA_CANCELADO'] = pd.to_datetime(cancelamentos_df['DATA_CANCELADO'])

        return emissoes_df, cancelamentos_df

    except Exception as e:
        st.error(f"Erro ao carregar os dados: {e}")
        return None, None


import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date
import numpy as np

# Configuração da página
st.set_page_config(
    page_title="Dashboard KM - Controle de Emissões e Cancelamentos",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado para estilização
st.markdown("""
<style>
    /* Importar fonte Google */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Reset e configurações globais */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }
    
    /* Header principal */
    .main-header {
        font-family: 'Inter', sans-serif;
        font-size: 2.8rem;
        font-weight: 700;
        color: #1e40af;
        text-align: center;
        margin-bottom: 2rem;
        padding: 2rem;
        background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 50%, #bae6fd 100%);
        border-radius: 16px;
        border: 1px solid #e0f2fe;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        position: relative;
        overflow: hidden;
    }
    
    .main-header::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, #3b82f6, #1d4ed8, #1e40af);
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background-color: #f8fafc;
        border-right: 2px solid #e2e8f0;
    }
    
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #f8fafc 0%, #f1f5f9 100%);
        padding: 1.5rem 1rem;
    }
    
    /* Filtros sidebar - CSS corrigido para selectbox */
    .stSelectbox > div > div > div {
        background-color: white !important;
        border: 2px solid #e2e8f0 !important;
        border-radius: 8px !important;
        color: #1f2937 !important;
    }
    
    .stSelectbox > div > div > div > div {
        color: #1f2937 !important;
        font-weight: 500 !important;
    }
    
    .stSelectbox input {
        color: #1f2937 !important;
        background-color: white !important;
    }
    
    .stSelectbox [data-baseweb="select"] {
        color: #1f2937 !important;
    }
    
    .stSelectbox [data-baseweb="select"] > div {
        color: #1f2937 !important;
        background-color: white !important;
    }
    
    /* Métricas */
    [data-testid="metric-container"] {
        background: white;
        border: 1px solid #e2e8f0;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);
        transition: all 0.2s ease;
    }
    
    [data-testid="metric-container"]:hover {
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        transform: translateY(-2px);
    }
    
    [data-testid="metric-container"] > div {
        font-family: 'Inter', sans-serif;
    }
    
    [data-testid="metric-container"] [data-testid="metric-label"] {
        font-size: 0.875rem;
        font-weight: 500;
        color: #64748b;
        margin-bottom: 0.5rem;
    }
    
    [data-testid="metric-container"] [data-testid="metric-value"] {
        font-size: 1.875rem;
        font-weight: 700;
        color: #1e293b;
    }
    
    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 12px;
        background-color: #f8fafc;
        padding: 12px;
        border-radius: 16px;
        border: 1px solid #e2e8f0;
        display: flex;
        justify-content: space-between;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 60px;
        white-space: pre-wrap;
        background-color: transparent;
        border-radius: 12px;
        color: #64748b;
        font-weight: 500;
        font-family: 'Inter', sans-serif;
        transition: all 0.3s ease;
        padding: 12px 20px;
        flex: 1;
        display: flex;
        align-items: center;
        justify-content: center;
        text-align: center;
        font-size: 1.3rem;  /* ou 18px */
        border: 2px solid transparent;
        min-width: 0;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%) !important;
        color: white !important;
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
        font-weight: 600;
        transform: translateY(-2px);
        border: 2px solid #1d4ed8;
    }
    
    .stTabs [data-baseweb="tab"]:hover:not([aria-selected="true"]) {
        background-color: white;
        color: #3b82f6;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        transform: translateY(-1px);
        border: 2px solid #e2e8f0;
    }
    
    /* Responsividade para as abas */
    @media (max-width: 768px) {
        .stTabs [data-baseweb="tab-list"] {
            flex-wrap: wrap;
            gap: 8px;
        }
        
        .stTabs [data-baseweb="tab"] {
            height: 50px;
            font-size: 0.85rem;
            padding: 8px 12px;
            min-width: calc(50% - 4px);
        }
    }
    
    @media (max-width: 480px) {
        .stTabs [data-baseweb="tab"] {
            min-width: 100%;
            margin-bottom: 4px;
        }
    }
    
    /* Botões */
    .stButton > button {
        background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        font-family: 'Inter', sans-serif;
        transition: all 0.2s ease;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #2563eb 0%, #1e40af 100%);
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        transform: translateY(-1px);
    }
    
    /* Download button */
    .stDownloadButton > button {
        background: linear-gradient(135deg, #059669 0%, #047857 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        font-family: 'Inter', sans-serif;
        transition: all 0.2s ease;
    }
    
    .stDownloadButton > button:hover {
        background: linear-gradient(135deg, #047857 0%, #065f46 100%);
        transform: translateY(-1px);
    }
    
    /* Dataframes */
    .stDataFrame {
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
    }
    
    /* Headers das seções */
    h1, h2, h3 {
        font-family: 'Inter', sans-serif;
        color: #1e293b;
        font-weight: 600;
    }
    
    /* Plotly charts container */
    .js-plotly-plot {
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
    }
    
    /* Animações */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .main .block-container > div {
        animation: fadeIn 0.5s ease-out;
    }
    
    /* Responsividade */
    @media (max-width: 768px) {
        .main-header {
            font-size: 2rem;
            padding: 1.5rem;
        }
        
        [data-testid="metric-container"] {
            padding: 1rem;
        }
        
        [data-testid="metric-container"] [data-testid="metric-value"] {
            font-size: 1.5rem;
        }
    }
    
    /* Status indicators */
    .status-success {
        color: #059669;
        background-color: #d1fae5;
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.875rem;
        font-weight: 500;
    }
    
    .status-warning {
        color: #d97706;
        background-color: #fef3c7;
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.875rem;
        font-weight: 500;
    }
</style>
""", unsafe_allow_html=True)

def format_number(num):
    """Formata números no padrão brasileiro"""
    if pd.isna(num) or num is None:
        return "0"
    try:
        return f"{int(num):,}".replace(",", ".")
    except (ValueError, TypeError):
        return "0"

def main():
    # Título principal
    st.markdown('<div class="main-header">📊 Dashboard KM - Controle de Emissões e Cancelamentos</div>', unsafe_allow_html=True)
    
    # Carregando dados
    emissoes_df, cancelamentos_df = load_data()
    
    if emissoes_df is None or cancelamentos_df is None:
        st.error("Não foi possível carregar os dados. Verifique os arquivos.")
        return
    
    # Sidebar com filtros
    st.sidebar.header("🔍 Filtros")
    
    # Filtro de Período (Calendário)
    st.sidebar.subheader("📅 Período")
    min_date = emissoes_df['DATA_EMISSÃO'].min().date()
    max_date = emissoes_df['DATA_EMISSÃO'].max().date()
    
    date_range = st.sidebar.date_input(
        "Selecione o período:",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )
    
    # Filtro de Mês
    st.sidebar.subheader("📆 Mês")
    meses_ordem = ['JANEIRO', 'FEVEREIRO', 'MARÇO', 'ABRIL', 'MAIO', 'JUNHO', 
                   'JULHO', 'AGOSTO', 'SETEMBRO', 'OUTUBRO', 'NOVEMBRO', 'DEZEMBRO']
    meses_disponiveis = [mes for mes in meses_ordem if mes in emissoes_df['MÊS'].unique()]
    
    mes_selecionado = st.sidebar.selectbox(
        "Selecione o mês:",
        options=['Todos'] + meses_disponiveis,
        index=0
    )
    
    # Filtro de Expedição
    st.sidebar.subheader("🚛 Expedição")
    expedicoes_disponiveis = sorted(emissoes_df['EXPEDIÇÃO'].unique())
    
    expedicao_selecionada = st.sidebar.selectbox(
        "Selecione a expedição:",
        options=['Todas'] + expedicoes_disponiveis,
        index=0
    )
    
    # Filtro de Usuários
    st.sidebar.subheader("👥 Usuários")
    # Combinar usuários de emissões e cancelamentos, removendo espaços
    usuarios_emissoes = set(emissoes_df['USUARIO'].str.strip().unique())
    usuarios_cancelamentos = set(cancelamentos_df['USUARIO'].str.strip().unique())
    usuarios_disponiveis = sorted(usuarios_emissoes.union(usuarios_cancelamentos))
    
    usuario_selecionado = st.sidebar.selectbox(
        "Selecione o usuário:",
        options=['Todos'] + usuarios_disponiveis,
        index=0
    )
    
    # Aplicando filtros
    df_filtrado = emissoes_df.copy()
    cancelamentos_filtrado = cancelamentos_df.copy()
    
    # Filtro de data
    if isinstance(date_range, tuple) and len(date_range) == 2:
        start_date, end_date = date_range
        df_filtrado = df_filtrado[
            (df_filtrado['DATA_EMISSÃO'].dt.date >= start_date) & 
            (df_filtrado['DATA_EMISSÃO'].dt.date <= end_date)
        ]
    
    # Filtro de mês
    if mes_selecionado != 'Todos':
        df_filtrado = df_filtrado[df_filtrado['MÊS'] == mes_selecionado]
        cancelamentos_filtrado = cancelamentos_filtrado[cancelamentos_filtrado['MÊS'] == mes_selecionado]
    
    # Filtro de expedição
    if expedicao_selecionada != 'Todas':
        df_filtrado = df_filtrado[df_filtrado['EXPEDIÇÃO'] == expedicao_selecionada]
        cancelamentos_filtrado = cancelamentos_filtrado[cancelamentos_filtrado['EXPEDIÇÃO'] == expedicao_selecionada]
    
    # Filtro de usuário
    if usuario_selecionado != 'Todos':
        # Para emissões, usar USUÁRIO com trim
        df_filtrado = df_filtrado[df_filtrado['USUARIO'].str.strip() == usuario_selecionado.strip()]
        # Para cancelamentos, usar USUARIO com trim
        cancelamentos_filtrado = cancelamentos_filtrado[cancelamentos_filtrado['USUARIO'].str.strip() == usuario_selecionado.strip()]
    
    # Botão para limpar filtros
    if st.sidebar.button("🔄 Limpar Todos os Filtros"):
        st.rerun()
    
    # Informações dos filtros aplicados
    st.sidebar.markdown("---")
    st.sidebar.subheader("📋 Resumo dos Filtros")
    st.sidebar.write(f"📊 **Total de Emissões:** {format_number(df_filtrado['CTRC_EMITIDO'].sum())}")
    st.sidebar.write(f"❌ **Total de Cancelamentos:** {len(cancelamentos_filtrado):,}".replace(",", "."))
    
    # Abas principais
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Visão Geral", 
        "📈 Análise Temporal", 
        "⚡ Produtividade", 
        "❌ Cancelamentos", 
        "📋 Dados Detalhados"
    ])
    
    with tab1:
        st.header("📊 Visão Geral")
        
        # Calculando KPIs
        total_emissoes = df_filtrado['CTRC_EMITIDO'].sum()
        total_cancelamentos = len(cancelamentos_filtrado)
        taxa_cancelamento = (total_cancelamentos / total_emissoes * 100) if total_emissoes > 0 else 0
        meta_taxa = 0.75
        
        # Indicador de meta
        if taxa_cancelamento <= meta_taxa:
            status_meta = "✅ Dentro da Meta"
            cor_meta = "success"
        else:
            status_meta = "⚠️ Fora da Meta"
            cor_meta = "warning"
        
        # KPIs com design moderno em cartões coloridos
        st.markdown("""
        <style>
        .kpi-card {
            background: linear-gradient(135deg, var(--card-color-1), var(--card-color-2));
            padding: 2rem;
            border-radius: 16px;
            color: white;
            text-align: center;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
            margin-bottom: 1rem;
            position: relative;
            overflow: hidden;
        }
        
        .kpi-card::before {
            content: '';
            position: absolute;
            top: -50%;
            right: -50%;
            width: 100%;
            height: 100%;
            background: rgba(255,255,255,0.1);
            border-radius: 50%;
            transform: rotate(45deg);
        }
        
        .kpi-icon {
            font-size: 2rem;
            margin-bottom: 0.5rem;
            position: relative;
            z-index: 1;
        }
        
        .kpi-value {
            font-size: 2.5rem;
            font-weight: 700;
            margin: 0.5rem 0;
            position: relative;
            z-index: 1;
        }
        
        .kpi-label {
            font-size: 1rem;
            opacity: 0.9;
            position: relative;
            z-index: 1;
        }
        
        .kpi-blue {
            --card-color-1: #3b82f6;
            --card-color-2: #1d4ed8;
        }
        
        .kpi-red {
            --card-color-1: #ef4444;
            --card-color-2: #dc2626;
        }
        
        .kpi-purple {
            --card-color-1: #8b5cf6;
            --card-color-2: #7c3aed;
        }
        
        .kpi-orange {
            --card-color-1: #f97316;
            --card-color-2: #ea580c;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Exibindo KPIs em cartões coloridos
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="kpi-card kpi-blue">
                <div class="kpi-icon">📈</div>
                <div class="kpi-value">{format_number(total_emissoes)}</div>
                <div class="kpi-label">Total de Emissões<br>CTRCs emitidos</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="kpi-card kpi-red">
                <div class="kpi-icon">❌</div>
                <div class="kpi-value">{format_number(total_cancelamentos)}</div>
                <div class="kpi-label">Total de Cancelamentos<br>CTRCs cancelados</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="kpi-card kpi-purple">
                <div class="kpi-icon">📊</div>
                <div class="kpi-value">{taxa_cancelamento:.2f}%</div>
                <div class="kpi-label">Taxa de Cancelamento<br>Percentual atual</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            cor_classe = "kpi-orange" if taxa_cancelamento > meta_taxa else "kpi-blue"
            icone_meta = "⚠️" if taxa_cancelamento > meta_taxa else "✅"
            st.markdown(f"""
            <div class="kpi-card {cor_classe}">
                <div class="kpi-icon">{icone_meta}</div>
                <div class="kpi-value">0.75%</div>
                <div class="kpi-label">Meta de Cancelamento<br>{status_meta.replace('✅ ', '').replace('⚠️ ', '')}</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Gráfico de resumo
        st.subheader("📊 Resumo por Expedição")
        resumo_expedicao = df_filtrado.groupby('EXPEDIÇÃO')['CTRC_EMITIDO'].sum().reset_index()
        
        fig_resumo = px.bar(
            resumo_expedicao, 
            x='EXPEDIÇÃO', 
            y='CTRC_EMITIDO',
            title="Emissões por Expedição",
            color='EXPEDIÇÃO',
            text='CTRC_EMITIDO'
        )
        fig_resumo.update_traces(texttemplate='%{text:,}', textposition='outside')
        fig_resumo.update_layout(showlegend=False)
        st.plotly_chart(fig_resumo, use_container_width=True)
    
    with tab2:
        st.header("📈 Análise Temporal")
        
        # Análise por mês
        st.subheader("📅 Emissões por Mês")
        emissoes_mes = df_filtrado.groupby('MÊS')['CTRC_EMITIDO'].sum().reset_index()
        
        # Ordenar meses cronologicamente
        meses_ordem = ['JANEIRO', 'FEVEREIRO', 'MARÇO', 'ABRIL', 'MAIO', 'JUNHO', 
                       'JULHO', 'AGOSTO', 'SETEMBRO', 'OUTUBRO', 'NOVEMBRO', 'DEZEMBRO']
        emissoes_mes['ordem'] = emissoes_mes['MÊS'].map({mes: i for i, mes in enumerate(meses_ordem)})
        emissoes_mes = emissoes_mes.sort_values('ordem')
        
        fig_mes = px.line(
            emissoes_mes, 
            x='MÊS', 
            y='CTRC_EMITIDO',
            title="Evolução das Emissões por Mês",
            markers=True,
            text='CTRC_EMITIDO'
        )
        fig_mes.update_traces(texttemplate='%{text:,}', textposition='top center')
        fig_mes.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig_mes, use_container_width=True)
        
        # Análise por dia da semana
        st.subheader("📊 Emissões por Dia da Semana")
        df_filtrado['dia_semana'] = df_filtrado['DATA_EMISSÃO'].dt.day_name()
        dias_pt = {
            'Monday': 'Segunda-feira',
            'Tuesday': 'Terça-feira', 
            'Wednesday': 'Quarta-feira',
            'Thursday': 'Quinta-feira',
            'Friday': 'Sexta-feira',
            'Saturday': 'Sábado',
            'Sunday': 'Domingo'
        }
        df_filtrado['dia_semana_pt'] = df_filtrado['dia_semana'].map(dias_pt)
        
        emissoes_dia = df_filtrado.groupby('dia_semana_pt')['CTRC_EMITIDO'].sum().reset_index()
        
        fig_dia = px.bar(
            emissoes_dia,
            x='dia_semana_pt',
            y='CTRC_EMITIDO',
            title="Emissões por Dia da Semana",
            color='CTRC_EMITIDO',
            color_continuous_scale='Blues'
        )
        fig_dia.update_layout(xaxis_tickangle=-45, showlegend=False)
        st.plotly_chart(fig_dia, use_container_width=True)
        
        # Análise de tendência
        st.subheader("📈 Tendência Diária")
        emissoes_diaria = df_filtrado.groupby('DATA_EMISSÃO')['CTRC_EMITIDO'].sum().reset_index()
        
        fig_tendencia = px.line(
            emissoes_diaria,
            x='DATA_EMISSÃO',
            y='CTRC_EMITIDO',
            title="Tendência Diária de Emissões"
        )
        st.plotly_chart(fig_tendencia, use_container_width=True)
    
    with tab3:
        st.header("⚡ Produtividade")
        
        # Top usuários por emissões
        st.subheader("🏆 Top 10 Usuários - Emissões")
        top_usuarios = df_filtrado.groupby('USUARIO')['CTRC_EMITIDO'].sum().sort_values(ascending=False).head(10).reset_index()
        
        fig_top_usuarios = px.bar(
            top_usuarios,
            x='CTRC_EMITIDO',
            y='USUARIO',
            orientation='h',
            title="Top 10 Usuários por Emissões",
            color='CTRC_EMITIDO',
            color_continuous_scale='Viridis',
            text='CTRC_EMITIDO'
        )
        fig_top_usuarios.update_traces(texttemplate='%{text:,}', textposition='outside')
        fig_top_usuarios.update_layout(height=500, showlegend=False)
        st.plotly_chart(fig_top_usuarios, use_container_width=True)
        
        # Produtividade por expedição
        st.subheader("🚛 Produtividade por Expedição")
        col1, col2 = st.columns(2)
        
        with col1:
            prod_expedicao = df_filtrado.groupby('EXPEDIÇÃO')['CTRC_EMITIDO'].agg(['sum', 'mean', 'count']).reset_index()
            prod_expedicao.columns = ['EXPEDIÇÃO', 'Total', 'Média', 'Dias']
            
            # Formatação manual dos números
            prod_expedicao['Total_fmt'] = prod_expedicao['Total'].apply(lambda x: f"{x:,.0f}".replace(',', '.'))
            prod_expedicao['Média_fmt'] = prod_expedicao['Média'].apply(lambda x: f"{x:.1f}")
            prod_expedicao['Dias_fmt'] = prod_expedicao['Dias'].apply(lambda x: f"{x:,.0f}".replace(',', '.'))
            
            # Exibir tabela com formatação
            display_df = prod_expedicao[['EXPEDIÇÃO', 'Total_fmt', 'Média_fmt', 'Dias_fmt']].copy()
            display_df.columns = ['EXPEDIÇÃO', 'Total', 'Média', 'Dias']
            
            st.dataframe(display_df, use_container_width=True)
        
        with col2:
            fig_prod_exp = px.pie(
                prod_expedicao,
                values='Total',
                names='EXPEDIÇÃO',
                title="Distribuição de Emissões por Expedição"
            )
            st.plotly_chart(fig_prod_exp, use_container_width=True)
        
        # Análise de produtividade mensal por usuário
        st.subheader("📊 Produtividade Mensal por Usuário")
        prod_mensal = df_filtrado.groupby(['MÊS', 'USUARIO'])['CTRC_EMITIDO'].sum().reset_index()
        
        # Selecionar usuários para análise
        usuarios_selecionados = st.multiselect(
            "Selecione usuários para análise:",
            options=sorted(df_filtrado['USUARIO'].unique()),
            default=sorted(df_filtrado['USUARIO'].unique())[:5]
        )
        
        if usuarios_selecionados:
            prod_mensal_filtrado = prod_mensal[prod_mensal['USUARIO'].isin(usuarios_selecionados)]
            
            fig_prod_mensal = px.line(
                prod_mensal_filtrado,
                x='MÊS',
                y='CTRC_EMITIDO',
                color='USUARIO',
                title="Evolução da Produtividade Mensal por Usuário",
                markers=True
            )
            fig_prod_mensal.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig_prod_mensal, use_container_width=True)
    
    with tab4:
        st.header("❌ Cancelamentos")
        
        # KPIs de cancelamentos
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                label="📊 Total de Cancelamentos",
                value=format_number(len(cancelamentos_filtrado))
            )
        
        with col2:
            cancelamentos_mes = len(cancelamentos_filtrado)
            emissoes_mes_total = df_filtrado['CTRC_EMITIDO'].sum()
            taxa_atual = (cancelamentos_mes / emissoes_mes_total * 100) if emissoes_mes_total > 0 else 0
            st.metric(
                label="📈 Taxa de Cancelamento",
                value=f"{taxa_atual:.2f}%"
            )
        
        with col3:
            meta_status = "✅ Dentro da Meta" if taxa_atual <= 0.75 else "⚠️ Fora da Meta"
            st.metric(
                label="🎯 Status da Meta",
                value=meta_status
            )
        
        # Análise de cancelamentos por mês
        st.subheader("📅 Cancelamentos por Mês")
        cancelamentos_mes = cancelamentos_filtrado.groupby('MÊS').size().reset_index(name='Cancelamentos')
        
        # Ordenar meses cronologicamente
        meses_ordem = ['JANEIRO', 'FEVEREIRO', 'MARÇO', 'ABRIL', 'MAIO', 'JUNHO', 
                       'JULHO', 'AGOSTO', 'SETEMBRO', 'OUTUBRO', 'NOVEMBRO', 'DEZEMBRO']
        cancelamentos_mes['ordem'] = cancelamentos_mes['MÊS'].map({mes: i for i, mes in enumerate(meses_ordem)})
        cancelamentos_mes = cancelamentos_mes.sort_values('ordem')
        
        fig_canc_mes = px.bar(
            cancelamentos_mes,
            x='MÊS',
            y='Cancelamentos',
            title="Cancelamentos por Mês",
            color='Cancelamentos',
            color_continuous_scale='Reds',
            text='Cancelamentos'
        )
        fig_canc_mes.update_traces(texttemplate='%{text}', textposition='outside')
        fig_canc_mes.update_layout(xaxis_tickangle=-45, showlegend=False)
        st.plotly_chart(fig_canc_mes, use_container_width=True)
        
        # Top motivos de cancelamento
        st.subheader("🔍 Top 10 Motivos de Cancelamento")
        top_motivos = cancelamentos_filtrado['MOTIVO'].value_counts().head(10).reset_index()
        top_motivos.columns = ['Motivo', 'Quantidade']
        
        fig_motivos = px.bar(
            top_motivos,
            x='Quantidade',
            y='Motivo',
            orientation='h',
            title="Top 10 Motivos de Cancelamento",
            color='Quantidade',
            color_continuous_scale='Oranges',
            text='Quantidade'
        )
        fig_motivos.update_traces(texttemplate='%{text}', textposition='outside')
        fig_motivos.update_layout(height=500, showlegend=False)
        st.plotly_chart(fig_motivos, use_container_width=True)
        
        # Cancelamentos por usuário
        st.subheader("👥 Cancelamentos por Usuário")
        canc_usuario = cancelamentos_filtrado.groupby('USUARIO').size().sort_values(ascending=False).head(10).reset_index()
        canc_usuario.columns = ['Usuário', 'Cancelamentos']
        
        fig_canc_usuario = px.bar(
            canc_usuario,
            x='Cancelamentos',
            y='Usuário',
            orientation='h',
            title="Top 10 Usuários com Mais Cancelamentos",
            color='Cancelamentos',
            color_continuous_scale='Reds',
            text='Cancelamentos'
        )
        fig_canc_usuario.update_traces(texttemplate='%{text}', textposition='outside')
        fig_canc_usuario.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig_canc_usuario, use_container_width=True)
        
        # Cancelamentos por expedição
        st.subheader("🚛 Cancelamentos por Expedição")
        canc_expedicao = cancelamentos_filtrado.groupby('EXPEDIÇÃO').size().reset_index(name='Cancelamentos')
        
        fig_canc_exp = px.pie(
            canc_expedicao,
            values='Cancelamentos',
            names='EXPEDIÇÃO',
            title="Distribuição de Cancelamentos por Expedição"
        )
        st.plotly_chart(fig_canc_exp, use_container_width=True)
    
    with tab5:
        st.header("📋 Dados Detalhados")
        
        # Seletor de tipo de dados
        tipo_dados = st.selectbox(
            "Selecione o tipo de dados para visualizar:",
            ["Emissões", "Cancelamentos"]
        )
        
        if tipo_dados == "Emissões":
            st.subheader("📊 Dados de Emissões")
            
            # Estatísticas resumidas
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("📈 Total de Registros", format_number(len(df_filtrado)))
            
            with col2:
                st.metric("📊 Total de Emissões", format_number(df_filtrado['CTRC_EMITIDO'].sum()))
            
            with col3:
                st.metric("📅 Período", f"{df_filtrado['DATA_EMISSÃO'].min().strftime('%d/%m/%Y')} - {df_filtrado['DATA_EMISSÃO'].max().strftime('%d/%m/%Y')}")
            
            with col4:
                st.metric("👥 Usuários Únicos", format_number(df_filtrado['USUARIO'].nunique()))
            
            # Tabela de dados
            st.subheader("📋 Tabela de Emissões")
            
            # Opções de visualização
            col1, col2 = st.columns(2)
            
            with col1:
                mostrar_linhas = st.selectbox(
                    "Número de linhas para exibir:",
                    [50, 100, 200, 500, "Todos"],
                    index=0
                )
            
            with col2:
                ordenar_por = st.selectbox(
                    "Ordenar por:",
                    ["DATA_EMISSÃO", "CTRC_EMITIDO", "USUARIO", "MÊS"],
                    index=0
                )
            
            # Preparar dados para exibição
            df_exibir = df_filtrado.copy()
            df_exibir = df_exibir.sort_values(ordenar_por, ascending=False)
            
            if mostrar_linhas != "Todos":
                df_exibir = df_exibir.head(int(mostrar_linhas))
            
            # Formatação da tabela
            df_exibir['DATA_EMISSÃO'] = df_exibir['DATA_EMISSÃO'].dt.strftime('%d/%m/%Y')
            df_exibir['CTRC_EMITIDO'] = df_exibir['CTRC_EMITIDO'].apply(format_number)
            
            st.dataframe(
                df_exibir[['DATA_EMISSÃO', 'MÊS', 'CTRC_EMITIDO', 'USUARIO', 'EXPEDIÇÃO']],
                use_container_width=True,
                height=400
            )
            
            # Botão para download
            csv_emissoes = df_filtrado.to_csv(index=False)
            st.download_button(
                label="📥 Baixar dados de emissões (CSV)",
                data=csv_emissoes,
                file_name=f"emissoes_km_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime='text/csv'
            )
        
        else:  # Cancelamentos
            st.subheader("❌ Dados de Cancelamentos")
            
            # Estatísticas resumidas
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("📈 Total de Registros", format_number(len(cancelamentos_filtrado)))
            
            with col2:
                st.metric("👥 Usuários Únicos", format_number(cancelamentos_filtrado['USUARIO'].nunique()))
            
            with col3:
                st.metric("🔍 Motivos Únicos", format_number(cancelamentos_filtrado['MOTIVO'].nunique()))
            
            with col4:
                st.metric("🚛 Expedições", format_number(cancelamentos_filtrado['EXPEDIÇÃO'].nunique()))
            
            # Tabela de dados
            st.subheader("📋 Tabela de Cancelamentos")
            
            # Opções de visualização
            col1, col2 = st.columns(2)
            
            with col1:
                mostrar_linhas_canc = st.selectbox(
                    "Número de linhas para exibir:",
                    [50, 100, 200, 500, "Todos"],
                    index=0,
                    key="linhas_canc"
                )
            
            with col2:
                ordenar_por_canc = st.selectbox(
                    "Ordenar por:",
                    ["DATA_CANCELADO", "USUARIO", "MÊS", "EXPEDIÇÃO"],
                    index=0,
                    key="ordenar_canc"
                )
            
            # Preparar dados para exibição
            df_canc_exibir = cancelamentos_filtrado.copy()
            df_canc_exibir = df_canc_exibir.sort_values(ordenar_por_canc, ascending=False)
            
            if mostrar_linhas_canc != "Todos":
                df_canc_exibir = df_canc_exibir.head(int(mostrar_linhas_canc))
            
            st.dataframe(
                df_canc_exibir[['CTRC CANCELADOS', 'DATA_CANCELADO', 'MÊS', 'USUARIO', 'EXPEDIÇÃO', 'MOTIVO']],
                use_container_width=True,
                height=400
            )
            
            # Botão para download
            csv_cancelamentos = cancelamentos_filtrado.to_csv(index=False)
            st.download_button(
                label="📥 Baixar dados de cancelamentos (CSV)",
                data=csv_cancelamentos,
                file_name=f"cancelamentos_km_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime='text/csv'
            )

if __name__ == "__main__":
    main()

