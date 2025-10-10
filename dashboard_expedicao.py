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
import base64
import unicodedata
from streamlit_option_menu import option_menu
import os 

# ✅ NOVA FUNÇÃO PARA EMBUTIR A IMAGEM
def get_image_as_base64(path):
    """Lê um arquivo de imagem e o converte para o formato Base64."""
    if not os.path.exists(path):
        return None
    with open(path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode()

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
        padding: 1rem;
        background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 50%, #bae6fd 100%);
        border-radius: 16px;
        border: 1px solid #e0f2fe;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        position: relative;
        overflow: hidden;
    }
            
    /* Centralizar toda a área da tabela */
    [data-testid="stDataFrame"] {
        display: flex;
        justify-content: center;
    }

    /* Centralizar cabeçalhos */
    [data-testid="stDataFrame"] th div {
        justify-content: center !important;
        text-align: center !important;
    }

    /* Centralizar células */
    [data-testid="stDataFrame"] td div {
        justify-content: center !important;
        text-align: center !important;
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

    /* Estilo padrão para abas selecionadas (será sobrescrito pelas específicas) */
    .stTabs [aria-selected="true"] {
        color: white !important;
        font-weight: 800;
        font-size: 1.4rem !important;
        transform: scale(1.07);
    }

    /* Aba Visão Geral - Azul */
    .stTabs [data-baseweb="tab"][aria-selected="true"]:nth-child(1) {
        background: linear-gradient(135deg, #3B82F6, #1D4ED8) !important;
        box-shadow: 0 6px 18px rgba(59, 130, 246, 0.35) !important;
    }

    /* Aba Análise Temporal - Verde */
    .stTabs [data-baseweb="tab"][aria-selected="true"]:nth-child(2) {
        background: linear-gradient(135deg, #10b981, #059669) !important;
        box-shadow: 0 6px 18px rgba(16, 185, 129, 0.35) !important;
    }

    /* Aba Análise Individual - Roxo */
    .stTabs [data-baseweb="tab"][aria-selected="true"]:nth-child(3) {
        background: linear-gradient(135deg, #8b5cf6, #7c3aed) !important;
        box-shadow: 0 6px 18px rgba(139, 92, 246, 0.35) !important;
    }

    /* Aba Produtividade - Laranja */
    .stTabs [data-baseweb="tab"][aria-selected="true"]:nth-child(4) {
        background: linear-gradient(135deg, #f97316, #ea580c) !important;
        box-shadow: 0 6px 18px rgba(249, 115, 22, 0.35) !important;
    }

    /* Aba Cancelamentos - Vermelho */
    .stTabs [data-baseweb="tab"][aria-selected="true"]:nth-child(5) {
        background: linear-gradient(135deg, #ef4444, #dc2626) !important;
        box-shadow: 0 6px 18px rgba(239, 68, 68, 0.35) !important;
    }

     /* Aba Dados Detalhados - Azul Marinho */
    .stTabs [data-baseweb="tab"][aria-selected="true"]:nth-child(6) {
        background: linear-gradient(135deg, #1e3a8a, #0c2a66) !important; /* Tons de Azul Marinho */
        box-shadow: 0 6px 18px rgba(30, 58, 138, 0.4) !important;
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
            
/* Estilizar blocos da sidebar */
.sidebar-card {
    background: #1e293b;          /* Fundo igual ao restante do dashboard */
    padding: 15px;
    margin-bottom: 15px;
    border-radius: 12px;
    border: 1px solid #334155;
    box-shadow: 0 4px 10px rgba(0,0,0,0.3);
}
.sidebar-card h3 {
    font-size: 1rem;
    font-weight: 600;
    color: #f1f5f9;
    margin-bottom: 10px;
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
            
/* Força o bloco do radio (todo o container) a usar a largura da página */
div[data-testid="stHorizontalBlock"] {
    width: 100% !important;
    margin-left: 0 !important;
    margin-right: 0 !important;
    padding-left: 0 !important;
    padding-right: 0 !important;
}

/* Container interno */
div[data-testid="stHorizontalBlock"] div[data-baseweb="radio"] {
    width: 100% !important;
    display: flex !important;
}

/* Força o bloco do radio (todo o container) a usar a largura da página */
div[data-testid="stHorizontalBlock"] {
    width: 100% !important;
    margin-left: 0 !important;
    margin-right: 0 !important;
    padding-left: 0 !important;
    padding-right: 0 !important;
}

/* Container interno */
div[data-testid="stHorizontalBlock"] div[data-baseweb="radio"] {
    width: 100% !important;
    display: flex !important;
}

/* Cada botão ocupa metade da linha */
div[data-baseweb="radio"] > label {
    flex: 1 !important;
    text-align: center !important;
    margin: 0 6px !important;
}

/* Emissões (1ª opção) selecionada → azul */
div[data-testid="stHorizontalBlock"] div[data-baseweb="radio"] > label:nth-of-type(1)[aria-checked="true"] {
    background: linear-gradient(135deg, #3b82f6, #1d4ed8) !important;
    box-shadow: 0 6px 18px rgba(59, 130, 246, 0.35) !important;
    color: white !important;
    border: none !important;
}

/* Cancelamentos (2ª opção) selecionada → vermelho */
div[data-testid="stHorizontalBlock"] div[data-baseweb="radio"] > label:nth-of-type(2)[aria-checked="true"] {
    background: linear-gradient(135deg, #ef4444, #dc2626) !important;
    box-shadow: 0 6px 18px rgba(239, 68, 68, 0.35) !important;
    color: white !important;
    border: none !important;
}

/* Força o texto interno também a ficar branco */
div[data-testid="stHorizontalBlock"] div[data-baseweb="radio"] > label[aria-checked="true"] span {
    color: white !important;
}




            
# ==============================
# 🎨 CSS para Sidebar e Filtros
# ==============================
            
<style>
/* Estilizar a sidebar */
section[data-testid="stSidebar"] {
background-color: #1e293b !important;
padding: 10px;
}

/* Card dos filtros */
.sidebar-card {
background: #1e293b;
padding: 15px;
margin-bottom: 15px;
border-radius: 12px;
border: 1px solid #334155;
box-shadow: 0 4px 10px rgba(0,0,0,0.3);
}
.sidebar-card h3 {
font-size: 1rem;
font-weight: 600;
margin-bottom: 10px;
}
/* Ícones coloridos nos títulos */
.sidebar-card:nth-of-type(1) h3 { color: #3b82f6; } /* Azul */
.sidebar-card:nth-of-type(2) h3 { color: #8b5cf6; } /* Roxo */
.sidebar-card:nth-of-type(3) h3 { color: #10b981; } /* Verde */
.sidebar-card:nth-of-type(4) h3 { color: #f97316; } /* Laranja */


/* Inputs da sidebar */
section[data-testid="stSidebar"] .stSelectbox,
section[data-testid="stSidebar"] .stDateInput,
section[data-testid="stSidebar"] .stRadio {
background: #0f172a !important;
border-radius: 8px !important;
padding: 6px 8px !important;
}
</style>

<style>
    /* ... (seu CSS existente) ... */

    /* NOVA CLASSE PARA O LOGO NA SIDEBAR - VERSÃO ATUALIZADA */
.logo-sidebar {
    display: flex;          /* ✅ Habilita o alinhamento flexível */
    justify-content: center;/* ✅ Centraliza o conteúdo (a imagem) horizontalmente */
    margin-top: -20px;      /* Puxa a imagem para cima. Ajuste o valor se necessário. */
    margin-bottom: -20px;   /* Reduz o espaço abaixo do logo. Ajuste se precisar. */
}

    /* ... (resto do seu CSS) ... */
</style>     
            
""", unsafe_allow_html=True)

def normalizar_usuario(nome):
    if pd.isna(nome):
        return None
    # Remove acentos e transforma em maiúsculo
    return ''.join(
        c for c in unicodedata.normalize('NFKD', str(nome))
        if not unicodedata.combining(c)
    ).strip().upper()

@st.cache_data
def load_data():
    """Carrega e processa os dados dos arquivos Excel"""
    try:
        # 🔹 Descobrir a pasta onde está o app.py
        base_dir = os.path.dirname(os.path.abspath(__file__))

        # Carregando dados de emissões
        emissoes_path = os.path.join(base_dir, "EMISSOES_KM.xlsx")
        emissoes_df = pd.read_excel(emissoes_path)
        emissoes_df['DATA_EMISSÃO'] = pd.to_datetime(emissoes_df['DATA_EMISSÃO'])

        # ✅ Normalizar usuários
        emissoes_df["USUÁRIO"] = emissoes_df["USUÁRIO"].map(normalizar_usuario)

        # Garantir meses em português
        meses_pt = [
            "JANEIRO","FEVEREIRO","MARÇO","ABRIL","MAIO","JUNHO",
            "JULHO","AGOSTO","SETEMBRO","OUTUBRO","NOVEMBRO","DEZEMBRO"
        ]
        emissoes_df['MÊS'] = emissoes_df['DATA_EMISSÃO'].dt.month.apply(lambda x: meses_pt[x-1])

        # Carregando dados de cancelamentos
        cancelamentos_path = os.path.join(base_dir, "CANCELAMENTOS_KM.xlsx")
        cancelamentos_df = pd.read_excel(cancelamentos_path)
        cancelamentos_df["DATA_CANCELADO"] = pd.to_datetime(cancelamentos_df["DATA_CANCELADO"])
        cancelamentos_df["MÊS"] = cancelamentos_df["DATA_CANCELADO"].dt.month.apply(lambda x: meses_pt[x-1])

        # ✅ Normalizar usuários também nos cancelamentos
        cancelamentos_df["USUARIO"] = cancelamentos_df["USUARIO"].map(normalizar_usuario)

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
        "SETEMBRO": 43683,
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
    # Português - minúsculo
    "jan": "Jan", "fev": "Fev", "mar": "Mar",
    "abr": "Abr", "mai": "Mai", "jun": "Jun",
    "jul": "Jul", "ago": "Ago", "set": "Set",
    "out": "Out", "nov": "Nov", "dez": "Dez",

    # Português - maiúsculo (segurança extra)
    "JAN": "Jan", "FEV": "Fev", "MAR": "Mar",
    "ABR": "Abr", "MAI": "Mai", "JUN": "Jun",
    "JUL": "Jul", "AGO": "Ago", "SET": "Set",
    "OUT": "Out", "NOV": "Nov", "DEZ": "Dez",

    # Inglês
    "jan": "Jan", "feb": "Fev", "mar": "Mar",
    "apr": "Abr", "may": "Mai", "jun": "Jun",
    "jul": "Jul", "aug": "Ago", "sep": "Set",
    "oct": "Out", "nov": "Nov", "dec": "Dez",

    # Inglês - maiúsculo (segurança extra)
    "JAN": "Jan", "FEB": "Fev", "MAR": "Mar",
    "APR": "Abr", "MAY": "Mai", "JUN": "Jun",
    "JUL": "Jul", "AUG": "Ago", "SEP": "Set",
    "OCT": "Out", "NOV": "Nov", "DEC": "Dez"
}

    # PARA:
    # ==============================
    # 🖼️ Logo na Sidebar (com Base64 para garantir a exibição)
    # ==============================
    
    # 1. Define o caminho para o arquivo do logo
    #    (Assumindo que 'logo_km.png' está na mesma pasta que o seu script .py)
    logo_path = "logo_km.png" 
    
    
    # 2. Converte a imagem para Base64
    logo_base64 = get_image_as_base64(logo_path)

    # 3. Renderiza o logo apenas se a conversão funcionou
    if logo_base64:
        st.sidebar.markdown(
            f"""
            <div class="logo-sidebar">
                <img src="data:image/png;base64,{logo_base64}" width="180px"> 
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        st.sidebar.warning("Logo não encontrado. Verifique o caminho do arquivo.")

    # Adiciona o divisor
    st.sidebar.markdown("---")

    # ==============================
    # ==============================
    # 📅 Período de Emissão (sempre aberto)
    # ==============================
    with st.sidebar.expander("🗓️ Período de Emissão", expanded=True):
        today = datetime.now().date()
        
        # --- ALTERAÇÃO AQUI ---
        # Define a data de início padrão como 1º de janeiro de 2024.
        default_start_date = date(2024, 1, 1)
        # A data final padrão continua sendo a data atual.
        default_end_date = today
        # --- FIM DA ALTERAÇÃO ---

        date_range_calendar = st.date_input(
            "Selecione o intervalo de datas:",
            value=(default_start_date, default_end_date),
            max_value=today,
            format="DD/MM/YYYY"
        )

        if len(date_range_calendar) == 2:
            start_date, end_date = date_range_calendar
        else:
            # Garante que os padrões sejam usados se algo der errado.
            start_date, end_date = default_start_date, default_end_date

    # ==============================
    # 📅 Filtro de Ano (ORDEM CORRIGIDA)
    # ==============================
    with st.sidebar.expander("📅 Filtro por Ano", expanded=True):
        # Garante que a lista de anos não quebre se o dataframe estiver vazio
        if not emissoes_df.empty:
            # --- ALTERAÇÃO AQUI ---
            # Ordena os anos em ordem CRESCENTE (removendo reverse=True)
            anos_disponiveis = sorted(emissoes_df['DATA_EMISSÃO'].dt.year.unique())
            # --- FIM DA ALTERAÇÃO ---
        else:
            anos_disponiveis = [datetime.now().year] # Usa o ano atual como fallback

        # Define as opções do selectbox, com "Todos" no início
        opcoes_ano = ["Todos"] + anos_disponiveis
        
        # O padrão será o ano mais recente, que agora é o último item da lista
        # Para encontrar o índice do ano mais recente, usamos len(opcoes_ano) - 1
        indice_padrao = len(opcoes_ano) - 1

        ano_selecionado = st.selectbox(
            "Selecione o ano para análise:",
            options=opcoes_ano,
            index=indice_padrao, # Começa com o ano mais recente selecionado
            key="filtro_ano_principal"
        )


    # --- Lógica para definir as datas com base no ano selecionado ---
    today = datetime.now().date()
    if ano_selecionado == "Todos":
        # Se "Todos" for selecionado, pega a primeira data de 2024 até a data atual
        start_date = date(2024, 1, 1)
        end_date = today
    else:
        # Se um ano específico for selecionado, define o intervalo para aquele ano
        start_date = date(ano_selecionado, 1, 1)
        # Se o ano selecionado for o ano atual, a data final é hoje. Senão, é 31/12 do ano selecionado.
        if ano_selecionado == today.year:
            end_date = today
        else:
            end_date = date(ano_selecionado, 12, 31)

    # ==============================
    # 🗓️ Período de Emissão (Calendário para ajuste fino)
    # ==============================
    with st.sidebar.expander("🗓️ Ajuste Fino do Período", expanded=False): # Começa fechado
        # O valor do calendário agora é definido pela seleção do filtro de ano
        date_range_calendar = st.date_input(
            "Ajuste o intervalo de datas, se necessário:",
            value=(start_date, end_date),
            max_value=today,
            format="DD/MM/YYYY"
        )

        # Atualiza as datas se o usuário modificar o calendário
        if len(date_range_calendar) == 2:
            start_date, end_date = date_range_calendar
        else:
            # Mantém as datas definidas pelo filtro de ano se o calendário falhar
            pass # As datas já foram definidas acima


    # ==============================
    # 📆 Mês (expander)
    # ==============================
    with st.sidebar.expander("📆 Mês", expanded=True):
        meses_ordem = ['JANEIRO', 'FEVEREIRO', 'MARÇO', 'ABRIL', 'MAIO', 'JUNHO',
                    'JULHO', 'AGOSTO', 'SETEMBRO', 'OUTUBRO', 'NOVEMBRO', 'DEZEMBRO']
        meses_disponiveis = [mes for mes in meses_ordem if mes in emissoes_df['MÊS'].unique()]

        mes_selecionado = st.selectbox(
            "Selecione o mês:",
            options=['Todos'] + meses_disponiveis,
            index=0
        )


    # ==============================
    # 🚛 Expedição (expander)
    # ==============================
    with st.sidebar.expander("🚛 Expedição", expanded=True):
        expedicoes_disponiveis = sorted(emissoes_df['EXPEDIÇÃO'].unique())
        expedicao_selecionada = st.selectbox(
            "Selecione a expedição:",
            options=['Todas'] + expedicoes_disponiveis,
            index=0
        )


    # ==============================
    # 👥 Usuários (expander)
    # ==============================
    with st.sidebar.expander("👥 Usuários", expanded=True):
        usuarios_emissoes = set(emissoes_df["USUÁRIO"].str.strip().unique())
        usuarios_cancelamentos = set(cancelamentos_df["USUARIO"].str.strip().unique())
        usuarios_disponiveis = sorted(list(usuarios_emissoes.union(usuarios_cancelamentos)))
        if 'Usuario Automatico' in usuarios_disponiveis:
            usuarios_disponiveis.remove('Usuario Automatico')

        opcoes_usuario = ["Todos"] + usuarios_disponiveis

        if "usuario_selecionado" not in st.session_state:
            st.session_state.usuario_selecionado = "Nenhum"

        if st.session_state.usuario_selecionado not in opcoes_usuario:
            st.session_state.usuario_selecionado = "Nenhum"

        try:
            default_index = opcoes_usuario.index(st.session_state.usuario_selecionado)
        except ValueError:
            default_index = 0

        usuario_selecionado = st.selectbox(
            "Selecione o usuário:",
            options=opcoes_usuario,
            index=default_index,
            key="filtro_usuario_principal"
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
            
            # --- LÓGICA CONDICIONAL PARA O CÁLCULO DA MÉDIA DIÁRIA (VERSÃO 3.0 - REGRA FINAL) ---
            
            # Se a expedição "NOITE" estiver selecionada, aplicamos a regra especial
            if expedicao_selecionada == 'NOITE':
                # 1. Filtra o dataframe para incluir APENAS dias de segunda a sexta (weekday < 5)
                df_exp_noite_dias_uteis = df_produtividade[df_produtividade['DATA_EMISSÃO'].dt.weekday < 5]
                
                # 2. Calcula o total de emissões SOMENTE desses dias
                total_emissoes_periodo = df_exp_noite_dias_uteis['CTRC_EMITIDO'].sum()
                
                # 3. Conta quantos dias ÚNICOS de seg-sex tiveram atividade
                dias_divisor = df_exp_noite_dias_uteis['DATA_EMISSÃO'].nunique()

            # Para qualquer outra seleção ("Todas", "Dia", etc.), usamos a lógica original
            else:
                total_emissoes_periodo = df_produtividade["CTRC_EMITIDO"].sum()
                dias_divisor = df_produtividade['DATA_EMISSÃO'].nunique()

            # --- FIM DA LÓGICA CONDICIONAL ---

            # Cálculo final da média diária
            if dias_divisor > 0:
                media_diaria_produtividade = total_emissoes_periodo / dias_divisor
            else:
                media_diaria_produtividade = 0
            
            # Média semanal (agrupar por semana) - Lógica original mantida
            # Para consistência, podemos também filtrar os sábados/domingos aqui se a Exp. Noite for selecionada
            df_semanal = df_produtividade[df_produtividade['DATA_EMISSÃO'].dt.weekday < 5] if expedicao_selecionada == 'NOITE' else df_produtividade
            df_semanal['semana'] = df_semanal['DATA_EMISSÃO'].dt.isocalendar().week
            df_semanal['ano'] = df_semanal['DATA_EMISSÃO'].dt.year
            emissoes_semanais = df_semanal.groupby(['ano', 'semana'])['CTRC_EMITIDO'].sum()
            media_semanal_produtividade = emissoes_semanais.mean()
            
            # Média mensal - Lógica original mantida
            df_mensal = df_produtividade[df_produtividade['DATA_EMISSÃO'].dt.weekday < 5] if expedicao_selecionada == 'NOITE' else df_produtividade
            if mes_selecionado != 'Todos':
                media_mensal_produtividade = df_mensal[df_mensal["MÊS"] == mes_selecionado]["CTRC_EMITIDO"].sum()
            else:
                emissoes_mensais = df_mensal.groupby(df_mensal['DATA_EMISSÃO'].dt.to_period('M'))['CTRC_EMITIDO'].sum()
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
                        col_title1, col_title2 = st.columns([1, 2])
                        with col_title1:
                            st.markdown(
                                "<h3 style='text-align:center; font-size:24px;'>🎯 Monitoramento da Meta de Cancelamento</h3>",
                                unsafe_allow_html=True
                            )

                        ano_atual = datetime.now().year
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
                            st.plotly_chart(gauge_fig, use_container_width=True)

                            # Definir nome do mês ou período
                            mes_texto = mes_selecionado if mes_selecionado != "Todos" else "Ano Atual"
                            st.markdown(f"""
                                <div style="text-align:center; margin-top:10px;">
                                    <span style="color:#FFFFFF; font-size:24px; font-weight:bold;">📆 {mes_texto}</span>
                                </div>
                            """, unsafe_allow_html=True)

                            # Aviso Dinâmico abaixo do velocímetro
                            if taxa_cancelamento <= meta_taxa:
                                st.markdown(
                                    """
                                    <div style="text-align:center; margin-top:10px;">
                                        <span style="color:#10b981; font-size:20px;"><b>✅ Status: DENTRO DA META<b></span>
                                    </div>
                                    """,
                                    unsafe_allow_html=True
                                )
                            else:
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
                                        pos = MESES_MAP[nome_mes] - 1
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
                                    annotation=dict(font_size=14, font_color="orange")
                                )

                                fig_evolucao_taxa.update_layout(
                                    xaxis_title='',
                                    yaxis_title='Taxa de Cancelamento (%)',
                                    height=550,
                                    showlegend=False,
                                    hovermode='x unified',
                                    plot_bgcolor='rgba(0,0,0,0)',
                                    paper_bgcolor='rgba(0,0,0,0)',
                                    margin=dict(l=40, r=40, t=50, b=0),
                                    xaxis=dict(
                                        showgrid=True,
                                        gridcolor='rgba(128,128,128,0.2)',
                                        tickformat="%b/%y",
                                        tickfont=dict(size=15, color='white')
                                    ),
                                    yaxis=dict(
                                        showgrid=True,
                                        gridcolor='rgba(128,128,128,0.2)',
                                        tickformat='.2f',
                                        range=[0, df_evolucao['Taxa_Cancelamento'].max() * 1.1]
                                    )
                                )

                                st.plotly_chart(fig_evolucao_taxa, use_container_width=True)

        # Seção de gráficos principais
        st.markdown("<br>", unsafe_allow_html=True)
        
        # ===============================
        # 📊 Exibição dos Dados - Emissões e Cancelamentos
        # ===============================
        st.markdown("<h3 style='text-align: center;'>📊 Exibição dos Dados - Emissões e Cancelamentos</h3>", unsafe_allow_html=True)


        # --- Lógica para Centralização ---
        # 1. Criamos 3 colunas. As colunas das pontas (col_vazia1, col_vazia2) servirão como espaçamento.
        # 2. A coluna do meio (col_central) conterá o nosso seletor.
        # 3. O 'width' define a proporção. [1, 2, 1] significa que a coluna central terá o dobro da largura das laterais,
        #    empurrando o conteúdo para o centro da tela.
        col_vazia1, col_central, col_vazia2 = st.columns([1, 2, 1])

        with col_central:
            # Seletor com estilo moderno, agora dentro da coluna central
            tipo_agregacao = option_menu(
                menu_title=None,
                options=["Totais", "Médias"],
                icons=['bar-chart-fill', 'graph-up'],
                menu_icon="cast",
                default_index=0,
                orientation="horizontal",
                styles={
                    # Container principal que envolve os botões
                    "container": {
                        "padding": "5px !important",
                        "background-color": "#0f172a",
                        "border-radius": "12px",
                        "border": "1px solid #334155"
                    },
                    # Ícone de cada botão
                    "icon": {
                        "color": "#f1f5f9",
                        "font-size": "18px",
                        "vertical-align": "middle",
                    },
                    # Estilo de cada botão (link de navegação)
                    "nav-link": {
                        "font-size": "16px",
                        "text-align": "center",
                        "margin": "0px",
                        "padding": "10px 0px",
                        "border-radius": "10px",
                        "flex-grow": "1",
                        "color": "#9CA3AF",
                        "--hover-color": "#334155",
                    },
                    # Estilo do botão QUANDO ESTÁ SELECIONADO
                    "nav-link-selected": {
                        "background": "linear-gradient(135deg, #1e40af, #3b82f6)",
                        "color": "white",
                        "box-shadow": "inset 0 1px 2px rgba(0,0,0,0.2)",
                    },
                }
            )

        # O resto do seu código para os gráficos continua normalmente fora das colunas
        col1_chart, col2_chart = st.columns(2)

        with col1_chart:
            # Título foi removido conforme solicitado anteriormente
            # st.markdown(f"<h3 style='text-align: center;'>📈 Emissões ({tipo_agregacao})</h3>", unsafe_allow_html=True)
            
            # --- INÍCIO DA LÓGICA ATUALIZADA ---
            
            # Aplicar agregação baseada na seleção do usuário
            if tipo_agregacao == "Totais":
                emissoes_mes = df_filtrado.groupby('MÊS')['CTRC_EMITIDO'].sum().reset_index()
                # Renomeia a coluna para uma chave genérica ('Valor') para facilitar o plot
                emissoes_mes.rename(columns={'CTRC_EMITIDO': 'Valor'}, inplace=True)
                y_axis_title = 'Total de Emissões'

            else:  # Lógica avançada para 'Médias'
                y_axis_title = 'Média de Emissões'
                
                # 1. Cria uma cópia do dataframe já filtrado pelos seletores da sidebar
                df_para_media = df_filtrado.copy()
                
                # 2. Adiciona uma coluna com o dia da semana numérico (0=Segunda, 6=Domingo)
                df_para_media['DIA_SEMANA_NUM'] = df_para_media['DATA_EMISSÃO'].dt.weekday

                # 3. Aplica as regras de filtro de dias da semana com base na expedição selecionada
                if expedicao_selecionada == 'NOITE':
                    # Para 'NOITE', considera apenas dias de Segunda a Sexta (dias < 5)
                    df_para_media = df_para_media[df_para_media['DIA_SEMANA_NUM'] < 5]
                elif expedicao_selecionada == 'DIA':
                    # Para 'DIA', considera apenas dias de Segunda a Sábado (dias < 6)
                    df_para_media = df_para_media[df_para_media['DIA_SEMANA_NUM'] < 6]
                # Se for 'Todas' ou outra expedição, nenhum filtro de dia da semana é aplicado.

                # 4. Calcula o total de emissões por mês (usando o dataframe já filtrado por dia da semana, se aplicável)
                soma_mensal = df_para_media.groupby('MÊS')['CTRC_EMITIDO'].sum()

                # 5. Conta o número de DIAS ÚNICOS que tiveram emissão em cada mês
                dias_unicos_com_emissao = df_para_media.groupby('MÊS')['DATA_EMISSÃO'].nunique()

                # 6. Calcula a média correta: Total de Emissões / Dias Únicos com Emissão
                # O .reset_index() transforma a Series resultante de volta em um DataFrame
                media_correta = (soma_mensal / dias_unicos_com_emissao).reset_index(name='Valor')
                
                # O DataFrame final para o gráfico é o que contém as médias corretas
                emissoes_mes = media_correta

            # --- FIM DA LÓGICA ATUALIZADA ---

            # Ordenar meses cronologicamente (código comum para Totais e Médias)
            if not emissoes_mes.empty:
                meses_ordem = ['JANEIRO', 'FEVEREIRO', 'MARÇO', 'ABRIL', 'MAIO', 'JUNHO', 
                            'JULHO', 'AGOSTO', 'SETEMBRO', 'OUTUBRO', 'NOVEMBRO', 'DEZEMBRO']
                emissoes_mes["ordem"] = emissoes_mes["MÊS"].map({mes: i for i, mes in enumerate(meses_ordem)})
                emissoes_mes = emissoes_mes.sort_values("ordem")

                # Cria o gráfico de barras usando a coluna genérica 'Valor'
                fig_emissoes_mes = px.bar(
                    emissoes_mes,
                    x="MÊS",
                    y="Valor",
                    title="",
                    color="Valor",
                    color_continuous_scale='Blues',
                    text='Valor'
                )
                
                # Formatação do texto (padrão brasileiro com ponto como separador de milhar)
                fig_emissoes_mes.update_traces(
                    text=[f"{int(v):,}".replace(",", ".") for v in emissoes_mes["Valor"]],
                    textposition='outside',
                    textfont_size=15
                )
                    
                fig_emissoes_mes.update_layout(
                    xaxis_tickangle=0,
                    showlegend=False,
                    margin=dict(t=50, b=50, l=70, r=20),
                    yaxis=dict(
                        range=[0, emissoes_mes["Valor"].max() * 1.3],
                        title_text=y_axis_title, # Título do eixo Y dinâmico
                        tickformat=",.0f"  # ✅ <--- A linha foi adicionada aqui
                    ),
                    coloraxis_colorbar=dict(
                        tickformat=",.0f" 
                    ),
                    height=550
                )

                st.plotly_chart(fig_emissoes_mes, use_container_width=True)
            else:
                st.info("Nenhum dado de emissão para exibir com os filtros aplicados.")


        with col2_chart:
            # Título foi removido conforme solicitado anteriormente
            # st.markdown(f"<h3 style='text-align: center;'>✖️ Cancelamentos ({tipo_agregacao})</h3>", unsafe_allow_html=True)
            
            # Aplicar agregação baseada na seleção
            if tipo_agregacao == "Totais":
                cancelamentos_mes = cancelamentos_filtrado.groupby('MÊS').size().reset_index(name='Cancelamentos')
                y_axis_title_canc = 'Total de Cancelamentos'
            else:  # Médias
                # Para médias de cancelamentos, calcular média diária por mês
                cancelamentos_por_dia = cancelamentos_filtrado.groupby(['MÊS', cancelamentos_filtrado['DATA_CANCELADO'].dt.date]).size().reset_index(name='Cancelamentos_Dia')
                cancelamentos_mes = cancelamentos_por_dia.groupby('MÊS')['Cancelamentos_Dia'].mean().reset_index()
                cancelamentos_mes.rename(columns={'Cancelamentos_Dia': 'Cancelamentos'}, inplace=True)
                y_axis_title_canc = 'Média de Cancelamentos'
            
            # Ordenar meses cronologicamente
            if not cancelamentos_mes.empty:
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
                    # ✅ 1. Escala de cores aprimorada para maior contraste
                    color_continuous_scale=px.colors.sequential.OrRd, 
                    text="Cancelamentos"
                )
                
                # ✅ 2. Formatação do texto para usar ponto como separador de milhar
                fig_canc_mes.update_traces(
                    text=[f"{int(v):,}".replace(",", ".") for v in cancelamentos_mes["Cancelamentos"]],
                    textposition='outside',
                    textfont_size=15
                )
                    
                # ✅ 3. Layout atualizado com formatação do eixo Y
                fig_canc_mes.update_layout(
                    xaxis_tickangle=0,
                    showlegend=False,
                    margin=dict(t=50, b=50, l=70, r=20),
                    yaxis=dict(
                        range=[0, cancelamentos_mes["Cancelamentos"].max() * 1.2],
                        title_text=y_axis_title_canc, # Título do eixo Y dinâmico
                        tickformat=",.0f"  # Garante que o eixo Y mostre números inteiros
                    ),
                    # Remove a barra de cores para um visual mais limpo, como na imagem
                    coloraxis_showscale=False, 
                    height=550
                )

                st.plotly_chart(fig_canc_mes, use_container_width=True)

            else:
                st.info("Nenhum dado de cancelamento para exibir com os filtros aplicados.")

    
    with tab2:

        # Criar cópias dos dataframes filtrados globalmente para uso específico da aba
        df_tab2 = df_filtrado.copy()
        cancelamentos_tab2 = cancelamentos_filtrado.copy()

        if df_tab2.empty:
            st.warning("Nenhum dado disponível para o período selecionado.")
        else:

           # ==================================================================
            #  NOVA SEÇÃO UNIFICADA: DADOS DETALHADOS (EMISSÕES E CANCELAMENTOS)
            # ==================================================================

            # 1. SELETOR PRINCIPAL PARA ESCOLHER ENTRE EMISSÕES E CANCELAMENTOS
            #    (Estilo atualizado para corresponder à imagem)
            tipo_dado_detalhado = option_menu(
                menu_title=None,
                options=["Emissões", "Cancelamentos"],
                icons=['box-arrow-up-right', 'box-seam-fill'],  # Ícones preenchidos para mais destaque
                menu_icon="table",
                default_index=0,
                orientation="horizontal",
                styles={
                    # Container principal que envolve os botões
                    "container": {
                        "padding": "5px !important",
                        "background-color": "#0f172a", # Fundo escuro do container
                        "border-radius": "12px",
                        "border": "1px solid #334155"
                    },
                    # Ícone de cada botão
                    "icon": {
                        "color": "#f1f5f9",
                        "font-size": "18px",
                        "vertical-align": "middle",
                    },
                    # Estilo de cada botão (link de navegação)
                    "nav-link": {
                        "font-size": "16px",
                        "text-align": "center",
                        "margin": "0px",
                        "padding": "10px 0px",
                        "border-radius": "10px",
                        "flex-grow": "1", # Faz os botões ocuparem o espaço
                        "color": "#9CA3AF", # Cor cinza para o texto não selecionado
                        "--hover-color": "#334155",
                    },
                    # Estilo do botão QUANDO ESTÁ SELECIONADO
                    "nav-link-selected": {
                        # Gradiente azul para um visual premium
                        "background": "linear-gradient(135deg, #1e40af, #3b82f6)",
                        "color": "white",
                        "box-shadow": "inset 0 1px 2px rgba(0,0,0,0.2)",
                    },
                }
            )


            # --- SE O USUÁRIO ESCOLHER "EMISSÕES" ---
            if tipo_dado_detalhado == "Emissões":
                
                # Garante que a coluna de data é datetime
                df_tab2["DATA_EMISSÃO"] = pd.to_datetime(df_tab2["DATA_EMISSÃO"], errors="coerce")

                # Filtro de dia da semana para emissões
                mapa_dias_numerico = {0: "Segunda", 1: "Terça", 2: "Quarta", 3: "Quinta", 4: "Sexta", 5: "Sábado"}
                df_tab2["DIA_SEMANA"] = df_tab2["DATA_EMISSÃO"].dt.weekday.map(mapa_dias_numerico)

                # =================================================================
                # ✅ INÍCIO DA ALTERAÇÃO
                # =================================================================
                
                # 1. Cria o título dinâmico
                titulo_seletor_dia = " Selecione o Dia da Semana"
                if mes_selecionado != "Todos":
                    # Adiciona o mês ao título, com a primeira letra maiúscula
                    titulo_seletor_dia += f" - {mes_selecionado.upper()}" # <--- MUDANÇA APLICADA

                # 2. Usa a variável dinâmica no 'menu_title'
                dia_selecionado = option_menu(
                    menu_title=titulo_seletor_dia,
                    options=["Todos", "Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado"],
                    # ✅ --- NOVOS ÍCONES PROFISSIONAIS AQUI --- ✅
                    icons=[
                        "stack",                # Ícone para "Todos"
                        "calendar-check",         # Ícone para "Segunda"
                        "calendar-check",     # Ícone para "Terça"
                        "calendar-check",        # Ícone para "Quarta"
                        "calendar-check",       # Ícone para "Quinta"
                        "calendar-check",       # Ícone para "Sexta"
                        "calendar-check",        # Ícone para "Sábado"
                    ],
                    menu_icon="calendar-check", 
                    default_index=0, 
                    orientation="horizontal",
                    styles={
                        "container": {"padding": "0!important", "background-color": "transparent", "margin-bottom": "25px"},
                        "menu_title": {"font-size": "16px", "font-weight": "600", "margin-bottom": "10px"},
                        "icon": {"color": "#f1f5f9", "font-size": "16px"},
                        "nav-link": {"font-size": "14px", "text-align": "center", "margin": "0px 2px", "--hover-color": "#334155", "border-radius": "10px", "background-color": "#1e293b", "padding": "8px 12px"},
                        "nav-link-selected": {"background-color": "#4f46e5", "font-weight": "bold", "color": "white"},
                    }
                )
                
                # =================================================================
                # ✅ FIM DA ALTERAÇÃO
                # =================================================================

                # Aplica o filtro de dia
                if dia_selecionado != "Todos":
                    df_filtrado_dias = df_tab2[df_tab2["DIA_SEMANA"] == dia_selecionado]
                else:
                    df_filtrado_dias = df_tab2.copy()


                # =================================================================
                # ✅ INÍCIO DA ATUALIZAÇÃO - LÓGICA CORRIGIDA E FINAL (v7)
                # =================================================================

                # Calcula e exibe os KPIs de emissões
                if not df_filtrado_dias.empty:
                    
                    # --- LÓGICA DE MÉDIA ADAPTATIVA ---
                    is_single_day = (start_date == end_date)

                    # --- PREPARAÇÃO DO DATAFRAME BASE PARA OS CÁLCULOS ---
                    df_kpis = df_filtrado_dias.copy()

                    # REGRA PRINCIPAL: Se "Todos" estiver selecionado, filtramos o df_kpis
                    # Se "Todas" estiver selecionado, só considerar NOITE e DIA
                    if expedicao_selecionada.upper() in ['TODOS', 'TODAS']:
                        df_kpis = df_kpis[df_kpis['EXPEDIÇÃO'].isin(['NOITE', 'DIA'])]

                    # --- CÁLCULO DOS KPIs A PARTIR DO df_kpis JÁ FILTRADO ---
                    if not df_kpis.empty:
                        total_emissoes = df_kpis["CTRC_EMITIDO"].sum()
                        usuarios_unicos = df_kpis["USUÁRIO"].nunique()
                        periodo = f"{df_kpis['DATA_EMISSÃO'].min().strftime('%d/%m/%Y')} a {df_kpis['DATA_EMISSÃO'].max().strftime('%d/%m/%Y')}"

                        if is_single_day:
                            # CENÁRIO 1: DIA ÚNICO
                            label_media = "Média do Dia Selecionado"
                            # O divisor é a contagem de registros do df_kpis (que já foi filtrado)
                            divisor = len(df_kpis)
                            # A média usa o total_emissoes do df_kpis (também já filtrado)
                            media_emissoes = total_emissoes / divisor if divisor > 0 else 0

                        else:
                            # CENÁRIO 2: MÚLTIPLOS DIAS
                            label_media = "Média Diária de Emissões"
                            
                            df_para_media = df_kpis.copy()
                            df_para_media['DIA_SEMANA_NUM'] = df_para_media['DATA_EMISSÃO'].dt.weekday

                            if expedicao_selecionada == 'NOITE':
                                df_para_media = df_para_media[df_para_media['DIA_SEMANA_NUM'] != 5]
                            
                            dias_unicos_divisor = df_para_media['DATA_EMISSÃO'].nunique()
                            total_emissoes_media = df_para_media['CTRC_EMITIDO'].sum()
                            media_emissoes = total_emissoes_media / dias_unicos_divisor if dias_unicos_divisor > 0 else 0

                        # Lógica para encontrar o usuário com mais emissões
                        emissoes_por_usuario = df_kpis.groupby('USUÁRIO')['CTRC_EMITIDO'].sum()
                        if not emissoes_por_usuario.empty:
                            usuario_top = emissoes_por_usuario.idxmax()
                            emissoes_top = emissoes_por_usuario.max()
                        else:
                            usuario_top, emissoes_top = "Nenhum", 0
                    else:
                        # Caso df_kpis fique vazio após o filtro de expedição
                        total_emissoes, media_emissoes, usuarios_unicos, periodo = 0, 0, 0, "N/A"
                        usuario_top, emissoes_top = "Nenhum", 0
                        label_media = "Média Diária de Emissões"

                else:
                    # Se não houver dados desde o início
                    total_emissoes, media_emissoes, usuarios_unicos, periodo = 0, 0, 0, "N/A"
                    usuario_top, emissoes_top = "Nenhum", 0
                    label_media = "Média Diária de Emissões"


                # =================================================================
                # ✅ FIM DA ATUALIZAÇÃO
                # =================================================================

                # ✅ LAYOUT AJUSTADO PARA 5 COLUNAS
                col1, col2, col3, col4, col5 = st.columns(5)
                
                # ✅ CARD 1 ATUALIZADO: Mostra o usuário com mais emissões
                with col1: 
                    st.markdown(f'''
                    <div class="kpi-card kpi-blue">
                        <div class="kpi-icon">🏆</div>
                        <div class="kpi-value" style="font-size: 1.5rem; padding-top: 10px;">{usuario_top}</div>
                        <div class="kpi-label">
                            Usuário com Mais Emissões  
            ({format_number(emissoes_top)} emissões)
                        </div>
                    </div>
                    ''', unsafe_allow_html=True)
                    
                with col2: st.markdown(f'<div class="kpi-card kpi-green"><div class="kpi-icon">📈</div><div class="kpi-value">{format_number(total_emissoes)}</div><div class="kpi-label">Total de Emissões</div></div>', unsafe_allow_html=True)
                with col3: 
                    st.markdown(f'''
                    <div class="kpi-card kpi-teal">
                        <div class="kpi-icon">📊</div>
                        <div class="kpi-value">{format_number(media_emissoes)}</div>
                        <div class="kpi-label">{label_media}</div>
                    </div>
                    ''', unsafe_allow_html=True)
                with col4: st.markdown(f'<div class="kpi-card kpi-purple"><div class="kpi-icon">👤</div><div class="kpi-value">{usuarios_unicos}</div><div class="kpi-label">Usuários</div></div>', unsafe_allow_html=True)
                with col5: st.markdown(f'<div class="kpi-card kpi-orange"><div class="kpi-icon">📅</div><div class="kpi-value" style="font-size: 1.4rem; padding-top: 10px;">{periodo}</div><div class="kpi-label">Período Analisado</div></div>', unsafe_allow_html=True)
                
                st.markdown("---")

                # Mostra a tabela de emissões
                if not df_filtrado_dias.empty:
                    df_para_exibir = df_filtrado_dias.copy()
                    df_para_exibir['DATA_EMISSÃO'] = df_para_exibir['DATA_EMISSÃO'].dt.strftime('%d-%m-%Y')
                    df_para_exibir['CTRC_EMITIDO'] = df_para_exibir['CTRC_EMITIDO'].astype(str)
                    st.dataframe(df_para_exibir[["MÊS", "DATA_EMISSÃO", "DIA_SEMANA", "CTRC_EMITIDO", "USUÁRIO", "EXPEDIÇÃO"]], use_container_width=True, hide_index=True)
                else:
                    st.warning(f"Nenhum dado de emissão encontrado para '{dia_selecionado}' com os filtros atuais.")

                # Botão de download de emissões
                csv = df_filtrado_dias.to_csv(index=False).encode("utf-8")
                st.download_button("📥 Baixar dados de emissões (CSV)", data=csv, file_name="dados_emissões_semanais.csv", mime="text/csv", key="download_emissao_detalhada")


            # --- SE O USUÁRIO ESCOLHER "CANCELAMENTOS" ---
            else:
                # Garante que a coluna de data é datetime
                cancelamentos_tab2["DATA_CANCELADO"] = pd.to_datetime(cancelamentos_tab2["DATA_CANCELADO"], errors="coerce")

                # Filtro de dia da semana para cancelamentos
                mapa_dias_numerico_canc = {0: "Segunda", 1: "Terça", 2: "Quarta", 3: "Quinta", 4: "Sexta", 5: "Sábado"}
                cancelamentos_tab2["DIA_SEMANA"] = cancelamentos_tab2["DATA_CANCELADO"].dt.weekday.map(mapa_dias_numerico_canc)

                # =================================================================
                # ✅ INÍCIO DA ALTERAÇÃO
                # =================================================================

                # 1. Cria o título dinâmico, mostrando o mês selecionado
                titulo_base_canc = "Selecione o Dia da Semana"
                # Adiciona o mês ao título se um filtro de mês estiver ativo
                titulo_mes_canc = f" - {mes_selecionado.upper()}" if mes_selecionado != "Todos" else ""
                titulo_completo_canc = f"{titulo_base_canc}{titulo_mes_canc}"

                # 2. Usa o título dinâmico e a lista de ícones correta
                dia_selecionado_canc = option_menu(
                    menu_title=titulo_completo_canc,  # <--- TÍTULO DINÂMICO APLICADO
                    options=["Todos", "Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado"],
                    # ✅ --- ÍCONES CORRIGIDOS E VARIADOS --- ✅
                    icons=[
                        "stack", "calendar-x", "calendar-x", "calendar-x",
                        "calendar-x", "calendar-x", "calendar-x"
                    ],
                    menu_icon="calendar-x",  # Ícone principal temático
                    default_index=0,
                    orientation="horizontal",
                    key="filtro_dia_cancelamento",
                    styles={
                        "container": {"padding": "0!important", "background-color": "transparent", "margin-bottom": "25px"},
                        "menu_title": {"font-size": "16px", "font-weight": "600", "margin-bottom": "10px"},
                        "icon": {"color": "#f1f5f9", "font-size": "16px"},
                        "nav-link": {"font-size": "14px", "text-align": "center", "margin": "0px 2px", "--hover-color": "#334155", "border-radius": "10px", "background-color": "#1e293b", "padding": "8px 12px"},
                        "nav-link-selected": {"background-color": "#dc2626", "font-weight": "bold", "color": "white"},
                    }
                )

                # =================================================================
                # ✅ FIM DA ALTERAÇÃO
                # =================================================================

                # Aplica o filtro de dia
                if dia_selecionado_canc != "Todos":
                    df_filtrado_dias_canc = cancelamentos_tab2[cancelamentos_tab2["DIA_SEMANA"] == dia_selecionado_canc]
                else:
                    df_filtrado_dias_canc = cancelamentos_tab2.copy()

                # =================================================================
                # ✅ INÍCIO DA NOVA LÓGICA - IDENTIFICAR SETOR COM MAIS CANCELAMENTOS
                # =================================================================
                
                if not df_filtrado_dias_canc.empty:
                    # 1. KPIs gerais (cálculos existentes)
                    total_cancelamentos_kpi = len(df_filtrado_dias_canc)
                    media_cancelamentos_kpi = df_filtrado_dias_canc.groupby(df_filtrado_dias_canc['DATA_CANCELADO'].dt.date).size().mean()
                    usuarios_unicos_canc = df_filtrado_dias_canc["USUARIO"].nunique()
                    periodo_canc = f"{df_filtrado_dias_canc['DATA_CANCELADO'].min().strftime('%d/%m/%Y')} a {df_filtrado_dias_canc['DATA_CANCELADO'].max().strftime('%d/%m/%Y')}"
                    
                    cancelamentos_por_usuario = df_filtrado_dias_canc['USUARIO'].value_counts()
                    usuario_top_canc = cancelamentos_por_usuario.idxmax()
                    cancelamentos_top = cancelamentos_por_usuario.max()

                    # 2. FUNÇÃO PARA EXTRAIR O SETOR (BASEADA EM PREFIXOS ESPECÍFICOS - v10)
                    def extrair_setor(motivo):
                        motivo_str = str(motivo).upper().strip()

                        # Define as listas de prefixos para cada setor, do mais específico para o mais geral
                        prefixos_expedicao = [
                            "EXPEDICAO -", "EXPEDICAO.", "EXPEDICAO", "EXP -", "EXP.", "EXP"
                        ]
                        prefixos_coleta = [
                            "COLETA -", "COLETA.", "COLETA:", "COLETA", "COL"
                        ]
                        prefixos_sefaz = [
                            "SEFAZ -", "SEFAZ-", "SEFAZ.", "SEFAZ"
                        ]
                        prefixos_cliente = [
                            "CLIENTE -", "CLIENTE-", "CLIENTE.", "CLIENTE", "CLI"
                        ]
                        prefixos_operacional = [
                            "OPERACIONAL -", "OPERACIONAL-", "OPERACIONAL.", "OPERACIONAL", "OPE"
                        ]
                        prefixos_comercial = [
                            "COMERCIAL -", "COMERCIAL.", "COM -", "COM.", "COMERCIAL", "COM"
                        ]

                        # Verifica cada setor na ordem de prioridade
                        if any(motivo_str.startswith(p) for p in prefixos_expedicao):
                            return "EXPEDIÇÃO"
                        
                        if any(motivo_str.startswith(p) for p in prefixos_coleta):
                            return "COLETA"
                        
                        if any(motivo_str.startswith(p) for p in prefixos_sefaz):
                            return "SEFAZ"
                        
                        if any(motivo_str.startswith(p) for p in prefixos_cliente):
                            return "CLIENTE"
                        
                        if any(motivo_str.startswith(p) for p in prefixos_operacional):
                            return "OPERACIONAL"
                        
                        if any(motivo_str.startswith(p) for p in prefixos_comercial):
                            return "COMERCIAL"
                        
                        # Se não começar com nenhum prefixo conhecido, retorna "OUTROS"
                        return "OUTROS"

                    # 3. APLICA A FUNÇÃO E CONTA OS SETORES
                    df_filtrado_dias_canc['SETOR'] = df_filtrado_dias_canc['MOTIVO'].apply(extrair_setor)
                    contagem_setores = df_filtrado_dias_canc['SETOR'].value_counts()

                    # =================================================================
                    # ✅ INÍCIO DA NOVA LÓGICA - IGNORAR "OUTROS"
                    # =================================================================
                    
                    # 4. REMOVE A CATEGORIA "OUTROS" DA CONTAGEM
                    # O método .drop() remove o índice 'OUTROS'. 'errors='ignore'' garante que não dará erro se 'OUTROS' não existir.
                    contagem_setores_filtrada = contagem_setores.drop('OUTROS', errors='ignore')

                    # 5. IDENTIFICA O SETOR TOP E SUA CONTAGEM A PARTIR DA LISTA FILTRADA
                    if not contagem_setores_filtrada.empty:
                        setor_top = contagem_setores_filtrada.idxmax()
                        qtd_setor_top = contagem_setores_filtrada.max()
                    else:
                        # Se a lista ficar vazia após remover "OUTROS", define um valor padrão
                        setor_top, qtd_setor_top = "Nenhum", 0
                        
                else:
                    # Define valores padrão se não houver dados
                    total_cancelamentos_kpi, media_cancelamentos_kpi, usuarios_unicos_canc, periodo_canc = 0, 0, 0, "N/A"
                    usuario_top_canc, cancelamentos_top = "Nenhum", 0
                    setor_top, qtd_setor_top = "Nenhum", 0


                # ✅ LAYOUT ATUALIZADO PARA 5 COLUNAS
                col1_c, col2_c, col3_c, col4_c, col5_c = st.columns(5)

                # Card 1: Usuário com mais cancelamentos
                with col1_c: 
                    st.markdown(f'''
                    <div class="kpi-card kpi-red">
                        <div class="kpi-icon">🏆</div>
                        <div class="kpi-value" style="font-size: 1.5rem; padding-top: 10px;">{usuario_top_canc}</div>
                        <div class="kpi-label">
                            Usuário com Mais Cancelamentos  
({format_number(cancelamentos_top)} cancelamentos)
                        </div>
                    </div>
                    ''', unsafe_allow_html=True)
                
                # Card 2: Setor com mais cancelamentos
                with col2_c:
                    st.markdown(f'''
                    <div class="kpi-card kpi-orange">
                        <div class="kpi-icon">🎯</div>
                        <div class="kpi-value" style="font-size: 1.5rem; padding-top: 10px;">{setor_top}</div>
                        <div class="kpi-label">
                            Setor com Mais Cancelamentos  
({format_number(qtd_setor_top)} ocorrências)
                        </div>
                    </div>
                    ''', unsafe_allow_html=True)
                    
                # Card 3: Total de Cancelamentos
                with col3_c: 
                    st.markdown(f'''
                    <div class="kpi-card kpi-indigo">
                        <div class="kpi-icon">❌</div>
                        <div class="kpi-value">{format_number(total_cancelamentos_kpi)}</div>
                        <div class="kpi-label">Total de Cancelamentos</div>
                    </div>
                    ''', unsafe_allow_html=True)
                
                # Card 4: Média Diária
                with col4_c: 
                    st.markdown(f'''
                    <div class="kpi-card kpi-purple">
                        <div class="kpi-icon">📊</div>
                        <div class="kpi-value">{round(media_cancelamentos_kpi)}</div>
                        <div class="kpi-label">Média Diária</div>
                    </div>
                    ''', unsafe_allow_html=True)
                
                # Card 5: Período Analisado
                with col5_c: 
                    st.markdown(f'''
                    <div class="kpi-card kpi-teal">
                        <div class="kpi-icon">📅</div>
                        <div class="kpi-value" style="font-size: 1.4rem; padding-top: 10px;">{periodo_canc}</div>
                        <div class="kpi-label">Período Analisado</div>
                    </div>
                    ''', unsafe_allow_html=True)


                st.markdown("---")

                # Mostra a tabela de cancelamentos
                if not df_filtrado_dias_canc.empty:
                    df_para_exibir_canc = df_filtrado_dias_canc.copy()
                    df_para_exibir_canc['DATA_CANCELADO'] = df_para_exibir_canc['DATA_CANCELADO'].dt.strftime('%d-%m-%Y')
                    df_para_exibir_canc = df_para_exibir_canc[["MÊS", "DATA_CANCELADO", "DIA_SEMANA", "USUARIO", "EXPEDIÇÃO", "MOTIVO"]]
                    df_para_exibir_canc.rename(columns={"USUARIO": "USUÁRIO"}, inplace=True)
                    st.dataframe(df_para_exibir_canc, use_container_width=True, hide_index=True)
                else:
                    st.warning(f"Nenhum dado de cancelamento encontrado para '{dia_selecionado_canc}' com os filtros atuais.")

                # Botão de download de cancelamentos
                csv_canc = df_filtrado_dias_canc.to_csv(index=False).encode("utf-8")
                st.download_button("📥 Baixar dados de cancelamentos (CSV)", data=csv_canc, file_name="dados_cancelamentos_semanais.csv", mime="text/csv", key="download_cancelamento_detalhado")

            st.markdown("---")

            # ===============================
            # Substitua o conteúdo da sua 'tab2' por este bloco
            with tab2:
                # Criar cópias dos dataframes filtrados para uso específico da aba
                df_tab2 = df_filtrado.copy()
                cancelamentos_tab2 = cancelamentos_filtrado.copy()

                if df_tab2.empty:
                    st.warning("Nenhum dado disponível para o período selecionado.")
                else:
                    # ==================================================================
                    #  CABEÇALHO E SELETOR DE VISUALIZAÇÃO (COM TÍTULO CENTRALIZADO)
                    # ==================================================================

                    # Título principal da seção, dinâmico com a expedição selecionada
                    titulo_expedicao = f" – Expedição: {expedicao_selecionada}" if expedicao_selecionada != "Todas" else ""
                    
                    # ✅ TÍTULO CENTRALIZADO USANDO st.markdown
                    st.markdown(f"<h3 style='text-align: center; color: #E0E0E0; margin-bottom: 1rem;'>📅 Padrões por Dia da Semana{titulo_expedicao}</h3>", unsafe_allow_html=True)

                    # Seletor principal para escolher entre "Totais" e "Médias"
                    tipo_visualizacao = option_menu(
                        menu_title=None,
                        options=["Total de Emissões", "Médias de Emissões"],
                        # Ícones profissionais da biblioteca Bootstrap
                        icons=['bar-chart-fill', 'graph-up-arrow'],
                        menu_icon="cast",
                        default_index=0,
                        orientation="horizontal",
                        styles={
                            # Container que envolve os botões
                            "container": {
                                "padding": "5px !important",
                                "background-color": "#0f172a",
                                "border-radius": "12px",
                                "border": "1px solid #334155",
                                "margin-bottom": "2rem" # Espaço abaixo do menu
                            },
                            # Ícone de cada botão
                            "icon": {
                                "color": "#f1f5f9",
                                "font-size": "18px",
                                "vertical-align": "middle",
                            },
                            # Estilo de cada botão (não selecionado)
                            "nav-link": {
                                "font-size": "16px",
                                "font-weight": "500",
                                "text-align": "center",
                                "margin": "0px",
                                "padding": "10px 0px",
                                "border-radius": "10px",
                                "flex-grow": "1",
                                "color": "#9CA3AF",
                                "--hover-color": "#334155",
                            },
                            # Estilo do botão QUANDO ESTÁ SELECIONADO
                            "nav-link-selected": {
                                "background": "linear-gradient(135deg, #1e40af, #3b82f6)",
                                "color": "white",
                                "font-weight": "bold",
                            },
                        }
                    )

            # Preparar dados base
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

            # Calcular taxa de cancelamento (%)
            weekday_stats['taxa_cancelamento'] = (
                (weekday_stats['cancelamentos_sum'] / weekday_stats['sum']) * 100
            ).fillna(0)

            # Criar duas colunas para os gráficos
            col1, col2 = st.columns(2)

            # ===============================
            # 📈 GRÁFICO 1: Totais
            # ===============================
            with col1:
                # Adiciona o mês no título (se não for "Todos")
                titulo_mes = f" - {mes_selecionado.upper()}" if mes_selecionado != "Todos" else ""
                st.markdown(f"<h3 style='text-align: center;'>📈 Total de Emissões{titulo_mes}</h3>", unsafe_allow_html=True)   

                max_emissoes_sum = weekday_stats["sum"].max()
                max_cancelamentos_sum = weekday_stats["cancelamentos_sum"].max()

                fig_totais = make_subplots(specs=[[{"secondary_y": True}]])

                fig_totais.add_trace(go.Bar(
                x=weekday_stats["weekday_pt"], 
                y=weekday_stats["sum"],
                name='Emissões', 
                marker_color="#0752ca",

                # 🔹 Aqui formatamos com ponto como separador
                text=[f"{v:,}".replace(",", ".") for v in weekday_stats["sum"]],
                textposition="outside",
                textfont_size=16,

                customdata=np.stack([
                    weekday_stats["weekday_pt"],
                    weekday_stats["sum"].astype(int),
                    weekday_stats["cancelamentos_sum"].astype(int)
                ], axis=-1),
                hovertemplate=(
                    "📆 %{customdata[0]}<br>"
                    "📊 Total de Emissões: %{customdata[1]}<br>"
                    "✖️ Cancelamentos: %{customdata[2]}<extra></extra>"
                )
            ), secondary_y=False)


                # Linha de cancelamentos
                fig_totais.add_trace(go.Scatter(
                    x=weekday_stats["weekday_pt"], y=weekday_stats["cancelamentos_sum"],
                    name='Cancelamentos', mode='lines+markers+text',
                    line=dict(color='#ef4444', width=3),
                    marker=dict(size=8, color='white', line=dict(width=2, color='#ef4444')),
                    text=weekday_stats["cancelamentos_sum"].astype(int), textposition="top center",
                    textfont=dict(size=14, color="#ffffff"),
                    customdata=np.stack([
                        weekday_stats["weekday_pt"],
                        weekday_stats["sum"].astype(int),
                        weekday_stats["cancelamentos_sum"].astype(int)
                    ], axis=-1),
                    hovertemplate=(
                        "📆 %{customdata[0]}<br>"
                        "📊 Total de Emissões: %{customdata[1]}<br>"
                        "✖️ Cancelamentos: %{customdata[2]}<extra></extra>"
                    )
                ), secondary_y=True)

                # CÓDIGO CORRIGIDO

                # Layout
                fig_totais.update_layout(
                    xaxis_title="Dia da Semana", 
                    height=600,
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                    hoverlabel=dict(
                        bgcolor="white",
                        font_size=16,
                        font_family="Verdana",
                        font_color="black"
                    ),
                    separators=".,",  # ✅ Aqui força padrão brasileiro em todo o gráfico
                )

                # Eixo Y primário (Emissões) - Aumenta o espaço para os rótulos
                fig_totais.update_yaxes(
                    title_text="<b>Total de Emissões</b>", title_font_color="#3b82f6",
                    tickfont_color="#3b82f6", secondary_y=False, 
                    range=[0, max_emissoes_sum * 1.20], # Aumentei um pouco o multiplicador para dar mais espaço
                    tickformat=",.0f"
                )

                # Eixo Y secundário (Cancelamentos) - Aumenta o teto do eixo
                fig_totais.update_yaxes(
                    title_text="<b>Total de Cancelamentos</b>", title_font_color="#ef4444",
                    tickfont_color="#ef4444", secondary_y=True, 
                    # ✅ ESTA É A CORREÇÃO PRINCIPAL:
                    # Aumentamos o multiplicador de 2.0 para 2.5 (ou mais, se necessário)
                    # para dar mais "ar" acima da linha de cancelamento.
                    range=[0, max_cancelamentos_sum * 2.5], 
                    tickformat=",.0f"
                )


                st.plotly_chart(fig_totais, use_container_width=True)

                # Estatísticas
                melhor_dia_totais = weekday_stats.loc[weekday_stats['sum'].idxmax(), 'weekday_pt']
                pior_dia_totais = weekday_stats.loc[weekday_stats['sum'].idxmin(), 'weekday_pt']
                dia_pico_cancelamentos = weekday_stats.loc[weekday_stats['cancelamentos_sum'].idxmax(), 'weekday_pt']

                if usuario_selecionado != "Todos":
                    titulo_estatisticas = f"📊 Estatísticas - Totais de Emissões de {usuario_selecionado}"
                else:
                    titulo_estatisticas = "📊 Estatísticas - Totais de Emissões"

                st.markdown(f"#### {titulo_estatisticas}")
                st.markdown(f"🚀 **Dia de Pico:** {melhor_dia_totais}")
                st.markdown(f"📉 **Menor Produção:** {pior_dia_totais}")
                st.markdown(f"🚨 **Pico de Cancelamentos:** {dia_pico_cancelamentos}")

            
            # ===============================
            # 📊 Cálculo correto do weekday_stats
            # ===============================

            # Dicionário para mapear nomes dos dias da semana para o formato curto
            weekday_map = {
                'Monday': 'Segunda', 'Tuesday': 'Terça', 'Wednesday': 'Quarta',
                'Thursday': 'Quinta', 'Friday': 'Sexta', 'Saturday': 'Sábado', 'Sunday': 'Domingo'
            }

            # Base de emissões
            df_weekday = df_filtrado.copy()
            df_weekday["weekday_num"] = df_weekday["DATA_EMISSÃO"].dt.weekday
            # ✅ CORREÇÃO: Usa o dicionário para gerar nomes curtos
            df_weekday["weekday_pt"] = df_weekday["DATA_EMISSÃO"].dt.day_name().map(weekday_map)

            # 1. Soma total de emissões por dia da semana
            soma_emissoes = df_weekday.groupby(
                ["weekday_num", "weekday_pt"]
            )["CTRC_EMITIDO"].sum().reset_index(name="sum")

            # 2. Conta quantos dias únicos de emissão existem para cada dia da semana
            dias_unicos = df_weekday.groupby(
                ["weekday_num", "weekday_pt"]
            )["DATA_EMISSÃO"].nunique().reset_index(name="dias_unicos")

            # 3. Junta os dois
            weekday_stats = pd.merge(soma_emissoes, dias_unicos, on=["weekday_num", "weekday_pt"])

            # 4. Calcula a média correta (total / nº de dias únicos)
            weekday_stats["mean"] = weekday_stats["sum"] / weekday_stats["dias_unicos"]

           # ===============================
            # 📊 Cancelamentos (corrigido)
            # ===============================
            cancelamentos_stats = cancelamentos_filtrado.copy()

            # Dia da semana (número e nome em PT-BR)
            cancelamentos_stats["weekday_num"] = cancelamentos_stats["DATA_CANCELADO"].dt.weekday
            # ✅ CORREÇÃO: Usa o mesmo dicionário para garantir consistência
            cancelamentos_stats["weekday_pt"] = cancelamentos_stats["DATA_CANCELADO"].dt.day_name().map(weekday_map)

            # 🔴 Contagem de cancelamentos (cada linha é um cancelamento)
            soma_cancel = cancelamentos_stats.groupby(
                ["weekday_num", "weekday_pt"]
            )["CTRC_CANCELADOS"].count().reset_index(name="sum_cancel")

            # 🟠 Dias únicos com registro de cancelamento
            dias_cancel_unicos = cancelamentos_stats.groupby(
                ["weekday_num", "weekday_pt"]
            )["DATA_CANCELADO"].nunique().reset_index(name="dias_cancel_unicos")

            # 🟢 Junta e calcula média
            cancelamentos_mean = pd.merge(
                soma_cancel, dias_cancel_unicos, on=["weekday_num", "weekday_pt"], how="left"
            )
            cancelamentos_mean["cancelamentos_mean"] = (
                cancelamentos_mean["sum_cancel"] / cancelamentos_mean["dias_cancel_unicos"]
)
            # ===============================
            # 📊 Merge final
            # ===============================
            weekday_stats = weekday_stats.merge(
                cancelamentos_mean[["weekday_num", "weekday_pt", "cancelamentos_mean"]],
                on=["weekday_num", "weekday_pt"],
                how="left"
            ).fillna(0)

            # Ordena pela sequência normal da semana
            weekday_stats = weekday_stats.sort_values("weekday_num")



            # ===============================
            # 📊 GRÁFICO 2: Médias
            # ===============================
            with col2:
                # Adiciona o mês no título (se não for "Todos")
                titulo_mes = f" - {mes_selecionado}" if mes_selecionado != "Todos" else ""
                st.markdown(f"### 📊 Médias de Emissões{titulo_mes}")
                
                max_emissoes_mean = weekday_stats["mean"].max()
                max_cancelamentos_mean = weekday_stats["cancelamentos_mean"].max()
                
                fig_medias = make_subplots(specs=[[{"secondary_y": True}]])

                # Barras de média de emissões
                fig_medias.add_trace(go.Bar(
                    x=weekday_stats["weekday_pt"], y=weekday_stats["mean"],
                    name='Média de Emissões', marker_color="#058d37",
                    text=[f"{v:,.0f}".replace(",", ".") for v in weekday_stats["mean"]],
                    textposition="outside",
                    textfont_size=16,
                    customdata=np.stack([
                        weekday_stats["weekday_pt"],
                        weekday_stats["mean"].round(0),
                        weekday_stats["cancelamentos_mean"].round(0)
                    ], axis=-1),
                    hovertemplate=(
                        "📆 %{customdata[0]}<br>"
                        "📊 Média de Emissões: %{customdata[1]}<br>"
                        "✖️ Média de Cancelamentos: %{customdata[2]}<extra></extra>"
                    )
                ), secondary_y=False)

                # Linha de média de cancelamentos
                fig_medias.add_trace(go.Scatter(
                    x=weekday_stats["weekday_pt"], y=weekday_stats["cancelamentos_mean"],
                    name='Média de Cancelamentos', mode='lines+markers+text',
                    line=dict(color='#f97316', width=3),
                    marker=dict(size=8, color='white', line=dict(width=2, color='#f97316')),
                    text=weekday_stats["cancelamentos_mean"].round(0), texttemplate='%{text:.0f}',
                    textposition="top center",
                    textfont=dict(size=14, color="#ffffff"),
                    customdata=np.stack([
                        weekday_stats["weekday_pt"],
                        weekday_stats["mean"].round(0),
                        weekday_stats["cancelamentos_mean"].round(0)
                    ], axis=-1),
                    hovertemplate=(
                        "📆 %{customdata[0]}<br>"
                        "📊 Média de Emissões: %{customdata[1]}<br>"
                        "✖️ Média de Cancelamentos: %{customdata[2]}<extra></extra>"
                    )
                ), secondary_y=True)

                fig_medias.update_layout(
                    xaxis_title="Dia da Semana", 
                    height=600,
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),

                    # ✅ Aumenta tooltip
                    hoverlabel=dict(
                        bgcolor="white",
                        font_size=16,
                        font_family="Verdana",
                        font_color="black"
                    ),
                    separators=".,",  # ✅ Aplica padrão brasileiro em todo o gráfico
                )

                fig_medias.update_yaxes(
                    title_text="<b>Média de Emissões</b>", title_font_color="#22c55e",
                    tickfont_color="#22c55e", secondary_y=False, range=[0, max_emissoes_mean * 1.2],
                    tickformat=",.0f"  # ✅ força separador de milhar
                )

                fig_medias.update_yaxes(
                    title_text="<b>Média de Cancelamentos</b>", title_font_color="#f97316",
                    tickfont_color="#f97316", secondary_y=True, range=[0, max_cancelamentos_mean * 2.0],
                    tickformat=",.0f"  # ✅ idem no eixo secundário
                )


                st.plotly_chart(fig_medias, use_container_width=True)

                # Estatísticas
                melhor_dia_medias = weekday_stats.loc[weekday_stats['mean'].idxmax(), 'weekday_pt']
                pior_dia_medias = weekday_stats.loc[weekday_stats['mean'].idxmin(), 'weekday_pt']
                dia_mais_cancel_mean = weekday_stats.loc[weekday_stats['cancelamentos_mean'].idxmax(), 'weekday_pt']

                if usuario_selecionado != "Todos":
                    titulo_estatisticas_medias = f"📊 Estatísticas - Médias de Emissões de {usuario_selecionado}"
                else:
                    titulo_estatisticas_medias = "📊 Estatísticas - Médias de Emissões"

                st.markdown(f"#### {titulo_estatisticas_medias}")
                st.markdown(f"🚀 **Dia de Pico:** {melhor_dia_medias}")
                st.markdown(f"📉 **Menor Média:** {pior_dia_medias}")
                st.markdown(f"🚨 **Pico de Cancelamentos:** {dia_mais_cancel_mean}")

        st.markdown("---")

    
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
                # =============================================================
                # 📊 Nova Análise Visual (Versão Moderna)
                # =============================================================
                st.markdown("""
                    <div style="display: flex; align-items: center; justify-content: center; margin-bottom: 1rem;">
                        <span style="font-size: 2.2rem; margin-right: 0.8rem;">📊</span>
                        <h3 style="color: #C5C5C5; font-weight: 500; margin-bottom: 0;">Análise Comparativa de Performance</h3>
                    </div>
                """, unsafe_allow_html=True)

                # --- Seletor Centralizado e Moderno ---
                _, col_central_seletor, _ = st.columns([1, 1.5, 1])
                with col_central_seletor:
                    tipo_agregacao_unificada = option_menu(
                        menu_title=None, options=["Totais", "Médias"], icons=['bar-chart-fill', 'graph-up'],
                        menu_icon="cast", default_index=0, orientation="horizontal", key="agregacao_unificada_user",
                        styles={
                            "container": {"padding": "5px !important", "background-color": "#0f172a", "border-radius": "12px", "border": "1px solid #334155"},
                            "icon": {"color": "#f1f5f9", "font-size": "18px"},
                            "nav-link": {
                                "font-size": "16px", "text-align": "center", "margin": "0px", "padding": "10px 0px",
                                "border-radius": "10px", "flex-grow": "1", "color": "#9CA3AF", "--hover-color": "#334155",
                            },
                            "nav-link-selected": {"background": "linear-gradient(135deg, #6366f1, #4f46e5)", "color": "white"},
                        }
                    )

                # --- Gráficos Lado a Lado ---
                col1, col2 = st.columns(2)

                with col1:
                    st.markdown("<h5 style='text-align: center; color: #E0E0E0;'>📈 Emissões</h5>", unsafe_allow_html=True)
                    df_emissoes = pd.DataFrame({
                        "Categoria": [f"{tipo_agregacao_unificada} Mensal", f"{tipo_agregacao_unificada} Semanal", f"{tipo_agregacao_unificada} Diário"],
                        "Valor": [
                            df_user.groupby(df_user["DATA_EMISSÃO"].dt.to_period("M"))["CTRC_EMITIDO"].sum().mean() if tipo_agregacao_unificada == "Totais" else media_mensal_user,
                            df_user.groupby([df_user["DATA_EMISSÃO"].dt.isocalendar().year, df_user["DATA_EMISSÃO"].dt.isocalendar().week])["CTRC_EMITIDO"].sum().mean() if tipo_agregacao_unificada == "Totais" else media_semanal_user,
                            df_user.groupby(df_user["DATA_EMISSÃO"].dt.date)["CTRC_EMITIDO"].sum().mean() if tipo_agregacao_unificada == "Totais" else media_diaria_user
                        ]
                    })
                    fig_emissoes = px.bar(
                        df_emissoes, x="Valor", y="Categoria", orientation="h", text="Valor", color="Valor", color_continuous_scale="Blues",
                        range_x=[0, df_emissoes["Valor"].max() * 1.25]
                    )
                    fig_emissoes.update_traces(texttemplate="%{text:,.0f}", textposition="outside", textfont_size=15)
                    fig_emissoes.update_layout(height=350, showlegend=False, margin=dict(l=20, r=40, t=20, b=20), yaxis_title=None, xaxis_title=None, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', yaxis={'categoryorder':'total descending'})
                    st.plotly_chart(fig_emissoes, use_container_width=True)

                with col2:
                    st.markdown("<h5 style='text-align: center; color: #E0E0E0;'>❌ Cancelamentos</h5>", unsafe_allow_html=True)
                    df_cancelamentos = pd.DataFrame({
                        "Categoria": [f"{tipo_agregacao_unificada} Mensal", f"{tipo_agregacao_unificada} Semanal", f"{tipo_agregacao_unificada} Diário"],
                        "Valor": [
                            cancelamentos_user.groupby([cancelamentos_user["DATA_CANCELADO"].dt.year, cancelamentos_user["DATA_CANCELADO"].dt.month]).size().mean() if tipo_agregacao_unificada == "Totais" else media_mensal_canc_user,
                            cancelamentos_user.groupby([cancelamentos_user["DATA_CANCELADO"].dt.isocalendar().year, cancelamentos_user["DATA_CANCELADO"].dt.isocalendar().week]).size().mean() if tipo_agregacao_unificada == "Totais" else media_semanal_canc_user,
                            cancelamentos_user.groupby(cancelamentos_user["DATA_CANCELADO"].dt.date).size().mean() if tipo_agregacao_unificada == "Totais" else media_diaria_canc_user
                        ]
                    })
                    fig_cancel = px.bar(
                        df_cancelamentos, x="Valor", y="Categoria", orientation="h", text="Valor", color="Valor", color_continuous_scale="Reds",
                        range_x=[0, df_cancelamentos["Valor"].max() * 1.25]
                    )
                    fig_cancel.update_traces(texttemplate="%{text:,.0f}", textposition="outside", textfont_size=15)
                    fig_cancel.update_layout(height=350, showlegend=False, margin=dict(l=20, r=40, t=20, b=20), yaxis_title=None, xaxis_title=None, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', yaxis={'categoryorder':'total descending'})
                    st.plotly_chart(fig_cancel, use_container_width=True)

                st.markdown("---")

                # =============================================================
                # ❌ Análise de Motivos de Cancelamento (Versão Moderna)
                # =============================================================
                st.markdown("""
                    <div style="display: flex; align-items: center; justify-content: center; margin-bottom: 1rem;">
                        <span style="font-size: 2.2rem; margin-right: 0.8rem;">📝</span>
                        <h3 style="color: #C5C5C5; font-weight: 500; margin-bottom: 0;">Top Motivos de Cancelamento</h3>
                    </div>
                """, unsafe_allow_html=True)

                # --- Seletores Modernos para o Gráfico de Motivos ---
                col_sel1, col_sel2 = st.columns(2)
                with col_sel1:
                    metric_opcao = option_menu(
                        "Visualizar por:", ["Quantidade", "Percentual (%)"], icons=['hash', 'percent'],
                        menu_icon="eye", default_index=0, orientation="horizontal", key="metric_cancelamentos_modern"
                    )
                with col_sel2:
                    top_n = option_menu(
                        "Exibir Top:", ["5", "10", "15", "20"], icons=['5-circle', '10-circle', 'list-ol', 'list-ol'],
                        menu_icon="sort-down", default_index=1, orientation="horizontal", key="top_cancelamentos_modern"
                    )
                    top_n = int(top_n) # Converte a string selecionada para inteiro

                # --- Preparação dos Dados e Gráfico ---
                if not cancelamentos_user.empty:
                    canc_motivo = cancelamentos_user.groupby("MOTIVO").size().reset_index(name="Quantidade").sort_values(by="Quantidade", ascending=False)
                    canc_motivo["Percentual"] = (canc_motivo["Quantidade"] / canc_motivo["Quantidade"].sum()) * 100

                    coluna_y, text_template = ("Quantidade", "%{x:,.0f}") if metric_opcao == "Quantidade" else ("Percentual", "%{x:.1f}%")

                    fig_motivos_cancel = px.bar(
                        canc_motivo.head(top_n), x=coluna_y, y="MOTIVO", orientation='h',
                        text=coluna_y, color=coluna_y, color_continuous_scale="Reds"
                    )
                    fig_motivos_cancel.update_traces(texttemplate=text_template, textposition="outside", textfont_size=14)
                    fig_motivos_cancel.update_layout(
                        height=max(400, top_n * 40), # Altura dinâmica baseada no número de itens
                        margin=dict(l=20, r=40, t=40, b=40),
                        xaxis_title=metric_opcao, yaxis_title=None,
                        yaxis=dict(categoryorder="total ascending"),
                        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)'
                    )
                    st.plotly_chart(fig_motivos_cancel, use_container_width=True)
                else:
                    st.info(f"Nenhum cancelamento encontrado para o usuário {usuario_selecionado} no período.")




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

       # =============================================================
        # 🏆 Ranking de Usuários (Versão Moderna e Larga)
        # =============================================================

        # --- Título Moderno e Centralizado ---
        st.markdown("""
            <div style="display: flex; align-items: center; justify-content: center; margin-bottom: 1rem;">
                <span style="font-size: 2.2rem; margin-right: 0.8rem;">🏆</span>
                <h3 style="color: #C5C5C5; font-weight: 500; margin-bottom: 0;">Ranking de Usuários</h3>
            </div>
        """, unsafe_allow_html=True)

        # --- Seletor option_menu Esticado (sem colunas) ---
        tipo_ranking = option_menu(
            menu_title=None,
            options=["Emissões", "Média de Emissões", "Cancelamentos"],
            icons=['graph-up-arrow', 'bar-chart-line-fill', 'x-circle-fill'],
            menu_icon="trophy-fill",
            default_index=0,
            orientation="horizontal",
            key="ranking_largo", # Nova chave única
            styles={
                # Container que envolve os botões
                "container": {
                    "padding": "5px !important",
                    "background-color": "#0f172a",
                    "border-radius": "12px",
                    "border": "1px solid #334155",
                    "margin-bottom": "2rem"
                },
                # Ícone de cada botão
                "icon": {
                    "color": "#f1f5f9",
                    "font-size": "18px",
                    "vertical-align": "middle",
                },
                # Estilo de cada botão (não selecionado)
                "nav-link": {
                    "font-size": "16px",
                    "font-weight": "500",
                    "text-align": "center",
                    "margin": "0px 4px",
                    "padding": "12px 0px", # Aumentei um pouco o padding vertical
                    "border-radius": "10px",
                    "flex-grow": "1", # Essencial para os botões preencherem o espaço
                    "color": "#9CA3AF",
                    "background-color": "#1e293b",
                    "--hover-color": "#334155",
                },
                # Estilo do botão QUANDO ESTÁ SELECIONADO
                "nav-link-selected": {
                    "background": "linear-gradient(135deg, #8b5cf6, #6d28d9)", # Gradiente Roxo
                    "color": "white",
                    "font-weight": "bold",
                },
            }
        )

# O resto do seu código para o gráfico continua o mesmo...


        # ... (o resto do seu código para preparar os dados e o gráfico continua o mesmo)



        # 2. LÓGICA PARA PREPARAR OS DADOS E CONFIGURAÇÕES
        
        # Define o dataframe de emissões a ser usado, já filtrado pela expedição selecionada
        df_emissoes_ranking = df_tab3.copy() # df_tab3 já respeita o filtro de expedição
        
        # Define o dataframe de cancelamentos a ser usado
        df_cancel_ranking = cancelamentos_tab3.copy() # cancelamentos_tab3 também já respeita o filtro

        if tipo_ranking == "Emissões":
            ranking_df = (
                df_emissoes_ranking.groupby("USUÁRIO")["CTRC_EMITIDO"]
                .sum()
                .sort_values(ascending=False)
                .reset_index()
            )
            ranking_df.columns = ['Usuário', 'Total']
            
            coluna_dados = 'Total'
            titulo_base = "Ranking de Usuários por Emissões"

        elif tipo_ranking == "Média de Emissões":
            # Agrupa por usuário e calcula a média de emissões por dia
            emissoes_por_usuario_dia = (
                df_emissoes_ranking
                .groupby(["USUÁRIO", df_emissoes_ranking["DATA_EMISSÃO"].dt.date])["CTRC_EMITIDO"]
                .sum()
                .reset_index()
            )
            ranking_df = (
                emissoes_por_usuario_dia
                .groupby("USUÁRIO")["CTRC_EMITIDO"]
                .mean()
                .sort_values(ascending=False)
                .reset_index()
            )
            ranking_df.columns = ['Usuário', 'Média']

            coluna_dados = 'Média'
            titulo_base = "Ranking de Usuários por Média de Emissões"

            # Gráfico de barras
            fig = px.bar(
                ranking_df,
                x="Usuário",
                y=coluna_dados,
                color="Usuário",
                text=coluna_dados
            )

            # Tooltip personalizado
            fig.update_traces(
                hovertemplate="Média de Emissões: %{y}<extra></extra>"
            )



        else:  # tipo_ranking == "Cancelamentos"
            if not df_cancel_ranking.empty:
                ranking_df = (
                    df_cancel_ranking['USUARIO']
                    .value_counts()
                    .reset_index()
                )
                ranking_df.columns = ['Usuário', 'Total']
            else:
                ranking_df = pd.DataFrame(columns=['Usuário', 'Total'])

            coluna_dados = 'Total'
            titulo_base = "Ranking de Usuários por Cancelamentos"

        # 3. LÓGICA PARA O TÍTULO DINÂMICO (COM EXPEDIÇÃO)
        
        # Parte do título que mostra a expedição
        if expedicao_selecionada != 'Todas':
            titulo_expedicao = f" (Exp. {expedicao_selecionada.title()})"
        else:
            # Se "Todas" estiver selecionado, não adiciona nada sobre a expedição ao título
            titulo_expedicao = ""

        # Parte do título que mostra o período
        if mes_selecionado != 'Todos':
            titulo_periodo = f" - {mes_selecionado.title()}"
        else:
            start_date_fmt = start_date.strftime('%d/%m/%Y')
            end_date_fmt = end_date.strftime('%d/%m/%Y')
            titulo_periodo = f" | Período: {start_date_fmt} a {end_date_fmt}"
            
        # Combina todas as partes para o título final
        titulo_dinamico = f"{titulo_base}{titulo_expedicao}{titulo_periodo}"


        # 4. CRIAÇÃO DO GRÁFICO DE COLUNAS VERTICAIS
        if not ranking_df.empty:
            ranking_df['TextoFormatado'] = ranking_df[coluna_dados].apply(lambda x: f"{x:,.0f}".replace(",", "."))

            fig_colunas = px.bar(
                ranking_df,
                x='Usuário',
                y=coluna_dados,
                color='Usuário',
                title=titulo_dinamico,
                text='TextoFormatado',
                labels={
                    coluna_dados: f"Total de {tipo_ranking}",
                    "Usuário": "Usuário"
                },
                # --- ADICIONE CUSTOM_DATA AQUI ---
                custom_data=['TextoFormatado']
            )

            fig_colunas.update_traces(
                texttemplate='%{text}',
                textposition='outside',
                textfont_size=16,
                hovertemplate=(
                    "<b>👤 Usuário:</b> %{x}<br>"
                    "<b>📊 Total:</b> %{customdata}<extra></extra>"
                )
            )

            fig_colunas.update_layout(
                height=700,
                xaxis_title="Usuário",
                yaxis_title=f"Total de {tipo_ranking}",
                showlegend=True,
                yaxis=dict(range=[0, ranking_df[coluna_dados].max() * 1.2]),
                xaxis=dict(
                    tickfont=dict(size=14)
                ),
                # 🔹 AQUI VOCÊ CONTROLA O TOOLTIP
                hoverlabel=dict(
                    font_size=14,   # << aumenta o tamanho da fonte
                    font_family="Arial"  # opcional: muda a fonte
                )
            )



            st.plotly_chart(fig_colunas, use_container_width=True)
        else:
            st.info(f"Não há dados de '{tipo_ranking}' para exibir com os filtros aplicados.")
        # --- FIM DO BLOCO UNIFICADO ---



                # --- INÍCIO DO GRÁFICO DE COLUNAS EMPILHADAS POR EXPEDIÇÃO ---

        # 1. PREPARAR OS DADOS
        # Agrupa os dados por Expedição e Usuário para somar as emissões.
        # Usamos df_tab3, que já respeita os filtros da interface (data, mês, etc.).
        # O filtro de expedição da sidebar também já foi aplicado em df_tab3.
        dados_agrupados = df_tab3.groupby(['EXPEDIÇÃO', 'USUÁRIO'])['CTRC_EMITIDO'].sum().reset_index()

        # 2. LÓGICA PARA O TÍTULO DINÂMICO
        # Parte do título que mostra a expedição
        if expedicao_selecionada != 'Todas':
            titulo_expedicao = f" (Exp. {expedicao_selecionada.title()})"
        else:
            titulo_expedicao = ""

        # Parte do título que mostra o período
        if mes_selecionado != 'Todos':
            titulo_periodo = f" - {mes_selecionado.title()}"
        else:
            start_date_fmt = start_date.strftime('%d/%m/%Y')
            end_date_fmt = end_date.strftime('%d/%m/%Y')
            titulo_periodo = f" | Período: {start_date_fmt} a {end_date_fmt}"
            
        # Combina as partes para o título final
        titulo_dinamico = f"Emissões por Usuário em cada Expedição{titulo_expedicao}{titulo_periodo}"

        # --- INÍCIO DO NOVO GRÁFICO DE PERFORMANCE VS. MÉDIA ---
        st.subheader("🚀 Performance Individual vs. Média da Equipe")
        st.markdown("Análise do total de emissões de cada usuário em comparação com a média geral do período.")

        # 1. PREPARAR OS DADOS
        # Agrupa por usuário e calcula o total de emissões
        df_performance = df_tab3.groupby('USUÁRIO')['CTRC_EMITIDO'].sum().reset_index()
        df_performance.rename(columns={'CTRC_EMITIDO': 'Total Emissões'}, inplace=True)

        # 2. CALCULAR A MÉDIA
        if not df_performance.empty:
            media_geral = df_performance['Total Emissões'].mean()
        else:
            media_geral = 0

        # 3. DEFINIR CORES COM BASE NA MÉDIA
        # Cria uma coluna 'Cor' que será 'Acima da Média' ou 'Abaixo da Média'
        if media_geral > 0:
            df_performance['Cor'] = df_performance['Total Emissões'].apply(
                lambda x: 'Acima da Média' if x >= media_geral else 'Abaixo da Média'
            )
        else:
            df_performance['Cor'] = 'Sem dados'

        # Ordena os dados do maior para o menor para melhor visualização
        df_performance = df_performance.sort_values(by='Total Emissões', ascending=False)

        # 4. LÓGICA PARA O TÍTULO DINÂMICO
        if expedicao_selecionada != 'Todas':
            titulo_expedicao = f" (Exp. {expedicao_selecionada.title()})"
        else:
            titulo_expedicao = ""

        if mes_selecionado != 'Todos':
            titulo_periodo = f" - {mes_selecionado.title()}"
        else:
            start_date_fmt = start_date.strftime('%d/%m/%Y')
            end_date_fmt = end_date.strftime('%d/%m/%Y')
            titulo_periodo = f" | Período: {start_date_fmt} a {end_date_fmt}"
            
        titulo_dinamico = f"Performance de Usuários vs. Média{titulo_expedicao}{titulo_periodo}"

        # 5. CRIAÇÃO DO GRÁFICO DE BARRAS COM LINHA DE MÉDIA
        if not df_performance.empty:
            # Formata os números para exibição
            df_performance['TextoFormatado'] = df_performance['Total Emissões'].apply(
                lambda x: f"{x:,.0f}".replace(",", ".")
            )

            # Adiciona coluna de ícone (🔵 para acima / 🔴 para abaixo da média)
            df_performance['Icone'] = df_performance['Cor'].apply(
                lambda x: "🔵" if x == "Acima da Média" else "🔴"
            )

            fig_barras_media = px.bar(
                df_performance,
                x='USUÁRIO',
                y='Total Emissões',
                title=titulo_dinamico,
                text='TextoFormatado',
                color='Cor',  # Usa a coluna 'Cor' para definir a cor das barras
                color_discrete_map={  # Mapeia os valores da coluna 'Cor' para cores reais
                    'Acima da Média': "#1814cb",  # Azul para acima da média
                    'Abaixo da Média': "#a31d1d"  # Vermelho para abaixo da média
                },
                labels={
                    "USUÁRIO": "Usuário",
                    "Total Emissões": "Total de Emissões"
                },
                custom_data=['TextoFormatado', 'Cor', 'Icone']  # 🔹 controla o que aparece no tooltip
            )

            # Adiciona a linha horizontal da média
            fig_barras_media.add_hline(
                y=media_geral,
                line_dash="dash",
                line_color="orange",
                line_width=1.5,
                annotation_text=f"Média: {media_geral:,.0f}".replace(",", "."),
                annotation_position="top right",
                annotation_font_size=16,
                annotation_font_color="orange"
            )

            # Ajusta rótulos de valores nas barras
            fig_barras_media.update_traces(
                textposition='outside',
                textfont_size=16,
                hovertemplate=(
                    "%{customdata[2]} <b>%{customdata[1]}</b><br>"
                    "👤 <b>Usuário:</b> %{x}<br>"
                    "📊 <b>Total:</b> %{customdata[0]}<extra></extra>"
                )
            )

            # Layout do gráfico
            fig_barras_media.update_layout(
                height=700,
                xaxis_title="Usuário",
                yaxis_title="Total de Emissões",
                legend_title="Performance",
                yaxis=dict(range=[0, df_performance['Total Emissões'].max() * 1.2]),
                xaxis=dict(
                    tickfont=dict(size=14)
                ),
                hoverlabel=dict(
                    font_size=14,
                    font_family="Arial"
                )
            )

            st.plotly_chart(fig_barras_media, use_container_width=True)

        else:
            st.info("Não há dados de emissões para gerar a análise de performance.")
        # --- FIM DO NOVO GRÁFICO DE PERFORMANCE VS. MÉDIA ---



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
            cancelamentos_semanais = cancelamentos_tab4.groupby(cancelamentos_tab4["DATA_CANCELADO"].dt.to_period("W")).size()
            media_semanal_cancelamentos = cancelamentos_semanais.mean()

            # Média Mensal de Cancelamentos
            cancelamentos_mensais = cancelamentos_tab4.groupby(cancelamentos_tab4["DATA_CANCELADO"].dt.to_period("M")).size()
            media_mensal_cancelamentos = cancelamentos_mensais.mean()

            # Usuário com Mais Cancelamentos
            usuario_mais_cancelamentos = cancelamentos_tab4["USUARIO"].value_counts().idxmax()
            qtd_usuario_mais_cancelamentos = cancelamentos_tab4["USUARIO"].value_counts().max()

            # Motivo de Cancelamento Mais Comum
            motivo_mais_comum = cancelamentos_tab4["MOTIVO"].value_counts().idxmax()
            qtd_motivo_mais_comum = cancelamentos_tab4["MOTIVO"].value_counts().max()


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

        # Gráfico de Evolução da Taxa de Cancelamento
        st.subheader(f"📈 Evolução da Taxa de Cancelamento vs Meta ({ano_selecionado})")

        # Filtrar dados para o ano selecionado
        ano_atual = ano_selecionado
        emissoes_ano_atual = df_tab4[df_tab4['DATA_EMISSÃO'].dt.year == ano_atual].copy()
        cancelamentos_ano_atual = cancelamentos_tab4[cancelamentos_tab4['DATA_CANCELADO'].dt.year == ano_atual].copy()

        if not emissoes_ano_atual.empty and not cancelamentos_ano_atual.empty:
            emissoes_mensais = emissoes_ano_atual.groupby(emissoes_ano_atual['DATA_EMISSÃO'].dt.to_period('M'))['CTRC_EMITIDO'].sum()
            cancelamentos_mensais = cancelamentos_ano_atual.groupby(cancelamentos_ano_atual['DATA_CANCELADO'].dt.to_period('M')).size()

            meses_ano = pd.period_range(start=f'{ano_atual}-01', end=f'{ano_atual}-12', freq='M')
            df_evolucao = pd.DataFrame(index=meses_ano)
            df_evolucao['Emissoes'] = emissoes_mensais.reindex(meses_ano, fill_value=0)

            # Força denominadores fixos (jan–ago) APENAS na visão geral
            if usuario_selecionado == "Todos" and expedicao_selecionada == "Todas":
                for nome_mes, valor in EMISSOES_FIXAS_MES.items():
                    pos = MESES_MAP[nome_mes] - 1
                    if 0 <= pos < len(df_evolucao):
                        df_evolucao.iloc[pos, df_evolucao.columns.get_loc('Emissoes')] = valor

            df_evolucao['Cancelamentos'] = cancelamentos_mensais.reindex(meses_ano, fill_value=0)
            df_evolucao['Taxa_Cancelamento'] = (df_evolucao['Cancelamentos'] / df_evolucao['Emissoes'] * 100).fillna(0)
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
            motivos_cancelamento_usuario = cancelamentos_tab4[cancelamentos_tab4["USUARIO"].str.strip() == usuario_selecionado.strip()]["MOTIVO"].value_counts().head(5).reset_index()
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

            # ==================================================================
            # CÓDIGO CORRIGIDO E COMPLETO PARA A ABA "DADOS DETALHADOS" (tab5)
            # ==================================================================

            with tab5:

                # Criar cópias dos dataframes filtrados globalmente
                df_tab5 = df_filtrado.copy()
                cancelamentos_tab5 = cancelamentos_filtrado.copy()

                # --- INÍCIO DA CORREÇÃO PARA LARGURA TOTAL ---

                # 2. Usar o option_menu diretamente na página (sem with col2:)
                # Seletor de tipo de dados com o novo visual e ícones
                tipo_dados = option_menu(
                    menu_title=None,
                    options=["Emissões", "Cancelamentos"],
                    # ✅ --- ÍCONES ATUALIZADOS PARA CORRESPONDER À IMAGEM --- ✅
                    icons=['box-arrow-up-right', 'box-seam-fill'],
                    menu_icon="cast",
                    default_index=0,
                    orientation="horizontal",
                    key="seletor_dados_detalhados_v2", # Chave única
                    styles={
                        # ✅ --- CSS ATUALIZADO PARA O NOVO VISUAL --- ✅
                        # O contêiner geral que envolve os botões
                        "container": {
                            "padding": "5px !important",
                            "background-color": "#0f172a", # Fundo escuro do container
                            "border-radius": "12px",
                            "border": "1px solid #334155"
                        },
                        # Ícone de cada botão
                        "icon": {
                            "color": "#f1f5f9", # Ícone branco
                            "font-size": "18px",
                            "vertical-align": "middle",
                        },
                        # Estilo de cada botão (link de navegação) QUANDO NÃO SELECIONADO
                        "nav-link": {
                            "font-size": "16px",
                            "text-align": "center",
                            "margin": "0px",
                            "padding": "10px 0px",
                            "border-radius": "10px",
                            "flex-grow": "1",
                            "color": "#9CA3AF", # Cor cinza para o texto
                            "background-color": "transparent", # Fundo transparente
                            "--hover-color": "#334155", # Cor ao passar o mouse
                        },
                        # Estilo do botão QUANDO ESTÁ SELECIONADO
                        "nav-link-selected": {
                            # Gradiente sutil ou cor sólida para um visual premium
                            "background": "linear-gradient(135deg, #1e40af, #3b82f6)",
                            "color": "white", # Texto branco
                            "font-weight": "bold",
                            "box-shadow": "inset 0 1px 2px rgba(0,0,0,0.2)",
                        },
                    }
                )

                # --- FIM DA CORREÇÃO ---

                # Escolhe o DataFrame com base no tipo
                if tipo_dados == "Emissões":
                    df_exibicao_original = df_tab5.copy()
                    col_data = "DATA_EMISSÃO"
                    col_usuario = "USUÁRIO"
                    col_exp = "EXPEDIÇÃO"
                    col_valor = "CTRC_EMITIDO"
                    opcoes_grafico = ["USUÁRIO", "EXPEDIÇÃO", "MÊS"]
                else:  # Cancelamentos
                    df_exibicao_original = cancelamentos_tab5.copy()
                    col_data = "DATA_CANCELADO"
                    col_usuario = "USUARIO"
                    col_exp = "EXPEDIÇÃO"
                    col_valor = None
                    opcoes_grafico = ["USUARIO", "EXPEDIÇÃO", "MOTIVO", "MÊS"]

                # ====== FILTROS AVANÇADOS ======
                st.subheader("🔍 Filtros Avançados")
                col1, col2, col3 = st.columns(3)

                with col1:
                    busca = st.text_input("Busca por texto (Usuário, Expedição ou Motivo):", key="busca_detalhada").strip().lower()
                with col2:
                    # Garante que as opções de filtro não quebrem se o dataframe estiver vazio
                    opcoes_usuario_filtro = ["Todos"] + sorted(df_exibicao_original[col_usuario].unique().tolist()) if not df_exibicao_original.empty else ["Todos"]
                    filtro_usuario = st.selectbox(
                        "Filtrar por Usuário:",
                        opcoes_usuario_filtro, key="filtro_usuario_tab5"
                    )
                with col3:
                    opcoes_exp_filtro = ["Todos"] + sorted(df_exibicao_original[col_exp].unique().tolist()) if not df_exibicao_original.empty else ["Todos"]
                    filtro_exp = st.selectbox(
                        "Filtrar por Expedição:",
                        opcoes_exp_filtro, key="filtro_exp_tab5"
                    )

                # Aplica filtros
                df_exibicao = df_exibicao_original.copy()
                if busca:
                    mask = df_exibicao.apply(lambda row: row.astype(str).str.lower().str.contains(busca).any(), axis=1)
                    df_exibicao = df_exibicao[mask]
                if filtro_usuario != "Todos":
                    df_exibicao = df_exibicao[df_exibicao[col_usuario] == filtro_usuario]
                if filtro_exp != "Todos":
                    df_exibicao = df_exibicao[df_exibicao[col_exp] == filtro_exp]

                # ====== INDICADORES RESUMIDOS ======
                st.markdown("### 📊 Indicadores Resumidos")
                col1_kpi, col2_kpi, col3_kpi, col4_kpi = st.columns(4)

                if not df_exibicao.empty:
                    total_registros_filtrados = len(df_exibicao)
                    total_valores_filtrados = df_exibicao[col_valor].sum() if col_valor else len(df_exibicao)
                    periodo_str = f"{df_exibicao[col_data].min().strftime('%d/%m/%Y')} - {df_exibicao[col_data].max().strftime('%d/%m/%Y')}"
                    usuarios_unicos_filtrados = df_exibicao[col_usuario].nunique()

                    with col1_kpi:
                        st.metric("Total Registros", f"{total_registros_filtrados:,}".replace(",", "."))
                    with col2_kpi:
                        st.metric(f"Total {tipo_dados}", f"{total_valores_filtrados:,}".replace(",", "."))
                    with col3_kpi:
                        st.metric("Período", periodo_str)
                    with col4_kpi:
                        st.metric("Usuários Únicos", usuarios_unicos_filtrados)
                else:
                    with col1_kpi: st.metric("Total Registros", "0")
                    with col2_kpi: st.metric(f"Total {tipo_dados}", "0")
                    with col3_kpi: st.metric("Período", "N/A")
                    with col4_kpi: st.metric("Usuários Únicos", "0")

                # A PARTIR DAQUI, TUDO DEPENDE DE df_exibicao NÃO ESTAR VAZIO
                if not df_exibicao.empty:
                    
                    # ====== TABELA DE DADOS PRINCIPAL ======
                    st.markdown("### 📋 Tabela de Dados")
                    st.write(f"Mostrando todos os {len(df_exibicao)} registros filtrados.")
                    df_para_mostrar = df_exibicao.copy()
                    if col_data in df_para_mostrar.columns:
                        df_para_mostrar[col_data] = pd.to_datetime(df_para_mostrar[col_data]).dt.strftime('%d-%m-%Y')
                    if col_valor and col_valor in df_para_mostrar.columns:
                        df_para_mostrar[col_valor] = df_para_mostrar[col_valor].astype(str)
                    st.dataframe(df_para_mostrar, use_container_width=True, hide_index=True)

                    # ====== DOWNLOAD DOS DADOS PRINCIPAIS ======
                    st.markdown("### 💾 Download dos Dados")
                    csv = df_exibicao.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="📥 Baixar dados filtrados (CSV)",
                        data=csv,
                        file_name=f"{tipo_dados.lower()}_filtrados_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv"
                    )
                    
                  # ====== GRÁFICO DINÂMICO E TABELA DE SETORES ======
                    # (Dentro de with tab5, após a seção de download)

                    # ...

                    # ====== GRÁFICO DINÂMICO E TABELA DE SETORES ======
                    st.markdown("---")

                    titulo_grafico = "📈 Análise Gráfica dos Dados Filtrados"
                    if filtro_usuario != "Todos":
                        titulo_grafico += f" - {filtro_usuario}"
                    if filtro_exp != "Todos":
                        titulo_grafico += f" | {filtro_exp}"

                    st.markdown(f"<h3 style='text-align: center;'>{titulo_grafico}</h3>", unsafe_allow_html=True)

                    default_index = 0
                    if tipo_dados == "Cancelamentos" and "MOTIVO" in opcoes_grafico:
                        default_index = opcoes_grafico.index("MOTIVO")

                    # ✅ --- ESTE É O BLOCO DE CÓDIGO ATUALIZADO --- ✅
                    coluna_para_grafico = option_menu(
                        menu_title=None,
                        options=opcoes_grafico, # Suas opções: ["USUÁRIO", "EXPEDIÇÃO", "MÊS", etc.]
                        
                        # Ícones atualizados para um visual mais profissional
                        icons=['people-fill', 'truck', 'calendar-month-fill', 'tag-fill'], # Adicionei um ícone extra para "MOTIVO"
                        
                        menu_icon="bar-chart-steps",
                        default_index=default_index,
                        orientation="horizontal",
                        key="seletor_analise_grafica", # Chave única
                        styles={
                            # O contêiner geral que envolve os botões
                            "container": {
                                "padding": "5px !important",
                                "background-color": "#0f172a",
                                "border-radius": "12px",
                                "border": "1px solid #334155",
                                "margin-bottom": "25px" # Adiciona um espaço abaixo do seletor
                            },
                            # Ícone de cada botão
                            "icon": {
                                "color": "#f1f5f9",
                                "font-size": "18px",
                                "vertical-align": "middle",
                            },
                            # Estilo do botão (link) QUANDO NÃO SELECIONADO
                            "nav-link": {
                                "font-family": "Roboto, sans-serif", # Fonte melhorada
                                "font-weight": "500",
                                "font-size": "16px",
                                "text-align": "center",
                                "margin": "0px 4px", # Pequeno espaço entre os botões
                                "padding": "10px 0px",
                                "border-radius": "10px",
                                "flex-grow": "1",
                                "color": "#9CA3AF",
                                "background-color": "transparent",
                                "--hover-color": "#334155",
                            },
                            # Estilo do botão QUANDO ESTÁ SELECIONADO
                            "nav-link-selected": {
                                "font-family": "Roboto, sans-serif", # Fonte melhorada
                                "font-weight": "700", # Negrito
                                "background": "linear-gradient(135deg, #1e40af, #3b82f6)",
                                "color": "white",
                                "box-shadow": "inset 0 1px 2px rgba(0,0,0,0.2)",
                            },
                        }
                    )

                    # ... (o resto do código para gerar o gráfico continua aqui)


                    # Define o eixo Y e o título com base no tipo de dados
                    if tipo_dados == "Emissões":
                        dados_grafico = df_exibicao.groupby(coluna_para_grafico)[col_valor].sum().reset_index()
                        eixo_y = col_valor
                        titulo_grafico = f"Total de Emissões por {coluna_para_grafico.title()}"
                    else: # Cancelamentos
                        dados_grafico = df_exibicao[coluna_para_grafico].value_counts().reset_index()
                        dados_grafico.columns = [coluna_para_grafico, 'Quantidade']
                        eixo_y = 'Quantidade'
                        titulo_grafico = f"Total de Cancelamentos por {coluna_para_grafico.title()}"

                    # --- LÓGICA DE ORDENAÇÃO E COR ---
                    if coluna_para_grafico == 'MÊS':
                        meses_ordem_cronologica = [
                            'JANEIRO', 'FEVEREIRO', 'MARÇO', 'ABRIL', 'MAIO', 'JUNHO', 
                            'JULHO', 'AGOSTO', 'SETEMBRO', 'OUTUBRO', 'NOVEMBRO', 'DEZEMBRO'
                        ]
                        # Converte para categoria para ordenar corretamente
                        dados_grafico['MÊS'] = pd.Categorical(dados_grafico['MÊS'], categories=meses_ordem_cronologica, ordered=True)
                        dados_grafico = dados_grafico.sort_values('MÊS')
                        
                        # Cria uma coluna numérica para a ordem e a usa para a cor
                        dados_grafico['ordem_cor'] = range(len(dados_grafico))
                        coluna_cor = 'ordem_cor' 
                        
                    else:
                        # Mantém a ordenação e coloração por valor para outras categorias
                        dados_grafico = dados_grafico.sort_values(by=eixo_y, ascending=False)
                        coluna_cor = eixo_y # Colore pelo valor numérico

                    dados_grafico = dados_grafico.head(15)

                    # Formata o texto da barra com ponto
                    dados_grafico['TextoFormatado'] = dados_grafico[eixo_y].apply(lambda x: f"{x:,.0f}".replace(",", "."))

                    fig_detalhada = px.bar(
                        dados_grafico,
                        x=coluna_para_grafico,
                        y=eixo_y,
                        title=titulo_grafico,
                        text='TextoFormatado',
                        color=coluna_cor,
                        color_continuous_scale=px.colors.sequential.Oranges if tipo_dados == "Emissões" else px.colors.sequential.Reds
                    )

                    fig_detalhada.update_traces(
                        textposition='outside', 
                        texttemplate='%{text}',
                        textfont_size=16
                    )

                    # --- LÓGICA FINAL PARA O LAYOUT DO GRÁFICO ---

                    # Formata a legenda de cores (será usada quando a barra for visível)
                    min_val = dados_grafico[eixo_y].min()
                    max_val = dados_grafico[eixo_y].max()
                    tick_values = np.linspace(min_val, max_val, num=5, dtype=int)
                    tick_texts = [f"{val:,.0f}".replace(",", ".") for val in tick_values]

                    # Define se a barra de legenda deve ser mostrada
                    mostrar_legenda_cor = True
                    if coluna_para_grafico == 'MÊS':
                        mostrar_legenda_cor = False

                    fig_detalhada.update_layout(
                        height=700,
                        xaxis_title=coluna_para_grafico.title(),
                        yaxis_title=f"Total de {tipo_dados}",
                        showlegend=False,
                        
                        # Usa a variável para mostrar ou esconder a barra dinamicamente
                        coloraxis_showscale=mostrar_legenda_cor, 
                        
                        yaxis=dict(range=[0, dados_grafico[eixo_y].max() * 1.25]),
                        # Garante que a ordem do eixo X seja a mesma do DataFrame
                        xaxis={'categoryorder':'array', 'categoryarray': dados_grafico[coluna_para_grafico]},
                        
                        # Mantém a formatação da barra, que será aplicada quando ela for visível
                        coloraxis_colorbar=dict(
                            title=f"Total de {tipo_dados}",
                            tickvals=tick_values,
                            ticktext=tick_texts
                        )
                    )

                    st.plotly_chart(fig_detalhada, use_container_width=True)


                    dados_grafico = dados_grafico.head(15)

                    # ==================================================================
                    # FUNÇÃO DE MAPEAMENTO DE SETOR (v11 - COM PRIORIDADE MÁXIMA PARA "EXP")
                    # ==================================================================
                    def mapear_setor(motivo):
                        """
                        Classifica um motivo de cancelamento em um setor específico, garantindo
                        que motivos iniciados com "EXP" sejam sempre do setor EXPEDIÇÃO.
                        """
                        # Normaliza o texto para garantir consistência na comparação
                        motivo_upper = str(motivo).upper().strip()

                        # --- REGRAS DE ALTA PRIORIDADE (VERIFICADAS PRIMEIRO) ---

                        # ✅ 1. REGRA MÁXIMA: EXPEDIÇÃO (por prefixo)
                        # Garante que qualquer motivo que comece com "EXP" ou "EXPEDICAO"
                        # seja classificado como EXPEDIÇÃO, antes de qualquer outra regra.
                        if motivo_upper.startswith("EXPEDICAO") or motivo_upper.startswith("EXP"):
                            return "EXPEDIÇÃO"

                        # 2. COMERCIAL
                        keywords_comercial = [
                            "VALOR NAO COERENTE COM A COTACAO",
                            "AGUARDANDO DESBLOQUEIO TRATATIVA CO",
                            "COMERCIAL"
                        ]
                        if any(keyword in motivo_upper for keyword in keywords_comercial):
                            return "COMERCIAL"

                        # 3. CTE COMPLEMENTAR
                        if "COMPLEMENTAR" in motivo_upper:
                            return "EXPEDIÇÃO"

                        # 4. OPERACIONAL (por palavra-chave prioritária)
                        if "OPERACIONAL" in motivo_upper or "OPE" in motivo_upper:
                            return "OPERACIONAL"

                        # 5. SEFAZ (por rejeição)
                        if "REJEITADA" in motivo_upper:
                            return "SEFAZ"

                        # --- REGRAS SECUNDÁRIAS (CONTINUAM COMO ANTES) ---

                        # 6. CLIENTE
                        keywords_cliente = [
                            "NAO VEIO MERCADORIA CONFORME", "CLIENTE CANCELOU", "CLIENTE RECUSOU",
                            "CLIENTE PEDIU CANCELAMENTO", "CANCELADO A PEDIDO DO CLIENTE", "PEDIDO DO CLIENTE",
                            "SAO 2 VOL FALTANTES", "MERCADORIA VEIO INVERTIDA CONFORME", "MERCADORIA   BATE COM A NOTA",
                            "NAO VEIO MERCADORIA CONF VITINHO", "REPRESENTANTE VIRA TIRAR MERCADORIA",
                            "NAO ATENDEMOS AGENDAMENTO PARA SOLI", "BINHO TRANSPORTES MANDOU QUANTIDADE",
                            "CANCELAMENTO VOLUME NAO VEIO", "CANCELAMENTO VAI DEVOLVER PRA SOLIS", "NAO VEIO VOL CONF CUAN",
                            "DEVOLUCAO PRO REMETENTE CIDADE NAO", "NAO TRANSPORTA MAIS PERECIVEIS PRA",
                            "NAO VEIO MERCADORIA, VEIO SOMENTE A", "VOLUME NAO IDENTIFICADO CONF OLIVER", "CLIENTE"
                        ]
                        if any(keyword in motivo_upper for keyword in keywords_cliente):
                            return "CLIENTE"

                        # 7. EDI
                        keywords_edi = [
                            "EMITIDO NA OPCAO INCORRETA VIA MANI", "EMITIDO NA OPCAO INCORRETA",
                            "NAO DEVERIA SER EMITIDO COMO RPS", "QUANTIDADE INCORRETA VIA EDI",
                            "FALTOU ARQUIVO DE NOTA", "FALTOU USAR ARQUIVO DHL", "ARQUIVO EDI."
                        ]
                        if any(keyword in motivo_upper for keyword in keywords_edi):
                            return "EDI"

                        # 8. OPERACIONAL (motivos específicos adicionais)
                        keywords_operacional_especifico = [
                            "MARQUINHOS PEDIU CANCELAR", "VOLTOU ALTERACAO DE CUBAGENS APOS V",
                            "ENCONTRADO 6 VOLUMES NA MATRIZ, VAI"
                        ]
                        if any(keyword in motivo_upper for keyword in keywords_operacional_especifico):
                            return "OPERACIONAL"

                        # 9. SEFAZ (outros motivos)
                        keywords_sefaz = [
                            "PROBLEMA NO SSW NAO GERA IMPRESSAO", "EMITIDO VIA MANIFESTO INCORRETAMENT",
                            "EMITIDO INCORRETAMENTE VIA MANIFEST", "SEFAZ"
                        ]
                        if any(keyword in motivo_upper for keyword in keywords_sefaz):
                            return "SEFAZ"

                        # 10. COLETA
                        if motivo_upper.startswith("COLETA"):
                            return "COLETA"

                        # --- REGRA FINAL E PADRÃO ---

                        # 11. Se nenhuma regra corresponder, classifica como EXPEDIÇÃO por padrão.
                        return "EXPEDIÇÃO"



                    # --- TABELA DE DADOS FILTRADA POR SETOR ---
                    if tipo_dados == "Cancelamentos":
                        st.markdown("---")
                        # Título já centralizado para manter a consistência
                        st.markdown("<h3 style='text-align: center;'>📋 Tabela por Setores de Cancelamentos</h3>", unsafe_allow_html=True)

                        df_com_setor_tabela = df_exibicao.copy()
                        df_com_setor_tabela['SETOR'] = df_com_setor_tabela['MOTIVO'].apply(mapear_setor)

                        # ======================= INÍCIO DA ATUALIZAÇÃO =======================
                        # 1. Dicionário de ícones (usando nomes da biblioteca Bootstrap Icons)
                        icones_setor_bootstrap = {
                            "EXPEDIÇÃO": "truck",
                            "SEFAZ": "bank",
                            "COLETA": "box-seam",
                            "CLIENTE": "person",
                            "OPERACIONAL": "gear",
                            "EDI": "pc-display-horizontal",
                            "COMERCIAL": "telephone"
                        }

                        # Prepara as listas de opções e ícones para o menu
                        setores_disponiveis = sorted(df_com_setor_tabela['SETOR'].unique())
                        opcoes_menu_setor = ["Todos"] + setores_disponiveis
                        icones_menu_setor = ["collection-fill"] + [icones_setor_bootstrap.get(setor, "question-circle") for setor in setores_disponiveis]

                        # ✅ --- ESTE É O BLOCO ATUALIZADO --- ✅
                        setor_selecionado = option_menu(
                            menu_title=None,
                            options=opcoes_menu_setor,
                            icons=icones_menu_setor,
                            menu_icon="filter-square-fill",
                            default_index=0,
                            orientation="horizontal",
                            key="seletor_setores_cancelamento", # Chave única
                            styles={
                                "container": {"padding": "0!important", "background-color": "transparent", "margin-bottom": "25px"},
                                "icon": {"color": "#f1f5f9", "font-size": "16px"},
                                
                                # --- AJUSTE PRINCIPAL AQUI ---
                                "nav-link": {
                                    "font-family": "Roboto, sans-serif",
                                    "font-size": "14px",
                                    "text-align": "center",
                                    "margin": "0px 4px",
                                    "--hover-color": "#334155",
                                    "border-radius": "10px",
                                    "padding": "8px 12px",
                                    "background-color": "#1e293b", # <-- MUDANÇA: Fundo sólido para botões não selecionados
                                },
                                
                                "nav-link-selected": {
                                    "font-family": "Roboto, sans-serif",
                                    "background-color": "#a31d1d", # Cor vermelha para o selecionado
                                    "font-weight": "bold",
                                    "color": "white",
                                },
                            }
                        )
                        # ======================== FIM DA ATUALIZAÇÃO =========================

                        # Filtra o DataFrame diretamente com o valor retornado pelo option_menu
                        if setor_selecionado != "Todos":
                            df_tabela_setor = df_com_setor_tabela[df_com_setor_tabela['SETOR'] == setor_selecionado]
                        else:
                            df_tabela_setor = df_com_setor_tabela

                        # O resto do seu código para exibir a tabela e o botão de download permanece o mesmo
                        if not df_tabela_setor.empty:
                            st.write(f"Mostrando {len(df_tabela_setor)} registros para o setor '{setor_selecionado}'.")
                            
                            df_tabela_setor_display = df_tabela_setor.copy()
                            df_tabela_setor_display['DATA_CANCELADO'] = pd.to_datetime(df_tabela_setor_display['DATA_CANCELADO']).dt.strftime('%d-%m-%Y')

                            st.dataframe(
                                df_tabela_setor_display[['REMETENTE', 'CTRC_CANCELADOS', 'MÊS', 'DATA_CANCELADO', 'EXPEDIÇÃO', 'USUARIO', 'MOTIVO', 'SETOR']],
                                use_container_width=True,
                                hide_index=True
                            )

                            csv_setor = df_tabela_setor.to_csv(index=False).encode('utf-8')
                            st.download_button(
                            label="📥 Baixar dados do setor (CSV)",
                            data=csv_setor,
                            file_name=f"cancelamentos_setor_{setor_selecionado.lower()}_{datetime.now().strftime('%Y%m%d')}.csv",
                            mime="text/csv",
                            key="download_setor_button"
                            )
                        else:
                            st.info(f"Nenhum cancelamento encontrado para o setor '{setor_selecionado}' com os filtros atuais.")


                   # --- GRÁFICO DE PIZZA POR SETOR ---
                    if tipo_dados == "Cancelamentos" and coluna_para_grafico == "MOTIVO":
                        st.markdown("---")

                        # Monta o título dinâmico
                        titulo_setor = "### 📊 Análise de Cancelamentos por Setor"
                        if filtro_usuario != "Todos":
                            titulo_setor += f" - {filtro_usuario}"
                        if filtro_exp != "Todos":
                            titulo_setor += f" | {filtro_exp}"

                        st.markdown(titulo_setor)

                        df_com_setor_pizza = df_exibicao.copy()
                        df_com_setor_pizza['SETOR'] = df_com_setor_pizza['MOTIVO'].apply(mapear_setor)

                        dados_pizza = df_com_setor_pizza['SETOR'].value_counts().reset_index()
                        dados_pizza.columns = ['Setor', 'Quantidade']

                        # 🔹 Mapeamento de ícones por setor
                        icones_setor = {
                            "EXPEDIÇÃO": "🚚",
                            "SEFAZ": "🏛️",
                            "COLETA": "📦",
                            "CLIENTE": "👤",
                            "OPERACIONAL": "⚙️",
                            "EDI": "💻",
                            "COMERCIAL": "📞"
                        }
                        dados_pizza["ICON"] = dados_pizza["Setor"].map(icones_setor).fillna("❓")

                        cores_setores = ["#1F77B4", "#FF7F0E", "#2CA02C", "#9467BD"]

                        fig_pizza_setor = px.pie(
                            dados_pizza,
                            names='Setor',
                            values='Quantidade',
                            hole=0.4,
                            color_discrete_sequence=cores_setores
                        )

                        # Texto fora das fatias + Tooltip customizado com ícones
                        fig_pizza_setor.update_traces(
                            textposition='outside',
                            texttemplate='%{label}<br>%{percent:.2%}',
                            textfont=dict(size=18),  # 👈 cor será ajustada abaixo
                            pull=[0.05 if i == 0 else 0 for i in range(len(dados_pizza))],
                            hovertemplate='<b>%{customdata[0]} %{label}</b><br>' +
                                        '📦 Quantidade: %{value:,}<br>' +
                                        '📊 Percentual: %{percent:.2%}<extra></extra>',
                            customdata=np.stack([dados_pizza["ICON"]], axis=-1)
                        )

                        # 🔹 Ajusta a cor dos textos para a mesma das fatias
                        fig_pizza_setor.for_each_trace(
                            lambda t: t.update(textfont=dict(size=18, color=t.marker.colors))
                        )

                        # Número total no centro
                        total_cancelamentos = dados_pizza['Quantidade'].sum()
                        fig_pizza_setor.add_annotation(
                            dict(
                                text=f"<span style='font-size:34px; font-weight:bold;'>{total_cancelamentos}</span>"
                                    f"<br><span style='font-size:6px;'>&nbsp;</span><br>"
                                    f"<span style='font-size:16px;'>Cancelamentos</span>",
                                x=0.5, y=0.5,
                                font=dict(color="white"),
                                showarrow=False
                            )
                        )

                        # Ajusta a legenda e ADICIONA A CONFIGURAÇÃO DO TOOLTIP
                        fig_pizza_setor.update_layout(
                            height=800,
                            margin=dict(t=150, b=50, l=50, r=50),
                            
                            # ✅✅✅ INÍCIO DA ALTERAÇÃO ✅✅✅
                            hoverlabel=dict(
                                bgcolor="white",        # Cor de fundo da caixa do tooltip (branco)
                                font_size=16,           # Tamanho da fonte do texto (aumentado)
                                font_family="Verdana",  # Fonte do texto (opcional)
                                font_color="black"      # Cor do texto (preto para contrastar com o fundo branco)
                            ),
                            # ✅✅✅ FIM DA ALTERAÇÃO ✅✅✅

                            legend=dict(
                                title=dict(
                                    text="Setores",
                                    font=dict(size=20, color="white")
                                ),
                                font=dict(size=18, color="white"),
                                orientation="v",
                                yanchor="top",
                                y=0.9,
                                xanchor="left",
                                x=1.02
                            )
                        )

                        st.plotly_chart(fig_pizza_setor, use_container_width=True)

                else:
                    st.warning("Nenhum dado para exibir com os filtros globais aplicados.")

if __name__ == "__main__":
    main()