import streamlit as st
import pandas as pd
import plotly.express as px
from locales import TRANSLATIONS

# Varsayılan Uygulama Adı
APP_NAME = "DataZen"

# Sayfa Ayarları
st.set_page_config(page_title=APP_NAME, page_icon="📊", layout="wide")

# Dil Oturum Yönetimi (Session State)
if 'lang' not in st.session_state:
    st.session_state['lang'] = 'EN'

# Sidebar: Dil Seçimi
with st.sidebar:
    lang_options = {"EN": "English", "TR": "Türkçe", "JA": "日本語 (Japanese)", "KO": "한국어 (Korean)", "ZH": "中文 (Chinese)"}
    selected_lang_code = st.selectbox(
        "🌐 Language / Dil", 
        list(lang_options.keys()), 
        format_func=lambda x: lang_options[x],
        index=list(lang_options.keys()).index(st.session_state['lang'])
    )
    st.session_state['lang'] = selected_lang_code

# Seçili dile göre çevirileri al
t = TRANSLATIONS[st.session_state['lang']]

# Başlık ve Açıklama
st.title(t["title"].format(app_name=APP_NAME))
st.markdown(t["description"])

# Sidebar - Dosya Yükleme Alanı
with st.sidebar:
    st.header(t["sidebar_header"])
    uploaded_file = st.file_uploader(t["file_uploader"], type=['csv', 'xlsx'])
    
    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
            st.success(t["upload_success"])
        except Exception as e:
            st.error(t["upload_error"].format(e))
            df = None
    else:
        df = None
        st.info(t["upload_info"])

# Ana Ekran
if df is not None and uploaded_file is not None:
    # Veri değişikliklerini tutmak için Session State kullanımı
    if 'current_df' not in st.session_state or st.session_state.get('last_uploaded') != uploaded_file.name:
        st.session_state['current_df'] = df.copy()
        st.session_state['last_uploaded'] = uploaded_file.name
        
    current_df = st.session_state['current_df']

    tab1, tab2, tab3, tab4, tab5 = st.tabs(["🗂️ Preview", "🔍 EDA", "🧹 Cleaning", "📈 Visualization", "💾 Download"])
    
    with tab1:
        st.header(t["preview_header"])
        
        col1, col2, col3 = st.columns(3)
        col1.metric(t["row_count"], current_df.shape[0])
        col2.metric(t["col_count"], current_df.shape[1])
        col3.metric(t["nan_count"], current_df.isna().sum().sum())
        
        st.dataframe(current_df.head(10), use_container_width=True)
        st.divider()
        st.header(t["col_details"])
        info_df = pd.DataFrame({
            t["dtype"]: current_df.dtypes.astype(str),
            t["nan"]: current_df.isna().sum(),
            t["unique"]: current_df.nunique()
        })
        st.dataframe(info_df, use_container_width=True)

    with tab2:
        st.header(t["eda_header"])
        if st.checkbox(t["show_stats"]):
            st.dataframe(current_df.describe(), use_container_width=True)
            
    with tab3:
        st.header(t["cleaning_header"])
        
        clean_col1, clean_col2, clean_col3 = st.columns(3)
        
        with clean_col1:
            if st.button(t["clean_nan_btn"], use_container_width=True):
                st.session_state['current_df'] = current_df.dropna()
                st.success(t["success_clean"])
                st.rerun()
                
        with clean_col2:
            if st.button(t["fill_mean_btn"], use_container_width=True):
                # Sadece sayısal sütunlardaki boşlukları ortalama ile doldur
                numeric_cols = current_df.select_dtypes(include=['number']).columns
                current_df[numeric_cols] = current_df[numeric_cols].fillna(current_df[numeric_cols].mean())
                st.session_state['current_df'] = current_df
                st.success(t["success_clean"])
                st.rerun()
                
        with clean_col3:
            if st.button(t["drop_dup_btn"], use_container_width=True):
                st.session_state['current_df'] = current_df.drop_duplicates()
                st.success(t["success_clean"])
                st.rerun()

    with tab4:
        st.header(t["vis_header"])
        
        # Grafik eksenleri için sütun seçimi
        columns = current_df.columns.tolist()
        if len(columns) >= 2:
            plot_col1, plot_col2, plot_col3 = st.columns(3)
            with plot_col1:
                x_axis = st.selectbox(t["select_x"], options=columns, index=0)
            with plot_col2:
                y_axis = st.selectbox(t["select_y"], options=columns, index=1)
            with plot_col3:
                chart_type = st.selectbox(t["select_type"], options=["Bar", "Line", "Scatter"])
                
            if st.button(t["plot_btn"], use_container_width=True):
                if chart_type == "Bar":
                    fig = px.bar(current_df, x=x_axis, y=y_axis)
                elif chart_type == "Line":
                    fig = px.line(current_df, x=x_axis, y=y_axis)
                else:
                    fig = px.scatter(current_df, x=x_axis, y=y_axis)
                
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Görselleştirme için en az 2 sütuna ihtiyaç var.")

    with tab5:
        st.header(t["download_header"])
        csv = current_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label=t["download_btn"],
            data=csv,
            file_name=f"cleaned_{uploaded_file.name}",
            mime='text/csv',
        )

else:
    st.write(t["wait_msg"])
