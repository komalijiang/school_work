# 导入所需库
import streamlit as st
import streamlit.components.v1 as components  # 用于嵌入HTML图表
import requests
import pandas as pd
from bs4 import BeautifulSoup
import jieba
from collections import Counter
from pyecharts import options as opts
from pyecharts.charts import WordCloud, Bar, Line, Pie, Radar, Scatter, Funnel
from pyecharts.globals import ThemeType

# 页面配置
st.set_page_config(
    page_title="URL文本词频分析工具",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------- 功能函数定义 ----------------------
def get_web_text(url):
    """抓取URL网页中的文章正文文本"""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8"
    }
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        response.encoding = response.apparent_encoding
        soup = BeautifulSoup(response.text, "html.parser")
        text_content = []
        article_tag = soup.find("article")
        if article_tag:
            p_tags = article_tag.find_all("p")
        else:
            content_div = soup.find("div", class_=lambda cls: cls and "content" in cls.lower())
            p_tags = content_div.find_all("p") if content_div else soup.find_all("p")
        for p in p_tags:
            p_text = p.get_text(strip=True)
            if p_text and len(p_text) > 5:
                text_content.append(p_text)
        if not text_content:
            full_text = soup.get_text(strip=True, separator="\n")
            text_content = [line for line in full_text.split("\n") if len(line) > 10]
        return "\n".join(text_content)
    except Exception as e:
        st.error(f"URL抓取失败：{str(e)}")
        return None

def load_stopwords():
    """加载中文停用词表"""
    stopwords = {
        "的", "地", "得", "我", "你", "他", "她", "它", "我们", "你们", "他们",
        "她们", "它们", "这", "那", "此", "彼", "在", "上", "下", "左", "右",
        "前", "后", "和", "与", "或", "及", "而", "且", "是", "不是", "有", "没有",
        "能", "不能", "会", "不会", "可以", "不可以", "就", "才", "都", "也", "还",
        "只", "却", "更", "最", "很", "非常", "稍微", "比较", "着", "了", "过",
        "啊", "呀", "吗", "呢", "吧", "哦", "嗯", "一", "二", "三", "四", "五",
        "六", "七", "八", "九", "十", "百", "千", "万", "亿", "个", "只", "条",
        "本", "张", "件", "把", "对", "双", "副", "篇", "首", "支", "辆", "台",
        "架", "艘", "页", "行", "列", "天", "月", "年", "时", "分", "秒", "日",
        "周", "季", "网页", "文章", "内容", "来源", "作者", "发布", "时间", "阅读",
        "评论", "分享", "点赞", "收藏", "返回", "首页", "上一页", "下一页", "导航",
        "菜单", "版权", "所有", "保留", "转载", "请注明", "链接", "点击", "查看",
        "更多", "相关", "推荐", "热门", "最新", "更新", "访问", "使用", "帮助",
        "客服", "联系", "关于", "我们", "介绍", "功能", "说明", "注意", "事项"
    }
    return stopwords

def word_processing(text, stopwords):
    """文本分词与词频统计"""
    clean_text = text.replace("\n", "").replace(" ", "").replace("\t", "")\
                     .replace("\\", "").replace("/", "").replace("：", "")\
                     .replace("；", "").replace("，", "").replace("。", "")\
                     .replace("！", "").replace("？", "").replace("“", "")\
                     .replace("”", "").replace("‘", "").replace("’", "")\
                     .replace("（", "").replace("）", "").replace("【", "")\
                     .replace("】", "").replace("《", "").replace("》", "")
    words = jieba.lcut(clean_text)
    filtered_words = [
        word for word in words
        if word not in stopwords
        and len(word) >= 2
        and all("\u4e00" <= char <= "\u9fff" for char in word)
    ]
    return Counter(filtered_words)

# ---------------------- 页面布局与交互 ----------------------
st.title("📝 URL文章文本词频分析与可视化工具")
st.divider()

url = st.text_input("请输入文章完整URL地址", placeholder="示例：https://www.example.com/article/123.html", label_visibility="collapsed")

st.sidebar.title("⚙️ 可视化配置")
chart_options = [
    "词云图",
    "柱状图（词频前20）",
    "水平条形图（词频前20）",
    "折线图（词频前20）",
    "饼图（词频前20）",
    "雷达图（词频前10）",
    "散点图（词频前20）",
    "漏斗图（词频前20）"
]
selected_chart = st.sidebar.selectbox("选择可视化图表类型", options=chart_options, index=0)
min_freq = st.sidebar.slider("过滤低频词（最小词频）", min_value=1, max_value=20, value=2, step=1)

# ---------------------- 核心功能执行流程 ----------------------
if url:
    article_text = get_web_text(url)
    if article_text:
        stopwords = load_stopwords()
        word_frequency = word_processing(article_text, stopwords)
        if word_frequency:
            filtered_word_freq = {word: freq for word, freq in word_frequency.items() if freq >= min_freq}
            if filtered_word_freq:
                top20_word_freq = Counter(filtered_word_freq).most_common(20)
                top20_words = [item[0] for item in top20_word_freq]
                top20_freqs = [item[1] for item in top20_word_freq]
                st.dataframe(pd.DataFrame(top20_word_freq, columns=["词汇", "词频"]), use_container_width=True, hide_index=True)

                if selected_chart == "词云图":
                    wc = (
                        WordCloud(init_opts=opts.InitOpts(theme=ThemeType.LIGHT, width="1000px", height="600px"))
                        .add("", list(filtered_word_freq.items()), word_size_range=[20, 100])
                        .set_global_opts(title_opts=opts.TitleOpts(title="文章词汇词云图", subtitle=f"过滤低频词（最小词频：{min_freq}）"))
                    )
                    components.html(wc.render_embed(), width=1000, height=600, scrolling=False)

                elif selected_chart == "柱状图（词频前20）":
                    bar = (
                        Bar(init_opts=opts.InitOpts(theme=ThemeType.LIGHT, width="1000px", height="600px"))
                        .add_xaxis(top20_words)
                        .add_yaxis("词频", top20_freqs, color="#1890ff")
                        .set_global_opts(
                            title_opts=opts.TitleOpts(title="词频前20柱状图", subtitle="词汇词频对比"),
                            xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(rotate=-45)),
                            yaxis_opts=opts.AxisOpts(name="词频"),
                            tooltip_opts=opts.TooltipOpts(trigger="axis")
                        )
                        .set_series_opts(label_opts=opts.LabelOpts(is_show=True, position="top"))
                    )
                    components.html(bar.render_embed(), width=1000, height=600, scrolling=False)

                elif selected_chart == "水平条形图（词频前20）":
                    bar = (
                        Bar(init_opts=opts.InitOpts(theme=ThemeType.LIGHT, width="1000px", height="600px"))
                        .add_xaxis(top20_words)
                        .add_yaxis("词频", top20_freqs, color="#4e79a7")
                        .reversal_axis()  # 修复这里
                        .set_global_opts(
                            title_opts=opts.TitleOpts(title="词频前20水平条形图", subtitle="词汇词频对比"),
                            xaxis_opts=opts.AxisOpts(name="词频"),
                            yaxis_opts=opts.AxisOpts(name="词汇"),
                            tooltip_opts=opts.TooltipOpts(trigger="axis")
                        )
                        .set_series_opts(label_opts=opts.LabelOpts(is_show=True, position="right"))
                    )
                    components.html(bar.render_embed(), width=1000, height=600, scrolling=False)

                elif selected_chart == "折线图（词频前20）":
                    line = (
                        Line(init_opts=opts.InitOpts(theme=ThemeType.LIGHT, width="1000px", height="600px"))
                        .add_xaxis(top20_words)
                        .add_yaxis("词频", top20_freqs, color="#f56c6c",
                                   markpoint_opts=opts.MarkPointOpts(data=[opts.MarkPointItem(type_="max"), opts.MarkPointItem(type_="min")]),
                                   markline_opts=opts.MarkLineOpts(data=[opts.MarkLineItem(type_="average")]))
                        .set_global_opts(
                            title_opts=opts.TitleOpts(title="词频前20折线图", subtitle="词汇词频趋势"),
                            xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(rotate=-45)),
                            yaxis_opts=opts.AxisOpts(name="词频"),
                            tooltip_opts=opts.TooltipOpts(trigger="axis")
                        )
                    )
                    components.html(line.render_embed(), width=1000, height=600, scrolling=False)

                elif selected_chart == "饼图（词频前20）":
                    pie = (
                        Pie(init_opts=opts.InitOpts(theme=ThemeType.LIGHT, width="1000px", height="600px"))
                        .add("", top20_word_freq, radius=["30%", "75%"], rosetype="radius")
                        .set_global_opts(
                            title_opts=opts.TitleOpts(title="词频前20饼图（玫瑰图）", subtitle="词汇词频占比分布"),
                            legend_opts=opts.LegendOpts(orient="vertical", pos_left="left")  # 删除 max_width
                        )
                        .set_series_opts(
                            tooltip_opts=opts.TooltipOpts(formatter="词汇：{b}<br/>词频：{c}<br/>占比：{d}%"),
                            label_opts=opts.LabelOpts(formatter="{b}: {d}%")
                        )
                    )
                    components.html(pie.render_embed(), width=1000, height=600, scrolling=False)

                elif selected_chart == "雷达图（词频前10）":
                    top10 = Counter(filtered_word_freq).most_common(10)
                    max_val = max([f for w, f in top10])
                    radar = (
                        Radar(init_opts=opts.InitOpts(theme=ThemeType.LIGHT, width="1000px", height="600px"))
                        .add_schema([opts.RadarIndicatorItem(name=w, max_=max_val) for w, f in top10])
                        .add("词频", [[f for w, f in top10]], color="#2f4554")
                        .set_global_opts(title_opts=opts.TitleOpts(title="词频前10雷达图", subtitle="词汇词频多维度对比"))
                    )
                    components.html(radar.render_embed(), width=1000, height=600, scrolling=False)

                elif selected_chart == "散点图（词频前20）":
                    scatter = (
                        Scatter(init_opts=opts.InitOpts(theme=ThemeType.LIGHT, width="1000px", height="600px"))
                        .add_xaxis(top20_words)
                        .add_yaxis("词频", top20_freqs, symbol_size=lambda x: x * 2, color="#e15454")
                        .set_global_opts(
                            title_opts=opts.TitleOpts(title="词频前20散点图", subtitle="词汇词频分布"),
                            xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(rotate=-45)),
                            yaxis_opts=opts.AxisOpts(name="词频"),
                            tooltip_opts=opts.TooltipOpts(formatter="词汇：{b}<br/>词频：{c}"),
                            visualmap_opts=opts.VisualMapOpts(type_="color", max_=max(top20_freqs), min_=min(top20_freqs), dimension=1)
                        )
                    )
                    components.html(scatter.render_embed(), width=1000, height=600, scrolling=False)

                elif selected_chart == "漏斗图（词频前20）":
                    funnel = (
                        Funnel(init_opts=opts.InitOpts(theme=ThemeType.LIGHT, width="1000px", height="600px"))
                        .add("", top20_word_freq, sort_="ascending", gap=2)
                        .set_global_opts(
                            title_opts=opts.TitleOpts(title="词频前20漏斗图", subtitle="词汇词频层级分布"),
                            tooltip_opts=opts.TooltipOpts(formatter="词汇：{b}<br/>词频：{c}")
                        )
                        .set_series_opts(label_opts=opts.LabelOpts(is_show=True, position="inside", formatter="{b}: {c}"))
                    )
                    components.html(funnel.render_embed(), width=1000, height=600, scrolling=False)
            else:
                st.warning("过滤后无有效词汇")
        else:
            st.warning("未提取到有效词汇")
    else:
        st.error("未获取到文本内容")
else:
    st.info("请输入文章URL地址")
