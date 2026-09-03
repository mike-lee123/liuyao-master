# -*- coding: utf-8 -*-
"""
六爻神斷 · 回答觀眾專用 App
整合：三數起卦 + 星僑NCC純圖形排盤 + 四維經典全息神斷 + 超深入生活化轉譯 + 原生 Google Gemini API 一鍵解盤
"""
import streamlit as st
import streamlit.components.v1 as components
from datetime import datetime
import requests
import json

st.set_page_config(
    page_title="六爻神斷 · 回答觀眾專用 App",
    page_icon="☯️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 側邊控制欄 ---
st.sidebar.markdown("## 🎙️ 觀眾提問與起卦設定")
viewer_name = st.sidebar.text_input("觀眾稱呼 / 姓名", value="陳小姐")
matter_type = st.sidebar.selectbox("問事類別", ["尋找遺失物", "身體健康與注意事項", "事業轉職與職場", "感情婚姻與桃花", "投資求財", "綜合運勢"])
user_q = st.sidebar.text_input("具體問題簡述", value="悠遊卡遺失地點" if matter_type == "尋找遺失物" else "問身體健康注意事項")

st.sidebar.markdown("---")
st.sidebar.markdown("### 🔢 觀眾提供的三組數字")
preset_choice = st.sidebar.selectbox("載入經典卦例", [
    "自訂輸入三組數字",
    "案例 1：悠遊卡遺失 (29 34 19 ➔ 澤風大過 之 澤天夬)",
    "案例 2：問健康注意事項 (54 12 65 ➔ 雷水解 之 澤水困)"
])

if preset_choice == "案例 1：悠遊卡遺失 (29 34 19 ➔ 澤風大過 之 澤天夬)":
    init_n1, init_n2, init_n3 = 29, 34, 19
    c_solar, c_y, c_m, c_d, c_h = "2019/12/10 22:00", "己亥", "丙子", "辛巳", "己亥"
    c_kong = "申酉"
elif preset_choice == "案例 2：問健康注意事項 (54 12 65 ➔ 雷水解 之 澤水困)":
    init_n1, init_n2, init_n3 = 54, 12, 65
    c_solar, c_y, c_m, c_d, c_h = "2026/09/03 16:21", "丙午", "丙申", "庚辰", "甲申"
    c_kong = "申酉"
else:
    init_n1, init_n2, init_n3 = 29, 34, 19
    c_solar = datetime.now().strftime("%Y/%m/%d %H:%M")
    c_y, c_m, c_d, c_h = "丙午", "丙申", "庚辰", "甲申"
    c_kong = "申酉"

col_n1, col_n2, col_n3 = st.sidebar.columns(3)
n1 = col_n1.number_input("第1組(下)", value=init_n1, min_value=1, step=1)
n2 = col_n2.number_input("第2組(上)", value=init_n2, min_value=1, step=1)
n3 = col_n3.number_input("第3組(動)", value=init_n3, min_value=1, step=1)

# --- 核心排盤資料結構 ---
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

GUA_64 = {
    (1,1): ("乾為天", "乾為天", "金", 6, "本宮"), (1,5): ("天風姤", "乾為天", "金", 1, "一世"),
    (1,7): ("天山遯", "乾為天", "金", 2, "二世"), (1,8): ("天地否", "乾為天", "金", 3, "三世"),
    (5,8): ("風地觀", "乾為天", "金", 4, "四世"), (7,8): ("山地剝", "乾為天", "金", 5, "五世"),
    (3,8): ("火地晉", "乾為天", "金", 4, "游"),   (3,1): ("火天大有", "乾為天", "金", 3, "歸"),
    (6,6): ("坎為水", "坎為水", "水", 6, "本宮"), (6,2): ("水澤節", "坎為水", "水", 1, "一世"),
    (6,4): ("水雷屯", "坎為水", "水", 2, "二世"), (6,3): ("水火既濟", "坎為水", "水", 3, "三世"),
    (2,3): ("澤火革", "坎為水", "水", 4, "四世"), (4,3): ("雷火豐", "坎為水", "水", 5, "五世"),
    (8,3): ("地火明夷", "坎為水", "水", 4, "游"), (8,6): ("地水師", "坎為水", "水", 3, "歸"),
    (7,7): ("艮為山", "艮為山", "土", 6, "本宮"), (7,3): ("山火賁", "艮為山", "土", 1, "一世"),
    (7,1): ("山天大畜", "艮為山", "土", 2, "二世"), (7,2): ("山澤損", "艮為山", "土", 3, "三世"),
    (3,2): ("火澤睽", "艮為山", "土", 4, "四世"), (1,2): ("天澤履", "艮為山", "土", 5, "五世"),
    (5,2): ("風澤中孚", "艮為山", "土", 4, "游"), (5,7): ("風山漸", "艮為山", "土", 3, "歸"),
    (4,4): ("震為雷", "震為雷", "木", 6, "本宮"), (4,8): ("雷地豫", "震為雷", "木", 1, "一世"),
    (4,6): ("雷水解", "震為雷", "木", 2, "二世"), (4,5): ("雷風恆", "震為雷", "木", 3, "三世"),
    (8,5): ("地風升", "震為雷", "木", 4, "四世"), (6,5): ("水風井", "震為雷", "木", 5, "五世"),
    (2,5): ("澤風大過", "震為雷", "木", 4, "游"), (2,4): ("澤雷隨", "震為雷", "木", 3, "歸"),
    (5,5): ("巽為風", "巽為風", "木", 6, "本宮"), (5,1): ("風天小畜", "巽為風", "木", 1, "一世"),
    (5,3): ("風火家人", "巽為風", "木", 2, "二世"), (5,4): ("風雷益", "巽為風", "木", 3, "三世"),
    (1,4): ("天雷無妄", "巽為風", "木", 4, "四世"), (3,4): ("火雷噬嗑", "巽為風", "木", 5, "五世"),
    (7,4): ("山雷頤", "巽為風", "木", 4, "游"),   (7,5): ("山風蠱", "巽為風", "木", 3, "歸"),
    (3,3): ("離為火", "離為火", "火", 6, "本宮"), (3,7): ("火山旅", "離為火", "火", 1, "一世"),
    (3,5): ("火風鼎", "離為火", "火", 2, "二世"), (3,6): ("火水未濟", "離為火", "火", 3, "三世"),
    (7,6): ("山水蒙", "離為火", "火", 4, "四世"), (5,6): ("風水渙", "離為火", "火", 5, "五世"),
    (1,6): ("天水訟", "離為火", "火", 4, "游"),   (1,3): ("天火同人", "離為火", "火", 3, "歸"),
    (8,8): ("坤為地", "坤為地", "土", 6, "本宮"), (8,4): ("地雷復", "坤為地", "土", 1, "一世"),
    (8,2): ("地澤臨", "坤為地", "土", 2, "二世"), (8,1): ("地天泰", "坤為地", "土", 3, "三世"),
    (4,1): ("雷天大壯", "坤為地", "土", 4, "四世"), (2,1): ("澤天夬", "坤為地", "土", 5, "五世"),
    (6,1): ("水天需", "坤為地", "土", 4, "游"),   (6,8): ("水地比", "坤為地", "土", 3, "歸"),
    (2,2): ("兌為澤", "兌為澤", "金", 6, "本宮"), (2,6): ("澤水困", "兌為澤", "金", 1, "一世"),
    (2,8): ("澤地萃", "兌為澤", "金", 2, "二世"), (2,7): ("澤山咸", "兌為澤", "金", 3, "三世"),
    (6,7): ("水山蹇", "兌為澤", "金", 4, "四世"), (8,7): ("地山謙", "兌為澤", "金", 5, "五世"),
    (4,7): ("雷山小過", "兌為澤", "金", 4, "游"), (4,2): ("雷澤歸妹", "兌為澤", "金", 3, "歸")
}

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

# --- 核心排盤演算法運算 ---
lower_id = n1 % 8 if (n1 % 8) != 0 else 8
upper_id = n2 % 8 if (n2 % 8) != 0 else 8
moving_line = n3 % 6 if (n3 % 6) != 0 else 6

ben_name, shou_name, palace_elem, shi_pos, ben_type = GUA_64.get((upper_id, lower_id), ("自訂卦", "乾為天", "金", 3, "世卦"))
ying_pos = (shi_pos + 3) % 6 or 6
ben_lines = BAGUA[lower_id]["lines"] + BAGUA[upper_id]["lines"]

bian_lines = list(ben_lines)
bian_lines[moving_line - 1] = 1 - bian_lines[moving_line - 1]
bian_lower_lines = bian_lines[:3]
bian_upper_lines = bian_lines[3:]
bian_lower_id = next(k for k, v in BAGUA.items() if v["lines"] == bian_lower_lines)
bian_upper_id = next(k for k, v in BAGUA.items() if v["lines"] == bian_upper_lines)
bian_name, _, _, _, _ = GUA_64.get((bian_upper_id, bian_lower_id), ("變卦", "乾為天", "金", 3, "世卦"))

hu_lower_lines = [ben_lines[1], ben_lines[2], ben_lines[3]]
hu_upper_lines = [ben_lines[2], ben_lines[3], ben_lines[4]]
hu_lower_id = next(k for k, v in BAGUA.items() if v["lines"] == hu_lower_lines)
hu_upper_id = next(k for k, v in BAGUA.items() if v["lines"] == hu_upper_lines)
hu_name, _, _, _, _ = GUA_64.get((hu_upper_id, hu_lower_id), ("互卦", "乾為天", "金", 3, "世卦"))

l_gan = BAGUA[lower_id]["inner_gan"]
u_gan = BAGUA[upper_id]["outer_gan"]
ben_ganzhi = [f"{l_gan}{b}" for b in BAGUA[lower_id]["inner"]] + [f"{u_gan}{b}" for b in BAGUA[upper_id]["outer"]]

bl_gan = BAGUA[bian_lower_id]["inner_gan"]
bu_gan = BAGUA[bian_upper_id]["outer_gan"]
bian_ganzhi = [f"{bl_gan}{b}" for b in BAGUA[bian_lower_id]["inner"]] + [f"{bu_gan}{b}" for b in BAGUA[bian_upper_id]["outer"]]

day_gan = c_d[0] if len(c_d) > 0 else "辛"
liushen = get_liushen(day_gan)

pure_branches = PURE_GUA.get(shou_name, PURE_GUA["乾為天"])
present_qins = set()
for gz in ben_ganzhi:
    present_qins.add(get_liuqin(palace_elem, DIZHI_ELEM[gz[1]]))

fushen_dict = {}
for idx, (p_gz, p_elem) in enumerate(pure_branches):
    q = get_liuqin(palace_elem, p_elem)
    if q not in present_qins and (idx + 1) not in fushen_dict:
        fushen_dict[idx + 1] = (q, p_gz[0], p_gz[1], p_elem)

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
    sym_type = ("dong_yin" if ben_lines[i] == 0 else "dong_yang") if is_mv else ("yang" if ben_lines[i] == 1 else "yin")
    
    bi_gan, bi_zhi, bi_qin, bi_he = "", "", "", ""
    if is_mv:
        bigz = bian_ganzhi[i]
        bi_gan, bi_zhi = bigz[0], bigz[1]
        bi_el = DIZHI_ELEM[bi_zhi]
        bi_qin = get_liuqin(palace_elem, bi_el)
        if (b_zhi, bi_zhi) in [("丑","子"),("子","丑"),("辰","酉"),("酉","辰"),("寅","亥"),("亥","寅"),("卯","戌"),("戌","卯"),("巳","申"),("申","巳"),("午","未"),("未","午")]:
            bi_he = "合"
            
    fu_gan, fu_zhi, fu_el, fu_qin = "", "", "", ""
    if l_num in fushen_dict:
        fu_qin, fu_gan, fu_zhi, fu_el = fushen_dict[l_num]
        
    dynamic_lines.append((
        beast, b_qin, sy_label, sym_type, b_gan, b_zhi, b_el, is_kong,
        bi_gan, bi_zhi, bi_qin, bi_he, fu_gan, fu_zhi, fu_el, fu_qin
    ))

# --- SVG 產生器 ---
def generate_ncc_svg():
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
    headers = [(16, "六", "獸"), (48, "六", "親"), (78, "世", "應"), (112, "NCC", "星僑"), (155, "裝", "卦"), (201, "變", "卦"), (240, "六", "親"), (278, "伏", "神"), (315, "六", "親")]
    for x, t1, t2 in headers:
        svg += f'<text x="{x}" y="55" font-size="12" font-weight="bold" fill="#111" text-anchor="middle">{t1}</text>'
        svg += f'<text x="{x}" y="68" font-size="12" font-weight="bold" fill="#111" text-anchor="middle">{t2}</text>'

    svg += f'''
        <text x="343" y="55" font-size="13" fill="#111" text-anchor="middle">日</text>
        <text x="343" y="69" font-size="12" font-weight="bold" fill="#111" text-anchor="middle">{c_d}</text>
        <text x="369" y="55" font-size="13" fill="#111" text-anchor="middle">月</text>
        <text x="369" y="69" font-size="12" font-weight="bold" fill="#111" text-anchor="middle">{c_m}</text>
        <text x="395" y="55" font-size="13" fill="#111" text-anchor="middle">年</text>
        <text x="395" y="69" font-size="12" font-weight="bold" fill="#111" text-anchor="middle">{c_y}</text>
        <rect x="330" y="72" width="80" height="18" fill="#ffffff" stroke="#777" stroke-width="0.8"/>
        <text x="370" y="85" font-size="11" fill="#cc0000" font-weight="bold" text-anchor="middle">{c_solar.split(' ')[0]}</text>
    '''

    row_h, y_start = 55, 72
    for idx, row in enumerate(reversed(dynamic_lines)):
        y = y_start + idx * row_h
        beast, qin, sy, sym, z_gan, z_zhi, z_el, kong, bi_gan, bi_zhi, bi_qin, he, fu_gan, fu_zhi, fu_el, fu_qin = row
        svg += f'<line x1="0" y1="{y+row_h}" x2="330" y2="{y+row_h}" stroke="#777" stroke-width="1"/>'
        svg += f'<text x="16" y="{y+32}" font-size="15" font-weight="bold" fill="#800080" text-anchor="middle">{beast[0]}</text>'
        svg += f'<text x="16" y="{y+46}" font-size="15" font-weight="bold" fill="#800080" text-anchor="middle">{beast[1]}</text>'
        svg += f'<text x="48" y="{y+32}" font-size="15" font-weight="bold" fill="#8b2500" text-anchor="middle">{qin[0]}</text>'
        svg += f'<text x="48" y="{y+46}" font-size="15" font-weight="bold" fill="#8b2500" text-anchor="middle">{qin[1]}</text>'
        if sy:
            svg += f'<text x="78" y="{y+36}" font-size="18" font-weight="bold" fill="#cc0000" text-anchor="middle">{sy}</text>'

        if sym == "yang":
            svg += f'<line x1="98" y1="{y+38}" x2="126" y2="{y+20}" stroke="#0000cc" stroke-width="4.5" stroke-linecap="round"/>'
        elif sym == "yin":
            svg += f'<line x1="96" y1="{y+40}" x2="110" y2="{y+28}" stroke="#0000cc" stroke-width="4.5" stroke-linecap="round"/>'
            svg += f'<line x1="114" y1="{y+28}" x2="128" y2="{y+16}" stroke="#0000cc" stroke-width="4.5" stroke-linecap="round"/>'
        elif sym == "dong_yin":
            svg += f'<line x1="98" y1="{y+18}" x2="126" y2="{y+42}" stroke="#0000cc" stroke-width="5" stroke-linecap="round"/>'
            svg += f'<line x1="98" y1="{y+42}" x2="126" y2="{y+18}" stroke="#0000cc" stroke-width="5" stroke-linecap="round"/>'
        elif sym == "dong_yang":
            svg += f'<circle cx="112" cy="{y+30}" r="11" stroke="#cc0000" stroke-width="4" fill="none"/>'

        svg += f'<text x="165" y="{y+22}" font-size="13" font-weight="bold" fill="#008000" text-anchor="middle">{z_gan}</text>'
        svg += f'<text x="146" y="{y+30}" font-size="18" font-weight="bold" fill="#000080" text-anchor="middle">{z_zhi}</text>'
        svg += f'<text x="146" y="{y+48}" font-size="13" font-weight="bold" fill="#8b2500" text-anchor="middle">{z_el}</text>'
        if kong:
            svg += f'<rect x="158" y="{y+24}" width="15" height="15" fill="#f0f0f0" stroke="#777" stroke-width="1" rx="2"/>'
            svg += f'<text x="165.5" y="{y+35.5}" font-size="10" fill="#444" font-weight="bold" text-anchor="middle">空</text>'

        if bi_zhi:
            svg += f'<text x="210" y="{y+22}" font-size="13" font-weight="bold" fill="#008000" text-anchor="middle">{bi_gan}</text>'
            svg += f'<text x="190" y="{y+30}" font-size="18" font-weight="bold" fill="#cc0000" text-anchor="middle">{bi_zhi}</text>'
            if he:
                svg += f'<text x="190" y="{y+48}" font-size="13" font-weight="bold" fill="#111" text-anchor="middle">{he}</text>'
            svg += f'<text x="240" y="{y+32}" font-size="15" font-weight="bold" fill="#cc0000" text-anchor="middle">{bi_qin[0]}</text>'
            svg += f'<text x="240" y="{y+46}" font-size="15" font-weight="bold" fill="#cc0000" text-anchor="middle">{bi_qin[1]}</text>'

        if fu_zhi:
            svg += f'<text x="290" y="{y+22}" font-size="13" font-weight="bold" fill="#008000" text-anchor="middle">{fu_gan}</text>'
            svg += f'<text x="270" y="{y+30}" font-size="17" font-weight="bold" fill="#008000" text-anchor="middle">{fu_zhi}</text>'
            svg += f'<text x="270" y="{y+48}" font-size="13" font-weight="bold" fill="#8b2500" text-anchor="middle">{fu_el}</text>'
            svg += f'<text x="315" y="{y+32}" font-size="15" font-weight="bold" fill="#008000" text-anchor="middle">{fu_qin[0]}</text>'
            svg += f'<text x="315" y="{y+46}" font-size="15" font-weight="bold" fill="#008000" text-anchor="middle">{fu_qin[1]}</text>'

    for cx in [32, 64, 92, 132, 178, 224, 256, 300, 330]:
        svg += f'<line x1="{cx}" y1="42" x2="{cx}" y2="402" stroke="#777" stroke-width="1"/>'

    b_svg = make_vert_svg(bian_name, 343, 185, font_size=15, color="#cc0000", line_gap=20)
    be_svg = make_vert_svg(ben_name, 369, 185, font_size=15, color="#000080", line_gap=20)
    s_svg = make_vert_svg(shou_name, 396, 170, font_size=14, color="#cc0000", line_gap=18)
    h_svg = make_vert_svg(hu_name, 396, 325, font_size=14, color="#78237b", line_gap=18)
    m_svg = make_vert_svg(user_q, 435, 105, font_size=13, color="#78237b", line_gap=20, max_chars=8)

    svg += f'''
        <rect x="330" y="90" width="26" height="312" fill="#ffffff" stroke="#777" stroke-width="1"/>
        <text x="343" y="115" font-size="13" font-weight="bold" fill="#111" text-anchor="middle">變</text>
        <text x="343" y="133" font-size="13" font-weight="bold" fill="#111" text-anchor="middle">卦</text>
        {b_svg}

        <rect x="356" y="90" width="26" height="312" fill="#ffffff" stroke="#777" stroke-width="1"/>
        <text x="369" y="115" font-size="13" font-weight="bold" fill="#111" text-anchor="middle">本</text>
        <rect x="358" y="125" width="22" height="18" fill="#1d4ed8" rx="2"/>
        <text x="369" y="138" font-size="12" font-weight="bold" fill="#ffffff" text-anchor="middle">{ben_type}</text>
        {be_svg}

        <rect x="382" y="90" width="28" height="156" fill="#ffffff" stroke="#777" stroke-width="1"/>
        <text x="396" y="112" font-size="13" font-weight="bold" fill="#111" text-anchor="middle">首</text>
        <rect x="385" y="122" width="22" height="18" fill="#8b4513" rx="2"/>
        <text x="396" y="135" font-size="12" font-weight="bold" fill="#ffffff" text-anchor="middle">{palace_elem}</text>
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

# --- 頁面標籤頁配置 ---
st.markdown("<h2 style='text-align:center; color:#7f1d1d; margin-bottom:5px;'>🎙️ 六爻神斷 · 回答觀眾專用 App</h2>", unsafe_allow_html=True)
st.markdown(f"<p style='text-align:center; color:#666;'>當前連線諮詢觀眾：<b>{viewer_name}</b> ｜ 提問：<b>{user_q}</b></p>", unsafe_allow_html=True)

tab_report, tab_pan, tab_prompt, tab_ai = st.tabs([
    "🎙️ 回答觀眾大師說詞 (生活化轉譯)",
    "📱 星僑 (NCC) 手機純圖形排盤",
    "📋 頂級生活化 Prompt (一鍵複製)",
    "⚡ Google Gemini AI 一鍵即時批卦"
])

# 準備頂級 Prompt 內容
line_labels = ["初爻", "二爻", "三爻", "四爻", "五爻", "六爻"]
p_lines = []
for i in range(5, -1, -1):
    l_num = i + 1
    beast, b_qin, sy_label, sym_type, b_gan, b_zhi, b_el, is_kong, bi_gan, bi_zhi, bi_qin, bi_he, fu_gan, fu_zhi, fu_el, fu_qin = dynamic_lines[i]
    tag = line_labels[i] + (f"【{sy_label}爻】" if sy_label else "")
    k_str = " 空亡" if is_kong else ""
    bi_str = f"，變爻：{bi_qin} ({bi_zhi}{DIZHI_ELEM[bi_zhi]})" if bi_zhi else ""
    fu_str = f"，伏神：{fu_qin} ({fu_zhi}{fu_el})" if fu_zhi else ""
    p_lines.append(f"{tag}：{beast} {b_qin} ({b_zhi}{b_el}){k_str}{bi_str}{fu_str}")

full_prompt_text = f"""【角色設定】
你是一位精通納甲六爻與象數易學的國學宗師，正透過線上直播節目為觀眾「{viewer_name}」解答疑惑。你的解說風格溫暖、極具親和力、一針見血、充滿生活畫面感，絕不說空洞的術數黑話，全篇轉譯為現代生活場景。

【占卦資訊】
觀眾稱呼：{viewer_name} ｜ 問事主題：{user_q}
占卦時間：{c_solar} ｜ 干支：{c_y}年 {c_m}月 {c_d}日 {c_h}時 ｜ 旬空：{c_kong}
本卦：{ben_name}（{palace_elem}宮） ｜ 變卦：{bian_name} ｜ 互卦：{hu_name} ｜ 首卦：{shou_name}

【六爻排盤詳情】
{chr(10).join(p_lines)}

────────────────────────────────────────
【請嚴格依據以下「四維經典 × 超深入生活化轉譯」為觀眾解卦】

一、【大師開場定心丸】
開門見山給觀眾明確結果（能成/不能成、能找回/不能找回、吉或凶），讓觀眾瞬間安心。

二、【生活場景逼真還原】
結合《易經64卦卦圖象解》與動爻，具體描摹當事人在家裡、辦公室、交通工具上的日常行為與環境細節（如包包黑洞底層、沙發夾縫、出門急促等）。

三、【身心痛點精確共鳴】
點出當事人最近的身體痛點（肩頸僵硬、喉嚨乾、睡眠品質、腸胃排便）與內心焦慮糾結點。

四、【四維經典深度破局】
1. 野鶴老人：論用神旺衰與動變回頭合，推算精確應期（何日何時見分曉）。
2. 高島易斷：剖析當前時空機先與謀略對策。
3. 易經經文：引述動爻爻辭，給予處世智慧指引。

五、【超實用生活處方箋】
提供 2~3 條明天就能立刻執行的日常行動清單（收納排查方位、生活習慣改善、調養心法）。
請全程使用繁體中文，語氣溫暖、直擊痛點！"""

# ==================== 標籤 1：回答觀眾大師說詞 ====================
with tab_report:
    st.markdown(f"### 📢 大師親口開解：回答【{viewer_name}】問【{user_q}】")
    
    if "悠遊卡" in user_q or "遺失" in user_q or "失物" in matter_type:
        st.markdown(f"""
        > **【大師開場定心丸】：**
        > 「{viewer_name}，先請您大大地鬆一口氣！根據這張卦盤（澤風大過變澤天夬，初爻動），用神妻財丑土逢日辰生扶，底氣非常旺。**我可以直接給您鐵板釘釘的結論：這張卡片絕對沒有被偷，也沒有掉在路邊水溝，它毫髮無傷，100% 能找回！**」

        #### 一、生活場景逼真還原（你今天做了什麼？）
        * **包包被你塞得太滿了（大過卦）**：
          你今天出門是不是行色匆匆，心裡裝著一堆事情？大過卦就是『超載、過度緊繃』。你檢查一下你背的隨身大包包，裡面是不是塞滿了保溫瓶、摺疊傘、薄外套、化妝包或一大堆充電線雜物？
        * **卡片滑進了『黑洞夾層』**：
          你當時為了掏手機或掏鑰匙，手指不小心順手把卡片帶了出來。卡片順著重力一路滑到了**包包最底層的死角**，現在正被大衣摺疊處、或是雨傘與水壺的底部死死壓住！平常隨手伸進去摸是摸不到的。
        * **車輛座椅的『死亡夾縫』**：
          卦圖中明現『官人乘車』與『文書在地』。回想一下你今天坐公車、捷運或計程車時，有沒有把卡片隨手放在大腿上？當你起身時，卡片就順著臀部滑進了**座椅椅墊與安全帶扣環之間那個又黑又窄的夾縫裡**（子丑六合之象，被夾得緊緊的）！

        #### 二、高島易斷與易經的破局心態
        * **高島易斷曰**：『物在暗昧與明處交界，多因倉促被衣物包袱遮掩。』不要急著跑去掛失辦新卡，那只會白花錢！
        * **易經初爻爻辭**：**『藉用白茅，無咎。』**
          白茅是柔軟的草。這是在提醒你：**不要心浮氣躁！不要生氣地把東西亂甩！** 請放慢呼吸，溫柔、耐心地把包包裡的東西一件一件拿出來，去摸索底部襯布，必然失而復得！

        #### 三、超實用找回處方箋（今晚立刻這樣做）
        1. **第一步（清空包包）**：回家把今天背的包包倒在床上，翻開內層拉鍊暗袋，抖一抖內裡夾層。
        2. **第二步（檢查車輛座椅與玄關）**：若有開車或搭車，拿手機手電筒照一下車座縫隙；或者看家門口穿鞋椅旁邊的地面死角。
        3. **精確應期**：子丑六合，逢沖即出。今天**子時（晚上11點）前**細找，或者**明天中午（午時）**，卡片必定現身！
        """)
    elif "健康" in user_q or "身體" in user_q or "健康" in matter_type:
        st.markdown(f"""
        > **【大師開場定心丸】：**
        > 「{viewer_name}，請先放寬心！世爻辰土臨日辰自旺，這代表您的先天體質與腸胃底子其實非常好，元氣充沛。**這絕對不是什麼凶險重症，目前的難受，純粹是你的身體在向你的不良生活作息發出抗議警報！**」

        #### 一、直擊你近期的身心痛點（五爻申金動化酉金進神）
        * **痛點 1：標準的『現代低頭族頸椎綜合症』**
          五爻是脖子肩頸，金旺化進神就是『骨頭硬、筋緊繃』。你最近是不是每天盯著電腦螢幕、或是躺在沙發上低頭滑手機好幾個小時？你現在伸手摸摸自己的後頸椎和兩側肩膀，是不是**緊繃僵硬得像兩塊硬石頭**？偶爾轉動脖子還會發出『喀喀』的乾澀聲響？
        * **痛點 2：辦公室冷氣病、喉嚨乾癢**
          金燥剋木（寅木月破）。你最近是不是常覺得**喉嚨乾澀、老是想清喉嚨、偶爾乾咳、早上起床鼻子過敏打噴嚏**？
        * **痛點 3：大腸乾熱，排便肚子脹**
          金主大腸，臨勾陳阻滯。你最近這幾天排便是不是很不順暢？肚子容易悶脹、代謝變慢？
        * **痛點 4：大腦關不了機、淺眠多夢**
          寅木受剋，木主自律神經。到了晚上明明身體已經累癱了，一躺上床腦袋卻像高速運轉的電腦一樣轉個不停，容易淺眠作夢，早上起來依然覺得睡不飽？

        #### 二、四維經典破局：藥爐與傾水救魚
        * **天紀圖象解密**：變卦《澤水困》圖象出現了**『藥爐』**與**『貴人傾水救旱池魚，池中青草仍有生氣』**！這說明**『有藥可救、有良醫相助』**，但必須**『待時緩進』**，不能妄想吃一顆成藥就馬上好，要給身體修復的時間。
        * **高島與易經指引**：爻辭說**『君子維有解，小人退也』**。在健康上，小人就是**『晚睡熬夜、久坐不動、把手搖飲當水喝』**的惡習！只要斬斷這些惡習，病根自除！

        #### 三、超實用生活調養處方箋（明天開始照做）
        1. **立刻補水救魚**：別再拿黑咖啡或含糖手搖飲代替水了！你現在細胞嚴重缺水，每天強迫自己喝足 2000cc 溫開水，可喝白木耳蓮子湯滋陰潤肺。
        2. **睡前放鬆頸椎**：睡前半小時把手機放到客廳，用熱毛巾熱敷後頸 15 分鐘，做簡單的仰頭擴胸拉筋，強迫大腦『關機』。
        3. **最佳體檢/就醫方位**：若需看診，適宜尋找住家**北方或南方**的大型醫療院所（肖雞或肖羊之醫師佳），按部就班調理必獲痊癒！
        """)
    else:
        st.markdown(f"""
        > **【大師開解】：**
        > 「{viewer_name}，針對您問的【{user_q}】，本卦為【{ben_name}】，第 {moving_line} 爻發動變為【{bian_name}】。
        > 
        > **1. 局勢定性（野鶴老人）**：世爻持身臨旺，說明您自身實力與底氣充足；動爻發動代表事情正面臨根本性轉折點。
        > **2. 生活場景外應（卦圖象解）**：留意周遭環境變化，行事講究節奏，切勿操之過急。
        > **3. 策略與心態（高島易斷與易經）**：爻動化進/化合，眼前看似膠著，實則蓄勢待發。順天應人，當機立斷者吉！」
        """)

# ==================== 標籤 2：星僑 NCC 圖形排盤 ====================
with tab_pan:
    st.markdown("### 📱 1:1 星僑 (NCC) 向量圖形排盤畫面")
    svg_code = generate_ncc_svg()
    html_block = f"""
    <!DOCTYPE html><html><head><meta charset="utf-8">
    <style>body {{ margin:0; padding:10px 0; display:flex; justify-content:center; align-items:center; background:transparent; }}</style>
    </head><body>{svg_code}</body></html>
    """
    components.html(html_block, height=850, scrolling=True)

# ==================== 標籤 3：頂級 AI Prompt 產生器 ====================
with tab_prompt:
    st.markdown("### 📋 頂級生活化 AI 提示詞（可直接複製至各大 AI）")
    st.text_area("生成的頂級 Prompt（一鍵全選複製）", value=full_prompt_text, height=360)

# ==================== 標籤 4：Google Gemini AI 一鍵即時批卦 ====================
with tab_ai:
    st.markdown("### ⚡ Google Gemini AI 一鍵即時批卦 (支援 Gemini 3.6 最新版)")
    st.caption("系統已鎖定 Google 最新 Gemini 3.6 系列旗艦模型，並配備連續自動容錯引擎！")
    
    default_key = st.secrets.get("GEMINI_API_KEY", "")
    
    col_k1, col_k2 = st.columns([3, 1])
    gemini_key = col_k1.text_input("輸入 Gemini API Key", value=default_key, type="password")
    st.caption("💡 優先調用：Google 官方推薦之 `gemini-3.6-flash` 極速大模型")
    
    if st.button("🚀 啟動 Gemini AI 大師現場即時批盤"):
        clean_key = gemini_key.strip() if gemini_key else ""
        
        if not clean_key:
            st.warning("⚠️ 請先輸入您的 Gemini API Key！")
        else:
            with st.spinner("🔍 正在連線 Google 最新 Gemini 3.6 引擎推演卦理..."):
                try:
                    # 1. 取得帳號可用模型清單
                    list_url = f"https://generativelanguage.googleapis.com/v1beta/models?key={clean_key}"
                    list_resp = requests.get(list_url, timeout=15)
                    
                    usable_models = []
                    if list_resp.status_code == 200:
                        models_data = list_resp.json().get("models", [])
                        usable_models = [
                            m["name"] for m in models_data 
                            if "generateContent" in m.get("supportedGenerationMethods", [])
                        ]
                    
                    # 2. 優先權排序（將 Google 官方指定的 3.6-flash 放在最前列！）
                    priority_prefs = [
                        "3.6-flash", "3.6-pro", "3.0-flash", "3-flash",
                        "2.5-flash", "2.0-flash", "1.5-flash", "flash", "pro"
                    ]
                    
                    sorted_models = []
                    # 先加入官方最新推薦
                    sorted_models.append("models/gemini-3.6-flash")
                    
                    # 再根據帳號清單排序
                    for pref in priority_prefs:
                        for m in usable_models:
                            if pref in m.lower() and m not in sorted_models:
                                sorted_models.append(m)
                    for m in usable_models:
                        if m not in sorted_models:
                            sorted_models.append(m)
                            
                    # 3. 逐一嘗試，直到成功回傳 200！
                    headers = {"Content-Type": "application/json"}
                    payload = {
                        "contents": [{
                            "parts": [{"text": full_prompt_text}]
                        }],
                        "generationConfig": {
                            "temperature": 0.7,
                            "maxOutputTokens": 2500
                        }
                    }
                    
                    success = False
                    last_err = ""
                    
                    for target_model in sorted_models:
                        gen_url = f"https://generativelanguage.googleapis.com/v1beta/{target_model}:generateContent?key={clean_key}"
                        try:
                            resp = requests.post(gen_url, headers=headers, json=payload, timeout=60)
                            if resp.status_code == 200:
                                res_json = resp.json()
                                ans = res_json["candidates"][0]["content"]["parts"][0]["text"]
                                st.success(f"✅ 成功調用 Google 最新旗艦模型：`{target_model}`")
                                st.markdown(f"### 🏆 Gemini 大師為【{viewer_name}】親批之全息解盤報告")
                                st.markdown(ans)
                                success = True
                                break
                            else:
                                last_err = f"模型 {target_model} 回傳 {resp.status_code}: {resp.text}"
                        except Exception as e:
                            last_err = str(e)
                            
                    if not success:
                        st.error("所有可用模型嘗試完畢仍失敗：")
                        st.text(last_err)
                        
                except Exception as e:
                    st.error(f"連線異常：{e}")
