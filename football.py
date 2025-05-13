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

# НОВЫЕ ФУНКЦИИ ДЛЯ РАСШИРЕННОГО АНАЛИЗА

# Функция для создания графика по категориям событий
def create_events_category_chart(team_stats, colors, height=500):
    """
    Создает график распределения событий по категориям для команд.
    """
    teams = list(team_stats.keys())
    
    # Создаем данные для графика
    data = []
    for team in teams:
        event_categories = team_stats[team].get('event_categories', {})
        for category, count in event_categories.items():
            data.append({
                'Команда': team,
                'Категория': category,
                'Количество': count
            })
    
    # Сортируем данные
    df = pd.DataFrame(data)
    if df.empty:
        fig = go.Figure()
        fig.update_layout(
            title="Нет данных о категориях событий",
            height=height
        )
        return fig
    
    # Создаем график
    fig = px.bar(
        df,
        x='Категория',
        y='Количество',
        color='Команда',
        barmode='group',
        color_discrete_map={teams[0]: colors['team1'], teams[1]: colors['team2']} if len(teams) > 1 else None,
        height=height
    )
    
    fig.update_layout(
        title='Распределение событий по категориям',
        xaxis_title=None,
        yaxis_title='Количество',
        legend_title='Команда'
    )
    
    return fig

# Функция для создания графика типов событий для выбранной категории
def create_event_types_chart(team_stats, team, event_category, color, height=400):
    """
    Создает график типов событий для выбранной категории.
    """
    event_types = team_stats[team].get('event_types', {}).get(event_category, {})
    
    if not event_types:
        fig = go.Figure()
        fig.update_layout(
            title=f"Нет данных о типах событий для категории '{event_category}' команды {team}",
            height=height
        )
        return fig
    
    # Создаем данные для графика
    data = []
    for event_type, count in event_types.items():
        data.append({
            'Тип': event_type,
            'Количество': count
        })
    
    # Сортируем по количеству
    data = sorted(data, key=lambda x: x['Количество'], reverse=True)
    
    # Создаем DataFrame
    df = pd.DataFrame(data)
    
    # Создаем график
    fig = px.bar(
        df,
        y='Тип',
        x='Количество',
        color_discrete_sequence=[color],
        height=height,
        orientation='h'
    )
    
    fig.update_layout(
        title=f"Типы событий для категории '{event_category}' - {team}",
        xaxis_title='Количество',
        yaxis_title=None
    )
    
    return fig

# Функция для создания графика использования ног
def create_foot_usage_chart(team_stats, colors, height=400):
    """
    Создает график распределения использования ног по командам.
    """
    teams = list(team_stats.keys())
    
    # Создаем данные для графика
    data = []
    for team in teams:
        foot_usage = team_stats[team].get('foot_used', {})
        for foot, count in foot_usage.items():
            # Преобразуем английские названия в русские для отображения
            foot_display = {
                'Right': 'Правая',
                'Left': 'Левая',
                'Head': 'Голова',
                'Other': 'Другое'
            }.get(foot, foot)
            
            data.append({
                'Команда': team,
                'Часть тела': foot_display,
                'Количество': count
            })
    
    # Создаем DataFrame
    df = pd.DataFrame(data)
    
    if df.empty:
        fig = go.Figure()
        fig.update_layout(
            title="Нет данных об использовании ног",
            height=height
        )
        return fig
    
    # Создаем график
    fig = px.bar(
        df,
        x='Часть тела',
        y='Количество',
        color='Команда',
        barmode='group',
        color_discrete_map={teams[0]: colors['team1'], teams[1]: colors['team2']} if len(teams) > 1 else None,
        height=height
    )
    
    fig.update_layout(
        title='Использование частей тела при игре',
        xaxis_title=None,
        yaxis_title='Количество',
        legend_title='Команда'
    )
    
    return fig

# Функция для создания графика использования ног по типам событий
def create_foot_by_event_chart(team_stats, team, color, height=400):
    """
    Создает график распределения использования ног по типам событий.
    """
    foot_by_event = team_stats[team].get('foot_by_event', {})
    
    if not foot_by_event:
        fig = go.Figure()
        fig.update_layout(
            title=f"Нет данных об использовании ног по типам событий для {team}",
            height=height
        )
        return fig
    
    # Создаем данные для графика
    data = []
    for event, foot_data in foot_by_event.items():
        for foot, count in foot_data.items():
            # Преобразуем английские названия в русские для отображения
            foot_display = {
                'Right': 'Правая',
                'Left': 'Левая',
                'Head': 'Голова',
                'Other': 'Другое'
            }.get(foot, foot)
            
            data.append({
                'Событие': event,
                'Часть тела': foot_display,
                'Количество': count
            })
    
    # Создаем DataFrame
    df = pd.DataFrame(data)
    
    # Создаем график
    fig = px.bar(
        df,
        x='Событие',
        y='Количество',
        color='Часть тела',
        barmode='stack',
        height=height
    )
    
    fig.update_layout(
        title=f"Использование частей тела по типам событий - {team}",
        xaxis_title=None,
        yaxis_title='Количество',
        legend_title='Часть тела'
    )
    
    return fig

# Функция для создания графика действий вратаря
def create_goalkeeper_actions_chart(team_stats, team, color, height=400):
    """
    Создает график действий вратаря.
    """
    gk_actions = team_stats[team].get('gk_actions', {})
    
    if not gk_actions:
        fig = go.Figure()
        fig.update_layout(
            title=f"Нет данных о действиях вратаря для {team}",
            height=height
        )
        return fig
    
    # Создаем данные для графика
    data = []
    for action, count in gk_actions.items():
        data.append({
            'Действие': action,
            'Количество': count
        })
    
    # Сортируем по количеству
    data = sorted(data, key=lambda x: x['Количество'], reverse=True)
    
    # Создаем DataFrame
    df = pd.DataFrame(data)
    
    # Создаем график
    fig = px.bar(
        df,
        y='Действие',
        x='Количество',
        color_discrete_sequence=[color],
        height=height,
        orientation='h'
    )
    
    fig.update_layout(
        title=f"Действия вратаря - {team}",
        xaxis_title='Количество',
        yaxis_title=None
    )
    
    return fig

# Функция для создания графика типов сейвов
def create_save_types_chart(team_stats, team, color, height=400):
    """
    Создает диаграмму типов сейвов вратаря.
    """
    save_types = team_stats[team].get('save_types', {})
    
    if not save_types:
        fig = go.Figure()
        fig.update_layout(
            title=f"Нет данных о типах сейвов для {team}",
            height=height
        )
        return fig
    
    # Преобразуем словарь в списки для построения графика
    labels = list(save_types.keys())
    values = list(save_types.values())
    
    # Создаем круговую диаграмму
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=.3,
        marker_colors=[color, color+'90', color+'70', color+'50', color+'30']
    )])
    
    fig.update_layout(
        title=f"Типы сейвов вратаря - {team}",
        height=height
    )
    
    return fig

# Функция для создания графика результатов под давлением
def create_pressure_results_chart(team_stats, team, color, height=500):
    """
    Создает график результатов действий под давлением.
    """
    pressure_results = team_stats[team].get('pressure_results', {})
    
    if not pressure_results:
        fig = go.Figure()
        fig.update_layout(
            title=f"Нет данных о результатах под давлением для {team}",
            height=height
        )
        return fig
    
    # Создаем данные для графика
    data = []
    for pressure, results in pressure_results.items():
        for result, count in results.items():
            # Преобразуем названия для отображения
            pressure_display = 'Под давлением' if pressure == 'Yes' else 'Без давления'
            
            data.append({
                'Давление': pressure_display,
                'Результат': result,
                'Количество': count
            })
    
    # Создаем DataFrame
    df = pd.DataFrame(data)
    
    if df.empty:
        return go.Figure()
    
    # Создаем график
    fig = px.bar(
        df,
        x='Давление',
        y='Количество',
        color='Результат',
        barmode='stack',
        color_discrete_sequence=px.colors.qualitative.Set1,
        height=height
    )
    
    fig.update_layout(
        title=f"Результаты действий под давлением - {team}",
        xaxis_title=None,
        yaxis_title='Количество',
        legend_title='Результат'
    )
    
    return fig

# Функция для создания сетевой диаграммы пасов
def create_pass_network_chart(team_stats, team, color, height=600, min_passes=2):
    """
    Создает график сети пасов между игроками одной команды.
    """
    pass_combinations = team_stats[team].get('pass_combinations', {})
    
    if not pass_combinations:
        fig = go.Figure()
        fig.update_layout(
            title=f"Нет данных о комбинациях пасов для {team}",
            height=height
        )
        return fig
    
    # Преобразуем данные о пасах в формат для построения сети
    edges = []
    for player1, targets in pass_combinations.items():
        for player2, count in targets.items():
            if count >= min_passes:  # Фильтруем по минимальному количеству пасов
                edges.append((player1, player2, count))
    
    if not edges:
        fig = go.Figure()
        fig.update_layout(
            title=f"Недостаточно данных для сети пасов команды {team}",
            height=height
        )
        return fig
    
    # Создаем список всех игроков
    all_players = set()
    for edge in edges:
        all_players.add(edge[0])
        all_players.add(edge[1])
    all_players = list(all_players)
    
    # Создаем словарь позиций игроков (распределяем по кругу)
    player_positions = {}
    n_players = len(all_players)
    for i, player in enumerate(all_players):
        angle = 2 * math.pi * i / n_players
        r = 0.8  # радиус круга
        player_positions[player] = (r * math.cos(angle) + 1.0, r * math.sin(angle) + 1.0)
    
    # Создаем граф
    fig = go.Figure()
    
    # Добавляем связи (пасы)
    for player1, player2, count in edges:
        start_pos = player_positions[player1]
        end_pos = player_positions[player2]
        
        # Ширина линии пропорциональна количеству пасов
        width = min(10, 1 + count / 2)
        
        fig.add_trace(go.Scatter(
            x=[start_pos[0], end_pos[0]],
            y=[start_pos[1], end_pos[1]],
            mode='lines',
            line=dict(
                width=width,
                color=color
            ),
            opacity=0.7,
            showlegend=False,
            hoverinfo='text',
            text=f"{player1} → {player2}: {count} пасов"
        ))
    
    # Расчет статистики пасов для определения размера узлов
    player_pass_counts = defaultdict(int)
    for player1, player2, count in edges:
        player_pass_counts[player1] += count  # Отданные пасы
        player_pass_counts[player2] += count  # Полученные пасы
    
    # Добавляем узлы (игроков)
    for player in all_players:
        pos = player_positions[player]
        
        # Размер узла зависит от общего числа связанных пасов
        size = max(15, player_pass_counts[player] / 2)
        
        fig.add_trace(go.Scatter(
            x=[pos[0]],
            y=[pos[1]],
            mode='markers+text',
            marker=dict(
                size=size,
                color=color,
                line=dict(width=2, color='white')
            ),
            text=player,
            textposition="top center",
            hoverinfo='text',
            hovertext=f"{player}: {player_pass_counts[player]} связанных пасов",
            showlegend=False
        ))
    
    # Настраиваем макет
    fig.update_layout(
        title=f"Сеть пасов команды {team}",
        height=height,
        showlegend=False,
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        plot_bgcolor='rgba(240, 240, 240, 0.8)'
    )
    
    return fig

# Функция для создания графика игроков по использованию разных ног
def create_player_foot_usage_chart(team_stats, team, color, height=500, top_n=10):
    """
    Создает график распределения использования ног разными игроками.
    """
    player_foot_usage = team_stats[team].get('player_foot_usage', {})
    
    if not player_foot_usage:
        fig = go.Figure()
        fig.update_layout(
            title=f"Нет данных об использовании ног игроками команды {team}",
            height=height
        )
        return fig
    
    # Создаем данные для графика
    data = []
    for player, foot_data in player_foot_usage.items():
        total_actions = sum(foot_data.values())
        if total_actions < 3:  # Пропускаем игроков с малым количеством действий
            continue
            
        # Рассчитываем соотношение правой/левой ноги
        right_pct = foot_data.get('Right', 0) / total_actions * 100 if total_actions > 0 else 0
        left_pct = foot_data.get('Left', 0) / total_actions * 100 if total_actions > 0 else 0
        
        # Вычисляем "двуногость" - насколько игрок одинаково пользуется обеими ногами
        if right_pct > 0 and left_pct > 0:
            two_footedness = min(right_pct, left_pct) / max(right_pct, left_pct) * 100
        else:
            two_footedness = 0
        
        data.append({
            'Игрок': player,
            'Всего действий': total_actions,
            'Правая (%)': right_pct,
            'Левая (%)': left_pct,
            'Двуногость (%)': two_footedness
        })
    
    # Сортируем по общему количеству действий и берем топ N
    data = sorted(data, key=lambda x: x['Всего действий'], reverse=True)[:top_n]
    
    if not data:
        fig = go.Figure()
        fig.update_layout(
            title=f"Недостаточно данных об использовании ног игроками команды {team}",
            height=height
        )
        return fig
    
    # Создаем DataFrame
    df = pd.DataFrame(data)
    
    # Создаем график
    fig = go.Figure()
    
    # Добавляем столбцы для правой ноги
    fig.add_trace(go.Bar(
        y=df['Игрок'],
        x=df['Правая (%)'],
        name='Правая нога (%)',
        orientation='h',
        marker=dict(color='rgba(58, 71, 80, 0.6)')
    ))
    
    # Добавляем столбцы для левой ноги
    fig.add_trace(go.Bar(
        y=df['Игрок'],
        x=df['Левая (%)'],
        name='Левая нога (%)',
        orientation='h',
        marker=dict(color='rgba(246, 78, 139, 0.6)')
    ))
    
    # Добавляем метки с процентом "двуногости"
    for i, row in df.iterrows():
        fig.add_annotation(
            x=row['Правая (%)'] + row['Левая (%)'] + 5,
            y=row['Игрок'],
            text=f"Двуногость: {row['Двуногость (%)']:.1f}%",
            showarrow=False,
            font=dict(color="black", size=10),
            align="left"
        )
    
    # Настраиваем макет
    fig.update_layout(
        title=f"Использование правой и левой ноги игроками - {team}",
        barmode='stack',
        height=height,
        xaxis=dict(title='Процент использования (%)'),
        yaxis=dict(title=None)
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
            
        # Анализ использования ног (новый)
        foot_used = team_stats.get('foot_used', {})
        if foot_used:
            total_actions = sum(foot_used.values())
            if total_actions > 0:
                right_pct = foot_used.get('Right', 0) / total_actions * 100
                left_pct = foot_used.get('Left', 0) / total_actions * 100
                
                if right_pct > 80:
                    insights['tactics'].append(
                        f"Команда очень сильно полагается на правую ногу ({right_pct:.1f}%). "
                        f"Развитие игры левой ногой может добавить непредсказуемости."
                    )
                    insights['improvement_areas'].append("Развитие игры левой ногой")
                elif left_pct > 80:
                    insights['tactics'].append(
                        f"Команда очень сильно полагается на левую ногу ({left_pct:.1f}%). "
                        f"Развитие игры правой ногой может добавить непредсказуемости."
                    )
                    insights['improvement_areas'].append("Развитие игры правой ногой")
                elif min(right_pct, left_pct) > 30:
                    insights['strengths'].append(
                        f"Команда хорошо использует обе ноги в игре (правая: {right_pct:.1f}%, левая: {left_pct:.1f}%), "
                        f"что делает её атаки более разнообразными."
                    )
    
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
            
    # Анализ поведения под давлением (новый)
    pressure_results = team_stats.get('pressure_results', {})
    if pressure_results:
        # Рассчитаем успешность действий под давлением и без него
        under_pressure = pressure_results.get('Yes', {})
        no_pressure = pressure_results.get('No', {})
        
        successful_under_pressure = sum(count for result, count in under_pressure.items() 
                                    if result in ['Successful', 'On Target', 'Goal'])
        total_under_pressure = sum(under_pressure.values())
        
        successful_no_pressure = sum(count for result, count in no_pressure.items() 
                                  if result in ['Successful', 'On Target', 'Goal'])
        total_no_pressure = sum(no_pressure.values())
        
        # Рассчитаем процент успешности
        if total_under_pressure > 0 and total_no_pressure > 0:
            success_rate_under_pressure = successful_under_pressure / total_under_pressure * 100
            success_rate_no_pressure = successful_no_pressure / total_no_pressure * 100
            
            pressure_diff = success_rate_no_pressure - success_rate_under_pressure
            
            if pressure_diff > 30:
                insights['weaknesses'].append(
                    f"Значительное снижение успешности действий под давлением "
                    f"({success_rate_under_pressure:.1f}% против {success_rate_no_pressure:.1f}% без давления)."
                )
                insights['improvement_areas'].append("Улучшение игры под прессингом")
            elif pressure_diff < 10:
                insights['strengths'].append(
                    f"Команда хорошо действует под давлением "
                    f"({success_rate_under_pressure:.1f}% против {success_rate_no_pressure:.1f}% без давления)."
                )
    
    # Анализ использования вратаря (новый)
    gk_actions = team_stats.get('gk_actions', {})
    if gk_actions:
        total_gk_actions = sum(gk_actions.values())
        if total_gk_actions > 0:
            # Анализ стиля вратаря
            long_passes = gk_actions.get('Long Pass', 0)
            short_passes = gk_actions.get('Short Pass', 0)
            
            if long_passes > short_passes * 2:
                insights['tactics'].append(
                    f"Вратарь предпочитает длинные передачи ({long_passes} длинных против {short_passes} коротких). "
                    f"Команда стремится быстро переходить к атаке, минуя центр поля."
                )
            elif short_passes > long_passes * 2:
                insights['tactics'].append(
                    f"Вратарь предпочитает короткие передачи ({short_passes} коротких против {long_passes} длинных). "
                    f"Команда стремится контролировать мяч и строить атаки через розыгрыш от вратаря."
                )
            
            # Анализ сейвов
            saves = gk_actions.get('Save', 0)
            if saves > 5:
                insights['key_players'].append(
                    f"Вратарь совершил {saves} сейвов, что указывает на его важную роль в защите."
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
        
        Расширенный анализ также использует:
        - Pressure: Наличие прессинга
        - Foot_Used: Используемая нога
        - GK_Action: Действие вратаря
        - Save_Type: Тип сейва
        - Player_Name_2: Имя игрока, получающего пас
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
            
            # Раздел с расширенным анализом
            if settings["show_event_categories"]:
                st.header("Анализ категорий событий")
                st.plotly_chart(create_events_category_chart(team_stats, color_scheme, settings["chart_height"]), use_container_width=True)
                
                # Выбор команды и категории для анализа
                event_team = st.selectbox("Выберите команду для анализа типов событий", teams)
                event_categories = list(team_stats[event_team].get('event_categories', {}).keys())
                
                if event_categories:
                    event_category = st.selectbox("Выберите категорию события", event_categories)
                    
                    st.plotly_chart(
                        create_event_types_chart(
                            team_stats, event_team, event_category,
                            color_scheme['team1'] if event_team == teams[0] else color_scheme['team2'],
                            settings["chart_height"]
                        ),
                        use_container_width=True
                    )
            
            if settings["show_foot_analysis"]:
                st.header("Анализ использования ног")
                st.plotly_chart(create_foot_usage_chart(team_stats, color_scheme, settings["chart_height"]), use_container_width=True)
                
                if len(teams) > 0:
                    foot_team_tabs = st.tabs(teams)
                    for i, team in enumerate(teams):
                        with foot_team_tabs[i]:
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                st.plotly_chart(
                                    create_foot_by_event_chart(
                                        team_stats, team,
                                        color_scheme['team1'] if i == 0 else color_scheme['team2'],
                                        settings["chart_height"]
                                    ),
                                    use_container_width=True
                                )
                            
                            with col2:
                                st.plotly_chart(
                                    create_player_foot_usage_chart(
                                        team_stats, team,
                                        color_scheme['team1'] if i == 0 else color_scheme['team2'],
                                        settings["chart_height"]
                                    ),
                                    use_container_width=True
                                )
            
            if settings["show_pressure_analysis"]:
                st.header("Анализ действий под давлением")
                
                if len(teams) > 0:
                    pressure_team_tabs = st.tabs(teams)
                    for i, team in enumerate(teams):
                        with pressure_team_tabs[i]:
                            st.plotly_chart(
                                create_pressure_results_chart(
                                    team_stats, team,
                                    color_scheme['team1'] if i == 0 else color_scheme['team2'],
                                    settings["chart_height"]
                                ),
                                use_container_width=True
                            )
            
            if settings["show_goalkeeper_analysis"]:
                st.header("Анализ действий вратарей")
                
                if len(teams) > 0:
                    gk_team_tabs = st.tabs(teams)
                    for i, team in enumerate(teams):
                        with gk_team_tabs[i]:
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                st.plotly_chart(
                                    create_goalkeeper_actions_chart(
                                        team_stats, team,
                                        color_scheme['team1'] if i == 0 else color_scheme['team2'],
                                        settings["chart_height"]
                                    ),
                                    use_container_width=True
                                )
                            
                            with col2:
                                st.plotly_chart(
                                    create_save_types_chart(
                                        team_stats, team,
                                        color_scheme['team1'] if i == 0 else color_scheme['team2'],
                                        settings["chart_height"]
                                    ),
                                    use_container_width=True
                                )
            
            if settings["show_pass_network"]:
                st.header("Сеть передач между игроками")
                
                if len(teams) > 0:
                    network_team_tabs = st.tabs(teams)
                    for i, team in enumerate(teams):
                        with network_team_tabs[i]:
                            min_passes = st.slider(
                                "Минимальное количество пасов для отображения связи", 
                                1, 10, 2, 
                                key=f"min_passes_{team}"
                            )
                            
                            st.plotly_chart(
                                create_pass_network_chart(
                                    team_stats, team,
                                    color_scheme['team1'] if i == 0 else color_scheme['team2'],
                                    settings["chart_height"] + 100,
                                    min_passes
                                ),
                                use_container_width=True
                            )
            
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
