import streamlit as st
import pandas as pd
import math

# 设置页面配置
st.set_page_config(page_title="患者检验查询助手", page_icon="🏥", layout="wide")

# --- 1. 初始化 Session State (用于记录页码) ---
if 'current_page' not in st.session_state:
    st.session_state.current_page = 1

# --- 2. 数据加载 (支持 Excel/CSV 或 模拟数据) ---
@st.cache_data
def load_data():
    try:
        # 实际使用请确保目录下有该文件
        df = pd.read_excel("检验项目.xlsx")
    except:
        # 模拟 100 条数据用于分页演示
        data = []
        categories = ["呼吸系统", "消化系统", "心血管", "免疫系统", "内分泌"]
        for i in range(1, 101):
            data.append({
                "分类": categories[i % 5],
                "项目名称": f"检验项目 {i:03d}",
                "临床意义": f"这是项目 {i} 的科普介绍：用于评估您的生理指标是否在正常范围。",
                "采样要求": "空腹，静脉血。",
                "报告时限": "当天 17:00 前",
                "温馨提示": "采样前请保持情绪平稳，避免剧烈运动。"
            })
        df = pd.DataFrame(data)
    return df

df = load_data()

# --- 3. 顶部：搜索与筛选 ---
st.title("🏥 检验项目查询系统")
st.markdown("---")

col_search1, col_search2 = st.columns([2, 1])
with col_search1:
    search_query = st.text_input("输入项目名称或疾病关键词", placeholder="搜索项目...")
with col_search2:
    all_categories = ["全部"] + list(df["分类"].unique())
    selected_category = st.selectbox("按疾病分类筛选", all_categories)

# 执行过滤逻辑
filtered_df = df.copy()
if selected_category != "全部":
    filtered_df = filtered_df[filtered_df["分类"] == selected_category]
if search_query:
    filtered_df = filtered_df[
        filtered_df["项目名称"].str.contains(search_query, case=False) | 
        filtered_df["临床意义"].str.contains(search_query, case=False)
    ]

# 重置页码逻辑：如果搜索内容变化，通常需要回到第一页
# 这里简单处理：如果搜索过滤后的数据量小于当前页对应的索引，重置为1
items_per_page = 20
total_items = len(filtered_df)
total_pages = math.ceil(total_items / items_per_page) if total_items > 0 else 1

if st.session_state.current_page > total_pages:
    st.session_state.current_page = 1

# --- 4. 中间：内容展示区 ---
start_idx = (st.session_state.current_page - 1) * items_per_page
end_idx = start_idx + items_per_page
current_page_df = filtered_df.iloc[start_idx:end_idx]

st.caption(f"共找到 {total_items} 条记录，当前显示第 {st.session_state.current_page}/{total_pages} 页")

if filtered_df.empty:
    st.warning("未找到匹配项目。")
else:
    for index, row in current_page_df.iterrows():
        with st.expander(f"📌 {row['项目名称']}"):
            c1, c2 = st.columns([2, 1])
            with c1:
                st.markdown(f"**💡 临床意义**\n{row['临床意义']}")
                st.info(f"**📢 温馨提示**：{row['温馨提示']}")
            with c2:
                st.markdown(f"**🩸 采样要求**\n{row['采样要求']}")
                st.markdown(f"**⏱️ 报告时限**\n{row['报告时限']}")

# --- 5. 底部：分页控制区 ---
st.markdown("---")

# 创建 5 列布局，让分页控件居中且美观
# 比例调整为 [2, 1, 1.5, 1, 2]，给中间的文字多一点空间
col_page1, col_page2, col_page3, col_page4, col_page5 = st.columns([2, 1, 1.5, 1, 2])

with col_page2:
    # 上一页按钮
    if st.button("⬅️ 上一页") and st.session_state.current_page > 1:
        st.session_state.current_page -= 1
        st.rerun()

with col_page3:
    # 显示格式：第 1 / 5 页
    # 使用 markdown 让文字水平居中对齐
    st.markdown(
        f"<h4 style='text-align: center; margin: 0;'>第 {st.session_state.current_page} / {total_pages} 页</h4>", 
        unsafe_allow_html=True
    )

with col_page4:
    # 下一页按钮
    if st.button("下一页 ➡️") and st.session_state.current_page < total_pages:
        st.session_state.current_page += 1
        st.rerun()

with col_page5:
    # 快速跳转
    jump_page = st.number_input(
        "跳转至", 
        min_value=1, 
        max_value=total_pages, 
        value=st.session_state.current_page, 
        label_visibility="collapsed"
    )
    # 如果手动输入的页码与当前页码不同，则跳转
    if jump_page != st.session_state.current_page:
        st.session_state.current_page = jump_page
        st.rerun()