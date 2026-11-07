"""
Қылмыс статистикасына арналған интерактивті Dash дашборды
"""

import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output


# 1. ДЕРЕКТЕРДІ ЖҮКТЕУ ЖӘНЕ ТАЗАЛАУ

FILE_PATH = 'data.csv'  # немесе 'data.xlsx'

if FILE_PATH.endswith('.csv'):
    df = pd.read_csv('crimes.csv')
else:
    df = pd.read_excel('crimes.xlsx')

if 'Удалено' in df.columns:
    df = df[df['Удалено'] == False].copy()

if 'Дата совершения' in df.columns:
    df['Дата совершения'] = pd.to_datetime(df['Дата совершения'], errors='coerce')


# 2. DASH ҚОСЫМШАСЫН БАСТАУ

app = Dash(__name__)
app.title = "Қылмыс статистикасы дашборды"

years = sorted(df['Год'].dropna().unique())
districts = sorted(df['Район'].dropna().unique())


# 3. АУДАРМА СӨЗДІГІ (KK / RU / EN)

TRANSLATIONS = {
    'kk': {
        'title': 'Қылмыс статистикасы дашборды',
        'year_range': 'Жыл диапазоны',
        'district': 'Аудан',
        'all_districts': 'Барлық аудандар',
        'total_records': 'Барлық жазба',
        'district_count': 'Аудан саны',
        'crime_type_count': 'Қылмыс түрі саны',
        'tab_time': 'Уақыт трендi',
        'tab_district': 'Аудандар',
        'tab_type': 'Қылмыс түрі',
        'tab_map': 'Карта',
        'time_title': 'Жыл бойынша қылмыс саны',
        'district_title': 'Топ-15 аудан бойынша қылмыс саны',
        'type_title': 'Топ-15 қылмыс түрі',
        'severity_title': 'Ауырлық дәрежесі бойынша үлес',
        'count': 'Саны',
        'severity': 'Тяжесть',
    },
    'ru': {
        'title': 'Дашборд статистики преступлений',
        'year_range': 'Диапазон лет',
        'district': 'Район',
        'all_districts': 'Все районы',
        'total_records': 'Всего записей',
        'district_count': 'Кол-во районов',
        'crime_type_count': 'Кол-во видов преступлений',
        'tab_time': 'Тренд по времени',
        'tab_district': 'Районы',
        'tab_type': 'Вид преступления',
        'tab_map': 'Карта',
        'time_title': 'Количество преступлений по годам',
        'district_title': 'Топ-15 районов по количеству преступлений',
        'type_title': 'Топ-15 видов преступлений',
        'severity_title': 'Доля по степени тяжести',
        'count': 'Количество',
        'severity': 'Тяжесть',
    },
    'en': {
        'title': 'Crime Statistics Dashboard',
        'year_range': 'Year range',
        'district': 'District',
        'all_districts': 'All districts',
        'total_records': 'Total records',
        'district_count': 'District count',
        'crime_type_count': 'Crime type count',
        'tab_time': 'Time trend',
        'tab_district': 'Districts',
        'tab_type': 'Crime type',
        'tab_map': 'Map',
        'time_title': 'Crime count by year',
        'district_title': 'Top 15 districts by crime count',
        'type_title': 'Top 15 crime types',
        'severity_title': 'Share by severity level',
        'count': 'Count',
        'severity': 'Severity',
    },
}


# 4. LAYOUT (СЫРТҚЫ КӨРІНІС)

app.layout = html.Div(style={'fontFamily': 'Arial', 'margin': '20px'}, children=[

    html.Div(style={'display': 'flex', 'justifyContent': 'space-between', 'alignItems': 'center'}, children=[
        html.H1(id='page-title', style={'textAlign': 'center', 'flex': 1}),
        dcc.Dropdown(
            id='lang-selector',
            options=[
                {'label': 'Қазақша', 'value': 'kk'},
                {'label': 'Русский', 'value': 'ru'},
                {'label': 'English', 'value': 'en'},
            ],
            value='kk',
            clearable=False,
            style={'width': '160px'}
        )
    ]),

    # --- Сүзгілер ---
    html.Div(style={'display': 'flex', 'gap': '20px', 'marginBottom': '20px'}, children=[
        html.Div([
            html.Label(id='label-year-range'),
            dcc.RangeSlider(
                id='year-slider',
                min=min(years), max=max(years), step=1,
                value=[min(years), max(years)],
                marks={int(y): str(int(y)) for y in years}
            )
        ], style={'flex': 2}),

        html.Div([
            html.Label(id='label-district'),
            dcc.Dropdown(
                id='district-filter',
                options=[{'label': d, 'value': d} for d in districts],
                multi=True,
                placeholder=""
            )
        ], style={'flex': 1}),
    ]),

    # --- Metric карталары ---
    html.Div(id='metric-cards', style={'display': 'flex', 'gap': '16px', 'marginBottom': '20px'}),

    # --- Графиктер (қойындылар) ---
    dcc.Tabs(id='tabs', value='tab-time', children=[
        dcc.Tab(id='tab-time-label', label='', value='tab-time'),
        dcc.Tab(id='tab-district-label', label='', value='tab-district'),
        dcc.Tab(id='tab-type-label', label='', value='tab-type'),
        dcc.Tab(id='tab-map-label', label='', value='tab-map'),
    ]),
    html.Div(id='tab-content')
])



# 5. CALLBACK-ТЕР (ИНТЕРАКТИВТІЛІК)


def filter_df(year_range, selected_districts):
    dff = df[(df['Год'] >= year_range[0]) & (df['Год'] <= year_range[1])]
    if selected_districts:
        dff = dff[dff['Район'].isin(selected_districts)]
    return dff


# --- Тіл өзгергенде барлық статикалық мәтіндерді жаңарту ---
@app.callback(
    Output('page-title', 'children'),
    Output('label-year-range', 'children'),
    Output('label-district', 'children'),
    Output('district-filter', 'placeholder'),
    Output('tab-time-label', 'label'),
    Output('tab-district-label', 'label'),
    Output('tab-type-label', 'label'),
    Output('tab-map-label', 'label'),
    Input('lang-selector', 'value')
)
def update_static_text(lang):
    t = TRANSLATIONS[lang]
    return (
        t['title'], t['year_range'], t['district'], t['all_districts'],
        t['tab_time'], t['tab_district'], t['tab_type'], t['tab_map']
    )


@app.callback(
    Output('metric-cards', 'children'),
    Input('year-slider', 'value'),
    Input('district-filter', 'value'),
    Input('lang-selector', 'value')
)
def update_metrics(year_range, selected_districts, lang):
    t = TRANSLATIONS[lang]
    dff = filter_df(year_range, selected_districts)
    card_style = {
        'background': '#f4f4f4', 'borderRadius': '8px', 'padding': '16px',
        'flex': 1, 'textAlign': 'center'
    }
    return [
        html.Div([html.P(t['total_records']), html.H3(f"{len(dff):,}")], style=card_style),
        html.Div([html.P(t['district_count']), html.H3(f"{dff['Район'].nunique()}")], style=card_style),
        html.Div([html.P(t['crime_type_count']), html.H3(f"{dff['Вид преступления'].nunique()}")], style=card_style),
    ]


@app.callback(
    Output('tab-content', 'children'),
    Input('tabs', 'value'),
    Input('year-slider', 'value'),
    Input('district-filter', 'value'),
    Input('lang-selector', 'value')
)
def render_tab(tab, year_range, selected_districts, lang):
    t = TRANSLATIONS[lang]
    dff = filter_df(year_range, selected_districts)

    if tab == 'tab-time':
        yearly = dff.groupby('Год')['ID'].count().reset_index()
        fig = px.line(yearly, x='Год', y='ID', markers=True, title=t['time_title'])
        return dcc.Graph(figure=fig)

    elif tab == 'tab-district':
        top_districts = dff['Район'].value_counts().head(15).reset_index()
        top_districts.columns = ['Район', t['count']]
        fig = px.bar(top_districts, x=t['count'], y='Район', orientation='h',
                      title=t['district_title'])
        fig.update_layout(yaxis={'categoryorder': 'total ascending'})
        return dcc.Graph(figure=fig)

    elif tab == 'tab-type':
        top_types = dff['Вид преступления'].value_counts().head(15).reset_index()
        top_types.columns = ['Вид преступления', t['count']]
        fig = px.bar(top_types, x=t['count'], y='Вид преступления', orientation='h',
                      title=t['type_title'])
        fig.update_layout(yaxis={'categoryorder': 'total ascending'})

        severity = dff['Тяжесть преступления'].value_counts().reset_index()
        severity.columns = [t['severity'], t['count']]
        fig2 = px.pie(severity, names=t['severity'], values=t['count'],
                       title=t['severity_title'])

        return html.Div(style={'display': 'flex', 'gap': '20px'}, children=[
            dcc.Graph(figure=fig, style={'flex': 1}),
            dcc.Graph(figure=fig2, style={'flex': 1}),
        ])

    elif tab == 'tab-map':
        geo_dff = dff.dropna(subset=['Широта', 'Долгота'])
        geo_dff = geo_dff[(geo_dff['Широта'] != 0) & (geo_dff['Долгота'] != 0)]
        sample = geo_dff.sample(min(20000, len(geo_dff)), random_state=42)
        fig = px.scatter_mapbox(
            sample, lat='Широта', lon='Долгота',
            hover_data=['Район', 'Вид преступления','Улица'],
            zoom=10, height=600, opacity=0.4
        )
        fig.update_layout(mapbox_style='open-street-map', margin={'l': 0, 'r': 0, 't': 0, 'b': 0})
        return dcc.Graph(figure=fig)



# 6. ІСКЕ ҚОСУ

if __name__ == '__main__':
    app.run(debug=True)
    