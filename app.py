import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime, date
import io
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
import base64
import time

# --- НАСТРОЙКИ СТРАНИЦЫ ---
st.set_page_config(
    page_title="Компьютерный клуб - Смена",
    page_icon="🎮",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- КАСТОМНЫЙ CSS (Футуристичный дизайн) ---
st.markdown("""
<style>
    /* Общий фон */
    .stApp {
        background: linear-gradient(135deg, #0a0a1a 0%, #1a0a2e 50%, #0a0a1a 100%);
    }
    
    /* Заголовки */
    h1, h2, h3 {
        background: linear-gradient(90deg, #00d4ff, #7b2ffc);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 700 !important;
    }
    
    /* Карточки */
    .css-1r6slb0, .css-1v3fvcr, .stAlert, .stInfo {
        background: rgba(255, 255, 255, 0.05) !important;
        backdrop-filter: blur(10px) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 20px !important;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3) !important;
    }
    
    /* Кнопки */
    .stButton > button {
        background: linear-gradient(135deg, #00d4ff, #7b2ffc) !important;
        color: white !important;
        border: none !important;
        border-radius: 50px !important;
        padding: 10px 25px !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(0, 212, 255, 0.3) !important;
    }
    
    .stButton > button:hover {
        transform: scale(1.05) !important;
        box-shadow: 0 8px 25px rgba(123, 47, 252, 0.5) !important;
    }
    
    /* Метрики */
    .stMetric {
        background: rgba(255, 255, 255, 0.05) !important;
        backdrop-filter: blur(10px) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 15px !important;
        padding: 15px !important;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2) !important;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: rgba(255, 255, 255, 0.05);
        border-radius: 50px;
        padding: 5px;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 50px;
        padding: 10px 25px;
        color: #888;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background: linear-gradient(135deg, #00d4ff, #7b2ffc);
        color: white;
    }
    
    /* Инпуты */
    .stNumberInput input, .stTextInput input, .stTextArea textarea {
        background: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 10px !important;
        color: white !important;
    }
    
    /* Чекбоксы */
    .stCheckbox label {
        color: white !important;
    }
    
    /* Датафреймы */
    .stDataFrame {
        background: rgba(255, 255, 255, 0.05) !important;
        border-radius: 15px !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
    }
    
    /* Кастомные контейнеры */
    .glass-card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px;
        padding: 20px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
    }
    
    .neon-text {
        text-shadow: 0 0 10px #00d4ff, 0 0 20px #7b2ffc;
    }
    
    .divider {
        background: linear-gradient(90deg, transparent, #00d4ff, #7b2ffc, transparent);
        height: 2px;
        margin: 20px 0;
    }
</style>
""", unsafe_allow_html=True)

# --- ПОДКЛЮЧЕНИЕ К БАЗЕ ДАННЫХ ---
def init_db():
    conn = sqlite3.connect('club_data.db')
    c = conn.cursor()
    
    # Продажи Фуди
    c.execute('''CREATE TABLE IF NOT EXISTS sales_food
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  date TEXT,
                  product TEXT,
                  quantity INTEGER,
                  price REAL)''')
    
    # Продажи Бара
    c.execute('''CREATE TABLE IF NOT EXISTS sales_bar
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  date TEXT,
                  product TEXT,
                  quantity INTEGER,
                  price REAL DEFAULT 0)''')
    
    # Остатки Фуди
    c.execute('''CREATE TABLE IF NOT EXISTS food_remaining
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  date TEXT,
                  product TEXT,
                  remaining INTEGER)''')
    
    # Состояние ПК
    c.execute('''CREATE TABLE IF NOT EXISTS pc_status
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  date TEXT,
                  pc_number INTEGER,
                  status TEXT,
                  note TEXT)''')
    
    # Игры
    c.execute('''CREATE TABLE IF NOT EXISTS games
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT UNIQUE,
                  updated BOOLEAN,
                  last_check TEXT)''')
    
    # Итоги смены
    c.execute('''CREATE TABLE IF NOT EXISTS shift_totals
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  date TEXT,
                  terminal REAL,
                  cash REAL,
                  pc_rent REAL,
                  extras REAL,
                  food_total REAL,
                  bar_total REAL,
                  salary_today REAL,
                  salary_to_account REAL,
                  cash_taken REAL,
                  remaining_cash REAL)''')
    
    # Накопления ЗП
    c.execute('''CREATE TABLE IF NOT EXISTS salary_accumulation
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  date TEXT,
                  amount REAL,
                  total_accumulated REAL)''')
    
    conn.commit()
    conn.close()

init_db()

# --- СПИСКИ ТОВАРОВ ---
FOOD_PRODUCTS = {
    "Бургер": 80,
    "Картошка фри": 80,
    "Нагетсы": 80,
    "Мини-чебуречки": 80,
    "Хот-дог 2х": 80,
    "Хот-дог": 75,
    "Соус": 10
}

BAR_PRODUCTS = {
    "Pepsi 0,5л": 25,
    "Pepsi 0,33л": 20,
    "Pepsi 0,33л ж/б": 22,
    "Карпатська жерельна 0,5л": 18,
    "Battery 0,33л ж/б": 22,
    "Battery 0,5л ж/б": 25,
    "Battery 0,5л ж/б с соком": 28,
    "Ситро 0,5л ж/б": 20,
    "Дюшес 0,5л ж/б": 20,
    "Квас Тарас 0,5л ж/б": 22,
    "Shwepps 0,33": 20,
    "Coca-Cola/Fanta/Sprite 0,33": 20,
    "Салфетки обычные": 10,
    "Флинт 60 г": 30,
    "Флинт Гренки 55 г": 28,
    "Hroom 50 г": 32,
    "Big bob 60 г": 30,
    "Флинт с Соусом 65 г": 35,
    "Chipsters чипси 60 г": 28
}

GAMES_LIST = [
    "League of Legends",
    "Legends of Runeterra",
    "Dota 2",
    "CS2",
    "Dota Underlords",
    "Apex Legends",
    "PUBG: BATTLEGROUNDS",
    "Arena Breakout: Infinite",
    "Roblox",
    "Minecraft",
    "World of Tanks",
    "World of Warships",
    "Hearthstone",
    "World of Warcraft / WoW Classic",
    "Fortnite",
    "War Thunder",
    "Warcraft III: The Frozen Throne / ICCup Launcher"
]

PC_NUMBERS = list(range(7, 21))

# --- ФУНКЦИИ ДЛЯ РАБОТЫ С БАЗОЙ ---

def get_today():
    return date.today().isoformat()

# ФУДИ
def add_food_sale(product, quantity=1):
    conn = sqlite3.connect('club_data.db')
    c = conn.cursor()
    price = FOOD_PRODUCTS[product]
    c.execute("INSERT INTO sales_food (date, product, quantity, price) VALUES (?, ?, ?, ?)",
              (get_today(), product, quantity, price))
    conn.commit()
    conn.close()

def get_food_sales_today():
    conn = sqlite3.connect('club_data.db')
    df = pd.read_sql_query(f"SELECT product, SUM(quantity) as total_qty, price FROM sales_food WHERE date='{get_today()}' GROUP BY product", conn)
    conn.close()
    return df

def get_food_total_today():
    conn = sqlite3.connect('club_data.db')
    df = pd.read_sql_query(f"SELECT SUM(quantity * price) as total FROM sales_food WHERE date='{get_today()}'", conn)
    conn.close()
    return df['total'][0] if not df.empty and df['total'][0] else 0

def save_food_remaining(rem_dict):
    conn = sqlite3.connect('club_data.db')
    c = conn.cursor()
    today = get_today()
    for product, rem in rem_dict.items():
        c.execute("INSERT INTO food_remaining (date, product, remaining) VALUES (?, ?, ?)",
                  (today, product, rem))
    conn.commit()
    conn.close()

def get_food_remaining_today():
    conn = sqlite3.connect('club_data.db')
    df = pd.read_sql_query(f"SELECT product, remaining FROM food_remaining WHERE date='{get_today()}'", conn)
    conn.close()
    return df

# БАР (как Фуд-корт)
def add_bar_sale(product, quantity=1):
    conn = sqlite3.connect('club_data.db')
    c = conn.cursor()
    price = BAR_PRODUCTS[product]
    c.execute("INSERT INTO sales_bar (date, product, quantity, price) VALUES (?, ?, ?, ?)",
              (get_today(), product, quantity, price))
    conn.commit()
    conn.close()

def get_bar_sales_today():
    conn = sqlite3.connect('club_data.db')
    df = pd.read_sql_query(f"SELECT product, SUM(quantity) as total_qty, price FROM sales_bar WHERE date='{get_today()}' GROUP BY product", conn)
    conn.close()
    return df

def get_bar_total_today():
    conn = sqlite3.connect('club_data.db')
    df = pd.read_sql_query(f"SELECT SUM(quantity * price) as total FROM sales_bar WHERE date='{get_today()}'", conn)
    conn.close()
    return df['total'][0] if not df.empty and df['total'][0] else 0

# ПК
def save_pc_status(pc_num, status, note):
    conn = sqlite3.connect('club_data.db')
    c = conn.cursor()
    c.execute("INSERT INTO pc_status (date, pc_number, status, note) VALUES (?, ?, ?, ?)",
              (get_today(), pc_num, status, note))
    conn.commit()
    conn.close()

def get_pc_status_today():
    conn = sqlite3.connect('club_data.db')
    df = pd.read_sql_query(f"SELECT * FROM pc_status WHERE date='{get_today()}'", conn)
    conn.close()
    return df

# ИГРЫ
def init_games():
    conn = sqlite3.connect('club_data.db')
    c = conn.cursor()
    for game in GAMES_LIST:
        c.execute("INSERT OR IGNORE INTO games (name, updated, last_check) VALUES (?, ?, ?)",
                  (game, False, ''))
    conn.commit()
    conn.close()

def update_game_status(game_name, updated):
    conn = sqlite3.connect('club_data.db')
    c = conn.cursor()
    c.execute("UPDATE games SET updated=?, last_check=? WHERE name=?",
              (updated, get_today(), game_name))
    conn.commit()
    conn.close()

def get_games_status():
    conn = sqlite3.connect('club_data.db')
    df = pd.read_sql_query("SELECT * FROM games ORDER BY name", conn)
    conn.close()
    return df

# ЗП И НАКОПЛЕНИЯ
def get_salary_accumulation():
    conn = sqlite3.connect('club_data.db')
    df = pd.read_sql_query("SELECT SUM(amount) as total FROM salary_accumulation", conn)
    conn.close()
    return df['total'][0] if not df.empty and df['total'][0] else 0

def add_salary_accumulation(amount):
    conn = sqlite3.connect('club_data.db')
    c = conn.cursor()
    total = get_salary_accumulation() + amount
    c.execute("INSERT INTO salary_accumulation (date, amount, total_accumulated) VALUES (?, ?, ?)",
              (get_today(), amount, total))
    conn.commit()
    conn.close()

def get_daily_salary_accumulation():
    conn = sqlite3.connect('club_data.db')
    df = pd.read_sql_query(f"SELECT * FROM salary_accumulation WHERE date='{get_today()}'", conn)
    conn.close()
    return df

# ИТОГИ СМЕНЫ
def save_shift_totals(terminal, cash, pc_rent, extras, food_total, bar_total, salary_today, salary_to_account, cash_taken, remaining_cash):
    conn = sqlite3.connect('club_data.db')
    c = conn.cursor()
    c.execute("INSERT INTO shift_totals (date, terminal, cash, pc_rent, extras, food_total, bar_total, salary_today, salary_to_account, cash_taken, remaining_cash) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
              (get_today(), terminal, cash, pc_rent, extras, food_total, bar_total, salary_today, salary_to_account, cash_taken, remaining_cash))
    conn.commit()
    conn.close()

def get_shift_totals_today():
    conn = sqlite3.connect('club_data.db')
    df = pd.read_sql_query(f"SELECT * FROM shift_totals WHERE date='{get_today()}' ORDER BY id DESC LIMIT 1", conn)
    conn.close()
    return df

# --- ФУНКЦИЯ ДЛЯ СОЗДАНИЯ PDF ---
def generate_pdf_report():
    today = get_today()
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=20, leftMargin=20, topMargin=20, bottomMargin=20)
    styles = getSampleStyleSheet()
    style_title = ParagraphStyle('CustomTitle', parent=styles['Heading1'], fontSize=18, alignment=TA_CENTER, spaceAfter=20, textColor=colors.HexColor('#00d4ff'))
    style_header = ParagraphStyle('CustomHeader', parent=styles['Heading2'], fontSize=14, spaceAfter=10, textColor=colors.HexColor('#7b2ffc'))
    style_normal = styles['Normal']
    
    elements = []
    
    # Заголовок
    elements.append(Paragraph(f"🎮 Отчет по смене от {today}", style_title))
    elements.append(Spacer(1, 10))
    
    # 1. Продажи Фуди
    elements.append(Paragraph("🍔 1. Продажи Фуд-корта", style_header))
    food_df = get_food_sales_today()
    if not food_df.empty:
        food_data = [["Товар", "Кол-во", "Цена", "Сумма"]]
        for _, row in food_df.iterrows():
            food_data.append([row['product'], row['total_qty'], f"{row['price']:.0f} грн", f"{row['total_qty'] * row['price']:.0f} грн"])
        food_data.append(["", "", "ИТОГО:", f"{get_food_total_today():.0f} грн"])
        table = Table(food_data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#00d4ff')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -2), colors.HexColor('#f0f0f0')),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(table)
    else:
        elements.append(Paragraph("Продаж за сегодня нет", style_normal))
    
    elements.append(Spacer(1, 10))
    
    # 2. Продажи Бара
    elements.append(Paragraph("🍫 2. Продажи Бара", style_header))
    bar_df = get_bar_sales_today()
    if not bar_df.empty:
        bar_data = [["Товар", "Кол-во", "Цена", "Сумма"]]
        for _, row in bar_df.iterrows():
            bar_data.append([row['product'], row['total_qty'], f"{row['price']:.0f} грн", f"{row['total_qty'] * row['price']:.0f} грн"])
        bar_data.append(["", "", "ИТОГО:", f"{get_bar_total_today():.0f} грн"])
        table = Table(bar_data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#7b2ffc')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -2), colors.HexColor('#f0f0f0')),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(table)
    else:
        elements.append(Paragraph("Продаж за сегодня нет", style_normal))
    
    elements.append(Spacer(1, 10))
    
    # 3. Остатки Фуди
    elements.append(Paragraph("📦 3. Остатки Фуд-корта", style_header))
    rem_df = get_food_remaining_today()
    if not rem_df.empty:
        rem_data = [["Товар", "Остаток"]]
        for _, row in rem_df.iterrows():
            rem_data.append([row['product'], row['remaining']])
        table = Table(rem_data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#00d4ff')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(table)
    else:
        elements.append(Paragraph("Остатки не введены", style_normal))
    
    elements.append(Spacer(1, 10))
    
    # 4. ПК
    elements.append(Paragraph("🖥️ 4. Состояние компьютеров", style_header))
    pc_df = get_pc_status_today()
    if not pc_df.empty:
        pc_data = [["№ ПК", "Статус", "Заметка"]]
        for _, row in pc_df.iterrows():
            pc_data.append([row['pc_number'], row['status'], row['note'] or "-"])
        table = Table(pc_data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#00d4ff')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(table)
    else:
        elements.append(Paragraph("Статусы ПК не заполнены", style_normal))
    
    elements.append(Spacer(1, 10))
    
    # 5. Игры
    elements.append(Paragraph("🎮 5. Обновление игр", style_header))
    games_df = get_games_status()
    if not games_df.empty:
        games_data = [["Игра", "Обновлено", "Дата проверки"]]
        for _, row in games_df.iterrows():
            status = "✅" if row['updated'] else "❌"
            games_data.append([row['name'], status, row['last_check'] or "-"])
        table = Table(games_data, colWidths=[120, 50, 80])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#00d4ff')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(table)
    else:
        elements.append(Paragraph("Список игр не загружен", style_normal))
    
    elements.append(Spacer(1, 10))
    
    # 6. Финансовый итог
    elements.append(Paragraph("💰 6. Финансовый итог смены", style_header))
    shift_df = get_shift_totals_today()
    if not shift_df.empty:
        row = shift_df.iloc[0]
        total_cash = row['terminal'] + row['cash'] + row['pc_rent'] + row['extras'] + row['food_total'] + row['bar_total']
        
        fin_data = [
            ["Статья", "Сумма (грн)"],
            ["Терминал (безнал)", f"{row['terminal']:.0f}"],
            ["Наличные", f"{row['cash']:.0f}"],
            ["Аренда ПК", f"{row['pc_rent']:.0f}"],
            ["Допы (печать и т.д.)", f"{row['extras']:.0f}"],
            ["Фуд-корт (выручка)", f"{row['food_total']:.0f}"],
            ["Бар (выручка)", f"{row['bar_total']:.0f}"],
            ["", ""],
            ["ОБЩАЯ КАССА", f"{total_cash:.0f}"],
            ["Заработано за день", f"{row['salary_today']:.0f}"],
            ["Забрал сейчас (наличкой)", f"{row['cash_taken']:.0f}"],
            ["Отложено к 9 числу", f"{row['salary_to_account']:.0f}"],
            ["", ""],
            ["ИТОГОВЫЙ ОСТАТОК", f"{row['remaining_cash']:.0f}"]
        ]
        table = Table(fin_data, colWidths=[150, 100])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#7b2ffc')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('BACKGROUND', (-2, -2), (-1, -1), colors.HexColor('#00ff88'))
        ]))
        elements.append(table)
        
        # Накопления к 9 числу
        total_accumulated = get_salary_accumulation()
        elements.append(Spacer(1, 10))
        elements.append(Paragraph(f"💰 Накопления к 9 числу: {total_accumulated:.0f} грн", style_header))
    else:
        elements.append(Paragraph("Финансовый итог не подведен", style_normal))
    
    doc.build(elements)
    buffer.seek(0)
    return buffer

# --- ИНТЕРФЕЙС STREAMLIT ---

# Шапка с анимацией
st.markdown("""
<div style="text-align: center; padding: 20px 0;">
    <h1 style="font-size: 48px; background: linear-gradient(90deg, #00d4ff, #7b2ffc); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
        🎮 КОМПЬЮТЕРНЫЙ КЛУБ
    </h1>
    <p style="color: #888; font-size: 18px; letter-spacing: 2px;">
        УПРАВЛЕНИЕ СМЕНОЙ • ФУТУРИСТИЧНЫЙ ДАШБОРД
    </p>
    <div class="divider"></div>
</div>
""", unsafe_allow_html=True)

st.markdown(f"<p style='text-align: right; color: #666;'>📅 {get_today()}</p>", unsafe_allow_html=True)

# Накопления ЗП (видны всегда сверху)
total_accumulated = get_salary_accumulation()
st.markdown(f"""
<div style="background: linear-gradient(135deg, rgba(0, 212, 255, 0.1), rgba(123, 47, 252, 0.1)); 
            border: 1px solid rgba(255,255,255,0.1); 
            border-radius: 15px; 
            padding: 15px 25px; 
            margin-bottom: 20px;
            text-align: center;">
    <span style="color: #888;">💰 НАКОПЛЕНИЯ К 9 ЧИСЛУ:</span>
    <span style="color: #00d4ff; font-size: 28px; font-weight: 700; margin-left: 15px;">
        {total_accumulated:.0f} грн
    </span>
</div>
""", unsafe_allow_html=True)

# Вкладки
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "🏠 Главная", 
    "🍔 Фуд-корт", 
    "🍫 Бар", 
    "🖥️ ПК", 
    "🎮 Игры",
    "💰 Финансы"
])

# --- ВКЛАДКА 1: ГЛАВНАЯ ---
with tab1:
    st.markdown("<h2 style='text-align: center;'>📊 ДАШБОРД СМЕНЫ</h2>", unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        food_total = get_food_total_today()
        st.metric("🍔 Фуд-корт", f"{food_total:.0f} грн")
    
    with col2:
        bar_total = get_bar_total_today()
        st.metric("🍫 Бар", f"{bar_total:.0f} грн")
    
    with col3:
        total = food_total + bar_total
        st.metric("💵 Общая выручка", f"{total:.0f} грн")
    
    with col4:
        st.metric("👤 Администратор", "Сегодня")
    
    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
    
    col5, col6 = st.columns(2)
    
    with col5:
        st.markdown("""
        <div class="glass-card">
            <h3>📌 Краткие итоги</h3>
        </div>
        """, unsafe_allow_html=True)
        
        shift_df = get_shift_totals_today()
        if not shift_df.empty:
            row = shift_df.iloc[0]
            total_cash = row['terminal'] + row['cash'] + row['pc_rent'] + row['extras'] + row['food_total'] + row['bar_total']
            st.write(f"💳 Терминал: **{row['terminal']:.0f} грн**")
            st.write(f"💵 Наличные: **{row['cash']:.0f} грн**")
            st.write(f"🖥️ Аренда ПК: **{row['pc_rent']:.0f} грн**")
            st.write(f"🖨️ Допы: **{row['extras']:.0f} грн**")
            st.write(f"🍔 Фуд-корт: **{row['food_total']:.0f} грн**")
            st.write(f"🍫 Бар: **{row['bar_total']:.0f} грн**")
            st.write(f"---")
            st.write(f"💰 Общая касса: **{total_cash:.0f} грн**")
            st.write(f"👤 Заработано за день: **{row['salary_today']:.0f} грн**")
            st.write(f"💸 Забрал сейчас: **{row['cash_taken']:.0f} грн**")
            st.write(f"🏦 Отложено к 9 числу: **{row['salary_to_account']:.0f} грн**")
            st.write(f"---")
            st.write(f"💵 Остаток в кассе: **{row['remaining_cash']:.0f} грн**")
        else:
            st.info("Смена еще не закрыта")
    
    with col6:
        st.markdown("""
        <div class="glass-card">
            <h3>📄 Отчеты</h3>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button