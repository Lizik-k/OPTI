import pandas as pd
import csv
import plotly.express as px
import streamlit as st
from datetime import date, datetime


# ====================== НАСТРОЙКА СТРАНИЦ ======================
if 'page' not in st.session_state:
    st.session_state.page = 'page1'  # По умолчанию первая страница

# Стили для кнопок навигации
st.markdown("""
<style>
    .nav-button {
        margin: 5px;
        padding: 10px;
        border-radius: 5px;
        width: 100%;
    }
    .nav-button.active {
        background-color: #4CAF50;
        color: white;
    }
</style>
""", unsafe_allow_html=True)



# Чтение всех необходимых файлов из первой программы

#Партнеры АЗС, номера, регионы
spisok_azs = pd.read_excel('список АЗС.xlsx')
spisok_azs['Регион'] = spisok_azs['Адрес АЗС'].str.split(',').str[0]
# partners = pd.read_csv(r'Список АЗС.csv')
# print(partners
#       )


partner_azs = spisok_azs['Партнер']
name_partner = partner_azs.drop_duplicates()
number_azs =  pd.to_numeric(spisok_azs['АЗС '])
region = spisok_azs['Регион'].drop_duplicates()
# adres = list(spisok_azs['Адрес АЗС'])
# reg = []
# for i in adres:
#     b = i.split(',')[0]
#     reg.append(b)
# reg = pd.DataFrame(reg)
# region =  reg.drop_duplicates()


#Выгрузка отзывов
data = pd.read_excel('ДатаФрейм.xlsx')
max_date = max(list(data['Дата']))
min_date = min(list(data['Дата']))
start_date = min_date.split('-')
start_day = int(start_date[2])
start_month = int(start_date[1])
start_year = int(start_date[0])
end_date = max_date.split('-')
end_day = int(end_date[2])
end_month = int(end_date[1])
end_year = int(end_date[0])
data['Дата'] = pd.to_datetime(data['Дата']).dt.date
data['АЗС'] = pd.to_numeric(data['АЗС'])
data['Рейтинг'] = pd.to_numeric(data['Рейтинг'])


# Теги
tags_category = pd.read_excel('Комментарии_теги.xlsx')
tag_list =  list(pd.DataFrame(tags_category)['Тег'].drop_duplicates())

# Теги
tonal = pd.read_excel('Комментарии_тональность.xlsx')


# ====================== НАВИГАЦИОННОЕ МЕНЮ ======================
cols = st.columns(3)
with cols[0]:
    if st.button('📊 Категории, теги и тональности', key='btn_page1'):
        st.session_state.page = 'page1'

with cols[1]:
    if st.button('🍩 Топы партнеров', key='btn_page2'):
        st.session_state.page = 'page2'
with cols[2]:
    if st.button('Проверка ответов', key='btn_page3'):
        st.session_state.page = 'page3'

st.markdown("---")  # Горизонтальная разделительная линия


# ====================== СТРАНИЦА 1 ======================
if st.session_state.page == 'page1':

    # ДАШБОРД

    st.write("""# Анализ отзывов с георесурсов""")
    #st.write("""## Версия 0.0.1""")

    st.sidebar.header('Параметры')

    # st.sidebar.date_input(
    #     "Выберите период:",
    #     value=[None, None],  # начальное значение
    #     min_value=start_date,  # минимальная доступная дата
    #     max_value= end_date, # максимальная дата
    #     format="DD.MM.YYYY",  # формат отображения (опционально)
    #     key="date_range",
    #     range = True
    #
    # )

    #
    st.sidebar.write("Выберите период:")
    col1, col2 = st.sidebar.columns(2)
    with col1:
        start = st.date_input("Начало",
                              value = date(start_year, start_month, start_day),
                              min_value=date(start_year, start_month, start_day),
                              max_value=date(end_year, end_month, end_day))
    with col2:
        end = st.date_input("Конец",
                            value=date(end_year, end_month, end_day),
                            min_value=date(start_year, start_month, start_day),
                            max_value=date(end_year, end_month, end_day))


    region = st.sidebar.multiselect('Регион', (region), region)
    #partner = st.sidebar.multiselect('Партнер', (name_partner), name_partner)
    if region:
        available_partners = spisok_azs[spisok_azs['Регион'].isin(region)]['Партнер'].unique().tolist()
    else:
        available_partners = spisok_azs['Партнер'].unique().tolist()
    # # Применяем фильтры к данным
    partner = st.sidebar.multiselect(
        'Партнер',
        options=available_partners,
        default=available_partners
    )
    if region or partner:
        filter_condition = True
        if region:
            filter_condition &= (spisok_azs['Регион'].isin(region))
        if partner:
            filter_condition &= (spisok_azs['Партнер'].isin(partner))

        available_azs = spisok_azs[filter_condition]['АЗС '].unique().tolist()
    else:
        available_azs = spisok_azs['АЗС '].unique().tolist()

    azs = st.sidebar.multiselect(
        'Номер АЗС',
        options=available_azs,
        default=available_azs
    )




    filtered_data = data[
        (data['Дата'] >= start) &
        (data['Дата'] <= end) &
        (data['Регион'].isin(region)) &
        (data['АЗС'].isin(azs)) &
        (data['Партнер'].isin(partner))
    ]

    # Рассчитываем средний рейтинг по отфильтрованным данным
    avg_rating = filtered_data['Рейтинг'].mean() if not filtered_data.empty else 0
    count_records = len(filtered_data)

    # if avg_rating < 3.5:
    #     color = "red"
    # elif avg_rating < 4.6:
    #     color = "orange"
    # else:
    #     color = "green"


    # Создаем карточку с метрикой
    rank_avg, len_otz = st.columns(2)
    # st.markdown(
    #     f"""
    #        <div style="
    #            background-color: {color}20;
    #            padding: 10px;
    #            border-radius: 10px;
    #            border-left: 5px solid {color};
    #        ">
    #            <div style="font-size: 0.8em; color: #666;">Средний рейтинг</div>
    #            <div style="font-size: 1.5em; font-weight: bold;">{}</div>
    #        </div>
    #        """,
    #     unsafe_allow_html=True
    # )
    with rank_avg:
        st.metric(
            label="Средний рейтинг",
            value=f"{avg_rating:.1f}",
            help="Рассчитан по выбранным фильтрам"
        )


    with len_otz:
        st.metric(
            label="Количество оценок",
            value=count_records
        )





    # ДИНАМИКА РЕЙТИНГА - линейная диаграмма

    cumulative_daily = (filtered_data.sort_values('Дата')
                        .groupby('Дата')['Рейтинг']
                        .mean()
                        .expanding()
                        .mean()
                        .reset_index())

    # st.line_chart(
    #         cumulative_daily.set_index('Дата'),
    #         y='Рейтинг',
    #         height=400
    #     )

    fig = px.line(
        cumulative_daily,
        x='Дата',
        y='Рейтинг',
        title='График рейтинга по дням',
        labels={'Рейтинг': 'Рейтинг', 'Дата': 'Дата'},
        height=400,
    )

    # Настройка внешнего вида (опционально)
    fig.update_layout(
        hovermode='x unified',  # показывает данные при наведении
        plot_bgcolor='white',  # белый фон
        xaxis=dict(showgrid=True, gridcolor='lightgray'),  # сетка по X
        yaxis=dict(showgrid=True, gridcolor='lightgray'),  # сетка по Y
    )

    # Вывод графика в Streamlit
    st.plotly_chart(fig, use_container_width=True)



    # КОЛИЧЕСТВО ТЕГОВ - круговая диаграмма

    data_with_tags = pd.merge(data, tags_category, on='id Отзыва')

    filtered_data_tag = data_with_tags[
        (data_with_tags['Дата'] >= start) &
        (data_with_tags['Дата'] <= end) &
        (data_with_tags['Регион'].isin(region)) &
        (data_with_tags['АЗС'].isin(azs)) &
        (data_with_tags['Партнер'].isin(partner))
    ]

    # Группируем по тегам
    tag_counts = filtered_data_tag['Тег'].value_counts().reset_index()
    tag_counts.columns = ['Тег', 'Количество']

    # Размещаем в один ряд
    tags_colc, ton_colc = st.columns([6, 1])  # Создаем две колонки

    if not tag_counts.empty:
        fig_tag = px.pie(
            tag_counts,
            values='Количество',
            names='Тег',
            hole=0.5,
            title=f'Распределение тегов',
            color_discrete_sequence=px.colors.qualitative.Prism
        )

        # Настройка отображен
        fig_tag.update_traces(
            textposition='outside',
            textinfo='percent+label',
            pull=[0.05] * len(tag_counts),
        insidetextfont = dict(size=12)  # Увеличиваем шрифт для читаемости
        )

        fig_tag.update_layout(
            showlegend=False,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-1,
                xanchor="center",
                x=0.5
            ),
            margin=dict(t=50, b=0, l=0, r=0),
            annotations=[
                dict(
                    text=f"Всего: {tag_counts['Количество'].sum()}",
                    x=0.5, y=0.5,
                    font_size=16,
                    showarrow=False
                )
            ]

        )

        # Добавляем callback для обработки кликов
        fig_tag.update_layout(
            clickmode='event+select'
        )


        # Отображаем диаграмму
        #st.plotly_chart(fig_tag, use_container_width=True)
        with tags_colc:
            selected = st.plotly_chart(fig_tag, use_container_width=True)  # use_container_width растягивает на всю ширину колонки
            # # Обработка клика
            # if selected.select_data:
            #     clicked_tag = selected.select_data[0]['points'][0]['label']
            #     comments = tag_counts[tag_counts['Тег'] == clicked_tag]['Комментарии'].iloc[0]
            #
            #     st.subheader(f"Комментарии с тегом '{clicked_tag}':")
            #     for comment in comments:
            #         st.write(f"- {comment}")

        # Дополнительная таблица с данными
        st.write("### Статистика по тегам")
        tag_counts['Доля'] = (tag_counts['Количество'] / tag_counts['Количество'].sum() * 100).round(1)
        st.dataframe(
            tag_counts.sort_values('Количество', ascending=False),
            column_config={
                "Тег": "Категория",
                "Количество": st.column_config.NumberColumn(format="%d"),
                "Доля": st.column_config.NumberColumn(format="%.1f%%")
            },
            hide_index=True
        )

    else:
        st.warning("Нет данных по выбранным фильтрам")




    # Объединяем таблицы с тональностью
    data_with_ton = pd.merge(data, tonal, on='id Отзыва')

    filtered_data_tag_ton = data_with_ton[
        (data_with_ton['Дата'] >= start) &
        (data_with_ton['Дата'] <= end) &
        (data_with_ton['Регион'].isin(region)) &
        (data_with_ton['АЗС'].isin(azs)) &
        (data_with_ton['Партнер'].isin(partner))
    ]

    # Группируем по тональности
    sentiment_counts = filtered_data_tag_ton['Тональность'].value_counts().reset_index()
    sentiment_counts.columns = ['Тональность', 'Количество']

    # Строим круговую диаграмму
    if not sentiment_counts.empty:
        fig_ton = px.pie(
            sentiment_counts,
            values='Количество',
            names='Тональность',
            title="""Тональность""",


            color='Тональность',
            color_discrete_map={
                'Позитивная': '#73af48',
                'Негативная': '#ff5454',
                'Нейтральная': '#ffe354',
                'Смешанная': '#a154ff'
            },
            hole=0
        )

        # Настройка отображения
        fig_ton.update_traces(
            textposition='inside',
            textinfo='percent',
            insidetextfont=dict(size=12, color='white'),
            #marker=dict(line=dict(color='#000000', width=1))
            marker=dict(
                colors=['#73af48', '#ff5454', '#ffe354', '#a154ff']  # Дублируем цвета здесь!
            )
        )

        fig_ton.update_layout(
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.2,
                xanchor="center",
                x=0.5
            ),
            margin=dict(t=50, b=0, l=0, r=0)
        )

        # Отображаем диаграмму
        #st.plotly_chart(fig_ton, use_container_width=True)

        with ton_colc:
            st.plotly_chart(fig_ton, use_container_width=True)

        # # Таблица с детализацией
        # st.write("### Детализация по тональностям")
        # sentiment_counts['Доля'] = (sentiment_counts['Количество'] / sentiment_counts['Количество'].sum() * 100).round(1)
        # st.dataframe(
        #     sentiment_counts.sort_values('Количество', ascending=False),
        #     column_config={
        #         "Тональность": st.column_config.TextColumn("Тип тональности"),
        #         "Количество": st.column_config.NumberColumn(format="%d"),
        #         "Доля": st.column_config.NumberColumn(format="%.1f%%")
        #     },
        #     hide_index=True
        # )
    else:
        st.warning("Нет данных по выбранным фильтрам")



    # ТЕГИ ВНУТРИ КАТЕГОРИИИ - СТОЛБЧАТАЯ ДИАГРАММА



    # Создаем графики для каждой категории
    if not filtered_data_tag.empty:
        categories = ['ПЕРСОНАЛ', 'ПОМЕЩЕНИЕ', 'ТОПЛИВО', 'ОПЛАТА', 'ДОПОЛНИТЕЛЬНО']
        figs = []

        for category in categories:
            category_data = filtered_data_tag[filtered_data_tag['Категория'] == category]
            if not category_data.empty:
                grouped = category_data.groupby('Тег').size().reset_index(name='Количество')
                grouped = grouped.sort_values('Количество', ascending=False)
                fig = px.bar(
                    grouped,
                    x='Тег',
                    y='Количество',
                    title=f'{category}',
                    color='Тег',
                    color_discrete_sequence=px.colors.qualitative.Pastel,
                    height=400,
                    category_orders={"Тег": grouped['Тег'].tolist()}
                )
                fig.update_layout(showlegend=False,
                                  xaxis=dict(
                                      tickangle=-45,
                                      tickfont=dict(size=10),
                                      tickvals=grouped['Тег'],  # Явно задаем значения
                                      ticktext=[t.replace(' ', '\n') for t in grouped['Тег']]  # Перенос слов
                                  ),
                                  margin=dict(b=150)  # Увеличиваем нижний отступ для подписей
                                   #margin=dict(t=50, b=100)
                                  )

                figs.append(fig)
            else:
                figs.append(None)

        # Первый ряд - 3 графика
        cols = st.columns(3)
        for i in range(3):
            with cols[i]:
                if figs[i]:
                    st.plotly_chart(figs[i], use_container_width=True)
                else:
                    st.warning(f"Нет данных для категории {categories[i]}")

        # Второй ряд - 2 графика
        cols = st.columns(2)
        for i in range(3, 5):
            with cols[i - 3]:
                if figs[i]:
                    st.plotly_chart(figs[i], use_container_width=True)
                else:
                    st.warning(f"Нет данных для категории {categories[i]}")

    else:
        st.warning("Нет данных по выбранным фильтрам")


    # Размещаем в один ряд
    cat_colc, pust, ton_bar  = st.columns([2, 1, 5])  # Создаем две колонки


    # Круговая диаграмма - какие категории чаще затрагивают в комментариях

    category_counts = filtered_data_tag['Категория'].value_counts().reset_index()
    category_counts.columns = ['Категория', 'Количество']

    # Создаем круговую диаграмму
    fig = px.pie(
        category_counts,
        values='Количество',
        names='Категория',
        title='Распределение отзывов по категориям',
        hole=0,  # Кольцевая диаграмма (установите 0 для обычной круговой)
        color_discrete_sequence=px.colors.qualitative.Prism # Цветовая схема
    )

    # Настройка отображения
    fig.update_traces(
        textposition='inside',
        textinfo='percent+label',
        insidetextfont=dict(size=12, color='white'),
        pull=[0.02]*len(category_counts)  # Легкое отделение секторов
    )

    fig.update_layout(
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.2,
            xanchor="center",
            x=0.5
        ),
        margin=dict(t=50, b=0, l=0, r=0),
        annotations=[dict(
            text=f" ",
            x=0.5, y=0.5,
            font_size=16,
            showarrow=False
        )]
    )

    with cat_colc:
        # Отображаем график
        st.plotly_chart(fig, use_container_width=True)

    # Строим диаграмму
    if not filtered_data_tag_ton.empty:
        # Группируем данные по категориям и тональностям
        grouped_data = filtered_data_tag_ton.groupby(['Категория', 'Тональность']).size().reset_index(name='Количество')
        tonality_order = ['позитивная', 'негативная', 'нейтральная', 'смешанная']
        color_map = {
            'позитивная': '#73af48',
            'негативная': '#ff5454',
            'нейтральная': '#ffe354',
            'смешанная': '#a154ff'
        }

        # Создаем столбчатую диаграмму
        fig = px.bar(
            grouped_data,
            x='Категория',
            y='Количество',
            color='Тональность',
            barmode='group',
            title='Распределение тональностей по категориям',
            category_orders={'Тональность': tonality_order},
            color_discrete_map=color_map,

            height=500
        )
        # Критически важная часть - принудительное назначение цветов
        # for i, ton in enumerate(tonality_order):
        #     fig.update_traces(
        #         marker_color=color_map[ton],
        #         selector={'name': ton}  # Выбираем только следы с этим именем
        #     )

        # Настройка отображения
        fig.update_layout(
            xaxis_title='Категории',
            yaxis_title='Количество отзывов',
            legend_title='Тональность',
            xaxis={'tickangle': -45, 'categoryorder': 'total descending'},
            uniformtext_minsize=8,
            margin=dict(b=150)  # Увеличиваем отступ снизу для подписей
        )

        # Добавляем подписи значений
        fig.update_traces(
            texttemplate='%{y}',
            textposition='outside'
        )
        with ton_bar:
            # Отображаем график
            st.plotly_chart(fig, use_container_width=True)


    else:
        st.warning("Нет данных по выбранным фильтрам")


    # СТОЛБЧАТАЯ ДИАГРАММА С КОЛИЧЕСТВОМ КАЖДОЙ ОЦЕНКИ
    # Создаем DataFrame с рейтингами
    rating_counts = filtered_data['Рейтинг'].value_counts().reindex([5, 4, 3, 2, 1], fill_value=0).reset_index()
    rating_counts.columns = ['Рейтинг', 'Количество']

    # Создаем столбчатую диаграмму
    fig = px.bar(
        rating_counts,
        x='Рейтинг',
        y='Количество',
        title='Распределение оценок',
        text='Количество',
        color='Рейтинг',
        color_discrete_map={
            5: '#4CAF50',  # Зеленый
            4: '#8BC34A',  # Светло-зеленый
            3: '#FFC107',  # Желтый
            2: '#FF9800',  # Оранжевый
            1: '#F44336'  # Красный
        },
        category_orders={'Оценка': [5, 4, 3, 2, 1]}  # Фиксированный порядок
    )

    # Настраиваем внешний вид
    fig.update_traces(
        textposition='outside',
        marker_line_color='white',
        marker_line_width=1.5,
        opacity=0.9
    )

    fig.update_layout(
        xaxis_title='Оценка',
        yaxis_title='Количество оценок',
        showlegend=False,
        uniformtext_minsize=8,
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(t=40, b=0, l=0, r=0)
    )

    # Выводим диаграмму
    st.plotly_chart(fig, use_container_width=True)


    st.write('## Распределение по каталогам')

    filtered_data = data[
        (data['Дата'] >= start) &
        (data['Дата'] <= end) &
        (data['Регион'].isin(region)) &
        (data['АЗС'].isin(azs)) &
        (data['Партнер'].isin(partner))
        ]
    filtered_data['Каталог'] = filtered_data['Каталог'].replace(
        ['2ГИС', '2gis', '2 гис'],
        '2GIS'
    )
    # Группируем данные по каталогам
    catalog_stats = filtered_data['Каталог'].value_counts().reset_index()
    catalog_stats.columns = ['Каталог', 'Количество отзывов']

    # Сортируем по количеству (для лучшей визуализации)
    catalog_stats = catalog_stats.sort_values('Количество отзывов', ascending=True)

    # Создаем горизонтальную столбчатую диаграмму
    fig = px.bar(
        catalog_stats,
        y='Каталог',
        x='Количество отзывов',
        orientation='h',
        title='Количество отзывов по каталогам',
        text='Количество отзывов',
        color='Каталог',
        color_discrete_sequence=px.colors.qualitative.Pastel,
        height=500  # Фиксированная высота для лучшего отображения
    )

    # Настраиваем отображение
    fig.update_traces(
        textposition='outside',
        marker_line_color='white',
        marker_line_width=1.5,
        opacity=0.9
    )

    fig.update_layout(
        yaxis_title=None,
        xaxis_title='Количество отзывов',
        showlegend=False,
        uniformtext_minsize=8,
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(t=40, b=0, l=0, r=0)
    )

    # Выводим диаграмму
    st.plotly_chart(fig, use_container_width=True)


    st.write('### 2GIS')

    filtered_data_tag['Каталог'] = filtered_data_tag['Каталог'].replace(
        ['2ГИС', '2gis', '2 гис'],
        '2GIS'
    )

    df_2gis = filtered_data_tag[filtered_data_tag['Каталог'].isin(['2GIS', '2ГИС'])]
    df_2gis_all = filtered_data[filtered_data['Каталог'] == '2GIS']
    # Создаем два столбца

    if df_2gis.empty or df_2gis_all.empty:
        st.warning("Нет данных для отображения по 2GIS")
    else:

        col1, col2 = st.columns(2)

        with col1:
            # Кольцевая диаграмма распределения категорий
            category_counts = df_2gis['Категория'].value_counts().reset_index()
            category_counts.columns = ['Категория', 'Количество']

            fig_2g = px.pie(
                category_counts,
                values='Количество',
                names='Категория',
                hole=0.5,
                color_discrete_sequence=px.colors.qualitative.Prism
            )
            fig_2g.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig_2g, use_container_width=True, key='1')

        with col2:
            # Метрики для 2GIS
            avg_rating = df_2gis_all['Рейтинг'].mean()
            num_comments = len(df_2gis_all)
            st.metric(
                label="Средний рейтинг",
                value=f"{avg_rating:.1f}"
            )
            st.metric(
                label="Количество комментариев",
                value=f"{num_comments}"
            )

    st.write('### Яндекс Карты')
    df_ya = filtered_data_tag[filtered_data_tag['Каталог'] == 'Яндекс Карты']
    df_ya_all = filtered_data[filtered_data['Каталог'] == 'Яндекс Карты']

    # Создаем два столбца
    # Проверяем, есть ли данные для отображения
    if df_ya.empty or df_ya_all.empty:
        st.warning("Нет данных для отображения по Google Business Profile")
    else:

        col1, col2 = st.columns(2)

        with col1:
            # Кольцевая диаграмма распределения категорий
            category_counts = df_ya['Категория'].value_counts().reset_index()
            category_counts.columns = ['Категория', 'Количество']

            fig_ya = px.pie(
                category_counts,
                values='Количество',
                names='Категория',
                hole=0.5,
                color_discrete_sequence=px.colors.qualitative.Prism
            )
            fig_ya.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig_ya, use_container_width=True, key='2')

        with col2:
            # Метрики
            avg_rating = df_ya_all['Рейтинг'].mean()
            num_comments = len(df_ya_all)
            st.metric(
                label="Средний рейтинг",
                value=f"{avg_rating:.1f}"
            )
            st.metric(
                label="Количество комментариев",
                value=f"{num_comments}"
            )

    st.write('### Google Business Profile')
    df_go = filtered_data_tag[filtered_data_tag['Каталог'] == 'Google Business Profile']
    df_go_all = filtered_data[filtered_data['Каталог'] == 'Google Business Profile']

    # Проверяем, есть ли данные для отображения
    if df_go.empty or df_go_all.empty:
        st.warning("Нет данных для отображения по Google Business Profile")
    else:
        # Создаем два столбца

        col1, col2 = st.columns(2)

        with col1:
            # Кольцевая диаграмма распределения категорий
            category_counts = df_go['Категория'].value_counts().reset_index()
            category_counts.columns = ['Категория', 'Количество']

            fig_go = px.pie(
                category_counts,
                values='Количество',
                names='Категория',
                hole=0.5,
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            fig_go.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig_go, use_container_width=True, key='3')

        with col2:
            # Метрики для 2GIS
            avg_rating = df_go_all['Рейтинг'].mean()
            num_comments = len(df_go_all)
            st.metric(
                label="Средний рейтинг",
                value=f"{avg_rating:.1f}"
            )
            st.metric(
                label="Количество комментариев",
                value=f"{num_comments}"
            )

    st.write('### flamp.ru')


    df_fl = filtered_data_tag[filtered_data_tag['Каталог'] == 'flamp.ru']
    df_fl_all = filtered_data[filtered_data['Каталог'] == 'flamp.ru']
    # Создаем два столбца

    # Проверяем, есть ли данные для отображения
    if df_fl.empty or df_fl_all.empty:
        st.warning("Нет данных для отображения по flamp.ru")
    else:
        col1, col2 = st.columns(2)

        with col1:
            # Кольцевая диаграмма распределения категорий
            category_counts = df_fl['Категория'].value_counts().reset_index()
            category_counts.columns = ['Категория', 'Количество']

            fig_fl = px.pie(
                category_counts,
                values='Количество',
                names='Категория',
                hole=0.5,
                color_discrete_sequence=px.colors.qualitative.Prism
            )
            fig_fl.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig_fl, use_container_width=True, key='4')

        with col2:
            # Метрики для 2GIS
            avg_rating = df_fl_all['Рейтинг'].mean()
            num_comments = len(df_fl_all)
            st.metric(
                label="Средний рейтинг",
                value=f"{avg_rating:.1f}"
            )
            st.metric(
                label="Количество комментариев",
                value=f"{num_comments}"
            )



# ====================== СТРАНИЦА 2 ======================
elif st.session_state.page == 'page2':
    st.write("""# Топ-партнеров""")

    st.sidebar.header('Параметры')

    st.sidebar.write("Выберите период:")
    col1, col2 = st.sidebar.columns(2)
    with col1:
        start = st.date_input("Начало",
                              value=date(start_year, start_month, start_day),
                              min_value=date(start_year, start_month, start_day),
                              max_value=date(end_year, end_month, end_day))
    with col2:
        end = st.date_input("Конец",
                            value=date(end_year, end_month, end_day),
                            min_value=date(start_year, start_month, start_day),
                            max_value=date(end_year, end_month, end_day))

    tags = st.selectbox('Тег', (tag_list), None)

    data_with_tags = pd.merge(data, tags_category, on='id Отзыва')

    filtered_data = data_with_tags[
        (data_with_tags['Дата'] >= start) &
        (data_with_tags['Дата'] <= end) &
        (data_with_tags['Тег'] == tags)
        ]


    # Группируем по партнерам и АЗС
    partner_stats = filtered_data.groupby(['Партнер', 'АЗС']).size().reset_index(name='Количество тегов')

    # Сортируем и берем топ-10
    top_partners = partner_stats.sort_values('Количество тегов', ascending=False).head(10)

    # Отображаем таблицу
    st.header(f"Топ-10 партнеров по тегу '{tags}'")

    # Красивое отображение таблицы
    st.dataframe(
        top_partners,
        column_config={
            "Партнер": st.column_config.TextColumn("Партнер", width="medium"),
            "Номер АЗС": st.column_config.TextColumn("Номер АЗС"),
            "Количество тегов": st.column_config.NumberColumn(
                "Количество",
                format="%d",
                help="Количество выбранных тегов за период"
            )
        },
        hide_index=True,
        use_container_width=True
    )
    data_with_tags = pd.merge(data, tags_category, on='id Отзыва')

    filtered_data = data[
        (data['Дата'] >= start) &
        (data['Дата'] <= end)
        ]

    # Группируем данные по партнерам и АЗС
    partner_stats = filtered_data.groupby(['Партнер', 'АЗС']).agg(
        Средний_рейтинг=('Рейтинг', 'mean'),
        Количество_отзывов=('id Отзыва', 'count')
    ).reset_index()


    # Сортируем и получаем топы
    top_partners = partner_stats.sort_values(['Средний_рейтинг', 'Количество_отзывов'], ascending=[False, False]).head(
        10)
    bottom_partners = partner_stats.sort_values(['Средний_рейтинг', 'Количество_отзывов']).head(10)

    # Отображаем таблицы в двух колонках
    st.header("Топ партнеров по рейтингу")
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Топ-10 с наивысшим рейтингом")
        st.dataframe(
            top_partners,
            column_config={
                "Партнер": st.column_config.TextColumn("Партнер", width="small"),
                "Номер АЗС": st.column_config.TextColumn("АЗС"),
                "Средний_рейтинг": st.column_config.NumberColumn(
                    "Рейтинг",
                    format="%.1f",
                    help="Средний рейтинг по отзывам"
                ),
                "Количество_отзывов": st.column_config.NumberColumn(
                    "Отзывов",
                    format="%d"
                )
            },
            hide_index=True,
            use_container_width=True
        )

    with col2:
        st.subheader("Топ-10 с наименьшим рейтингом")
        st.dataframe(
            bottom_partners,
            column_config={
                "Партнер": st.column_config.TextColumn("Партнер", width="small"),
                "Номер АЗС": st.column_config.TextColumn("АЗС"),
                "Средний_рейтинг": st.column_config.NumberColumn(
                    "Рейтинг",
                    format="%.1f"
                ),
                "Количество_отзывов": st.column_config.NumberColumn(
                    "Отзывов",
                    format="%d"
                )
            },
            hide_index=True,
            use_container_width=True
        )

        # Добавляем визуализацию для первых 5 партнеров
    if not bottom_partners.empty:
        # Получаем 5 худших партнеров и их АЗС из таблицы
        worst_5 = bottom_partners.head(5)[['Партнер', 'АЗС']].values.tolist()
        data_with_tags = pd.merge(data, tags_category, on='id Отзыва')

        filtered_data = data_with_tags[
            (data_with_tags['Дата'] >= start) &
            (data_with_tags['Дата'] <= end)
            ]
        # Фильтруем исходные данные по этим парам (партнер + АЗС)
        worst_data = filtered_data[
            filtered_data.apply(lambda x: [x['Партнер'], x['АЗС']] in worst_5, axis=1)
        ]

        # Группируем по партнеру, АЗС и категории
        category_counts = worst_data.groupby(['Партнер', 'АЗС', 'Категория']).size().reset_index(
            name='Количество')

        # Создаем комбинированный столбец для отображения
        category_counts['Партнер и АЗС'] = category_counts['Партнер'] + ' (' + category_counts['АЗС'].astype(str) + ')'

        # Строим горизонтальную столбчатую диаграмму
        fig = px.bar(
            category_counts,
            x='Количество',
            y='Партнер и АЗС',
            color='Категория',
            orientation='h',
            title='Категории жалоб для 5 худших партнеров и их АЗС',
            labels={'Количество': 'Количество жалоб'},
            color_discrete_sequence=px.colors.qualitative.Pastel,
            height=700,
            barmode='group'
        )

        # Настраиваем отображение
        fig.update_layout(
            yaxis={'categoryorder': 'total ascending'},
            legend=dict(
                title='Категории',
                orientation='h',
                yanchor='bottom',
                y=-0.5,
                xanchor='center',
                x=0.5
            ),
            margin=dict(b=150)
        )

        # Добавляем подписи
        fig.update_traces(
            texttemplate='%{x}',
            textposition='outside'
        )

        st.plotly_chart(fig, use_container_width=True)
if st.session_state.page == 'page3':

    st.write("""# Анализ отработки отзывов""")

    st.sidebar.header('Параметры')

    st.sidebar.write("Выберите период:")
    col1, col2 = st.sidebar.columns(2)
    with col1:
        start = st.date_input("Начало",
                              value = date(start_year, start_month, start_day),
                              min_value=date(start_year, start_month, start_day),
                              max_value=date(end_year, end_month, end_day))
    with col2:
        end = st.date_input("Конец",
                            value=date(end_year, end_month, end_day),
                            min_value=date(start_year, start_month, start_day),
                            max_value=date(end_year, end_month, end_day))

    azs = st.sidebar.multiselect('Номер АЗС', (number_azs), number_azs)


    filtered_data = data[
            (data['Дата'] >= start) &
            (data['Дата'] <= end) &
            (data['АЗС'].isin(azs))
            ]


    comment_count = len(filtered_data)
    # Выводим метрику
    st.metric(
            label="Количество комментариев",
            value=comment_count
        )


    ans, ton = st.columns(2)
    with ans:
        # Подготовка данных
        response_stats = filtered_data['Ответ'].apply(
            lambda x: 'С ответом' if pd.notna(x) else 'Без ответа').value_counts().reset_index()
        response_stats.columns = ['Статус', 'Количество']

        # Создание кольцевой диаграммы
        fig_response = px.pie(
            response_stats,
            values='Количество',
            names='Статус',
            title="Наличие ответа на комментарии",
            color='Статус',
            # color_discrete_map={
            #     'С ответом': '#4CAF50',  # Зеленый
            #     'Без ответа': '#F44336'  # Красный
            # },
            hole=0.5  # Делаем кольцевую диаграмму (donut)
        )

        # Настройка отображения
        fig_response.update_traces(
            textposition='inside',
            textinfo='percent+value',
            insidetextfont=dict(size=12, color='white'),
            marker=dict(
                line=dict(color='#FFFFFF', width=1)
                # colors=['#4CAF50', '#F44336']  # Дублируем цвета
            )
        )

        fig_response.update_layout(
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.2,
                xanchor="center",
                x=0.5
            ),
            margin=dict(t=50, b=0, l=0, r=0),
            uniformtext_minsize=12,
            uniformtext_mode='hide'
        )
        st.plotly_chart(fig_response, use_container_width=True)

    with ton:
        # Объединяем таблицы с тональностью
        data_with_ton = pd.merge(data, tonal, on='id Отзыва')

        # Фильтруем только неотвеченные комментарии
        unanswered = data_with_ton[data_with_ton['Ответ'].isna()]

        filtered_unanswered = unanswered[
            (unanswered['Дата'] >= start) &
            (unanswered['Дата'] <= end) &
            (unanswered['АЗС'].isin(azs))
            ]
        # Группируем по тональности и считаем количество
        tonality_counts = filtered_unanswered['Тональность'].value_counts().reset_index()
        tonality_counts.columns = ['Тональность', 'Количество']

        # Сортируем по заданному порядку тональностей
        tonality_order = ['негативная', 'смешанная', 'нейтральная', 'позитивная']
        tonality_counts['Тональность'] = pd.Categorical(
            tonality_counts['Тональность'],
            categories=tonality_order,
            ordered=True
        )
        tonality_counts = tonality_counts.sort_values('Тональность')

        # Создаем столбчатую диаграмму
        fig = px.bar(
            tonality_counts,
            x='Тональность',
            y='Количество',
            title='Распределение неотвеченных комментариев по тональности',
            color='Тональность',
            color_discrete_map={
                'позитивная': '#73af48',
                'негативная': '#ff5454',
                'нейтральная': '#ffe354',
                'смешанная': '#a154ff'
            },
            text='Количество'
        )

        # Настраиваем внешний вид
        fig.update_traces(
            textposition='outside',
            marker_line_color='rgb(255,255,255)',
            marker_line_width=1.5,
            opacity=0.9
        )

        fig.update_layout(
            xaxis_title=None,
            yaxis_title='Количество комментариев',
            showlegend=False,
            uniformtext_minsize=8,
            uniformtext_mode='hide',
            plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(t=50, b=0, l=0, r=0)
        )

        # Выводим диаграмму
        st.plotly_chart(fig, use_container_width=True)


    # Разделяем экран на две колонки
    col1, col2 = st.columns([2, 5])

    # Первая колонка - метрика среднего времени обработки
    with col1:
        # Рассчитываем среднее время обработки (в часах)
        avg_time = filtered_data['Время обработки отзыва'].mean()/60
        # Выводим метрику
        st.metric(
            label="Среднее время ответа (часы)",
            value=f"{avg_time:.1f}",
            help="Рассчитано по выбранным фильтрам"
        )

    # Вторая колонка - список комментариев
    # with col2:
    #     st.subheader("Комментарии по выбранным фильтрам")
    #
    #     # Создаем расширяемый контейнер для комментариев
    #     with st.expander("Показать комментарии", expanded=True):
    #         # Отображаем только нужные колонки
    #         comments_df = filtered_data[['Дата', 'АЗС', 'Отзыв']]
    #
    #         # # Форматируем дату для лучшего отображения
    #         # comments_df['дата'] = comments_df['дата'].dt.strftime('%d.%m.%Y')
    #
    #         # Выводим в виде таблицы с возможностью прокрутки
    #         st.dataframe(
    #             comments_df,
    #             column_config={
    #                 "Дата": "Дата",
    #                 "АЗС": st.column_config.TextColumn("АЗС", width="small"),
    #                 "Отзыв": st.column_config.TextColumn("Отзыв", width="large")
    #             },
    #             hide_index=True,
    #             use_container_width=True,
    #             height=400  # Фиксированная высота с прокруткой
    #         )



