import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime, date

# --- НАСТРОЙКИ СТРАНИЦЫ ---
st.set_page_config(
    page_title="Компьютерный клуб - Смена",
    page_icon="🐱",
    layout="wide"
)

# --- CSS (МИЛЫЙ ДИЗАЙН С КОТИКАМИ) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Quicksand:wght@400;600;700&display=swap');
    
    .stApp {
        background: linear-gradient(135deg, #ffe6f0 0%, #ffd6e8 50%, #fce4ec 100%);
        font-family: 'Quicksand', sans-serif;
    }
    
    h1 {
        font-family: 'Quicksand', sans-serif !important;
        background: linear-gradient(90deg, #f78da7, #d4a5f5);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 700 !important;
        font-size: 42px !important;
        text-align: center;
    }
    
    h2, h3, h4 {
        font-family: 'Quicksand', sans-serif !important;
        color: #6b4c6b !important;
        font-weight: 600 !important;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #f78da7, #d4a5f5) !important;
        color: white !important;
        border: none !important;
        border-radius: 50px !important;
        padding: 12px 30px !important;
        font-weight: 600 !important;
        font-family: 'Quicksand', sans-serif !important;
        box-shadow: 0 4px 15px rgba(247, 141, 167, 0.4) !important;
        transition: all 0.3s ease !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-3px) scale(1.02) !important;
        box-shadow: 0 8px 30px rgba(212, 165, 245, 0.5) !important;
    }
    
    .stMetric {
        background: rgba(255, 255, 255, 0.7) !important;
        backdrop-filter: blur(10px) !important;
        border-radius: 20px !important;
        padding: 15px !important;
        border: 2px solid rgba(247, 141, 167, 0.2) !important;
        box-shadow: 0 4px 20px rgba(247, 141, 167, 0.1) !important;
    }
    
    .stMetric label {
        color: #6b4c6b !important;
        font-weight: 600 !important;
        font-family: 'Quicksand', sans-serif !important;
    }
    
    .stMetric .stMetricValue {
        color: #4a2d4a !important;
        font-weight: 700 !important;
        font-size: 28px !important;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: rgba(255, 255, 255, 0.5);
        border-radius: 50px;
        padding: 5px;
        backdrop-filter: blur(10px);
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 50px;
        padding: 10px 25px;
        color: #6b4c6b !important;
        font-weight: 500;
        font-family: 'Quicksand', sans-serif !important;
        transition: all 0.3s ease;
    }
    
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background: linear-gradient(135deg, #f78da7, #d4a5f5);
        color: white !important;
        border-radius: 50px;
    }
    
    .divider {
        background: linear-gradient(90deg, transparent, #f78da7, #d4a5f5, transparent);
        height: 3px;
        margin: 30px 0;
        border-radius: 10px;
    }
    
    .glass-card {
        background: rgba(255, 255, 255, 0.7);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        padding: 25px;
        box-shadow: 0 8px 32px rgba(247, 141, 167, 0.1);
        border: 2px solid rgba(255, 255, 255, 0.3);
    }
    
    .cat-icon {
        font-size: 24px;
        display: inline-block;
        animation: bounce 2s infinite;
    }
    
    @keyframes bounce {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-5px); }
    }
    
    /* Стили для текстовых полей */
    .stTextInput input, .stNumberInput input, .stTextArea textarea {
        background: rgba(255, 255, 255, 0.8) !important;
        border: 2px solid rgba(247, 141, 167, 0.3) !important;
        border-radius: 15px !important;
        color: #4a2d4a !important;
        font-family: 'Quicksand', sans-serif !important;
    }
    
    .stTextInput input:focus, .stNumberInput input:focus, .stTextArea textarea:focus {
        border-color: #d4a5f5 !important;
        box-shadow: 0 0 0 3px rgba(212, 165, 245, 0.2) !important;
    }
    
    /* Чекбоксы */
    .stCheckbox label {
        color: #4a2d4a !important;
        font-weight: 500 !important;
        font-family: 'Quicksand', sans-serif !important;
    }
    
    /* Датафреймы */
    .stDataFrame {
        background: rgba(255, 255, 255, 0.7) !important;
        border-radius: 15px !important;
        border: 2px solid rgba(247, 141, 167, 0.2) !important;
        padding: 10px !important;
    }
    
    /* Инфо блоки */
    .stAlert, .stInfo, .stSuccess, .stWarning {
        border-radius: 15px !important;
        font-family: 'Quicksand', sans-serif !important;
    }
</style>
""", unsafe_allow_html=True)

# --- БАЗА ДАННЫХ ---
def init_db():
    conn = sqlite3.connect('club_data.db')
    c = conn.cursor()
    
    c.execute('''CREATE TABLE IF NOT EXISTS sales_fudi
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  date TEXT, product TEXT, quantity INTEGER, price REAL)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS fudi_remaining
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  date TEXT, product TEXT, remaining INTEGER)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS fudi_arrival
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  date TEXT, product TEXT, quantity INTEGER)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS fudi_incassation
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  date TEXT, amount REAL)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS sales_bar
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  date TEXT, product TEXT, quantity INTEGER, price REAL)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS bar_stock
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  date TEXT, product TEXT, start_stock INTEGER, actual_stock INTEGER, sold INTEGER)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS bar_arrival
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  date TEXT, product TEXT, quantity INTEGER)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS bar_products
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT UNIQUE, price REAL)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS pc_status
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  date TEXT, pc_number INTEGER, status TEXT, note TEXT)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS games
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT UNIQUE, updated BOOLEAN, last_check TEXT)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS shift_totals
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  date TEXT, terminal REAL, cash REAL, pc_rent REAL,
                  extras REAL, fudi_total REAL, bar_total REAL,
                  incassation_total REAL, fudi_debt REAL,
                  salary_today REAL, salary_to_account REAL, 
                  cash_taken REAL, remaining_cash REAL, notes TEXT)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS salary_accumulation
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  date TEXT, amount REAL, total_accumulated REAL)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS daily_notes
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  date TEXT, note TEXT, timestamp TEXT)''')
    
    conn.commit()
    conn.close()

init_db()

# --- СПИСКИ ---
FUDI_PRODUCTS = {
    "Бургер": 80,
    "Картошка фри": 80,
    "Нагетсы": 80,
    "Мини-чебуречки": 80,
    "Хот-дог 2х": 80,
    "Хот-дог": 75,
    "Соус": 10
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

# ===== ЗАМЕТКИ =====
def add_note(note):
    conn = sqlite3.connect('club_data.db')
    c = conn.cursor()
    c.execute("INSERT INTO daily_notes (date, note, timestamp) VALUES (?, ?, ?)",
              (get_today(), note, datetime.now().strftime("%H:%M")))
    conn.commit()
    conn.close()

def get_notes_today():
    conn = sqlite3.connect('club_data.db')
    df = pd.read_sql_query(f"SELECT timestamp, note FROM daily_notes WHERE date='{get_today()}' ORDER BY id DESC", conn)
    conn.close()
    return df

def clear_notes():
    conn = sqlite3.connect('club_data.db')
    c = conn.cursor()
    c.execute("DELETE FROM daily_notes WHERE date=?", (get_today(),))
    conn.commit()
    conn.close()

# ===== ФУДИ =====
def add_fudi_sale(product):
    conn = sqlite3.connect('club_data.db')
    c = conn.cursor()
    price = FUDI_PRODUCTS[product]
    c.execute("INSERT INTO sales_fudi (date, product, quantity, price) VALUES (?, ?, ?, ?)",
              (get_today(), product, 1, price))
    conn.commit()
    conn.close()

def get_fudi_sales_today():
    conn = sqlite3.connect('club_data.db')
    df = pd.read_sql_query(f"SELECT product, SUM(quantity) as total_qty, price FROM sales_fudi WHERE date='{get_today()}' GROUP BY product", conn)
    conn.close()
    return df

def get_fudi_total_today():
    conn = sqlite3.connect('club_data.db')
    df = pd.read_sql_query(f"SELECT SUM(quantity * price) as total FROM sales_fudi WHERE date='{get_today()}'", conn)
    conn.close()
    return df['total'][0] if not df.empty and df['total'][0] else 0

def save_fudi_remaining(rem_dict):
    conn = sqlite3.connect('club_data.db')
    c = conn.cursor()
    today = get_today()
    c.execute("DELETE FROM fudi_remaining WHERE date=?", (today,))
    for product, rem in rem_dict.items():
        c.execute("INSERT INTO fudi_remaining (date, product, remaining) VALUES (?, ?, ?)",
                  (today, product, rem))
    conn.commit()
    conn.close()

def get_fudi_remaining_today():
    conn = sqlite3.connect('club_data.db')
    df = pd.read_sql_query(f"SELECT product, remaining FROM fudi_remaining WHERE date='{get_today()}'", conn)
    conn.close()
    return df

def add_fudi_arrival(product, quantity):
    conn = sqlite3.connect('club_data.db')
    c = conn.cursor()
    c.execute("INSERT INTO fudi_arrival (date, product, quantity) VALUES (?, ?, ?)",
              (get_today(), product, quantity))
    conn.commit()
    conn.close()

def get_fudi_arrivals_today():
    conn = sqlite3.connect('club_data.db')
    df = pd.read_sql_query(f"SELECT product, SUM(quantity) as total FROM fudi_arrival WHERE date='{get_today()}' GROUP BY product", conn)
    conn.close()
    return df

def add_fudi_incassation(amount):
    conn = sqlite3.connect('club_data.db')
    c = conn.cursor()
    c.execute("INSERT INTO fudi_incassation (date, amount) VALUES (?, ?)",
              (get_today(), amount))
    conn.commit()
    conn.close()

def get_fudi_incassation_today():
    conn = sqlite3.connect('club_data.db')
    df = pd.read_sql_query(f"SELECT SUM(amount) as total FROM fudi_incassation WHERE date='{get_today()}'", conn)
    conn.close()
    return df['total'][0] if not df.empty and df['total'][0] else 0

# ===== БАР =====
def add_bar_product(name, price):
    conn = sqlite3.connect('club_data.db')
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO bar_products (name, price) VALUES (?, ?)", (name, price))
    conn.commit()
    conn.close()

def get_bar_products():
    conn = sqlite3.connect('club_data.db')
    df = pd.read_sql_query("SELECT name, price FROM bar_products ORDER BY name", conn)
    conn.close()
    return df

def delete_bar_product(name):
    conn = sqlite3.connect('club_data.db')
    c = conn.cursor()
    c.execute("DELETE FROM bar_products WHERE name=?", (name,))
    conn.commit()
    conn.close()

def add_bar_sale(product, price):
    conn = sqlite3.connect('club_data.db')
    c = conn.cursor()
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

def add_bar_arrival(product, quantity):
    conn = sqlite3.connect('club_data.db')
    c = conn.cursor()
    c.execute("INSERT INTO bar_arrival (date, product, quantity) VALUES (?, ?, ?)",
              (get_today(), product, quantity))
    conn.commit()
    conn.close()

def get_bar_arrivals_today():
    conn = sqlite3.connect('club_data.db')
    df = pd.read_sql_query(f"SELECT product, SUM(quantity) as total FROM bar_arrival WHERE date='{get_today()}' GROUP BY product", conn)
    conn.close()
    return df

def save_bar_stock(start_dict, actual_dict):
    conn = sqlite3.connect('club_data.db')
    c = conn.cursor()
    today = get_today()
    c.execute("DELETE FROM bar_stock WHERE date=?", (today,))
    for product, start in start_dict.items():
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

# ===== ПК =====
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

# ===== ИГРЫ =====
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

# ===== ЗП =====
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

# ===== ИТОГИ =====
def save_shift_totals(terminal, cash, pc_rent, extras, fudi_total, bar_total, incassation_total, fudi_debt, salary_today, salary_to_account, cash_taken, remaining_cash, notes):
    conn = sqlite3.connect('club_data.db')
    c = conn.cursor()
    c.execute("INSERT INTO shift_totals (date, terminal, cash, pc_rent, extras, fudi_total, bar_total, incassation_total, fudi_debt, salary_today, salary_to_account, cash_taken, remaining_cash, notes) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
              (get_today(), terminal, cash, pc_rent, extras, fudi_total, bar_total, incassation_total, fudi_debt, salary_today, salary_to_account, cash_taken, remaining_cash, notes))
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
    c.execute("DELETE FROM sales_fudi WHERE date=?", (today,))
    c.execute("DELETE FROM fudi_remaining WHERE date=?", (today,))
    c.execute("DELETE FROM fudi_arrival WHERE date=?", (today,))
    c.execute("DELETE FROM fudi_incassation WHERE date=?", (today,))
    c.execute("DELETE FROM sales_bar WHERE date=?", (today,))
    c.execute("DELETE FROM bar_stock WHERE date=?", (today,))
    c.execute("DELETE FROM bar_arrival WHERE date=?", (today,))
    c.execute("DELETE FROM pc_status WHERE date=?", (today,))
    c.execute("DELETE FROM shift_totals WHERE date=?", (today,))
    c.execute("DELETE FROM daily_notes WHERE date=?", (today,))
    conn.commit()
    conn.close()

def clear_all_data():
    conn = sqlite3.connect('club_data.db')
    c = conn.cursor()
    c.execute("DELETE FROM sales_fudi")
    c.execute("DELETE FROM fudi_remaining")
    c.execute("DELETE FROM fudi_arrival")
    c.execute("DELETE FROM fudi_incassation")
    c.execute("DELETE FROM sales_bar")
    c.execute("DELETE FROM bar_stock")
    c.execute("DELETE FROM bar_arrival")
    c.execute("DELETE FROM bar_products")
    c.execute("DELETE FROM pc_status")
    c.execute("DELETE FROM shift_totals")
    c.execute("DELETE FROM salary_accumulation")
    c.execute("DELETE FROM games")
    c.execute("DELETE FROM daily_notes")
    c.execute("DELETE FROM sqlite_sequence")
    conn.commit()
    conn.close()

# ===== HTML ОТЧЕТ =====
def generate_html_report(notes_text=""):
    today = get_today()
    
    fudi_df = get_fudi_sales_today()
    fudi_total = get_fudi_total_today()
    bar_df = get_bar_sales_today()
    bar_total = get_bar_total_today()
    rem_df = get_fudi_remaining_today()
    bar_stock = get_bar_stock_today()
    pc_df = get_pc_status_today()
    games_df = get_games_status()
    shift_df = get_shift_totals_today()
    total_accumulated = get_salary_accumulation()
    fudi_inc = get_fudi_incassation_today()
    fudi_arrivals = get_fudi_arrivals_today()
    bar_arrivals = get_bar_arrivals_today()
    notes_df = get_notes_today()
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Отчет по смене от {today}</title>
        <style>
            body {{ font-family: 'Segoe UI', Arial, sans-serif; margin: 40px; background: #fce4ec; color: #4a2d4a; }}
            .container {{ max-width: 900px; margin: 0 auto; background: white; padding: 40px; border-radius: 25px; box-shadow: 0 10px 40px rgba(247, 141, 167, 0.2); }}
            h1 {{ text-align: center; color: #f78da7; font-size: 28px; border-bottom: 3px solid #f78da7; padding-bottom: 15px; }}
            h2 {{ color: #d4a5f5; font-size: 20px; margin-top: 30px; border-left: 4px solid #d4a5f5; padding-left: 15px; }}
            table {{ width: 100%; border-collapse: collapse; margin: 15px 0; font-size: 14px; }}
            th {{ background: #f78da7; color: white; padding: 10px; text-align: center; border-radius: 10px; }}
            td {{ padding: 8px 10px; border-bottom: 1px solid #fce4ec; text-align: center; }}
            tr:hover {{ background: #fce4ec; }}
            .total-row {{ background: #f3e5f5; font-weight: bold; }}
            .footer {{ text-align: center; margin-top: 30px; padding-top: 20px; border-top: 2px solid #fce4ec; color: #b39ddb; font-size: 14px; }}
            .summary {{ background: #f3e5f5; border: 1px solid #d4a5f5; border-radius: 15px; padding: 20px; margin: 20px 0; }}
            .summary-row {{ display: flex; justify-content: space-between; padding: 5px 0; }}
            .label {{ font-weight: 600; color: #6b4c6b; }}
            .value {{ font-weight: 700; color: #4a2d4a; }}
            .value-green {{ color: #66bb6a; }}
            .value-orange {{ color: #ffa726; }}
            .value-red {{ color: #ef5350; }}
            .value-blue {{ color: #7e57c2; }}
            .notes-box {{ background: #fce4ec; border-radius: 15px; padding: 20px; margin-top: 20px; border: 2px dashed #f78da7; }}
            .cat {{
                display: inline-block;
                animation: bounce 2s infinite;
            }}
            @keyframes bounce {{
                0%, 100% {{ transform: translateY(0); }}
                50% {{ transform: translateY(-5px); }}
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🐱 Отчет по смене</h1>
            <p style="text-align: center; color: #b39ddb;">Дата: <strong>{today}</strong></p>
    """
    
    # ===== ФУДИ =====
    html += f"<h2>🍣 1. Фуди - продажи</h2>"
    if not fudi_df.empty:
        html += """<table><tr><th>Товар</th><th>Кол-во</th><th>Цена</th><th>Сумма</th></tr>"""
        for _, row in fudi_df.iterrows():
            html += f"<tr><td>{row['product']}</td><td>{row['total_qty']}</td><td>{row['price']:.0f} грн</td><td>{row['total_qty'] * row['price']:.0f} грн</td></tr>"
        html += f"<tr class='total-row'><td colspan='2'></td><td>ИТОГО:</td><td>{fudi_total:.0f} грн</td></tr></table>"
    else:
        html += "<p style='color: #b39ddb;'>Продаж за сегодня нет</p>"
    
    # Фуди - приход
    html += f"<h2>📦 Фуди - приход товара</h2>"
    if not fudi_arrivals.empty:
        html += """<table><tr><th>Товар</th><th>Количество</th></tr>"""
        for _, row in fudi_arrivals.iterrows():
            html += f"<tr><td>{row['product']}</td><td>{row['total']}</td></tr>"
        html += "</table>"
    else:
        html += "<p style='color: #b39ddb;'>Прихода за сегодня нет</p>"
    
    # Фуди - инкассация
    html += f"<h2>💰 Фуди - инкассация</h2>"
    html += f"<p>Всего инкассировано: <strong>{fudi_inc:.0f} грн</strong></p>"
    fudi_debt = fudi_total - fudi_inc
    if fudi_debt > 0:
        html += f"<p style='color: #ffa726;'>Остаток в кассе Фуди (долг Елены): <strong>{fudi_debt:.0f} грн</strong></p>"
    else:
        html += f"<p>Остаток в кассе Фуди: <strong>0 грн</strong></p>"
    
    # Фуди - остатки
    html += f"<h2>📊 Фуди - остатки на конец дня</h2>"
    if not rem_df.empty:
        html += """<table><tr><th>Товар</th><th>Остаток</th></tr>"""
        for _, row in rem_df.iterrows():
            html += f"<tr><td>{row['product']}</td><td>{row['remaining']}</td></tr>"
        html += "</table>"
    else:
        html += "<p style='color: #b39ddb;'>Остатки не введены</p>"
    
    # ===== БАР =====
    html += f"<h2>🧋 2. Бар - продажи</h2>"
    if not bar_df.empty:
        html += """<table><tr><th>Товар</th><th>Кол-во</th><th>Цена</th><th>Сумма</th></tr>"""
        for _, row in bar_df.iterrows():
            html += f"<tr><td>{row['product']}</td><td>{row['total_qty']}</td><td>{row['price']:.0f} грн</td><td>{row['total_qty'] * row['price']:.0f} грн</td></tr>"
        html += f"<tr class='total-row'><td colspan='2'></td><td>ИТОГО:</td><td>{bar_total:.0f} грн</td></tr></table>"
    else:
        html += "<p style='color: #b39ddb;'>Продаж за сегодня нет</p>"
    
    # Бар - приход
    html += f"<h2>📦 Бар - приход товара</h2>"
    if not bar_arrivals.empty:
        html += """<table><tr><th>Товар</th><th>Количество</th></tr>"""
        for _, row in bar_arrivals.iterrows():
            html += f"<tr><td>{row['product']}</td><td>{row['total']}</td></tr>"
        html += "</table>"
    else:
        html += "<p style='color: #b39ddb;'>Прихода за сегодня нет</p>"
    
    # Бар - остатки
    html += f"<h2>📊 Бар - остатки</h2>"
    if not bar_stock.empty:
        html += """<table><tr><th>Товар</th><th>Начало</th><th>Продано</th><th>Остаток</th></tr>"""
        for _, row in bar_stock.iterrows():
            html += f"<tr><td>{row['product']}</td><td>{row['start_stock']}</td><td>{row['sold']}</td><td>{row['actual_stock']}</td></tr>"
        html += "</table>"
    else:
        html += "<p style='color: #b39ddb;'>Остатки бара не введены</p>"
    
    # ===== ПК =====
    html += f"<h2>💻 3. Состояние компьютеров</h2>"
    if not pc_df.empty:
        html += """<table><tr><th>N ПК</th><th>Статус</th><th>Заметка</th></tr>"""
        for _, row in pc_df.iterrows():
            html += f"<tr><td>{row['pc_number']}</td><td>{row['status']}</td><td>{row['note'] or '-'}</td></tr>"
        html += "</table>"
    else:
        html += "<p style='color: #b39ddb;'>Статусы ПК не заполнены</p>"
    
    # ===== ИГРЫ =====
    html += f"<h2>🎮 4. Обновление игр</h2>"
    if not games_df.empty:
        html += """<table><tr><th>Игра</th><th>Обновлено</th><th>Дата проверки</th></tr>"""
        for _, row in games_df.iterrows():
            status_text = 'Да' if row['updated'] else 'Нет'
            color = '#66bb6a' if row['updated'] else '#ef5350'
            html += f"<tr><td>{row['name']}</td><td style='color:{color};'>{status_text}</td><td>{row['last_check'] or '-'}</td></tr>"
        html += "</table>"
    else:
        html += "<p style='color: #b39ddb;'>Список игр не загружен</p>"
    
    # ===== ФИНАНСЫ =====
    html += f"<h2>💰 5. Финансовый итог смены</h2>"
    if not shift_df.empty:
        row = shift_df.iloc[0]
        total_cash = row['terminal'] + row['cash'] + row['pc_rent'] + row['extras'] + row['fudi_total'] + row['bar_total']
        html += f"""
        <div class="summary">
            <div class="summary-row"><span class="label">💳 Терминал (безнал):</span><span class="value">{row['terminal']:.0f} грн</span></div>
            <div class="summary-row"><span class="label">💵 Наличные:</span><span class="value">{row['cash']:.0f} грн</span></div>
            <div class="summary-row"><span class="label">🖥️ Аренда ПК:</span><span class="value">{row['pc_rent']:.0f} грн</span></div>
            <div class="summary-row"><span class="label">🖨️ Допы:</span><span class="value">{row['extras']:.0f} грн</span></div>
            <div class="summary-row"><span class="label">🍣 Фуди:</span><span class="value">{row['fudi_total']:.0f} грн</span></div>
            <div class="summary-row"><span class="label">🧋 Бар:</span><span class="value">{row['bar_total']:.0f} грн</span></div>
            <div class="summary-row"><span class="label">💰 Инкассация Фуди:</span><span class="value value-red">-{row['incassation_total']:.0f} грн</span></div>
            <div class="summary-row"><span class="label">🐱 Долг Елены (остаток в Фуди):</span><span class="value value-orange">{row['fudi_debt']:.0f} грн</span></div>
            <hr style="border: 1px solid #fce4ec; margin: 15px 0;">
            <div class="summary-row"><span class="label" style="font-size: 18px;">📊 ОБЩАЯ КАССА:</span><span class="value" style="font-size: 18px; color: #7e57c2;">{total_cash:.0f} грн</span></div>
            <div class="summary-row"><span class="label">👩‍💼 Заработано за день:</span><span class="value value-blue">{row['salary_today']:.0f} грн</span></div>
            <div class="summary-row"><span class="label">💸 Забрал сейчас (наличкой):</span><span class="value value-green">{row['cash_taken']:.0f} грн</span></div>
            <div class="summary-row"><span class="label">🏦 Отложено к 9 числу:</span><span class="value value-orange">{row['salary_to_account']:.0f} грн</span></div>
            <hr style="border: 1px solid #fce4ec; margin: 15px 0;">
            <div class="summary-row"><span class="label" style="font-size: 18px;">💎 ИТОГОВЫЙ ОСТАТОК:</span><span class="value" style="font-size: 18px; color: #66bb6a;">{row['remaining_cash']:.0f} грн</span></div>
        </div>
        """
        html += f"""
        <div style="text-align: center; background: #f3e5f5; padding: 15px; border-radius: 15px; margin-top: 15px;">
            <span style="font-weight: 600;">🐱 Накопления к 9 числу:</span>
            <span style="font-size: 24px; font-weight: 700; color: #7e57c2;">{total_accumulated:.0f} грн</span>
        </div>
        """
    else:
        html += "<p style='color: #b39ddb;'>Финансовый итог не подведен</p>"
    
    # ===== ЗАМЕТКИ =====
    if notes_text:
        html += f"""
        <h2>📝 Заметки за смену</h2>
        <div class="notes-box">
            <p style="white-space: pre-wrap;">{notes_text}</p>
        </div>
        """
    elif not notes_df.empty:
        html += f"""
        <h2>📝 Заметки за смену</h2>
        <div class="notes-box">
        """
        for _, row in notes_df.iterrows():
            html += f"<p><strong>{row['timestamp']}</strong> - {row['note']}</p>"
        html += "</div>"
    
    html += f"""
            <div class="footer">🐱 Отчет сгенерирован автоматически • {today}</div>
        </div>
    </body>
    </html>
    """
    
    return html

# ===== РАСЧЕТ БОНУСА =====
def calculate_bonus(total_cash_without_fudi):
    """Расчет бонуса: 
       - если >= 1200: +100
       - потом за каждые 1000 сверху: +100
    """
    if total_cash_without_fudi >= 1200:
        bonus = 100
        extra = total_cash_without_fudi - 1200
        if extra >= 1000:
            bonus += (int(extra // 1000)) * 100
        return bonus
    return 0

# ===== ИНТЕРФЕЙС =====

st.markdown("""
<div style="text-align: center; padding: 30px 0 20px 0;">
    <h1>🐱 КОМПЬЮТЕРНЫЙ КЛУБ</h1>
    <p style="color: #b39ddb; font-size: 18px; letter-spacing: 3px;">УПРАВЛЕНИЕ СМЕНОЙ ✨</p>
    <div class="divider"></div>
</div>
""", unsafe_allow_html=True)

st.markdown(f"<p style='text-align: right; color: #b39ddb;'>📅 {get_today()}</p>", unsafe_allow_html=True)

total_accumulated = get_salary_accumulation()
st.markdown(f"""
<div style="background: linear-gradient(135deg, rgba(247, 141, 167, 0.1), rgba(212, 165, 245, 0.1));
            border: 2px solid rgba(247, 141, 167, 0.2);
            border-radius: 20px;
            padding: 15px 25px;
            margin-bottom: 20px;
            text-align: center;">
    <span style="color: #6b4c6b; font-size: 16px; font-weight: 600;">🐱 НАКОПЛЕНИЯ К 9 ЧИСЛУ:</span>
    <span style="color: #7e57c2; font-size: 30px; font-weight: 700; margin-left: 15px;">
        {total_accumulated:.0f} грн
    </span>
</div>
""", unsafe_allow_html=True)

col_new1, col_new2, col_new3 = st.columns([1, 2, 1])
with col_new2:
    if st.button("🔄 НОВАЯ СМЕНА", use_container_width=True):
        clear_day_data()
        st.success("✨ Данные за сегодня очищены! Можно начинать новую смену.")
        st.rerun()

st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
    "🏠 Главная", "🍣 Фуди", "🧋 Бар", "💻 ПК", "🎮 Игры", "💰 Финансы", "📚 Архив", "📝 Заметки"
])

# ===== ГЛАВНАЯ =====
with tab1:
    st.markdown("<h2 style='text-align: center;'>📊 ДАШБОРД СМЕНЫ</h2>", unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("🍣 Фуди", f"{get_fudi_total_today():.0f} грн")
    with col2:
        st.metric("🧋 Бар", f"{get_bar_total_today():.0f} грн")
    with col3:
        st.metric("💵 Общая выручка", f"{get_fudi_total_today() + get_bar_total_today():.0f} грн")
    with col4:
        st.metric("🐱 Админ", "Сегодня")
    
    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
    
    shift_df = get_shift_totals_today()
    if not shift_df.empty:
        row = shift_df.iloc[0]
        total_cash = row['terminal'] + row['cash'] + row['pc_rent'] + row['extras'] + row['fudi_total'] + row['bar_total']
        
        st.subheader("📋 Итоги смены")
        col5, col6 = st.columns(2)
        with col5:
            st.write(f"💳 Терминал: **{row['terminal']:.0f} грн**")
            st.write(f"💵 Наличные: **{row['cash']:.0f} грн**")
            st.write(f"🖥️ Аренда ПК: **{row['pc_rent']:.0f} грн**")
            st.write(f"🖨️ Допы: **{row['extras']:.0f} грн**")
            st.write(f"🍣 Фуди: **{row['fudi_total']:.0f} грн**")
        with col6:
            st.write(f"🧋 Бар: **{row['bar_total']:.0f} грн**")
            st.write(f"💰 Инкассация Фуди: **-{row['incassation_total']:.0f} грн**")
            st.write(f"🐱 Долг Елены: **{row['fudi_debt']:.0f} грн**")
            st.write(f"📊 Общая касса: **{total_cash:.0f} грн**")
            st.write(f"👩‍💼 Заработано: **{row['salary_today']:.0f} грн**")
            st.write(f"💸 Забрал сейчас: **{row['cash_taken']:.0f} грн**")
            st.write(f"🏦 Отложено: **{row['salary_to_account']:.0f} грн**")
            st.write(f"💎 Остаток в кассе: **{row['remaining_cash']:.0f} грн**")
    else:
        st.info("✨ Смена еще не закрыта. Перейдите во вкладку 'Финансы' для закрытия смены.")
    
    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
    
    # Отчет с заметками
    notes_df = get_notes_today()
    notes_text = ""
    if not notes_df.empty:
        notes_text = "\n".join([f"{row['timestamp']} - {row['note']}" for _, row in notes_df.iterrows()])
    
    if st.button("📄 Открыть отчет в браузере", use_container_width=True):
        html_report = generate_html_report(notes_text)
        st.markdown(f"""
        <div style="text-align: center; padding: 20px; background: #f3e5f5; border-radius: 20px; border: 2px solid #d4a5f5;">
            <p style="font-size: 18px; color: #6b4c6b;">🐱 Отчет готов!</p>
            <p style="color: #b39ddb;">Нажмите <strong>Ctrl+P</strong> (или Cmd+P на Mac) и выберите <strong>"Сохранить как PDF"</strong></p>
            <div style="border: 2px solid #fce4ec; border-radius: 15px; padding: 20px; margin-top: 15px; background: white; text-align: left; max-height: 500px; overflow: auto;">
                {html_report}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Кнопка очистки месяца
    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
    
    col_del1, col_del2, col_del3 = st.columns([1, 2, 1])
    with col_del2:
        if st.button("🗑️ ОЧИСТИТЬ МЕСЯЦ", use_container_width=True):
            st.warning("⚠️ ВНИМАНИЕ! Будут удалены ВСЕ данные: все смены, накопления, история!")
            if st.button("✅ ПОДТВЕРДИТЬ УДАЛЕНИЕ", use_container_width=True):
                clear_all_data()
                st.success("✅ Все данные полностью очищены!")
                st.balloons()
                st.rerun()

# ===== ФУДИ =====
with tab2:
    st.header("🍣 Фуди")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("➕ Продажи")
        for product in FUDI_PRODUCTS:
            col_a, col_b = st.columns([3, 1])
            with col_a:
                st.write(f"{product} — {FUDI_PRODUCTS[product]} грн")
            with col_b:
                if st.button(f"+1", key=f"fudi_{product}"):
                    add_fudi_sale(product)
                    st.success(f"✅ {product} добавлен")
                    st.rerun()
    
    with col2:
        st.subheader("📊 Продажи сегодня")
        df = get_fudi_sales_today()
        if not df.empty:
            df['Сумма'] = df['total_qty'] * df['price']
            st.dataframe(df[['product', 'total_qty', 'price', 'Сумма']].rename(
                columns={'product': 'Товар', 'total_qty': 'Кол-во', 'price': 'Цена'}))
            st.metric("Общая выручка", f"{get_fudi_total_today():.0f} грн")
        else:
            st.info("Продаж пока нет")
    
    st.divider()
    
    st.subheader("📦 Приход товара (Елена принесла)")
    col_a, col_b = st.columns([3, 1])
    with col_a:
        product_arrival = st.selectbox("Товар", list(FUDI_PRODUCTS.keys()), key="fudi_arrival_product")
    with col_b:
        quantity_arrival = st.number_input("Количество", min_value=1, step=1, key="fudi_arrival_qty")
    if st.button("➕ Добавить приход"):
        add_fudi_arrival(product_arrival, quantity_arrival)
        st.success(f"✅ Приход {product_arrival} x{quantity_arrival} добавлен!")
        st.rerun()
    
    arrivals_df = get_fudi_arrivals_today()
    if not arrivals_df.empty:
        st.write("📋 Приходы сегодня:")
        st.dataframe(arrivals_df.rename(columns={'product': 'Товар', 'total': 'Количество'}))
    
    st.divider()
    
    st.subheader("💰 Инкассация (Елена забирает)")
    incassation_amount = st.number_input("Сумма инкассации", min_value=0.0, step=10.0, format="%.0f", key="fudi_inc")
    if st.button("💸 Забрать деньги"):
        if incassation_amount > 0:
            add_fudi_incassation(incassation_amount)
            st.success(f"✅ Инкассация {incassation_amount:.0f} грн сохранена!")
            st.rerun()
        else:
            st.warning("Введите сумму больше 0")
    
    inc_total = get_fudi_incassation_today()
    fudi_total = get_fudi_total_today()
    if inc_total > 0:
        st.info(f"💰 Всего инкассировано: **{inc_total:.0f} грн**")
        fudi_debt = fudi_total - inc_total
        if fudi_debt > 0:
            st.warning(f"🐱 Остаток в кассе Фуди (долг Елены): **{fudi_debt:.0f} грн**")
        else:
            st.success("✨ Касса Фуди пуста")
    
    st.divider()
    
    st.subheader("📊 Остатки на конец дня")
    rem_cols = st.columns(3)
    rem_values = {}
    for i, product in enumerate(FUDI_PRODUCTS.keys()):
        with rem_cols[i % 3]:
            rem_values[product] = st.number_input(f"{product}", min_value=0, step=1, key=f"fudi_rem_{product}")
    if st.button("💾 Сохранить остатки"):
        save_fudi_remaining(rem_values)
        st.success("✅ Остатки сохранены!")

# ===== БАР =====
with tab3:
    st.header("🧋 Бар")
    
    with st.expander("📝 Управление товарами (добавить/удалить)"):
        col_a, col_b = st.columns(2)
        with col_a:
            new_product = st.text_input("Название товара")
            new_price = st.number_input("Цена", min_value=0.0, step=1.0, format="%.0f")
            if st.button("➕ Добавить товар"):
                if new_product and new_price > 0:
                    add_bar_product(new_product, new_price)
                    st.success(f"✅ Товар '{new_product}' добавлен!")
                    st.rerun()
                else:
                    st.warning("Введите название и цену")
        
        with col_b:
            bar_products_df = get_bar_products()
            if not bar_products_df.empty:
                product_to_delete = st.selectbox("Выберите товар для удаления", bar_products_df['name'].tolist())
                if st.button("🗑️ Удалить товар"):
                    delete_bar_product(product_to_delete)
                    st.success(f"✅ Товар '{product_to_delete}' удален!")
                    st.rerun()
            else:
                st.info("Список товаров пуст")
    
    st.divider()
    
    bar_products_df = get_bar_products()
    if not bar_products_df.empty:
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("➕ Продажи")
            for _, row in bar_products_df.iterrows():
                col_a, col_b = st.columns([3, 1])
                with col_a:
                    st.write(f"{row['name']} — {row['price']:.0f} грн")
                with col_b:
                    if st.button(f"+1", key=f"bar_{row['name']}"):
                        add_bar_sale(row['name'], row['price'])
                        st.success(f"✅ {row['name']} добавлен")
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
        
        st.subheader("📦 Приход товара")
        bar_arrival_product = st.selectbox("Товар", bar_products_df['name'].tolist(), key="bar_arrival_product")
        bar_arrival_qty = st.number_input("Количество", min_value=1, step=1, key="bar_arrival_qty")
        if st.button("➕ Добавить приход в бар"):
            add_bar_arrival(bar_arrival_product, bar_arrival_qty)
            st.success(f"✅ Приход {bar_arrival_product} x{bar_arrival_qty} добавлен!")
            st.rerun()
        
        arrivals_bar_df = get_bar_arrivals_today()
        if not arrivals_bar_df.empty:
            st.write("📋 Приходы сегодня:")
            st.dataframe(arrivals_bar_df.rename(columns={'product': 'Товар', 'total': 'Количество'}))
        
        st.divider()
        
        st.subheader("📊 Остатки бара")
        st.info("Введите начальные остатки (в начале смены) и фактические (в конце смены)")
        
        bar_stock_df = get_bar_stock_today()
        
        if bar_stock_df.empty:
            st.subheader("📝 Начальные остатки")
            start_cols = st.columns(3)
            start_values = {}
            for i, product in enumerate(bar_products_df['name'].tolist()):
                with start_cols[i % 3]:
                    start_values[product] = st.number_input(f"{product}", min_value=0, step=1, key=f"bar_start_{product}")
            
            if st.button("💾 Сохранить начальные остатки"):
                conn = sqlite3.connect('club_data.db')
                c = conn.cursor()
                today = get_today()
                c.execute("DELETE FROM bar_stock WHERE date=?", (today,))
                for product, start in start_values.items():
                    c.execute("INSERT INTO bar_stock (date, product, start_stock, actual_stock, sold) VALUES (?, ?, ?, ?, ?)",
                              (today, product, start, start, 0))
                conn.commit()
                conn.close()
                st.success("✅ Начальные остатки сохранены!")
                st.rerun()
        else:
            st.subheader("📋 Текущие данные")
            st.dataframe(bar_stock_df[['product', 'start_stock', 'sold']].rename(
                columns={'product': 'Товар', 'start_stock': 'Начало', 'sold': 'Продано по учету'}))
            
            st.subheader("📝 Фактические остатки (введите в конце смены)")
            actual_cols = st.columns(3)
            actual_values = {}
            for i, product in enumerate(bar_products_df['name'].tolist()):
                with actual_cols[i % 3]:
                    default_val = bar_stock_df[bar_stock_df['product'] == product]['actual_stock'].iloc[0] if not bar_stock_df[bar_stock_df['product'] == product].empty else 0
                    actual_values[product] = st.number_input(f"{product}", min_value=0, step=1, value=default_val, key=f"bar_actual_{product}")
            
            if st.button("💾 Сохранить фактические остатки"):
                conn = sqlite3.connect('club_data.db')
                c = conn.cursor()
                today = get_today()
                for product, actual in actual_values.items():
                    start = bar_stock_df[bar_stock_df['product'] == product]['start_stock'].iloc[0] if not bar_stock_df[bar_stock_df['product'] == product].empty else 0
                    sold = start - actual
                    c.execute("UPDATE bar_stock SET actual_stock=?, sold=? WHERE date=? AND product=?",
                              (actual, sold, today, product))
                conn.commit()
                conn.close()
                st.success("✅ Фактические остатки сохранены!")
                st.rerun()
            
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
    else:
        st.info("🐱 Сначала добавьте товары в разделе 'Управление товарами'")

# ===== ПК =====
with tab4:
    st.header("💻 Состояние компьютеров")
    
    status_options = ["Работает отлично", "Проблема с наушниками", "Зависает", "Не включается", "Требуется перезагрузка", "Другое"]
    new_status = st.text_input("➕ Добавить свой статус")
    if new_status and st.button("Добавить статус"):
        status_options.append(new_status)
        st.success(f"✅ Статус '{new_status}' добавлен!")
    
    st.divider()
    pc_cols = st.columns(5)
    for i, pc in enumerate(PC_NUMBERS):
        with pc_cols[i % 5]:
            with st.container(border=True):
                st.write(f"**💻 ПК N{pc}**")
                status = st.selectbox("Статус", status_options, key=f"status_{pc}")
                note = st.text_area("Заметка", placeholder="Опишите проблему...", key=f"note_{pc}")
                if st.button(f"💾 Сохранить N{pc}", key=f"save_{pc}"):
                    save_pc_status(pc, status, note)
                    st.success(f"✅ ПК N{pc} сохранен")
                    st.rerun()
    
    st.divider()
    pc_df = get_pc_status_today()
    if not pc_df.empty:
        st.dataframe(pc_df[['pc_number', 'status', 'note']].rename(
            columns={'pc_number': 'N ПК', 'status': 'Статус', 'note': 'Заметка'}))

# ===== ИГРЫ =====
with tab5:
    st.header("🎮 Обновление игр")
    init_games()
    st.info("🐱 Отмечайте галочкой игры, которые обновлены и работают")
    
    games_df = get_games_status()
    game_cols = st.columns(3)
    for i, (_, row) in enumerate(games_df.iterrows()):
        with game_cols[i % 3]:
            with st.container(border=True):
                col_a, col_b = st.columns([4, 1])
                with col_a:
                    st.write(f"**{row['name']}**")
                    if row['last_check']:
                        st.caption(f"📅 Проверка: {row['last_check']}")
                with col_b:
                    updated = st.checkbox("✅", value=bool(row['updated']), key=f"game_{row['name']}")
                    if updated != bool(row['updated']):
                        update_game_status(row['name'], updated)
                        st.rerun()

# ===== ФИНАНСЫ =====
with tab6:
    st.header("💰 Финансовый итог смены")
    st.info("🐱 Заполните все суммы и нажмите 'Закрыть смену'")
    
    fudi_total = get_fudi_total_today()
    bar_total = get_bar_total_today()
    fudi_inc = get_fudi_incassation_today()
    fudi_debt = fudi_total - fudi_inc
    
    with st.form("shift_close"):
        col1, col2 = st.columns(2)
        with col1:
            terminal = st.number_input("💳 Терминал (безнал)", min_value=0.0, step=50.0, format="%.0f")
            cash = st.number_input("💵 Наличные", min_value=0.0, step=50.0, format="%.0f")
            pc_rent = st.number_input("🖥️ Аренда ПК", min_value=0.0, step=50.0, format="%.0f")
        with col2:
            extras = st.number_input("🖨️ Допы (печать и т.д.)", min_value=0.0, step=10.0, format="%.0f")
        
        # Расчет кассы без Фуди для бонуса
        total_cash_without_fudi = terminal + cash + pc_rent + extras + bar_total
        total_cash = total_cash_without_fudi + fudi_total
        
        # Расчет ЗП с бонусом
        bonus = calculate_bonus(total_cash_without_fudi)
        salary_today = 400 + bonus
        
        cash_taken = 200
        salary_to_account = salary_today - cash_taken
        if salary_to_account < 0:
            salary_to_account = 0
        
        remaining_cash = total_cash - salary_today - fudi_inc
        
        st.divider()
        st.markdown(f"""
        <div style="background: #f3e5f5; padding: 20px; border-radius: 20px; border: 2px solid #d4a5f5;">
            <h4>🐱 Расчет ЗП</h4>
            <p>🍣 Фуди: <b>{fudi_total:.0f} грн</b></p>
            <p>🧋 Бар: <b>{bar_total:.0f} грн</b></p>
            <p>💳 Терминал: <b>{terminal:.0f} грн</b></p>
            <p>💵 Наличные: <b>{cash:.0f} грн</b></p>
            <p>🖥️ Аренда ПК: <b>{pc_rent:.0f} грн</b></p>
            <p>🖨️ Допы: <b>{extras:.0f} грн</b></p>
            <p>💰 Касса без Фуди: <b>{total_cash_without_fudi:.0f} грн</b></p>
            <p>🎁 Бонус: <b>+{bonus:.0f} грн</b> (за каждые 1000 грн без Фуди)</p>
            <p>👩‍💼 Заработано за день: <b>{salary_today:.0f} грн</b> (ставка 400 + бонус)</p>
            <p style="color: #66bb6a;">💸 Забираю сейчас (наличкой): <b>{cash_taken:.0f} грн</b></p>
            <p style="color: #ffa726;">🏦 Откладывается к 9 числу: <b>{salary_to_account:.0f} грн</b></p>
            <p style="color: #ef5350;">💰 Инкассация Фуди: <b>-{fudi_inc:.0f} грн</b></p>
            <p style="color: #ffa726;">🐱 Долг Елены: <b>{fudi_debt:.0f} грн</b></p>
            <p>💎 Остаток в кассе: <b>{remaining_cash:.0f} грн</b></p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.form_submit_button("✨ Закрыть смену"):
            if total_cash > 0:
                if salary_to_account > 0:
                    add_salary_accumulation(salary_to_account)
                
                # Получаем заметки
                notes_df = get_notes_today()
                notes_text = ""
                if not notes_df.empty:
                    notes_text = "\n".join([f"{row['timestamp']} - {row['note']}" for _, row in notes_df.iterrows()])
                
                save_shift_totals(terminal, cash, pc_rent, extras, fudi_total, bar_total, fudi_inc, fudi_debt, salary_today, salary_to_account, cash_taken, remaining_cash, notes_text)
                st.success(f"✨ Смена закрыта! 🐱 Заработано: {salary_today:.0f} грн, Забрал: {cash_taken:.0f} грн, Отложено: {salary_to_account:.0f} грн, Остаток: {remaining_cash:.0f} грн")
                st.balloons()
            else:
                st.error("❌ Ошибка: общая касса не может быть 0")

# ===== АРХИВ =====
with tab7:
    st.header("📚 Архив смен")
    
    all_shifts = get_all_shifts()
    if not all_shifts.empty:
        all_shifts['Общая касса'] = all_shifts['terminal'] + all_shifts['cash'] + all_shifts['pc_rent'] + all_shifts['extras'] + all_shifts['fudi_total'] + all_shifts['bar_total']
        all_shifts['Дата'] = all_shifts['date']
        
        display_cols = ['Дата', 'terminal', 'cash', 'pc_rent', 'extras', 'fudi_total', 'bar_total', 'incassation_total', 'fudi_debt', 'salary_today', 'cash_taken', 'salary_to_account', 'remaining_cash', 'Общая касса', 'notes']
        display_names = {
            'Дата': '📅 Дата',
            'terminal': '💳 Терминал',
            'cash': '💵 Наличные',
            'pc_rent': '🖥️ Аренда ПК',
            'extras': '🖨️ Допы',
            'fudi_total': '🍣 Фуди',
            'bar_total': '🧋 Бар',
            'incassation_total': '💰 Инкассация Фуди',
            'fudi_debt': '🐱 Долг Елены',
            'salary_today': '👩‍💼 Заработано',
            'cash_taken': '💸 Забрал сейчас',
            'salary_to_account': '🏦 Отложено',
            'remaining_cash': '💎 Остаток',
            'Общая касса': '📊 Общая касса',
            'notes': '📝 Заметки'
        }
        
        st.dataframe(all_shifts[display_cols].rename(columns=display_names))
        
        total_all = all_shifts['Общая касса'].sum()
        total_accum = get_salary_accumulation()
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("📊 Общая выручка за все дни", f"{total_all:.0f} грн")
        with col2:
            st.metric("🏦 Всего отложено к 9 числу", f"{total_accum:.0f} грн")
        with col3:
            st.metric("📅 Всего смен", f"{len(all_shifts)}")
    else:
        st.info("🐱 Архив пока пуст. Закройте первую смену!")

# ===== ЗАМЕТКИ =====
with tab8:
    st.header("📝 Заметки к отчету")
    st.info("🐱 Пишите заметки в течение смены — они прикрепятся к отчету!")
    
    # Показать существующие заметки
    notes_df = get_notes_today()
    if not notes_df.empty:
        st.subheader("📋 Заметки за сегодня:")
        for _, row in notes_df.iterrows():
            st.write(f"**{row['timestamp']}** — {row['note']}")
        st.divider()
    
    # Добавить заметку
    new_note = st.text_area("✏️ Напишите заметку", placeholder="Например: Приехала Елена, привезла 20 бургеров...")
    if st.button("💾 Сохранить заметку"):
        if new_note.strip():
            add_note(new_note.strip())
            st.success("✅ Заметка сохранена!")
            st.rerun()
        else:
            st.warning("Напишите текст заметки")
    
    # Очистить заметки
    if st.button("🗑️ Очистить все заметки за сегодня"):
        clear_notes()
        st.success("✅ Заметки очищены!")
        st.rerun()
