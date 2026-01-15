import streamlit as st
from sys import exit
# 注意這裡：新版引用方式
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="自助餐點餐系統", layout="centered")

# 建立連線
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    df_menu = conn.read(worksheet="Menu")
except Exception as e:
    st.error("連線失敗，請檢查 Secrets 設定或試算表網址。")
    st.stop()

st.title("🥢 自助餐點餐系統")

# --- (1) 飯量選擇 ---
st.subheader("(1) 飯量")
rice_options = df_menu[df_menu['category'] == '(1) 飯量']['name'].tolist()
selected_rice = st.radio("選擇飯量需求：", rice_options, label_visibility="collapsed")

# --- (2) 主食選擇 ---
st.subheader("(2) 主食")
main_options = df_menu[df_menu['category'] == '(2) 主食']['name'].tolist()
selected_main = st.selectbox("請選擇一個主食：", ["未選擇"] + main_options)

# --- (3) 副餐選擇 (複選) ---
st.subheader("(3) 副餐")
side_options = df_menu[df_menu['category'] == '(3) 副餐']['name'].tolist()
selected_sides = st.multiselect("可複選配菜：", side_options)

st.divider()

# --- 訂單匯總 ---
if st.button("確認下單", type="primary", use_container_width=True):
    if selected_main == "未選擇":
        st.warning("請記得選擇主食喔！")
    else:
        order_details = f"飯量:{selected_rice} | 主食:{selected_main} | 配菜:{', '.join(selected_sides)}"
        
        new_order = pd.DataFrame([{
            "時間": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "點餐內容": order_details
        }])
        
        # 寫入資料
        try:
            # 使用新版的更新語法
            existing_data = conn.read(worksheet="Orders")
            updated_df = pd.concat([existing_data, new_order], ignore_index=True)
            conn.update(worksheet="Orders", data=updated_df)
            
            st.success("✅ 訂單已送出！")
            st.balloons()
        except Exception as e:
            st.error(f"寫入失敗，請確認你的 Google Sheets 權限已開放給所有人編輯。")
            st.info(f"預覽訂單內容：{order_details}")