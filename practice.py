import streamlit as st
import pandas as pd
import datetime
import plotly.graph_objects as go
from PIL import Image
import calendar
import plotly.express as px
# Məlumatların yüklənməsi
fact_url = 'https://drive.google.com/uc?id=1lfRDeRq36e-wBn6undzT1DxlDiKst_8M&export=download'
fakt_df = pd.read_csv(fact_url)
plan_df = pd.read_excel("plan fakt.xlsx")
plan_fr = pd.read_excel("Ekspeditor Fraxt.xlsx")

# Tarix sütunlarını datetime formatına çevirmək
fakt_df['Tarix'] = pd.to_datetime(fakt_df['Tarix'], errors='coerce')
plan_df['Tarix'] = pd.to_datetime(plan_df['Tarix'], errors='coerce')
plan_fr['Tarix'] = pd.to_datetime(plan_fr['Tarix'], errors='coerce') 
# Səhifəni tənzimləmək
st.set_page_config(layout="wide")
st.markdown('<style>div.block-container{padding-top:3rem;}</style>', unsafe_allow_html=True)

# Səhifəni seçin
page = st.sidebar.radio(
    "Səhifəni seçin",
    ("Report", "Current Month", "Current Year", "Tranzit")
)

if page == "Report":
    
    image = Image.open('Picture1.png')

    col1, col2 = st.columns([0.1, 0.9])
    with col1:
        st.image(image, width=100)
    
    dashboard_title = """
        <style>
        .title-test{
        font-weight:bold;
        padding:2px;
        border-radius:4px;
        color: #16105c;
        }
        </style>
        <center><h3 class="title-test">Ekspeditorlar üzrə aylıq və illik daşınma məlumatları</h3></center>
    """
    with col2:
        st.markdown(dashboard_title, unsafe_allow_html=True)

    col3, col4 = st.columns(2)
    
    # Filterlər
    with col3:
        # Tarix filteri üçün başlanğıc və bitiş tarixini seçmək
        selected_dates = st.date_input(
            '',
            value=[fakt_df['Tarix'].min().date(), fakt_df['Tarix'].max().date()],
            min_value=fakt_df['Tarix'].min().date(),
            max_value=fakt_df['Tarix'].max().date()
        )

        # Əgər yalnız bir tarix seçilərsə, həmin tarixi həm başlanğıc, həm də bitiş tarixi kimi qəbul edirik
        if len(selected_dates) == 1:
            start_date = pd.to_datetime(selected_dates[0])
            end_date = start_date
        else:
            start_date = pd.to_datetime(selected_dates[0])
            end_date = pd.to_datetime(selected_dates[1])

        # Seçilmiş tarix aralığına görə fakt datasını filtr edirik
        filtered_fakt_df = fakt_df[(fakt_df['Tarix'] >= start_date) & (fakt_df['Tarix'] <= end_date)]

    with col4:
        # Rejimlər üçün unikal dəyərləri əldə edirik
        rejimler_plan = plan_df['Rejim'].unique()
        rejimler_fakt = fakt_df['Rejim'].unique()
        rejimler = list(set(rejimler_plan) | set(rejimler_fakt))

        # Rejimləri seçmək üçün multiselect
        selected_rejim = st.multiselect('', rejimler, default=rejimler)

    # Seçilmiş rejimlər və tarix aralığına görə plan datasını filtr edirik
    plan_df_filtered = plan_df[
        (plan_df['Tarix'] >= start_date) & 
        (plan_df['Tarix'] <= end_date) & 
        (plan_df['Rejim'].isin(selected_rejim))
    ]

    # **Plan həcmi hesablanması**
    total_plan = 0
    for rejim in selected_rejim:
        start_month = start_date.month
        end_month = end_date.month
        start_year = start_date.year
        end_year = end_date.year

        for year in range(start_year, end_year + 1):
            for month in range(1, 13):
                if (year == start_year and month < start_month) or (year == end_year and month > end_month):
                    continue
                if year == end_year and month == end_month:
                    days_in_month = calendar.monthrange(year, month)[1]
                    days_to_include = min(days_in_month, end_date.day)
                    monthly_plan = plan_df[(plan_df['Rejim'] == rejim) & (plan_df['Tarix'].dt.month == month)]['plan hecm'].sum()
                    total_plan += (monthly_plan / days_in_month) * days_to_include
                else:
                    monthly_plan = plan_df[(plan_df['Rejim'] == rejim) & (plan_df['Tarix'].dt.month == month)]['plan hecm'].sum()
                    total_plan += monthly_plan

    # Faktik məlumatları toplamaq (seçilmiş rejim və tarix aralığı üzrə)
    total_fakt = filtered_fakt_df[filtered_fakt_df['Rejim'].isin(selected_rejim)]['Həcm_fakt'].sum()

    # % fərqini hesablamaq
    if total_plan > 0:
        percent_difference = (total_fakt / total_plan) * 100
    else:
        percent_difference = 0

    # Kartları göstərmək üçün 3 sütun
    col5, col6, col7 = st.columns(3)

    # Kart tərzi üçün CSS
    card_style = """
        <style>
        .card {
            box-shadow: 0 4px 8px 0 rgba(0, 0, 0, 0.2);
            transition: 0.3s;
            width: 100%;
            padding: 9px;
            border-radius: 8px;
            background-color: #ecebf2;
            text-align: center;
        }

        .card:hover {
            box-shadow: 0 8px 16px 0 rgba(0, 0, 0, 0.2);
        }

        .container {
            padding: 2px 9px;
        }
        .big-font {{
                font-size: 20px;
                font-weight: bold;
                color: #05073b;
            }}
            .small-font {{
                font-size: 24px;
                color: #05073b;
                font-weight: bold;
            }}
        </style>
    """

    # CSS kodunu tətbiq etmək
    st.markdown(card_style, unsafe_allow_html=True)

    # col5-də plan kartı (tam rəqəmlə vergüllə ayrılan format)
    with col5:
        st.markdown(f"""
        <div class="card" style="text-align: center;">
            <h3 style="font-size:24px; color: #10265c;"><strong>Plan</strong></h3>
            <p style="font-size: 28px; color: #10265c;"><strong>{total_plan:,.0f}</strong></p>
        </div>
        """.replace(',', 'X').replace('.', ',').replace('X', ','), unsafe_allow_html=True)

    # col6-da faktiki kart (tam rəqəmlə vergüllə ayrılan format)
    with col6:
        st.markdown(f"""
        <div class="card" style="text-align: center;">
            <h3 style="font-size:24px; color: #10265c;">Fakt</h3>
            <p style="font-size: 28px; color: #10265c;"><strong>{total_fakt:,.0f}</strong></p>
        </div>
        """.replace(',', 'X').replace('.', ',').replace('X', ','), unsafe_allow_html=True)

    # col7-də faiz fərqi kartı (faiz dəyərini iki onluq dəqiqliklə göstəririk)
    with col7:
        st.markdown(f"""
        <div class="card" style="text-align: center;">
            <h3 style="font-size:24px; color: #10265c;">Yerinə yetirmə %</h3>
            <p style="font-size: 28px; color: #10265c;"><strong>{percent_difference:.0f}%</strong></p>
        </div>
        """, unsafe_allow_html=True)

    # Ekspeditorlar üzrə məlumatları toplamaq
    ekspeditor_plan_list = plan_df['Ekspeditor'].unique()
    ekspeditor_fakt_list = filtered_fakt_df['Eksp'].unique()

    # Plan datasında olmayan lakin fakt datasında olan ekspeditorları əlavə edirik
    all_ekspeditor_list = list(set(ekspeditor_plan_list) | set(ekspeditor_fakt_list))

    table_data = []

    for eksp in all_ekspeditor_list:
        total_plan_eksp = 0
        total_fakt_eksp = 0
        for rejim in selected_rejim:
            for year in range(start_date.year, end_date.year + 1):
                for month in range(1, 13):
                    if (year == start_date.year and month < start_date.month) or (year == end_date.year and month > end_date.month):
                        continue
                    if year == end_date.year and month == end_date.month:
                        days_in_month = calendar.monthrange(year, month)[1]
                        days_to_include = min(days_in_month, end_date.day)
                        monthly_plan = plan_df[(plan_df['Rejim'] == rejim) & (plan_df['Ekspeditor'] == eksp) & (plan_df['Tarix'].dt.month == month) & (plan_df['Tarix'].dt.year == year)]['plan hecm'].sum()
                        total_plan_eksp += (monthly_plan / days_in_month) * days_to_include
                    else:
                        monthly_plan = plan_df[(plan_df['Rejim'] == rejim) & (plan_df['Ekspeditor'] == eksp) & (plan_df['Tarix'].dt.month == month) & (plan_df['Tarix'].dt.year == year)]['plan hecm'].sum()
                        total_plan_eksp += monthly_plan

            # Fakt həcmi həmin tarix aralığı üzrə hesablanır
            total_fakt_eksp += filtered_fakt_df[(filtered_fakt_df['Rejim'] == rejim) & (filtered_fakt_df['Eksp'] == eksp)]['Həcm_fakt'].sum()

        # Faiz hesablanması
        if total_plan_eksp > 0:
            yerinə_yetirmə_faizi = (total_fakt_eksp / total_plan_eksp) * 100
        else:
            yerinə_yetirmə_faizi = 0

        # Məlumatları cədvəl üçün hazırlamaq
        table_data.append({
            'Ekspeditor': eksp,
            'Plan Həcmi': total_plan_eksp,
            'Fakt Həcmi': total_fakt_eksp,
            '% Yerinə Yetirmə': yerinə_yetirmə_faizi
        })

    # Məlumatları DataFrame formatına salırıq
    table_df = pd.DataFrame(table_data)

    # Ümumi fakt həcmini toplayırıq
    total_fakt_all = table_df['Fakt Həcmi'].sum()

    # Ümumi daşınma payı sütununu hesablayırıq
    table_df['Umumi dasinma payi'] = (table_df['Fakt Həcmi'] / total_fakt_all) * 100

    # Cədvəli azalan sıraya görə sırala
    table_df_sorted = table_df.sort_values(by=['Plan Həcmi', 'Fakt Həcmi'], ascending=False)

    # Plan və Fakt həcmlərini formatlamaq
    table_df_sorted['Plan Həcmi'] = table_df_sorted['Plan Həcmi'].apply(lambda x: f"{x:,.0f}".replace(',', 'X').replace('.', ',').replace('X', ','))
    table_df_sorted['Fakt Həcmi'] = table_df_sorted['Fakt Həcmi'].apply(lambda x: f"{x:,.0f}".replace(',', 'X').replace('.', ',').replace('X', ','))
    table_df_sorted['% Yerinə Yetirmə'] = table_df_sorted['% Yerinə Yetirmə'].apply(lambda x: f"{x:.0f}%")
    table_df_sorted['Umumi dasinma payi'] = table_df_sorted['Umumi dasinma payi'].apply(lambda x: f"{x:.0f}%")


    # **Cədvəl Yaratmaq**
    header_values = ['Ekspeditor', 'Plan', 'Fakt', 'Yerinə Yetirmə %', 'Daşınma payı']
    cell_values = [
        table_df_sorted['Ekspeditor'],
        table_df_sorted['Plan Həcmi'],
        table_df_sorted['Fakt Həcmi'],
        table_df_sorted['% Yerinə Yetirmə'],
        table_df_sorted['Umumi dasinma payi']
    ]

    fig_table = go.Figure(data=[go.Table(
        header=dict(
            values=header_values,
            fill_color='#011836',
            font=dict(color='white', size=18),
            align='center',
            height=35,
            line_color='white'
        ),
        cells=dict(
            values=cell_values,
            fill_color=[['#eeedf2'] * len(table_df_sorted)],
            align='center',
            font=dict(color='black', size=14),
            line_color='#c0bfc9',
            height=23

        )
    )])

    fig_table.update_layout(
        width=2000,
        height=400,
        margin=dict(l=10, r=10, t=16, b=2)
    )

        
    # Plotly cədvəlini göstəririk
    st.plotly_chart(fig_table)
    # **Bar Chart Yaratmaq**
    st.markdown("<h4 style='color:#05031c; text-align: center; font-size: 25px; font-weight: bold;'>Ekspeditorlar üzrə Plan və Fakt Həcmləri</h4>", unsafe_allow_html=True)



    # Bar chart yaratmaq
    fig_plan_fact = go.Figure(data=[
        go.Bar(
            name='Plan',
            x=table_df_sorted['Ekspeditor'],
            y=table_df_sorted['Plan Həcmi'].apply(lambda x: float(x.replace(',', ''))),
            marker_color='#263066',
            text=table_df_sorted['Plan Həcmi'],
            textposition='outside',
            textfont_size=14,
            textfont_color='black',
            marker_line_color='black',
            marker_line_width=1.5
        ),
        go.Bar(
            name='Fakt',
            x=table_df_sorted['Ekspeditor'],
            y=table_df_sorted['Fakt Həcmi'].apply(lambda x: float(x.replace(',', ''))),
            marker_color='#a2b0fc',
            text=table_df_sorted['Fakt Həcmi'],
            textposition='outside',
            textfont_size=14,
            textfont_color='black',
            marker_line_color='black',
            marker_line_width=1.5
        )
    ])

    # Layout parametrləri və grid xəttlərini silmək
    fig_plan_fact.update_layout(
    barmode='group',
    template="plotly_white",
    xaxis=dict(
        showgrid=False,
        tickfont=dict(size=12, color='black'),
    ),
    yaxis=dict(
        showgrid=False,
        tickfont=dict(size=12, color='black')
    ),
    title="",
    title_x=0,
    legend_title="",
    margin=dict(l=5, r=5, t=20, b=5)  # Bar chart üçün kənar boşluqları daha kiçik təyin edirik
    )
    # Plotly bar chartını göstəririk
    st.plotly_chart(fig_plan_fact)

elif page == "Tranzit":
    # Şəkili göstərmək
    image = Image.open('Picture1.png')
    col1, col2 = st.columns([0.1, 0.9])
    with col1:
        st.image(image, width=100)
    
    # Başlıq üçün dizayn
    dashboard_title = """
        <style>
        .title-test{
        font-weight:bold;
        padding:2px;
        border-radius:4px;
        color: #16105c;
        }
        </style>
        <center><h3 class="title-test">Tranzit rejimdə yük göndərən ölkələr üzrə daşınma statistikası</h3></center>
    """
    with col2:
        st.markdown(dashboard_title, unsafe_allow_html=True)

    # Start Date və End Date başlıqları üçün qırmızı rəng
        st.markdown("""
            <style>
            .date-label {
                color: red;
                font-weight: bold;
                font-size: 18px;
            }
            </style>
            """, unsafe_allow_html=True)

    # Tarix aralığını seçmək üçün iki yanaşı column istifadə edirik
        col_start, col_end = st.columns(2)  # Tarixləri yanaşı göstərmək üçün iki column yaradırıq

    with col_start:
        st.markdown('<p class="date-label">Start Date</p>', unsafe_allow_html=True)
        start_date = st.date_input(' ', fakt_df['Tarix'].min())  # Başlığı boş string ilə gizlətmək

    with col_end:
        st.markdown('<p class="date-label">End Date</p>', unsafe_allow_html=True)
        end_date = st.date_input('  ', fakt_df['Tarix'].max())  # Başlığı boş string ilə gizlətməkgizlədirik

    # Filtrə əsasən məlumatların süzülməsi (yalnız Tranzit rejimi və "Digər yüklər" xaric)
    filtered_df = fakt_df[(fakt_df['Tarix'] >= pd.to_datetime(start_date)) & 
                          (fakt_df['Tarix'] <= pd.to_datetime(end_date)) & 
                          (fakt_df['Rejim'] == 'Tranzit') & 
                          (fakt_df['əsas_yüklər'] != 'Digər yüklər')]

    # "Malın adı", "Göndərən ölkə" və "GSA"-ya görə qruplaşdırma və "Vaqon_sayı", "Həcm_fakt" cəmlənməsi
    grouped_df = filtered_df.groupby(['Malın_adı', 'Göndərən ölkə', 'GSA']).agg({
        'Vaqon_sayı': 'sum',
        'Həcm_fakt': 'sum'
    }).reset_index()

    # Adlara görə qruplaşdırmaq və Həcm_fakta görə azalan sırada sıralamaq
    grouped_df = grouped_df.sort_values(by=['Malın_adı', 'Həcm_fakt'], ascending=[True, False])

    # Ümumi cəm hesablamaq
    total_vaqon_sayi = grouped_df['Vaqon_sayı'].sum()
    total_hecm_fakt = grouped_df['Həcm_fakt'].sum()

    # Ümumi cəmi olan bir sətir əlavə etmək (ən yuxarıya əlavə etmək üçün)
    total_row = pd.DataFrame({
        'Malın_adı': ['Ümumi cəm'],
        'Göndərən ölkə': [''],
        'GSA': [''],
        'Vaqon_sayı': [total_vaqon_sayi],
        'Həcm_fakt': [total_hecm_fakt]
    })

    # Ümumi cəmi əsas cədvələ yuxarıya əlavə etmək
    grouped_df = pd.concat([total_row, grouped_df], ignore_index=True)

    # Plotly cədvəlini qurmaq (scrollsuz)
    fig = go.Figure(data=[go.Table(
        columnwidth=[250, 200, 200, 100, 100],  # Sütun genişliyini tənzimləmək
        header=dict(values=['Malın adı', 'Göndərən ölkə', 'Göndərən stansiya', 'Vaqon sayı', 'Həcm'],
                    fill_color='#011836',
                    align='center',
                    font=dict(color='white', size=14),
                    height=40,
                    line_color='white'),
        cells=dict(values=[grouped_df['Malın_adı'], grouped_df['Göndərən ölkə'], grouped_df['GSA'], 
                           grouped_df['Vaqon_sayı'].map('{:,.0f}'.format),  # Vaqon sayını vergüllə ayırmaq
                           grouped_df['Həcm_fakt'].map('{:,.0f}'.format)],  # Həcm faktını vergüllə ayırmaq
                   fill_color=[['#c4c1b9'] + ['#F0F2F6'] * (len(grouped_df) - 1)],  # Ümumi cəm üçün qırmızı fon
                   align='center',
                   font=dict(size=14, color=['Black'] + ['black'] * (len(grouped_df) - 1)),  # Ümumi cəm üçün ağ rəng
                   height=30))
    ])

    # Cədvəli göstərmək (scrollsuz)
    fig.update_layout(height=1000, margin=dict(l=10, r=10, b=10, t=10))  # Cədvəlin hündürlüyünü artırmaq
    st.plotly_chart(fig, use_container_width=True)

elif page == "Current Month":
    
     # Şəkili göstərmək
    image = Image.open('Picture1.png')
    col1, col2 = st.columns([0.1, 0.9])
    with col1:
        st.image(image, width=100)
    
    # Başlıq üçün dizayn
    dashboard_title = """
        <style>
        .title-test{
        font-weight:bold;
        padding:2px;
        border-radius:18px;
        color: #16105c;
        }
        </style>
        <center><h3 class="title-test">Rejimlər üzrə aylıq göstəricilər</h3></center>
    """
    with col2:
        st.markdown(dashboard_title, unsafe_allow_html=True)

    # Filterləri yan-yana yerləşdirmək üçün columns() istifadə edirik
    col3, col4= st.columns(2)

    with col3:
        # Tarix filterini fakt datasındakı bütün tarixlərə əsasən hazırlayırıq
        available_dates = fakt_df['Tarix'].dt.date.unique()
        available_dates = sorted(available_dates)

        selected_date = st.selectbox('', available_dates)

        selected_date = pd.to_datetime(selected_date)

    with col4:
        # Rejimlər üçün unikal dəyərləri əldə edirik
        rejimler_plan = plan_df['Rejim'].unique()
        rejimler_fakt = fakt_df['Rejim'].unique()
        rejimler_fr = plan_fr['Rejim'].unique()
        rejimler = list(set(rejimler_plan) | set(rejimler_fakt) | set(rejimler_fr))
        rejimler = sorted(rejimler)

        # Rejim filterini selectbox kimi yaradırıq
        selected_rejim = st.selectbox('', rejimler)

    # Data filtrasiyası
    # Plan datasını seçilmiş ay və ilə görə filtr edirik
    plan_df_filtered = plan_df[
        (plan_df['Tarix'].dt.month == selected_date.month) &
        (plan_df['Tarix'].dt.year == selected_date.year) &
        (plan_df['Rejim'] == selected_rejim)
    ]
    plan_df_fraxt = plan_fr[
        (plan_fr['Tarix'].dt.month == selected_date.month) &
        (plan_fr['Tarix'].dt.year == selected_date.year) &
        (plan_fr['Rejim'] == selected_rejim)
    ]
    # Fakt datasını ayın əvvəli ilə seçilmiş tarix arasında və seçilmiş rejimə görə filtr edirik
    start_of_month = pd.to_datetime(f'{selected_date.year}-{selected_date.month}-01')

    fakt_df_filtered = fakt_df[
        (fakt_df['Tarix'] >= start_of_month) &
        (fakt_df['Tarix'] <= selected_date) &
        (fakt_df['Rejim'] == selected_rejim)
    ]

    # Plan həcmini seçilmiş tarixə uyğun tənzimləmək üçün
    if not plan_df_filtered.empty:
        # Ayın gün sayını və seçilmiş günü hesablayırıq
        days_in_month = calendar.monthrange(selected_date.year, selected_date.month)[1]
        selected_day = selected_date.day

        # Plan həcmini tənzimləyirik
        plan_df_filtered['plan hecm'] = (plan_df_filtered['plan hecm'] / days_in_month) * selected_day
    else:
        plan_df_filtered['plan hecm'] = 0

    # Fraxt plan həcmini hesablayaq
    if not plan_df_fraxt.empty:
        # Ayın gün sayını və seçilmiş günü hesablayırıq
        days_in_month = calendar.monthrange(selected_date.year, selected_date.month)[1]
        selected_day = selected_date.day

        # Fraxt plan həcmini tənzimləyirik
        plan_df_fraxt['Həcm_fraxt'] = (plan_df_fraxt['Həcm_fraxt'] / days_in_month) * selected_day
    else:
        plan_df_fraxt['Həcm_fraxt'] = 0

    # Fakt həcmini hesablayırıq
    total_fact = fakt_df_filtered['Həcm_fakt'].sum()
    total_plan = plan_df_filtered['plan hecm'].sum()
    total_fraxt = plan_df_fraxt['Həcm_fraxt'].sum()

    # Yerinə yetirmə faizini hesablayırıq
    if total_plan == 0:
        total_percentage = 0
    else:
        total_percentage = (total_fact / total_plan) * 100

    # Fraxt üçün yerinə yetirmə faizini hesablayaq
    if total_fraxt == 0:
        total_percfraxt = 0
    else:
        total_percfraxt = (total_fact / total_fraxt) * 100

    # Kartlar üçün formatlanmış dəyərlər
    total_plan_formatted = "{:,.0f}".format(total_plan) if total_plan else "0"
    total_fact_formatted = "{:,.0f}".format(total_fact) if total_fact else "0"
    total_percentage_formatted = "{:,.0f}%".format(total_percentage) if total_percentage else "0%"
    total_percfraxt_formatted = "{:,.0f}%".format(total_percfraxt) if total_percfraxt else "0%"
    total_fraxt_formatted = "{:,.0f}".format(total_fraxt) if total_fraxt else "0"
     # **Üçlü Kartlar: Plan, Fakt və Yerinə Yetirmə Faizi**
    st.markdown("---")
    # HTML kodunu formatlanmış dəyərlərlə birləşdiririk
    html_code = f"""
        <style>
            .card-container {{
                display: flex;
                justify-content: center;
                gap: 20px;
                margin-top: 30px;
            }}
            .metric-box {{
                background-color: #ecebf2;
                border-radius: 10px;
                padding: 20px;
                width: 300px;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
                text-align: center;
                transition: transform 0.3s ease-in-out;
            }}
            .metric-box:hover {{
                transform: scale(1.05);
            }}
            .big-font {{
                font-size: 20px;
                font-weight: bold;
                color: #05073b;
            }}
            .small-font {{
                font-size: 24px;
                color: #05073b;
                font-weight: bold;
            }}
        </style>

        <div class="card-container">
            <div class="metric-box">
                <div class="big-font">Plan</div>
                <div class="small-font">{total_plan_formatted}</div>
            </div>
            <div class="metric-box">
                <div class="big-font">Fakt</div>
                <div class="small-font">{total_fact_formatted}</div>
            </div>
            <div class="metric-box">
                <div class="big-font">Yerinə Yetirmə %</div>
                <div class="small-font">{total_percentage_formatted}</div>
            </div>
        </div>
    """


# HTML kodunu Streamlit ilə göstərin
    st.markdown(html_code, unsafe_allow_html=True)
    # **Məhsullar üzrə Plan və Fakt Həcm Cədvəlinin Yaradılması**

    # Plan datasında 'Əsas yük' sütununu 'Məhsul' olaraq adlandırırıq
    plan_df_filtered = plan_df_filtered.rename(columns={'Əsas yük': 'Məhsul'})

    # Fakt datasında 'əsas_yüklər' sütununu 'Məhsul' olaraq adlandırırıq
    fakt_df_filtered = fakt_df_filtered.rename(columns={'əsas_yüklər': 'Məhsul'})

    # Məhsul üzrə plan həcmlərini hesablayırıq
    plan_by_product = plan_df_filtered.groupby('Məhsul')['plan hecm'].sum().reset_index()

    # Məhsul üzrə fakt həcmlərini hesablayırıq
    fakt_by_product = fakt_df_filtered.groupby('Məhsul')['Həcm_fakt'].sum().reset_index()

    # Plan və fakt datasını məhsul üzrə birləşdiririk
    merged_product = pd.merge(plan_by_product, fakt_by_product, on='Məhsul', how='outer')

    # NaN dəyərləri 0 ilə əvəz edirik
    merged_product['plan hecm'] = merged_product['plan hecm'].fillna(0)
    merged_product['Həcm_fakt'] = merged_product['Həcm_fakt'].fillna(0)

    # **Sıralama tətbiq edirik (plan həcmi və fakt həcmi üzrə çoxdan aza doğru)**
    merged_product['total'] = merged_product['plan hecm'] + merged_product['Həcm_fakt']
    merged_product = merged_product.sort_values(by=['total'], ascending=False).reset_index(drop=True)
    merged_product = merged_product.drop('total', axis=1)

    # **'Digər yüklər' sətrini ən aşağı yerləşdiririk**
    if 'Digər yüklər' in merged_product['Məhsul'].values:
        # 'Digər yüklər' sətrini seçirik
        other_row = merged_product[merged_product['Məhsul'] == 'Digər yüklər']
        # Qalan sətrləri seçirik
        rest_rows = merged_product[merged_product['Məhsul'] != 'Digər yüklər']
        # Qalan sətrləri birləşdiririk və 'Digər yüklər' sətrini ən sona əlavə edirik
        merged_product = pd.concat([rest_rows, other_row], ignore_index=True)

    # Yerinə yetirmə faizini hesablayırıq
    merged_product['Faiz'] = merged_product.apply(
        lambda row: (row['Həcm_fakt'] / row['plan hecm']) * 100 if row['plan hecm'] != 0 else 0, axis=1)

    # Rəqəmləri formatlayırıq
    merged_product['plan hecm_formatted'] = merged_product['plan hecm'].apply(lambda x: "{:,.0f}".format(x))
    merged_product['Həcm_fakt_formatted'] = merged_product['Həcm_fakt'].apply(lambda x: "{:,.0f}".format(x))
    merged_product['Faiz_formatted'] = merged_product['Faiz'].apply(lambda x: "{:,.0f}%".format(x))

    # **Məhsullar üzrə cədvəli göstəririk**
    st.markdown("<h3 style='text-align: center; color: #004AAD;'></h3>", unsafe_allow_html=True)

    # Cədvəl üçün sütunları və dəyərləri hazırlayırıq
    header_values_product = ['Yükün adı', 'Plan', 'Fakt', 'Yerinə yetirmə %']
    cell_values_product = [merged_product['Məhsul'],
                           merged_product['plan hecm_formatted'],
                           merged_product['Həcm_fakt_formatted'],
                           merged_product['Faiz_formatted']]

    fig_table_product = go.Figure(data=[go.Table(
        columnwidth=[200, 100, 100, 106],
        header=dict(
            values=header_values_product,
            fill_color='#011836',
            font=dict(color='white', size=14, family='Arial'),
            align='center',
            line_color='white'
        ),
        cells=dict(
            values=cell_values_product,
            fill_color=[['#F0F2F6'] * len(merged_product)],
            align='center',
            font=dict(color='black', size=12, family='Arial'),
            line_color='#c0bfc9'
        )
    )])

    # Cədvəlin ölçüsünü artırırıq
    fig_table_product.update_layout(
        width=2000,
        height=600,
        margin=dict(l=10, r=10, t=10, b=0)
    )

    # Plotly cədvəlini göstəririk
    st.plotly_chart(fig_table_product)

    # Ekspeditorlar üzrə məlumatları toplamaq

    # Şərtli olaraq fraxt sütunlarını daxil etmək üçün "Tranzit" rejiminin seçilib-seçilmədiyini yoxlayırıq
    is_tranzit_selected = selected_rejim == 'Tranzit'

    # Fakt datasında 'Eksp' sütununu 'Ekspeditor' olaraq adlandırırıq
    fakt_df_filtered = fakt_df_filtered.rename(columns={'Eksp': 'Ekspeditor'})

    # Plan datasında 'Ekspeditor' sütunu varsa, yoxlayırıq
    if 'Ekspeditor' not in plan_df_filtered.columns:
        plan_df_filtered['Ekspeditor'] = 'Naməlum'

    # Ekspeditor üzrə plan həcmlərini hesablayırıq
    plan_by_ekspeditor = plan_df_filtered.groupby('Ekspeditor')['plan hecm'].sum().reset_index()

    # Ekspeditor üzrə fakt həcmlərini hesablayırıq
    fakt_by_ekspeditor = fakt_df_filtered.groupby('Ekspeditor')['Həcm_fakt'].sum().reset_index()

    # Yalnız "Tranzit" seçildiyi halda fraxt datalarını da hesablayırıq
    if is_tranzit_selected:
        fraxt_by_ekspeditor = plan_df_fraxt.groupby('Ekspeditor')['Həcm_fraxt'].sum().reset_index()
        merged_ekspeditor = pd.merge(plan_by_ekspeditor, fakt_by_ekspeditor, on='Ekspeditor', how='outer')
        merged_ekspeditor = pd.merge(merged_ekspeditor, fraxt_by_ekspeditor, on='Ekspeditor', how='outer')
        merged_ekspeditor['Həcm_fraxt'] = merged_ekspeditor['Həcm_fraxt'].fillna(0)
    else:
        # Əgər "Tranzit" seçilməyibsə, fraxt datalarını daxil etməyə ehtiyac yoxdur
        merged_ekspeditor = pd.merge(plan_by_ekspeditor, fakt_by_ekspeditor, on='Ekspeditor', how='outer')

    # NaN dəyərləri 0 ilə əvəz edirik
    merged_ekspeditor['plan hecm'] = merged_ekspeditor['plan hecm'].fillna(0)
    merged_ekspeditor['Həcm_fakt'] = merged_ekspeditor['Həcm_fakt'].fillna(0)

    # Sıralama tətbiq edirik (plan həcmi və fakt həcmi üzrə çoxdan aza doğru)
    merged_ekspeditor['total'] = merged_ekspeditor['plan hecm'] + merged_ekspeditor['Həcm_fakt']
    merged_ekspeditor = merged_ekspeditor.sort_values(by=['total'], ascending=False).reset_index(drop=True)
    merged_ekspeditor = merged_ekspeditor.drop('total', axis=1)

    # Yerinə yetirmə faizini hesablayırıq
    merged_ekspeditor['Faiz'] = merged_ekspeditor.apply(
        lambda row: (row['Həcm_fakt'] / row['plan hecm']) * 100 if row['plan hecm'] != 0 else 0, axis=1
    )

    # Yalnız "Tranzit" rejimi üçün fraxt faizini hesablayırıq
    if is_tranzit_selected:
        merged_ekspeditor['Fraxt Faizi'] = merged_ekspeditor.apply(
            lambda row: (row['Həcm_fakt'] / row['Həcm_fraxt']) * 100 if row['Həcm_fraxt'] != 0 else 0, axis=1
        )

    # Rəqəmləri formatlayırıq
    merged_ekspeditor['plan hecm_formatted'] = merged_ekspeditor['plan hecm'].apply(lambda x: "{:,.0f}".format(x))
    merged_ekspeditor['Həcm_fakt_formatted'] = merged_ekspeditor['Həcm_fakt'].apply(lambda x: "{:,.0f}".format(x))
    merged_ekspeditor['Faiz_formatted'] = merged_ekspeditor['Faiz'].apply(lambda x: "{:,.0f}%".format(x))

    if is_tranzit_selected:
        merged_ekspeditor['fraxt hecm_formatted'] = merged_ekspeditor['Həcm_fraxt'].apply(lambda x: "{:,.0f}".format(x))
        merged_ekspeditor['Fraxt_formatted'] = merged_ekspeditor['Fraxt Faizi'].apply(lambda x: "{:,.0f}%".format(x))

    # **Cədvəl Yaratmaq**
    if is_tranzit_selected:
        header_values_ekspeditor = ['Ekspeditor', 'Plan(KM)', 'Fakt(KM)', 'Yerinə yetirmə %', 'Plan (Fraxt)', 'Fakt (Fraxt)','Yerinə yetirmə %']
        cell_values_ekspeditor = [
            merged_ekspeditor['Ekspeditor'],
            merged_ekspeditor['plan hecm_formatted'],
            merged_ekspeditor['Həcm_fakt_formatted'],
            merged_ekspeditor['Faiz_formatted'],
            merged_ekspeditor['fraxt hecm_formatted'],
            merged_ekspeditor['Həcm_fakt_formatted'],
            merged_ekspeditor['Fraxt_formatted']
        ]
    else:
        header_values_ekspeditor = ['Ekspeditor adı', 'Plan', 'Fakt', 'Yerinə yetirmə %']
        cell_values_ekspeditor = [
            merged_ekspeditor['Ekspeditor'],
            merged_ekspeditor['plan hecm_formatted'],
            merged_ekspeditor['Həcm_fakt_formatted'],
            merged_ekspeditor['Faiz_formatted']
        ]

    # Cədvəli yaratmaq və göstərmək
    fig_table_ekspeditor = go.Figure(data=[go.Table(
        columnwidth=[200, 100, 100, 80],
        header=dict(
            values=header_values_ekspeditor,
            fill_color='#011836',
            font=dict(color='white', size=14, family='Arial'),
            align='center',
            line_color="white"
        ),
        cells=dict(
            values=cell_values_ekspeditor,
            fill_color=[['#F0F2F6'] * len(merged_ekspeditor)],
            align='center',
            font=dict(color='black', size=12, family='Arial')
        )
    )])

    # Cədvəlin ölçüsünü artırırıq
    fig_table_ekspeditor.update_layout(
        width=2000 if is_tranzit_selected else 1500,
        height=600
    )

    # Plotly cədvəlini göstəririk
    st.plotly_chart(fig_table_ekspeditor)


    # **Vaqon/Konteyner üzrə Plan və Fakt Həcm Cədvəlinin Yaradılması**

    # Plan datasında 'Vaqon/konteyner' sütununu 'vaqon_növü' olaraq adlandırırıq
    plan_df_filtered = plan_df_filtered.rename(columns={'Vaqon/konteyner': 'vaqon_növü'})

    # Fakt datasında 'vaqon_növü' sütunu artıq mövcuddur



    # Vaqon_növü üzrə plan həcmlərini hesablayırıq
    plan_by_vaqon = plan_df_filtered.groupby('vaqon_növü')['plan hecm'].sum().reset_index()

    # Vaqon_növü üzrə fakt həcmlərini hesablayırıq
    fakt_by_vaqon = fakt_df_filtered.groupby('vaqon_növü')['Həcm_fakt'].sum().reset_index()

    # Plan və fakt datasını vaqon_növü üzrə birləşdiririk
    merged_vaqon = pd.merge(plan_by_vaqon, fakt_by_vaqon, on='vaqon_növü', how='outer')

    # NaN dəyərləri 0 ilə əvəz edirik
    merged_vaqon['plan hecm'] = merged_vaqon['plan hecm'].fillna(0)
    merged_vaqon['Həcm_fakt'] = merged_vaqon['Həcm_fakt'].fillna(0)

    # **Sıralama tətbiq edirik (plan həcmi və fakt həcmi üzrə çoxdan aza doğru)**
    merged_vaqon['total'] = merged_vaqon['plan hecm'] + merged_vaqon['Həcm_fakt']
    merged_vaqon = merged_vaqon.sort_values(by=['total'], ascending=False).reset_index(drop=True)
    merged_vaqon = merged_vaqon.drop('total', axis=1)

    # Yerinə yetirmə faizini hesablayırıq
    merged_vaqon['Faiz'] = merged_vaqon.apply(
        lambda row: (row['Həcm_fakt'] / row['plan hecm']) * 100 if row['plan hecm'] != 0 else 0, axis=1)

    # Rəqəmləri formatlayırıq
    merged_vaqon['plan hecm_formatted'] = merged_vaqon['plan hecm'].apply(lambda x: "{:,.0f}".format(x))
    merged_vaqon['Həcm_fakt_formatted'] = merged_vaqon['Həcm_fakt'].apply(lambda x: "{:,.0f}".format(x))
    merged_vaqon['Faiz_formatted'] = merged_vaqon['Faiz'].apply(lambda x: "{:,.0f}%".format(x))

    # **Vaqon/Konteyner üzrə cədvəli göstəririk**
    st.markdown("<h3 style='text-align: center; color: #004AAD;'></h3>", unsafe_allow_html=True)

    # Cədvəl üçün sütunları və dəyərləri hazırlayırıq
    header_values_vaqon = ['Vaqon tipi', 'Plan', 'Fakt', 'Yerinə yetirmə %']
    cell_values_vaqon = [merged_vaqon['vaqon_növü'],
                         merged_vaqon['plan hecm_formatted'],
                         merged_vaqon['Həcm_fakt_formatted'],
                         merged_vaqon['Faiz_formatted']]

    fig_table_vaqon = go.Figure(data=[go.Table(
        columnwidth=[200, 100, 100, 80],
        header=dict(
            values=header_values_vaqon,
            fill_color='#011836',
            font=dict(color='white', size=14, family='Arial'),
            align='center',
            line_color = "white"
        ),
        cells=dict(
            values=cell_values_vaqon,
            fill_color=[['#F0F2F6'] * len(merged_vaqon)],
            align='center',
            font=dict(color='black', size=12, family='Arial')
        )
    )])

    # Cədvəlin ölçüsünü artırırıq
    fig_table_vaqon.update_layout(
        width=2000,
        height=600,
        margin=dict(l=10, r=10, t=15, b=0)
    )

    # Plotly cədvəlini göstəririk
    st.plotly_chart(fig_table_vaqon)
    
elif page =="Current Year":
    # Şəkili göstərmək
    image = Image.open('Picture1.png')
    col1, col2 = st.columns([0.1, 0.9])
    with col1:
        st.image(image, width=100)
    
    # Başlıq üçün dizayn
    dashboard_title = """
        <style>
        .title-test{
        font-weight:bold;
        padding:2px;
        border-radius:18px;
        color: #16105c;
        }
        </style>
        <center><h3 class="title-test">Rejimlər üzrə illik göstəricilər</h3></center>
    """
    with col2:
        st.markdown(dashboard_title, unsafe_allow_html=True)

    col3, col4 = st.columns(2)

    with col3:
        # Tarix filteri: istifadəçi spesifik tarix seçə biləcək
        available_dates = fakt_df['Tarix'].dt.date.unique()
        available_dates = sorted(available_dates)

        selected_date = st.selectbox('', options=available_dates)
        selected_date = pd.to_datetime(selected_date)

        # Seçilmiş tarixə uyğun ay və il
        selected_month = selected_date.month
        selected_year = selected_date.year
        selected_day = selected_date.day

        # Ayın gün sayını hesablayırıq
        days_in_month = calendar.monthrange(selected_year, selected_month)[1]

    with col4:
        # Rejimlər üçün unikal dəyərləri əldə edirik
        rejimler_plan = plan_df['Rejim'].unique()
        rejimler_fakt = fakt_df['Rejim'].unique()
        rejimler_fr = plan_fr['Rejim'].unique()
        rejimler = list(set(rejimler_plan) | set(rejimler_fakt) | set(rejimler_fr))
        rejimler = sorted(rejimler)

        # Rejimləri seçmək üçün selectbox (single-select)
        selected_rejim = st.selectbox('', rejimler)

    # **Plan Datasını Filtr Etmək**
    plan_df_filtered = plan_df[
        (plan_df['Tarix'].dt.year == selected_year) &
        (plan_df['Tarix'].dt.month <= selected_month) &
        (plan_df['Rejim'] == selected_rejim)
    ]
    plan_df_fraxt = plan_fr[
        (plan_fr['Tarix'].dt.month == selected_date.month) &
        (plan_fr['Tarix'].dt.year == selected_date.year) &
        (plan_fr['Rejim'] == selected_rejim)
    ]

    # Yanvar ayından seçilmiş aya qədər olan ayların plan həcmlərini toplamaq
    if not plan_df_filtered.empty:
        # Seçilmiş aydan əvvəlki bütün ayların plan həcmi
        plan_before_selected_month = plan_df_filtered[plan_df_filtered['Tarix'].dt.month < selected_month]
        total_plan_before_selected_month = plan_before_selected_month['plan hecm'].sum()

        # Seçilmiş ay üçün plan həcmini tənzimləyirik
        plan_selected_month = plan_df_filtered[plan_df_filtered['Tarix'].dt.month == selected_month]
        total_plan_selected_month = plan_selected_month['plan hecm'].sum()
        adjusted_plan_selected_month = (total_plan_selected_month / days_in_month) * selected_day

        # Ümumi plan həcmi
        total_plan = total_plan_before_selected_month + adjusted_plan_selected_month
    else:
        total_plan = 0

    if not plan_df_fraxt.empty:
        # Seçilmiş aydan əvvəlki bütün ayların plan həcmi
        plan_before_selected_month_fraxt = plan_df_fraxt[plan_df_fraxt['Tarix'].dt.month < selected_month]
        total_plan_before_selected_month_fraxt = plan_before_selected_month_fraxt['Həcm_fraxt'].sum()

        # Seçilmiş ay üçün plan həcmini tənzimləyirik
        plan_selected_month_fraxt = plan_df_fraxt[plan_df_fraxt['Tarix'].dt.month == selected_month]
        total_plan_selected_month_fraxt = plan_selected_month_fraxt['Həcm_fraxt'].sum()
        adjusted_plan_selected_month_fraxt = (total_plan_selected_month_fraxt / days_in_month) * selected_day

    # Ümumi plan həcmi
        total_plan_fraxt = total_plan_before_selected_month_fraxt + adjusted_plan_selected_month_fraxt
    else:
        total_plan_fraxt = 0
        
    # **Fakt Datasını Filtr Etmək**
    fakt_df_filtered = fakt_df[
        (fakt_df['Tarix'].dt.year == selected_year) &
        (fakt_df['Tarix'].dt.month <= selected_month) &
        (fakt_df['Rejim'] == selected_rejim)
    ]

    # Seçilmiş aya qədər olan bütün fakt həcmlərini toplamaq
    if not fakt_df_filtered.empty:
        # Seçilmiş aydan əvvəlki bütün ayların fakt həcmi
        fakt_before_selected_month = fakt_df_filtered[fakt_df_filtered['Tarix'].dt.month < selected_month]
        total_fact_before_selected_month = fakt_before_selected_month['Həcm_fakt'].sum()

        # Seçilmiş ay üçün fakt həcmi (seçilmiş günə qədər)
        fakt_selected_month = fakt_df_filtered[
            (fakt_df_filtered['Tarix'].dt.month == selected_month) &
            (fakt_df_filtered['Tarix'].dt.day <= selected_day)
        ]
        total_fact_selected_month = fakt_selected_month['Həcm_fakt'].sum()

        # Ümumi fakt həcmi
        total_fact = total_fact_before_selected_month + total_fact_selected_month
    else:
        total_fact = 0

    # **Yerinə Yetirmə Faizinin Hesablanması**
    if total_plan == 0:
        total_percentage = 0
    else:
        total_percentage = (total_fact / total_plan) * 100
     
    if total_plan_fraxt == 0:
        total_percentage_fraxt = 0
    else:
        total_percentage_fraxt = (total_fact / total_plan_fraxt) * 100
    
    # Rəqəmləri formatlayırıq
    total_plan_formatted = "{:,.0f}".format(total_plan)
    total_fact_formatted = "{:,.0f}".format(total_fact)
    total_fraxt_formated = "{:,.0f}".format(total_plan_fraxt)
    total_percentage_formatted = "{:,.0f}%".format(total_percentage)
    total_percentage_formatted_fraxt = "{:,.0f}%".format(total_percentage_fraxt)

    # **Üçlü Kartlar: Plan, Fakt və Yerinə Yetirmə Faizi**
    st.markdown("---")

    # Kartları yaratmaq üçün üç sütun
    col1, col2, col3 = st.columns(3)

    # Stilizə olunmuş kartlar üçün CSS
    st.markdown("""
        <style>
            .card {
                background-color: #f0f0f5;
                padding: 20px;
                border-radius: 10px;
                text-align: center;
                box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.1);
                margin-bottom: 20px;
            }
            .card-title {
                font-size: 20px;
                font-weight: bold;
                color: #05073b;
                margin-bottom: 10px;
            }
            .card-value {
                font-size: 28px;
                font-weight: bold;
                color: #05073b;
            }
        </style>
    """, unsafe_allow_html=True)

    with col1:
        st.markdown(f"""
            <div class="card">
                <div class="card-title">Plan</div>
                <div class="card-value">{total_plan_formatted}</div>
            </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
            <div class="card">
                <div class="card-title">Fakt</div>
                <div class="card-value">{total_fact_formatted}</div>
            </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
            <div class="card">
                <div class="card-title">Yerinə Yetirmə %</div>
                <div class="card-value">{total_percentage_formatted}</div>
            </div>
        """, unsafe_allow_html=True)

    # **Məhsullar üzrə plan və fakt həcmlərinin cədvəli**
    # Plan datasında 'Əsas yük' sütununu 'Məhsul' olaraq adlandırırıq
    plan_df_filtered = plan_df_filtered.rename(columns={'Əsas yük': 'Məhsul'})

    # Fakt datasında 'əsas_yüklər' sütununu 'Məhsul' olaraq adlandırırıq
    fakt_df_filtered = fakt_df_filtered.rename(columns={'əsas_yüklər': 'Məhsul'})


    # Məhsul üzrə plan həcmlərini hesablayırıq
    plan_by_product = plan_df_filtered.groupby('Məhsul')['plan hecm'].sum().reset_index()

    # Məhsul üzrə fakt həcmlərini hesablayırıq
    fakt_by_product = fakt_df_filtered.groupby('Məhsul')['Həcm_fakt'].sum().reset_index()

    # Plan və fakt datasını məhsul üzrə birləşdiririk
    merged_product = pd.merge(plan_by_product, fakt_by_product, on='Məhsul', how='outer')

    # NaN dəyərləri 0 ilə əvəz edirik
    merged_product['plan hecm'] = merged_product['plan hecm'].fillna(0)
    merged_product['Həcm_fakt'] = merged_product['Həcm_fakt'].fillna(0)

    # **Sıralama tətbiq edirik (plan həcmi və fakt həcmi üzrə çoxdan aza doğru)**
    merged_product['total'] = merged_product['plan hecm'] + merged_product['Həcm_fakt']
    merged_product = merged_product.sort_values(by=['total'], ascending=False).reset_index(drop=True)
    merged_product = merged_product.drop('total', axis=1)

    # **'Digər yüklər' sətrini ən aşağı yerləşdiririk**
    if 'Digər yüklər' in merged_product['Məhsul'].values:
        # 'Digər yüklər' sətrini seçirik
        other_row = merged_product[merged_product['Məhsul'] == 'Digər yüklər']
        # Qalan sətrləri seçirik
        rest_rows = merged_product[merged_product['Məhsul'] != 'Digər yüklər']
        # Qalan sətrləri birləşdiririk və 'Digər yüklər' sətrini ən sona əlavə edirik
        merged_product = pd.concat([rest_rows, other_row], ignore_index=True)

    # Yerinə yetirmə faizini hesablayırıq
    merged_product['Faiz'] = merged_product.apply(
        lambda row: (row['Həcm_fakt'] / row['plan hecm']) * 100 if row['plan hecm'] != 0 else 0, axis=1
    )

    # Rəqəmləri formatlayırıq
    merged_product['plan hecm_formatted'] = merged_product['plan hecm'].apply(lambda x: "{:,.0f}".format(x))
    merged_product['Həcm_fakt_formatted'] = merged_product['Həcm_fakt'].apply(lambda x: "{:,.0f}".format(x))
    merged_product['Faiz_formatted'] = merged_product['Faiz'].apply(lambda x: "{:,.0f}%".format(x))

    # **Məhsullar üzrə cədvəli göstəririk**
    st.markdown("<h3 style='text-align: center; color: #004AAD;'></h3>", unsafe_allow_html=True)

    # Cədvəl üçün sütunları və dəyərləri hazırlayırıq
    header_values_product = ['Yükün adı', 'Plan', 'Fakt', 'Yerinə yetirmə %']
    cell_values_product = [merged_product['Məhsul'],
                        merged_product['plan hecm_formatted'],
                        merged_product['Həcm_fakt_formatted'],
                        merged_product['Faiz_formatted']]

    fig_table_product = go.Figure(data=[go.Table(
        columnwidth=[200, 100, 100, 80],
        header=dict(
            values=header_values_product,
            fill_color='#011836',
            font=dict(color='white', size=14, family='Arial'),
            align='center',
            line_color ="white"
        ),
        cells=dict(
            values=cell_values_product,
            fill_color=[['#F0F2F6'] * len(merged_product)],
            align='center',
            font=dict(color='black', size=12, family='Arial'),
            line_color="#c0bfc9"
        )
    )])

    # Cədvəlin ölçüsünü artırırıq
    fig_table_product.update_layout(
        width=2000,
        height=600,
        margin=dict(l=10, r=10, t=10, b=0)
    )

    # Plotly cədvəlini göstəririk
    st.plotly_chart(fig_table_product)

    is_tranzit_selected = selected_rejim == 'Tranzit'
    # Fakt datasında 'Eksp' sütununu 'Ekspeditor' olaraq adlandırırıq
    fakt_df_filtered = fakt_df_filtered.rename(columns={'Eksp': 'Ekspeditor'})
    # **Ekspeditorlar üzrə plan və fakt həcmlərinin cədvəli**

    # Plan datasında 'Ekspeditor' sütunu varsa, yoxlayırıq
    if 'Ekspeditor' not in plan_df_filtered.columns:
        plan_df_filtered['Ekspeditor'] = 'Naməlum'
    # Plan datasında 'Ekspeditor' sütununu əldə edirik
    plan_by_ekspeditor = plan_df_filtered.groupby('Ekspeditor')['plan hecm'].sum().reset_index()
    
    # Fakt datasında 'Ekspeditor' sütununu əldə edirik
    fakt_by_ekspeditor = fakt_df_filtered.groupby('Ekspeditor')['Həcm_fakt'].sum().reset_index()

    # Plan və fakt datasını ekspeditorlar üzrə birləşdiririk
    if is_tranzit_selected:
        plan_fraxt_ekspeditor = plan_df_fraxt.groupby('Ekspeditor')['Həcm_fraxt'].sum().reset_index()
        merged_ekspeditor = pd.merge(plan_by_ekspeditor, fakt_by_ekspeditor, on='Ekspeditor', how='outer')
        merged_ekspeditor = pd.merge(merged_ekspeditor, plan_fraxt_ekspeditor, on='Ekspeditor', how='outer')
        merged_ekspeditor['Həcm_fraxt'] = merged_ekspeditor['Həcm_fraxt'].fillna(0)
    else:
     # Əgər "Tranzit" seçilməyibsə, fraxt datalarını daxil etməyə ehtiyac yoxdur
        merged_ekspeditor = pd.merge(plan_by_ekspeditor, fakt_by_ekspeditor, on='Ekspeditor', how='outer')

    # NaN dəyərləri 0 ilə əvəz edirik
    merged_ekspeditor['plan hecm'] = merged_ekspeditor['plan hecm'].fillna(0)
    merged_ekspeditor['Həcm_fakt'] = merged_ekspeditor['Həcm_fakt'].fillna(0)
    
    # **Yerinə Yetirmə Faizini Hesablayırıq**
    merged_ekspeditor['Faiz'] = merged_ekspeditor.apply(
        lambda row: (row['Həcm_fakt'] / row['plan hecm']) * 100 if row['plan hecm'] != 0 else 0, axis=1
    )

    # Yalnız "Tranzit" rejimi üçün fraxt faizini hesablayırıq
    if is_tranzit_selected:
        merged_ekspeditor['Fraxt Faizi'] = merged_ekspeditor.apply(
            lambda row: (row['Həcm_fakt'] / row['Həcm_fraxt']) * 100 if row['Həcm_fraxt'] != 0 else 0, axis=1
        )

    # Rəqəmləri formatlayırıq
    merged_ekspeditor['plan hecm_formatted'] = merged_ekspeditor['plan hecm'].apply(lambda x: "{:,.0f}".format(x))
    merged_ekspeditor['Həcm_fakt_formatted'] = merged_ekspeditor['Həcm_fakt'].apply(lambda x: "{:,.0f}".format(x))
    merged_ekspeditor['Faiz_formatted'] = merged_ekspeditor['Faiz'].apply(lambda x: "{:,.0f}%".format(x))

    if is_tranzit_selected:
        merged_ekspeditor['fraxt hecm_formatted'] = merged_ekspeditor['Həcm_fraxt'].apply(lambda x: "{:,.0f}".format(x))
        merged_ekspeditor['Fraxt_formatted'] = merged_ekspeditor['Fraxt Faizi'].apply(lambda x: "{:,.0f}%".format(x))

    # **Ekspeditorlar üzrə cədvəli və barplotu göstəririk**
    st.markdown("<h3 style='text-align: center; color: #004AAD;'></h3>", unsafe_allow_html=True)

    # Ekspeditorlar üzrə cədvəl
    if is_tranzit_selected:
        header_values_expeditor = ['Ekspeditor', 'Plan', 'Fakt', 'Yerinə yetirmə %',"Plan (Fraxt)",'Fakt (Fraxt)',"Yerinə yetirmə %"]
        cell_values_expeditor = [merged_ekspeditor['Ekspeditor'],
                                merged_ekspeditor['plan hecm_formatted'],
                                merged_ekspeditor['Həcm_fakt_formatted'],
                                merged_ekspeditor['Faiz_formatted'],
                                merged_ekspeditor['fraxt hecm_formatted'],
                                merged_ekspeditor['Fraxt_formatted'],
                                merged_ekspeditor['Həcm_fakt_formatted']
                                ]
    else:
        header_values_expeditor = ['Ekspeditor adı', 'Plan', 'Fakt', 'Yerinə yetirmə %']
        cell_values_expeditor = [
            merged_ekspeditor['Ekspeditor'],
            merged_ekspeditor['plan hecm_formatted'],
            merged_ekspeditor['Həcm_fakt_formatted'],
            merged_ekspeditor['Faiz_formatted']
        ]

    fig_table_expeditor = go.Figure(data=[go.Table(
        columnwidth=[200, 100, 100, 80],
        header=dict(
            values=header_values_expeditor,
            fill_color='#011836',
            font=dict(color='white', size=14, family='Arial'),
            align='center',
            line_color = "white"
        ),
        cells=dict(
            values=cell_values_expeditor,
            fill_color=[['#F0F2F6'] * len(merged_ekspeditor)],
            align='center',
            font=dict(color='black', size=12, family='Arial'),
            line_color="#c0bfc9"
        )
    )])

    # Cədvəlin ölçüsünü artırırıq
    fig_table_expeditor.update_layout(
        width=2000,
        height=600
    )

    # Plotly cədvəlini göstəririk
    st.plotly_chart(fig_table_expeditor)

    # Vaqon/Konteyner üzrə Plan və Fakt Hesabatı
    st.markdown("<h3 style='text-align: center; color: #004AAD;'></h3>", unsafe_allow_html=True)

    # Plan datasında vaqon/konteyner məlumatlarını hesablayırıq
    plan_by_vagon = plan_df_filtered.groupby('Vaqon/konteyner')['plan hecm'].sum().reset_index()

    # Fakt datasında vaqon/konteyner məlumatlarını hesablayırıq
    fakt_by_vagon = fakt_df_filtered.groupby('vaqon_növü')['Həcm_fakt'].sum().reset_index()

    # Plan və fakt məlumatlarını vaqon/konteyner üzrə birləşdiririk
    merged_vagon = pd.merge(plan_by_vagon, fakt_by_vagon, left_on='Vaqon/konteyner', right_on='vaqon_növü', how='outer')

    # NaN dəyərləri 0 ilə əvəz edirik
    merged_vagon['plan hecm'] = merged_vagon['plan hecm'].fillna(0)
    merged_vagon['Həcm_fakt'] = merged_vagon['Həcm_fakt'].fillna(0)

    # **Yerinə Yetirmə Faizini Hesablayırıq**
    merged_vagon['Faiz'] = merged_vagon.apply(
        lambda row: (row['Həcm_fakt'] / row['plan hecm']) * 100 if row['plan hecm'] != 0 else 0, axis=1
    )

    # Rəqəmləri formatlayırıq
    merged_vagon['plan hecm_formatted'] = merged_vagon['plan hecm'].apply(lambda x: "{:,.0f}".format(x))
    merged_vagon['Həcm_fakt_formatted'] = merged_vagon['Həcm_fakt'].apply(lambda x: "{:,.0f}".format(x))
    merged_vagon['Faiz_formatted'] = merged_vagon['Faiz'].apply(lambda x: "{:,.0f}%".format(x))

    # **Vaqon/Konteyner üzrə Cədvəli Sıralayıb Göstəririk**
    # Əvvəlcə 'total_hecm' sütunu əlavə edirik
    merged_vagon['total_hecm'] = merged_vagon['plan hecm'] + merged_vagon['Həcm_fakt']

    # 'total_hecm' sütununa görə azalan sırada sıralayırıq
    merged_vagon = merged_vagon.sort_values(by='total_hecm', ascending=False).reset_index(drop=True)

    # İndi cədvəl və barplot üçün lazım olan sütunlardan 'total_hecm' silirik
    merged_vagon = merged_vagon.drop('total_hecm', axis=1)

    header_values_vagon = ['Vaqon növü', 'Plan', 'Fakt', 'Yerinə yetirmə %']
    cell_values_vagon = [merged_vagon['Vaqon/konteyner'],
                        merged_vagon['plan hecm_formatted'],
                        merged_vagon['Həcm_fakt_formatted'],
                        merged_vagon['Faiz_formatted']]

    # Cədvəl üçün barplot və cədvəli yan-yana göstərmək üçün sütunlar yaradırıq
    col_vagon1, col_vagon2 = st.columns([2, 1])  # Cədvəl geniş, barplot dar

    with col_vagon1:
        st.markdown("<h3 style='text-align: center; color: #004AAD;'></h3>", unsafe_allow_html=True)
        
        fig_table_vagon = go.Figure(data=[go.Table(
            columnwidth=[200, 100, 100, 80],
            header=dict(
                values=header_values_vagon,
                fill_color='#011836',
                font=dict(color='white', size=14, family='Arial'),
                align='center',
                line_color = "white"
            ),
            cells=dict(
                values=cell_values_vagon,
                fill_color=[['#F0F2F6'] * len(merged_vagon)],
                align='center',
                font=dict(color='black', size=13, family='Arial'),
                line_color="#c0bfc9"
            )
        )])
        
        # Cədvəlin ölçüsünü artırırıq
        fig_table_vagon.update_layout(
            width=1200,
            height=600,
            margin=dict(l=0, r=0, t=0, b=0)
        )
        
        # Plotly cədvəlini göstəririk
        st.plotly_chart(fig_table_vagon)
  
