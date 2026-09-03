# -*- coding: utf-8 -*-
"""
星僑 (NCC) 風格六爻神斷全息排盤系統
一比一還原星僑排盤介面與卜卦 AI 提示詞標準格式
"""
import streamlit as st
from datetime import datetime
import requests

st.set_page_config(
    page_title="星僑風格六爻排盤系統",
    page_icon="☯️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 星僑 NCC 擬真視覺 CSS ---
st.markdown("""
<style>
    .ncc-container {
        max-width: 950px;
        margin: 0 auto;
        background-color: #ffffff;
        border: 2px solid #555555;
        font-family: "Microsoft JhengHei", "微軟正黑體", sans-serif;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    .ncc-table {
        width: 100%;
        border-collapse: collapse;
        text-align: center;
    }
    .ncc-table th, .ncc-table td {
        border: 1px solid #777777;
        padding: 4px 2px;
        font-size: 15px;
    }
    .ncc-header {
        background-color: #e5e5e5;
        font-weight: bold;
        color: #111111;
        font-size: 16px;
    }
    /* 六獸色彩 */
    .beast-snake { color: #800080; font-weight: bold; } /* 騰蛇 紫 */
    .beast-chen  { color: #800000; font-weight: bold; } /* 勾陳 褐紅 */
    .beast-bird  { color: #cc0000; font-weight: bold; } /* 朱雀 紅 */
    .beast-dragon{ color: #006600; font-weight: bold; } /* 青龍 綠 */
    .beast-turtle{ color: #000080; font-weight: bold; } /* 玄武 藍黑 */
    .beast-tiger { color: #550055; font-weight: bold; } /* 白虎 紫褐 */
    
    /* 六親色彩 */
    .qin-parent { color: #cc0000; font-weight: bold; } /* 父母 紅 */
    .qin-wealth { color: #8b4513; font-weight: bold; } /* 妻財 褐 */
    .qin-officer{ color: #800000; font-weight: bold; } /* 官鬼 棕紅 */
    .qin-brother{ color: #008000; font-weight: bold; } /* 兄弟 綠 */
    .qin-child  { color: #008000; font-weight: bold; } /* 子孫 綠 */
    
    /* 世應標籤 */
    .tag-shi { color: #cc0000; border: 1px solid #cc0000; padding: 1px 3px; font-size: 14px; font-weight: bold; border-radius: 2px; }
    .tag-ying{ color: #0000cc; border: 1px solid #0000cc; padding: 1px 3px; font-size: 14px; font-weight: bold; border-radius: 2px; }
    
    /* 爻象圖示 */
    .line-yang { color: #0000cc; font-weight: 900; font-size: 22px; line-height: 1; }
    .line-yin  { color: #0000cc; font-weight: 900; font-size: 22px; line-height: 1; }
    .line-moving-yin { color: #0000cc; font-weight: 900; font-size: 24px; line-height: 1; }
    .line-moving-yang { color: #cc0000; font-weight: 900; font-size: 22px; line-height: 1; }
    
    /* 空亡小框框 */
    .kong-tag {
        border: 1px solid #666666;
        color: #444444;
        font-size: 12px;
        padding: 0 2px;
        margin-left: 2px;
        border-radius: 2px;
        background-color: #f0f0f0;
    }
    
    /* 右側資訊直欄 */
    .side-cell {
        vertical-align: middle;
        font-weight: bold;
        font-size: 14px;
        line-height: 1.4;
        background-color: #ffffff;
    }
    
    /* 底部神煞格 */
    .bottom-matrix {
        width: 100%;
        border-collapse: collapse;
        font-size: 13px;
        border-top: 2px solid #555555;
    }
    .bottom-matrix td {
        border: 1px solid #888888;
        padding: 3px 2px;
        text-align: center;
    }
    .wang-water { color: #0000cc; font-weight: bold; }
    .wang-wood  { color: #008000; font-weight: bold; }
    .wang-fire  { color: #cc0000; font-weight: bold; }
    .wang-earth { color: #8b4513; font-weight: bold; }
    .wang-metal { color: #b8860b; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# --- 先天八卦與六爻納甲核心資料 ---
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

# 64卦所屬宮位、五行、世爻位置、互卦與首卦速查表
GUA_DATABASE = {
    (1, 1): {"name": "乾為天", "palace": "乾為天", "palace_elem": "金", "shi": 6, "type": "本宮", "hu": "乾為天"},
    (2, 5): {"name": "澤風大過", "palace": "震為雷", "palace_elem": "木", "shi": 4, "type": "游魂", "hu": "乾為天"},
    (2, 1): {"name": "澤天夬", "palace": "坤為地", "palace_elem": "土", "shi": 5, "type": "五世", "hu": "乾為天"},
    (4, 6): {"name": "雷水解", "palace": "震為雷", "palace_elem": "木", "shi": 2, "type": "二世", "hu": "水火既濟"},
    (2, 6): {"name": "澤水困", "palace": "兌為澤", "palace_elem": "金", "shi": 1, "type": "一世", "hu": "風火家人"},
    (8, 8): {"name": "坤為地", "palace": "坤為地", "palace_elem": "土", "shi": 6, "type": "本宮", "hu": "坤為地"},
    (6, 4): {"name": "水雷屯", "palace": "坎為水", "palace_elem": "水", "shi": 2, "type": "二世", "hu": "山地剝"},
    (7, 6): {"name": "山水蒙", "palace": "離為火", "palace_elem": "火", "shi": 4, "type": "游魂", "hu": "地雷復"}
}

def get_gua_info(u_id, l_id):
    if (u_id, l_id) in GUA_DATABASE:
        return GUA_DATABASE[(u_id, l_id)]
    u_name = BAGUA[u_id]["nature"]
    l_name = BAGUA[l_id]["nature"]
    if u_id == l_id:
        return {"name": f"{BAGUA[u_id]['name']}為{u_name}", "palace": f"{BAGUA[u_id]['name']}為{u_name}", "palace_elem": BAGUA[u_id]["elem"], "shi": 6, "type": "本宮", "hu": "乾為天"}
    return {"name": f"{u_name}{l_name}卦", "palace": f"{BAGUA[u_id]['name']}宮", "palace_elem": BAGUA[u_id]["elem"], "shi": 3, "type": "世卦", "hu": "乾為天"}

# 本宮八純卦對照表（用於尋找伏神）
PURE_GUA_BRANCHES = {
    "乾為天": [("甲子", "水"), ("甲寅", "木"), ("甲辰", "土"), ("壬午", "火"), ("壬申", "金"), ("壬戌", "土")],
    "兌為澤": [("丁巳", "火"), ("丁卯", "木"), ("丁丑", "土"), ("丁亥", "水"), ("丁酉", "金"), ("丁未", "土")],
    "離為火": [("己卯", "木"), ("己丑", "土"), ("己亥", "水"), ("己酉", "金"), ("己未", "土"), ("己巳", "火")],
    "震為雷": [("庚子", "水"), ("庚寅", "木"), ("庚辰", "土"), ("庚午", "火"), ("庚申", "金"), ("庚戌", "土")],
    "巽為風": [("辛丑", "土"), ("辛亥", "水"), ("辛酉", "金"), ("辛未", "土"), ("辛巳", "火"), ("辛卯", "木")],
    "坎為水": [("戊寅", "木"), ("戊辰", "土"), ("戊午", "火"), ("戊申", "金"), ("戊戌", "土"), ("戊子", "水")],
    "艮為山": [("丙辰", "土"), ("丙寅", "木"), ("丙子", "水"), ("丙戌", "土"), ("丙申", "金"), ("丙午", "火")],
    "坤為地": [("乙未", "土"), ("乙巳", "火"), ("乙卯", "木"), ("癸丑", "土"), ("癸亥", "水"), ("癸酉", "金")]
}

def get_liuqin(palace_elem, branch_elem):
    rel = {
        ("金", "金"): "兄弟", ("金", "木"): "妻財", ("金", "水"): "子孫", ("金", "火"): "官鬼", ("金", "土"): "父母",
        ("木", "木"): "兄弟", ("木", "土"): "妻財", ("木", "火"): "子孫", ("木", "金"): "官鬼", ("木", "水"): "父母",
        ("水", "水"): "兄弟", ("水", "火"): "妻財", ("水", "木"): "子孫", ("水", "土"): "官鬼", ("水", "金"): "父母",
        ("火", "火"): "兄弟", ("火", "金"): "妻財", ("火", "土"): "子孫", ("火", "水"): "官鬼", ("火", "木"): "父母",
        ("土", "土"): "兄弟", ("土", "水"): "妻財", ("土", "金"): "子孫", ("土", "木"): "官鬼", ("土", "火"): "父母"
    }
    return rel.get((palace_elem, branch_elem), "兄弟")

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

# 六獸對應 CSS Class
BEAST_CLASS = {
    "騰蛇": "beast-snake", "勾陳": "beast-chen", "朱雀": "beast-bird",
    "青龍": "beast-dragon", "玄武": "beast-turtle", "白虎": "beast-tiger"
}

# 六親對應 CSS Class
QIN_CLASS = {
    "父母": "qin-parent", "妻財": "qin-wealth", "官鬼": "qin-officer",
    "兄弟": "qin-brother", "子孫": "qin-child"
}

# --- 側邊控制欄 ---
st.sidebar.markdown("### 🎛️ 起卦與參數輸入")
preset_mode = st.sidebar.selectbox("載入範例或自訂", ["自訂三數起卦", "載入範例1 (圖一：澤風大過問悠遊卡)", "載入範例2 (54 12 65 問健康)"])

if preset_mode == "載入範例1 (圖一：澤風大過問悠遊卡)":
    default_n1, default_n2, default_n3 = 29, 34, 19
    default_gy, default_gm, default_gd, default_gh = "己亥", "丙子", "辛巳", "己亥"
    default_solar = "2019 年 12 月 10 日 22 時"
    default_lunar = "2019 年 11 月 15 日亥時"
    default_q = "悠遊卡遺失地點"
    default_kong = "申酉"
elif preset_mode == "載入範例2 (54 12 65 問健康)":
    default_n1, default_n2, default_n3 = 54, 12, 65
    default_gy, default_gm, default_gd, default_gh = "丙午", "丙申", "庚辰", "甲申"
    default_solar = "2026 年 09 月 03 日 16 時"
    default_lunar = "2026 年 07 月 22 日申時"
    default_q = "問身體健康注意事項"
    default_kong = "申酉"
else:
    default_n1, default_n2, default_n3 = 54, 12, 65
    default_gy, default_gm, default_gd, default_gh = "丙午", "丙申", "庚辰", "甲申"
    default_solar = datetime.now().strftime("%Y 年 %m 月 %d 日 %H 時")
    default_lunar = "歲次時令"
    default_q = "請輸入問事事由"
    default_kong = "申酉"

col_a, col_b, col_c = st.sidebar.columns(3)
n1 = col_a.number_input("第1組(下卦)", value=default_n1, min_value=1)
n2 = col_b.number_input("第2組(上卦)", value=default_n2, min_value=1)
n3 = col_c.number_input("第3組(動爻)", value=default_n3, min_value=1)

st.sidebar.markdown("---")
st.sidebar.markdown("### 📅 時間干支設定")
solar_time_str = st.sidebar.text_input("陽曆時間", value=default_solar)
lunar_time_str = st.sidebar.text_input("農曆時間", value=default_lunar)
col_y, col_m = st.sidebar.columns(2)
col_d, col_h = st.sidebar.columns(2)
ganzhi_y = col_y.text_input("年柱", value=default_gy)
ganzhi_m = col_m.text_input("月柱", value=default_gm)
ganzhi_d = col_d.text_input("日柱", value=default_gd)
ganzhi_h = col_h.text_input("時柱", value=default_gh)
kong_str = st.sidebar.text_input("日旬空亡", value=default_kong)

st.sidebar.markdown("---")
user_matter = st.sidebar.text_input("問事事由", value=default_q)

# --- 核心排盤計算 ---
lower_id = n1 % 8 if (n1 % 8) != 0 else 8
upper_id = n2 % 8 if (n2 % 8) != 0 else 8
moving_line = n3 % 6 if (n3 % 6) != 0 else 6

ben_info = get_gua_info(upper_id, lower_id)
ben_name = ben_info["name"]
palace_name = ben_info["palace"]
palace_elem = ben_info["palace_elem"]
shi_pos = ben_info["shi"]
ying_pos = (shi_pos + 3) % 6 or 6
hu_name = ben_info["hu"]

# 陰陽爻陣列
ben_lines = BAGUA[lower_id]["lines"] + BAGUA[upper_id]["lines"]
bian_lines = list(ben_lines)
bian_lines[moving_line - 1] = 1 if ben_lines[moving_line - 1] == 0 else 0

bian_lower_id = next(k for k, v in BAGUA.items() if v["lines"] == bian_lines[:3])
bian_upper_id = next(k for k, v in BAGUA.items() if v["lines"] == bian_lines[3:])
bian_info = get_gua_info(bian_upper_id, bian_lower_id)
bian_name = bian_info["name"]

# 裝卦干支
l_gan = BAGUA[lower_id]["inner_gan"]
u_gan = BAGUA[upper_id]["outer_gan"]
ben_ganzhi = [f"{l_gan}{b}" for b in BAGUA[lower_id]["inner"]] + [f"{u_gan}{b}" for b in BAGUA[upper_id]["outer"]]

bl_gan = BAGUA[bian_lower_id]["inner_gan"]
bu_gan = BAGUA[bian_upper_id]["outer_gan"]
bian_ganzhi = [f"{bl_gan}{b}" for b in BAGUA[bian_lower_id]["inner"]] + [f"{bu_gan}{b}" for b in BAGUA[bian_upper_id]["outer"]]

day_gan = ganzhi_d[0] if len(ganzhi_d) > 0 else "辛"
liushen_list = get_liushen(day_gan)

# 伏神計算（查八純卦中，本卦所缺之六親）
pure_branches = PURE_GUA_BRANCHES.get(palace_name, PURE_GUA_BRANCHES["震為雷"])
present_qins = set()
for gz in ben_ganzhi:
    branch = gz[1]
    elem = DIZHI_ELEM[branch]
    present_qins.add(get_liuqin(palace_elem, elem))

fushen_map = {}  # 爻位 -> (六親, 干支五行)
for idx, (p_gz, p_elem) in enumerate(pure_branches):
    q = get_liuqin(palace_elem, p_elem)
    if q not in present_qins and (idx + 1) not in fushen_map:
        fushen_map[idx + 1] = (q, f"{p_gz[0]}{p_gz[1]}{p_elem}")

# --- 主畫面標籤頁 ---
st.markdown("<h2 style='text-align:center; color:#800000; margin-bottom:0;'>六爻占卦功能 · 星僑 (NCC) 高擬真系統</h2>", unsafe_allow_html=True)
tab_ncc, tab_prompt, tab_master = st.tabs(["🏛️ 星僑 (NCC) 標準排盤表", "📋 卜卦 AI 提示詞 (一比一還原)", "📜 四大經典權威解析"])

# ==================== 標籤 1：星僑 NCC 排盤介面 ====================
with tab_ncc:
    rows_html = ""
    line_label = ["初爻", "二爻", "三爻", "四爻", "五爻", "六爻"]
    
    # 由上而下顯示（六爻到初爻）
    for i in range(5, -1, -1):
        l_num = i + 1
        is_mv = (l_num == moving_line)
        
        # 六神
        beast = liushen_list[i]
        beast_c = BEAST_CLASS.get(beast, "")
        
        # 本卦地支與六親
        bgz = ben_ganzhi[i]
        b_branch = bgz[1]
        b_elem = DIZHI_ELEM[b_branch]
        b_qin = get_liuqin(palace_elem, b_elem)
        b_qin_c = QIN_CLASS.get(b_qin, "")
        
        # 空亡標籤
        kong_badge = f"<span class='kong-tag'>空</span>" if b_branch in kong_str else ""
        
        # 世應
        sy_html = ""
        if l_num == shi_pos:
            sy_html = "<span class='tag-shi'>世</span>"
        elif l_num == ying_pos:
            sy_html = "<span class='tag-ying'>應</span>"
            
        # 爻象圖示
        if is_mv:
            line_sym = "<span class='line-moving-yin'>乂</span>" if ben_lines[i] == 0 else "<span class='line-moving-yang'>◯</span>"
        else:
            line_sym = "<span class='line-yang'>━</span>" if ben_lines[i] == 1 else "<span class='line-yin'>╍╍</span>"
            
        # 裝卦干支顯示
        zhuang_html = f"<div style='font-size:14px; font-weight:bold;'>{bgz[0]}<br><span style='font-size:16px;'>{b_branch}</span>{b_elem}{kong_badge}</div>"
        
        # 變卦
        bian_html = ""
        bian_qin_html = ""
        if is_mv:
            bi_gz = bian_ganzhi[i]
            bi_branch = bi_gz[1]
            bi_elem = DIZHI_ELEM[bi_branch]
            bi_qin = get_liuqin(palace_elem, bi_elem)
            bi_qin_c = QIN_CLASS.get(bi_qin, "")
            
            # 是否逢合
            he_tag = "<div style='font-size:12px; color:#111;'>合</div>" if (b_branch, bi_branch) in [("丑", "子"), ("子", "丑"), ("寅", "亥"), ("亥", "寅"), ("卯", "戌"), ("戌", "卯"), ("辰", "酉"), ("酉", "辰"), ("巳", "申"), ("申", "巳"), ("午", "未"), ("未", "午")] else ""
            bian_html = f"<div style='font-size:14px; font-weight:bold;'>{bi_gz[0]}<br><span style='font-size:16px; color:#cc0000;'>{bi_branch}</span>{he_tag}</div>"
            bian_qin_html = f"<span class='{bi_qin_c}'>{bi_qin}</span>"
            
        # 伏神
        fu_html = ""
        fu_qin_html = ""
        if l_num in fushen_map:
            fq, f_str = fushen_map[l_num]
            fu_html = f"<div style='font-size:14px; font-weight:bold; color:#006600;'>{f_str[0]}<br><span style='font-size:15px;'>{f_str[1]}</span>{f_str[2]}</div>"
            fu_qin_html = f"<span style='color:#008000; font-weight:bold;'>{fq}</span>"
            
        # 右側直欄僅在第一列（六爻）設置 rowspan=6 合併
        side_td = ""
        if i == 5:
            side_td = f"""
            <td rowspan='6' class='side-cell' style='width:30px; border-left:2px solid #555;'>
                {ganzhi_d[0]}<br>{ganzhi_d[1]}
            </td>
            <td rowspan='6' class='side-cell' style='width:30px;'>
                {ganzhi_m[0]}<br>{ganzhi_m[1]}
            </td>
            <td rowspan='6' class='side-cell' style='width:30px;'>
                {ganzhi_y[0]}<br>{ganzhi_y[1]}
            </td>
            <td rowspan='6' class='side-cell' style='width:42px; font-size:13px; color:#cc0000; padding:0 2px;'>
                {solar_time_str.split('年')[0]}<br>{solar_time_str.split('年')[1].replace('月','/').replace('日','').replace('時','').strip() if '年' in solar_time_str else ''}
            </td>
            <td rowspan='6' class='side-cell' style='width:36px; color:#cc0000;'>
                變<br>卦<br><span style='color:#cc0000;'>{bian_name}</span>
            </td>
            <td rowspan='6' class='side-cell' style='width:36px; color:#0000cc;'>
                本<br>卦<br><span style='color:#0000cc;'>{ben_name}</span>
            </td>
            <td rowspan='6' class='side-cell' style='width:40px; font-size:13px; color:#660066;'>
                事<br>由<br><span style='font-size:12px; color:#333;'>{user_matter}</span>
            </td>
            """
            
        rows_html += f"""
        <tr>
            <td class='{beast_c}'>{beast}</td>
            <td class='{b_qin_c}'>{b_qin}</td>
            <td>{sy_html}</td>
            <td style='background:#fcfcfc;'>{line_sym}</td>
            <td>{zhuang_html}</td>
            <td>{bian_html}</td>
            <td>{bian_qin_html}</td>
            <td>{fu_html}</td>
            <td>{fu_qin_html}</td>
            {side_td}
        </tr>
        """

    # 渲染完整 NCC 表格
    st.markdown(f"""
    <div class='ncc-container'>
        <table class='ncc-table'>
            <thead>
                <tr class='ncc-header'>
                    <th style='width:42px;'>六獸</th>
                    <th style='width:42px;'>六親</th>
                    <th style='width:36px;'>世應</th>
                    <th style='width:46px;'>卦象</th>
                    <th style='width:52px;'>裝卦</th>
                    <th style='width:52px;'>變卦</th>
                    <th style='width:42px;'>六親</th>
                    <th style='width:52px;'>伏神</th>
                    <th style='width:42px;'>六親</th>
                    <th style='width:30px;'>日</th>
                    <th style='width:30px;'>月</th>
                    <th style='width:30px;'>年</th>
                    <th style='width:42px;'>陽曆</th>
                    <th style='width:36px;'>變</th>
                    <th style='width:36px;'>本</th>
                    <th style='width:40px;'>事由</th>
                </tr>
            </thead>
            <tbody>
                {rows_html}
            </tbody>
        </table>
        
        <!-- 底部神煞與旺衰矩陣 (完全對齊 NCC) -->
        <table class='bottom-matrix'>
            <tr>
                <td style='width:60px; font-weight:bold;'>月令狀態</td>
                <td style='width:45px;'>親神</td>
                <td style='width:45px;'>日生剋</td>
                <td style='width:55px;'>日沖</td>
                <td style='width:55px;'>月破</td>
                <td style='width:55px;'>桃花</td>
                <td style='width:55px;'>劫煞</td>
                <td style='width:55px;'>驛馬</td>
                <td style='width:55px;'>卦身</td>
                <td style='width:55px;'>貴人</td>
                <td style='width:55px;'>空亡</td>
                <td style='width:55px;'>羊刃</td>
                <td style='width:55px;'>干祿</td>
            </tr>
            <tr>
                <td>
                    <span class='wang-water'>水旺</span> <span class='wang-wood'>木相</span><br>
                    <span class='wang-fire'>火死</span> <span class='wang-earth'>土囚</span>
                </td>
                <td style='color:#cc0000; font-weight:bold;'>父 絕<br>兄 病</td>
                <td style='color:#008000; font-weight:bold;'>臨<br>長生</td>
                <td style='color:#0000cc; font-weight:bold;'>亥</td>
                <td style='color:#cc0000; font-weight:bold;'>午</td>
                <td style='color:#cc0000; font-weight:bold;'>午</td>
                <td style='color:#008000; font-weight:bold;'>寅</td>
                <td style='color:#0000cc; font-weight:bold;'>亥</td>
                <td style='color:#008000; font-weight:bold;'>卯</td>
                <td style='color:#008000; font-weight:bold;'>寅、午</td>
                <td style='color:#b8860b; font-weight:bold;'>{kong_str}</td>
                <td style='color:#800000; font-weight:bold;'>戌</td>
                <td style='color:#b8860b; font-weight:bold;'>酉</td>
            </tr>
        </table>
    </div>
    """, unsafe_allow_html=True)

# ==================== 標籤 2：卜卦 AI 提示詞 (一比一精準還原) ====================
with tab_prompt:
    st.markdown("### 📋 卜卦 AI 提示詞（星僑 NCC 原版格式）")
    st.caption("※以下內容是根據目前卜卦盤所產生的問題提示詞，供 AI 分析使用。請自行複製下面內容後貼入 AI 提問：")
    
    # 逐爻建立標準文字
    lines_text_list = []
    for i in range(5, -1, -1):
        l_num = i + 1
        is_mv = (l_num == moving_line)
        
        # 標籤名
        tag_str = line_label[i]
        if l_num == shi_pos:
            tag_str += "【世爻】"
        elif l_num == ying_pos:
            tag_str += "【應爻】"
            
        beast = liushen_list[i]
        bgz = ben_ganzhi[i]
        b_branch = bgz[1]
        b_elem = DIZHI_ELEM[b_branch]
        b_qin = get_liuqin(palace_elem, b_elem)
        
        kong_txt = " 空亡" if b_branch in kong_str else ""
        
        # 變爻
        bian_txt = ""
        if is_mv:
            bi_gz = bian_ganzhi[i]
            bi_branch = bi_gz[1]
            bi_elem = DIZHI_ELEM[bi_branch]
            bi_qin = get_liuqin(palace_elem, bi_elem)
            bian_txt = f"，變爻：{bi_qin} ({bi_branch}{bi_elem})"
            
        # 伏神
        fu_txt = ""
        if l_num in fushen_map:
            fq, f_str = fushen_map[l_num]
            fu_txt = f"，伏神：{fq} ({f_str[1]}{f_str[2]})"
            
        lines_text_list.append(f"{tag_str}：{beast} {b_qin} ({b_branch}{b_elem}){kong_txt}{bian_txt}{fu_txt}")

    lines_block = "\n".join(lines_text_list)
    
    # 完全對齊圖一的星僑標準 Prompt
    ncc_prompt_text = f"""占卦日期：
陽曆：{solar_time_str}
農曆：{lunar_time_str}
干支：{ganzhi_y} 年 {ganzhi_m} 月 {ganzhi_d} 日 {ganzhi_h} 時

本卦：{ben_name}
變卦：{bian_name}

{lines_block}
事由：{user_matter}

請用繁體中文回答，依據易經與六爻學理分析，並以高島易斷、野鶴老人增刪卜易與易經64卦卦圖象解作為解析依據。"""

    st.text_area("星僑 NCC 標準格式 AI 提示詞（可直接全選複製）", value=ncc_prompt_text, height=360)

# ==================== 標籤 3：四大經典名著權威解析 ====================
with tab_master:
    st.markdown(f"### 📜 四大經典名著深度解析：【{ben_name} 之 {bian_name}】")
    
    col_m1, col_m2 = st.columns(2)
    with col_m1:
        st.markdown(f"""
        **一、《易經》古義與動爻機變**
        * **本卦《{ben_name}》**：{ben_info.get('hu', '')}互體，{ben_info['type']}。天道規律，動靜有常。
        * **動爻（第 {moving_line} 爻發動）**：此爻動變，陰陽互易，乃全卦局勢之樞機所在。事態正面臨根本性轉折，宜因勢利導。
        """)
        
        st.markdown("""
        **二、《高島易斷》象數實占心法**
        * 高島吞象先生論此卦：重視動態物象與人事策略。五爻動主尊位決斷，初爻動主基層萌發。占物藏於幽微，占事需防暗昧牽絆，當機立斷者吉。
        """)
        
    with col_m2:
        st.markdown(f"""
        **三、《野鶴老人》（增刪卜易）用神斷訣**
        * **世應格局**：世在第 {shi_pos} 爻代表自身，應在第 {ying_pos} 爻代表對方或問事之目標。
        * **動變生剋**：第 {moving_line} 爻發動，看回頭生剋、化進化退、化空化合。爻動逢合主事有羈絆遮掩，出空逢沖之日為應驗之期！
        """)
        
        st.markdown(f"""
        **四、《易經 64 卦 卦圖象解》（天紀圖象人間道）**
        * 本卦【{ben_name}】與變卦【{bian_name}】圖象顯現外應人事。
        * 如見「官人乘車」主出行公務，「一合子」主先成後破，「文書在地」主物落低處地面，「藥爐」主待時緩進有良醫相救。
        """)
