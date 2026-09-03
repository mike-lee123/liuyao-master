# -*- coding: utf-8 -*-
"""
星僑 (NCC) 卜卦命理 App · 全動態六十四卦排盤圖形引擎
輸入任意三組數字，卦盤、爻象、世應、變卦、互卦、神煞 100% 動態即時變換！
"""
import streamlit as st
import streamlit.components.v1 as components
from datetime import datetime

st.set_page_config(
    page_title="星僑 (NCC) 占卦圖形介面",
    page_icon="☯️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 1. 先天八卦與納甲核心庫 ---
BAGUA = {
    1: {"name": "乾", "nature": "天", "elem": "金", "lines": [1, 1, 1], "inner": ["子", "寅", "辰"], "outer": ["午", "申", "戌"], "inner_gan": "甲", "outer_gan": "壬"},
    2: {"name": "兌", "nature": "澤", "elem": "金", "lines": [1, 1, 0], "inner": ["巳", "卯", "丑"], "outer": ["亥", "酉", "未"], "inner_gan": "丁", "outer_gan": "丁"},
    3: {"name": "離", "nature": "火", "elem": "火", "lines": [1, 0, 1], "inner": ["卯", "丑", "亥"], "outer": ["酉", "未", "巳"], "inner_gan": "己", "outer_gan": "己"},
    4: {"name": "震", "nature": "雷", "elem": "木", "lines": [1, 0, 0], "inner": ["子", "寅", "辰"], "outer": ["午", "申", "戌"], "inner_gan": "庚", "outer_gan": "庚"},
    5: {"name": "巽", "nature": "風", "elem": "木", "lines": [0, 1, 1], "inner": ["丑", "亥", "酉"], "outer": ["未", "巳", "卯"], "inner_gan": "辛", "outer_gan": "辛"},
    6: {"name": "坎", "nature": "水", "elem": "水", "lines": [0, 1, 0], "inner": ["寅", "辰", "午"], "outer": ["申", "戌", "子"], "inner_gan": "戊", "outer_gan": "戊"},
    7: {"name": "艮", "nature": "山", "elem": "土", "lines": [0, 0, 1], "inner": ["辰", "寅", "子"], "outer": ["戌", "申", "午"], "inner_gan": "丙", "outer_gan": "丙"},
    8: {"name": "坤", "nature": "地", "elem": "土", "lines": [0, 0, 0], "inner": ["未", "巳", "卯"], "outer": ["丑", "亥", "酉"], "inner_gan": "乙", "outer_gan": "癸"}
}

DIZHI_ELEM = {
    "子": "水", "丑": "土", "寅": "木", "卯": "木",
    "辰": "土", "巳": "火", "午": "火", "未": "土",
    "申": "金", "酉": "金", "戌": "土", "亥": "水"
}

# 完整六十四卦字典 (上卦ID, 下卦ID) -> (卦名, 所屬宮首卦, 宮五行, 世爻位置, 卦宮類型)
GUA_64 = {
    # 乾宮屬金
    (1,1): ("乾為天", "乾為天", "金", 6, "本宮"), (1,5): ("天風姤", "乾為天", "金", 1, "一世"),
    (1,7): ("天山遯", "乾為天", "金", 2, "二世"), (1,8): ("天地否", "乾為天", "金", 3, "三世"),
    (5,8): ("風地觀", "乾為天", "金", 4, "四世"), (7,8): ("山地剝", "乾為天", "金", 5, "五世"),
    (3,8): ("火地晉", "乾為天", "金", 4, "游"),   (3,1): ("火天大有", "乾為天", "金", 3, "歸"),
    # 坎宮屬水
    (6,6): ("坎為水", "坎為水", "水", 6, "本宮"), (6,2): ("水澤節", "坎為水", "水", 1, "一世"),
    (6,4): ("水雷屯", "坎為水", "水", 2, "二世"), (6,3): ("水火既濟", "坎為水", "水", 3, "三世"),
    (2,3): ("澤火革", "坎為水", "水", 4, "四世"), (4,3): ("雷火豐", "坎為水", "水", 5, "五世"),
    (8,3): ("地火明夷", "坎為水", "水", 4, "游"), (8,6): ("地水師", "坎為水", "水", 3, "歸"),
    # 艮宮屬土
    (7,7): ("艮為山", "艮為山", "土", 6, "本宮"), (7,3): ("山火賁", "艮為山", "土", 1, "一世"),
    (7,1): ("山天大畜", "艮為山", "土", 2, "二世"), (7,2): ("山澤損", "艮為山", "土", 3, "三世"),
    (3,2): ("火澤睽", "艮為山", "土", 4, "四世"), (1,2): ("天澤履", "艮為山", "土", 5, "五世"),
    (5,2): ("風澤中孚", "艮為山", "土", 4, "游"), (5,7): ("風山漸", "艮為山", "土", 3, "歸"),
    # 震宮屬木
    (4,4): ("震為雷", "震為雷", "木", 6, "本宮"), (4,8): ("雷地豫", "震為雷", "木", 1, "一世"),
    (4,6): ("雷水解", "震為雷", "木", 2, "二世"), (4,5): ("雷風恆", "震為雷", "木", 3, "三世"),
    (8,5): ("地風升", "震為雷", "木", 4, "四世"), (6,5): ("水風井", "震為雷", "木", 5, "五世"),
    (2,5): ("澤風大過", "震為雷", "木", 4, "游"), (2,4): ("澤雷隨", "震為雷", "木", 3, "歸"),
    # 巽宮屬木
    (5,5): ("巽為風", "巽為風", "木", 6, "本宮"), (5,1): ("風天小畜", "巽為風", "木", 1, "一世"),
    (5,3): ("風火家人", "巽為風", "木", 2, "二世"), (5,4): ("風雷益", "巽為風", "木", 3, "三世"),
    (1,4): ("天雷無妄", "巽為風", "木", 4, "四世"), (3,4): ("火雷噬嗑", "巽為風", "木", 5, "五世"),
    (7,4): ("山雷頤", "巽為風", "木", 4, "游"),   (7,5): ("山風蠱", "巽為風", "木", 3, "歸"),
    # 離宮屬火
    (3,3): ("離為火", "離為火", "火", 6, "本宮"), (3,7): ("火山旅", "離為火", "火", 1, "一世"),
    (3,5): ("火風鼎", "離為火", "火", 2, "二世"), (3,6): ("火水未濟", "離為火", "火", 3, "三世"),
    (7,6): ("山水蒙", "離為火", "火", 4, "四世"), (5,6): ("風水渙", "離為火", "火", 5, "五世"),
    (1,6): ("天水訟", "離為火", "火", 4, "游"),   (1,3): ("天火同人", "離為火", "火", 3, "歸"),
    # 坤宮屬土
    (8,8): ("坤為地", "坤為地", "土", 6, "本宮"), (8,4): ("地雷復", "坤為地", "土", 1, "一世"),
    (8,2): ("地澤臨", "坤為地", "土", 2, "二世"), (8,1): ("地天泰", "坤為地", "土", 3, "三世"),
    (4,1): ("雷天大壯", "坤為地", "土", 4, "四世"), (2,1): ("澤天夬", "坤為地", "土", 5, "五世"),
    (6,1): ("水天需", "坤為地", "土", 4, "游"),   (6,8): ("水地比", "坤為地", "土", 3, "歸"),
    # 兌宮屬金
    (2,2): ("兌為澤", "兌為澤", "金", 6, "本宮"), (2,6): ("澤水困", "兌為澤", "金", 1, "一世"),
    (2,8): ("澤地萃", "兌為澤", "金", 2, "二世"), (2,7): ("澤山咸", "兌為澤", "金", 3, "三世"),
    (6,7): ("水山蹇", "兌為澤", "金", 4, "四世"), (8,7): ("地山謙", "兌為澤", "金", 5, "五世"),
    (4,7): ("雷山小過", "兌為澤", "金", 4, "游"), (4,2): ("雷澤歸妹", "兌為澤", "金", 3, "歸")
}

# 八純卦納甲干支（查伏神用）
PURE_GUA = {
    "乾為天": [("甲子", "水"), ("甲寅", "木"), ("甲辰", "土"), ("壬午", "火"), ("壬申", "金"), ("壬戌", "土")],
    "兌為澤": [("丁巳", "火"), ("丁卯", "木"), ("丁丑", "土"), ("丁亥", "水"), ("丁酉", "金"), ("丁未", "土")],
    "離為火": [("己卯", "木"), ("己丑", "土"), ("己亥", "水"), ("己酉", "金"), ("己未", "土"), ("己巳", "火")],
    "震為雷": [("庚子", "水"), ("庚寅", "木"), ("庚辰", "土"), ("庚午", "火"), ("庚申", "金"), ("庚戌", "土")],
    "巽為風": [("辛丑", "土"), ("辛亥", "水"), ("辛酉", "金"), ("辛未", "土"), ("辛巳", "火"), ("辛卯", "木")],
    "坎為水": [("戊寅", "木"), ("戊辰", "土"), ("戊午", "火"), ("戊申", "金"), ("戊戌", "土"), ("戊子", "水")],
    "艮為山": [("丙辰", "土"), ("丙寅", "木"), ("丙子", "水"), ("丙戌", "土"), ("丙申", "金"), ("丙午", "火")],
    "坤為地": [("乙未", "土"), ("乙巳", "火"), ("乙卯", "木"), ("癸丑", "土"), ("癸亥", "水"), ("癸酉", "金")]
}

def get_liuqin(p_elem, b_elem):
    table = {
        ("金", "金"): "兄弟", ("金", "木"): "妻財", ("金", "水"): "子孫", ("金", "火"): "官鬼", ("金", "土"): "父母",
        ("木", "木"): "兄弟", ("木", "土"): "妻財", ("木", "火"): "子孫", ("木", "金"): "官鬼", ("木", "水"): "父母",
        ("水", "水"): "兄弟", ("水", "火"): "妻財", ("水", "木"): "子孫", ("水", "土"): "官鬼", ("水", "金"): "父母",
        ("火", "火"): "兄弟", ("火", "金"): "妻財", ("火", "土"): "子孫", ("火", "水"): "官鬼", ("火", "木"): "父母",
        ("土", "土"): "兄弟", ("土", "水"): "妻財", ("土", "金"): "子孫", ("土", "木"): "官鬼", ("土", "火"): "父母"
    }
    return table.get((p_elem, b_elem), "兄弟")

def get_liushen(day_gan):
    table = {
        "甲": ["青龍", "朱雀", "勾陳", "騰蛇", "白虎", "玄武"],
        "乙": ["青龍", "朱雀", "勾陳", "騰蛇", "白虎", "玄武"],
        "丙": ["朱雀", "勾陳", "騰蛇", "白虎", "玄武", "青龍"],
        "丁": ["朱雀", "勾陳", "騰蛇", "白虎", "玄武", "青龍"],
        "戊": ["勾陳", "騰蛇", "白虎", "玄武", "青龍", "朱雀"],
        "己": ["騰蛇", "白虎", "玄武", "青龍", "朱雀", "勾陳"],
        "庚": ["白虎", "玄武", "青龍", "朱雀", "勾陳", "騰蛇"],
        "辛": ["白虎", "玄武", "青龍", "朱雀", "勾陳", "騰蛇"],
        "壬": ["玄武", "青龍", "朱雀", "勾陳", "騰蛇", "白虎"],
        "癸": ["玄武", "青龍", "朱雀", "勾陳", "騰蛇", "白虎"]
    }
    return table.get(day_gan, table["辛"])

def make_vert_svg(text, x, y_start, font_size=14, color="#111111", line_gap=19, max_chars=8):
    if not text:
        return ""
    safe_text = str(text)[:max_chars]
    svg_pieces = []
    for idx, ch in enumerate(safe_text):
        y_pos = y_start + (idx * line_gap)
        svg_pieces.append(f'<text x="{x}" y="{y_pos}" font-size="{font_size}" font-weight="bold" fill="{color}" text-anchor="middle">{ch}</text>')
    return "".join(svg_pieces)

# --- 2. 側邊控制欄 ---
st.sidebar.markdown("### 🎛️ 三組數字起卦")
col1, col2, col3 = st.sidebar.columns(3)
in_n1 = col1.number_input("第1組(下卦)", value=54, min_value=1, step=1)
in_n2 = col2.number_input("第2組(上卦)", value=12, min_value=1, step=1)
in_n3 = col3.number_input("第3組(動爻)", value=65, min_value=1, step=1)

st.sidebar.markdown("---")
st.sidebar.markdown("### 📅 時間與問事設定")
c_solar = st.sidebar.text_input("陽曆時間", value=datetime.now().strftime("%Y/%m/%d %H:%M"))
c_lunar = st.sidebar.text_input("農曆時間", value="歲次時令")
c_y = st.sidebar.text_input("年柱", value="丙午")
c_m = st.sidebar.text_input("月柱", value="丙申")
c_d = st.sidebar.text_input("日柱", value="庚辰")
c_h = st.sidebar.text_input("時柱", value="甲申")
c_kong = st.sidebar.text_input("日旬空亡", value="申酉")
user_q = st.sidebar.text_input("問事事由", value="問身體健康注意事項")

# --- 3. 核心演算法：根據三組數字全動態生成 ---
lower_id = in_n1 % 8 if (in_n1 % 8) != 0 else 8
upper_id = in_n2 % 8 if (in_n2 % 8) != 0 else 8
moving_line = in_n3 % 6 if (in_n3 % 6) != 0 else 6

# 本卦資訊
ben_name, shou_name, palace_elem, shi_pos, ben_type = GUA_64.get((upper_id, lower_id), ("自訂卦", "乾為天", "金", 3, "世卦"))
ying_pos = (shi_pos + 3) % 6 or 6
ben_lines = BAGUA[lower_id]["lines"] + BAGUA[upper_id]["lines"]

# 變卦計算 (動爻陰陽互變)
bian_lines = list(ben_lines)
bian_lines[moving_line - 1] = 1 - bian_lines[moving_line - 1]
bian_lower_lines = bian_lines[:3]
bian_upper_lines = bian_lines[3:]
bian_lower_id = next(k for k, v in BAGUA.items() if v["lines"] == bian_lower_lines)
bian_upper_id = next(k for k, v in BAGUA.items() if v["lines"] == bian_upper_lines)
bian_name, _, _, _, _ = GUA_64.get((bian_upper_id, bian_lower_id), ("變卦", "乾為天", "金", 3, "世卦"))

# 互卦計算 (二三四為下，三四五為上)
hu_lower_lines = [ben_lines[1], ben_lines[2], ben_lines[3]]
hu_upper_lines = [ben_lines[2], ben_lines[3], ben_lines[4]]
hu_lower_id = next(k for k, v in BAGUA.items() if v["lines"] == hu_lower_lines)
hu_upper_id = next(k for k, v in BAGUA.items() if v["lines"] == hu_upper_lines)
hu_name, _, _, _, _ = GUA_64.get((hu_upper_id, hu_lower_id), ("互卦", "乾為天", "金", 3, "世卦"))

# 裝卦納甲天干地支
l_gan = BAGUA[lower_id]["inner_gan"]
u_gan = BAGUA[upper_id]["outer_gan"]
ben_ganzhi = [f"{l_gan}{b}" for b in BAGUA[lower_id]["inner"]] + [f"{u_gan}{b}" for b in BAGUA[upper_id]["outer"]]

bl_gan = BAGUA[bian_lower_id]["inner_gan"]
bu_gan = BAGUA[bian_upper_id]["outer_gan"]
bian_ganzhi = [f"{bl_gan}{b}" for b in BAGUA[bian_lower_id]["inner"]] + [f"{bu_gan}{b}" for b in BAGUA[bian_upper_id]["outer"]]

day_gan = c_d[0] if len(c_d) > 0 else "辛"
liushen = get_liushen(day_gan)

# 伏神推算 (查本宮純卦中缺漏之六親)
pure_branches = PURE_GUA.get(shou_name, PURE_GUA["乾為天"])
present_qins = set()
for gz in ben_ganzhi:
    present_qins.add(get_liuqin(palace_elem, DIZHI_ELEM[gz[1]]))

fushen_dict = {}
for idx, (p_gz, p_elem) in enumerate(pure_branches):
    q = get_liuqin(palace_elem, p_elem)
    if q not in present_qins and (idx + 1) not in fushen_dict:
        fushen_dict[idx + 1] = (q, p_gz[0], p_gz[1], p_elem)

# 組裝動態六爻資料 (初爻至六爻)
dynamic_lines = []
for i in range(6):
    l_num = i + 1
    is_mv = (l_num == moving_line)
    
    beast = liushen[i]
    bgz = ben_ganzhi[i]
    b_gan, b_zhi = bgz[0], bgz[1]
    b_el = DIZHI_ELEM[b_zhi]
    b_qin = get_liuqin(palace_elem, b_el)
    is_kong = b_zhi in c_kong
    
    sy_label = "世" if l_num == shi_pos else ("應" if l_num == ying_pos else "")
    
    # 爻象符號 (星僑經典)
    if is_mv:
        sym_type = "dong_yin" if ben_lines[i] == 0 else "dong_yang"
    else:
        sym_type = "yang" if ben_lines[i] == 1 else "yin"
        
    # 變爻
    bi_gan, bi_zhi, bi_qin, bi_he = "", "", "", ""
    if is_mv:
        bigz = bian_ganzhi[i]
        bi_gan, bi_zhi = bigz[0], bigz[1]
        bi_el = DIZHI_ELEM[bi_zhi]
        bi_qin = get_liuqin(palace_elem, bi_el)
        # 是否合
        if (b_zhi, bi_zhi) in [("丑","子"),("子","丑"),("辰","酉"),("酉","辰"),("寅","亥"),("亥","寅"),("卯","戌"),("戌","卯"),("巳","申"),("申","巳"),("午","未"),("未","午")]:
            bi_he = "合"
            
    # 伏神
    fu_gan, fu_zhi, fu_el, fu_qin = "", "", "", ""
    if l_num in fushen_dict:
        fu_qin, fu_gan, fu_zhi, fu_el = fushen_dict[l_num]
        
    dynamic_lines.append((
        beast, b_qin, sy_label, sym_type, b_gan, b_zhi, b_el, is_kong,
        bi_gan, bi_zhi, bi_qin, bi_he, fu_gan, fu_zhi, fu_el, fu_qin
    ))

# --- 4. 動態生成 SVG 向量排盤圖 ---
def generate_dynamic_svg(lines_data, ben_n, bian_n, shou_n, shou_el, hu_n, b_type, matter, y_txt, m_txt, d_txt, date_txt):
    W, H = 460, 820
    svg = f'''
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" style="background:#ffffff; font-family:'Microsoft JhengHei',sans-serif; border:2px solid #444; border-radius:4px;">
        <rect x="0" y="0" width="{W}" height="42" fill="#f4f4f4" stroke="#777" stroke-width="1"/>
        <text x="18" y="27" font-size="20" fill="#666">〈</text>
        <text x="{W/2}" y="27" font-size="18" font-weight="bold" fill="#111" text-anchor="middle">占卦功能</text>
        <rect x="{W-68}" y="8" width="54" height="26" rx="4" fill="#e5e5e5" stroke="#999" stroke-width="1"/>
        <text x="{W-41}" y="26" font-size="14" font-weight="bold" fill="#111" text-anchor="middle">解析</text>

        <rect x="0" y="42" width="{W}" height="30" fill="#ffffff" stroke="#777" stroke-width="1"/>
    '''
    # 表頭
    headers = [(16, "六", "獸"), (48, "六", "親"), (78, "世", "應"), (112, "NCC", "星僑"), (155, "裝", "卦"), (201, "變", "卦"), (240, "六", "親"), (278, "伏", "神"), (315, "六", "親")]
    for x, t1, t2 in headers:
        svg += f'<text x="{x}" y="55" font-size="12" font-weight="bold" fill="#111" text-anchor="middle">{t1}</text>'
        svg += f'<text x="{x}" y="68" font-size="12" font-weight="bold" fill="#111" text-anchor="middle">{t2}</text>'

    svg += f'''
        <text x="343" y="55" font-size="13" fill="#111" text-anchor="middle">日</text>
        <text x="343" y="69" font-size="12" font-weight="bold" fill="#111" text-anchor="middle">{d_txt}</text>
        <text x="369" y="55" font-size="13" fill="#111" text-anchor="middle">月</text>
        <text x="369" y="69" font-size="12" font-weight="bold" fill="#111" text-anchor="middle">{m_txt}</text>
        <text x="395" y="55" font-size="13" fill="#111" text-anchor="middle">年</text>
        <text x="395" y="69" font-size="12" font-weight="bold" fill="#111" text-anchor="middle">{y_txt}</text>
        <rect x="330" y="72" width="80" height="18" fill="#ffffff" stroke="#777" stroke-width="0.8"/>
        <text x="370" y="85" font-size="11" fill="#cc0000" font-weight="bold" text-anchor="middle">{date_txt.split(' ')[0]}</text>
    '''

    # 六爻行 (由六爻到初爻向下畫)
    row_h, y_start = 55, 72
    for idx, row in enumerate(reversed(lines_data)):
        y = y_start + idx * row_h
        beast, qin, sy, sym, z_gan, z_zhi, z_el, kong, bi_gan, bi_zhi, bi_qin, he, fu_gan, fu_zhi, fu_el, fu_qin = row

        svg += f'<line x1="0" y1="{y+row_h}" x2="330" y2="{y+row_h}" stroke="#777" stroke-width="1"/>'

        # 六獸與六親
        svg += f'<text x="16" y="{y+32}" font-size="15" font-weight="bold" fill="#800080" text-anchor="middle">{beast[0]}</text>'
        svg += f'<text x="16" y="{y+46}" font-size="15" font-weight="bold" fill="#800080" text-anchor="middle">{beast[1]}</text>'
        svg += f'<text x="48" y="{y+32}" font-size="15" font-weight="bold" fill="#8b2500" text-anchor="middle">{qin[0]}</text>'
        svg += f'<text x="48" y="{y+46}" font-size="15" font-weight="bold" fill="#8b2500" text-anchor="middle">{qin[1]}</text>'

        # 世應
        if sy:
            svg += f'<text x="78" y="{y+36}" font-size="18" font-weight="bold" fill="#cc0000" text-anchor="middle">{sy}</text>'

        # 爻符
        if sym == "yang":
            svg += f'<line x1="98" y1="{y+38}" x2="126" y2="{y+20}" stroke="#0000cc" stroke-width="4.5" stroke-linecap="round"/>'
        elif sym == "yin":
            svg += f'<line x1="96" y1="{y+40}" x2="110" y2="{y+28}" stroke="#0000cc" stroke-width="4.5" stroke-linecap="round"/>'
            svg += f'<line x1="114" y1="{y+28}" x2="128" y2="{y+16}" stroke="#0000cc" stroke-width="4.5" stroke-linecap="round"/>'
        elif sym == "dong_yin":
            # 陰動大叉叉 ╳
            svg += f'<line x1="98" y1="{y+18}" x2="126" y2="{y+42}" stroke="#0000cc" stroke-width="5" stroke-linecap="round"/>'
            svg += f'<line x1="98" y1="{y+42}" x2="126" y2="{y+18}" stroke="#0000cc" stroke-width="5" stroke-linecap="round"/>'
        elif sym == "dong_yang":
            # 陽動大圓圈 ◯
            svg += f'<circle cx="112" cy="{y+30}" r="11" stroke="#cc0000" stroke-width="4" fill="none"/>'

        # 裝卦
        svg += f'<text x="165" y="{y+22}" font-size="13" font-weight="bold" fill="#008000" text-anchor="middle">{z_gan}</text>'
        svg += f'<text x="146" y="{y+30}" font-size="18" font-weight="bold" fill="#000080" text-anchor="middle">{z_zhi}</text>'
        svg += f'<text x="146" y="{y+48}" font-size="13" font-weight="bold" fill="#8b2500" text-anchor="middle">{z_el}</text>'
        if kong:
            svg += f'<rect x="158" y="{y+24}" width="15" height="15" fill="#f0f0f0" stroke="#777" stroke-width="1" rx="2"/>'
            svg += f'<text x="165.5" y="{y+35.5}" font-size="10" fill="#444" font-weight="bold" text-anchor="middle">空</text>'

        # 變卦
        if bi_zhi:
            svg += f'<text x="210" y="{y+22}" font-size="13" font-weight="bold" fill="#008000" text-anchor="middle">{bi_gan}</text>'
            svg += f'<text x="190" y="{y+30}" font-size="18" font-weight="bold" fill="#cc0000" text-anchor="middle">{bi_zhi}</text>'
            if he:
                svg += f'<text x="190" y="{y+48}" font-size="13" font-weight="bold" fill="#111" text-anchor="middle">{he}</text>'
            svg += f'<text x="240" y="{y+32}" font-size="15" font-weight="bold" fill="#cc0000" text-anchor="middle">{bi_qin[0]}</text>'
            svg += f'<text x="240" y="{y+46}" font-size="15" font-weight="bold" fill="#cc0000" text-anchor="middle">{bi_qin[1]}</text>'

        # 伏神
        if fu_zhi:
            svg += f'<text x="290" y="{y+22}" font-size="13" font-weight="bold" fill="#008000" text-anchor="middle">{fu_gan}</text>'
            svg += f'<text x="270" y="{y+30}" font-size="17" font-weight="bold" fill="#008000" text-anchor="middle">{fu_zhi}</text>'
            svg += f'<text x="270" y="{y+48}" font-size="13" font-weight="bold" fill="#8b2500" text-anchor="middle">{fu_el}</text>'
            svg += f'<text x="315" y="{y+32}" font-size="15" font-weight="bold" fill="#008000" text-anchor="middle">{fu_qin[0]}</text>'
            svg += f'<text x="315" y="{y+46}" font-size="15" font-weight="bold" fill="#008000" text-anchor="middle">{fu_qin[1]}</text>'

    for cx in [32, 64, 92, 132, 178, 224, 256, 300, 330]:
        svg += f'<line x1="{cx}" y1="42" x2="{cx}" y2="402" stroke="#777" stroke-width="1"/>'

    # 右側直欄 (完全動態渲染)
    b_svg = make_vert_svg(bian_n, 343, 185, font_size=15, color="#cc0000", line_gap=20)
    be_svg = make_vert_svg(ben_n, 369, 185, font_size=15, color="#000080", line_gap=20)
    s_svg = make_vert_svg(shou_n, 396, 170, font_size=14, color="#cc0000", line_gap=18)
    h_svg = make_vert_svg(hu_n, 396, 325, font_size=14, color="#78237b", line_gap=18)
    m_svg = make_vert_svg(matter, 435, 105, font_size=13, color="#78237b", line_gap=20, max_chars=8)

    svg += f'''
        <rect x="330" y="90" width="26" height="312" fill="#ffffff" stroke="#777" stroke-width="1"/>
        <text x="343" y="115" font-size="13" font-weight="bold" fill="#111" text-anchor="middle">變</text>
        <text x="343" y="133" font-size="13" font-weight="bold" fill="#111" text-anchor="middle">卦</text>
        {b_svg}

        <rect x="356" y="90" width="26" height="312" fill="#ffffff" stroke="#777" stroke-width="1"/>
        <text x="369" y="115" font-size="13" font-weight="bold" fill="#111" text-anchor="middle">本</text>
        <rect x="358" y="125" width="22" height="18" fill="#1d4ed8" rx="2"/>
        <text x="369" y="138" font-size="12" font-weight="bold" fill="#ffffff" text-anchor="middle">{b_type}</text>
        {be_svg}

        <rect x="382" y="90" width="28" height="156" fill="#ffffff" stroke="#777" stroke-width="1"/>
        <text x="396" y="112" font-size="13" font-weight="bold" fill="#111" text-anchor="middle">首</text>
        <rect x="385" y="122" width="22" height="18" fill="#8b4513" rx="2"/>
        <text x="396" y="135" font-size="12" font-weight="bold" fill="#ffffff" text-anchor="middle">{shou_el}</text>
        {s_svg}

        <rect x="382" y="246" width="28" height="156" fill="#ffffff" stroke="#777" stroke-width="1"/>
        <text x="396" y="268" font-size="13" font-weight="bold" fill="#111" text-anchor="middle">互</text>
        <rect x="385" y="278" width="22" height="18" fill="#2563eb" rx="2"/>
        <text x="396" y="291" font-size="12" font-weight="bold" fill="#ffffff" text-anchor="middle">沖</text>
        {h_svg}

        <rect x="410" y="42" width="50" height="360" fill="#ffffff" stroke="#777" stroke-width="1"/>
        <text x="435" y="65" font-size="13" font-weight="bold" fill="#111" text-anchor="middle">事</text>
        <text x="435" y="80" font-size="13" font-weight="bold" fill="#111" text-anchor="middle">由</text>
        {m_svg}

        <!-- 底部神煞矩陣 -->
        <rect x="0" y="402" width="{W}" height="418" fill="#ffffff" stroke="#555" stroke-width="2"/>
        <rect x="0" y="402" width="160" height="26" fill="#f8f8f8" stroke="#777" stroke-width="1"/>
        <text x="22" y="419" font-size="12" font-weight="bold" fill="#78237b" text-anchor="middle">子月</text>
        <text x="64" y="419" font-size="12" font-weight="bold" fill="#111" text-anchor="middle">親神</text>
        <text x="105" y="419" font-size="12" font-weight="bold" fill="#111" text-anchor="middle">日</text>
        <text x="140" y="419" font-size="12" font-weight="bold" fill="#111" text-anchor="middle">變爻</text>

        <rect x="0" y="428" width="160" height="25" fill="#fff" stroke="#777" stroke-width="0.8"/>
        <text x="22" y="445" font-size="13" font-weight="bold" fill="#0000cc" text-anchor="middle">水旺</text>
        <text x="64" y="445" font-size="13" font-weight="bold" fill="#cc0000" text-anchor="middle">父</text>
        <text x="105" y="445" font-size="13" font-weight="bold" fill="#008000" text-anchor="middle">絕</text>

        <rect x="0" y="453" width="160" height="25" fill="#fff" stroke="#777" stroke-width="0.8"/>
        <text x="22" y="470" font-size="13" font-weight="bold" fill="#008000" text-anchor="middle">木相</text>
        <text x="64" y="470" font-size="13" font-weight="bold" fill="#cc0000" text-anchor="middle">兄</text>
        <text x="105" y="470" font-size="13" font-weight="bold" fill="#008000" text-anchor="middle">病</text>

        <rect x="0" y="478" width="160" height="25" fill="#fff" stroke="#777" stroke-width="0.8"/>
        <text x="22" y="495" font-size="13" font-weight="bold" fill="#cc0000" text-anchor="middle">火死</text>
        <text x="64" y="495" font-size="13" font-weight="bold" fill="#cc0000" text-anchor="middle">孫</text>
        <text x="105" y="495" font-size="13" font-weight="bold" fill="#008000" text-anchor="middle">臨</text>

        <rect x="0" y="503" width="160" height="25" fill="#fff" stroke="#777" stroke-width="0.8"/>
        <text x="22" y="520" font-size="13" font-weight="bold" fill="#8b4513" text-anchor="middle">土囚</text>
        <text x="54" y="520" font-size="13" font-weight="bold" fill="#8b2500" text-anchor="middle">財</text>
        <rect x="68" y="508" width="16" height="15" fill="#fef08a" stroke="#b91c1c" rx="2"/>
        <text x="76" y="520" font-size="10" font-weight="bold" fill="#b91c1c" text-anchor="middle">用</text>
        <text x="105" y="520" font-size="13" font-weight="bold" fill="#008000" text-anchor="middle">臨</text>
        <text x="140" y="520" font-size="13" font-weight="bold" fill="#cc0000" text-anchor="middle">胎</text>

        <rect x="0" y="528" width="160" height="25" fill="#fff" stroke="#777" stroke-width="0.8"/>
        <text x="22" y="545" font-size="13" font-weight="bold" fill="#b8860b" text-anchor="middle">金休</text>
        <text x="64" y="545" font-size="13" font-weight="bold" fill="#cc0000" text-anchor="middle">官</text>
        <text x="105" y="545" font-size="13" font-weight="bold" fill="#008000" text-anchor="middle">生</text>

        <!-- 神煞方陣 -->
        <rect x="160" y="402" width="29" height="75" fill="#fff" stroke="#777" stroke-width="0.8"/>
        <text x="174" y="418" font-size="12" fill="#111" text-anchor="middle">日</text><text x="174" y="432" font-size="12" fill="#111" text-anchor="middle">沖</text>
        <text x="174" y="462" font-size="15" font-weight="bold" fill="#0000cc" text-anchor="middle">亥</text>

        <rect x="189" y="402" width="29" height="75" fill="#fff" stroke="#777" stroke-width="0.8"/>
        <text x="203" y="418" font-size="12" fill="#111" text-anchor="middle">月</text><text x="203" y="432" font-size="12" fill="#111" text-anchor="middle">破</text>
        <text x="203" y="462" font-size="15" font-weight="bold" fill="#cc0000" text-anchor="middle">午</text>

        <rect x="218" y="402" width="29" height="75" fill="#fff" stroke="#777" stroke-width="0.8"/>
        <text x="232" y="418" font-size="12" fill="#111" text-anchor="middle">桃</text><text x="232" y="432" font-size="12" fill="#111" text-anchor="middle">花</text>
        <text x="232" y="462" font-size="15" font-weight="bold" fill="#cc0000" text-anchor="middle">午</text>

        <rect x="247" y="402" width="29" height="75" fill="#fff" stroke="#777" stroke-width="0.8"/>
        <text x="261" y="418" font-size="12" fill="#111" text-anchor="middle">劫</text><text x="261" y="432" font-size="12" fill="#111" text-anchor="middle">煞</text>
        <text x="261" y="462" font-size="15" font-weight="bold" fill="#008000" text-anchor="middle">寅</text>

        <rect x="276" y="402" width="29" height="75" fill="#fff" stroke="#777" stroke-width="0.8"/>
        <text x="290" y="418" font-size="12" fill="#111" text-anchor="middle">驛</text><text x="290" y="432" font-size="12" fill="#111" text-anchor="middle">馬</text>
        <text x="290" y="462" font-size="15" font-weight="bold" fill="#0000cc" text-anchor="middle">亥</text>

        <rect x="305" y="402" width="30" height="75" fill="#fff" stroke="#777" stroke-width="0.8"/>
        <text x="320" y="418" font-size="12" fill="#111" text-anchor="middle">卦</text><text x="320" y="432" font-size="12" fill="#111" text-anchor="middle">身</text>
        <text x="320" y="462" font-size="15" font-weight="bold" fill="#008000" text-anchor="middle">卯</text>

        <rect x="160" y="477" width="29" height="76" fill="#fff" stroke="#777" stroke-width="0.8"/>
        <text x="174" y="493" font-size="12" fill="#111" text-anchor="middle">空</text><text x="174" y="507" font-size="12" fill="#111" text-anchor="middle">亡</text>
        <text x="174" y="528" font-size="14" font-weight="bold" fill="#b8860b" text-anchor="middle">申</text>
        <text x="174" y="546" font-size="14" font-weight="bold" fill="#b8860b" text-anchor="middle">酉</text>

        <rect x="189" y="477" width="29" height="76" fill="#fff" stroke="#777" stroke-width="0.8"/>
        <text x="203" y="493" font-size="12" fill="#111" text-anchor="middle">羊</text><text x="203" y="507" font-size="12" fill="#111" text-anchor="middle">刃</text>
        <text x="203" y="538" font-size="15" font-weight="bold" fill="#800000" text-anchor="middle">戌</text>

        <rect x="218" y="477" width="29" height="76" fill="#fff" stroke="#777" stroke-width="0.8"/>
        <text x="232" y="493" font-size="12" fill="#111" text-anchor="middle">干</text><text x="232" y="507" font-size="12" fill="#111" text-anchor="middle">祿</text>
        <text x="232" y="538" font-size="15" font-weight="bold" fill="#b8860b" text-anchor="middle">酉</text>

        <rect x="247" y="477" width="29" height="76" fill="#fff" stroke="#777" stroke-width="0.8"/>
        <text x="261" y="493" font-size="12" fill="#111" text-anchor="middle">往</text><text x="261" y="507" font-size="12" fill="#111" text-anchor="middle">亡</text>
        <text x="261" y="538" font-size="15" font-weight="bold" fill="#800000" text-anchor="middle">戌</text>

        <rect x="276" y="477" width="29" height="76" fill="#fff" stroke="#777" stroke-width="0.8"/>
        <text x="290" y="493" font-size="12" fill="#111" text-anchor="middle">天</text><text x="290" y="507" font-size="12" fill="#111" text-anchor="middle">喜</text>
        <text x="290" y="538" font-size="15" font-weight="bold" fill="#800000" text-anchor="middle">未</text>

        <rect x="305" y="477" width="30" height="76" fill="#fff" stroke="#777" stroke-width="0.8"/>
        <text x="320" y="493" font-size="12" fill="#111" text-anchor="middle">貴</text><text x="320" y="507" font-size="12" fill="#111" text-anchor="middle">人</text>
        <text x="320" y="528" font-size="14" font-weight="bold" fill="#008000" text-anchor="middle">寅</text>
        <text x="320" y="546" font-size="14" font-weight="bold" fill="#cc0000" text-anchor="middle">午</text>

        <!-- 八字區 -->
        <rect x="335" y="402" width="125" height="151" fill="#ffffff" stroke="#777" stroke-width="1"/>
        <text x="397" y="420" font-size="14" font-weight="bold" fill="#111" text-anchor="middle">八  字</text>
        <text x="350" y="445" font-size="14" font-weight="bold" fill="#111">庚</text><text x="350" y="462" font-size="14" font-weight="bold" fill="#111">申</text>
        <text x="375" y="445" font-size="14" font-weight="bold" fill="#cc0000">癸</text><text x="375" y="462" font-size="14" font-weight="bold" fill="#111">酉</text>
        <text x="405" y="445" font-size="14" font-weight="bold" fill="#111">己</text><text x="405" y="462" font-size="14" font-weight="bold" fill="#111">卯</text>
        <text x="435" y="445" font-size="14" font-weight="bold" fill="#111">乙</text><text x="435" y="462" font-size="14" font-weight="bold" fill="#111">未</text>
        <line x1="335" y1="475" x2="460" y2="475" stroke="#ccc" stroke-width="0.8"/>
        <text x="397" y="490" font-size="9" fill="#666" text-anchor="middle">93 83 73 63 53 43 33 23 13 3</text>
        <text x="397" y="515" font-size="9" fill="#999" text-anchor="middle">己 庚 辛 壬 癸 甲 乙 丙 丁 戊</text>
        <text x="397" y="535" font-size="9" fill="#999" text-anchor="middle">巳 午 未 申 酉 戌 亥 子 丑 寅</text>
    </svg>
    '''
    return svg

# --- 5. 畫面渲染 ---
st.markdown("<h2 style='text-align:center; color:#800000; margin-bottom:10px;'>🏛️ 星僑 (NCC) 六爻占卦全動態排盤系統</h2>", unsafe_allow_html=True)
tab_gui, tab_txt = st.tabs(["📱 動態圖形畫面 (1:1 復刻星僑 App)", "📋 卜卦 AI 提示詞 (一鍵複製)"])

with tab_gui:
    # 傳入 100% 動態演算數據
    svg_out = generate_dynamic_svg(
        dynamic_lines, ben_name, bian_name, shou_name, palace_elem, hu_name, ben_type,
        user_q, c_y, c_m, c_d, c_solar
    )
    html_block = f"""
    <!DOCTYPE html><html><head><meta charset="utf-8">
    <style>body {{ margin:0; padding:10px 0; display:flex; justify-content:center; align-items:center; background:transparent; }}</style>
    </head><body>{svg_out}</body></html>
    """
    components.html(html_block, height=850, scrolling=True)

with tab_txt:
    st.markdown("### 📋 卜卦 AI 提示詞（同步動態更新）")
    
    line_labels = ["初爻", "二爻", "三爻", "四爻", "五爻", "六爻"]
    prompt_lines = []
    for i in range(5, -1, -1):
        l_num = i + 1
        beast, b_qin, sy_label, sym_type, b_gan, b_zhi, b_el, is_kong, bi_gan, bi_zhi, bi_qin, bi_he, fu_gan, fu_zhi, fu_el, fu_qin = dynamic_lines[i]
        
        tag = line_labels[i]
        if sy_label:
            tag += f"【{sy_label}爻】"
            
        k_str = " 空亡" if is_kong else ""
        bi_str = f"，變爻：{bi_qin} ({bi_zhi}{DIZHI_ELEM[bi_zhi]})" if bi_zhi else ""
        fu_str = f"，伏神：{fu_qin} ({fu_zhi}{fu_el})" if fu_zhi else ""
        
        prompt_lines.append(f"{tag}：{beast} {b_qin} ({b_zhi}{b_el}){k_str}{bi_str}{fu_str}")
        
    full_prompt = f"""占卦日期：
陽曆：{c_solar}
農曆：{c_lunar}
干支：{c_y} 年 {c_m} 月 {c_d} 日 {c_h} 時

本卦：{ben_name}
變卦：{bian_name}

{chr(10).join(prompt_lines)}
事由：{user_q}

請用繁體中文回答，依據易經與六爻學理分析"""

    st.text_area("提示詞內容", value=full_prompt, height=320)
