import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime, date
import io
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
import plotly.express as px

# --- НАСТРОЙКИ СТРАНИЦЫ ---
st.set_page_config(
    page_title="Компьютерный клуб - Смена",
    page_icon="🎮",
    layout="wide"
)

# --- КАСТОМНЫЙ CSS (СВЕТЛЫЙ ДИЗАЙН) ---
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 50%, #f5f7fa 100%);
    }
    
    /* Заголовки */
    h1 {
        background: linear-gradient(90deg, #667eea, #764ba2);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800 !important;
        font-size: 42px !important;
    }
    h2, h3 {
        color: #2d3748 !important;
        font-weight: 700 !important;
    }
    
    /* Карточки */
    .css-1r6slb0, .css-1v3fvcr, .stAlert, .stInfo, .stSuccess {
        background: rgba(255, 255, 255, 0.85) !important;
        backdrop-filter: blur(10px) !important;
        border-radius: 20px !important;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.08) !important;
        border: 1px solid rgba(255, 255, 255, 0.3) !important;
        padding: 20px !important;
    }
    
    /* Кнопки */
    .stButton > button {
        background: linear-gradient(135deg, #667eea, #764ba2) !important;
        color: white !important;
        border: none !important;
        border-radius: 50px !important;
        padding: 12px 30px !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3) !important;
    }
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.5) !important;
    }
    
    /* Метрики */
    .stMetric {
        background: white !important;
        border-radius: 15px !important;
        padding: 15px !important;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.06) !important;
        border: 1px solid rgba(102, 126, 234, 0.1) !important;
    }
    .stMetric label {
        color: #4a5568 !important;
        font-weight: 600 !important;
    }
    .stMetric .stMetricValue {
        color: #2d3748 !important;
        font-size: 28px !important;
        font-weight: 700 !important;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: rgba(255, 255, 255, 0.7);
        border-radius: 50px;
        padding: 5px;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 50px;
        padding: 10px 25px;
        color: #4a5568 !important;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white !important;
    }
    
    /* Инпуты */
    .stNumberInput input, .stTextInput input, .stTextArea textarea {
        background: white !important;
        border: 2px solid #e2e8f0 !important;
        border-radius: 10px !important;
        color: #2d3748 !important;
        padding: 10px !important;
    }
    .stNumberInput input:focus, .stTextInput input:focus {
        border-color: #667eea !important;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1) !important;
    }
    
    /* Чекбоксы */
    .stCheckbox label {
        color: #2d3748 !important;
        font-weight: 500 !important;
    }
    
    /* Датафреймы */
    .stDataFrame {
        background: white !important;
        border-radius: 15px !important;
        border: 1px solid #e2e8f0 !important;
        padding: 10px !important;
    }
    
    /* Делитель */
    .divider {
        background: linear-gradient(90deg, transparent, #667eea, #764ba2, transparent);
        height: 3px;
        margin: 30px 0;
        border-radius: 10px;
    }
    
    /* Кастомные карточки */
    .glass-card {
        background: rgba(255, 255, 255, 0.85);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        padding: 25px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.08);
        border: 1px solid rgba(255, 255, 255, 0.3);
    }
    
    .gradient-text {
        background: linear-gradient(90deg, #667eea, #764ba2);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
</style>
""", unsafe_allow_html=True)

# --- БАЗА ДАННЫХ ---
def init_db():
    conn = sqlite3.connect('club_data.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS sales_food
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  date TEXT, product TEXT, quantity INTEGER, price REAL)''')
    c.execute('''CREATE TABLE IF NOT EXISTS sales_bar
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  date TEXT, product TEXT, quantity INTEGER, price REAL)''')
    c.execute('''CREATE TABLE IF NOT EXISTS food_remaining
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  date TEXT, product TEXT, remaining INTEGER)''')
    c.execute('''CREATE TABLE IF NOT EXISTS bar_stock
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  date TEXT, product TEXT, start_stock INTEGER, actual_stock INTEGER, sold INTEGER)''')
    c.execute('''CREATE TABLE IF NOT EXISTS pc_status
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  date TEXT, pc_number INTEGER, status TEXT, note TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS games
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT UNIQUE, updated BOOLEAN, last_check TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS shift_totals
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  date TEXT, terminal REAL, cash REAL, pc_rent REAL,
                  extras REAL, food_total REAL, bar_total REAL,
                  food_incassation REAL, salary_today REAL, 
                  salary_to_account REAL, cash_taken REAL, remaining_cash REAL)''')
    c.execute('''CREATE TABLE IF NOT EXISTS salary_accumulation
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  date TEXT, amount REAL, total_accumulated REAL)''')
    conn.commit()
    conn.close()

init_db()

# --- СПИСКИ ---
FOOD_PRODUCTS = {
    "Бургер": 80, "Картошка фри": 80, "Нагетсы": 80,
    "Мини-чебуречки": 80, "Хот-дог 2х": 80,
    "Хот-дог": 75, "Соус": 10
}

BAR_PRODUCTS = {
    "Pepsi 0,5л": 25, "Pepsi 0,33л": 20, "Pepsi 0,33л ж/б": 22,
    "Карпатська жерельна 0,5л": 18, "Battery 0,33л ж/б": 22,
    "Battery 0,5л ж/б": 25, "Battery 0,5л ж/б с соком": 28,
    "Ситро 0,5л ж/б": 20, "Дюшес 0,5л ж/б": 20,
    "Квас Тарас 0,5л ж/б": 22, "Shwepps 0,33": 20,
    "Coca-Cola/Fanta/Sprite 0,33": 20, "Салфетки обычные": 10,
    "Флинт 60 г": 30, "Флинт Гренки 55 г": 28,
    "Hroom 50 г": 32, "Big bob 60 г": 30,
    "Флинт с Соусом 65 г": 35, "Chipsters чипси 60 г": 28
}

GAMES_LIST = [
    "League of Legends", "Legends of Runeterra", "Dota 2", "CS2",
    "Dota Underlords", "Apex Legends", "PUBG: BATTLEGROUNDS",
    "Arena Breakout: Infinite", "Roblox", "Minecraft",
    "World of Tanks", "World of Warships", "Hearthstone",
    "World of Warcraft / WoW Classic", "Fortnite", "War Thunder",
    "Warcraft III: The Frozen Throne / ICCup Launcher"
]

PC_NUMBERS = list(range(7, 21))

# --- ФУНКЦИИ ---
def get_today():
    return date.today().isoformat()

# ФУДИ
def add_food_sale(product):
    conn = sqlite3.connect('club_data.db')
    c = conn.cursor()
    price = FOOD_PRODUCTS[product]
    c.execute("INSERT INTO sales_food (date, product, quantity, price) VALUES (?, ?, ?, ?)",
              (get_today(), product, 1, price))
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
    c.execute("DELETE FROM food_remaining WHERE date=?", (today,))
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

# БАР
def add_bar_sale(product):
    conn = sqlite3.connect('club_data.db')
    c = conn.cursor()
    price = BAR_PRODUCTS[product]
    c.execute("INSERT INTO sales_bar (date, product, quantity, price) VALUES (?, ?, ?, ?)",
              (get_today(), product, 1, price))
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

def save_bar_stock(start_dict, actual_dict):
    conn = sqlite3.connect('club_data.db')
    c = conn.cursor()
    today = get_today()
    c.execute("DELETE FROM bar_stock WHERE date=?", (today,))
    for product in BAR_PRODUCTS:
        start = start_dict.get(product, 0)
        actual = actual_dict.get(product, 0)
        sold = start - actual
        c.execute("INSERT INTO bar_stock (date, product, start_stock, actual_stock, sold) VALUES (?, ?, ?, ?, ?)",
                  (today, product, start, actual, sold))
    conn.commit()
    conn.close()

def get_bar_stock_today():
    conn = sqlite3.connect('club_data.db')
    df = pd.read_sql_query(f"SELECT * FROM bar_stock WHERE date='{get_today()}'", conn)
    conn.close()
    return df

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

# ЗП
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

# ИТОГИ
def save_shift_totals(terminal, cash, pc_rent, extras, food_total, bar_total, food_incassation, salary_today, salary_to_account, cash_taken, remaining_cash):
    conn = sqlite3.connect('club_data.db')
    c = conn.cursor()
    c.execute("INSERT INTO shift_totals (date, terminal, cash, pc_rent, extras, food_total, bar_total, food_incassation, salary_today, salary_to_account, cash_taken, remaining_cash) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
              (get_today(), terminal, cash, pc_rent, extras, food_total, bar_total, food_incassation, salary_today, salary_to_account, cash_taken, remaining_cash))
    conn.commit()
    conn.close()

def get_shift_totals_today():
    conn = sqlite3.connect('club_data.db')
    df = pd.read_sql_query(f"SELECT * FROM shift_totals WHERE date='{get_today()}' ORDER BY id DESC LIMIT 1", conn)
    conn.close()
    return df

def get_all_shifts():
    conn = sqlite3.connect('club_data.db')
    df = pd.read_sql_query("SELECT * FROM shift_totals ORDER BY date DESC", conn)
    conn.close()
    return df

def clear_day_data():
    today = get_today()
    conn = sqlite3.connect('club_data.db')
    c = conn.cursor()
    c.execute("DELETE FROM sales_food WHERE date=?", (today,))
    c.execute("DELETE FROM sales_bar WHERE date=?", (today,))
    c.execute("DELETE FROM food_remaining WHERE date=?", (today,))
    c.execute("DELETE FROM bar_stock WHERE date=?", (today,))
    c.execute("DELETE FROM pc_status WHERE date=?", (today,))
    c.execute("DELETE FROM shift_totals WHERE date=?", (today,))
    conn.commit()
    conn.close()

# --- PDF ---
def generate_pdf_report():
    today = get_today()
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=20, leftMargin=20, topMargin=20, bottomMargin=20)
    styles = getSampleStyleSheet()
    style_title = ParagraphStyle('CustomTitle', parent=styles['Heading1'], fontSize=18, alignment=TA_CENTER, spaceAfter=20, textColor=colors.HexColor('#667eea'))
    style_header = ParagraphStyle('CustomHeader', parent=styles['Heading2'], fontSize=14, spaceAfter=10, textColor=colors.HexColor('#764ba2'))
    style_normal = styles['Normal']
    
    elements = []
    elements.append(Paragraph(f"Отчет по смене от {today}", style_title))
    elements.append(Spacer(1, 10))
    
    # Фуди
    elements.append(Paragraph("1. Продажи Фуд-корта", style_header))
    food_df = get_food_sales_today()
    if not food_df.empty:
        food_data = [["Товар", "Кол-во", "Цена", "Сумма"]]
        for _, row in food_df.iterrows():
            food_data.append([row['product'], row['total_qty'], f"{row['price']:.0f} грн", f"{row['total_qty'] * row['price']:.0f} грн"])
        food_data.append(["", "", "ИТОГО:", f"{get_food_total_today():.0f} грн"])
        table = Table(food_data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(table)
    else:
        elements.append(Paragraph("Продаж за сегодня нет", style_normal))
    elements.append(Spacer(1, 10))
    
    # Бар
    elements.append(Paragraph("2. Продажи Бара", style_header))
    bar_df = get_bar_sales_today()
    if not bar_df.empty:
        bar_data = [["Товар", "Кол-во", "Цена", "Сумма"]]
        for _, row in bar_df.iterrows():
            bar_data.append([row['product'], row['total_qty'], f"{row['price']:.0f} грн", f"{row['total_qty'] * row['price']:.0f} грн"])
        bar_data.append(["", "", "ИТОГО:", f"{get_bar_total_today():.0f} грн"])
        table = Table(bar_data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#764ba2')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(table)
    else:
        elements.append(Paragraph("Продаж за сегодня нет", style_normal))
    elements.append(Spacer(1, 10))
    
    # Остатки
    elements.append(Paragraph("3. Остатки Фуд-корта", style_header))
    rem_df = get_food_remaining_today()
    if not rem_df.empty:
        rem_data = [["Товар", "Остаток"]]
        for _, row in rem_df.iterrows():
            rem_data.append([row['product'], row['remaining']])
        table = Table(rem_data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
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
    
    # Бар остатки
    elements.append(Paragraph("4. Остатки Бара", style_header))
    bar_stock = get_bar_stock_today()
    if not bar_stock.empty:
        stock_data = [["Товар", "Начало", "Продано", "Остаток"]]
        for _, row in bar_stock.iterrows():
            stock_data.append([row['product'], row['start_stock'], row['sold'], row['actual_stock']])
        table = Table(stock_data, colWidths=[80, 50, 50, 50])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#764ba2')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(table)
    else:
        elements.append(Paragraph("Остатки бара не введены", style_normal))
    elements.append(Spacer(1, 10))
    
    # ПК
    elements.append(Paragraph("5. Состояние компьютеров", style_header))
    pc_df = get_pc_status_today()
    if not pc_df.empty:
        pc_data = [["№ ПК", "Статус", "Заметка"]]
        for _, row in pc_df.iterrows():
            pc_data.append([row['pc_number'], row['status'], row['note'] or "-"])
        table = Table(pc_data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
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
    
    # Игры
    elements.append(Paragraph("6. Обновление игр", style_header))
    games_df = get_games_status()
    if not games_df.empty:
        games_data = [["Игра", "Обновлено", "Дата проверки"]]
        for _, row in games_df.iterrows():
            status = "✅" if row['updated'] else "❌"
            games_data.append([row['name'], status, row['last_check'] or "-"])
        table = Table(games_data, colWidths=[120, 50, 80])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
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
    
    # Финансы
    elements.append(Paragraph("7. Финансовый итог смены", style_header))
    shift_df = get_shift_totals_today()
    if not shift_df.empty:
        row = shift_df.iloc[0]
        total_cash = row['terminal'] + row['cash'] + row['pc_rent'] + row['extras'] + row['food_total'] + row['bar_total']
        fin_data = [
            ["Статья", "Сумма (грн)"],
            ["Терминал (безнал)", f"{row['terminal']:.0f}"],
            ["Наличные", f"{row['cash']:.0f}"],
            ["Аренда ПК", f"{row['pc_rent']:.0f}"],
            ["Допы", f"{row['extras']:.0f}"],
            ["Фуд-корт", f"{row['food_total']:.0f}"],
            ["Бар", f"{row['bar_total']:.0f}"],
            ["Инкассация Фуди", f"-{row['food_incassation']:.0f}"],
            ["", ""],
            ["ОБЩАЯ КАССА", f"{total_cash:.0f}"],
            ["Заработано за день", f"{row['salary_today']:.0f}"],
            ["Забрал сейчас", f"{row['cash_taken']:.0f}"],
            ["Отложено к 9 числу", f"{row['salary_to_account']:.0f}"],
            ["", ""],
            ["ИТОГОВЫЙ ОСТАТОК", f"{row['remaining_cash']:.0f}"]
        ]
        table = Table(fin_data, colWidths=[150, 100])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#764ba2')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('BACKGROUND', (-2, -2), (-1, -1), colors.HexColor('#48bb78'))
        ]))
        elements.append(table)
        total_accumulated = get_salary_accumulation()
        elements.append(Spacer(1, 10))
        elements.append(Paragraph(f"Накопления к 9 числу: {total_accumulated:.0f} грн", style_header))
    else:
        elements.append(Paragraph("Финансовый итог не подведен", style_normal))
    
    doc.build(elements)
    buffer.seek(0)
    return buffer

# --- ИНТЕРФЕЙС ---

# Шапка
st.markdown("""
<div style="text-align: center; padding: 30px 0 20px 0;">
    <h1>🎮 КОМПЬЮТЕРНЫЙ КЛУБ</h1>
    <p style="color: #4a5568; font-size: 18px; letter-spacing: 3px; margin-top: 5px;">
        УПРАВЛЕНИЕ СМЕНОЙ • ДАШБОРД
    </p>
    <div class="divider"></div>
</div>
""", unsafe_allow_html=True)

st.markdown(f"<p style='text-align: right; color: #718096;'>📅 {get_today()}</p>", unsafe_allow_html=True)

# Накопления ЗП
total_accumulated = get_salary_accumulation()
st.markdown(f"""
<div style="background: linear-gradient(135deg, rgba(102, 126, 234, 0.1), rgba(118, 75, 162, 0.1));
            border: 2px solid rgba(102, 126, 234, 0.2);
            border-radius: 15px;
            padding: 15px 25px;
            margin-bottom: 20px;
            text-align: center;">
    <span style="color: #4a5568; font-size: 16px; font-weight: 600;">💰 НАКОПЛЕНИЯ К 9 ЧИСЛУ:</span>
    <span style="color: #667eea; font-size: 30px; font-weight: 800; margin-left: 15px;">
        {total_accumulated:.0f} грн
    </span>
</div>
""", unsafe_allow_html=True)

# Кнопка новой смены
col_new1, col_new2, col_new3 = st.columns([1, 2, 1])
with col_new2:
    if st.button("🔄 НОВАЯ СМЕНА", use_container_width=True):
        clear_day_data()
        st.success("✅ Данные за сегодня очищены! Можно начинать новую смену.")
        st.rerun()

st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

# Вкладки
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "🏠 Главная", "🍔 Фуд-корт", "🍫 Бар", "🖥️ ПК", "🎮 Игры", "💰 Финансы", "📚 Архив"
])

# --- ГЛАВНАЯ ---
with tab1:
    st.markdown("<h2 style='text-align: center;'>📊 ДАШБОРД СМЕНЫ</h2>", unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("🍔 Фуд-корт", f"{get_food_total_today():.0f} грн")
    with col2:
        st.metric("🍫 Бар", f"{get_bar_total_today():.0f} грн")
    with col3:
        st.metric("💵 Общая выручка", f"{get_food_total_today() + get_bar_total_today():.0f} грн")
    with col4:
        st.metric("👤 Администратор", "Сегодня")
    
    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
    
    shift_df = get_shift_totals_today()
    if not shift_df.empty:
        row = shift_df.iloc[0]
        total_cash = row['terminal'] + row['cash'] + row['pc_rent'] + row['extras'] + row['food_total'] + row['bar_total']
        
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.subheader("📌 Итоги смены")
        col5, col6 = st.columns(2)
        with col5:
            st.write(f"💳 Терминал: **{row['terminal']:.0f} грн**")
            st.write(f"💵 Наличные: **{row['cash']:.0f} грн**")
            st.write(f"🖥️ Аренда ПК: **{row['pc_rent']:.0f} грн**")
            st.write(f"🖨️ Допы: **{row['extras']:.0f} грн**")
            st.write(f"🍔 Фуд-корт: **{row['food_total']:.0f} грн**")
        with col6:
            st.write(f"🍫 Бар: **{row['bar_total']:.0f} грн**")
            st.write(f"💰 Общая касса: **{total_cash:.0f} грн**")
            st.write(f"👤 Заработано: **{row['salary_today']:.0f} грн**")
            st.write(f"💸 Забрал сейчас: **{row['cash_taken']:.0f} грн**")
            st.write(f"🏦 Отложено: **{row['salary_to_account']:.0f} грн**")
            st.write(f"💵 Остаток в кассе: **{row['remaining_cash']:.0f} грн**")
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("ℹ️ Смена еще не закрыта. Перейдите во вкладку 'Финансы' для закрытия смены.")
    
    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
    
    # PDF
    if st.button("📥 Скачать PDF-отчет за сегодня", use_container_width=True):
        pdf_buffer = generate_pdf_report()
        st.download_button(
            label="✅ Сохранить PDF",
            data=pdf_buffer,
            file_name=f"отчет_{get_today()}.pdf",
            mime="application/pdf"
        )

# --- ФУД-КОРТ ---
with tab2:
    st.header("🍔 Фуд-корт")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("➕ Продажи")
        for product in FOOD_PRODUCTS:
            col_a, col_b = st.columns([3, 1])
            with col_a:
                st.write(f"{product} — {FOOD_PRODUCTS[product]} грн")
            with col_b:
                if st.button(f"+1", key=f"food_{product}"):
                    add_food_sale(product)
                    st.success(f"✅ {product} добавлен")
                    st.rerun()
    
    with col2:
        st.subheader("📊 Продажи сегодня")
        df = get_food_sales_today()
        if not df.empty:
            df['Сумма'] = df['total_qty'] * df['price']
            st.dataframe(df[['product', 'total_qty', 'price', 'Сумма']].rename(
                columns={'product': 'Товар', 'total_qty': 'Кол-во', 'price': 'Цена'}))
            st.metric("Общая выручка", f"{get_food_total_today():.0f} грн")
        else:
            st.info("Продаж пока нет")
    
    st.divider()
    
    # Инкассация
    st.subheader("💰 Инкассация Фуди")
    food_inc = st.number_input("Сумма инкассации (забрали из кассы Фуди)", min_value=0.0, step=50.0, format="%.0f")
    if st.button("✅ Сохранить инкассацию"):
        st.session_state['food_incassation'] = food_inc
        st.success(f"Инкассация сохранена: {food_inc:.0f} грн")
    
    st.divider()
    
    # Остатки
    st.subheader("📦 Остатки на конец дня")
    rem_cols = st.columns(3)
    rem_values = {}
    for i, product in enumerate(FOOD_PRODUCTS.keys()):
        with rem_cols[i % 3]:
            rem_values[product] = st.number_input(f"{product}", min_value=0, step=1, key=f"rem_{product}")
    if st.button("💾 Сохранить остатки"):
        save_food_remaining(rem_values)
        st.success("Остатки сохранены!")

# --- БАР ---
with tab3:
    st.header("🍫 Бар")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("➕ Продажи")
        for product in BAR_PRODUCTS:
            col_a, col_b = st.columns([3, 1])
            with col_a:
                st.write(f"{product} — {BAR_PRODUCTS[product]} грн")
            with col_b:
                if st.button(f"+1", key=f"bar_{product}"):
                    add_bar_sale(product)
                    st.success(f"✅ {product} добавлен")
                    st.rerun()
    
    with col2:
        st.subheader("📊 Продажи сегодня")
        df = get_bar_sales_today()
        if not df.empty:
            df['Сумма'] = df['total_qty'] * df['price']
            st.dataframe(df[['product', 'total_qty', 'price', 'Сумма']].rename(
                columns={'product': 'Товар', 'total_qty': 'Кол-во', 'price': 'Цена'}))
            st.metric("Общая выручка", f"{get_bar_total_today():.0f} грн")
        else:
            st.info("Продаж пока нет")
    
    st.divider()
    st.subheader("📦 Остатки бара")
    st.info("Введите начальные остатки (в начале смены) и фактические (в конце смены)")
    
    bar_stock_df = get_bar_stock_today()
    
    if bar_stock_df.empty:
        st.subheader("Начальные остатки")
        start_cols = st.columns(3)
        start_values = {}
        for i, product in enumerate(BAR_PRODUCTS):
            with start_cols[i % 3]:
                start_values[product] = st.number_input(f"{product}", min_value=0, step=1, key=f"start_{product}")
        
        if st.button("✅ Сохранить начальные остатки"):
            # Сохраняем с одинаковыми началом и фактическим
            conn = sqlite3.connect('club_data.db')
            c = conn.cursor()
            today = get_today()
            c.execute("DELETE FROM bar_stock WHERE date=?", (today,))
            for product in BAR_PRODUCTS:
                c.execute("INSERT INTO bar_stock (date, product, start_stock, actual_stock, sold) VALUES (?, ?, ?, ?, ?)",
                          (today, product, start_values[product], start_values[product], 0))
            conn.commit()
            conn.close()
            st.success("Начальные остатки сохранены!")
            st.rerun()
    else:
        # Показываем текущие и предлагаем ввести фактические
        st.subheader("Текущие данные")
        st.dataframe(bar_stock_df[['product', 'start_stock', 'sold']].rename(
            columns={'product': 'Товар', 'start_stock': 'Начало', 'sold': 'Продано по учету'}))
        
        st.subheader("Фактические остатки (введите в конце смены)")
        actual_cols = st.columns(3)
        actual_values = {}
        for i, product in enumerate(BAR_PRODUCTS):
            with actual_cols[i % 3]:
                default_val = bar_stock_df[bar_stock_df['product'] == product]['actual_stock'].iloc[0] if not bar_stock_df[bar_stock_df['product'] == product].empty else 0
                actual_values[product] = st.number_input(f"{product}", min_value=0, step=1, value=default_val, key=f"actual_{product}")
        
        if st.button("💾 Сохранить фактические остатки"):
            conn = sqlite3.connect('club_data.db')
            c = conn.cursor()
            today = get_today()
            for product in BAR_PRODUCTS:
                start = bar_stock_df[bar_stock_df['product'] == product]['start_stock'].iloc[0] if not bar_stock_df[bar_stock_df['product'] == product].empty else 0
                sold = start - actual_values[product]
                c.execute("UPDATE bar_stock SET actual_stock=?, sold=? WHERE date=? AND product=?",
                          (actual_values[product], sold, today, product))
            conn.commit()
            conn.close()
            st.success("Фактические остатки сохранены!")
            st.rerun()
        
        # Сверка
        st.subheader("🔍 Сверка остатков")
        check_df = bar_stock_df.copy()
        check_df['Расхождение'] = check_df['start_stock'] - check_df['actual_stock']
        for idx, row in check_df.iterrows():
            if row['Расхождение'] != row['sold']:
                check_df.loc[idx, 'Статус'] = '⚠️ Расхождение!'
            else:
                check_df.loc[idx, 'Статус'] = '✅ Ок'
        st.dataframe(check_df[['product', 'start_stock', 'actual_stock', 'sold', 'Статус']].rename(
            columns={'product': 'Товар', 'start_stock': 'Начало', 'actual_stock': 'Факт', 'sold': 'Продано'}))

# --- ПК ---
with tab4:
    st.header("🖥️ Состояние компьютеров")
    
    status_options = ["Работает отлично", "Проблема с наушниками", "Зависает", "Не включается", "Требуется перезагрузка", "Другое"]
    new_status = st.text_input("➕ Добавить свой статус")
    if new_status and st.button("Добавить статус"):
        status_options.append(new_status)
        st.success(f"Статус '{new_status}' добавлен!")
    
    st.divider()
    pc_cols = st.columns(5)
    for i, pc in enumerate(PC_NUMBERS):
        with pc_cols[i % 5]:
            with st.container(border=True):
                st.write(f"**ПК №{pc}**")
                status = st.selectbox("Статус", status_options, key=f"status_{pc}")
                note = st.text_area("Заметка", placeholder="Опишите проблему...", key=f"note_{pc}")
                if st.button(f"Сохранить №{pc}", key=f"save_{pc}"):
                    save_pc_status(pc, status, note)
                    st.success(f"✅ ПК №{pc} сохранен")
                    st.rerun()
    
    st.divider()
    pc_df = get_pc_status_today()
    if not pc_df.empty:
        st.dataframe(pc_df[['pc_number', 'status', 'note']].rename(
            columns={'pc_number': '№ ПК', 'status': 'Статус', 'note': 'Заметка'}))

# --- ИГРЫ ---
with tab5:
    st.header("🎮 Обновление игр")
    init_games()
    st.info("Отмечайте галочкой игры, которые обновлены и работают")
    
    games_df = get_games_status()
    game_cols = st.columns(3)
    for i, (_, row) in enumerate(games_df.iterrows()):
        with game_cols[i % 3]:
            with st.container(border=True):
                col_a, col_b = st.columns([4, 1])
                with col_a:
                    st.write(f"**{row['name']}**")
                    if row['last_check']:
                        st.caption(f"Проверка: {row['last_check']}")
                with col_b:
                    updated = st.checkbox("✅", value=bool(row['updated']), key=f"game_{row['name']}")
                    if updated != bool(row['updated']):
                        update_game_status(row['name'], updated)
                        st.rerun()

# --- ФИНАНСЫ ---
with tab6:
    st.header("💰 Финансовый итог смены")
    st.info("Заполните все суммы и нажмите 'Закрыть смену'")
    
    food_total = get_food_total_today()
    bar_total = get_bar_total_today()
    
    with st.form("shift_close"):
        col1, col2 = st.columns(2)
        with col1:
            terminal = st.number_input("💳 Терминал (безнал)", min_value=0.0, step=50.0, format="%.0f")
            cash = st.number_input("💵 Наличные", min_value=0.0, step=50.0, format="%.0f")
            pc_rent = st.number_input("🖥️ Аренда ПК", min_value=0.0, step=50.0, format="%.0f")
        with col2:
            extras = st.number_input("🖨️ Допы (печать и т.д.)", min_value=0.0, step=10.0, format="%.0f")
        
        # Инкассация из сессии
        food_inc = st.session_state.get('food_incassation', 0)
        st.write(f"💰 Инкассация Фуди: **{food_inc:.0f} грн** (указана во вкладке Фуд-корт)")
        
        total_cash = terminal + cash + pc_rent + extras + food_total + bar_total
        
        # Расчет ЗП
        if total_cash >= 1200:
            bonus = 100
            if total_cash >= 2000:
                bonus = 200
            salary_today = 400 + bonus
        else:
            salary_today = 400
        
        cash_taken = 200
        salary_to_account = salary_today - cash_taken
        if salary_to_account < 0:
            salary_to_account = 0
        
        remaining_cash = total_cash - salary_today - food_inc
        
        st.divider()
        st.markdown(f"""
        <div style="background: rgba(102, 126, 234, 0.1); padding: 20px; border-radius: 15px; border: 1px solid rgba(102, 126, 234, 0.2);">
            <h4>🧮 Расчет ЗП</h4>
            <p>🍔 Фуд-корт: <b>{food_total:.0f} грн</b></p>
            <p>🍫 Бар: <b>{bar_total:.0f} грн</b></p>
            <p>💰 Общая касса: <b>{total_cash:.0f} грн</b></p>
            <p>👤 Заработано за день: <b>{salary_today:.0f} грн</b> (ставка 400 + бонус)</p>
            <p style="color: #48bb78;">💸 Забираю сейчас (наличкой): <b>{cash_taken:.0f} грн</b></p>
            <p style="color: #ed8936;">🏦 Откладывается к 9 числу: <b>{salary_to_account:.0f} грн</b></p>
            <p style="color: #e53e3e;">💰 Инкассация Фуди: <b>-{food_inc:.0f} грн</b></p>
            <p>💵 Остаток в кассе: <b>{remaining_cash:.0f} грн</b></p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.form_submit_button("✅ Закрыть смену"):
            if total_cash > 0:
                if salary_to_account > 0:
                    add_salary_accumulation(salary_to_account)
                
                save_shift_totals(terminal, cash, pc_rent, extras, food_total, bar_total, food_inc, salary_today, salary_to_account, cash_taken, remaining_cash)
                st.success(f"✅ Смена закрыта! Заработано: {salary_today:.0f} грн, Забрал: {cash_taken:.0f} грн, Отложено: {salary_to_account:.0f} грн, Остаток: {remaining_cash:.0f} грн")
                st.balloons()
            else:
                st.error("Ошибка: общая касса не может быть 0")

# --- АРХИВ ---
with tab7:
    st.header("📚 Архив смен")
    
    all_shifts = get_all_shifts()
    if not all_shifts.empty:
        all_shifts['Общая касса'] = all_shifts['terminal'] + all_shifts['cash'] + all_shifts['pc_rent'] + all_shifts['extras'] + all_shifts['food_total'] + all_shifts['bar_total']
        all_shifts['Дата'] = all_shifts['date']
        
        display_cols = ['Дата', 'terminal', 'cash', 'pc_rent', 'extras', 'food_total', 'bar_total', 'food_incassation', 'salary_today', 'cash_taken', 'salary_to_account', 'remaining_cash', 'Общая касса']
        display_names = {
            'Дата': 'Дата',
            'terminal': 'Терминал',
            'cash': 'Наличные',
            'pc_rent': 'Аренда ПК',
            'extras': 'Допы',
            'food_total': 'Фуд-корт',
            'bar_total': 'Бар',
            'food_incassation': 'Инкассация Фуди',
            'salary_today': 'Заработано',
            'cash_taken': 'Забрал сейчас',
            'salary_to_account': 'Отложено',
            'remaining_cash': 'Остаток',
            'Общая касса': 'Общая касса'
        }
        
        st.dataframe(all_shifts[display_cols].rename(columns=display_names))
        
        total_all = all_shifts['Общая касса'].sum()
        total_salary = all_shifts['salary_to_account'].sum()
        total_accum = get_salary_accumulation()
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("📊 Общая выручка за все дни", f"{total_all:.0f} грн")
        with col2:
            st.metric("🏦 Всего отложено к 9 числу", f"{total_accum:.0f} грн")
        with col3:
            st.metric("📅 Всего смен", f"{len(all_shifts)}")
    else:
        st.info("Архив пока пуст. Закройте первую смену!")
