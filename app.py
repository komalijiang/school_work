import streamlit as st
import requests
from bs4 import BeautifulSoup
import re
import jieba
from collections import Counter
import pyecharts.options as opts
from pyecharts.charts import WordCloud, Bar, Line, Pie, Radar, Scatter, HeatMap, TreeMap
from streamlit_echarts import st_pyecharts
import numpy as np

# --------------------------
# 1. 工具函数：URL内容抓取、文本清洗、分词统计（逻辑完全不变）
# --------------------------
def get_url_content(url):
    """抓取URL的文本内容"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.encoding = response.apparent_encoding or 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')
        # 提取body文本（优先正文容器，兜底body）
        content_tag = soup.find('div', class_='content') or soup.find('article') or soup.body
        if not content_tag:
            return None, "未提取到页面内容"
        raw_text = content_tag.get_text()
        return raw_text, None
    except Exception as e:
        return None, f"URL抓取失败：{str(e)}"

def clean_text(text):
    """清洗文本：去HTML标签、标点、空白字符"""
    # 去HTML标签
    text = re.sub(r'<[^>]+>', '', text)
    # 去标点和特殊字符（保留中文、英文、数字，去除其他）
    text = re.sub(r'[^\u4e00-\u9fa5a-zA-Z0-9]', ' ', text)
    # 去多余空白字符
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def word_freq_analysis(text, min_freq=1):
    """分词并统计词频，过滤低频词"""
    # jieba分词
    words = jieba.lcut(text)
    # 过滤单字、空字符
    words = [word for word in words if len(word) > 1 and word.strip()]
    # 统计词频
    word_count = Counter(words)
    # 过滤低频词
    word_count = {word: count for word, count in word_count.items() if count >= min_freq}
    # 排序
    sorted_word_count = sorted(word_count.items(), key=lambda x: x[1], reverse=True)
    return sorted_word_count, word_count

# --------------------------
# 2. Streamlit页面布局（仅调整界面风格，恢复原有样式）
# --------------------------
# 页面基础配置（恢复原有风格）
st.set_page_config(
    page_title="文章URL词频分析与可视化系统",
    page_icon="📊",
    layout="wide"
)

# 主页面标题（恢复原有风格）
st.title("📚 文章URL词频分析与可视化系统")
st.divider()  # 分隔线，提升规整度

# --------------------------
# 侧边栏：恢复原有风格的配置区（逻辑不变，仅调整布局/样式）
# --------------------------
st.sidebar.title("⚙️ 系统配置与筛选")
st.sidebar.divider()

# 1. URL输入（移回侧边栏，恢复原有位置）
url = st.sidebar.text_input(
    "请输入文章URL地址",
    placeholder="例如：https://www.cnsoftbei.com/content-1-982-1.html",
    help="支持绝大多数中文资讯类文章网页"
)

# 2. 抓取/分析按钮（侧边栏，恢复原有样式）
submit_btn = st.sidebar.button("🔍 开始分析文章", type="primary")
st.sidebar.divider()

# 3. 低频词过滤阈值（样式微调，保持逻辑）
min_freq = st.sidebar.slider(
    "低频词过滤阈值（词频≥该值）",
    min_value=1, max_value=20, value=2, step=1,
    help="过滤出现频次低于该值的词汇，数值越小保留词汇越多"
)

# 4. 前N个词展示（样式微调，保持逻辑）
top_n = st.sidebar.slider(
    "展示词频排名前N的词汇",
    min_value=10, max_value=50, value=20, step=5,
    help="控制词频表格和图表展示的词汇数量"
)
st.sidebar.divider()

# 5. 图表类型选择（保留多选择，样式微调，逻辑不变）
chart_types = st.sidebar.multiselect(
    "请选择要展示的图表类型",
    options=["词云", "柱状图", "折线图", "饼图", "雷达图", "散点图", "热力图", "树状图"],
    default=["词云", "柱状图"],
    help="可同时选择多种图表，按选择顺序展示"
)
st.sidebar.divider()

# 6. 使用说明（样式微调，恢复原有风格）
st.sidebar.info(
    """
    📌 操作说明：
    1. 在上方输入有效文章URL
    2. 点击「开始分析文章」按钮
    3. 调整阈值/展示数量优化结果
    4. 选择图表类型查看可视化效果
    """
)

# --------------------------
# 3. 核心逻辑：URL分析与可视化（逻辑完全不变，仅调整界面展示风格）
# --------------------------
if submit_btn and url:
    with st.spinner("🔄 正在抓取URL内容并进行词频分析，请稍候..."):
        # 1. 抓取URL内容（逻辑不变）
        raw_text, error = get_url_content(url)
        if error:
            st.error(f"❌ {error}")
        else:
            # 2. 文本清洗（逻辑不变）
            clean_text_data = clean_text(raw_text)
            if not clean_text_data:
                st.error("❌ 清洗后无有效文本内容（URL可能非文章页面）")
            else:
                # 新增：文本预览（恢复原有风格的折叠框）
                st.subheader("📝 文章文本预览")
                with st.expander("点击展开/折叠原始文本", expanded=False):
                    st.caption(f"文本字符数（清洗后）：{len(clean_text_data)}")
                    st.text_area(
                        "清洗后的文本内容",
                        value=clean_text_data,
                        height=200,
                        disabled=True
                    )
                st.divider()

                # 3. 分词统计词频（逻辑不变）
                sorted_word_count, word_count = word_freq_analysis(clean_text_data, min_freq)
                if not sorted_word_count:
                    st.warning("⚠️ 分词后无有效词汇（可降低低频词阈值重试）")
                else:
                    # 取前top_n个词（逻辑不变）
                    top_words = sorted_word_count[:top_n]
                    words = [item[0] for item in top_words]
                    counts = [item[1] for item in top_words]

                    # 展示词频排名（样式微调，恢复原有风格）
                    st.subheader(f"🏆 词频排名前{top_n}的词汇")
                    # 美化表格展示（增加列配置，更规整）
                    st.dataframe(
                        {"词汇": words, "词频": counts},
                        use_container_width=True,
                        column_config={
                            "词汇": st.column_config.TextColumn("词汇", width="medium"),
                            "词频": st.column_config.NumberColumn("词频", width="small")
                        }
                    )
                    st.divider()

                    # 4. 可视化图表（逻辑不变，仅调整展示风格）
                    st.subheader("🎨 数据可视化图表")
                    col1, col2 = st.columns(2)  # 分栏展示（保留）

                    # 词云（逻辑不变，样式微调）
                    if "词云" in chart_types:
                        with col1:
                            st.markdown("### 词云图")
                            wordcloud = (
                                WordCloud()
                                .add(series_name="词频", data_pair=top_words, word_size_range=[10, 80])
                                .set_global_opts(title_opts=opts.TitleOpts(title="文章词汇词云"))
                            )
                            st_pyecharts(wordcloud, width="100%", height="400px")

                    # 柱状图（逻辑不变，样式微调）
                    if "柱状图" in chart_types:
                        with col2:
                            st.markdown("### 横向柱状图")
                            bar = (
                                Bar()
                                .add_xaxis(words)
                                .add_yaxis("词频", counts)
                                .reversal_axis()  # 横向柱状图（保留）
                                .set_global_opts(
                                    title_opts=opts.TitleOpts(title="词频排名"),
                                    xaxis_opts=opts.AxisOpts(name="词频"),
                                    yaxis_opts=opts.AxisOpts(name="词汇")
                                )
                            )
                            st_pyecharts(bar, width="100%", height="400px")

                    # 折线图（逻辑不变，样式微调）
                    if "折线图" in chart_types:
                        st.markdown("### 词频折线图")
                        line = (
                            Line()
                            .add_xaxis(words)
                            .add_yaxis("词频", counts)
                            .set_global_opts(
                                title_opts=opts.TitleOpts(title="词频趋势分布"),
                                xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(rotate=-45))
                            )
                        )
                        st_pyecharts(line, width="100%", height="400px")
                        st.divider()

                    # 饼图（逻辑不变，样式微调）
                    if "饼图" in chart_types:
                        pie_data = top_words[:10]
                        st.markdown("### 词频饼图（前10词）")
                        pie = (
                            Pie()
                            .add("", pie_data)
                            .set_global_opts(title_opts=opts.TitleOpts(title="词频占比分布（前10词）"))
                            .set_series_opts(label_opts=opts.LabelOpts(formatter="{b}: {c}"))
                        )
                        st_pyecharts(pie, width="100%", height="400px")
                        st.divider()

                    # # 雷达图（逻辑不变，样式微调）
                    # if "雷达图" in chart_types:
                    #     radar_data = top_words[:8]
                    #     radar_words = [item[0] for item in radar_data]
                    #     radar_counts = [item[1] for item in radar_data]
                    #     st.markdown("### 词频雷达图（前8词）")
                    #     radar = (
                    #         Radar()
                    #         .add_schema(schema=[opts.RadarIndicatorOpts(name=w, max_=max(radar_counts)) for w in radar_words])
                    #         .add("词频", [radar_counts])
                    #         .set_global_opts(title_opts=opts.TitleOpts(title="词频多维对比（前8词）"))
                    #     )
                    #     st_pyecharts(radar, width="100%", height="400px")
                    #     st.divider()

                    # 雷达图（终极兼容版，适配所有pyecharts版本）
                    if "雷达图" in chart_types:
                        radar_data = top_words[:8]
                        radar_words = [item[0] for item in radar_data]
                        radar_counts = [item[1] for item in radar_data]
                        st.markdown("### 词频雷达图（前8词）")
                        # 手动构造雷达图schema（绕过属性名差异）
                        radar_schema = []
                        max_count = max(radar_counts)
                        for w in radar_words:
                            radar_schema.append({"name": w, "max": max_count})
                        
                        radar = (
                            Radar()
                            .add_schema(schema=radar_schema)  # 直接传字典列表，兼容所有版本
                            .add("词频", [radar_counts])
                            .set_global_opts(title_opts=opts.TitleOpts(title="词频多维对比（前8词）"))
                        )
                        st_pyecharts(radar, width="100%", height="400px")
                        st.divider()

                    # 散点图（逻辑不变，样式微调）
                    if "散点图" in chart_types:
                        st.markdown("### 词频散点图")
                        scatter = (
                            Scatter()
                            .add_xaxis(words)
                            .add_yaxis("词频", counts)
                            .set_global_opts(
                                title_opts=opts.TitleOpts(title="词频分布散点图"),
                                xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(rotate=-45))
                            )
                        )
                        st_pyecharts(scatter, width="100%", height="400px")
                        st.divider()

                    # 热力图（逻辑不变，样式微调）
                    if "热力图" in chart_types:
                        st.markdown("### 词频热力图（前10词）")
                        heat_data = top_words[:10]
                        heat_x = [item[0] for item in heat_data]
                        heat_y = ["词频"]
                        heat_values = [[i, 0, heat_data[i][1]] for i in range(len(heat_x))]
                        heatmap = (
                            HeatMap()
                            .add_xaxis(heat_x)
                            .add_yaxis("词频", heat_y, heat_values)
                            .set_global_opts(
                                title_opts=opts.TitleOpts(title="词频热力分布（前10词）"),
                                visualmap_opts=opts.VisualMapOpts(min_=min(counts), max_=max(counts))
                            )
                        )
                        st_pyecharts(heatmap, width="100%", height="400px")
                        st.divider()

                    # 树状图（逻辑不变，样式微调）
                    if "树状图" in chart_types:
                        st.markdown("### 词频树状图")
                        treemap_data = [{"value": count, "name": word} for word, count in top_words[:10]]
                        treemap = (
                            TreeMap()
                            .add("词频", treemap_data)
                            .set_global_opts(title_opts=opts.TitleOpts(title="词频层级分布（前10词）"))
                        )
                        st_pyecharts(treemap, width="100%", height="400px")
                        st.divider()

# 空URL点击按钮的提示（样式微调，恢复原有风格）
elif submit_btn and not url:
    st.warning("⚠️ 请先输入有效的文章URL地址！")

# 初始状态提示（新增，恢复原有风格）
if not submit_btn:
    st.info("💡 请在左侧侧边栏输入文章URL，点击「开始分析文章」按钮启动词频分析")