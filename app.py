"""资料收集 — 独立Streamlit页，供客户填表"""
import streamlit as st
st.set_page_config(page_title="高考志愿 — 考生资料收集", page_icon="📋", layout="centered")

st.markdown("""
<style>
    .tag-wrap { display: flex; flex-wrap: wrap; gap: 6px; margin: 8px 0; }
    .tag-btn { display: inline-block; padding: 5px 16px; border-radius: 20px;
               border: 1px solid #ccc; background: #fff; cursor: pointer;
               font-size: 14px; user-select: none; transition: all .15s; }
    .tag-btn.sel { background: #007aff !important; color: #fff !important; border-color: #007aff !important; }
    .del-tag { display: inline-block; padding: 3px 12px; margin: 2px; border-radius: 20px;
               background: #ffd; font-size: 13px; }
    .out-box { background: #f5f5f7; border-radius: 12px; padding: 20px; margin-top: 20px; }
    .stButton>button { border-radius: 20px !important; }
</style>
""", unsafe_allow_html=True)

st.title("📋 高考志愿 · 考生资料收集")
st.caption("填完后点底部「生成文本」按钮，复制结果发给咨询师")

# 初始化
for k in ["gend", "prov", "strat"]:
    if k not in st.session_state: st.session_state[k] = ""

# 职业方向 → 映射到专业关键词（后端匹配用）
CAREER_MAJOR_MAP = {
    '互联网/科技（程序员、产品、算法等）': ['计算机', '软件工程', '人工智能', '数据科学', '电子', '通信', '微电子', '集成电路'],
    '当医生/做医疗': ['临床', '口腔', '药学', '护理', '生物医学', '医学影像', '麻醉'],
    '当老师/做教育': ['师范', '汉语言', '数学', '英语', '物理', '化学', '生物', '教育'],
    '考公务员/事业编': ['法学', '知识产权', '行政管理', '公共管理', '汉语言', '会计'],
    '做律师/法务': ['法学', '知识产权'],
    '进银行/金融/会计': ['金融', '会计', '财务管理', '审计', '经济', '统计'],
    '做工程师/搞制造': ['电气', '自动化', '机械', '车辆工程', '机器人', '土木', '建筑', '航空航天'],
    '做生意/创业/管理': ['工商管理', '市场营销', '电子商务', '人力资源', '旅游管理'],
    '设计/媒体/广告/影视': ['新闻', '广告', '新媒体', '建筑', '设计'],
    '搞科研/做学术': ['数学', '物理', '化学', '生物', '材料', '统计', '心理学'],
    '参军/从警/消防': ['公安', '军事', '消防', '安全', '侦察'],
    '交通/物流/航运': ['交通运输', '物流', '航海', '飞行'],
    '农业/林业/环境': ['农学', '林学', '环境', '食品', '水产'],
    '外语/国际/外交': ['英语', '翻译', '外交', '国际'],
    '艺术/体育/特长生': ['艺术', '音乐', '美术', '设计', '体育'],
    '没想好，啥都行': [],
}

CAREER_OPTIONS = list(CAREER_MAJOR_MAP.keys())
CITIES = '杭州,宁波,温州,嘉兴,湖州,绍兴,金华,衢州,舟山,台州,丽水,上海,北京,南京,苏州,深圳,广州,成都,武汉,西安,重庆'.split(',')

# ===== 基本信息 =====
c1, c2 = st.columns(2)
with c1: name = st.text_input("姓名", placeholder="选填")
with c2: gender = st.selectbox("性别", ["", "男", "女"])

c3, c4 = st.columns(2)
with c3: score = st.number_input("高考总分", 0, 750, 0, step=1, format="%d")
with c4: rank = st.number_input("全省位次（核心）", 0, 300000, 0, step=1, format="%d")

# ===== 选考科目 =====
st.markdown("**选考科目**")
subs = st.columns(7)
subj_vals = []
for i, s in enumerate(["物理","化学","生物","政治","历史","地理","技术"]):
    with subs[i]: subj_vals.append(st.checkbox(s, key=f"sub_{s}"))

# ===== 职业方向 =====
st.markdown("**以后想做什么？（多选）**")
st.caption("选职业方向比选具体专业更简单，后台会帮你匹配对应的专业")
sel_careers = st.pills("职业方向", CAREER_OPTIONS, selection_mode="multi", label_visibility="collapsed", key="career_pills")

# 根据职业方向推导偏好专业
sel_majors = []
if sel_careers:
    seen = set()
    for c in sel_careers:
        for m in CAREER_MAJOR_MAP.get(c, []):
            if m not in seen:
                seen.add(m)
                sel_majors.append(m)

# ===== 抗拒的行业 =====
st.markdown("**绝对不去的行业（选上就不会推荐相关专业）**")
st.caption("选抗拒行业比想排除什么专业更简单")
sel_reject = st.pills("抗拒行业", CAREER_OPTIONS, selection_mode="multi", label_visibility="collapsed", key="reject_pills")

# 根据抗拒行业推导排除专业
reject_majors = []
if sel_reject:
    seen = set()
    for c in sel_reject:
        for m in CAREER_MAJOR_MAP.get(c, []):
            if m not in seen:
                seen.add(m)
                reject_majors.append(m)

# ===== 地域 =====
st.markdown("**地域偏好**")
prov_pref = st.radio("地域偏好选项", ["不限", "尽量省内", "愿意出省", "只去省内"], horizontal=True, label_visibility="collapsed")

st.markdown("**偏好城市（可选）**")
st.caption("不选择等于默认接受")
cc = st.columns(2)
city_data = {}
city_reject = []
for i, city in enumerate(CITIES):
    with cc[i % 2]:
        pri = st.selectbox(city, ["", "最想去", "次之", "第三选择", "接受", "最不想去"], key=f"c_{city}")
        if pri == "最不想去":
            city_reject.append(city)
        elif pri:
            city_data[city] = ["最想去", "次之", "第三选择", "接受"].index(pri) + 1

# ===== 学校性质 =====
st.markdown("**学校性质**")
a, b, c = st.columns(3)
with a: accept_private = st.checkbox("接受民办", True)
with b: accept_coop = st.checkbox("接受中外合作", True)
with c: accept_independent = st.checkbox("接受独立学院", True)

tuition = st.number_input("学费上限（元/年，0=不限）", 0, 100000, 0, step=5000)

# ===== 策略 =====
st.markdown("**填报策略**")
strategy = st.radio("填报策略选择", [
    "专业优先（专业>学校>城市）",
    "学校优先（学校>专业>城市）",
    "城市优先（城市>学校>专业）",
    "无明确偏好",
], horizontal=True, label_visibility="collapsed")

notes = st.text_area("备注（色盲色弱、单科成绩限制、家庭因素等）", placeholder="选填")

# ===== 生成 =====
if st.button("📋 生成资料文本", use_container_width=True, type="primary"):
    lines = []

    # 行业→专业对照（输出最前面）
    if sel_careers:
        lines.append("==== 你的行业选择对应的可选专业 ====")
        for c in sel_careers:
            majors = CAREER_MAJOR_MAP.get(c, [])
            if majors:
                lines.append(f"  {c} 可选：{'、'.join(majors)}")
            else:
                lines.append(f"  {c}（不限专业）")
        lines.append("")

    if name: lines.append(f"姓名：{name}")
    if gender: lines.append(f"性别：{gender}")
    if score: lines.append(f"高考总分：{score}")
    if rank: lines.append(f"全省位次：{rank}")
    selected_subjs = [s for i, s in enumerate(["物理","化学","生物","政治","历史","地理","技术"]) if subj_vals[i]]
    if selected_subjs: lines.append(f"选考科目：{'、'.join(selected_subjs)}")
    if sel_careers: lines.append(f"职业方向：{'、'.join(sel_careers)}")
    if sel_majors: lines.append(f"偏好专业（自动匹配）：{'、'.join(sel_majors)}")
    if sel_reject: lines.append(f"抗拒行业：{'、'.join(sel_reject)}")
    if reject_majors: lines.append(f"排除专业（自动匹配）：{'、'.join(reject_majors)}")
    lines.append(f"地域偏好：{prov_pref}")
    if city_data: lines.append(f"偏好城市：{'、'.join(f'{c}(优先{p})' for c, p in city_data.items())}")
    if city_reject: lines.append(f"排除城市：{'、'.join(city_reject)}")
    lines.append(f"接受民办：{'是' if accept_private else '否'}")
    lines.append(f"接受中外合作：{'是' if accept_coop else '否'}")
    lines.append(f"接受独立学院：{'是' if accept_independent else '否'}")
    if tuition: lines.append(f"学费上限：{tuition}元/年")
    lines.append(f"填报策略：{strategy}")
    if notes: lines.append(f"备注：{notes}")
    text = "\n".join(lines)

    st.divider()
    st.subheader("📄 复制以下文本发给咨询师")
    st.code(text, language="text")
    st.info("按 Ctrl+C / ⌘C 复制上方文本，或点下方按钮下载文件")
    st.download_button("⬇ 下载 .txt 文件", text, file_name="考生资料.txt", use_container_width=True)
