import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date, timedelta
import numpy as np
from plotly.subplots import make_subplots
import calendar

import locale
import platform

# Ajuste de locale para português (funciona em Windows, Linux e Mac)
so = platform.system()
try:
    if so == "Windows":
        locale.setlocale(locale.LC_TIME, "Portuguese_Brazil.1252")
    else:
        locale.setlocale(locale.LC_TIME, "pt_BR.UTF-8")
except Exception as e:
    print(f"⚠️ Não foi possível definir locale PT-BR: {e}")

# Configuração da página
st.set_page_config(
    page_title="Dashboard KM - Controle de Emissões e Cancelamentos",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS COMBINADO: CABEÇALHO ORIGINAL + ABAS MODERNAS + MELHORIAS + COR ÚNICA PARA TODAS AS ABAS
st.markdown("""
<style>
    /* Importar fontes */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Poppins:wght@400;500;600;700&display=swap' );

    /* Configurações globais */
    body {
        font-family: 'Roboto', sans-serif;
    }

    /* --- CABEÇALHO COM ROBOTO --- */
    .main-header {
        font-family: 'Roboto', sans-serif;
        font-size: 2.0rem;
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

    /* --- ABAS DE NAVEGAÇÃO COM ROBOTO --- */
    .stTabs [data-baseweb="tab-list"] {
        gap: 14px;
        background-color: #0f172a;
        padding: 12px;
        border-radius: 18px;
        display: flex;
        justify-content: center;
        border: 1px solid #334155;
        margin-bottom: 2rem;
    }

    .stTabs [data-baseweb="tab"] {
        min-height: 70px !important;
        height: 70px !important;
        padding: 0 50px !important;
        font-size: 1.4rem !important;
        line-height: 1.6 !important;
        font-family: 'Roboto', sans-serif !important; /* <<< FONTE ALTERADA AQUI */
        background-color: #1e293b;
        border-radius: 16px;
        color: #9CA3AF;
        font-weight: 700;
        transition: all 0.3s ease;
        border: none;
        display: flex;
        align-items: center;
        justify-content: center;
        flex-grow: 1;
        box-shadow: inset 0 0 0 1px #334155;
    }


    .stTabs [data-baseweb="tab"]:hover:not([aria-selected="true"]) {
        background-color: #334155;
        color: #F9FAFB;
        transform: translateY(-2px);
    }

    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #3B82F6, #1D4ED8) !important;
        box-shadow: 0 6px 18px rgba(59, 130, 246, 0.35) !important;
        color: white !important;
        font-weight: 800;
        font-size: 1.4rem !important;
        transform: scale(1.07);
    }

    /* --- CARTÕES KPI --- */
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
        display: flex;
        flex-direction: column;
        justify-content: center;
        height: 180px; /* Altura fixa para todos os cartões */
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
        font-size: 2.0rem;
        font-weight: 700;
        margin: 0; /* Remove margens verticais */
        padding-bottom: 0.5rem; /* Adiciona um pequeno espaço abaixo do número */
        position: relative;
        z-index: 1;
    }

    .kpi-label {
        font-size: 0.9rem;
        opacity: 0.9;
        position: relative;
        z-index: 1;
        line-height: 1.3; /* Melhora o espaçamento entre as linhas do texto */
    }
    
    /* NOVA CLASSE PARA O TÍTULO PRINCIPAL DO KPI (VERSÃO MELHORADA) */
    .kpi-main-label {
        display: block;
        position: relative; /* Habilita o deslocamento sem afetar outros elementos */
        top: -0.8rem;       /* << Puxa o texto para cima. Ajuste este valor. */
        margin-bottom: -0.5rem; /* << Compensa o espaço vazio deixado acima. Ajuste se necessário. */
    
        /* --- ADICIONE ESTAS LINHAS --- */
        font-size: 1.0rem !important;   /* Define o tamanho da fonte */
        font-weight: 700 !important;      /* Deixa o texto em negrito */
        line-height: 1.2;               /* Melhora o espaçamento entre linhas */
    } /* << A CLASSE AGORA TERMINA AQUI, COM TUDO DENTRO */

    .kpi-blue { --card-color-1: #3b82f6; --card-color-2: #1d4ed8; }
    .kpi-red { --card-color-1: #ef4444; --card-color-2: #dc2626; }
    .kpi-purple { --card-color-1: #8b5cf6; --card-color-2: #7c3aed; }
    .kpi-orange { --card-color-1: #f97316; --card-color-2: #ea580c; }
    .kpi-green { --card-color-1: #10b981; --card-color-2: #059669; }
    .kpi-teal { --card-color-1: #14b8a6; --card-color-2: #0d9488; }
    .kpi-indigo { --card-color-1: #6366f1; --card-color-2: #4f46e5; }
            
    }
            
    /* NOVA CLASSE PARA O TÍTULO PRINCIPAL DO KPI (VERSÃO MELHORADA) */
    .kpi-main-label {
        display: block;
        position: relative; 
        top: -0.8rem;       
        margin-bottom: -0.5rem; 
        font-size: 1.2rem !important;   
        font-weight: 700 !important;      
        line-height: 1.2;               
    }

    /* --- ADICIONE ESTA NOVA CLASSE AQUI --- */
    .kpi-title-only {
        font-size: 1.0rem !important;   /* Tamanho da fonte aumentado */
        font-weight: 700 !important;      /* Texto em negrito */
        line-height: 1.2;
    }

    .kpi-blue { --card-color-1: #3b82f6; --card-color-2: #1d4ed8; }
    .kpi-red { --card-color-1: #ef4444; --card-color-2: #dc2626; }
            
            

    /* Ajusta os cards internos dos Insights */
    .stContainer, .stCard {
        background: linear-gradient(135deg, #1e293b, #0f172a) !important; /* azul escuro → preto */
        border: 1px solid #334155 !important;
        border-radius: 16px !important;
    }

    .insights-title {
        font-size: 1.2rem;
        font-weight: 600;
        color: #f1f5f9;  /* <<< texto claro para título da seção */
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }

    .insight-item {
        background: #1e293b;   /* fundo escuro no lugar do branco */
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 0.5rem;
        border-left: 4px solid #3b82f6;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2); /* sombra mais visível no dark */
        color: #f1f5f9; /* texto claro */
    }
            /* Adicione esta nova classe ao seu CSS */
.kpi-main-label {
    display: block; /* Garante que o título ocupe sua própria linha */
    margin-bottom: 0.5rem; /* Espaço entre o título e o subtítulo */
}
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    """Carrega e processa os dados dos arquivos Excel"""
    try:
        # Carregando dados de emissões
        emissoes_df = pd.read_excel("EMISSOES_KM.xlsx")
        emissoes_df['DATA_EMISSÃO'] = pd.to_datetime(emissoes_df['DATA_EMISSÃO'])

        # 🔹 Garantir meses em português
        meses_pt = [
            "JANEIRO","FEVEREIRO","MARÇO","ABRIL","MAIO","JUNHO",
            "JULHO","AGOSTO","SETEMBRO","OUTUBRO","NOVEMBRO","DEZEMBRO"
        ]
        emissoes_df['MÊS'] = emissoes_df['DATA_EMISSÃO'].dt.month.apply(lambda x: meses_pt[x-1])

        # Carregando dados de cancelamentos
        cancelamentos_df = pd.read_excel("CANCELAMENTOS_KM.xlsx")
        cancelamentos_df["DATA_CANCELADO"] = pd.to_datetime(cancelamentos_df["DATA_CANCELADO"])
        meses_pt = [
            "JANEIRO","FEVEREIRO","MARÇO","ABRIL","MAIO","JUNHO",
            "JULHO","AGOSTO","SETEMBRO","OUTUBRO","NOVEMBRO","DEZEMBRO"
        ]
        cancelamentos_df["MÊS"] = cancelamentos_df["DATA_CANCELADO"].dt.month.apply(lambda x: meses_pt[x-1])

        return emissoes_df, cancelamentos_df
    except Exception as e:
        st.error(f"Erro ao carregar os dados: {e}")
        return None, None

def format_number(num):
    """Formata números no padrão brasileiro"""
    if pd.isna(num) or num is None:
        return "0"
    try:
        return f"{int(num):,}".replace(",", ".")
    except (ValueError, TypeError):
        return "0"

def create_gauge_chart(value, max_value, title, color_ranges=None):
    """Cria um gráfico de velocímetro (gauge)"""
    if color_ranges is None:
        color_ranges = [
            {"range": [0, 0.5], "color": "#10b981"},  # Verde
            {"range": [0.5, 0.75], "color": "#f59e0b"},  # Amarelo
            {"range": [0.75, max_value], "color": "#ef4444"}  # Vermelho
        ]
    
    fig = go.Figure(go.Indicator(
        mode = "gauge+number+delta",
        value = value * 100,
        number = {"valueformat": ".2f", "suffix": "%"},  # <<< arredonda e coloca %
        domain = {"x": [0, 1], "y": [0, 1]},
        title = {"text": title, "font": {"size": 16}, "align": "center"},
        delta = {"reference": 0.75, "increasing": {"color": "red"}, "decreasing": {"color": "green"}, "valueformat": ".2f"},
        gauge = {
            "axis": {"range": [None, max_value * 100], "tickformat": ".2f"},
            "bar": {"color": "#dc2626"},
            "steps": [
                {"range": [0, 0.5 * 100], "color": "#BDD9E7"},
                {"range": [0.5 * 100, 0.75 * 100], "color": "#4b5563"},
                {"range": [0.75 * 100, max_value * 100], "color": "#6b7280"}
            ],
            "threshold": {
                "line": {"color": "red", "width": 4},
                "thickness": 0.75,
                "value": 0.75 * 100
            }
        }
    ))
    
    fig.update_layout(
    height=300,
    margin=dict(l=20, r=20, t=70, b=20),  # <<< aumentei o 't'
    font={"color": "white", "family": "Arial"}
)
    
    return fig

def create_sparkline(data, title=""):
    """Cria um mini-gráfico de linha (sparkline)"""
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=list(range(len(data))),
        y=data,
        mode='lines+markers',
        line=dict(color='#3b82f6', width=2),
        marker=dict(size=4),
        showlegend=False
    ))
    
    fig.update_layout(
        height=100,
        margin=dict(l=0, r=0, t=20, b=0),
        xaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
        yaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        title=dict(text=title, font=dict(size=12), x=0.5)
    )
    
    return fig

def create_trend_analysis(df):
    """Cria análise de tendência com regressão linear"""
    df_daily = df.groupby('DATA_EMISSÃO')['CTRC_EMITIDO'].sum().reset_index()
    df_daily['days_from_start'] = (df_daily['DATA_EMISSÃO'] - df_daily['DATA_EMISSÃO'].min()).dt.days
    
    # Regressão linear simples
    from sklearn.linear_model import LinearRegression
    import numpy as np
    
    X = df_daily['days_from_start'].values.reshape(-1, 1)
    y = df_daily['CTRC_EMITIDO'].values
    
    model = LinearRegression()
    model.fit(X, y)
    
    # Predições
    y_pred = model.predict(X)
    
    # Criar gráfico
    fig = go.Figure()
    
    # Dados reais
    fig.add_trace(go.Scatter(
        x=df_daily['DATA_EMISSÃO'],
        y=df_daily['CTRC_EMITIDO'],
        mode='markers',
        name='Dados Reais',
        marker=dict(color='blue', size=6)
    ))
    
    # Linha de tendência
    fig.add_trace(go.Scatter(
        x=df_daily['DATA_EMISSÃO'],
        y=y_pred,
        mode='lines',
        name='Tendência',
        line=dict(color='red', width=2, dash='dash')
    ))
    
    fig.update_layout(
        title='Análise de Tendência - Emissões Diárias',
        xaxis_title='Data',
        yaxis_title='CTRCs Emitidos',
        height=400
    )
    
    # Calcular coeficiente de correlação
    correlation = np.corrcoef(df_daily['days_from_start'], df_daily['CTRC_EMITIDO'])[0, 1]
    
    return fig, correlation, model.coef_[0]

def create_moving_averages(df, windows=[7, 30]):
    """Cria gráfico com médias móveis"""
    df_daily = df.groupby('DATA_EMISSÃO')['CTRC_EMITIDO'].sum().reset_index()
    
    fig = go.Figure()
    
    # Dados originais
    fig.add_trace(go.Scatter(
        x=df_daily['DATA_EMISSÃO'],
        y=df_daily['CTRC_EMITIDO'],
        mode='lines+markers',
        name='Dados Diários',
        line=dict(color='lightblue', width=1),
        marker=dict(size=3)
    ))
    
    colors = ['red', 'green', 'purple', 'orange']
    
    # Médias móveis
    for i, window in enumerate(windows):
        ma = df_daily['CTRC_EMITIDO'].rolling(window=window, center=True).mean()
        fig.add_trace(go.Scatter(
            x=df_daily['DATA_EMISSÃO'],
            y=ma,
            mode='lines',
            name=f'Média Móvel {window} dias',
            line=dict(color=colors[i % len(colors)], width=2)
        ))
    
    fig.update_layout(
        title='Emissões Diárias com Médias Móveis',
        xaxis_title='Data',
        yaxis_title='CTRCs Emitidos',
        height=400
    )
    
    return fig

def create_weekday_pattern(df):
    """Cria análise de padrão por dia da semana"""
    df_copy = df.copy()
    df_copy['weekday'] = df_copy['DATA_EMISSÃO'].dt.day_name()
    df_copy['weekday_num'] = df_copy['DATA_EMISSÃO'].dt.weekday
    
    # Mapear para português
    weekday_map = {
        'Monday': 'Segunda', 'Tuesday': 'Terça', 'Wednesday': 'Quarta',
        'Thursday': 'Quinta', 'Friday': 'Sexta', 'Saturday': 'Sábado', 'Sunday': 'Domingo'
    }
    df_copy['weekday_pt'] = df_copy['weekday'].map(weekday_map)
    
    # Agrupar por dia da semana
    weekday_stats = df_copy.groupby(['weekday_num', 'weekday_pt'])['CTRC_EMITIDO'].agg(['sum', 'mean', 'std']).reset_index()
    weekday_stats = weekday_stats.sort_values('weekday_num')
    
    # Criar gráfico de barras com erro
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=weekday_stats['weekday_pt'],
        y=weekday_stats['mean'],
        name='Média Diária',
        marker_color='lightblue',
        text=weekday_stats['mean'],
        textposition='outside',      # <<< posição acima das barras
        texttemplate='%{text:.0f}'    # <<< formata sem casas decimais
    ))
    
    fig.update_layout(
        title='Padrão de Emissões por Dia da Semana',
        xaxis_title='Dia da Semana',
        yaxis_title='Média de CTRCs Emitidos',
        height=400,
        margin=dict(t=80),  # Aumenta espaço no topo
        yaxis=dict(range=[0, weekday_stats['mean'].max() * 1.3])  # Dá folga para os rótulos
    )
    
    return fig, weekday_stats

def main():   
    # Cabeçalho principal
    st.markdown("""
    <div class="main-header">
        📊 Dashboard KM - Controle de Emissões e Cancelamentos
    </div>
    """, unsafe_allow_html=True)
    
    # Carregando dados
    emissoes_df, cancelamentos_df = load_data()

    # 🔹 Totais fixos de emissões (jan–ago)
    EMISSOES_FIXAS_MES = {
        "JANEIRO": 47391,
        "FEVEREIRO": 47957,
        "MARÇO": 46924,
        "ABRIL": 47150,
        "MAIO": 50778,
        "JUNHO": 47859,
        "JULHO": 55122,
        "AGOSTO": 47793,
    }

    MESES_MAP = {
        "JANEIRO": 1, "FEVEREIRO": 2, "MARÇO": 3, "ABRIL": 4,
        "MAIO": 5, "JUNHO": 6, "JULHO": 7, "AGOSTO": 8,
        "SETEMBRO": 9, "OUTUBRO": 10, "NOVEMBRO": 11, "DEZEMBRO": 12
    }

    def denom_para_taxa_cancelamento(mes_sel, usuario_sel, expedicao_sel, denom_real):
        """
        Usa os totais fixos apenas na visão geral (Todos os usuários e Todas as expedições).
        Para filtros por usuário/expedição, mantém o denominador real para não distorcer produtividade.
        """
        if usuario_sel != "Todos" or expedicao_sel != "Todas":
            return denom_real
        if mes_sel in EMISSOES_FIXAS_MES:
            return EMISSOES_FIXAS_MES[mes_sel]
        if mes_sel == "Todos":
            return sum(EMISSOES_FIXAS_MES.values())
        return denom_real
    
    if emissoes_df is None or cancelamentos_df is None:
        st.error("Não foi possível carregar os dados. Verifique os arquivos.")
        return
    
    # ✅ Agora o dicionário está sempre disponível
    meses_abrev = {
    # Português
    "jan": "Jan", "fev": "Fev", "mar": "Mar",
    "abr": "Abr", "mai": "Mai", "jun": "Jun",
    "jul": "Jul", "ago": "Ago", "set": "Set",
    "out": "Out", "nov": "Nov", "dez": "Dez",

    # Inglês
    "feb": "Fev", "apr": "Abr", "may": "Mai", "aug": "Ago",
    "sep": "Set", "oct": "Out", "dec": "Dez"
}
    
    # Sidebar com filtros
    st.sidebar.header("🔍 Filtros")
    
    # Filtro de Período por Calendário
    st.sidebar.subheader("🗓️ Seleção de Data")
    today = datetime.now().date()
    default_start_date = datetime(today.year, 1, 1).date()
    default_end_date = today

    date_range_calendar = st.sidebar.date_input(
        "Selecione o intervalo de datas:",
        value=(default_start_date, default_end_date),
        max_value=today,
        format="DD/MM/YYYY"
    )

    if len(date_range_calendar) == 2:
        start_date, end_date = date_range_calendar
    else:
        start_date, end_date = default_start_date, default_end_date

    # Filtro de Período pré-definido
    st.sidebar.subheader("📅 Período Pré-definido")
    periodo_selecionado = st.sidebar.selectbox(
        "Ou selecione um período rápido:",
        options=[
            "Nenhum",
            "Ano atual",
            "Últimos 7 dias",
            "Últimos 30 dias",
            "Últimos 90 dias",
            "Mês atual",
            "Último mês"
        ],
        index=0
    )

    if periodo_selecionado != "Nenhum":
        if periodo_selecionado == "Ano atual":
            start_date = datetime(datetime.now().year, 1, 1).date()
            end_date = datetime.now().date()
        elif periodo_selecionado == "Últimos 7 dias":
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=6)
        elif periodo_selecionado == "Últimos 30 dias":
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=29)
        elif periodo_selecionado == "Últimos 90 dias":
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=89)
        elif periodo_selecionado == "Mês atual":
            start_date = datetime(datetime.now().year, datetime.now().month, 1).date()
            end_date = datetime.now().date()
        elif periodo_selecionado == "Último mês":
            today = datetime.now()
            first_day_current_month = datetime(today.year, today.month, 1)
            end_date = first_day_current_month - timedelta(days=1)
            start_date = datetime(end_date.year, end_date.month, 1).date()

    # Certifique-se de que start_date e end_date são objetos date
    if start_date and isinstance(start_date, datetime):
        start_date = start_date.date()
    if end_date and isinstance(end_date, datetime):
        end_date = end_date.date()

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
    usuarios_emissoes = set(emissoes_df["USUÁRIO"].str.strip().unique())
    usuarios_cancelamentos = set(cancelamentos_df["USUARIO"].str.strip().unique())
    usuarios_disponiveis = sorted(list(usuarios_emissoes.union(usuarios_cancelamentos)))
    if 'Usuario Automatico' in usuarios_disponiveis:
        usuarios_disponiveis.remove('Usuario Automatico')

    # Adiciona 'Todos' ao início da lista de opções
    opcoes_usuario = ["Todos"] + usuarios_disponiveis

    # Tenta manter a seleção anterior, se o usuário ainda estiver disponível
    if "usuario_selecionado" not in st.session_state:
        st.session_state.usuario_selecionado = "Nenhum"

    # Verifica se o usuário atualmente selecionado ainda está nas opções disponíveis
    if st.session_state.usuario_selecionado not in opcoes_usuario:
        st.session_state.usuario_selecionado = "Nenhum"

    # Encontra o índice do usuário selecionado para definir o valor inicial do selectbox
    try:
        default_index = opcoes_usuario.index(st.session_state.usuario_selecionado)
    except ValueError:
        default_index = 0 # Se não encontrar, volta para 'Todos'

    usuario_selecionado = st.sidebar.selectbox(
        "Selecione o usuário:",
        options=opcoes_usuario,
        index=default_index,
        key="filtro_usuario_principal" # Chave única para o selectbox
    )


    
    # Aplicando filtros
    df_filtrado = emissoes_df.copy()
    cancelamentos_filtrado = cancelamentos_df.copy()
    
    # Filtro de data
    if start_date and end_date:
        df_filtrado = df_filtrado[
            (df_filtrado["DATA_EMISSÃO"].dt.date >= start_date) &
            (df_filtrado["DATA_EMISSÃO"].dt.date <= end_date)
        ]
        cancelamentos_filtrado = cancelamentos_filtrado[
            (cancelamentos_filtrado["DATA_CANCELADO"].dt.date >= start_date) &
            (cancelamentos_filtrado["DATA_CANCELADO"].dt.date <= end_date)
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
        df_filtrado = df_filtrado[df_filtrado['USUÁRIO'].str.strip() == usuario_selecionado.strip()]
        # Para cancelamentos, usar USUARIO com trim
        cancelamentos_filtrado = cancelamentos_filtrado[cancelamentos_filtrado['USUARIO'].str.strip() == usuario_selecionado.strip()]
    
    # Abas principais
    tab1, tab2, tab_individual, tab3, tab4, tab5 = st.tabs([
        "📊 Visão Geral", 
        "📈 Análise Temporal", 
        "📌 Análise Individual",
        "⚡ Produtividade", 
        "❌ Cancelamentos", 
        "📋 Dados Detalhados"
    ])
    
    with tab1:
        st.header("📊 Visão Geral")
        
        # Criar cópias dos dataframes filtrados globalmente para uso específico da aba
        df_tab1 = df_filtrado.copy()
        cancelamentos_tab1 = cancelamentos_filtrado.copy()
        
        # Calculando KPIs principais
        total_emissoes = df_tab1["CTRC_EMITIDO"].sum()
        total_cancelamentos = len(cancelamentos_tab1)
        denom_taxa = denom_para_taxa_cancelamento(
            mes_selecionado,
            usuario_selecionado,
            expedicao_selecionada,
            total_emissoes
        )
        taxa_cancelamento = (total_cancelamentos / denom_taxa * 100) if denom_taxa > 0 else 0
        meta_taxa = 0.75
        
        # Calculando novos KPIs de média
        # Criar uma cópia do df_tab1 para os cálculos de produtividade
        df_produtividade = df_tab1.copy()
        
        # Aplicar apenas filtros de data e usuário para produtividade
        if start_date and end_date:
            df_produtividade = df_produtividade[
                (df_produtividade["DATA_EMISSÃO"].dt.date >= start_date) &
                (df_produtividade["DATA_EMISSÃO"].dt.date <= end_date)
            ]
        
        if mes_selecionado != 'Todos':
            df_produtividade = df_produtividade[df_produtividade['MÊS'] == mes_selecionado]
        
        if usuario_selecionado != 'Todos':
            df_produtividade = df_produtividade[df_produtividade['USUÁRIO'].str.strip() == usuario_selecionado.strip()]
        
        # Calcular médias
        if not df_produtividade.empty:
            # Agrupar por data para médias
            emissoes_diarias = df_produtividade.groupby('DATA_EMISSÃO')['CTRC_EMITIDO'].sum()
            
            # Média diária
            media_diaria_produtividade = emissoes_diarias.mean()
            
            # Média semanal (agrupar por semana)
            df_produtividade['semana'] = df_produtividade['DATA_EMISSÃO'].dt.isocalendar().week
            df_produtividade['ano'] = df_produtividade['DATA_EMISSÃO'].dt.year
            emissoes_semanais = df_produtividade.groupby(['ano', 'semana'])['CTRC_EMITIDO'].sum()
            media_semanal_produtividade = emissoes_semanais.mean()
            
            # Média mensal
            if mes_selecionado != 'Todos':
                media_mensal_produtividade = df_produtividade[df_produtividade["MÊS"] == mes_selecionado]["CTRC_EMITIDO"].sum()
            else:
                # Se 'Todos' os meses forem selecionados, calcula a média das emissões mensais
                emissoes_mensais = df_produtividade.groupby(df_produtividade['DATA_EMISSÃO'].dt.to_period('M'))['CTRC_EMITIDO'].sum()
                media_mensal_produtividade = emissoes_mensais.mean()
        else:
            media_diaria_produtividade = media_semanal_produtividade = media_mensal_produtividade = 0
        
        # Indicador de meta
        if taxa_cancelamento <= meta_taxa:
            status_meta = "✅ Dentro da Meta"
            cor_meta = "success"
        else:
            status_meta = "⚠️ Fora da Meta"
            cor_meta = "warning"
        
        # KPIs principais em cartões coloridos
        st.subheader("📈 Indicadores Principais")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="kpi-card kpi-blue">
                <div class="kpi-icon">📈</div>
                <div class="kpi-value">{format_number(total_emissoes)}</div>
                <div class="kpi-label">
                    <span class="kpi-main-label">Total de Emissões</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="kpi-card kpi-red">
                <div class="kpi-icon">✖️</div>
                <div class="kpi-value">{format_number(total_cancelamentos)}</div>
                <div class="kpi-label">
                    <span class="kpi-main-label">Total de Cancelamentos</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="kpi-card kpi-purple">
                <div class="kpi-icon">📊</div>
                <div class="kpi-value">{taxa_cancelamento:.2f}%</div>
                <div class="kpi-label">
                    <span class="kpi-main-label">Taxa de Cancelamento</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            cor_classe = "kpi-orange" if taxa_cancelamento > meta_taxa else "kpi-green"
            icone_meta = "⚠️" if taxa_cancelamento > meta_taxa else "✅"
            st.markdown(f"""
            <div class="kpi-card {cor_classe}">
                <div class="kpi-icon">{icone_meta}</div>
                <div class="kpi-value">0.75%</div>
                <div class="kpi-label">
                    <span class="kpi-main-label">Meta de Cancelamento</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")
        
        # Novos KPIs de Média
        st.subheader("📊 Indicadores de Produtividade")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"""
            <div class="kpi-card kpi-teal">
                <div class="kpi-icon">📅</div>
                <div class="kpi-value">{format_number(media_diaria_produtividade)}</div>
                <div class="kpi-label kpi-title-only">Média Diária Total</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="kpi-card kpi-indigo">
                <div class="kpi-icon">🗓️</div>
                <div class="kpi-value">{format_number(media_semanal_produtividade)}</div>
                <div class="kpi-label kpi-title-only">Média Semanal Total</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="kpi-card kpi-green">
                <div class="kpi-icon">🗓️</div>
                <div class="kpi-value">{format_number(media_mensal_produtividade)}</div>  
                <div class="kpi-label kpi-title-only">Média Mensal Total</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")
        
        # Espaçamento após KPIs de Produtividade
        st.markdown("<br>", unsafe_allow_html=True)

        # ===============================
        # 📉 Comparação com Meses Anteriores
        # ===============================

        # Definir mês atual e mês anterior com base no filtro
        meses_map = {
            "JANEIRO": 1, "FEVEREIRO": 2, "MARÇO": 3, "ABRIL": 4, "MAIO": 5,
            "JUNHO": 6, "JULHO": 7, "AGOSTO": 8, "SETEMBRO": 9,
            "OUTUBRO": 10, "NOVEMBRO": 11, "DEZEMBRO": 12
        }
        meses_map_inv = {v: k for k, v in meses_map.items()}  # inverso para converter número → nome

        if mes_selecionado == "Todos":
            # Último mês disponível nos dados filtrados
            ultimo_mes_ordem = df_filtrado["DATA_EMISSÃO"].dt.month.max()
        else:
            ultimo_mes_ordem = meses_map.get(mes_selecionado, None)

        if ultimo_mes_ordem and ultimo_mes_ordem > 1:
            mes_anterior_ordem = ultimo_mes_ordem - 1

            nome_mes_atual = meses_map_inv[ultimo_mes_ordem]
            nome_mes_anterior = meses_map_inv[mes_anterior_ordem]

            st.subheader(f"📉 Comparação: {nome_mes_atual} vs {nome_mes_anterior}")

            # Filtrar dados do mês atual e anterior usando os dataframes originais
            dados_mes_atual = emissoes_df[emissoes_df["DATA_EMISSÃO"].dt.month == ultimo_mes_ordem]
            dados_mes_anterior = emissoes_df[emissoes_df["DATA_EMISSÃO"].dt.month == mes_anterior_ordem]

            canc_mes_atual = cancelamentos_df[cancelamentos_df["DATA_CANCELADO"].dt.month == ultimo_mes_ordem]
            canc_mes_anterior = cancelamentos_df[cancelamentos_df["DATA_CANCELADO"].dt.month == mes_anterior_ordem]

            # Aplicar filtros adicionais (expedição, usuário)...
            if expedicao_selecionada != 'Todas':
                dados_mes_atual = dados_mes_atual[dados_mes_atual['EXPEDIÇÃO'] == expedicao_selecionada]
                dados_mes_anterior = dados_mes_anterior[dados_mes_anterior['EXPEDIÇÃO'] == expedicao_selecionada]
                canc_mes_atual = canc_mes_atual[canc_mes_atual['EXPEDIÇÃO'] == expedicao_selecionada]
                canc_mes_anterior = canc_mes_anterior[canc_mes_anterior['EXPEDIÇÃO'] == expedicao_selecionada]

            if usuario_selecionado != 'Todos':
                dados_mes_atual = dados_mes_atual[dados_mes_atual['USUÁRIO'].str.strip() == usuario_selecionado.strip()]
                dados_mes_anterior = dados_mes_anterior[dados_mes_anterior['USUÁRIO'].str.strip() == usuario_selecionado.strip()]
                canc_mes_atual = canc_mes_atual[canc_mes_atual['USUARIO'].str.strip() == usuario_selecionado.strip()]
                canc_mes_anterior = canc_mes_anterior[canc_mes_anterior['USUARIO'].str.strip() == usuario_selecionado.strip()]

            # 📌 Aqui você calcula os totais reais primeiro
            emissoes_atual = dados_mes_atual["CTRC_EMITIDO"].sum()
            cancelamentos_atual = len(canc_mes_atual)

            emissoes_ant = dados_mes_anterior["CTRC_EMITIDO"].sum()
            cancelamentos_ant = len(canc_mes_anterior)

            # 📌 Só depois aplica os fixos no denominador da taxa
            emissoes_atual_denom = EMISSOES_FIXAS_MES.get(nome_mes_atual, emissoes_atual)
            emissoes_ant_denom   = EMISSOES_FIXAS_MES.get(nome_mes_anterior, emissoes_ant)

            # Mantém real se houver filtro por usuário/expedição
            if usuario_selecionado != "Todos" or expedicao_selecionada != "Todas":
                emissoes_atual_denom = emissoes_atual
                emissoes_ant_denom   = emissoes_ant

            taxa_atual = (cancelamentos_atual / emissoes_atual_denom * 100) if emissoes_atual_denom > 0 else 0
            taxa_ant   = (cancelamentos_ant   / emissoes_ant_denom   * 100) if emissoes_ant_denom   > 0 else 0




            # Filtrar dados do mês atual e anterior usando os dataframes originais
            dados_mes_atual = emissoes_df[emissoes_df["DATA_EMISSÃO"].dt.month == ultimo_mes_ordem]
            dados_mes_anterior = emissoes_df[emissoes_df["DATA_EMISSÃO"].dt.month == mes_anterior_ordem]

            canc_mes_atual = cancelamentos_df[cancelamentos_df["DATA_CANCELADO"].dt.month == ultimo_mes_ordem]
            canc_mes_anterior = cancelamentos_df[cancelamentos_df["DATA_CANCELADO"].dt.month == mes_anterior_ordem]

            # Aplicar filtros adicionais (expedição, usuário) aos dados do mês atual e anterior
            if expedicao_selecionada != 'Todas':
                dados_mes_atual = dados_mes_atual[dados_mes_atual['EXPEDIÇÃO'] == expedicao_selecionada]
                dados_mes_anterior = dados_mes_anterior[dados_mes_anterior['EXPEDIÇÃO'] == expedicao_selecionada]
                canc_mes_atual = canc_mes_atual[canc_mes_atual['EXPEDIÇÃO'] == expedicao_selecionada]
                canc_mes_anterior = canc_mes_anterior[canc_mes_anterior['EXPEDIÇÃO'] == expedicao_selecionada]

            if usuario_selecionado != 'Todos':
                dados_mes_atual = dados_mes_atual[dados_mes_atual['USUÁRIO'].str.strip() == usuario_selecionado.strip()]
                dados_mes_anterior = dados_mes_anterior[dados_mes_anterior['USUÁRIO'].str.strip() == usuario_selecionado.strip()]
                canc_mes_atual = canc_mes_atual[canc_mes_atual['USUARIO'].str.strip() == usuario_selecionado.strip()]
                canc_mes_anterior = canc_mes_anterior[canc_mes_anterior['USUARIO'].str.strip() == usuario_selecionado.strip()]

            # KPIs mês atual
            emissoes_atual = dados_mes_atual["CTRC_EMITIDO"].sum()
            cancelamentos_atual = len(canc_mes_atual)
            taxa_atual = (cancelamentos_atual / emissoes_atual * 100) if emissoes_atual > 0 else 0

            # KPIs mês anterior
            emissoes_ant = dados_mes_anterior["CTRC_EMITIDO"].sum()
            cancelamentos_ant = len(canc_mes_anterior)
            taxa_ant = (cancelamentos_ant / emissoes_ant * 100) if emissoes_ant > 0 else 0

            # Variações
            emissoes_var = ((emissoes_atual - emissoes_ant) / emissoes_ant * 100) if emissoes_ant > 0 else 0
            cancel_var = ((cancelamentos_atual - cancelamentos_ant) / cancelamentos_ant * 100) if cancelamentos_ant > 0 else 0

            # arredondar antes de calcular a variação
            taxa_atual = round(taxa_atual, 2)
            taxa_ant = round(taxa_ant, 2)
            taxa_var = ((taxa_atual - taxa_ant) / taxa_ant * 100) if taxa_ant > 0 else 0

            # Diferenças absolutas
            emissoes_diff = emissoes_atual - emissoes_ant
            cancelamentos_diff = cancelamentos_atual - cancelamentos_ant
            taxa_diff = taxa_atual - taxa_ant

            # Função para ícones de tendência
            def tendencia_icon_e_texto(var, referencia, positivo_bom=True):
                valor_formatado = f"{abs(var):.2f}".replace(".", ",")

                if var > 0:
                    if positivo_bom:
                        texto = "Crescimento"
                        cor = "Green"  # verde claro
                        icone = "▲"
                        blink = False
                    else:
                        texto = "Aumento"
                        cor = "red"
                        icone = "▲"
                        blink = True
                elif var < 0:
                    if positivo_bom:
                        texto = "Queda"
                        cor = "red"
                        icone = "▼"
                        blink = True
                    else:
                        texto = "Redução"
                        cor = "Green"  # verde claro
                        icone = "▼"
                        blink = False
                else:
                    texto = "Estável"
                    cor = "gray"
                    icone = "➡️"
                    blink = False

                # CSS de animação só se blink=True
                css_blink = """
                <style>
                @keyframes blink {
                    0%   { background-color: black; }
                    50%  { background-color: #333; }
                    100% { background-color: black; }
                }
                .tarja-blink {
                    animation: blink 1s infinite;
                    padding: 4px 10px;
                    border-radius: 6px;
                    display: inline-block;
                    font-weight: bold;
                }
                .tarja-static {
                    background-color: black;
                    padding: 4px 10px;
                    border-radius: 6px;
                    display: inline-block;
                    font-weight: bold;
                }
                </style>
                """

                classe = "tarja-blink" if blink else "tarja-static"

                return f"""
                {css_blink}
                <div style='text-align:center; margin-top:8px; font-size:1.1rem; font-weight:600;'>
                    {texto} de 
                    <span class="{classe}" style="color:{cor};">
                        {icone} {valor_formatado}%
                    </span>
                    em Relação a {referencia}
                </div>
                """
            
            # Layout em cartões
            col1, col2, col3 = st.columns(3)

            with col1:
                st.markdown(f"""
                <div class="kpi-card kpi-blue">
                    <div class="kpi-icon">📈</div>
                    <div class="kpi-value">{format_number(emissoes_atual)}</div>
                    <div class="kpi-label">
                        <span class="kpi-main-label"><b>Emissões<b></span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Emissões - Percentual com tarja preta
                st.markdown(
                    tendencia_icon_e_texto(emissoes_var, nome_mes_anterior, positivo_bom=True),
                    unsafe_allow_html=True
                )

                # Diferença absoluta
                st.markdown(f"""
                <div style='text-align:center; margin-top:2px; font-size:1.0rem; color:#9CA3AF;'>
                    <b>{'+' if emissoes_diff > 0 else ''}{format_number(emissoes_diff)} Emissões</b>
                </div>
                """, unsafe_allow_html=True)

            with col2:
                st.markdown(f"""
                <div class="kpi-card kpi-red">
                    <div class="kpi-icon">✖️</div>
                    <div class="kpi-value">{format_number(cancelamentos_atual)}</div>
                    <div class="kpi-label">
                        <span class="kpi-main-label"><b>Cancelamentos<b></span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # Cancelamentos - Texto percentual + absoluto
                st.markdown(
                    tendencia_icon_e_texto(cancel_var, nome_mes_anterior, positivo_bom=False),
                    unsafe_allow_html=True
                )

                st.markdown(f"""
                <div style='text-align:center; margin-top:2px; font-size:1.0rem; color:#9CA3AF;'>
                    <b>{'+' if cancelamentos_diff > 0 else ''}{format_number(cancelamentos_diff)} Cancelamentos</b>
                </div>
                """, unsafe_allow_html=True)


            with col3:
                cor_taxa = "kpi-green" if taxa_var < 0 else "kpi-orange"
                st.markdown(f"""
                <div class="kpi-card {cor_taxa}">
                    <div class="kpi-icon">📊</div>
                    <div class="kpi-value">{taxa_atual:.2f}%</div>
                    <div class="kpi-label">
                       <span class="kpi-main-label"><b>Taxa de Cancelamento<b></span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                st.markdown(
                    tendencia_icon_e_texto(taxa_var, nome_mes_anterior, positivo_bom=False),
                    unsafe_allow_html=True
                )

        else:
            st.info("Sem comparação disponível (primeiro mês do ano ou dados insuficientes).")
        
        st.markdown("---")

        # Espaçamento entre seções
        st.markdown("<br>", unsafe_allow_html=True)

        # Seção de insights específicos para usuário selecionado
        if usuario_selecionado != 'Todos':
            st.markdown(f"### 🎯 Insights para {usuario_selecionado}")
            
            col1_insights, col2_insights = st.columns(2)
            
            with col1_insights:
                st.markdown("**📈 Emissões do Usuário**")
                if len(df_filtrado) > 0:
                    emissoes_usuario = df_filtrado['CTRC_EMITIDO'].sum()
                    media_diaria_usuario = df_filtrado.groupby('DATA_EMISSÃO')['CTRC_EMITIDO'].sum().mean()
                    st.write(f"• Total de emissões: {format_number(emissoes_usuario)}")
                    st.write(f"• Média diária: {format_number(media_diaria_usuario)}")
                    
                    # Distribuição por expedição
                    if 'EXPEDIÇÃO' in df_filtrado.columns:
                        top_expedicao = df_filtrado.groupby('EXPEDIÇÃO')['CTRC_EMITIDO'].sum().idxmax()
                        st.write(f"• Expedição principal: {top_expedicao}")
                else:
                    st.info("Nenhuma emissão encontrada para o usuário selecionado no período.")

            with col2_insights:
                st.markdown("**🏆 Top 5 Motivos de Cancelamento (Usuário Selecionado)**")
                if len(cancelamentos_filtrado) > 0:
                    top_motivos_usuario = cancelamentos_filtrado["MOTIVO"].value_counts().head(5)
                    fig_motivos_usuario = px.bar(
                        x=top_motivos_usuario.values,
                        y=top_motivos_usuario.index,
                        orientation='h',
                        title="",
                        color=top_motivos_usuario.values,
                        color_continuous_scale='Oranges',
                        text=top_motivos_usuario.values
                    )
                    fig_motivos_usuario.update_traces(texttemplate='%{text}', textposition='outside')
                    fig_motivos_usuario.update_layout(
                        height=300,
                        showlegend=False,
                        margin=dict(l=20, r=20, t=20, b=20)
                    )
                    st.plotly_chart(fig_motivos_usuario, use_container_width=True)
                else:
                    st.info("Nenhum cancelamento encontrado para o usuário selecionado no período.")

                    # Seção de Velocímetro e Evolução da Taxa
        if usuario_selecionado == 'Todos':
            # --- AJUSTE AQUI ---
            col_title1, col_title2 = st.columns([1, 2])
            with col_title1:
                st.markdown(
                "<h3 style='text-align:center; font-size:24px;'>🎯 Monitoramento da Meta de Cancelamento</h3>",
                unsafe_allow_html=True
                )

            ano_atual = datetime.now().year   # ✅ garante que existe
            with col_title2:
                st.markdown(
                f"<h3 style='text-align:center; font-size:22px;'>📈 Evolução da Taxa de Cancelamento {ano_atual}</h3>",
                unsafe_allow_html=True
                )
            
            col1, col2 = st.columns([1, 2])
            
            with col1:
                # Gráfico de velocímetro para a meta
                gauge_fig = create_gauge_chart(
                    value=taxa_cancelamento/100,
                    max_value=0.02,  # 2% como máximo
                    title="Taxa de Cancelamento vs Meta"
                )

                st.markdown("<br>", unsafe_allow_html=True)


                st.plotly_chart(gauge_fig, use_container_width=True)

                # Definir nome do mês ou período
                mes_texto = mes_selecionado if mes_selecionado != "Todos" else "Ano Atual"

                # Mostrar o nome do mês acima do status
                st.markdown(f"""
                    <div style="text-align:center; margin-top:10px;">
                        <span style="color:##FFFFFF; font-size:24px; font-weight:bold;">📆 {mes_texto}</span>
                    </div>
                """, unsafe_allow_html=True)
                
                # Aviso Dinâmico abaixo do velocímetro
                if taxa_cancelamento <= meta_taxa:
                    # Status dentro da meta
                    st.markdown(
                        """
                        <div style="text-align:center; margin-top:10px;">
                            <span style="color:#10b981; font-size:20px;"><b>✅ Status: DENTRO DA META<b></span>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                    st.markdown(
                        """
                        <div style="
                            background-color:#16a34a;
                           color:white;
                           padding:12px;
                           border-radius:10px;
                           text-align:center;
                           font-size:16px;
                           font-weight:bold;
                           margin-top:10px;
                       ">
                           EXCELENTE !!<br>
                           A Taxa de Cancelamento está dentro da Meta de 0,75%.
                       </div>
                       """,
                       unsafe_allow_html=True
                    )

                else:
                    # 🚨 Status acima da meta (tarja preta piscando)
                    st.markdown(
                        """
                        <style>
                        @keyframes blink {
                            0%   { background-color: black; }
                            50%  { background-color: #333; }
                            100% { background-color: black; }
                        }
                        .tarja-blink {
                            animation: blink 1s infinite;
                            padding: 6px 14px;
                            border-radius: 8px;
                            display: inline-block;
                            font-weight: bold;
                        }
                        </style>

                        <div style="text-align:center; margin-top:10px; font-size:20px; font-weight:bold;">
                            🚨 <span class="tarja-blink" style="color:#ef4444;">Status: ACIMA DA META de 0.75%</span>
                        </div>

                        <div style="
                            background-color:#dc2626;
                            color:white;
                            padding:12px;
                            border-radius:10px;
                            text-align:center;
                            font-size:16px;
                            font-weight:bold;
                            margin-top:10px;
                        ">
                            A Taxa de Cancelamento Ultrapassou a Meta de 0,75%.<br>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
            
        with col2:
            # Gráfico de Evolução da Taxa de Cancelamento {ano_atual}
            ano_atual = datetime.now().year
            emissoes_ano_atual = df_filtrado[df_filtrado['DATA_EMISSÃO'].dt.year == ano_atual].copy()
            cancelamentos_ano_atual = cancelamentos_filtrado[cancelamentos_filtrado['DATA_CANCELADO'].dt.year == ano_atual].copy()
    
            if not emissoes_ano_atual.empty and not cancelamentos_ano_atual.empty:
                emissoes_mensais = emissoes_ano_atual.groupby(emissoes_ano_atual['DATA_EMISSÃO'].dt.to_period('M'))['CTRC_EMITIDO'].sum()
                cancelamentos_mensais = cancelamentos_ano_atual.groupby(cancelamentos_ano_atual['DATA_CANCELADO'].dt.to_period('M')).size()
        
                meses_ano = pd.period_range(start=f'{ano_atual}-01', end=f'{ano_atual}-12', freq='M')
                df_evolucao = pd.DataFrame(index=meses_ano)
                df_evolucao['Emissoes'] = emissoes_mensais.reindex(meses_ano, fill_value=0)

                # 👉 Força denominadores fixos (jan–ago) APENAS na visão geral
                if usuario_selecionado == "Todos" and expedicao_selecionada == "Todas":
                    for nome_mes, valor in EMISSOES_FIXAS_MES.items():
                        pos = MESES_MAP[nome_mes] - 1  # meses_ano vai de JAN..DEZ
                        if 0 <= pos < len(df_evolucao):
                            df_evolucao.iloc[pos, df_evolucao.columns.get_loc('Emissoes')] = valor
                
                df_evolucao['Cancelamentos'] = cancelamentos_mensais.reindex(meses_ano, fill_value=0)
                df_evolucao['Taxa_Cancelamento'] = (df_evolucao['Cancelamentos'] / df_evolucao['Emissoes'] * 100).fillna(0)
                df_evolucao['Mes'] = df_evolucao.index.strftime('%b/%y').str.title()
                df_evolucao = df_evolucao.reset_index(drop=True)

                fig_evolucao_taxa = go.Figure()
                fig_evolucao_taxa.add_trace(go.Scatter(
                    x=df_evolucao['Mes'],
                    y=df_evolucao['Taxa_Cancelamento'],
                    mode='lines+markers+text',
                    name='Taxa de Cancelamento (%)',
                    line=dict(color="#0145cd", width=3),
                    marker=dict(size=10, color="#FFFFFF", line=dict(color="#0145cd", width=2)),
                    text=[f'{val:.2f}%' for val in df_evolucao['Taxa_Cancelamento']],
                    textposition='top center',
                    textfont=dict(size=13, color="#FFFFFF", family="Verdana"),
                    hovertemplate='<b>%{x}</b><br>Taxa: %{y:.2f}%<extra></extra>'
                ))
        
                fig_evolucao_taxa.add_hline(
                    y=0.75, 
                    line_dash="dash", 
                    line_color="orange",
                    annotation_text="Meta: 0.75%",
                    annotation_position="top right",
                    annotation=dict(font_size=14, font_color="orange")  # <<< aumenta o tamanho e mantém cor
                )

                # Pega o valor máximo da taxa para definir limite superior com folga
                y_max = df_evolucao['Taxa_Cancelamento'].max() * 1.3  # 30% a mais de espaço

                fig_evolucao_taxa.update_layout(
                    xaxis_title='',
                    yaxis_title='Taxa de Cancelamento (%)',
                    height=550,
                    showlegend=False,
                    hovermode='x unified',
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    margin=dict(l=40, r=40, t=50, b=0),   # <<< AQUI VOCÊ CONTROLA A ALTURA/ESPAÇAMENTO
                    xaxis=dict(
                        showgrid=True,
                        gridcolor='rgba(128,128,128,0.2)',
                        tickformat="%b/%y",   # <<< mostra como JAN/25, FEV/25, MAR/25 ...
                        tickfont=dict(size=15, color='white')  # <<< aumenta tamanho e cor da legenda dos meses
                    ),
                    yaxis=dict(
                        showgrid=True,
                        gridcolor='rgba(128,128,128,0.2)',
                        tickformat='.2f',
                        range=[0, df_evolucao['Taxa_Cancelamento'].max() * 1.1]  # 10% de folga no topo
                    )
                )


                st.plotly_chart(fig_evolucao_taxa, use_container_width=True)

        st.markdown("---")

        # Seção de gráficos principais
        st.markdown("<br>", unsafe_allow_html=True)
        
        # ===============================
        # 📊 Exibição dos Dados (Emissões e Cancelamentos)
        # ===============================
        st.subheader("📊 Exibição dos Dados (Emissões e Cancelamentos)")
        tipo_agregacao = st.radio(
            "Selecione o tipo:",   
            ("Totais", "Médias"),
            index=0,
            horizontal=True
        )
        
        col1_chart, col2_chart = st.columns(2)
        
        with col1_chart:
            # Título dinâmico baseado no tipo de agregação
            st.subheader(f"📈 Emissões por Mês ({tipo_agregacao})")
            
            # Aplicar agregação baseada na seleção
            if tipo_agregacao == "Totais":
                emissoes_mes = df_filtrado.groupby('MÊS')['CTRC_EMITIDO'].sum().reset_index()
            else:  # Médias
                emissoes_mes = df_filtrado.groupby('MÊS')['CTRC_EMITIDO'].mean().reset_index()
            
            # Ordenar meses cronologicamente
            meses_ordem = ['JANEIRO', 'FEVEREIRO', 'MARÇO', 'ABRIL', 'MAIO', 'JUNHO', 
                           'JULHO', 'AGOSTO', 'SETEMBRO', 'OUTUBRO', 'NOVEMBRO', 'DEZEMBRO']
            emissoes_mes["ordem"] = emissoes_mes["MÊS"].map({mes: i for i, mes in enumerate(meses_ordem)})
            emissoes_mes = emissoes_mes.sort_values("ordem")

            fig_emissoes_mes = px.bar(
                emissoes_mes,
                x="MÊS",
                y="CTRC_EMITIDO",
                title="",
                color="CTRC_EMITIDO",
                color_continuous_scale='Blues',
                text="CTRC_EMITIDO"
            )
            
            # Formatação do texto baseada no tipo de agregação
            if tipo_agregacao == "Totais":
                fig_emissoes_mes.update_traces(
                    texttemplate='%{y:,}'.replace(",", "."),
                    textposition='outside',
                    textfont_size=15
                )
            else:  # Médias
                fig_emissoes_mes.update_traces(
                    texttemplate='%{text:,.0f}',
                    textposition='outside',
                    textfont_size=15
                )
                fig_emissoes_mes.update_yaxes(
                    tickformat=".0f",
                    separatethousands=True  # <<< força 43.292 em vez de 43,292
                    )
                
            fig_emissoes_mes.update_layout(
                xaxis_tickangle=0,
                showlegend=False,
                margin=dict(t=50, b=50, l=70, r=20),
                yaxis=dict(
                    range=[0, emissoes_mes["CTRC_EMITIDO"].max() * 1.3],
                    tickformat=",d"  # Garante que o número seja exibido por completo, com separador de milhar.
                ),
                coloraxis_colorbar=dict(
                    tickformat=",d"  # Boa prática manter a barra de cores consistente
                ),
                height=450
            )

            st.plotly_chart(fig_emissoes_mes, use_container_width=True)

        with col2_chart:
            # Título dinâmico baseado no tipo de agregação
            st.subheader(f"✖️ Cancelamentos por Mês ({tipo_agregacao})")
            
            # Aplicar agregação baseada na seleção
            if tipo_agregacao == "Totais":
                cancelamentos_mes = cancelamentos_filtrado.groupby('MÊS').size().reset_index(name='Cancelamentos')
            else:  # Médias
                # Para médias de cancelamentos, calcular média diária por mês
                cancelamentos_por_dia = cancelamentos_filtrado.groupby(['MÊS', cancelamentos_filtrado['DATA_CANCELADO'].dt.date]).size().reset_index(name='Cancelamentos_Dia')
                cancelamentos_mes = cancelamentos_por_dia.groupby('MÊS')['Cancelamentos_Dia'].mean().reset_index()
                cancelamentos_mes.rename(columns={'Cancelamentos_Dia': 'Cancelamentos'}, inplace=True)
            
            # Ordenar meses cronologicamente
            meses_ordem = ['JANEIRO', 'FEVEREIRO', 'MARÇO', 'ABRIL', 'MAIO', 'JUNHO', 
                           'JULHO', 'AGOSTO', 'SETEMBRO', 'OUTUBRO', 'NOVEMBRO', 'DEZEMBRO']
            cancelamentos_mes["ordem"] = cancelamentos_mes["MÊS"].map({mes: i for i, mes in enumerate(meses_ordem)})
            cancelamentos_mes = cancelamentos_mes.sort_values("ordem")

            fig_canc_mes = px.bar(
                cancelamentos_mes,
                x="MÊS",
                y="Cancelamentos",
                title="",
                color="Cancelamentos",
                color_continuous_scale='Reds',
                text="Cancelamentos"
            )
            
            # Formatação do texto baseada no tipo de agregação
            if tipo_agregacao == "Totais":
                fig_canc_mes.update_traces(
                    texttemplate='%{text}',
                    textposition='outside',
                    textfont_size=15
                )
            else:  # Médias
                fig_canc_mes.update_traces(
                    texttemplate='%{text:.0f}',
                    textposition='outside',
                    textfont_size=15
                )
                
            fig_canc_mes.update_layout(
                xaxis_tickangle=0,
                showlegend=False,
                margin=dict(t=50, b=50, l=70, r=20),
                yaxis=dict(range=[0, cancelamentos_mes["Cancelamentos"].max() * 1.2]),
                height=450
            )

            st.plotly_chart(fig_canc_mes, use_container_width=True)
    
    with tab2:
        st.header("📈 Análise Temporal Avançada")

        # Criar cópias dos dataframes filtrados globalmente para uso específico da aba
        df_tab2 = df_filtrado.copy()
        cancelamentos_tab2 = cancelamentos_filtrado.copy()

        if df_tab2.empty:
            st.warning("Nenhum dado disponível para o período selecionado.")
        else:
            # ===============================
            # Seção 1: Visão Geral Temporal
            # ===============================
            st.subheader("🔍 Visão Geral Temporal")

            col1, col2, col3, col4 = st.columns(4)

            dias_periodo = (df_tab2["DATA_EMISSÃO"].max() - df_tab2["DATA_EMISSÃO"].min()).days + 1
            dias_com_emissao = df_tab2["DATA_EMISSÃO"].nunique()
            pico_diario = df_tab2.groupby("DATA_EMISSÃO")["CTRC_EMITIDO"].sum().max()
            media_diaria_periodo = df_tab2.groupby("DATA_EMISSÃO")["CTRC_EMITIDO"].sum().mean()

            with col1:
                st.markdown(f"""
                <div class="kpi-card kpi-blue">
                    <div class="kpi-icon">📅</div>
                    <div class="kpi-value">{dias_periodo}</div>
                    <div class="kpi-label">Período Analisado<br>{dias_periodo} dias</div>
                </div>
                """, unsafe_allow_html=True)

            with col2:
                st.markdown(f"""
                <div class="kpi-card kpi-green">
                    <div class="kpi-icon">📊</div>
                    <div class="kpi-value">{dias_com_emissao}</div>
                    <div class="kpi-label">Dias com Emissão<br>Total de dias ativos</div>
                </div>
                """, unsafe_allow_html=True)

            with col3:
                st.markdown(f"""
                <div class="kpi-card kpi-orange">
                    <div class="kpi-icon">🚀</div>
                    <div class="kpi-value">{format_number(pico_diario)}</div>
                    <div class="kpi-label">Pico Diário<br>Maior emissão em um dia</div>
                </div>
                """, unsafe_allow_html=True)

            with col4:
                st.markdown(f"""
                <div class="kpi-card kpi-teal">
                    <div class="kpi-icon">📈</div>
                    <div class="kpi-value">{format_number(media_diaria_periodo)}</div>
                    <div class="kpi-label">Média Diária<br>Emissões por dia</div>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("---")

            # ===============================
            # 📊 Análise Temporal de Emissões e Cancelamentos
            # ===============================
            st.subheader("📊 Análise Temporal de Emissões e Cancelamentos")

            # ===============================
            # 🔵 Evolução Temporal de Emissões Totais
            # ===============================
            st.markdown("<h3 style='color:#2563eb'>🔵 Evolução Temporal de Emissões Totais</h3>", unsafe_allow_html=True)

            granularidade_emissoes_temporal = st.radio(
                "Selecione a granularidade para Emissões (Totais):",
                options=["Diário", "Semanal", "Mensal"],
                horizontal=True,
                key="gran_emissoes_temporal"
            )

            # Preparar dados base de emissões
            df_base_emissoes_temporal = df_tab2[["DATA_EMISSÃO", "CTRC_EMITIDO"]].copy()

            if granularidade_emissoes_temporal == "Diário":
                df_trend_emissoes_temporal = df_base_emissoes_temporal.groupby('DATA_EMISSÃO')['CTRC_EMITIDO'].sum().reset_index()
                periodo_label_emissoes = "dias"
                future_periods_emissoes = 7
            elif granularidade_emissoes_temporal == "Semanal":
                # Agrupa por semana, mas ajusta para cair na sexta-feira
                df_trend_emissoes_temporal = (
                    df_base_emissoes_temporal
                    .assign(SEMANA=df_base_emissoes_temporal['DATA_EMISSÃO'] - pd.to_timedelta(df_base_emissoes_temporal['DATA_EMISSÃO'].dt.weekday - 4, unit='D'))
                    .groupby('SEMANA')['CTRC_EMITIDO'].sum()
                    .reset_index()
                    .rename(columns={'SEMANA':'DATA_EMISSÃO'})
                )
                periodo_label_emissoes = "semanas"
                future_periods_emissoes = 4

                # 🔹 Aqui cria a figura primeiro
                fig_trend_emissoes_temporal = go.Figure()

                # 🔹 Adiciona os dados históricos
                fig_trend_emissoes_temporal.add_trace(go.Scatter(
                    x=df_trend_emissoes_temporal['DATA_EMISSÃO'],
                    y=df_trend_emissoes_temporal['CTRC_EMITIDO'],
                    mode="lines+markers+text", 
                    name="Histórico",
                    line=dict(color='#3b82f6', width=3),
                    marker=dict(size=6, color='white', line=dict(color='#3b82f6', width=2))
                ))

                # 🔹 Extrair apenas o início de cada mês
                # 🔹 Ajusta o eixo X para mostrar só início de cada mês (Jan/2025, Fev/2025, ...)
                tickvals = pd.date_range(
                    start=df_trend_emissoes_temporal['DATA_EMISSÃO'].min().replace(day=1),
                    end=df_trend_emissoes_temporal['DATA_EMISSÃO'].max(),
                    freq='MS'  # "Month Start"
                )

                # 🔹 Dicionário para abreviações (PT-BR + fallback EN)
                meses_abrev = {
                    "jan": "Jan", "fev": "Fev", "mar": "Mar",
                    "abr": "Abr", "mai": "Mai", "jun": "Jun",
                    "jul": "Jul", "ago": "Ago", "set": "Set",
                    "out": "Out", "nov": "Nov", "dez": "Dez",
                    "feb": "Fev", "apr": "Abr", "may": "Mai",   # fallback EN
                    "aug": "Ago", "sep": "Set", "oct": "Out", "dec": "Dez"
                }

                ticktext = [
                    f"{meses_abrev[d.strftime('%b').lower()]}/{d.strftime('%y')}"
                    for d in tickvals
                ]


                fig_trend_emissoes_temporal.update_xaxes(
                    dtick="M1",  # força marcação mensal
                    tickformat="%b/%y",  # exemplo: Jan/25, Fev/25
                    ticklabelmode="period"  # garante 1 label por mês
                )

            else:  # Mensal
                df_trend_emissoes_temporal = (df_base_emissoes_temporal
                                            .assign(MES_REF=df_base_emissoes_temporal['DATA_EMISSÃO'].dt.to_period('M').apply(lambda r: r.start_time))
                                            .groupby('MES_REF')['CTRC_EMITIDO'].sum()
                                            .reset_index()
                                            .rename(columns={'MES_REF':'DATA_EMISSÃO'}))
                periodo_label_emissoes = "meses"
                future_periods_emissoes = 3

            # Calcular previsão para emissões
            if len(df_trend_emissoes_temporal) >= 2:
                x_emissoes_temporal = (df_trend_emissoes_temporal['DATA_EMISSÃO'] - df_trend_emissoes_temporal['DATA_EMISSÃO'].min()).dt.days.values
                y_emissoes_temporal = df_trend_emissoes_temporal['CTRC_EMITIDO'].values
                
                # Regressão linear para emissões
                coef_emissoes_temporal = np.polyfit(x_emissoes_temporal, y_emissoes_temporal, 1)
                poly_emissoes_temporal = np.poly1d(coef_emissoes_temporal)
                
                # Gerar previsões futuras para emissões
                if granularidade_emissoes_temporal == "Diário":
                    future_x_emissoes_temporal = np.arange(x_emissoes_temporal[-1] + 1, x_emissoes_temporal[-1] + future_periods_emissoes + 1)
                    future_dates_emissoes_temporal = [df_trend_emissoes_temporal['DATA_EMISSÃO'].max() + timedelta(days=i) for i in range(1, future_periods_emissoes + 1)]
                elif granularidade_emissoes_temporal == "Semanal":
                    future_x_emissoes_temporal = np.arange(x_emissoes_temporal[-1] + 7, x_emissoes_temporal[-1] + (future_periods_emissoes * 7) + 1, 7)
                    future_dates_emissoes_temporal = [df_trend_emissoes_temporal['DATA_EMISSÃO'].max() + timedelta(weeks=i) for i in range(1, future_periods_emissoes + 1)]
                else:  # Mensal
                    future_x_emissoes_temporal = np.arange(x_emissoes_temporal[-1] + 30, x_emissoes_temporal[-1] + (future_periods_emissoes * 30) + 1, 30)
                    future_dates_emissoes_temporal = []
                    last_date = df_trend_emissoes_temporal['DATA_EMISSÃO'].max()
                    for i in range(1, future_periods_emissoes + 1):
                        if last_date.month + i <= 12:
                            future_dates_emissoes_temporal.append(last_date.replace(month=last_date.month + i))
                        else:
                            future_dates_emissoes_temporal.append(last_date.replace(year=last_date.year + 1, month=(last_date.month + i) % 12))
                
                future_y_emissoes_temporal = poly_emissoes_temporal(future_x_emissoes_temporal)
                
                # Criar gráfico de emissões
                fig_trend_emissoes_temporal = go.Figure()
                
                # Define se mostra rótulos ou não
                if granularidade_emissoes_temporal == "Diário":
                    if mes_selecionado == "Todos":
                        trace_mode = "lines+markers"   # <<< sem rótulos
                        trace_text = None
                        text_size = None
                    else:
                        trace_mode = "lines+markers+text"
                        trace_text = [f"{v:,.0f}".replace(",", ".") for v in y_emissoes_temporal]
                        text_size = 16   # <<< maior no diário
                elif granularidade_emissoes_temporal == "Semanal":
                    trace_mode = "lines+markers+text"
                    trace_text = [f"{v:,.0f}".replace(",", ".") for v in y_emissoes_temporal]
                    text_size = 12       # <<< menor no semanal
                else:  # Mensal
                    trace_mode = "lines+markers+text"
                    trace_text = [f"{v:,.0f}".replace(",", ".") for v in y_emissoes_temporal]
                    text_size = 12       # <<< médio no mensal
                
                fig_trend_emissoes_temporal.add_trace(go.Scatter(
                    x=df_trend_emissoes_temporal['DATA_EMISSÃO'], 
                    y=y_emissoes_temporal, 
                    mode=trace_mode,
                    name='Histórico', 
                    line=dict(color='#3b82f6', width=3),
                    marker=dict(size=6, color='white', line=dict(color='#3b82f6', width=2)),
                    hovertemplate="<b>%{x}</b><br>Emissões: %{customdata}<extra></extra>",
                    customdata=[format_number(v) for v in y_emissoes_temporal],
                    text=trace_text,
                    textposition="top center",
                    # só aplica textfont se realmente houver rótulos
                    textfont=dict(size=text_size, color="white", family="Verdana") if text_size else None
                ))
                
                # 🔹 Reaplica o ajuste do eixo X se for semanal
                if granularidade_emissoes_temporal == "Semanal":
                    fig_trend_emissoes_temporal.update_xaxes(
                        dtick="M1",              # força 1 tick por mês
                        tickformat="%b/%y",      # Jan/25, Fev/25
                        ticklabelmode="period"   # 1 rótulo por mês
                    )
                
                # Layout do gráfico de emissões
                fig_trend_emissoes_temporal.update_layout(
                    height=500,
                    margin=dict(l=20, r=20, t=40, b=20),
                    xaxis_title="Data",
                    yaxis_title="CTRCs Emitidos",
                    showlegend=True,
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=1.02,
                        xanchor="right",
                        x=1
                    ),
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    xaxis=dict(
                        showgrid=True,
                        gridcolor='rgba(128,128,128,0.2)',
                        tickformat="%b/%y",   # <<< força exibição Jan/25, Fev/25, etc
                        tickfont=dict(size=13, family="Verdana", color="white")  # <<< aumenta fonte meses
                    ),
                    yaxis=dict(
                        tickformat=",d",   # força número inteiro
                        separatethousands=True  # <<< separa milhares com ponto
                    )
                )
                
                # 🔹 Dicionário de meses abreviados em português
                meses_abrev = {
                    # Inglês
                    "jan": "Jan", "feb": "Fev", "mar": "Mar",
                    "apr": "Abr", "may": "Mai", "jun": "Jun",
                    "jul": "Jul", "aug": "Ago", "sep": "Set",
                    "oct": "Out", "nov": "Nov", "dec": "Dez",
                    # Português
                    "fev": "Fev", "abr": "Abr", "mai": "Mai",
                    "jun": "Jun", "jul": "Jul", "ago": "Ago",
                    "set": "Set", "out": "Out", "nov": "Nov", "dez": "Dez"
                }
                
                # 🔹 Ajustar labels do eixo X dependendo do filtro e granularidade
                if granularidade_emissoes_temporal == "Diário" and mes_selecionado == "Todos":
                    # Caso 1: Diário + Todos → mês/ano
                    tickvals = (
                        df_trend_emissoes_temporal['DATA_EMISSÃO']
                        .dt.to_period("M")
                        .drop_duplicates()
                        .dt.start_time
                    )
                    ticktext = [
                        f"{meses_abrev[dt.strftime('%b').lower()]}/{dt.strftime('%y')}"
                        for dt in tickvals
                    ]
                
                elif granularidade_emissoes_temporal == "Diário" and mes_selecionado != "Todos":
                    # Caso 2: Diário + 1 mês → dias do mês
                    tickvals = df_trend_emissoes_temporal['DATA_EMISSÃO'].unique()
                    ticktext = [
                        f"{dt.strftime('%d')}/{meses_abrev[dt.strftime('%b').lower()]}"
                        for dt in tickvals
                    ]
                
                elif granularidade_emissoes_temporal == "Mensal":
                    # Caso 3: Mensal → mês/ano
                    tickvals = df_trend_emissoes_temporal['DATA_EMISSÃO'].unique()
                    ticktext = [
                        f"{meses_abrev[pd.to_datetime(dt).strftime('%b').lower()]}/{pd.to_datetime(dt).strftime('%y')}"
                        for dt in tickvals
                    ]
                
                elif granularidade_emissoes_temporal == "Semanal":
                    # Caso 4: Semanal → apenas mês/ano (um rótulo por mês)
                    tickvals = (
                        df_trend_emissoes_temporal['DATA_EMISSÃO']
                        .dt.to_period("M")
                        .drop_duplicates()
                        .dt.start_time
                    )
                    ticktext = [
                        f"{meses_abrev[dt.strftime('%b').lower()]}/{dt.strftime('%y')}"
                        for dt in tickvals
                    ]
                
                fig_trend_emissoes_temporal.update_xaxes(
                    tickvals=tickvals,
                    ticktext=ticktext
                )


                # 🔹 Dicionário de dias da semana em português
                dias_semana = {
                    0: "Segunda-feira", 1: "Terça-feira", 2: "Quarta-feira",
                    3: "Quinta-feira", 4: "Sexta-feira", 5: "Sábado", 6: "Domingo"
                }

                # 🔹 Montar custom_hover dependendo da granularidade
                custom_hover = []
                if granularidade_emissoes_temporal == "Diário":
                    # Exemplo: 📅 06/01 | 📆 Segunda-feira | 📊 Total
                    custom_hover = [
                        [
                            dt.strftime('%d/%m'),                  # 📅 Data
                            dias_semana[dt.weekday()],             # 📆 Dia da semana
                            y                                      # 📊 Total emissões
                        ]
                        for dt, y in zip(
                            df_trend_emissoes_temporal['DATA_EMISSÃO'],
                            df_trend_emissoes_temporal['CTRC_EMITIDO']
                        )
                    ]

                elif granularidade_emissoes_temporal == "Semanal":
                    # Exemplo: 📅 06/01 | 📆 Semana | 📊 Total    
                    custom_hover = [
                        [
                            dt.strftime('%d/%m'),                  # 📅 Data de referência da semana
                            "Semana",                              # 📆 texto fixo
                            y
                        ]
                        for dt, y in zip(
                            df_trend_emissoes_temporal['DATA_EMISSÃO'],
                            df_trend_emissoes_temporal['CTRC_EMITIDO']
                        )
                    ]

                elif granularidade_emissoes_temporal == "Mensal":
                    # Exemplo: 📅 Jan/2025 | 📆 Mês | 📊 Total
                    custom_hover = [
                        [
                            dt.strftime('%b/%Y').capitalize(),     # 📅 Mês/ano
                            "Mês",                                 # 📆 texto fixo
                            y
                        ]
                        for dt, y in zip(
                            df_trend_emissoes_temporal['DATA_EMISSÃO'],
                            df_trend_emissoes_temporal['CTRC_EMITIDO']
                        )
                    ]

                # 🔹 Atualizar trace com hover customizado e ícones
                fig_trend_emissoes_temporal.data[0].update(
                    customdata=[
                        [dt.strftime('%d/%m'),
                        dias_semana[dt.weekday()],
                        f"{y:,.0f}".replace(",", ".")]   # aqui já troca vírgula por ponto
                        for dt, y in zip(
                            df_trend_emissoes_temporal['DATA_EMISSÃO'],
                            df_trend_emissoes_temporal['CTRC_EMITIDO']
                        )
                    ],
                    hovertemplate=(
                        "📅 %{customdata[0]}<br>"
                        "📆 %{customdata[1]}<br>"
                        "📊 Total de Emissões: %{customdata[2]}<extra></extra>"
                    )
                )

                # 🔹 Atualizar eixo X com apenas dd/mm
                fig_trend_emissoes_temporal.update_xaxes(
                tickvals=tickvals,
                ticktext=ticktext
            )

                st.plotly_chart(fig_trend_emissoes_temporal, use_container_width=True)
                
                # Mostrar insights da previsão de emissões
                tendencia_emissoes = "crescente" if coef_emissoes_temporal[0] > 0 else "decrescente" if coef_emissoes_temporal[0] < 0 else "estável"
                col1, col2, col3 = st.columns(3)
                                
            else:
                st.info("Dados insuficientes para gerar previsão de emissões. São necessários pelo menos 2 pontos de dados.")

            st.markdown("---")

      
            # ===============================
            # 🟢 Evolução Temporal de Emissões Médias
            # ===============================
            st.markdown("<h3 style='color:#059669'>🟢 Evolução Temporal de Emissões Médias</h3>", unsafe_allow_html=True)
            
            granularidade_medias_temporal = st.radio(
                "Selecione a granularidade para Emissões (Médias):",
                options=["Diário", "Semanal", "Mensal"],
                horizontal=True,
                key="gran_medias_temporal"
            )
            
            # Preparar dados base de emissões para médias
            df_base_medias_temporal = df_tab2[["DATA_EMISSÃO", "CTRC_EMITIDO"]].copy()
            
            if granularidade_medias_temporal == "Diário":
                df_trend_medias_temporal = df_base_medias_temporal.groupby("DATA_EMISSÃO")["CTRC_EMITIDO"].mean().reset_index()
                periodo_label_medias = "dias"
                future_periods_medias = 7
                show_text_medias = False
            elif granularidade_medias_temporal == "Semanal":
                # Agrupa por semana ajustando para cair na sexta-feira
                df_trend_medias_temporal = (
                    df_base_medias_temporal
                    .assign(SEMANA=df_base_medias_temporal["DATA_EMISSÃO"] - pd.to_timedelta(df_base_medias_temporal["DATA_EMISSÃO"].dt.weekday - 4, unit="D"))
                    .groupby("SEMANA")["CTRC_EMITIDO"].mean()
                    .reset_index()
                    .rename(columns={"SEMANA": "DATA_EMISSÃO"})
                )
                periodo_label_medias = "semanas"
                future_periods_medias = 4
                show_text_medias = True
            
            else:  # Mensal
                df_trend_medias_temporal = (df_base_medias_temporal
                                           .assign(MES_REF=df_base_medias_temporal["DATA_EMISSÃO"].dt.to_period("M").apply(lambda r: r.start_time))
                                           .groupby("MES_REF")["CTRC_EMITIDO"].mean()
                                           .reset_index()
                                           .rename(columns={"MES_REF": "DATA_EMISSÃO"}))
                periodo_label_medias = "meses"
                future_periods_medias = 3
                show_text_medias = True
            
            # Calcular previsão para médias de emissões
            if len(df_trend_medias_temporal) >= 2:
                x_medias_temporal = (df_trend_medias_temporal["DATA_EMISSÃO"] - df_trend_medias_temporal["DATA_EMISSÃO"].min()).dt.days.values
                y_medias_temporal = df_trend_medias_temporal["CTRC_EMITIDO"].values
            
                # Regressão linear para médias
                coef_medias_temporal = np.polyfit(x_medias_temporal, y_medias_temporal, 1)
                poly_medias_temporal = np.poly1d(coef_medias_temporal)
            
                # Gerar previsões futuras para médias
                if granularidade_medias_temporal == "Diário":
                    future_x_medias_temporal = np.arange(x_medias_temporal[-1] + 1, x_medias_temporal[-1] + future_periods_medias + 1)
                    future_dates_medias_temporal = [df_trend_medias_temporal["DATA_EMISSÃO"].max() + timedelta(days=i) for i in range(1, future_periods_medias + 1)]
                elif granularidade_medias_temporal == "Semanal":
                    future_x_medias_temporal = np.arange(x_medias_temporal[-1] + 7, x_medias_temporal[-1] + (future_periods_medias * 7) + 1, 7)
                    future_dates_medias_temporal = [df_trend_medias_temporal["DATA_EMISSÃO"].max() + timedelta(weeks=i) for i in range(1, future_periods_medias + 1)]
                else:  # Mensal
                    future_x_medias_temporal = np.arange(x_medias_temporal[-1] + 30, x_medias_temporal[-1] + (future_periods_medias * 30) + 1, 30)
                    future_dates_medias_temporal = []
                    last_date = df_trend_medias_temporal["DATA_EMISSÃO"].max()
                    for i in range(1, future_periods_medias + 1):
                        if last_date.month + i <= 12:
                            future_dates_medias_temporal.append(last_date.replace(month=last_date.month + i))
                        else:
                            future_dates_medias_temporal.append(last_date.replace(year=last_date.year + 1, month=(last_date.month + i) % 12))
            
                future_y_medias_temporal = poly_medias_temporal(future_x_medias_temporal)
            
                # Criar gráfico de médias
                fig_trend_medias_temporal = go.Figure()
            
                # Mapeamento dos dias da semana em português
                dias_semana = {
                    0:"Segunda-feira", 1:"Terça-feira", 2:"Quarta-feira",
                    3:"Quinta-feira", 4:"Sexta-feira", 5:"Sábado", 6:"Domingo"
                }
            
                # Criar coluna com dia da semana (agora que df_trend_medias_temporal já existe!)
                df_trend_medias_temporal["DIA_SEMANA"] = df_trend_medias_temporal["DATA_EMISSÃO"].dt.weekday.map(dias_semana)
            
                # Trace com hover customizado
                fig_trend_medias_temporal.add_trace(go.Scatter(
                    x=df_trend_medias_temporal["DATA_EMISSÃO"],
                    y=y_medias_temporal,
                    mode="lines+markers+text" if show_text_medias else "lines+markers",
                    name="Média Histórica",
                    line=dict(color="#10b981", width=3),
                    marker=dict(size=6, color="white", line=dict(color="#10b981", width=2)),
                    customdata=np.stack([
                        df_trend_medias_temporal["DATA_EMISSÃO"].dt.strftime("%d/%m"),
                        df_trend_medias_temporal["DIA_SEMANA"],
                        y_medias_temporal
                    ], axis=-1),
                    hovertemplate="📅 %{customdata[0]}<br>📆 %{customdata[1]}<br>📊 Média de Emissões: %{customdata[2]:.0f}<extra></extra>",
                    text=[f"{v:,.0f}" for v in y_medias_temporal] if show_text_medias else None,
                    textposition="top center",
                    textfont=dict(size=15, color="white")
                ))
            
                # Layout do gráfico de médias
                fig_trend_medias_temporal.update_layout(
                    height=500,
                    margin=dict(l=20, r=20, t=40, b=20),
                    xaxis_title="Data",
                    yaxis_title="Média de CTRCs Emitidos",
                    showlegend=True,
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=1.02,
                        xanchor="right",
                        x=1
                    ),
                    plot_bgcolor="rgba(0,0,0,0)",
                    paper_bgcolor="rgba(0,0,0,0)",
                    xaxis=dict(
                        showgrid=True,
                        gridcolor="rgba(128,128,128,0.2)"
                    ),
                    yaxis=dict(
                        showgrid=True,
                        gridcolor="rgba(128,128,128,0.2)"
                    )
                )
            
                # 🔹 Dicionário de meses abreviados em português
                meses_abrev = {
                    "jan": "Jan", "feb": "Fev", "mar": "Mar",
                    "apr": "Abr", "may": "Mai", "jun": "Jun",
                    "jul": "Jul", "aug": "Ago", "sep": "Set",
                    "oct": "Out", "nov": "Nov", "dec": "Dez"
                }
            
                # Ajustar eixo X dependendo do filtro e granularidade
                if granularidade_medias_temporal == "Diário" and mes_selecionado == "Todos":
                    tickvals = (
                        df_trend_medias_temporal["DATA_EMISSÃO"]
                        .dt.to_period("M")
                        .drop_duplicates()
                        .dt.start_time
                    )
                    ticktext = [
                        f"{meses_abrev[d.strftime('%b').lower()]}/{d.strftime('%y')}"
                        for d in tickvals
                    ]
            
                elif granularidade_medias_temporal == "Diário" and mes_selecionado != "Todos":
                    tickvals = df_trend_medias_temporal["DATA_EMISSÃO"].unique()
                    ticktext = [
                        f"{d.strftime('%d')}/{meses_abrev[d.strftime('%b').lower()]}"
                        for d in tickvals
                    ]
            
                elif granularidade_medias_temporal == "Mensal" and mes_selecionado == "Todos":
                    tickvals = df_trend_medias_temporal["DATA_EMISSÃO"].unique()
                    ticktext = [
                        f"{meses_abrev[pd.to_datetime(d).strftime('%b').lower()]}/{pd.to_datetime(d).strftime('%y')}"
                        for d in tickvals
                    ]
            
                elif granularidade_medias_temporal == "Semanal" and mes_selecionado == "Todos":
                    tickvals = (
                        df_trend_medias_temporal["DATA_EMISSÃO"]
                        .dt.to_period("M")
                        .drop_duplicates()
                        .dt.start_time
                    )
                    ticktext = [
                        f"{meses_abrev[d.strftime('%b').lower()]}/{d.strftime('%y')}"
                        for d in tickvals
                    ]
            
                fig_trend_medias_temporal.update_xaxes(
                    tickvals=tickvals,
                    ticktext=ticktext,
                    tickfont=dict(size=14, color="white")
                )
            
                st.plotly_chart(fig_trend_medias_temporal, use_container_width=True)
            
                # Mostrar insights da previsão de médias
                tendencia_medias = "crescente" if coef_medias_temporal[0] > 0 else "decrescente" if coef_medias_temporal[0] < 0 else "estável"
                col1, col2, col3 = st.columns(3)
            
            else:
                st.info("Dados insuficientes para gerar previsão de médias. São necessários pelo menos 2 pontos de dados.")


            st.markdown("---")

           
           # ===============================
           # ===============================
            # 🔴 Evolução Temporal de Cancelamentos Totais
            # ===============================
            st.markdown("<h3 style='color:#dc2626'>🔴 Evolução Temporal de Cancelamentos Totais</h3>", unsafe_allow_html=True)
            
            granularidade_cancelamentos_temporal = st.radio(
                "Selecione a granularidade para Cancelamentos (Totais):",
                options=["Diário", "Semanal", "Mensal"],
                horizontal=True,
                key="gran_cancelamentos_temporal"
            )
            
            if not cancelamentos_tab2.empty:
                df_base_cancelamentos_temporal = cancelamentos_tab2[["DATA_CANCELADO"]].copy()
                df_base_cancelamentos_temporal['CANCELAMENTOS'] = 1
            
                if granularidade_cancelamentos_temporal == "Diário":
                    df_trend_cancelamentos_temporal = (
                        df_base_cancelamentos_temporal
                        .groupby('DATA_CANCELADO')['CANCELAMENTOS']
                        .sum()
                        .reset_index()
                        .rename(columns={'DATA_CANCELADO': 'DATA'})
                    )
                    show_text_cancelamentos = False
            
                elif granularidade_cancelamentos_temporal == "Semanal":
                    df_base_cancelamentos_temporal['SEMANA'] = (
                        df_base_cancelamentos_temporal['DATA_CANCELADO']
                        .apply(lambda d: d - pd.Timedelta(days=(d.weekday() - 4) % 7))
                    )
            
                    df_trend_cancelamentos_temporal = (
                        df_base_cancelamentos_temporal
                        .groupby('SEMANA')['CANCELAMENTOS'].sum()
                        .reset_index()
                        .rename(columns={'SEMANA': 'DATA'})
                    )
            
                    primeira_data = df_base_cancelamentos_temporal['DATA_CANCELADO'].min().normalize()
                    offset = (4 - primeira_data.weekday()) % 7
                    primeira_sexta = primeira_data + pd.Timedelta(days=offset)
            
                    df_trend_cancelamentos_temporal = df_trend_cancelamentos_temporal[
                        df_trend_cancelamentos_temporal['DATA'] >= primeira_sexta
                    ]
            
                    show_text_cancelamentos = True
            
                else:  # Mensal
                    df_trend_cancelamentos_temporal = (
                        df_base_cancelamentos_temporal
                        .assign(MES_REF=df_base_cancelamentos_temporal['DATA_CANCELADO'].dt.to_period('M').apply(lambda r: r.start_time))
                        .groupby('MES_REF')['CANCELAMENTOS'].sum()
                        .reset_index()
                        .rename(columns={'MES_REF': 'DATA'})
                    )
                    show_text_cancelamentos = True
            
                if len(df_trend_cancelamentos_temporal) >= 2:
                    x_cancelamentos_temporal = (
                        df_trend_cancelamentos_temporal['DATA'] - df_trend_cancelamentos_temporal['DATA'].min()
                    ).dt.days.values
                    y_cancelamentos_temporal = df_trend_cancelamentos_temporal['CANCELAMENTOS'].values
            
                    coef_cancelamentos_temporal = np.polyfit(x_cancelamentos_temporal, y_cancelamentos_temporal, 1)
                    poly_cancelamentos_temporal = np.poly1d(coef_cancelamentos_temporal)
            
                    fig_trend_cancelamentos_temporal = go.Figure()
            
                    if show_text_cancelamentos:
                        trace_mode = "lines+markers+text"
                        trace_text = [f"{v:,.0f}".replace(",", ".") for v in y_cancelamentos_temporal]
                    else:
                        trace_mode = "lines+markers"
                        trace_text = None
            
                    fig_trend_cancelamentos_temporal.add_trace(go.Scatter(
                        x=df_trend_cancelamentos_temporal['DATA'],
                        y=y_cancelamentos_temporal,
                        mode=trace_mode,
                        name="Histórico",
                        line=dict(color="#dc2626", width=3),
                        marker=dict(size=6, color="white", line=dict(color="#dc2626", width=2)),
                        text=trace_text,
                        textposition="top center",
                        textfont=dict(size=13, color="#FFFFFF", family="Verdana")
                    ))
            
                    # 🔹 Hover em PT-BR
                    dias_semana = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"]
                    meses_pt = {
                        1: "Janeiro",  2: "Fevereiro", 3: "Março",
                        4: "Abril",    5: "Maio",      6: "Junho",
                        7: "Julho",    8: "Agosto",    9: "Setembro",
                        10: "Outubro", 11: "Novembro", 12: "Dezembro"
                    }
            
                    fig_trend_cancelamentos_temporal.data[0].update(
                        customdata=[
                            [dt.strftime("%d/%m"),
                             dias_semana[dt.weekday()],
                             meses_pt[dt.month],
                             f"{y:,.0f}".replace(",", ".")]
                            for dt, y in zip(
                                df_trend_cancelamentos_temporal["DATA"],
                                df_trend_cancelamentos_temporal["CANCELAMENTOS"]
                            )
                        ],
                        hovertemplate=(
                            "📅 %{customdata[0]}<br>"
                            "📆 %{customdata[1]}<br>"
                            "🗓️ %{customdata[2]}<br>"
                            "✖️ Cancelamentos: %{customdata[3]}<extra></extra>"
                        )
                    )
            
                    # 🔹 Layout
                    fig_trend_cancelamentos_temporal.update_layout(
                        height=500,
                        margin=dict(l=20, r=20, t=40, b=20),
                        xaxis_title="Data",
                        yaxis_title="Cancelamentos",
                        showlegend=True,
                        legend=dict(
                            orientation="h",
                            yanchor="bottom",
                            y=1.02,
                            xanchor="right",
                            x=1
                        ),
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        yaxis=dict(
                            tickformat=",d",
                            separatethousands=True
                        )
                    )
            
                    # 🔹 Ajustar rótulos do eixo X (meses PT-BR)
                    meses_pt_abrev = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun",
                                      "Jul", "Ago", "Set", "Out", "Nov", "Dez"]
            
                    if granularidade_cancelamentos_temporal == "Diário" and mes_selecionado == "Todos":
                        tickvals = df_trend_cancelamentos_temporal['DATA'].dt.to_period("M").drop_duplicates().dt.start_time
                        ticktext = [f"{meses_pt_abrev[d.month-1]}/{str(d.year)[-2:]}" for d in tickvals]
            
                    elif granularidade_cancelamentos_temporal == "Diário" and mes_selecionado != "Todos":
                        tickvals = df_trend_cancelamentos_temporal['DATA'].unique()
                        ticktext = [f"{d.strftime('%d')}/{meses_pt_abrev[d.month-1]}" for d in tickvals]
            
                    elif granularidade_cancelamentos_temporal == "Mensal":
                        tickvals = df_trend_cancelamentos_temporal['DATA'].unique()
                        ticktext = [f"{meses_pt_abrev[pd.to_datetime(d).month-1]}/{pd.to_datetime(d).strftime('%y')}" for d in tickvals]
            
                    elif granularidade_cancelamentos_temporal == "Semanal":
                        tickvals = df_trend_cancelamentos_temporal['DATA'].dt.to_period("M").drop_duplicates().dt.start_time
                        ticktext = [f"{meses_pt_abrev[d.month-1]}/{str(d.year)[-2:]}" for d in tickvals]
            
                    fig_trend_cancelamentos_temporal.update_xaxes(
                        tickmode="array",
                        tickvals=tickvals,
                        ticktext=ticktext,
                        tickfont=dict(size=14, color="white")
                    )
            
                    st.plotly_chart(fig_trend_cancelamentos_temporal, use_container_width=True)


            st.markdown("---")

            # ===============================
            # Seção 4: Padrões por Dia da Semana
            # ===============================
            st.subheader("📅 Padrões por Dia da Semana")

            # (O código de preparação de dados continua o mesmo, sem alterações)
            df_weekday = df_tab2.copy()
            df_weekday['weekday_num'] = df_weekday['DATA_EMISSÃO'].dt.weekday
            weekday_map = {
                'Monday': 'Segunda', 'Tuesday': 'Terça', 'Wednesday': 'Quarta',
                'Thursday': 'Quinta', 'Friday': 'Sexta', 'Saturday': 'Sábado', 'Sunday': 'Domingo'
            }
            df_weekday['weekday_pt'] = df_weekday['DATA_EMISSÃO'].dt.day_name().map(weekday_map)
            weekday_stats = df_weekday.groupby(['weekday_num', 'weekday_pt'])['CTRC_EMITIDO'].agg(['sum', 'mean', 'std']).reset_index()

            if not cancelamentos_tab2.empty:
                df_canc_weekday = cancelamentos_tab2.copy()
                df_canc_weekday['weekday_num'] = df_canc_weekday['DATA_CANCELADO'].dt.weekday
                df_canc_weekday['weekday_pt'] = df_canc_weekday['DATA_CANCELADO'].dt.day_name().map(weekday_map)
                canc_sum_stats = df_canc_weekday.groupby(['weekday_num', 'weekday_pt']).size().reset_index(name='cancelamentos_sum')
                dias_unicos_com_canc = df_canc_weekday.groupby(['weekday_num', 'weekday_pt'])['DATA_CANCELADO'].nunique().reset_index(name='dias_com_cancelamento')
                canc_mean_stats = pd.merge(canc_sum_stats, dias_unicos_com_canc, on=['weekday_num', 'weekday_pt'])
                canc_mean_stats['cancelamentos_mean'] = canc_mean_stats['cancelamentos_sum'] / canc_mean_stats['dias_com_cancelamento']
                weekday_stats = pd.merge(weekday_stats, canc_sum_stats, on=['weekday_num', 'weekday_pt'], how='left')
                weekday_stats = pd.merge(weekday_stats, canc_mean_stats[['weekday_num', 'weekday_pt', 'cancelamentos_mean']], on=['weekday_num', 'weekday_pt'], how='left')
                weekday_stats.fillna(0, inplace=True)
            else:
                weekday_stats['cancelamentos_sum'] = 0
                weekday_stats['cancelamentos_mean'] = 0

            weekday_stats = weekday_stats.sort_values('weekday_num')

            # --- ADIÇÃO IMPORTANTE AQUI: Calcular a Taxa de Cancelamento ---
            # Evita divisão por zero caso não haja emissões em um dia
            weekday_stats['taxa_cancelamento'] = (
                (weekday_stats['cancelamentos_sum'] / weekday_stats['sum']) * 100
            ).fillna(0)
            # --- FIM DA ADIÇÃO ---


            # Criar duas colunas para os gráficos
            col1, col2 = st.columns(2)

            # ===============================
            # GRÁFICO 1: Totais com RÓTULOS MAIORES
            # ===============================
            with col1:
                st.markdown("### 📈 Emissões e Cancelamentos Totais")

                max_emissoes_sum = weekday_stats["sum"].max()
                max_cancelamentos_sum = weekday_stats["cancelamentos_sum"].max()
                
                fig_totais = make_subplots(specs=[[{"secondary_y": True}]])

                # Adicionar BARRAS de Emissões
                fig_totais.add_trace(go.Bar(
                    x=weekday_stats["weekday_pt"], y=weekday_stats["sum"],
                    name='Emissões', text=weekday_stats["sum"],
                    texttemplate='%{text:,.0f}'.replace(",", "."), textposition="outside",
                    marker_color="#0752ca",
                    # --- ALTERAÇÃO AQUI: Aumenta o tamanho da fonte do rótulo da barra ---
                    textfont_size=16 
                ), secondary_y=False)

                # Adicionar LINHA de Cancelamentos
                fig_totais.add_trace(go.Scatter(
                    x=weekday_stats["weekday_pt"], y=weekday_stats["cancelamentos_sum"],
                    name='Cancelamentos', mode='lines+markers+text',
                    line=dict(color='#ef4444', width=3),
                    marker=dict(size=8, color='white', line=dict(width=2, color='#ef4444')),
                    text=weekday_stats["cancelamentos_sum"].astype(int), textposition="top center",
                    # --- ALTERAÇÃO AQUI: Aumenta o tamanho da fonte do rótulo da linha ---
                    textfont=dict(size=14, color="#ffffff") 
                ), secondary_y=True)

                # Layout e eixos
                fig_totais.update_layout(
                    xaxis_title="Dia da Semana", height=550,
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
                )
                fig_totais.update_yaxes(
                    title_text="<b>Total de Emissões</b>", title_font_color="#3b82f6",
                    tickfont_color="#3b82f6", secondary_y=False, range=[0, max_emissoes_sum * 1.2]
                )
                fig_totais.update_yaxes(
                    title_text="<b>Total de Cancelamentos</b>", title_font_color="#ef4444",
                    tickfont_color="#ef4444", secondary_y=True, range=[0, max_cancelamentos_sum * 2.0]
                )
                
                st.plotly_chart(fig_totais, use_container_width=True)

                # (Coloque isso antes da seção de Estatísticas)

                # Agrupar CANCELAMENTOS por dia da semana
                df_weekday_canc = cancelamentos_tab2.copy() # Use o dataframe de cancelamentos da aba

                if not df_weekday_canc.empty:
                    # Mapear nomes dos dias da semana para português
                    weekday_map = {
                        'Monday': 'Segunda', 'Tuesday': 'Terça', 'Wednesday': 'Quarta',
                        'Thursday': 'Quinta', 'Friday': 'Sexta', 'Saturday': 'Sábado', 'Sunday': 'Domingo'
                    }
                    df_weekday_canc['weekday_num'] = df_weekday_canc['DATA_CANCELADO'].dt.weekday
                    df_weekday_canc['weekday_pt'] = df_weekday_canc['DATA_CANCELADO'].dt.day_name().map(weekday_map)
                    
                    # Contar cancelamentos por dia
                    weekday_canc_stats = df_weekday_canc.groupby(['weekday_num', 'weekday_pt']).size().reset_index(name='total_cancelamentos')
                    weekday_canc_stats = weekday_canc_stats.sort_values('weekday_num')
                else:
                    # Cria um dataframe vazio para evitar erros se não houver cancelamentos
                    weekday_canc_stats = pd.DataFrame(columns=['weekday_num', 'weekday_pt', 'total_cancelamentos'])


                # Estatísticas
                melhor_dia_totais = weekday_stats.loc[weekday_stats['sum'].idxmax(), 'weekday_pt']
                pior_dia_totais = weekday_stats.loc[weekday_stats['sum'].idxmin(), 'weekday_pt']

                # --- INÍCIO DA MODIFICAÇÃO ---

                # Encontrar o dia com mais cancelamentos
                if not weekday_canc_stats.empty:
                    dia_pico_cancelamentos = weekday_canc_stats.loc[weekday_canc_stats['total_cancelamentos'].idxmax(), 'weekday_pt']
                else:
                    dia_pico_cancelamentos = "N/A" # Caso não haja dados de cancelamento

                st.markdown("#### 📊 Estatísticas - Totais")
                st.markdown(f"🚀 **Dia de Pico (Emissões):** {melhor_dia_totais}")
                st.markdown(f"📉 **Menor Produção (Emissões):** {pior_dia_totais}")
                # Adiciona a nova estatística de cancelamentos
                st.markdown(f"🚨 **Pico de Cancelamentos:** {dia_pico_cancelamentos}")

                # --- FIM DA MODIFICAÇÃO ---

            # ===============================
            # GRÁFICO 2: Médias com RÓTULOS MAIORES
            # ===============================
            with col2:
                st.markdown("### 📊 Médias por Dia da Semana")

                max_emissoes_mean = weekday_stats["mean"].max()
                max_cancelamentos_mean = weekday_stats["cancelamentos_mean"].max()
                texto_media_cancelamento = weekday_stats["cancelamentos_mean"].astype(int)

                fig_medias = make_subplots(specs=[[{"secondary_y": True}]])

                # Adicionar BARRAS de Média de Emissões
                fig_medias.add_trace(go.Bar(
                    x=weekday_stats["weekday_pt"], y=weekday_stats["mean"],
                    name='Média de Emissões', text=weekday_stats["mean"],
                    texttemplate='%{text:.0f}', textposition="outside",
                    marker_color="#058d37",
                    # --- ALTERAÇÃO AQUI: Aumenta o tamanho da fonte do rótulo da barra ---
                    textfont_size=16
                ), secondary_y=False)

                # Adicionar LINHA de Média de Cancelamentos
                fig_medias.add_trace(go.Scatter(
                    x=weekday_stats["weekday_pt"], y=weekday_stats["cancelamentos_mean"],
                    name='Média de Cancelamentos', mode='lines+markers+text',
                    line=dict(color='#f97316', width=3),
                    marker=dict(size=8, color='white', line=dict(width=2, color='#f97316')),
                    text=texto_media_cancelamento, texttemplate='%{text:.0f}',
                    textposition="top center",
                    # --- ALTERAÇÃO AQUI: Aumenta o tamanho da fonte do rótulo da linha ---
                    textfont=dict(size=14, color="#ffffff")
                ), secondary_y=True)

                # Layout e eixos
                fig_medias.update_layout(
                    xaxis_title="Dia da Semana", height=550,
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
                )
                fig_medias.update_yaxes(
                    title_text="<b>Média de Emissões</b>", title_font_color="#22c55e",
                    tickfont_color="#22c55e", secondary_y=False, range=[0, max_emissoes_mean * 1.2]
                )
                fig_medias.update_yaxes(
                    title_text="<b>Média de Cancelamentos</b>", title_font_color="#f97316",
                    tickfont_color="#f97316", secondary_y=True, range=[0, max_cancelamentos_mean * 2.0]
                )

                st.plotly_chart(fig_medias, use_container_width=True)

                # Estatísticas
                melhor_dia_medias = weekday_stats.loc[weekday_stats['mean'].idxmax(), 'weekday_pt']
                pior_dia_medias = weekday_stats.loc[weekday_stats['mean'].idxmin(), 'weekday_pt']
                dia_mais_cancel_mean = weekday_stats.loc[weekday_stats['cancelamentos_mean'].idxmax(), 'weekday_pt']
                st.markdown("#### 📊 Estatísticas - Médias")
                st.markdown(f"🚀 **Dia de Pico (Média Emissões):** {melhor_dia_medias}")
                st.markdown(f"📉 **Menor Média (Emissões):** {pior_dia_medias}")
                st.markdown(f"🚨 **Pico de Cancelamentos (Média):** {dia_mais_cancel_mean}")

    
    with tab_individual:
        st.header("📌 Análise Individual")

        # Verifica se um usuário foi selecionado
        if usuario_selecionado == 'Todos':
            st.warning("Por favor, selecione um usuário no filtro da barra lateral para ver a análise individual.")
        else:
            # Criar cópias dos dataframes para a aba
            df_user = df_filtrado.copy()
            cancelamentos_user = cancelamentos_filtrado.copy()
            
            # Verificar se há dados para o usuário
            if df_user.empty:
                st.warning(f"Não há dados de emissões para o usuário {usuario_selecionado} no período selecionado.")
            else:
                # ===============================
                # ANÁLISE INDIVIDUAL DE EMISSÕES - KPIs
                # ===============================
                st.subheader("📈 Análise Individual de Emissões")
                
                # Calcular KPIs de emissões
                total_emissoes_user = df_user['CTRC_EMITIDO'].sum()
                
                # Média diária de emissões
                if not df_user.empty:
                    emissoes_diarias_user = df_user.groupby(df_user['DATA_EMISSÃO'].dt.date)['CTRC_EMITIDO'].sum()
                    media_diaria_user = emissoes_diarias_user.mean()
                    
                    # Média semanal de emissões
                    df_user_copy = df_user.copy()
                    df_user_copy['semana'] = df_user_copy['DATA_EMISSÃO'].dt.isocalendar().week
                    df_user_copy['ano'] = df_user_copy['DATA_EMISSÃO'].dt.year
                    emissoes_semanais_user = df_user_copy.groupby(['ano', 'semana'])['CTRC_EMITIDO'].sum()
                    media_semanal_user = emissoes_semanais_user.mean()
                    
                    # Média mensal de emissões
                    emissoes_mensais_user = df_user.groupby(df_user['DATA_EMISSÃO'].dt.to_period('M'))['CTRC_EMITIDO'].sum()
                    media_mensal_user = emissoes_mensais_user.mean()
                else:
                    media_diaria_user = media_semanal_user = media_mensal_user = 0

                # KPIs de Emissões em cartões coloridos
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.markdown(f"""
                    <div class="kpi-card kpi-blue">
                        <div class="kpi-icon">📦</div>
                        <div class="kpi-value">{format_number(total_emissoes_user)}</div>
                        <div class="kpi-label">Total de Emissões<br>no período</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.markdown(f"""
                    <div class="kpi-card kpi-green">
                        <div class="kpi-icon">📅</div>
                        <div class="kpi-value">{format_number(media_diaria_user)}</div>
                        <div class="kpi-label">Média Diária<br>de Emissões</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col3:
                    st.markdown(f"""
                    <div class="kpi-card kpi-teal">
                        <div class="kpi-icon">🗓️</div>
                        <div class="kpi-value">{format_number(media_semanal_user)}</div>
                        <div class="kpi-label">Média Semanal<br>de Emissões</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col4:
                    st.markdown(f"""
                    <div class="kpi-card kpi-purple">
                        <div class="kpi-icon">📊</div>
                        <div class="kpi-value">{format_number(media_mensal_user)}</div>
                        <div class="kpi-label">Média Mensal<br>de Emissões</div>
                    </div>
                    """, unsafe_allow_html=True)

                st.markdown("---")

                # ===============================
                # ANÁLISE INDIVIDUAL DE CANCELAMENTOS - KPIs
                # ===============================
                st.subheader("❌ Análise Individual de Cancelamentos")
                
                # Calcular KPIs de cancelamentos
                total_cancelamentos_user = len(cancelamentos_user)
                taxa_cancelamento_user = (total_cancelamentos_user / total_emissoes_user * 100) if total_emissoes_user > 0 else 0
                
                # Média diária de cancelamentos
                if not cancelamentos_user.empty:
                    cancelamentos_diarios_user = cancelamentos_user.groupby(cancelamentos_user['DATA_CANCELADO'].dt.date).size()
                    media_diaria_canc_user = cancelamentos_diarios_user.mean()
                    
                    # Média semanal de cancelamentos
                    cancelamentos_user_copy = cancelamentos_user.copy()
                    cancelamentos_user_copy['semana'] = cancelamentos_user_copy['DATA_CANCELADO'].dt.isocalendar().week
                    cancelamentos_user_copy['ano'] = cancelamentos_user_copy['DATA_CANCELADO'].dt.year
                    cancelamentos_semanais_user = cancelamentos_user_copy.groupby(['ano', 'semana']).size()
                    media_semanal_canc_user = cancelamentos_semanais_user.mean()
                    
                    # Média mensal de cancelamentos
                    cancelamentos_mensais_user = cancelamentos_user.groupby(cancelamentos_user['DATA_CANCELADO'].dt.to_period('M')).size()
                    media_mensal_canc_user = cancelamentos_mensais_user.mean()
                else:
                    media_diaria_canc_user = media_semanal_canc_user = media_mensal_canc_user = 0

                # KPIs de Cancelamentos em cartões coloridos
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.markdown(f"""
                    <div class="kpi-card kpi-red">
                        <div class="kpi-icon">✖️</div>
                        <div class="kpi-value">{format_number(total_cancelamentos_user)}</div>
                        <div class="kpi-label">Total de Cancelamentos<br>no período</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.markdown(f"""
                    <div class="kpi-card kpi-orange">
                        <div class="kpi-icon">📅</div>
                        <div class="kpi-value">{format_number(media_diaria_canc_user)}</div>
                        <div class="kpi-label">Média Diária<br>de Cancelamentos</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col3:
                    st.markdown(f"""
                    <div class="kpi-card kpi-indigo">
                        <div class="kpi-icon">🗓️</div>
                        <div class="kpi-value">{format_number(media_semanal_canc_user)}</div>
                        <div class="kpi-label">Média Semanal<br>de Cancelamentos</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col4:
                    # Cor do cartão baseada na taxa de cancelamento
                    cor_taxa = "kpi-green" if taxa_cancelamento_user <= 0.75 else "kpi-orange"
                    st.markdown(f"""
                    <div class="kpi-card {cor_taxa}">
                        <div class="kpi-icon">📊</div>
                        <div class="kpi-value">{taxa_cancelamento_user:.2f}%</div>
                        <div class="kpi-label">Taxa de Cancelamento<br>do usuário</div>
                    </div>
                    """, unsafe_allow_html=True)

                st.markdown("---")
                

                # Gráficos de Emissões e Cancelamentos
                # ===============================
                # 📊 Nova Análise Visual
                # ===============================
                st.subheader("📊 Análise de Emissões e Cancelamentos")

                col1, col2 = st.columns(2)

                # --- Emissões ---
                with col1:
                    tipo_agregacao_emissoes_user = st.radio(
                        "Visualizar Emissões por:",
                        ("Total", "Média"),
                        key="agregacao_emissoes_user"
                    )
                    
                    if tipo_agregacao_emissoes_user == "Total":
                        # Calcular totais diário, semanal e mensal para emissões
                        emissoes_diarias_total = df_user.groupby(df_user["DATA_EMISSÃO"].dt.date)["CTRC_EMITIDO"].sum().mean()
                        emissoes_semanais_total = df_user.groupby([df_user["DATA_EMISSÃO"].dt.isocalendar().year, df_user["DATA_EMISSÃO"].dt.isocalendar().week])["CTRC_EMITIDO"].sum().mean()
                        emissoes_mensais_total = df_user.groupby([df_user["DATA_EMISSÃO"].dt.year, df_user["DATA_EMISSÃO"].dt.month])["CTRC_EMITIDO"].sum().mean()

                        df_emissoes = pd.DataFrame({
                            "Categoria": ["Total Mensal", "Total Semanal", "Total Diário"],
                            "Valor": [emissoes_mensais_total, emissoes_semanais_total, emissoes_diarias_total]
                        })
                    else: # Média
                        df_emissoes = pd.DataFrame({
                            "Categoria": ["Média Mensal", "Média Semanal", "Média Diária"],
                            "Valor": [media_mensal_user, media_semanal_user, media_diaria_user]
                        })

                    st.markdown("##### 📈 Emissões")
                    fig_emissoes = px.bar(
                        df_emissoes,
                        x="Valor", y="Categoria",
                        orientation="h",
                        text="Valor",
                        color="Valor",
                        color_continuous_scale="Blues",
                        range_x=[0, df_emissoes["Valor"].max() * 1.1] # Ajusta o range do eixo X
                    )
                    fig_emissoes.update_traces(
                        texttemplate="%{text:.0f}",  # força número inteiro sem casas decimais
                        textposition="outside",
                        textfont_size=15   # <<< tamanho dos valores nas barras
                    )

                    fig_emissoes.update_layout(
                        height=350,
                        showlegend=False,
                        margin=dict(l=20, r=20, t=20, b=20),
                        yaxis=dict(
                            tickfont=dict(size=13, color="white"),   # rótulos laterais
                            title=dict(                             # título do eixo
                                text="Categoria",
                                font=dict(size=18, color="white")
                            )
                        )
                    )

                    st.plotly_chart(fig_emissoes, use_container_width=True)

                # --- Cancelamentos ---
                with col2:
                    tipo_agregacao_cancelamentos_user = st.radio(
                        "Visualizar Cancelamentos por:",
                        ("Total", "Média"),
                        key="agregacao_cancelamentos_user"
                    )

                    if tipo_agregacao_cancelamentos_user == "Total":
                        # Calcular totais diário, semanal e mensal para cancelamentos
                        cancelamentos_diarios_total = cancelamentos_user.groupby(cancelamentos_user["DATA_CANCELADO"].dt.date).size().mean()
                        cancelamentos_semanais_total = cancelamentos_user.groupby([cancelamentos_user["DATA_CANCELADO"].dt.isocalendar().year, cancelamentos_user["DATA_CANCELADO"].dt.isocalendar().week]).size().mean()
                        cancelamentos_mensais_total = cancelamentos_user.groupby([cancelamentos_user["DATA_CANCELADO"].dt.year, cancelamentos_user["DATA_CANCELADO"].dt.month]).size().mean()

                        df_cancelamentos = pd.DataFrame({
                            "Categoria": ["Total Mensal", "Total Semanal", "Total Diário"],
                            "Valor": [cancelamentos_mensais_total, cancelamentos_semanais_total, cancelamentos_diarios_total]
                        })
                    else: # Média
                        df_cancelamentos = pd.DataFrame({
                            "Categoria": ["Média Mensal", "Média Semanal", "Média Diária"],
                            "Valor": [media_mensal_canc_user, media_semanal_canc_user, media_diaria_canc_user]
                        })

                    st.markdown("##### ❌ Cancelamentos")
                    fig_cancel = px.bar(
                        df_cancelamentos,
                        x="Valor", y="Categoria",
                        orientation="h",
                        text="Valor",
                        color="Valor",
                        color_continuous_scale="Oranges",
                        range_x=[0, df_cancelamentos["Valor"].max() * 1.1] # Ajusta o range do eixo X
                    )
                    fig_cancel.update_traces(
                        texttemplate="%{text:.0f}",
                        textposition="outside",
                        textfont_size=15   # <<< aumenta os valores nas barras
                    )  

                    fig_cancel.update_layout(
                        height=350,
                        showlegend=False,
                        margin=dict(l=20, r=20, t=20, b=20),
                        yaxis=dict(
                            tickfont=dict(size=13, color="white"),   # <<< aumenta rótulos laterais (Total Diário, etc.)
                            title=dict(
                                text="Categoria",                    # <<< título do eixo
                                font=dict(size=18, color="white")    # <<< tamanho/cor do título
                            )
                        )
                    )

                    st.plotly_chart(fig_cancel, use_container_width=True)
                    
                st.markdown("---")

                st.subheader("❌ Motivos de Cancelamentos")

                # --- Análise de Cancelamentos com Top Motivos (Barra) ---

                # Criar DataFrame com os motivos de cancelamento
                canc_motivo = (
                    cancelamentos_user.groupby("MOTIVO")   # <<< ajuste o nome da coluna que tem o motivo
                    .size()
                    .reset_index(name="Quantidade")
                    .sort_values(by="Quantidade", ascending=False)
                )

                # Calcula % dos cancelamentos
                canc_motivo["Percentual"] = (canc_motivo["Quantidade"] / canc_motivo["Quantidade"].sum()) * 100

                # Seletor para escolher métrica
                metric_opcao = st.radio(
                    "Visualizar por:",
                    options=["Quantidade", "Percentual (%)"],
                    horizontal=True,
                    key="metric_cancelamentos"
                )

                # Seletor para escolher quantos motivos mostrar
                top_n = st.selectbox(
                    "Quantidade de motivos a exibir:",
                    options=[5, 10, 15, 20],
                    index=1,  # padrão = Top 10
                    key="top_cancelamentos"
                )

                # Escolhe coluna e formata os textos conforme a métrica selecionada
                if metric_opcao == "Quantidade":
                    coluna_x = "Quantidade"
                    canc_motivo["Texto"] = canc_motivo["Quantidade"].astype(str)  # só número
                else:
                    coluna_x = "Percentual"
                    canc_motivo["Texto"] = canc_motivo["Percentual"].map(lambda x: f"{x:.1f}%")  # só %



                st.subheader("❌ Top Motivos de Cancelamento")

                # Prepara os textos das barras de acordo com a métrica selecionada
                if metric_opcao == "Quantidade":
                    canc_motivo["Texto"] = canc_motivo["Quantidade"].astype(str)
                else:
                    canc_motivo["Texto"] = canc_motivo["Percentual"].map(lambda x: f"{x:.1f}%")


                fig_motivos_cancel = px.bar(
                    canc_motivo.head(top_n),   # ✅ agora usa a variável certa
                    x=coluna_x,
                    y="MOTIVO",
                    orientation="h",
                    text="Texto",
                    color=coluna_x,
                    color_continuous_scale="Reds"
                )

                fig_motivos_cancel.update_traces(
                    textposition="outside",
                    textfont_size=14
                )

                fig_motivos_cancel.update_layout(
                    height=600,
                    margin=dict(l=20, r=20, t=40, b=20),
                    xaxis_title=metric_opcao,
                    yaxis_title="Motivo",
                    yaxis=dict(categoryorder="total ascending")
                )

                st.plotly_chart(fig_motivos_cancel, use_container_width=True)


    with tab3:
        st.header("⚡ Produtividade")
        
        # Criar cópias dos dataframes filtrados globalmente para uso específico da aba
        df_tab3 = df_filtrado.copy()
        cancelamentos_tab3 = cancelamentos_filtrado.copy()
        
        # KPIs de Produtividade
        st.subheader("📊 Indicadores de Produtividade")
        
        # Calculando KPIs de produtividade
        total_emissoes_periodo = df_tab3["CTRC_EMITIDO"].sum()
        media_diaria_periodo = df_tab3.groupby("DATA_EMISSÃO")["CTRC_EMITIDO"].sum().mean()
        
        # Usuário mais produtivo
        usuario_produtivo = df_tab3.groupby("USUÁRIO")["CTRC_EMITIDO"].sum().reset_index()
        usuario_top = usuario_produtivo.loc[usuario_produtivo['CTRC_EMITIDO'].idxmax()]
        nome_usuario_top = usuario_top['USUÁRIO']
        emissoes_usuario_top = usuario_top['CTRC_EMITIDO']
        
        # Expedição mais produtiva
        expedicao_produtiva = df_tab3.groupby("EXPEDIÇÃO")["CTRC_EMITIDO"].sum().reset_index()
        expedicao_top = expedicao_produtiva.loc[expedicao_produtiva['CTRC_EMITIDO'].idxmax()]
        nome_expedicao_top = expedicao_top['EXPEDIÇÃO']
        emissoes_expedicao_top = expedicao_top['CTRC_EMITIDO']
        
        # Total de usuários ativos
        total_usuarios = df_tab3["USUÁRIO"].nunique()
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.markdown(f"""
            <div class="kpi-card kpi-blue">
                <div class="kpi-icon">📦</div>
                <div class="kpi-value">{format_number(total_emissoes_periodo)}</div>
                <div class="kpi-label">Total de Emissões<br>no período</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="kpi-card kpi-green">
                <div class="kpi-icon">📈</div>
                <div class="kpi-value">{format_number(media_diaria_periodo)}</div>
                <div class="kpi-label">Média Diária<br>de emissões</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="kpi-card kpi-teal">
                <div class="kpi-icon">👥</div>
                <div class="kpi-value">{format_number(media_semanal_produtividade)}</div>
                <div class="kpi-label">Média Semanal de Emissões</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div class="kpi-card kpi-purple">
                <div class="kpi-icon">🥇</div>
                <div class="kpi-value">{format_number(media_mensal_produtividade)}</div>
                <div class="kpi-label">Média Mensal<br>de Emissões</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col5:
            st.markdown(f"""
            <div class="kpi-card kpi-orange">
                <div class="kpi-icon">👤</div>
                <div class="kpi-value">{total_usuarios}</div>
                <div class="kpi-label">Usuários Ativos<br>no período</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")

        # Top Performers
        st.subheader("🏆 Top Performers")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"""
            <div class="kpi-card kpi-indigo">
                <div class="kpi-icon">🥇</div>
                <div class="kpi-value">{nome_usuario_top}</div>
                <div class="kpi-label">Usuário Mais Produtivo<br>({format_number(emissoes_usuario_top)} emissões)</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="kpi-card kpi-red">
                <div class="kpi-icon">🚛</div>
                <div class="kpi-value">{nome_expedicao_top}</div>
                <div class="kpi-label">Expedição Mais Produtiva<br>({format_number(emissoes_expedicao_top)} emissões)</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")

        st.subheader("👥 Análise Comparativa de Usuários")
        st.markdown("Selecione dois usuários para comparar a produtividade e o perfil de emissão.")

        usuarios_disponiveis_tab3 = sorted(df_tab3["USUÁRIO"].unique())

        if len(usuarios_disponiveis_tab3) < 2:
            st.info("É necessário ter pelo menos dois usuários com dados no período selecionado para fazer uma comparação.")
        else:
            col_select1, col_select2 = st.columns(2)
            with col_select1:
                if 'usuario_a' not in st.session_state or st.session_state.usuario_a not in usuarios_disponiveis_tab3:
                    st.session_state.usuario_a = usuarios_disponiveis_tab3[0]
                
                usuario_a = st.selectbox(
                    "Selecione o Usuário A:",
                    options=usuarios_disponiveis_tab3,
                    index=usuarios_disponiveis_tab3.index(st.session_state.usuario_a),
                    key="comp_user_a"
                )
                st.session_state.usuario_a = usuario_a

            with col_select2:
                opcoes_b = [u for u in usuarios_disponiveis_tab3 if u != usuario_a]
                if not opcoes_b:
                    st.warning("Não há outro usuário para comparar.")
                    usuario_b = None
                else:
                    if 'usuario_b' not in st.session_state or st.session_state.usuario_b not in opcoes_b:
                        st.session_state.usuario_b = opcoes_b[0]

                    usuario_b = st.selectbox(
                        "Selecione o Usuário B:",
                        options=opcoes_b,
                        index=opcoes_b.index(st.session_state.usuario_b),
                        key="comp_user_b"
                    )
                    st.session_state.usuario_b = usuario_b

            if usuario_a and usuario_b:
                # Filtrar dados
                dados_a = df_tab3[df_tab3["USUÁRIO"] == usuario_a]
                dados_b = df_tab3[df_tab3["USUÁRIO"] == usuario_b]

                total_a = dados_a["CTRC_EMITIDO"].sum()
                total_b = dados_b["CTRC_EMITIDO"].sum()

                media_diaria_a = dados_a.groupby(dados_a["DATA_EMISSÃO"].dt.date)["CTRC_EMITIDO"].sum().mean()
                media_diaria_b = dados_b.groupby(dados_b["DATA_EMISSÃO"].dt.date)["CTRC_EMITIDO"].sum().mean()

                # Calcular média mensal para os usuários A e B
                media_mensal_a = dados_a.groupby(dados_a["DATA_EMISSÃO"].dt.to_period("M"))["CTRC_EMITIDO"].sum().mean() if not dados_a.empty else 0
                media_mensal_b = dados_b.groupby(dados_b["DATA_EMISSÃO"].dt.to_period("M"))["CTRC_EMITIDO"].sum().mean() if not dados_b.empty else 0

                variacao_total = ((total_a - total_b) / total_b * 100) if total_b > 0 else 0
                variacao_media = ((media_diaria_a - media_diaria_b) / media_diaria_b * 100) if media_diaria_b > 0 else 0

                # Badges coloridas para setas
                def badge(valor):
                    if valor > 0:
                        return "<span style='background-color:limegreen; color:white; padding:2px 6px; border-radius:6px; font-weight:bold;'>▲</span>"
                    elif valor < 0:
                        return "<span style='background-color:red; color:white; padding:2px 6px; border-radius:6px; font-weight:bold;'>▼</span>"
                    else:
                        return "<span style='background-color:gray; color:white; padding:2px 6px; border-radius:6px; font-weight:bold;'>=</span>"

                # --- KPIs em cartões ---

                col1, col2 = st.columns(2)

                with col1:
                    st.markdown(f"""
                    <div class="kpi-card kpi-blue">
                        <div class="kpi-icon">👤</div>
                        <div class="kpi-value">{format_number(total_a)}</div>
                        <div class="kpi-label"><b>{usuario_a}<b><br>Total de Emissões</div>
                    </div>
                    """, unsafe_allow_html=True)

                    st.markdown(f"""
                    <div class="kpi-card kpi-green">
                        <div class="kpi-icon">📅</div>
                        <div class="kpi-value">{media_diaria_a:.0f}</div>
                        <div class="kpi-label"><b>{usuario_a}<b><br>Média Diária </div>
                    </div>
                    """, unsafe_allow_html=True)

                    st.markdown(f"""
                    <div class="kpi-card kpi-purple">
                        <div class="kpi-icon">🗓️</div>
                        <div class="kpi-value">{media_mensal_a:.0f}</div>
                        <div class="kpi-label"><b>{usuario_a}<b><br>Média Mensal</div>
                    </div>
                    """, unsafe_allow_html=True)

                    with col2:  # lado direito
                        st.markdown(f"""
                        <div class="kpi-card kpi-blue">
                            <div class="kpi-icon">👤</div>
                            <div class="kpi-value">{format_number(total_b)}</div>
                            <div class="kpi-label"><b>{usuario_b}<b><br>Total de Emissões</div>
                        </div>
                        """, unsafe_allow_html=True)

                        st.markdown(f"""
                        <div class="kpi-card kpi-green">
                            <div class="kpi-icon">📅</div>
                            <div class="kpi-value">{media_diaria_b:.0f}</div>
                            <div class="kpi-label"><b>{usuario_b}<b><br>Média Diária </div>
                        </div>
                        """, unsafe_allow_html=True)

                        st.markdown(f"""
                        <div class="kpi-card kpi-purple">
                            <div class="kpi-icon">🗓️</div>
                            <div class="kpi-value">{media_mensal_b:.0f}</div>
                            <div class="kpi-label"><b>{usuario_b}<b><br>Média Mensal </div>
                        </div>
                        """, unsafe_allow_html=True)

                # Remover a seção de variação e insights lado a lado, pois o novo layout não a comporta
                # As variações podem ser calculadas e exibidas de outra forma se necessário, mas não nos KPIs.
                

                # (Dentro da aba "Produtividade", após a seleção dos usuários A e B)

                st.markdown("### 💡 Insights da Comparação")

                # (Dentro da aba "Produtividade", antes da chamada das colunas dos insights)

                # --- Função de Card de Insight v4 (com cálculo de percentual) ---
                # --- Função de Card de Insight v4 (com cálculo de percentual) ---
                def insight_card_v4(titulo, valor_a, valor_b, usuario_a, usuario_b, icone_titulo, cor_borda):
                    """
                    Gera um card de insight que calcula a diferença percentual e destaca o usuário superior.
                    """
                    # Evita divisão por zero se ambos os valores forem zero
                    if valor_a == 0 and valor_b == 0:
                        diferenca_abs = 0
                        percentual = 0
                    # Caso especial: um valor é zero e o outro não
                    elif valor_b == 0:
                        diferenca_abs = valor_a
                        percentual = 100.0
                    elif valor_a == 0:
                        diferenca_abs = -valor_b
                        percentual = 100.0
                    else:
                        diferenca_abs = valor_a - valor_b
                        percentual = (abs(diferenca_abs) / min(valor_a, valor_b)) * 100

                    # Define o vencedor e o texto da performance
                    if diferenca_abs > 0:
                        vencedor = usuario_a
                        icone_performance = "🏆"
                        cor_performance = "#22c55e"  # Verde
                        texto_performance = f"{vencedor} foi <b>{percentual:.1f}%</b> superior"
                        texto_diferenca = f"{format_number(round(abs(diferenca_abs)))} emissões a mais"

                    elif diferenca_abs < 0:
                        vencedor = usuario_b
                        icone_performance = "🏆"
                        cor_performance = "#22c55e"
                        texto_performance = f"{vencedor} foi <b>{percentual:.1f}%</b> superior"
                        texto_diferenca = f"{format_number(round(abs(diferenca_abs)))} emissões a mais"

                    else:
                        icone_performance = "🤝"
                        cor_performance = "#9ca3af" # Cinza
                        texto_performance = "Desempenho Idêntico"
                        texto_diferenca = ""

                    # Formata os valores
                    valor_a_fmt = f"{valor_a:,.0f}".replace(",", ".")
                    valor_b_fmt = f"{valor_b:,.0f}".replace(",", ".")

                    # Renderização do card
                    st.markdown(f"""
                    <div style="border: 2px solid {cor_borda}; border-radius: 12px; padding: 16px; margin-bottom: 16px; text-align: center;">
                        <div style="font-size: 1.1rem; font-weight: bold; margin-bottom: 6px;">{icone_titulo} {titulo}</div>
                        <div style="font-size: 1.1rem; color:{cor_performance}; margin-bottom:4px;">
                            {icone_performance} {texto_performance}
                        </div>
                        {"<div style='font-size:1rem; color:#9ca3af;'>" + texto_diferenca + "</div>" if texto_diferenca else ""}
                        <hr style="border: none; border-top: 1px solid #374151; margin: 10px 0;">
                        <div style="font-size: 0.9rem; color: #d1d5db;">
                            {usuario_a.upper()}: <b>{valor_a_fmt}</b> | {usuario_b.upper()}: <b>{valor_b_fmt}</b>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                # (Dentro da aba "Produtividade", após a definição das colunas)

                col1, col2, col3 = st.columns(3)

                with col1:
                    insight_card_v4(
                        "Total de Emissões", total_a, total_b, usuario_a, usuario_b,
                        "📦", "#3b82f6"
                    )

                with col2:
                    insight_card_v4(
                        "Média Diária", media_diaria_a, media_diaria_b, usuario_a, usuario_b,
                        "📅", "#10b981"
                    )

                with col3:
                    insight_card_v4(
                        "Média Mensal", media_mensal_a, media_mensal_b, usuario_a, usuario_b,
                        "🗓️", "#8b5cf6"
                    )

                st.markdown("---")

        # Ranking de Usuários
        if usuario_selecionado == 'Todos':
            st.subheader("📊 Ranking de Usuários")
        if usuario_selecionado == 'Todos':
            ranking_usuarios = df_tab3.groupby("USUÁRIO")["CTRC_EMITIDO"].sum().sort_values(ascending=False).head(10).reset_index()
            ranking_usuarios.columns = ['Usuário', 'Total de Emissões']
            
            fig_ranking = px.bar(
                ranking_usuarios,
                x='Total de Emissões',
                y='Usuário',
                orientation='h',
                title="Top 10 Usuários por Emissões",
                color='Total de Emissões',
                color_continuous_scale='Blues',
                text='Total de Emissões'
            )
            fig_ranking.update_traces(texttemplate='%{text:,}', textposition='outside')
            fig_ranking.update_layout(height=500, showlegend=False)
            st.plotly_chart(fig_ranking, use_container_width=True)
        # Distribuição por Expedição
        if usuario_selecionado == 'Todos':
            st.subheader("🚛 Distribuição por Expedição")
        if usuario_selecionado == 'Todos':
            dist_expedicao = df_tab3.groupby("EXPEDIÇÃO")["CTRC_EMITIDO"].sum().reset_index()
            
            fig_exp = px.pie(
                dist_expedicao,
                values="CTRC_EMITIDO",
                names="EXPEDIÇÃO",
                title="Distribuição de Emissões por Expedição"
            )
            st.plotly_chart(fig_exp, use_container_width=True)
    with tab4:
        st.header("✖️ Cancelamentos")
        
        # Criar cópias dos dataframes filtrados globalmente para uso específico da aba
        df_tab4 = df_filtrado.copy()
        cancelamentos_tab4 = cancelamentos_filtrado.copy()
        
        # Calculando KPIs de Cancelamento
        if not cancelamentos_tab4.empty:
            total_cancelamentos_periodo = len(cancelamentos_tab4)
            
            # Média Diária de Cancelamentos
            cancelamentos_diarios = cancelamentos_tab4.groupby(cancelamentos_tab4["DATA_CANCELADO"].dt.date).size()
            media_diaria_cancelamentos = cancelamentos_diarios.mean()
            
            # Média Semanal de Cancelamentos
            cancelamentos_semanais = cancelamentos_filtrado.groupby(cancelamentos_filtrado["DATA_CANCELADO"].dt.to_period("W")).size()
            media_semanal_cancelamentos = cancelamentos_semanais.mean()
            
            # Média Mensal de Cancelamentos
            cancelamentos_mensais = cancelamentos_filtrado.groupby(cancelamentos_filtrado["DATA_CANCELADO"].dt.to_period("M")).size()
            media_mensal_cancelamentos = cancelamentos_mensais.mean()
            
            # Usuário com Mais Cancelamentos
            usuario_mais_cancelamentos = cancelamentos_filtrado["USUARIO"].value_counts().idxmax()
            qtd_usuario_mais_cancelamentos = cancelamentos_filtrado["USUARIO"].value_counts().max()
            
            # Motivo de Cancelamento Mais Comum
            motivo_mais_comum = cancelamentos_filtrado["MOTIVO"].value_counts().idxmax()
            qtd_motivo_mais_comum = cancelamentos_filtrado["MOTIVO"].value_counts().max()

        else:
            total_cancelamentos_periodo = 0
            media_diaria_cancelamentos = 0
            media_semanal_cancelamentos = 0
            media_mensal_cancelamentos = 0
            usuario_mais_cancelamentos = "N/A"
            qtd_usuario_mais_cancelamentos = 0
            motivo_mais_comum = "N/A"
            qtd_motivo_mais_comum = 0

        # KPIs de Cancelamento
        st.subheader("📊 Indicadores de Cancelamento")
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.markdown(f"""
            <div class="kpi-card kpi-red">
                <div class="kpi-icon">✖️</div>
                <div class="kpi-value">{format_number(total_cancelamentos_periodo)}</div>
                <div class="kpi-label">Total de Cancelamentos<br>no período</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="kpi-card kpi-orange">
                <div class="kpi-icon">📅</div>
                <div class="kpi-value">{format_number(media_diaria_cancelamentos)}</div>
                <div class="kpi-label">Média Diária<br>de Cancelamentos</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="kpi-card kpi-purple">
                <div class="kpi-icon">🗓️</div>
                <div class="kpi-value">{format_number(media_semanal_cancelamentos)}</div>
                <div class="kpi-label">Média Semanal<br>de Cancelamentos</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div class="kpi-card kpi-teal">
                <div class="kpi-icon">📊</div>
                <div class="kpi-value">{format_number(media_mensal_cancelamentos)}</div>
                <div class="kpi-label">Média Mensal<br>de Cancelamentos</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col5:
            st.markdown(f"""
            <div class="kpi-card kpi-indigo">
                <div class="kpi-icon">👤</div>
                <div class="kpi-value">{usuario_mais_cancelamentos}</div>
                <div class="kpi-label">Usuário com Mais Cancelamentos<br>({format_number(qtd_usuario_mais_cancelamentos)} cancelamentos)</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")

        # Gráfico de Evolução da Taxa de Cancelamento (Ano Atual)
        st.subheader("📈 Evolução da Taxa de Cancelamento vs Meta")
        
        # Filtrar dados para o ano atual
        ano_atual = datetime.now().year
        emissoes_ano_atual = df_tab4[df_tab4['DATA_EMISSÃO'].dt.year == ano_atual].copy()
        cancelamentos_ano_atual = cancelamentos_tab4[cancelamentos_tab4['DATA_CANCELADO'].dt.year == ano_atual].copy()
        
        if not emissoes_ano_atual.empty and not cancelamentos_ano_atual.empty:
            # Agrupar emissões por mês
            emissoes_mensais = emissoes_ano_atual.groupby(emissoes_ano_atual['DATA_EMISSÃO'].dt.to_period('M'))['CTRC_EMITIDO'].sum()
            
            # Agrupar cancelamentos por mês
            cancelamentos_mensais = cancelamentos_ano_atual.groupby(cancelamentos_ano_atual['DATA_CANCELADO'].dt.to_period('M')).size()
            
            # Criar DataFrame com todos os meses do ano
            meses_ano = pd.period_range(start=f'{ano_atual}-01', end=f'{ano_atual}-12', freq='M')
            df_evolucao = pd.DataFrame(index=meses_ano)
            
            # Adicionar dados de emissões e cancelamentos
            df_evolucao['Emissoes'] = emissoes_mensais.reindex(meses_ano, fill_value=0)

            # 👉 Força denominadores fixos (jan–ago) APENAS na visão geral
            if usuario_selecionado == "Todos" and expedicao_selecionada == "Todas":
                for nome_mes, valor in EMISSOES_FIXAS_MES.items():
                    pos = MESES_MAP[nome_mes] - 1
                    if 0 <= pos < len(df_evolucao):
                        df_evolucao.iloc[pos, df_evolucao.columns.get_loc('Emissoes')] = valor
                        
            df_evolucao['Cancelamentos'] = cancelamentos_mensais.reindex(meses_ano, fill_value=0)
            
            # Calcular taxa de cancelamento
            df_evolucao['Taxa_Cancelamento'] = (df_evolucao['Cancelamentos'] / df_evolucao['Emissoes'] * 100).fillna(0)
            
            # Converter índice para string para plotagem
            df_evolucao['Mes'] = df_evolucao.index.strftime('%b/%Y')
            df_evolucao = df_evolucao.reset_index(drop=True)
            
            # Criar gráfico de linha
            fig_evolucao_taxa = go.Figure()
            
            # Linha da taxa de cancelamento
            fig_evolucao_taxa.add_trace(go.Scatter(
                x=df_evolucao['Mes'],
                y=df_evolucao['Taxa_Cancelamento'],
                mode='lines+markers+text',  # <<< rótulos ativados
                name='Taxa de Cancelamento (%)',
                line=dict(color="#0145cd", width=3),
                marker=dict(size=8, color="#FFFFFF"),
                text=[f'{val:.2f}%' for val in df_evolucao['Taxa_Cancelamento']],
                textposition='top center',
                textfont=dict(size=16, color='white'), # Adiciona cor e tamanho para melhor visibilidade
                hovertemplate='<b>%{x}</b><br>Taxa: %{y:.2f}%<extra></extra>'
            ))
            
            # Linha de meta (0.75%)
            fig_evolucao_taxa.add_hline(
                y=0.75, 
                line_dash="dash", 
                line_color="orange",
                annotation_text="Meta: 0.75%",
                annotation_position="top right"
            )

            # Definir nomes completos em PT-BR
            meses_labels = [
                "JANEIRO", "FEVEREIRO", "MARÇO", "ABRIL", "MAIO", "JUNHO",
                "JULHO", "AGOSTO", "SETEMBRO", "OUTUBRO", "NOVEMBRO", "DEZEMBRO"
            ]

            # Forçar ticks do eixo X com nomes em maiúsculo📈 Evolução da Taxa de Cancelamento (Ano Atual)
            fig_evolucao_taxa.update_xaxes(
                tickvals=df_evolucao.index,     # posições (um por mês)
                ticktext=meses_labels,          # nomes que irão aparecer
                tickfont=dict(size=15, color="white", family="Calibri")  # aumenta tamanho, cor e fonte
            )

            fig_evolucao_taxa.update_layout(
                xaxis_title='',
                yaxis_title='Taxa de Cancelamento (%)',
                height=550,
                showlegend=False,
                margin=dict(t=20, b=40),  # topo menor, gráfico sobe
                hovermode='x unified',
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                xaxis=dict(
                    showgrid=True,
                    gridcolor='rgba(128,128,128,0.2)'
                ),
                yaxis=dict(
                    showgrid=True,
                    gridcolor='rgba(128,128,128,0.2)',
                    tickformat='.2f',
                    tickfont=dict(size=15, color='white')  # <<< aumenta tamanho e cor da legenda dos meses
                )
            )
            
            st.plotly_chart(fig_evolucao_taxa, use_container_width=True)
            
        
        else:
            st.info("Dados insuficientes para gerar o gráfico de evolução da taxa de cancelamento para o ano atual.")
        
        st.markdown("---")

        # KPI de Motivo Mais Comum
        st.subheader("💡 Motivo de Cancelamento Mais Comum")
        col1_motivo, col2_motivo, col3_motivo = st.columns([1, 2, 1])
        with col2_motivo:
            st.markdown(f"""
            <div class="kpi-card kpi-green">
                <div class="kpi-icon">🔍</div>
                <div class="kpi-value">{motivo_mais_comum}</div>
                <div class="kpi-label">Motivo Mais Comum<br>({format_number(qtd_motivo_mais_comum)} ocorrências)</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Cancelamentos por mês
        
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
        fig_canc_mes.update_traces(
            texttemplate='%{text}',
            textposition='outside',
            textfont_size=16
        )
        fig_canc_mes.update_layout(
            xaxis_tickangle=0,
            showlegend=False,
            margin=dict(t=60),
            yaxis=dict(range=[0, cancelamentos_mes['Cancelamentos'].max() * 1.15])
        )

        st.plotly_chart(fig_canc_mes, use_container_width=True)

        st.markdown("---")

        # Top motivos de cancelamento
        st.subheader("🔍 Top 10 Motivos de Cancelamento")
        top_motivos = cancelamentos_tab4["MOTIVO"].value_counts().head(10).reset_index()
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
        fig_motivos.update_traces(
            texttemplate='%{text}',
            textposition='outside',
            textfont_size=16   # <<< aumenta o tamanho dos rótulos numéricos

        )
        fig_motivos.update_layout(
            height=600, 
            showlegend=False,
            yaxis=dict(  # <--- CONFIGURAÇÃO DO EIXO Y
                categoryorder='total ascending',  # Adiciona a ordem decrescente
                tickfont=dict(
                    size=14,      # Ajusta o tamanho da fonte
                    color='white' # Opcional: Garante que a fonte seja branca
                )
            )
        )
        st.plotly_chart(fig_motivos, use_container_width=True)

        st.markdown("---")

        # Cancelamentos por Usuário
        if usuario_selecionado == "Todos" or cancelamentos_tab4["USUARIO"].nunique() > 1:
            st.subheader("👥 Cancelamentos por Usuário")
            canc_usuario = cancelamentos_tab4["USUARIO"].value_counts().sort_values(ascending=False).head(10).reset_index()
            canc_usuario.columns = ['USUARIO', 'Cancelamentos']
            
            fig_canc_usuario = px.bar(
                canc_usuario,
                x='Cancelamentos',
                y='USUARIO',
                orientation='h',
                title="Top 10 Usuários com Mais Cancelamentos",
                color='Cancelamentos',
                color_continuous_scale='Reds',
                text='Cancelamentos'
            )
            fig_canc_usuario.update_traces(
                texttemplate='%{text}',
                textposition='outside',
                textfont_size=16
            )

            # --- AJUSTE AQUI ---
            fig_canc_usuario.update_layout(
                height=500, 
                showlegend=False,
                yaxis=dict(  # <--- CONFIGURAÇÃO DO EIXO Y
                    categoryorder='total ascending',  # Adiciona a ordem decrescente
                    tickfont=dict(
                        size=14,      # Ajusta o tamanho da fonte
                        color='white' # Define a cor da fonte
                    )
                )
            )
            st.plotly_chart(fig_canc_usuario, use_container_width=True)


        else:
            st.subheader(f"✖️ Motivos de Cancelamento para {usuario_selecionado}")
            motivos_cancelamento_usuario = cancelamentos_tab4[cancelamentos_tab4["USUARIO"].str.strip() == usuario_selecionado.strip()]["MOTIVO"].value_counts().head(10).reset_index()
            motivos_cancelamento_usuario.columns = ['Motivo', 'Quantidade']

            if not motivos_cancelamento_usuario.empty:
                fig_motivos_pizza = px.pie(
                    motivos_cancelamento_usuario,
                    values='Quantidade',
                    names='Motivo',
                    title=f"Distribuição de Motivos de Cancelamento para {usuario_selecionado}"
                )
                fig_motivos_pizza.update_traces(textposition='inside', textinfo='percent+label')
                st.plotly_chart(fig_motivos_pizza, use_container_width=True)
            else:
                st.info(f"Nenhum cancelamento encontrado para o usuário {usuario_selecionado} no período selecionado.")

        st.markdown("---")

        col_expedicao, col_motivos_geral = st.columns(2)
        

        # SÓ MOSTRA OS GRÁFICOS DE EXPEDIÇÃO E MOTIVOS GERAIS SE NENHUM USUÁRIO ESPECÍFICO ESTIVER SELECIONADO
        if usuario_selecionado == "Todos":
            col_expedicao, col_motivos_geral = st.columns(2)
            
            with col_expedicao:
                st.subheader("🚛 Cancelamentos por Expedição")
                canc_expedicao = cancelamentos_tab4.groupby("EXPEDIÇÃO").size().reset_index(name="Cancelamentos")
                
                # Verifica se há dados para plotar
                if not canc_expedicao.empty:
                    fig_canc_exp = px.pie(
                        canc_expedicao,
                        values="Cancelamentos",
                        names="EXPEDIÇÃO",
                        title="Distribuição de Cancelamentos por Expedição"
                    )
                    st.plotly_chart(fig_canc_exp, use_container_width=True)
                else:
                    st.info("Não há dados de cancelamento por expedição para exibir.")

            with col_motivos_geral:
                st.subheader("🔍 Top 10 Motivos de Cancelamento (Geral)")
                top_motivos_geral = cancelamentos_tab4["MOTIVO"].value_counts().head(10).reset_index()
                top_motivos_geral.columns = ["Motivo", "Quantidade"]

                if not top_motivos_geral.empty:
                    fig_motivos_geral = px.pie(
                        top_motivos_geral,
                        values="Quantidade",
                        names="Motivo",
                        title="Top 10 Motivos de Cancelamento"
                    )
                    fig_motivos_geral.update_traces(textposition='inside', textinfo='percent+label')
                    st.plotly_chart(fig_motivos_geral, use_container_width=True)
                else:
                    st.info("Nenhum motivo de cancelamento encontrado para o período selecionado.")

    with tab5:
        st.header("📋 Dados Detalhados")

        # Criar cópias dos dataframes filtrados globalmente para uso específico da aba
        df_tab5 = df_filtrado.copy()
        cancelamentos_tab5 = cancelamentos_filtrado.copy()

        # Seletor do tipo de dados
        tipo_dados = st.selectbox("Selecione o tipo de dados:", ["Emissões", "Cancelamentos"], key="tipo_dados_tab5")

        # Escolhe o DataFrame com base no tipo
        if tipo_dados == "Emissões":
            df_exibicao = df_tab5.copy()
            col_data = "DATA_EMISSÃO"
            col_usuario = "USUÁRIO"
            col_exp = "EXPEDIÇÃO"
            col_valor = "CTRC_EMITIDO"
        else:
            df_exibicao = cancelamentos_tab5.copy()
            col_data = "DATA_CANCELADO"
            col_usuario = "USUARIO"
            col_exp = "EXPEDIÇÃO"
            col_valor = None

        if df_exibicao.empty:
            st.warning("Nenhum dado encontrado com os filtros aplicados.")

        else:

            # ====== FILTROS INTERNOS ======
            st.subheader("🔍 Filtros Avançados")
            col1, col2, col3 = st.columns(3)

            with col1:
                busca = st.text_input("Busca por texto (Usuário, Expedição ou Motivo):").strip().lower()
            with col2:
                filtro_usuario = st.selectbox(
                    "Filtrar por Usuário:",
                    ["Todos"] + sorted(df_exibicao[col_usuario].unique().tolist()), key="filtro_usuario_tab5"
                )
            with col3:
                filtro_exp = st.selectbox(
                    "Filtrar por Expedição:",
                    ["Todos"] + sorted(df_exibicao[col_exp].unique().tolist()), key="filtro_exp_tab5"
                )

            # Aplica filtros
            if busca:
                df_exibicao = df_exibicao[
                    df_exibicao.apply(lambda row: row.astype(str).str.lower().str.contains(busca).any(), axis=1)
                ]
            if filtro_usuario != "Todos":
                df_exibicao = df_exibicao[df_exibicao[col_usuario] == filtro_usuario]
            if filtro_exp != "Todos":
                df_exibicao = df_exibicao[df_exibicao[col_exp] == filtro_exp]

            # ====== INDICADORES ======
            st.markdown("### 📊 Indicadores Resumidos")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Registros", f"{len(df_exibicao):,}".replace(",", "."))
            if col_valor:
                with col2:
                    st.metric("Total Emissões", f"{df_exibicao[col_valor].sum():,}".replace(",", "."))
            with col3:
                st.metric(
                    "Período",
                    f"{df_exibicao[col_data].min().strftime('%d/%m/%Y')} - {df_exibicao[col_data].max().strftime('%d/%m/%Y')}"
                )
            with col4:
                st.metric("Usuários Únicos", df_exibicao[col_usuario].nunique())

            # ====== TABELA DE DADOS ======
            st.markdown("### 📋 Tabela de Dados")
            
            # Configurações de paginação
            registros_por_pagina = st.selectbox("Registros por página:", [10, 25, 50, 100], index=1)
            total_paginas = (len(df_exibicao) - 1) // registros_por_pagina + 1
            
            if total_paginas > 1:
                pagina_atual = st.number_input("Página:", min_value=1, max_value=total_paginas, value=1)
                inicio = (pagina_atual - 1) * registros_por_pagina
                fim = inicio + registros_por_pagina
                df_pagina = df_exibicao.iloc[inicio:fim]
                st.write(f"Mostrando registros {inicio + 1} a {min(fim, len(df_exibicao))} de {len(df_exibicao)}")
            else:
                df_pagina = df_exibicao
                st.write(f"Mostrando todos os {len(df_exibicao)} registros")

            # Exibir tabela
            st.dataframe(df_pagina, use_container_width=True)

            # ====== DOWNLOAD ======
            st.markdown("### 💾 Download dos Dados")
            csv = df_exibicao.to_csv(index=False)
            st.download_button(
                label="📥 Baixar dados filtrados (CSV)",
                data=csv,
                file_name=f"{tipo_dados.lower()}_filtrados_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )

if __name__ == "__main__":
    main()




























