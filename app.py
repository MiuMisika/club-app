import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime, date
import json
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
import io
import os

# --- НАСТРОЙКИ СТРАНИЦЫ ---
st.set_page_config(page_title="Компьютерный клуб - Смена", page_icon="🎮", layout="wide")

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
    
    # Остатки Фуди
    c.execute('''CREATE TABLE IF NOT EXISTS food_remaining
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  date TEXT,
                  product TEXT,
                  remaining INTEGER)''')
    
    # Бар - остатки
    c.execute('''CREATE TABLE IF NOT EXISTS bar_stock
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  date TEXT,
                  product TEXT,
                  start_stock INTEGER,
                  actual_stock INTEGER,
                  sold INTEGER)''')
    
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
                  food_cash REAL,
                  food_incassation REAL,
                  salary REAL,
                  remaining_cash REAL)''')
    
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

BAR_PRODUCTS = [
    "Pepsi 0,5л",
    "Pepsi 0,33л",
    "Pepsi 0,33л ж/б",
    "Карпатська жерельна 0,5л г/н.г",
    "Battery 0,33л ж/б",
    "Battery 0,5л ж/б",
    "Battery 0,5л ж/б с соком",
    "Ситро 0,5л ж/б",
    "Дюшес 0,5л ж/б",
    "Квас Тарас 0,5л ж/б",
    "Shwepps 0,33",
    "Coca-Cola/Fanta/Sprite 0,33",
    "Салфетки обычные",
    "Флинт 60 г",
    "Флинт Гренки 55 г",
    "Hroom 50 г",
    "Big bob 60 г",
    "Флинт с Соусом 65 г",
    "Chipsters чипси 60 г"
]

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

def save_bar_stock(start_stock, actual_stock):
    conn = sqlite3.connect('club_data.db')
    c = conn.cursor()
    today = get_today()
    for product in BAR_PRODUCTS:
        sold = start_stock[product] - actual_stock[product]
        c.execute("INSERT INTO bar_stock (date, product, start_stock, actual_stock, sold) VALUES (?, ?, ?, ?, ?)",
                  (today, product, start_stock[product], actual_stock[product], sold))
    conn.commit()
    conn.close()

def get_bar_stock_today():
    conn = sqlite3.connect('club_data.db')
    df = pd.read_sql_query(f"SELECT * FROM bar_stock WHERE date='{get_today()}'", conn)
    conn.close()
    return df

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

def save_shift_totals(terminal, cash, pc_rent, extras, food_incassation, salary, remaining_cash):
    conn = sqlite3.connect('club_data.db')
    c = conn.cursor()
    food_total = get_food_total_today()
    c.execute("INSERT INTO shift_totals (date, terminal, cash, pc_rent, extras, food_cash, food_incassation, salary, remaining_cash) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
              (get_today(), terminal, cash, pc_rent, extras, food_total, food_incassation, salary, remaining_cash))
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
    style_title = ParagraphStyle('CustomTitle', parent=styles['Heading1'], fontSize=16, alignment=TA_CENTER, spaceAfter=20)
    style_header = ParagraphStyle('CustomHeader', parent=styles['Heading2'], fontSize=14, spaceAfter=10)
    style_normal = styles['Normal']
    
    elements = []
    
    # Заголовок
    elements.append(Paragraph(f"Отчет по смене от {today}", style_title))
    elements.append(Spacer(1, 10))
    
    # 1. Продажи Фуди
    elements.append(Paragraph("1. Продажи Фуд-корта", style_header))
    food_df = get_food_sales_today()
    if not food_df.empty:
        food_data = [["Товар", "Кол-во", "Цена", "Сумма"]]
        for _, row in food_df.iterrows():
            food_data.append([row['product'], row['total_qty'], f"{row['price']:.0f} грн", f"{row['total_qty'] * row['price']:.0f} грн"])
        food_data.append(["", "", "ИТОГО:", f"{get_food_total_today():.0f} грн"])
        table = Table(food_data)
        table.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                                   ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                                   ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                                   ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                                   ('FONTSIZE', (0, 0), (-1, -1), 10),
                                   ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                                   ('BACKGROUND', (0, 1), (-1, -2), colors.beige),
                                   ('GRID', (0, 0), (-1, -1), 1, colors.black)]))
        elements.append(table)
    else:
        elements.append(Paragraph("Продаж за сегодня нет", style_normal))
    
    # Остатки Фуди
    elements.append(Spacer(1, 10))
    elements.append(Paragraph("Остатки Фуд-корта", style_header))
    rem_df = get_food_remaining_today()
    if not rem_df.empty:
        rem_data = [["Товар", "Остаток"]]
        for _, row in rem_df.iterrows():
            rem_data.append([row['product'], row['remaining']])
        table = Table(rem_data)
        table.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                                   ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                                   ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                                   ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                                   ('FONTSIZE', (0, 0), (-1, -1), 10),
                                   ('GRID', (0, 0), (-1, -1), 1, colors.black)]))
        elements.append(table)
    else:
        elements.append(Paragraph("Остатки не введены", style_normal))
    
    # 2. Бар
    elements.append(Spacer(1, 10))
    elements.append(Paragraph("2. Бар - сверка остатков", style_header))
    bar_df = get_bar_stock_today()
    if not bar_df.empty:
        bar_data = [["Товар", "Начало", "Продано", "Фактически"]]
        for _, row in bar_df.iterrows():
            bar_data.append([row['product'], row['start_stock'], row['sold'], row['actual_stock']])
        table = Table(bar_data, colWidths=[70, 40, 40, 40])
        table.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                                   ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                                   ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                                   ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                                   ('FONTSIZE', (0, 0), (-1, -1), 8),
                                   ('GRID', (0, 0), (-1, -1), 1, colors.black)]))
        elements.append(table)
    else:
        elements.append(Paragraph("Данные по бару не введены", style_normal))
    
    # 3. ПК
    elements.append(Spacer(1, 10))
    elements.append(Paragraph("3. Состояние компьютеров", style_header))
    pc_df = get_pc_status_today()
    if not pc_df.empty:
        pc_data = [["№ ПК", "Статус", "Заметка"]]
        for _, row in pc_df.iterrows():
            pc_data.append([row['pc_number'], row['status'], row['note'] or "-"])
        table = Table(pc_data)
        table.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                                   ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                                   ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                                   ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                                   ('FONTSIZE', (0, 0), (-1, -1), 10),
                                   ('GRID', (0, 0), (-1, -1), 1, colors.black)]))
        elements.append(table)
    else:
        elements.append(Paragraph("Статусы ПК не заполнены", style_normal))
    
    # 4. Игры
    elements.append(Spacer(1, 10))
    elements.append(Paragraph("4. Обновление игр", style_header))
    games_df = get_games_status()
    if not games_df.empty:
        games_data = [["Игра", "Обновлено", "Дата проверки"]]
        for _, row in games_df.iterrows():
            status = "✅" if row['updated'] else "❌"
            games_data.append([row['name'], status, row['last_check'] or "-"])
        table = Table(games_data, colWidths=[120, 50, 80])
        table.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                                   ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                                   ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                                   ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                                   ('FONTSIZE', (0, 0), (-1, -1), 8),
                                   ('GRID', (0, 0), (-1, -1), 1, colors.black)]))
        elements.append(table)
    else:
        elements.append(Paragraph("Список игр не загружен", style_normal))
    
    # 5. Финансовый итог
    elements.append(Spacer(1, 10))
    elements.append(Paragraph("5. Финансовый итог смены", style_header))
    shift_df = get_shift_totals_today()
    if not shift_df.empty:
        row = shift_df.iloc[0]
        total_cash = row['terminal'] + row['cash'] + row['pc_rent'] + row['extras'] + row['food_cash']
        
        fin_data = [
            ["Статья", "Сумма (грн)"],
            ["Терминал (безнал)", f"{row['terminal']:.0f}"],
            ["Наличные", f"{row['cash']:.0f}"],
            ["Аренда ПК", f"{row['pc_rent']:.0f}"],
            ["Допы (печать и т.д.)", f"{row['extras']:.0f}"],
            ["Фуд-корт (выручка)", f"{row['food_cash']:.0f}"],
            ["- Инкассация Фуди", f"-{row['food_incassation']:.0f}"],
            ["", ""],
            ["ОБЩАЯ КАССА", f"{total_cash:.0f}"],
            ["Зарплата", f"{row['salary']:.0f}"],
            ["", ""],
            ["ИТОГОВЫЙ ОСТАТОК", f"{row['remaining_cash']:.0f}"]
        ]
        table = Table(fin_data, colWidths=[150, 100])
        table.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                                   ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                                   ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                                   ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                                   ('FONTSIZE', (0, 0), (-1, -1), 10),
                                   ('GRID', (0, 0), (-1, -1), 1, colors.black),
                                   ('BACKGROUND', (-2, -2), (-1, -1), colors.lightgreen)]))
        elements.append(table)
    else:
        elements.append(Paragraph("Финансовый итог не подведен", style_normal))
    
    doc.build(elements)
    buffer.seek(0)
    return buffer

# --- ИНТЕРФЕЙС STREAMLIT ---

st.title("🎮 Компьютерный клуб - Управление сменой")
st.markdown(f"**Сегодня:** {get_today()}")

# Боковое меню
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🏠 Главная", "🍔 Фуд-корт", "🍫 Бар", "🖥️ ПК", "🎮 Игры"
])

# --- ВКЛАДКА 1: ГЛАВНАЯ ---
with tab1:
    st.header("Управление сменой")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Итоги за сегодня")
        food_total = get_food_total_today()
        st.metric("Выручка Фуди", f"{food_total:.0f} грн")
        
        shift_df = get_shift_totals_today()
        if not shift_df.empty:
            row = shift_df.iloc[0]
            total = row['terminal'] + row['cash'] + row['pc_rent'] + row['extras'] + row['food_cash']
            st.metric("Общая касса", f"{total:.0f} грн")
            st.metric("Зарплата", f"{row['salary']:.0f} грн")
            st.metric("Остаток в кассе", f"{row['remaining_cash']:.0f} грн")
    
    with col2:
        st.subheader("📄 Отчеты")
        if st.button("📥 Скачать PDF-отчет за сегодня"):
            pdf_buffer = generate_pdf_report()
            st.download_button(
                label="✅ Скачать PDF",
                data=pdf_buffer,
                file_name=f"отчет_{get_today()}.pdf",
                mime="application/pdf"
            )
    
    st.divider()
    st.subheader("💰 Закрытие смены (финансовый итог)")
    
    with st.form("shift_close"):
        st.write("Введите итоговые суммы:")
        col3, col4 = st.columns(2)
        with col3:
            terminal = st.number_input("Терминал (безнал)", min_value=0.0, step=50.0, format="%.0f")
            cash = st.number_input("Наличные", min_value=0.0, step=50.0, format="%.0f")
            pc_rent = st.number_input("Аренда ПК", min_value=0.0, step=50.0, format="%.0f")
        with col4:
            extras = st.number_input("Допы (печать и т.д.)", min_value=0.0, step=10.0, format="%.0f")
            food_inc = st.number_input("Инкассация Фуди (забрали)", min_value=0.0, step=50.0, format="%.0f")
        
        # Расчет зарплаты
        food_total_calc = get_food_total_today()
        total_cash_calc = terminal + cash + pc_rent + extras + food_total_calc
        
        if total_cash_calc >= 1200:
            bonus = 100
            if total_cash_calc >= 2000:
                bonus = 200
            salary = 400 + bonus
        else:
            salary = 400
        
        st.info(f"💰 Расчетная зарплата: **{salary} грн** (ставка 400 + бонус за кассу > 1200/2000)")
        
        remaining = total_cash_calc - salary
        
        st.warning(f"💵 Остаток в кассе после выдачи ЗП: **{remaining:.0f} грн**")
        
        if st.form_submit_button("✅ Закрыть смену"):
            if total_cash_calc > 0:
                save_shift_totals(terminal, cash, pc_rent, extras, food_inc, salary, remaining)
                st.success(f"Смена закрыта! ЗП: {salary} грн, Остаток: {remaining:.0f} грн")
                st.balloons()
            else:
                st.error("Ошибка: общая касса не может быть 0")

# --- ВКЛАДКА 2: ФУД-КОРТ ---
with tab2:
    st.header("🍔 Фуд-корт - Продажи")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("➕ Добавить продажу")
        for product, price in FOOD_PRODUCTS.items():
            col_a, col_b = st.columns([3, 1])
            with col_a:
                st.write(f"{product} - {price} грн")
            with col_b:
                if st.button(f"+1", key=f"add_{product}"):
                    add_food_sale(product)
                    st.success(f"✅ {product} добавлен")
                    st.rerun()
    
    with col2:
        st.subheader("📊 Продажи сегодня")
        df = get_food_sales_today()
        if not df.empty:
            display_df = df.copy()
            display_df['Сумма'] = display_df['total_qty'] * display_df['price']
            display_df['total_qty'] = display_df['total_qty'].astype(int)
            display_df['price'] = display_df['price'].map(lambda x: f"{x:.0f} грн")
            display_df['Сумма'] = display_df['Сумма'].map(lambda x: f"{x:.0f} грн")
            st.dataframe(display_df[['product', 'total_qty', 'price', 'Сумма']].rename(
                columns={'product': 'Товар', 'total_qty': 'Кол-во', 'price': 'Цена'}))
            st.metric("Общая выручка Фуди", f"{get_food_total_today():.0f} грн")
        else:
            st.info("Продаж пока нет")
    
    st.divider()
    st.subheader("📦 Остатки продукции на конец дня")
    st.info("Введите фактический остаток каждого товара на полке")
    
    rem_cols = st.columns(3)
    rem_values = {}
    for i, product in enumerate(FOOD_PRODUCTS.keys()):
        with rem_cols[i % 3]:
            rem_values[product] = st.number_input(f"{product}", min_value=0, step=1, key=f"rem_{product}")
    
    if st.button("💾 Сохранить остатки"):
        if all(rem_values.values()):
            save_food_remaining(rem_values)
            st.success("Остатки сохранены")
        else:
            st.warning("Введите все остатки (можно 0)")

# --- ВКЛАДКА 3: БАР ---
with tab3:
    st.header("🍫 Бар - Учет остатков")
    st.info("Сверка: начальный остаток (ввели руками) и фактический остаток")
    
    # Получаем сегодняшние данные
    bar_df = get_bar_stock_today()
    
    if bar_df.empty:
        # Если данных нет - показываем форму ввода
        st.subheader("Введите остатки на начало смены")
        start_cols = st.columns(3)
        start_values = {}
        for i, product in enumerate(BAR_PRODUCTS):
            with start_cols[i % 3]:
                start_values[product] = st.number_input(f"{product}", min_value=0, step=1, key=f"start_{product}")
        
        if st.button("✅ Начать учет (сохранить начальные остатки)"):
            if all(start_values.values()):
                # Сохраняем с одинаковыми началом и фактическим (пока нет продаж)
                conn = sqlite3.connect('club_data.db')
                c = conn.cursor()
                today = get_today()
                for product in BAR_PRODUCTS:
                    c.execute("INSERT INTO bar_stock (date, product, start_stock, actual_stock, sold) VALUES (?, ?, ?, ?, ?)",
                              (today, product, start_values[product], start_values[product], 0))
                conn.commit()
                conn.close()
                st.success("Начальные остатки сохранены! Теперь введите фактические в конце смены")
                st.rerun()
            else:
                st.error("Заполните все поля (можно 0)")
    else:
        # Если данные есть - показываем текущие и предлагаем ввести фактические
        st.subheader("📊 Текущие данные за сегодня")
        st.dataframe(bar_df[['product', 'start_stock', 'sold']].rename(
            columns={'product': 'Товар', 'start_stock': 'Начало', 'sold': 'Продано по учету'}))
        
        st.subheader("✏️ Введите фактические остатки (сверка)")
        actual_cols = st.columns(3)
        actual_values = {}
        for i, product in enumerate(BAR_PRODUCTS):
            with actual_cols[i % 3]:
                default_val = bar_df[bar_df['product'] == product]['actual_stock'].iloc[0] if not bar_df[bar_df['product'] == product].empty else 0
                actual_values[product] = st.number_input(f"{product}", min_value=0, step=1, value=default_val, key=f"actual_{product}")
        
        if st.button("💾 Сохранить фактические остатки"):
            # Обновляем существующие записи
            conn = sqlite3.connect('club_data.db')
            c = conn.cursor()
            today = get_today()
            for product in BAR_PRODUCTS:
                start = bar_df[bar_df['product'] == product]['start_stock'].iloc[0] if not bar_df[bar_df['product'] == product].empty else 0
                sold = start - actual_values[product]
                c.execute("UPDATE bar_stock SET actual_stock=?, sold=? WHERE date=? AND product=?",
                          (actual_values[product], sold, today, product))
            conn.commit()
            conn.close()
            st.success("Фактические остатки сохранены!")
            st.rerun()
        
        # Показываем сверку
        st.subheader("🔍 Сверка остатков")
        check_df = bar_df.copy()
        check_df['Расхождение'] = check_df['start_stock'] - check_df['actual_stock']
        
        # Подсвечиваем расхождения
        for idx, row in check_df.iterrows():
            if row['Расхождение'] != row['sold']:
                check_df.loc[idx, 'Статус'] = '⚠️ Расхождение!'
            else:
                check_df.loc[idx, 'Статус'] = '✅ Ок'
        
        st.dataframe(check_df[['product', 'start_stock', 'actual_stock', 'sold', 'Статус']].rename(
            columns={'product': 'Товар', 'start_stock': 'Начало', 'actual_stock': 'Факт', 'sold': 'Продано'}))

# --- ВКЛАДКА 4: ПК ---
with tab4:
    st.header("🖥️ Состояние компьютеров")
    
    # Статусы для выбора
    status_options = ["Работает отлично", "Проблема с наушниками", "Зависает", "Не включается", "Требуется перезагрузка", "Другое"]
    new_status = st.text_input("➕ Добавить свой статус", placeholder="Напишите новый статус")
    if new_status and st.button("Добавить статус в список"):
        status_options.append(new_status)
        st.success(f"Статус '{new_status}' добавлен!")
    
    st.divider()
    st.subheader("Выберите ПК для отметки")
    
    # Создаем колонки для ПК
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
    st.subheader("📋 Все статусы за сегодня")
    pc_df = get_pc_status_today()
    if not pc_df.empty:
        # Сортируем по номеру ПК
        pc_df['pc_number'] = pc_df['pc_number'].astype(int)
        pc_df = pc_df.sort_values('pc_number')
        st.dataframe(pc_df[['pc_number', 'status', 'note']].rename(
            columns={'pc_number': '№ ПК', 'status': 'Статус', 'note': 'Заметка'}))
    else:
        st.info("Статусы еще не сохранены")

# --- ВКЛАДКА 5: ИГРЫ ---
with tab5:
    st.header("🎮 Обновление игр")
    
    # Инициализируем игры при первом запуске
    init_games()
    
    st.info("Отмечайте галочкой игры, которые обновлены и работают")
    
    games_df = get_games_status()
    
    # Создаем колонки для чек-листа
    game_cols = st.columns(3)
    for i, (_, row) in enumerate(games_df.iterrows()):
        with game_cols[i % 3]:
            with st.container(border=True):
                col_a, col_b = st.columns([4, 1])
                with col_a:
                    st.write(f"**{row['name']}**")
                    if row['last_check']:
                        st.caption(f"Последняя проверка: {row['last_check']}")
                with col_b:
                    updated = st.checkbox("✅", value=bool(row['updated']), key=f"game_{row['name']}")
                    if updated != bool(row['updated']):
                        update_game_status(row['name'], updated)
                        st.rerun()
