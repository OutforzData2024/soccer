import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from collections import defaultdict
import io
import re
import matplotlib.pyplot as plt
from matplotlib.patches import Arc

# Настройка страницы
st.set_page_config(layout="wide", page_title="Футбольная аналитика")

# Получаем настройки из боковой панели
def add_settings_sidebar():
    st.sidebar.title("Настройки анализа")
    
    # Общие настройки
    st.sidebar.header("Общие настройки")
    
    show_help = st.sidebar.checkbox("Показывать подсказки", value=True)
    
    # Настройки визуализации
    st.sidebar.header("Визуализация")
    
    color_scheme = st.sidebar.selectbox(
        "Цветовая схема графиков",
        ["Стандартная", "Командные цвета", "Зеленый-Оранжевый", "Пастельная"]
    )
    
    chart_height = st.sidebar.slider("Высота графиков", 300, 800, 400, 50)
    
    # Настройки анализа
    st.sidebar.header("Анализ")
    
    analysis_detail = st.sidebar.select_slider(
        "Детализация анализа",
        options=["Минимальная", "Средняя", "Подробная"],
        value="Средняя"
    )
    
    # Возвращаем настройки в виде словаря
    return {
        "show_help": show_help,
        "color_scheme": color_scheme,
        "chart_height": chart_height,
        "analysis_detail": analysis_detail
    }

# Получаем цветовую схему на основе настроек
def get_color_scheme(settings, teams=None):
    if settings["color_scheme"] == "Командные цвета" and teams and len(teams) >= 2:
        # Можно настроить цвета команд (пример с Шахтером - оранжево-черный)
        team_colors = {
            "Shakhtar": "#ff6600",  # Оранжевый для Шахтера
            "Kozak": "#1e88e5"  # Синий для Козака (предположим)
        }
        
        return {
            "team1": team_colors.get(teams[0], "#ff6600"),
            "team2": team_colors.get(teams[1], "#1e88e5")
        }
    elif settings["color_scheme"] == "Зеленый-Оранжевый":
        return {"team1": "#15803d", "team2": "#c2410c"}
    elif settings["color_scheme"] == "Пастельная":
        return {"team1": "#0ea5e9", "team2": "#f472b6"}
    else:  # Стандартная
        return {"team1": "#0088FE", "team2": "#FF8042"}

# Функция для анализа данных футбольного матча
def analyze_match_data(df):
    """
    Анализирует данные футбольного матча из CSV и возвращает статистику для обеих команд.
    """
    # Определяем команды
    teams = list(df['Team_1'].unique())
    
    # Инициализируем словарь для статистики
    team_stats = {team: {} for team in teams}
    
    # Основные счетчики для общей статистики
    for team in teams:
        team_stats[team]['shots'] = 0
        team_stats[team]['shots_on_target'] = 0
        team_stats[team]['shots_off_target'] = 0
        team_stats[team]['blocked_shots'] = 0
        team_stats[team]['goals'] = 0
        team_stats[team]['passes'] = 0
        team_stats[team]['successful_passes'] = 0
        team_stats[team]['crosses'] = 0
        team_stats[team]['successful_crosses'] = 0
        team_stats[team]['tackles'] = 0
        team_stats[team]['successful_tackles'] = 0
        team_stats[team]['interceptions'] = 0
        team_stats[team]['fouls'] = 0
        team_stats[team]['corners'] = 0
        team_stats[team]['offsides'] = 0
        team_stats[team]['possession_time'] = 0
        team_stats[team]['player_stats'] = {}
        team_stats[team]['pass_zones'] = defaultdict(int)
        team_stats[team]['shot_locations'] = defaultdict(int)
        team_stats[team]['shot_types'] = defaultdict(int)
        team_stats[team]['pressure_stats'] = {'under_pressure': 0, 'no_pressure': 0}
        team_stats[team]['half_stats'] = {1: {}, 2: {}}
        
        # Инициализируем статистику по таймам
        for half in [1, 2]:
            team_stats[team]['half_stats'][half] = {
                'shots': 0,
                'goals': 0,
                'passes': 0,
                'successful_passes': 0,
                'possession_time': 0
            }
    
    # Анализируем каждое событие
    for _, row in df.iterrows():
        team = row['Team_1']
        event = row['Event_Catalog']
        match_half = row.get('Half', 1)  # По умолчанию первый тайм, если нет данных
        
        # Обновляем статистику по игрокам
        player_name = row['Player_Name_1']
        if player_name not in team_stats[team]['player_stats']:
            team_stats[team]['player_stats'][player_name] = {
                'shots': 0,
                'goals': 0,
                'passes': 0,
                'successful_passes': 0,
                'tackles': 0,
                'interceptions': 0
            }
        
        # Анализ событий
        if event == 'Shot':
            team_stats[team]['shots'] += 1
            team_stats[team]['half_stats'][match_half]['shots'] += 1
            team_stats[team]['player_stats'][player_name]['shots'] += 1
            
            # Типы ударов
            shot_type = row.get('Type_Shots', 'Unknown')
            team_stats[team]['shot_types'][shot_type] += 1
            
            # Местоположение удара
            shot_location = row.get('Shot_Location', 'Unknown')
            team_stats[team]['shot_locations'][shot_location] += 1
            
            # Результат удара
            result = row.get('Results', '')
            if result == 'Goal':
                team_stats[team]['goals'] += 1
                team_stats[team]['half_stats'][match_half]['goals'] += 1
                team_stats[team]['player_stats'][player_name]['goals'] += 1
                team_stats[team]['shots_on_target'] += 1
            elif result == 'On Target':
                team_stats[team]['shots_on_target'] += 1
            elif result == 'Off Target':
                team_stats[team]['shots_off_target'] += 1
            elif result == 'Blocked':
                team_stats[team]['blocked_shots'] += 1
        
        elif event == 'Pass':
            team_stats[team]['passes'] += 1
            team_stats[team]['half_stats'][match_half]['passes'] += 1
            team_stats[team]['player_stats'][player_name]['passes'] += 1
            
            # Зона паса (используем координаты X2, Y2)
            x2, y2 = row.get('X2', 0), row.get('Y2', 0)
            zone = get_field_zone(x2, y2)
            team_stats[team]['pass_zones'][zone] += 1
            
            # Тип паса
            pass_type = row.get('Type', 'Normal')
            
            # Успешные пасы
            pass_outcome = row.get('Pass_Outcome', '')
            if pass_outcome == 'Successful':
                team_stats[team]['successful_passes'] += 1
                team_stats[team]['half_stats'][match_half]['successful_passes'] += 1
                team_stats[team]['player_stats'][player_name]['successful_passes'] += 1
            
            # Кросс
            if pass_type == 'Cross':
                team_stats[team]['crosses'] += 1
                if pass_outcome == 'Successful':
                    team_stats[team]['successful_crosses'] += 1
            
            # Статистика под давлением
            pressure = row.get('Pressure', 'No')
            if pressure == 'Yes':
                team_stats[team]['pressure_stats']['under_pressure'] += 1
            else:
                team_stats[team]['pressure_stats']['no_pressure'] += 1
        
        elif event == 'Tackle':
            team_stats[team]['tackles'] += 1
            team_stats[team]['player_stats'][player_name]['tackles'] += 1
            
            # Успешные отборы
            if row.get('Results', '') == 'Successful':
                team_stats[team]['successful_tackles'] += 1
        
        elif event == 'Interception':
            team_stats[team]['interceptions'] += 1
            team_stats[team]['player_stats'][player_name]['interceptions'] += 1
        
        elif event == 'Foul':
            team_stats[team]['fouls'] += 1
        
        elif event == 'Corner':
            team_stats[team]['corners'] += 1
        
        elif event == 'Offside':
            team_stats[team]['offsides'] += 1
    
    # Расчет процентов и соотношений
    for team in teams:
        # Точность ударов
        if team_stats[team]['shots'] > 0:
            team_stats[team]['shot_accuracy'] = round(
                team_stats[team]['shots_on_target'] / team_stats[team]['shots'] * 100, 1
            )
        else:
            team_stats[team]['shot_accuracy'] = 0
        
        # Точность пасов
        if team_stats[team]['passes'] > 0:
            team_stats[team]['pass_accuracy'] = round(
                team_stats[team]['successful_passes'] / team_stats[team]['passes'] * 100, 1
            )
        else:
            team_stats[team]['pass_accuracy'] = 0
        
        # Точность кроссов
        if team_stats[team]['crosses'] > 0:
            team_stats[team]['cross_accuracy'] = round(
                team_stats[team]['successful_crosses'] / team_stats[team]['crosses'] * 100, 1
            )
        else:
            team_stats[team]['cross_accuracy'] = 0
        
        # Точность отборов
        if team_stats[team]['tackles'] > 0:
            team_stats[team]['tackle_success'] = round(
                team_stats[team]['successful_tackles'] / team_stats[team]['tackles'] * 100, 1
            )
        else:
            team_stats[team]['tackle_success'] = 0
        
        # Статистика под давлением
        total_pressure_events = (team_stats[team]['pressure_stats']['under_pressure'] + 
                               team_stats[team]['pressure_stats']['no_pressure'])
        if total_pressure_events > 0:
            team_stats[team]['pressure_percentage'] = round(
                team_stats[team]['pressure_stats']['under_pressure'] / total_pressure_events * 100, 1
            )
        else:
            team_stats[team]['pressure_percentage'] = 0
            
        # Расчет статистики для игроков
        for player in team_stats[team]['player_stats']:
            player_stats = team_stats[team]['player_stats'][player]
            
            # Точность пасов игроков
            if player_stats['passes'] > 0:
                player_stats['pass_accuracy'] = round(
                    player_stats['successful_passes'] / player_stats['passes'] * 100, 1
                )
            else:
                player_stats['pass_accuracy'] = 0
                
            # Эффективность ударов игроков
            if player_stats['shots'] > 0:
                player_stats['goal_conversion'] = round(
                    player_stats['goals'] / player_stats['shots'] * 100, 1
                )
            else:
                player_stats['goal_conversion'] = 0
    
    return team_stats

# Функция для определения зоны поля на основе координат
def get_field_zone(x, y):
    """
    Определяет зону поля на основе координат.
    Предполагаем, что координаты нормализованы от 0 до 100.
    """
    # Упрощенная модель с 9 зонами (3x3)
    if x < 33:
        if y < 33:
            return "Defensive Left"
        elif y < 66:
            return "Defensive Center"
        else:
            return "Defensive Right"
    elif x < 66:
        if y < 33:
            return "Middle Left"
        elif y < 66:
            return "Middle Center"
        else:
            return "Middle Right"
    else:
        if y < 33:
            return "Attacking Left"
        elif y < 66:
            return "Attacking Center"
        else:
            return "Attacking Right"

# Функция для создания графика статистики команд
def create_team_stats_chart(team_stats, colors, height=400):
    """
    Создает график сравнения основной статистики команд.
    """
    teams = list(team_stats.keys())
    
    # Создаем данные для графика
    data = []
    for team in teams:
        data.append({
            'Команда': team,
            'Показатель': 'Удары',
            'Значение': team_stats[team].get('shots', 0)
        })
        data.append({
            'Команда': team,
            'Показатель': 'Удары в створ',
            'Значение': team_stats[team].get('shots_on_target', 0)
        })
        data.append({
            'Команда': team,
            'Показатель': 'Голы',
            'Значение': team_stats[team].get('goals', 0)
        })
        data.append({
            'Команда': team,
            'Показатель': 'Угловые',
            'Значение': team_stats[team].get('corners', 0)
        })
        data.append({
            'Команда': team,
            'Показатель': 'Офсайды',
            'Значение': team_stats[team].get('offsides', 0)
        })
        data.append({
            'Команда': team,
            'Показатель': 'Фолы',
            'Значение': team_stats[team].get('fouls', 0)
        })
    
    df = pd.DataFrame(data)
    
    # Создаем график
    fig = px.bar(
        df, 
        x='Показатель', 
        y='Значение', 
        color='Команда',
        barmode='group',
        color_discrete_map={teams[0]: colors['team1'], teams[1]: colors['team2']} if len(teams) > 1 else None,
        height=height
    )
    
    fig.update_layout(
        title='Основная статистика команд',
        xaxis_title=None,
        yaxis_title='Количество',
        legend_title='Команда'
    )
    
    return fig

# Функция для создания графика пасов
def create_pass_stats_chart(team_stats, colors, height=400):
    """
    Создает график статистики пасов команд.
    """
    teams = list(team_stats.keys())
    
    # Создаем данные для графика
    data = []
    for team in teams:
        data.append({
            'Команда': team,
            'Показатель': 'Всего пасов',
            'Значение': team_stats[team].get('passes', 0)
        })
        data.append({
            'Команда': team,
            'Показатель': 'Точность пасов (%)',
            'Значение': team_stats[team].get('pass_accuracy', 0)
        })
        data.append({
            'Команда': team,
            'Показатель': 'Кроссы',
            'Значение': team_stats[team].get('crosses', 0)
        })
        data.append({
            'Команда': team,
            'Показатель': 'Точность кроссов (%)',
            'Значение': team_stats[team].get('cross_accuracy', 0)
        })
        data.append({
            'Команда': team,
            'Показатель': 'Пасы под давлением (%)',
            'Значение': team_stats[team].get('pressure_percentage', 0)
        })
    
    df = pd.DataFrame(data)
    
    # Создаем график
    fig = px.bar(
        df, 
        x='Показатель', 
        y='Значение', 
        color='Команда',
        barmode='group',
        color_discrete_map={teams[0]: colors['team1'], teams[1]: colors['team2']} if len(teams) > 1 else None,
        height=height
    )
    
    fig.update_layout(
        title='Статистика пасов',
        xaxis_title=None,
        yaxis_title='Значение',
        legend_title='Команда'
    )
    
    return fig

# Функция для создания тепловой карты пасов
def create_pass_heatmap(team_stats, team, color, height=500):
    """
    Создает тепловую карту пасов на футбольном поле.
    """
    # Получаем данные о зонах пасов
    pass_zones = team_stats[team].get('pass_zones', {})
    total_passes = sum(pass_zones.values()) if pass_zones else 0
    
    # Создаем фигуру
    fig = go.Figure()
    
    # Создаем сетку данных для тепловой карты
    grid_size = 10
    x = np.linspace(0, 100, grid_size)
    y = np.linspace(0, 100, grid_size)
    z = np.zeros((grid_size, grid_size))
    
    # Заполняем тепловую карту
    zone_to_coords = {
        "Defensive Left": (16, 16),
        "Defensive Center": (16, 50),
        "Defensive Right": (16, 84),
        "Middle Left": (50, 16),
        "Middle Center": (50, 50),
        "Middle Right": (50, 84),
        "Attacking Left": (84, 16),
        "Attacking Center": (84, 50),
        "Attacking Right": (84, 84)
    }
    
    for zone, count in pass_zones.items():
        if zone in zone_to_coords and total_passes > 0:
            i, j = zone_to_coords[zone]
            # Находим ближайшие индексы в нашей сетке
            i_idx = int(i / 100 * (grid_size - 1))
            j_idx = int(j / 100 * (grid_size - 1))
            
            # Добавляем "тепло" пропорционально количеству пасов
            if i_idx < grid_size and j_idx < grid_size:
                z[i_idx, j_idx] = count / total_passes * 100
    
    # Добавляем тепловую карту
    fig.add_trace(go.Heatmap(
        z=z,
        x=y,  # Обратите внимание на переворот x и y для правильного отображения поля
        y=x,
        colorscale=[[0, 'rgba(255,255,255,0)'], [1, color]],
        showscale=True,
        colorbar=dict(title="% пасов")
    ))
    
    # Добавляем контуры футбольного поля
    # Внешние границы поля
    fig.add_shape(type="rect", x0=0, y0=0, x1=100, y1=100, line=dict(color="white"), fillcolor="rgba(0,100,0,0.3)")
    
    # Центральный круг
    fig.add_shape(type="circle", x0=40, y0=40, x1=60, y1=60, line=dict(color="white"))
    
    # Центральная линия
    fig.add_shape(type="line", x0=0, y0=50, x1=100, y1=50, line=dict(color="white"))
    
    # Штрафные площади
    fig.add_shape(type="rect", x0=0, y0=30, x1=16, y1=70, line=dict(color="white"))
    fig.add_shape(type="rect", x0=84, y0=30, x1=100, y1=70, line=dict(color="white"))
    
    # Настраиваем макет
    fig.update_layout(
        title=f"Тепловая карта пасов - {team}",
        height=height,
        xaxis=dict(showgrid=False, zeroline=False, range=[0, 100], scaleanchor="y", scaleratio=1),
        yaxis=dict(showgrid=False, zeroline=False, range=[0, 100]),
        margin=dict(l=0, r=0, t=40, b=0)
    )
    
    return fig

# Функция для создания диаграммы типов ударов
def create_shot_types_chart(team_stats, team, color, height=400):
    """
    Создает диаграмму типов ударов команды.
    """
    shot_types = team_stats[team].get('shot_types', {})
    
    if not shot_types:
        fig = go.Figure()
        fig.update_layout(
            title=f"Нет данных о типах ударов для {team}",
            height=height
        )
        return fig
    
    # Преобразуем словарь в списки для построения графика
    labels = list(shot_types.keys())
    values = list(shot_types.values())
    
    # Создаем круговую диаграмму
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=.3,
        marker_colors=[color, color+'90', color+'70', color+'50', color+'30']
    )])
    
    fig.update_layout(
        title=f"Типы ударов - {team}",
        height=height
    )
    
    return fig

# Функция для создания диаграммы результатов ударов
def create_shot_outcomes_chart(team_stats, team, color, height=400):
    """
    Создает диаграмму результатов ударов команды.
    """
    # Собираем данные о результатах ударов
    shot_outcomes = {
        'Голы': team_stats[team].get('goals', 0),
        'Удары в створ (не голы)': team_stats[team].get('shots_on_target', 0) - team_stats[team].get('goals', 0),
        'Удары мимо': team_stats[team].get('shots_off_target', 0),
        'Заблокированные удары': team_stats[team].get('blocked_shots', 0)
    }
    
    # Преобразуем словарь в списки для построения графика
    labels = list(shot_outcomes.keys())
    values = list(shot_outcomes.values())
    
    # Цвета для разных исходов
    colors = ['#2ecc71', '#3498db', '#e74c3c', '#95a5a6']
    
    # Создаем круговую диаграмму
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=.3,
        marker_colors=colors
    )])
    
    fig.update_layout(
        title=f"Результаты ударов - {team}",
        height=height
    )
    
    return fig

# Функция для создания графика статистики игроков
def create_player_stats_chart(team_stats, team, category, color, height=500, top_n=10):
    """
    Создает график статистики игроков по выбранной категории.
    
    Args:
        team_stats: Статистика команд
        team: Команда для анализа
        category: Категория статистики ('goals', 'passes', 'pass_accuracy', etc.)
        color: Цвет для графика
        height: Высота графика
        top_n: Количество лучших игроков для отображения
    """
    player_stats = team_stats[team].get('player_stats', {})
    
    # Категория для отображения
    category_display = {
        'goals': 'Голы',
        'shots': 'Удары',
        'passes': 'Пасы',
        'pass_accuracy': 'Точность пасов (%)',
        'tackles': 'Отборы',
        'interceptions': 'Перехваты',
        'goal_conversion': 'Конверсия ударов в голы (%)'
    }
    
    # Создаем данные для графика
    data = []
    for player, stats in player_stats.items():
        if category in stats:
            data.append({
                'Игрок': player,
                category_display.get(category, category): stats[category]
            })
    
    # Сортируем по убыванию и берем топ N
    data = sorted(data, key=lambda x: x[category_display.get(category, category)], reverse=True)[:top_n]
    
    if not data:
        fig = go.Figure()
        fig.update_layout(
            title=f"Нет данных о {category_display.get(category, category)} для игроков {team}",
            height=height
        )
        return fig
    
    # Создаем DataFrame
    df = pd.DataFrame(data)
    
    # Создаем горизонтальную столбчатую диаграмму
    fig = px.bar(
        df,
        y='Игрок',
        x=category_display.get(category, category),
        color_discrete_sequence=[color],
        height=height,
        orientation='h'
    )
    
    fig.update_layout(
        title=f"Топ-{len(data)} игроков по {category_display.get(category, category).lower()} - {team}",
        xaxis_title=category_display.get(category, category),
        yaxis_title=None
    )
    
    return fig

# Функция для создания графика сравнения статистики по таймам
def create_half_comparison_chart(team_stats, colors, height=400):
    """
    Создает график сравнения статистики команд по таймам.
    """
    teams = list(team_stats.keys())
    
    # Создаем данные для графика
    data = []
    for team in teams:
        for half in [1, 2]:
            half_stats = team_stats[team]['half_stats'][half]
            
            data.append({
                'Команда': team,
                'Тайм': f"{half} тайм",
                'Метрика': 'Удары',
                'Значение': half_stats.get('shots', 0)
            })
            
            data.append({
                'Команда': team,
                'Тайм': f"{half} тайм",
                'Метрика': 'Голы',
                'Значение': half_stats.get('goals', 0)
            })
            
            data.append({
                'Команда': team,
                'Тайм': f"{half} тайм",
                'Метрика': 'Пасы / 10',  # Делим на 10 для лучшей визуализации
                'Значение': half_stats.get('passes', 0) / 10
            })
            
            data.append({
                'Команда': team,
                'Тайм': f"{half} тайм",
                'Метрика': 'Точность пасов (%)',
                'Значение': half_stats.get('passes', 0) > 0 and half_stats.get('successful_passes', 0) / half_stats.get('passes', 0) * 100 or 0
            })
    
    df = pd.DataFrame(data)
    
    # Создаем график
    fig = px.bar(
        df, 
        x='Метрика', 
        y='Значение', 
        color='Команда',
        barmode='group',
        facet_col='Тайм',
        color_discrete_map={teams[0]: colors['team1'], teams[1]: colors['team2']} if len(teams) > 1 else None,
        height=height
    )
    
    fig.update_layout(
        title='Сравнение по таймам',
        xaxis_title=None,
        yaxis_title='Значение',
        legend_title='Команда'
    )
    
    return fig

# Функция для генерации рекомендаций и аналитических выводов
def generate_team_insights(team_stats, opponent_stats=None, detail_level="Средняя"):
    """
    Генерирует аналитические выводы и рекомендации для команды на основе статистики.
    
    Args:
        team_stats: Статистика команды
        opponent_stats: Статистика соперника (опционально)
        detail_level: Уровень детализации ("Минимальная", "Средняя", "Подробная")
    """
    insights = {
        'strengths': [],        # Сильные стороны
        'weaknesses': [],       # Слабые стороны
        'tactics': [],          # Тактические наблюдения
        'key_players': [],      # Ключевые игроки
        'improvement_areas': [] # Области для улучшения
    }
    
    # Анализ атаки
    if team_stats.get('shots', 0) > 0:
        # Эффективность атаки
        shot_accuracy = team_stats.get('shot_accuracy', 0)
        if shot_accuracy > 60:
            insights['strengths'].append(
                f"Высокая точность ударов ({shot_accuracy}%). "
                f"Команда эффективно создаёт качественные моменты."
            )
        elif shot_accuracy < 30:
            insights['weaknesses'].append(
                f"Низкая точность ударов ({shot_accuracy}%). "
                f"Стоит поработать над качеством завершения атак."
            )
            insights['improvement_areas'].append("Точность ударов и выбор позиции для завершения атак")
        
        # Конверсия моментов
        if team_stats.get('shots_on_target', 0) > 0:
            goal_conversion = team_stats.get('goals', 0) / team_stats.get('shots_on_target', 0) * 100
            if goal_conversion > 30:
                insights['strengths'].append(
                    f"Высокая реализация моментов ({goal_conversion:.1f}% ударов в створ превращаются в голы). "
                    f"Команда эффективно завершает атаки."
                )
            elif goal_conversion < 10:
                insights['weaknesses'].append(
                    f"Низкая реализация моментов ({goal_conversion:.1f}% ударов в створ превращаются в голы). "
                    f"Необходимо улучшить завершение атак."
                )
                insights['improvement_areas'].append("Улучшение реализации голевых моментов")
    
    # Анализ владения мячом и пасов
    if team_stats.get('passes', 0) > 0:
        pass_accuracy = team_stats.get('pass_accuracy', 0)
        if pass_accuracy > 80:
            insights['strengths'].append(
                f"Высокая точность пасов ({pass_accuracy}%). "
                f"Команда хорошо контролирует мяч."
            )
        elif pass_accuracy < 60:
            insights['weaknesses'].append(
                f"Низкая точность пасов ({pass_accuracy}%). "
                f"Стоит поработать над контролем мяча."
            )
            insights['improvement_areas'].append("Улучшение точности пасов и контроля мяча")
        
        # Анализ пасов под давлением
        pressure_percentage = team_stats.get('pressure_percentage', 0)
        if pressure_percentage > 50 and pass_accuracy > 70:
            insights['strengths'].append(
                f"Команда хорошо справляется с прессингом соперника "
                f"({pressure_percentage}% пасов под давлением, точность {pass_accuracy}%)."
            )
        elif pressure_percentage > 50 and pass_accuracy < 60:
            insights['weaknesses'].append(
                f"Команда испытывает сложности при прессинге соперника "
                f"({pressure_percentage}% пасов под давлением, точность {pass_accuracy}%)."
            )
            insights['improvement_areas'].append("Улучшение игры под прессингом")
    
    # Сравнение с соперником (если доступно)
    if opponent_stats:
        # Сравнение ударов
        team_shots = team_stats.get('shots', 0)
        opponent_shots = opponent_stats.get('shots', 0)
        
        if team_shots > opponent_shots * 1.5:
            insights['strengths'].append(
                f"Значительное преимущество по ударам ({team_shots} против {opponent_shots}). "
                f"Команда доминировала в атаке."
            )
            insights['tactics'].append(
                "Продолжать атакующий стиль игры, который приносит много моментов."
            )
        elif team_shots * 1.5 < opponent_shots:
            insights['weaknesses'].append(
                f"Значительное отставание по ударам ({team_shots} против {opponent_shots}). "
                f"Команда уступила в атаке."
            )
            insights['tactics'].append(
                "Необходимо улучшить создание атакующих моментов."
            )
        
        # Сравнение по таймам
        team_first_half_shots = team_stats['half_stats'][1].get('shots', 0)
        team_second_half_shots = team_stats['half_stats'][2].get('shots', 0)
        
        if team_first_half_shots * 1.5 < team_second_half_shots:
            insights['tactics'].append(
                f"Команда значительно усилила атаку во втором тайме "
                f"({team_first_half_shots} ударов в первом тайме, {team_second_half_shots} во втором)."
            )
        elif team_first_half_shots > team_second_half_shots * 1.5:
            insights['tactics'].append(
                f"Команда ослабила атаку во втором тайме "
                f"({team_first_half_shots} ударов в первом тайме, {team_second_half_shots} во втором)."
            )
            insights['improvement_areas'].append("Поддержание интенсивности атаки на протяжении всего матча")
    
    # Анализ ключевых игроков
    player_stats = team_stats.get('player_stats', {})
    if player_stats:
        # Лучшие бомбардиры
        goal_scorers = [(player, stats.get('goals', 0)) for player, stats in player_stats.items() if stats.get('goals', 0) > 0]
        if goal_scorers:
            goal_scorers.sort(key=lambda x: x[1], reverse=True)
            top_scorer, goals = goal_scorers[0]
            insights['key_players'].append(
                f"{top_scorer} - лучший бомбардир команды с {goals} голами."
            )
        
        # Лучшие по созданию моментов
        passers = [(player, stats.get('passes', 0), stats.get('pass_accuracy', 0)) 
                   for player, stats in player_stats.items() if stats.get('passes', 0) > 10]
        if passers:
            passers.sort(key=lambda x: x[1], reverse=True)
            top_passer, passes, accuracy = passers[0]
            insights['key_players'].append(
                f"{top_passer} - ключевой распасовщик с {passes} пасами (точность {accuracy}%)."
            )
        
        # Лучшие по отборам
        tacklers = [(player, stats.get('tackles', 0) + stats.get('interceptions', 0)) 
                    for player, stats in player_stats.items() if stats.get('tackles', 0) + stats.get('interceptions', 0) > 0]
        if tacklers:
            tacklers.sort(key=lambda x: x[1], reverse=True)
            top_tackler, tackles = tacklers[0]
            insights['key_players'].append(
                f"{top_tackler} - лучший в отборе мяча с {tackles} успешными действиями."
            )
    
    # Фильтрация инсайтов в соответствии с уровнем детализации
    if detail_level == "Минимальная":
        # Для минимальной детализации оставляем только самые важные выводы
        for category in insights:
            insights[category] = insights[category][:1]
    elif detail_level == "Средняя":
        # Для средней детализации ограничиваем количество выводов
        for category in insights:
            insights[category] = insights[category][:2]
    
    return insights

# Функция для отображения аналитических выводов
def display_team_insights(insights, detail_level):
    """
    Отображает аналитические выводы для команды.
    """
    if detail_level == "Минимальная":
        # Для минимальной детализации показываем только самое важное
        st.subheader("Ключевые выводы")
        
        # Объединяем все в один список
        all_insights = []
        for category, items in insights.items():
            all_insights.extend(items)
        
        # Выбираем максимум 3 самых важных вывода
        for insight in all_insights[:3]:
            st.write(f"• {insight}")
    else:
        # Для средней и подробной детализации показываем по категориям
        if insights['strengths']:
            st.subheader("💪 Сильные стороны")
            for strength in insights['strengths']:
                st.write(f"• {strength}")
        
        if insights['weaknesses']:
            st.subheader("⚠️ Слабые стороны")
            for weakness in insights['weaknesses']:
                st.write(f"• {weakness}")
        
        if insights['tactics']:
            st.subheader("🎯 Тактические наблюдения")
            for tactic in insights['tactics']:
                st.write(f"• {tactic}")
        
        if insights['key_players']:
            st.subheader("⭐ Ключевые игроки")
            for player in insights['key_players']:
                st.write(f"• {player}")
        
        if insights['improvement_areas']:
            st.subheader("🔄 Области для улучшения")
            for area in insights['improvement_areas']:
                st.write(f"• {area}")

# Функция для отображения тепловой карты ударов
def create_shot_heatmap(team_stats, team, color, height=500):
    """
    Создает тепловую карту ударов на футбольном поле.
    """
    # Получаем данные о местоположении ударов
    # Предположим, что у нас есть данные об ударах с координатами
    shot_locations = team_stats[team].get('shot_locations', {})
    total_shots = sum(shot_locations.values()) if shot_locations else 0
    
    if total_shots == 0:
        # Если нет данных, создаем пустую фигуру
        fig = go.Figure()
        fig.update_layout(
            title=f"Нет данных о расположении ударов для {team}",
            height=height
        )
        return fig
    
    # Создаем фигуру с футбольным полем
    fig = go.Figure()
    
    # Добавляем поле
    # Внешние границы
    fig.add_shape(type="rect", x0=0, y0=0, x1=100, y1=100, line=dict(color="white"), fillcolor="rgba(0,100,0,0.3)")
    
    # Штрафные площади
    fig.add_shape(type="rect", x0=0, y0=30, x1=16, y1=70, line=dict(color="white"))
    fig.add_shape(type="rect", x0=84, y0=30, x1=100, y1=70, line=dict(color="white"))
    
    # Ворота
    fig.add_shape(type="rect", x0=0, y0=45, x1=1, y1=55, line=dict(color="white"))
    fig.add_shape(type="rect", x0=99, y0=45, x1=100, y1=55, line=dict(color="white"))
    
    # Создаем маркеры для ударов
    # Преобразуем данные о местоположении ударов в координаты
    # Пример маппинга зон на координаты (упрощенно)
    location_to_coords = {
        "Inside Box": (90, 50),
        "Outside Box": (75, 50),
        "Left Wing": (80, 25),
        "Right Wing": (80, 75),
        "Center": (70, 50)
    }
    
    for location, count in shot_locations.items():
        if location in location_to_coords:
            x, y = location_to_coords[location]
            normalized_count = count / total_shots * 100
            
            # Добавляем маркер для удара
            size = max(10, normalized_count)  # Минимальный размер 10
            
            fig.add_trace(go.Scatter(
                x=[y],  # Swap x and y for football field orientation
                y=[x],
                mode="markers",
                marker=dict(
                    size=size,
                    color=color,
                    opacity=0.7,
                    line=dict(width=1, color="white")
                ),
                text=f"{location}: {count} ударов ({normalized_count:.1f}%)",
                hoverinfo="text",
                showlegend=False
            ))
    
    # Настраиваем макет
    fig.update_layout(
        title=f"Расположение ударов - {team}",
        height=height,
        xaxis=dict(showgrid=False, zeroline=False, range=[0, 100], showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, range=[0, 100], showticklabels=False, scaleanchor="x", scaleratio=1),
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=0, r=0, t=40, b=0)
    )
    
    return fig

# Основная функция приложения
def main():
    st.title("Футбольная аналитика")
    
    # Добавляем настройки в сайдбар
    settings = add_settings_sidebar()
    
    # Загрузка данных
    uploaded_file = st.file_uploader("Загрузите CSV файл с данными матча", type=['csv'])
    
    # Показываем подсказку, если включено
    if settings["show_help"]:
        st.info("""
        Загрузите CSV файл с данными футбольного матча. Файл должен содержать следующие столбцы:
        - Time: Время события
        - Match Time: Игровое время
        - Half: Тайм (1 или 2)
        - Team_1: Название команды, выполняющей действие
        - Player_Name_1: Имя игрока, выполняющего действие
        - X1, Y1: Координаты начала действия
        - X2, Y2: Координаты конца действия (для пасов)
        - Event_Catalog: Тип события (Shot, Pass, Tackle и т.д.)
        - Type: Подтип события
        - Type_Shots: Тип удара
        - Results: Результат действия
        """)
    
    if uploaded_file is not None:
        try:
            # Чтение данных
            df = pd.read_csv(uploaded_file)
            
            # Проверка обязательных столбцов
            required_columns = ['Team_1', 'Player_Name_1', 'Event_Catalog']
            if not all(col in df.columns for col in required_columns):
                st.error("Загруженный файл не содержит необходимых столбцов для анализа")
                return
            
            # Анализ данных
            team_stats = analyze_match_data(df)
            teams = list(team_stats.keys())
            
            if len(teams) == 0:
                st.error("Не удалось найти информацию о командах в данных")
                return
            
            # Получаем цветовую схему
            color_scheme = get_color_scheme(settings, teams)
            
            # Показываем общую информацию и счет
            st.header("Общая информация")
            
            col1, col2 = st.columns(2)
            with col1:
                st.subheader(f"{teams[0]}")
                goals1 = team_stats[teams[0]].get('goals', 0)
                st.write(f"Голы: {goals1}")
                st.write(f"Удары (в створ): {team_stats[teams[0]].get('shots', 0)} ({team_stats[teams[0]].get('shots_on_target', 0)})")
                st.write(f"Точность пасов: {team_stats[teams[0]].get('pass_accuracy', 0)}%")
                st.write(f"Угловые: {team_stats[teams[0]].get('corners', 0)}")
            
            if len(teams) > 1:
                with col2:
                    st.subheader(f"{teams[1]}")
                    goals2 = team_stats[teams[1]].get('goals', 0)
                    st.write(f"Голы: {goals2}")
                    st.write(f"Удары (в створ): {team_stats[teams[1]].get('shots', 0)} ({team_stats[teams[1]].get('shots_on_target', 0)})")
                    st.write(f"Точность пасов: {team_stats[teams[1]].get('pass_accuracy', 0)}%")
                    st.write(f"Угловые: {team_stats[teams[1]].get('corners', 0)}")
            
            # Отображаем счет крупно
            if len(teams) > 1:
                st.header(f"{teams[0]} {goals1} - {goals2} {teams[1]}")
            
            # Визуализации
            st.header("Визуализация данных")
            
            # График основной статистики команд
            st.plotly_chart(create_team_stats_chart(team_stats, color_scheme, settings["chart_height"]), use_container_width=True)
            
            # График статистики пасов
            st.plotly_chart(create_pass_stats_chart(team_stats, color_scheme, settings["chart_height"]), use_container_width=True)
            
            # График сравнения статистики по таймам
            st.plotly_chart(create_half_comparison_chart(team_stats, color_scheme, settings["chart_height"]), use_container_width=True)
            
            # Детальная статистика для каждой команды в отдельных вкладках
            st.header("Детальная статистика команд")
            
            team_tabs = st.tabs(teams)
            for i, team in enumerate(teams):
                with team_tabs[i]:
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.plotly_chart(
                            create_shot_types_chart(
                                team_stats, team, 
                                color_scheme['team1'] if i == 0 else color_scheme['team2'],
                                settings["chart_height"]
                            ),
                            use_container_width=True
                        )
                    
                    with col2:
                        st.plotly_chart(
                            create_shot_outcomes_chart(
                                team_stats, team, 
                                color_scheme['team1'] if i == 0 else color_scheme['team2'],
                                settings["chart_height"]
                            ),
                            use_container_width=True
                        )
                    
                    # Тепловые карты
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.plotly_chart(
                            create_pass_heatmap(
                                team_stats, team, 
                                color_scheme['team1'] if i == 0 else color_scheme['team2'],
                                settings["chart_height"]
                            ),
                            use_container_width=True
                        )
                    
                    with col2:
                        st.plotly_chart(
                            create_shot_heatmap(
                                team_stats, team, 
                                color_scheme['team1'] if i == 0 else color_scheme['team2'],
                                settings["chart_height"]
                            ),
                            use_container_width=True
                        )
                    
                    # Статистика игроков
                    st.subheader("Статистика игроков")
                    
                    stat_category = st.selectbox(
                        "Выберите показатель для анализа игроков",
                        ["goals", "shots", "passes", "pass_accuracy", "tackles", "interceptions", "goal_conversion"],
                        format_func=lambda x: {
                            "goals": "Голы",
                            "shots": "Удары",
                            "passes": "Пасы",
                            "pass_accuracy": "Точность пасов (%)",
                            "tackles": "Отборы",
                            "interceptions": "Перехваты",
                            "goal_conversion": "Конверсия ударов в голы (%)"
                        }.get(x, x),
                        key=f"stat_select_{team}"
                    )
                    
                    st.plotly_chart(
                        create_player_stats_chart(
                            team_stats, team, 
                            stat_category,
                            color_scheme['team1'] if i == 0 else color_scheme['team2'],
                            settings["chart_height"]
                        ),
                        use_container_width=True
                    )
            
            # Аналитические выводы
            st.header("Аналитические выводы")
            
            team_insight_tabs = st.tabs(teams)
            for i, team in enumerate(teams):
                with team_insight_tabs[i]:
                    # Генерируем выводы
                    opponent = teams[1-i] if len(teams) > 1 and i < len(teams) - 1 else None
                    opponent_stats = team_stats[opponent] if opponent else None
                    
                    insights = generate_team_insights(
                        team_stats[team], 
                        opponent_stats, 
                        settings["analysis_detail"]
                    )
                    
                    # Отображаем выводы
                    display_team_insights(insights, settings["analysis_detail"])
        
        except Exception as e:
            st.error(f"Произошла ошибка при анализе данных: {str(e)}")
            st.exception(e)

# Запуск приложения
if __name__ == "__main__":
    main()