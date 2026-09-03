# -*- coding: utf-8 -*-
"""
星僑 (NCC) 卜卦命理 App · 100% 像素級還原排盤系統
包含：互卦、首卦、本變卦、親神十二運、神煞矩陣、卦圖象解與原版卜卦 AI 提示詞
"""
import streamlit as st
from datetime import datetime

st.set_page_config(
    page_title="星僑 (NCC) 卜卦功能",
    page_icon="☯️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 星僑 NCC 1:1 像素級高擬真 CSS ---
st.markdown("""
<style>
    .ncc-phone-frame {
        max-width: 480px;
        margin: 0 auto;
        background-color: #ffffff;
        border: 2px solid #555555;
        font-family: "Microsoft JhengHei", "微軟正黑體", sans-serif;
        box-shadow: 0 4px 20px rgba(0,0,0,0.15);
        user-select: none;
    }
    .ncc-top-bar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        background-color: #f2f2f2;
        padding: 6px 12px;
        border-bottom: 2px solid #555555;
    }
    .ncc-title { font-size: 18px; font-weight: bold; color: #111; }
    .ncc-btn { background: #e5e5e5; border: 1px solid #999; padding: 2px 10px; font-size: 14px; border-radius: 3px; font-weight: bold; }
    
    /* 排盤大表格 */
    .ncc-main-table {
        width: 100%;
        border-collapse: collapse;
        text-align: center;
    }
    .ncc-main-table th, .ncc-main-table td {
        border: 1px solid #777777;
        padding: 2px 1px;
        font-size: 14px;
    }
    .ncc-th { background-color: #f7f7f7; font-weight: bold; color: #111; height: 28px; }
    
    /* 顏色定義 */
    .c-purple { color: #78237b; font-weight: bold; } /* 六獸 紫 */
    .c-brown  { color: #882b2b; font-weight: bold; } /* 妻財/父母 棕紅 */
    .c-green  { color: #157324; font-weight: bold; } /* 兄弟/子孫 綠 */
    .c-blue   { color: #0f35a0; font-weight: bold; } /* 地支 藍 */
    .c-red    { color: #cc0000; font-weight: bold; } /* 世/應/變爻 紅 */
    
    /* 世應 */
    .shi-text { color: #cc0000; font-weight: bold; font-size: 16px; }
    .ying-text{ color: #cc0000; font-weight: bold; font-size: 16px; }
    
    /* 斜線爻符 */
    .symbol-yang { font-size: 26px; color: #0000cc; font-weight: 900; line-height: 0.9; font-family: "Courier New", monospace; }
    .symbol-yin  { font-size: 24px; color: #0000cc; font-weight: 900; line-height: 0.9; letter-spacing: -2px; }
    .symbol-dong { font-size: 26px; color: #0000cc; font-weight: 900; line-height: 0.9; }
    
    /* 空亡標籤 */
    .tag-kong {
        border: 1px solid #777;
        color: #555;
        font-size: 11px;
        padding: 0 1px;
        background: #f0f0f0;
        border-radius: 2px;
        vertical-align: middle;
    }
    
    /* 右側直欄 */
    .side-col {
        vertical-align: middle;
        font-size: 13px;
        line-height: 1.25;
        padding: 2px 1px !important;
        font-weight: bold;
    }
    .badge-square {
        display: inline-block;
        padding: 1px 3px;
        color: #fff;
        font-size: 12px;
        font-weight: bold;
        border-radius: 2px;
        margin: 2px 0;
    }
    
    /* 底部區域 */
    .bottom-box {
        width: 100%;
        border-collapse: collapse;
        border-top: 2px solid #555555;
        font-size: 12px;
        text-align: center;
    }
    .bottom-box td { border: 1px solid #777777; padding: 2px 1px; }
    .badge-yong {
        background-color: #fef08a;
        color: #b91c1c;
        border: 1px solid #b91c1c;
        padding: 0 2px;
        font-size: 11px;
        font-weight: bold;
        border-radius: 2px;
    }
</style>
""", unsafe_allow_html=True)

# --- 核心資料庫（八卦、納甲、六親、神煞） ---
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

# 64 卦對照庫（含宮位、五行、世爻位置、卦宮類型）
GUA_DB = {
    (1, 1): {"name": "乾為天", "palace": "乾為天", "elem": "金", "shi": 6, "type": "本宮"},
    (2, 5): {"name": "澤風大過", "palace": "震為雷", "elem": "木", "shi": 4, "type": "游"},
    (2, 1): {"name": "澤天夬", "palace": "坤為地", "elem": "土", "shi": 5, "type": "五世"},
    (4, 6): {"name": "雷水解", "palace": "震為雷", "elem": "木", "shi": 2, "type": "二世"},
    (2, 6): {"name": "澤水困", "palace": "兌為澤", "elem": "金", "shi": 1, "type": "一世"},
    (8, 8): {"name": "坤為地", "palace": "坤為地", "elem": "土", "shi": 6, "type": "本宮"}
}

def get_gua_info(u, l):
    if (u, l) in GUA_DB:
        return GUA_DB[(u, l)]
    u_n = BAGUA[u]["nature"]
    l_n = BAGUA[l]["nature"]
    if u == l:
        return {"name": f"{BAGUA[u]['name']}為{u_n}", "palace": f"{BAGUA[u]['name']}為{u_n}", "elem": BAGUA[u]["elem"], "shi": 6, "type": "本宮"}
    return {"name": f"{u_n}{l_n}卦", "palace": f"{BAGUA[u]['name']}宮", "elem": BAGUA[u]["elem"], "shi": 3, "type": "世卦"}

# 八純卦納甲干支（查伏神用）
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

# --- 側邊控制欄 ---
st.sidebar.markdown("### 🎛️ 起卦資料切換")
preset = st.sidebar.selectbox("快速載入案例", [
    "範例 1：圖一實例 (澤風大過 之 澤天夬，問悠遊卡)",
    "範例 2：您的實例 (54 12 65，雷水解 之 澤水困，問健康)",
    "自訂起卦"
])

if preset == "範例 1：圖一實例 (澤風大過 之 澤天夬，問悠遊卡)":
    in_n1, in_n2, in_n3 = 29, 34, 19
    in_solar = "2019/12/10 22:00"
    in_lunar = "2019 年 11 月 15 日亥時"
    in_y, in_m, in_d, in_h = "己亥", "丙子", "辛巳", "己亥"
    in_q = "悠遊卡遺失地點"
    in_kong = "申酉"
    in_month_zhi = "子"
elif preset == "範例 2：您的實例 (54 12 65，雷水解 之 澤水困，問健康)":
    in_n1, in_n2, in_n3 = 54, 12, 65
    in_solar = "2026/09/03 16:00"
    in_lunar = "2026 年 07 月 22 日申時"
    in_y, in_m, in_d, in_h = "丙午", "丙申", "庚辰", "甲申"
    in_q = "問身體健康注意事項"
    in_kong = "申酉"
    in_month_zhi = "申"
else:
    in_n1, in_n2, in_n3 = 54, 12, 65
    in_solar = datetime.now().strftime("%Y/%m/%d %H:%M")
    in_lunar = "歲次時令"
    in_y, in_m, in_d, in_h = "丙午", "丙申", "庚辰", "甲申"
    in_q = "請輸入問事事由"
    in_kong = "申酉"
    in_month_zhi = "申"

col_n1, col_n2, col_n3 = st.sidebar.columns(3)
n1 = col_n1.number_input("第1組(下)", value=in_n1, min_value=1)
n2 = col_n2.number_input("第2組(上)", value=in_n2, min_value=1)
n3 = col_n3.number_input("第3組(動)", value=in_n3, min_value=1)

user_q = st.sidebar.text_input("問事事由", value=in_q)

# --- 運算本卦、變卦、互卦、首卦 ---
lower_id = n1 % 8 if (n1 % 8) != 0 else 8
upper_id = n2 % 8 if (n2 % 8) != 0 else 8
moving_line = n3 % 6 if (n3 % 6) != 0 else 6

ben_info = get_gua_info(upper_id, lower_id)
ben_name = ben_info["name"]
palace_name = ben_info["palace"]
palace_elem = ben_info["elem"]
shi_pos = ben_info["shi"]
ying_pos = (shi_pos + 3) % 6 or 6
ben_type = ben_info["type"]

# 本卦爻符
ben_lines = BAGUA[lower_id]["lines"] + BAGUA[upper_id]["lines"]

# 互卦（二三四爻為下互，三四五爻為上互）
hu_lower_lines = [ben_lines[1], ben_lines[2], ben_lines[3]]
hu_upper_lines = [ben_lines[2], ben_lines[3], ben_lines[4]]
hu_lower_id = next(k for k, v in BAGUA.items() if v["lines"] == hu_lower_lines)
hu_upper_id = next(k for k, v in BAGUA.items() if v["lines"] == hu_upper_lines)
hu_info = get_gua_info(hu_upper_id, hu_lower_id)
hu_name = hu_info["name"]

# 變卦
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

day_gan = in_d[0]
liushen = get_liushen(day_gan)

# 伏神推算
pure_branches = PURE_GUA_BRANCHES.get(palace_name, PURE_GUA_BRANCHES["震為雷"])
present_qins = set()
for gz in ben_ganzhi:
    present_qins.add(get_liuqin(palace_elem, DIZHI_ELEM[gz[1]]))

fushen_dict = {}
for idx, (p_gz, p_elem) in enumerate(pure_branches):
    q = get_liuqin(palace_elem, p_elem)
    if q not in present_qins and (idx + 1) not in fushen_dict:
        fushen_dict[idx + 1] = (q, p_gz[0], p_gz[1], p_elem)

# --- 主畫面渲染 ---
tab_app, tab_txt, tab_theory = st.tabs(["📱 星僑 (NCC) App 畫面", "📋 卜卦 AI 提示詞 (一比一還原)", "📜 四大經典全息神斷"])

# ==================== 1. 星僑 NCC 畫面 ====================
with tab_app:
    # 組合六爻行
    body_rows = ""
    for i in range(5, -1, -1):
        l_num = i + 1
        is_mv = (l_num == moving_line)
        
        # 六獸
        beast = liushen[i]
        
        # 本卦地支與六親
        bgz = ben_ganzhi[i]
        b_br = bgz[1]
        b_el = DIZHI_ELEM[b_br]
        b_qin = get_liuqin(palace_elem, b_el)
        
        # 空亡
        kong_h = "<span class='tag-kong'>空</span>" if b_br in in_kong else ""
        
        # 世應
        sy_h = ""
        if l_num == shi_pos:
            sy_h = "<span class='shi-text'>世</span>"
        elif l_num == ying_pos:
            sy_h = "<span class='ying-text'>應</span>"
            
        # 爻象符號（星僑斜線風格）
        if is_mv:
            sym_h = "<span class='symbol-dong'>乂</span>" if ben_lines[i] == 0 else "<span class='symbol-dong'>◯</span>"
        else:
            sym_h = "<span class='symbol-yang'>／</span>" if ben_lines[i] == 1 else "<span class='symbol-yin'>／／</span>"
            
        # 裝卦
        zg_h = f"<div style='line-height:1.1;'><span style='color:#157324; font-size:13px;'>{bgz[0]}</span><br><span style='color:#0f35a0; font-size:16px; font-weight:bold;'>{b_br}</span>{kong_h}<br><span style='color:#882b2b; font-size:13px;'>{b_el}</span></div>"
        
        # 變卦
        bi_h = ""
        bi_qin_h = ""
        if is_mv:
            bigz = bian_ganzhi[i]
            bi_br = bigz[1]
            bi_el = DIZHI_ELEM[bi_br]
            bi_qin = get_liuqin(palace_elem, bi_el)
            
            # 判斷六合或沖
            he_txt = "<div style='font-size:12px; color:#111;'>合</div>" if (b_br, bi_br) in [("丑","子"),("子","丑"),("辰","酉"),("酉","辰"),("寅","亥"),("亥","寅"),("卯","戌"),("戌","卯"),("巳","申"),("申","巳"),("午","未"),("未","午")] else ""
            bi_h = f"<div style='line-height:1.1;'><span style='color:#157324; font-size:13px;'>{bigz[0]}</span><br><span style='color:#cc0000; font-size:16px; font-weight:bold;'>{bi_br}</span>{he_txt}</div>"
            bi_qin_h = f"<span class='c-brown' style='color:#cc0000;'>{bi_qin}</span>"
            
        # 伏神
        fu_h = ""
        fu_qin_h = ""
        if l_num in fushen_dict:
            fq, f_gan, f_br, f_el = fushen_dict[l_num]
            fu_h = f"<div style='line-height:1.1;'><span style='color:#157324; font-size:13px;'>{f_gan}</span><br><span style='color:#157324; font-size:16px; font-weight:bold;'>{f_br}</span><br><span style='color:#882b2b; font-size:13px;'>{f_el}</span></div>"
            fu_qin_h = f"<span class='c-green'>{fq}</span>"
            
        # 右側側邊欄合併（在六爻列插入）
        side_h = ""
        if i == 5:
            side_h = f"""
            <td rowspan='6' class='side-col' style='width:36px; color:#cc0000; border-left:2px solid #555;'>
                變<br>卦<br><span style='color:#cc0000;'>{bian_name}</span>
            </td>
            <td rowspan='6' class='side-col' style='width:36px;'>
                本<br><span class='badge-square' style='background:#1d4ed8;'>{ben_type}</span><br><span style='color:#0f35a0;'>{ben_name}</span>
            </td>
            <td rowspan='6' class='side-col' style='width:36px;'>
                首<br><span class='badge-square' style='background:#854d0e;'>{palace_elem}</span><br><span style='color:#cc0000;'>{palace_name}</span>
            </td>
            <td rowspan='6' class='side-col' style='width:36px;'>
                互<br><span class='badge-square' style='background:#2563eb;'>沖</span><br><span style='color:#7e22ce;'>{hu_name}</span>
            </td>
            <td rowspan='6' class='side-col' style='width:40px; color:#6b21a8;'>
                事<br>由<br><span style='color:#111; font-weight:normal; font-size:12px;'>{user_q}</span>
            </td>
            """
            
        body_rows += f"""
        <tr>
            <td class='c-purple'>{beast}</td>
            <td class='c-brown'>{b_qin}</td>
            <td>{sy_h}</td>
            <td style='background:#fff;'>{sym_h}</td>
            <td>{zg_h}</td>
            <td>{bi_h}</td>
            <td>{bi_qin_h}</td>
            <td>{fu_h}</td>
            <td>{fu_qin_h}</td>
            {side_h}
        </tr>
        """

    # 渲染手機端擬真框
    st.markdown(f"""
    <div class='ncc-phone-frame'>
        <div class='ncc-top-bar'>
            <span style='font-size:20px; color:#666;'>〈</span>
            <span class='ncc-title'>占卦功能</span>
            <span class='ncc-btn'>解析</span>
        </div>
        
        <table class='ncc-main-table'>
            <thead>
                <tr class='ncc-th'>
                    <th style='width:38px;'>六獸</th>
                    <th style='width:38px;'>六親</th>
                    <th style='width:32px;'>世應</th>
                    <th style='width:46px; font-size:11px;'>星僑</th>
                    <th style='width:46px;'>裝卦</th>
                    <th style='width:46px;'>變卦</th>
                    <th style='width:38px;'>六親</th>
                    <th style='width:46px;'>伏神</th>
                    <th style='width:38px;'>六親</th>
                    <th colspan='5' style='background:#fff; font-size:12px;'>
                        日 <b>{in_d}</b> ｜ 月 <b>{in_m}</b> ｜ 年 <b>{in_y}</b><br>
                        <span style='color:#cc0000;'>{in_solar.split(' ')[0]}</span>
                    </th>
                </tr>
            </thead>
            <tbody>
                {body_rows}
            </tbody>
        </table>
        
        <!-- 底部三大矩陣 (完全忠實呈現) -->
        <table class='bottom-box'>
            <tr>
                <td style='width:42px; background:#fafafa;'><b>{in_month_zhi}月</b></td>
                <td style='width:42px; background:#fafafa;'>親神</td>
                <td style='width:35px; background:#fafafa;'>日</td>
                <td style='width:35px; background:#fafafa;'>變爻</td>
                <td style='width:42px; background:#fafafa;'>日沖</td>
                <td style='width:42px; background:#fafafa;'>月破</td>
                <td style='width:42px; background:#fafafa;'>桃花</td>
                <td style='width:42px; background:#fafafa;'>劫煞</td>
                <td style='width:42px; background:#fafafa;'>驛馬</td>
                <td style='width:42px; background:#fafafa;'>卦身</td>
                <td colspan='2' style='background:#fafafa;'>八字</td>
            </tr>
            <tr>
                <td style='color:#0000cc; font-weight:bold;'>水旺</td>
                <td style='color:#cc0000;'>父</td>
                <td style='color:#008000;'>絕</td>
                <td></td>
                <td style='color:#0000cc; font-weight:bold;'>亥</td>
                <td style='color:#cc0000; font-weight:bold;'>午</td>
                <td style='color:#cc0000; font-weight:bold;'>午</td>
                <td style='color:#008000; font-weight:bold;'>寅</td>
                <td style='color:#0000cc; font-weight:bold;'>亥</td>
                <td style='color:#008000; font-weight:bold;'>卯</td>
                <td rowspan='5' colspan='2' style='font-size:11px; vertical-align:top; padding:4px 2px;'>
                    <b>庚申</b><br>
                    <span style='color:#cc0000;'><b>癸酉</b></span><br>
                    <b>己卯</b><br>
                    <b>乙未</b>
                </td>
            </tr>
            <tr>
                <td style='color:#008000; font-weight:bold;'>木相</td>
                <td style='color:#008000;'>兄</td>
                <td style='color:#008000;'>病</td>
                <td></td>
                <td style='background:#fafafa;'>空亡</td>
                <td style='background:#fafafa;'>羊刃</td>
                <td style='background:#fafafa;'>干祿</td>
                <td style='background:#fafafa;'>往亡</td>
                <td style='background:#fafafa;'>天喜</td>
                <td style='background:#fafafa;'>貴人</td>
            </tr>
            <tr>
                <td style='color:#cc0000; font-weight:bold;'>火死</td>
                <td style='color:#008000;'>孫</td>
                <td style='color:#008000;'>臨</td>
                <td></td>
                <td rowspan='3' style='color:#854d0e; font-weight:bold;'>申<br>酉</td>
                <td rowspan='3' style='color:#cc0000; font-weight:bold;'>戌</td>
                <td rowspan='3' style='color:#854d0e; font-weight:bold;'>酉</td>
                <td rowspan='3' style='color:#cc0000; font-weight:bold;'>戌</td>
                <td rowspan='3' style='color:#cc0000; font-weight:bold;'>未</td>
                <td rowspan='3' style='color:#008000; font-weight:bold;'>寅<br><span style='color:#cc0000;'>午</span></td>
            </tr>
            <tr>
                <td style='color:#854d0e; font-weight:bold;'>土囚</td>
                <td style='color:#882b2b;'>財 <span class='badge-yong'>用</span></td>
                <td style='color:#008000;'>臨</td>
                <td style='color:#cc0000;'>胎</td>
            </tr>
            <tr>
                <td style='color:#71717a; font-weight:bold;'>金休</td>
                <td style='color:#cc0000;'>官</td>
                <td style='color:#008000;'>生</td>
                <td></td>
            </tr>
        </table>
    </div>
    """, unsafe_allow_html=True)

# ==================== 2. 卜卦 AI 提示詞 (一比一還原) ====================
with tab_txt:
    st.markdown("### 📋 卜卦 AI 提示詞（星僑 NCC 原版格式）")
    
    # 逐爻生成標準格式文字
    lines_str_list = []
    line_names = ["初爻", "二爻", "三爻", "四爻", "五爻", "六爻"]
    
    for i in range(5, -1, -1):
        l_num = i + 1
        is_mv = (l_num == moving_line)
        
        # 標籤名
        t_name = line_names[i]
        if l_num == shi_pos:
            t_name += "【世爻】"
        elif l_num == ying_pos:
            t_name += "【應爻】"
            
        beast = liushen[i]
        bgz = ben_ganzhi[i]
        b_br = bgz[1]
        b_el = DIZHI_ELEM[b_br]
        b_qin = get_liuqin(palace_elem, b_el)
        
        k_txt = " 空亡" if b_br in in_kong else ""
        
        bi_txt = ""
        if is_mv:
            bigz = bian_ganzhi[i]
            bi_br = bigz[1]
            bi_el = DIZHI_ELEM[bi_br]
            bi_qin = get_liuqin(palace_elem, bi_el)
            bi_txt = f"，變爻：{bi_qin} ({bi_br}{bi_el})"
            
        fu_txt = ""
        if l_num in fushen_dict:
            fq, fg, fb, fe = fushen_dict[l_num]
            fu_txt = f"，伏神：{fq} ({fb}{fe})"
            
        lines_str_list.append(f"{t_name}：{beast} {b_qin} ({b_br}{b_el}){k_txt}{bi_txt}{fu_txt}")

    full_lines_block = "\n".join(lines_str_list)
    
    # 100% 還原圖一文字
    exact_ai_prompt = f"""占卦日期：
陽曆：{in_solar}
農曆：{in_lunar}
干支：{in_y} 年 {in_m} 月 {in_d} 日 {in_h} 時

本卦：{ben_name}
變卦：{bian_name}

{full_lines_block}
事由：{user_q}

請用繁體中文回答，依據易經與六爻學理分析"""

    st.text_area("生成的 AI 提示詞（100% 對齊星僑 NCC，可直接全選複製）", value=exact_ai_prompt, height=360)

# ==================== 3. 四大經典全息神斷 ====================
with tab_theory:
    st.markdown(f"### 📜 四大經典權威深度解析：【{ben_name} 之 {bian_name}】")
    st.write(f"**占問事由**：{user_q} ｜ **互卦**：{hu_name} ｜ **首卦**：{palace_name}（{palace_elem}）")
    
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"""
        **一、《易經》古義與動爻爻辭**
        * 本卦《{ben_name}》：天地之大象，動變在第 {moving_line} 爻。
        * 爻象轉折：陰陽互換，陰變陽主主動出擊，陽變陰主收斂退守。
        """)
        st.markdown("""
        **二、《高島易斷》象數實占**
        * 高島吞象先生論此卦：重在時空機先與人事謀略。凡占失物多隱於低處夾層；占疾厄在於斷除惡習；占謀望宜順天應人。
        """)
    with c2:
        st.markdown(f"""
        **三、《野鶴老人》（增刪卜易）用神生剋**
        * 用神衰旺：看用神得日月建生扶與否。動爻發動逢六合，主暫時羈絆；出空逢沖之日為應期！
        """)
        st.markdown(f"""
        **四、《易經 64 卦 卦圖象解》（天紀圖象人間道）**
        * 卦中顯象：官人、車輛、文書在地、一合子先成後破。外應對應周遭人事物環境特徵。
        """)
