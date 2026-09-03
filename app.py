# -*- coding: utf-8 -*-
"""
星僑 (NCC) 卜卦命理 App · 向量圖形介面 (GUI) 引擎
修復：文字索引溢出 (IndexError)，支援動態字數垂直排版
"""
import streamlit as st
from datetime import datetime

st.set_page_config(
    page_title="星僑 (NCC) 占卦圖形介面",
    page_icon="☯️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .block-container { padding-top: 1rem; padding-bottom: 2rem; }
    .gui-card { display: flex; justify-content: center; align-items: center; margin: 10px 0; }
</style>
""", unsafe_allow_html=True)

# --- 輔助函式：安全垂直文字生成（解決 IndexError） ---
def make_vert_svg(text, x, y_start, font_size=14, color="#111111", line_gap=19, max_chars=8):
    if not text:
        return ""
    safe_text = str(text)[:max_chars]
    svg_pieces = []
    for idx, ch in enumerate(safe_text):
        y_pos = y_start + (idx * line_gap)
        svg_pieces.append(f'<text x="{x}" y="{y_pos}" font-size="{font_size}" font-weight="bold" fill="{color}" text-anchor="middle">{ch}</text>')
    return "".join(svg_pieces)

# --- 側邊控制欄 ---
st.sidebar.markdown("### 🎛️ 起卦參數設定")
case_mode = st.sidebar.selectbox("切換卦例", [
    "範例 1：悠遊卡遺失 (圖一截圖 1:1 復刻)",
    "範例 2：54 12 65 (雷水解 之 澤水困，問健康)",
    "自訂三組數字"
])

if case_mode == "範例 1：悠遊卡遺失 (圖一截圖 1:1 復刻)":
    c_n1, c_n2, c_n3 = 29, 34, 19
    c_solar = "2019/12/10 22:00"
    c_lunar = "2019 年 11 月 15 日亥時"
    c_y, c_m, c_d, c_h = "己亥", "丙子", "辛巳", "己亥"
    c_q = "悠遊卡遺失地點"
    c_ben, c_bian, c_shou, c_hu = "澤風大過", "澤天夬", "震為雷", "乾為天"
    c_shou_el, c_ben_type = "木", "游"
    c_moving = 1
    c_shi = 4
    c_ying = 1
    c_kong = "申酉"
elif case_mode == "範例 2：54 12 65 (雷水解 之 澤水困，問健康)":
    c_n1, c_n2, c_n3 = 54, 12, 65
    c_solar = "2026/09/03 16:21"
    c_lunar = "2026 年 07 月 22 日申時"
    c_y, c_m, c_d, c_h = "丙午", "丙申", "庚辰", "甲申"
    c_q = "問身體健康注意事項"
    c_ben, c_bian, c_shou, c_hu = "雷水解", "澤水困", "震為雷", "水火既濟"
    c_shou_el, c_ben_type = "木", "二世"
    c_moving = 5
    c_shi = 2
    c_ying = 5
    c_kong = "申酉"
else:
    c_n1, c_n2, c_n3 = 54, 12, 65
    c_solar = datetime.now().strftime("%Y/%m/%d %H:%M")
    c_lunar = "歲次時令"
    c_y, c_m, c_d, c_h = "丙午", "丙申", "庚辰", "甲申"
    c_q = "請輸入問事事由"
    c_ben, c_bian, c_shou, c_hu = "雷水解", "澤水困", "震為雷", "水火既濟"
    c_shou_el, c_ben_type = "木", "二世"
    c_moving = 5
    c_shi = 2
    c_ying = 5
    c_kong = "申酉"

col1, col2, col3 = st.sidebar.columns(3)
n1 = col1.number_input("第1組(下)", value=c_n1, min_value=1)
n2 = col2.number_input("第2組(上)", value=c_n2, min_value=1)
n3 = col3.number_input("第3組(動)", value=c_n3, min_value=1)
user_q = st.sidebar.text_input("問事事由", value=c_q)

# --- 產生純圖形介面 (SVG Vector Graphic) ---
def render_ncc_svg(ben_name, bian_name, shou_name, shou_el, hu_name, ben_type, matter, y_str, m_str, d_str, date_str, moving_line, shi_pos, ying_pos):
    # 定義六爻資料（以圖一澤風大過為基準）
    lines_data = [
        ("白虎", "妻財", "應", "dong_yin", "辛", "丑", "土", False, "甲", "子", "父母", "合", "", "", "", ""),
        ("玄武", "父母", "", "yang", "辛", "亥", "水", False, "", "", "", "", "庚", "寅", "木", "兄弟"),
        ("青龍", "官鬼", "", "yang", "辛", "酉", "金", True, "", "", "", "", "", "", "", ""),
        ("朱雀", "父母", "世", "yang", "丁", "亥", "水", False, "", "", "", "", "庚", "午", "火", "子孫"),
        ("勾陳", "官鬼", "", "yang", "丁", "酉", "金", True, "", "", "", "", "", "", "", ""),
        ("滕蛇", "妻財", "", "yin", "丁", "未", "土", False, "", "", "", "", "", "", "", "")
    ]
    
    # 若為雷水解案例切換
    if ben_name == "雷水解":
        lines_data = [
            ("白虎", "兄弟", "", "yin", "戊", "寅", "木", False, "", "", "", "", "庚", "子", "水", "父母"),
            ("玄武", "妻財", "世", "yang", "戊", "辰", "土", False, "", "", "", "", "", "", "", ""),
            ("青龍", "子孫", "", "yin", "戊", "午", "火", False, "", "", "", "", "", "", "", ""),
            ("朱雀", "子孫", "", "yang", "庚", "午", "火", False, "", "", "", "", "", "", "", ""),
            ("勾陳", "官鬼", "應", "dong_yin", "庚", "申", "金", True, "丁", "酉", "官鬼", "", "", "", "", ""),
            ("滕蛇", "妻財", "", "yin", "庚", "戌", "土", False, "", "", "", "", "", "", "", "")
        ]

    W = 460
    H = 820

    svg = f"""
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="100%" max-width="480" style="background:#ffffff; font-family:'Microsoft JhengHei',sans-serif; border:2px solid #555; box-shadow:0 6px 16px rgba(0,0,0,0.15);">
        <!-- 頂部標題列 -->
        <rect x="0" y="0" width="{W}" height="42" fill="#f4f4f4" stroke="#777" stroke-width="1"/>
        <text x="18" y="27" font-size="20" fill="#666">〈</text>
        <text x="{W/2}" y="27" font-size="18" font-weight="bold" fill="#111" text-anchor="middle">占卦功能</text>
        <rect x="{W-68}" y="8" width="54" height="26" rx="4" fill="#e5e5e5" stroke="#999" stroke-width="1"/>
        <text x="{W-41}" y="26" font-size="14" font-weight="bold" fill="#111" text-anchor="middle">解析</text>

        <!-- 表頭 -->
        <rect x="0" y="42" width="{W}" height="30" fill="#ffffff" stroke="#777" stroke-width="1"/>
    """

    # 表頭欄位
    headers = [
        (16, "六\\n獸"), (48, "六\\n親"), (78, "世\\n應"), (112, "NCC\\n星僑"), 
        (155, "裝\\n卦"), (201, "變\\n卦"), (240, "六\\n親"), (278, "伏\\n神"), (315, "六\\n親")
    ]
    for x, t in headers:
        parts = t.split("\\n")
        svg += f'<text x="{x}" y="55" font-size="12" font-weight="bold" fill="#111" text-anchor="middle">{parts[0]}</text>'
        svg += f'<text x="{x}" y="68" font-size="12" font-weight="bold" fill="#111" text-anchor="middle">{parts[1]}</text>'

    # 右上角 年月日
    svg += f"""
        <text x="343" y="55" font-size="13" fill="#111" text-anchor="middle">日</text>
        <text x="343" y="69" font-size="12" font-weight="bold" fill="#111" text-anchor="middle">{d_str}</text>
        <text x="369" y="55" font-size="13" fill="#111" text-anchor="middle">月</text>
        <text x="369" y="69" font-size="12" font-weight="bold" fill="#111" text-anchor="middle">{m_str}</text>
        <text x="395" y="55" font-size="13" fill="#111" text-anchor="middle">年</text>
        <text x="395" y="69" font-size="12" font-weight="bold" fill="#111" text-anchor="middle">{y_str}</text>
        <rect x="330" y="72" width="80" height="18" fill="#ffffff" stroke="#777" stroke-width="0.8"/>
        <text x="370" y="85" font-size="11" fill="#cc0000" font-weight="bold" text-anchor="middle">{date_str.split(' ')[0]}</text>
    """

    # 繪製六爻 (Y: 72 到 402)
    row_h = 55
    y_start = 72

    for idx, row in enumerate(reversed(lines_data)):
        y = y_start + idx * row_h
        beast, qin, sy, sym, z_gan, z_zhi, z_el, kong, bi_gan, bi_zhi, bi_qin, he, fu_gan, fu_zhi, fu_el, fu_qin = row

        svg += f'<line x1="0" y1="{y+row_h}" x2="330" y2="{y+row_h}" stroke="#777" stroke-width="1"/>'

        # 六獸
        svg += f'<text x="16" y="{y+32}" font-size="15" font-weight="bold" fill="#800080" text-anchor="middle">{beast[0]}</text>'
        svg += f'<text x="16" y="{y+46}" font-size="15" font-weight="bold" fill="#800080" text-anchor="middle">{beast[1]}</text>'

        # 六親
        svg += f'<text x="48" y="{y+32}" font-size="15" font-weight="bold" fill="#8b2500" text-anchor="middle">{qin[0]}</text>'
        svg += f'<text x="48" y="{y+46}" font-size="15" font-weight="bold" fill="#8b2500" text-anchor="middle">{qin[1]}</text>'

        # 世應
        if sy:
            svg += f'<text x="78" y="{y+36}" font-size="18" font-weight="bold" fill="#cc0000" text-anchor="middle">{sy}</text>'

        # 爻象符號 (星僑斜線)
        if sym == "yang":
            svg += f'<line x1="98" y1="{y+38}" x2="126" y2="{y+20}" stroke="#0000cc" stroke-width="4.5" stroke-linecap="round"/>'
        elif sym == "yin":
            svg += f'<line x1="96" y1="{y+40}" x2="110" y2="{y+28}" stroke="#0000cc" stroke-width="4.5" stroke-linecap="round"/>'
            svg += f'<line x1="114" y1="{y+28}" x2="128" y2="{y+16}" stroke="#0000cc" stroke-width="4.5" stroke-linecap="round"/>'
        elif sym == "dong_yin":
            svg += f'<line x1="98" y1="{y+18}" x2="126" y2="{y+42}" stroke="#0000cc" stroke-width="5" stroke-linecap="round"/>'
            svg += f'<line x1="98" y1="{y+42}" x2="126" y2="{y+18}" stroke="#0000cc" stroke-width="5" stroke-linecap="round"/>'

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

    # 垂直格線
    col_x = [32, 64, 92, 132, 178, 224, 256, 300, 330]
    for cx in col_x:
        svg += f'<line x1="{cx}" y1="42" x2="{cx}" y2="402" stroke="#777" stroke-width="1"/>'

    # 右側直欄（安全垂直排版，徹底杜絕 IndexError）
    bian_svg_text = make_vert_svg(bian_name, 343, 185, font_size=15, color="#cc0000", line_gap=20)
    ben_svg_text  = make_vert_svg(ben_name, 369, 185, font_size=15, color="#000080", line_gap=20)
    shou_svg_text = make_vert_svg(shou_name, 396, 170, font_size=14, color="#cc0000", line_gap=18)
    hu_svg_text   = make_vert_svg(hu_name, 396, 325, font_size=14, color="#78237b", line_gap=18)
    matter_svg    = make_vert_svg(matter, 435, 105, font_size=13, color="#78237b", line_gap=20, max_chars=8)

    svg += f"""
        <!-- 變卦直欄 -->
        <rect x="330" y="90" width="26" height="312" fill="#ffffff" stroke="#777" stroke-width="1"/>
        <text x="343" y="115" font-size="13" font-weight="bold" fill="#111" text-anchor="middle">變</text>
        <text x="343" y="133" font-size="13" font-weight="bold" fill="#111" text-anchor="middle">卦</text>
        {bian_svg_text}

        <!-- 本卦直欄 -->
        <rect x="356" y="90" width="26" height="312" fill="#ffffff" stroke="#777" stroke-width="1"/>
        <text x="369" y="115" font-size="13" font-weight="bold" fill="#111" text-anchor="middle">本</text>
        <rect x="358" y="125" width="22" height="18" fill="#1d4ed8" rx="2"/>
        <text x="369" y="138" font-size="12" font-weight="bold" fill="#ffffff" text-anchor="middle">{ben_type}</text>
        {ben_svg_text}

        <!-- 首卦與互卦 -->
        <rect x="382" y="90" width="28" height="156" fill="#ffffff" stroke="#777" stroke-width="1"/>
        <text x="396" y="112" font-size="13" font-weight="bold" fill="#111" text-anchor="middle">首</text>
        <rect x="385" y="122" width="22" height="18" fill="#8b4513" rx="2"/>
        <text x="396" y="135" font-size="12" font-weight="bold" fill="#ffffff" text-anchor="middle">{shou_el}</text>
        {shou_svg_text}

        <rect x="382" y="246" width="28" height="156" fill="#ffffff" stroke="#777" stroke-width="1"/>
        <text x="396" y="268" font-size="13" font-weight="bold" fill="#111" text-anchor="middle">互</text>
        <rect x="385" y="278" width="22" height="18" fill="#2563eb" rx="2"/>
        <text x="396" y="291" font-size="12" font-weight="bold" fill="#ffffff" text-anchor="middle">沖</text>
        {hu_svg_text}

        <!-- 事由直欄 -->
        <rect x="410" y="42" width="50" height="360" fill="#ffffff" stroke="#777" stroke-width="1"/>
        <text x="435" y="65" font-size="13" font-weight="bold" fill="#111" text-anchor="middle">事</text>
        <text x="435" y="80" font-size="13" font-weight="bold" fill="#111" text-anchor="middle">由</text>
        {matter_svg}

        <!-- 底部神煞區域 (402 ~ 820) -->
        <rect x="0" y="402" width="{W}" height="418" fill="#ffffff" stroke="#555" stroke-width="2"/>
        
        <!-- 左側：月令親神十二運 -->
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

        <!-- 中間：十二神煞方陣 -->
        <rect x="160" y="402" width="29" height="75" fill="#fff" stroke="#777" stroke-width="0.8"/>
        <text x="174" y="418" font-size="12" fill="#111" text-anchor="middle">日</text>
        <text x="174" y="432" font-size="12" fill="#111" text-anchor="middle">沖</text>
        <text x="174" y="462" font-size="15" font-weight="bold" fill="#0000cc" text-anchor="middle">亥</text>

        <rect x="189" y="402" width="29" height="75" fill="#fff" stroke="#777" stroke-width="0.8"/>
        <text x="203" y="418" font-size="12" fill="#111" text-anchor="middle">月</text>
        <text x="203" y="432" font-size="12" fill="#111" text-anchor="middle">破</text>
        <text x="203" y="462" font-size="15" font-weight="bold" fill="#cc0000" text-anchor="middle">午</text>

        <rect x="218" y="402" width="29" height="75" fill="#fff" stroke="#777" stroke-width="0.8"/>
        <text x="232" y="418" font-size="12" fill="#111" text-anchor="middle">桃</text>
        <text x="232" y="432" font-size="12" fill="#111" text-anchor="middle">花</text>
        <text x="232" y="462" font-size="15" font-weight="bold" fill="#cc0000" text-anchor="middle">午</text>

        <rect x="247" y="402" width="29" height="75" fill="#fff" stroke="#777" stroke-width="0.8"/>
        <text x="261" y="418" font-size="12" fill="#111" text-anchor="middle">劫</text>
        <text x="261" y="432" font-size="12" fill="#111" text-anchor="middle">煞</text>
        <text x="261" y="462" font-size="15" font-weight="bold" fill="#008000" text-anchor="middle">寅</text>

        <rect x="276" y="402" width="29" height="75" fill="#fff" stroke="#777" stroke-width="0.8"/>
        <text x="290" y="418" font-size="12" fill="#111" text-anchor="middle">驛</text>
        <text x="290" y="432" font-size="12" fill="#111" text-anchor="middle">馬</text>
        <text x="290" y="462" font-size="15" font-weight="bold" fill="#0000cc" text-anchor="middle">亥</text>

        <rect x="305" y="402" width="30" height="75" fill="#fff" stroke="#777" stroke-width="0.8"/>
        <text x="320" y="418" font-size="12" fill="#111" text-anchor="middle">卦</text>
        <text x="320" y="432" font-size="12" fill="#111" text-anchor="middle">身</text>
        <text x="320" y="462" font-size="15" font-weight="bold" fill="#008000" text-anchor="middle">卯</text>

        <rect x="160" y="477" width="29" height="76" fill="#fff" stroke="#777" stroke-width="0.8"/>
        <text x="174" y="493" font-size="12" fill="#111" text-anchor="middle">空</text>
        <text x="174" y="507" font-size="12" fill="#111" text-anchor="middle">亡</text>
        <text x="174" y="528" font-size="14" font-weight="bold" fill="#b8860b" text-anchor="middle">申</text>
        <text x="174" y="546" font-size="14" font-weight="bold" fill="#b8860b" text-anchor="middle">酉</text>

        <rect x="189" y="477" width="29" height="76" fill="#fff" stroke="#777" stroke-width="0.8"/>
        <text x="203" y="493" font-size="12" fill="#111" text-anchor="middle">羊</text>
        <text x="203" y="507" font-size="12" fill="#111" text-anchor="middle">刃</text>
        <text x="203" y="538" font-size="15" font-weight="bold" fill="#800000" text-anchor="middle">戌</text>

        <rect x="218" y="477" width="29" height="76" fill="#fff" stroke="#777" stroke-width="0.8"/>
        <text x="232" y="493" font-size="12" fill="#111" text-anchor="middle">干</text>
        <text x="232" y="507" font-size="12" fill="#111" text-anchor="middle">祿</text>
        <text x="232" y="538" font-size="15" font-weight="bold" fill="#b8860b" text-anchor="middle">酉</text>

        <rect x="247" y="477" width="29" height="76" fill="#fff" stroke="#777" stroke-width="0.8"/>
        <text x="261" y="493" font-size="12" fill="#111" text-anchor="middle">往</text>
        <text x="261" y="507" font-size="12" fill="#111" text-anchor="middle">亡</text>
        <text x="261" y="538" font-size="15" font-weight="bold" fill="#800000" text-anchor="middle">戌</text>

        <rect x="276" y="477" width="29" height="76" fill="#fff" stroke="#777" stroke-width="0.8"/>
        <text x="290" y="493" font-size="12" fill="#111" text-anchor="middle">天</text>
        <text x="290" y="507" font-size="12" fill="#111" text-anchor="middle">喜</text>
        <text x="290" y="538" font-size="15" font-weight="bold" fill="#800000" text-anchor="middle">未</text>

        <rect x="305" y="477" width="30" height="76" fill="#fff" stroke="#777" stroke-width="0.8"/>
        <text x="320" y="493" font-size="12" fill="#111" text-anchor="middle">貴</text>
        <text x="320" y="507" font-size="12" fill="#111" text-anchor="middle">人</text>
        <text x="320" y="528" font-size="14" font-weight="bold" fill="#008000" text-anchor="middle">寅</text>
        <text x="320" y="546" font-size="14" font-weight="bold" fill="#cc0000" text-anchor="middle">午</text>

        <!-- 右側：八字大運 (335 ~ 460) -->
        <rect x="335" y="402" width="125" height="151" fill="#ffffff" stroke="#777" stroke-width="1"/>
        <text x="397" y="420" font-size="14" font-weight="bold" fill="#111" text-anchor="middle">八  字</text>
        
        <text x="350" y="445" font-size="14" font-weight="bold" fill="#111">庚</text>
        <text x="350" y="462" font-size="14" font-weight="bold" fill="#111">申</text>
        <text x="375" y="445" font-size="14" font-weight="bold" fill="#cc0000">癸</text>
        <text x="375" y="462" font-size="14" font-weight="bold" fill="#111">酉</text>
        <text x="405" y="445" font-size="14" font-weight="bold" fill="#111">己</text>
        <text x="405" y="462" font-size="14" font-weight="bold" fill="#111">卯</text>
        <text x="435" y="445" font-size="14" font-weight="bold" fill="#111">乙</text>
        <text x="435" y="462" font-size="14" font-weight="bold" fill="#111">未</text>

        <line x1="335" y1="475" x2="460" y2="475" stroke="#ccc" stroke-width="0.8"/>
        <text x="397" y="490" font-size="9" fill="#666" text-anchor="middle">93 83 73 63 53 43 33 23 13 3</text>
        <text x="397" y="515" font-size="9" fill="#999" text-anchor="middle">己 庚 辛 壬 癸 甲 乙 丙 丁 戊</text>
        <text x="397" y="535" font-size="9" fill="#999" text-anchor="middle">巳 午 未 申 酉 戌 亥 子 丑 寅</text>
    </svg>
    """
    return svg

# --- 頁面輸出 ---
st.markdown("<h2 style='text-align:center; color:#800000; margin-bottom:10px;'>🏛️ 星僑 (NCC) 六爻占卦純圖形介面</h2>", unsafe_allow_html=True)

tab_gui, tab_ai_text = st.tabs(["📱 純圖形畫面 (1:1 復刻星僑 App)", "📋 卜卦 AI 提示詞 (一鍵複製)"])

with tab_gui:
    svg_code = render_ncc_svg(
        c_ben, c_bian, c_shou, c_shou_el, c_hu, c_ben_type,
        user_q, c_y, c_m, c_d, c_solar, c_moving, c_shi, c_ying
    )
    st.markdown(f"<div class='gui-card'>{svg_code}</div>", unsafe_allow_html=True)

with tab_ai_text:
    st.markdown("### 📋 卜卦 AI 提示詞（星僑原版）")
    txt = f"""占卦日期：
陽曆：{c_solar}
農曆：{c_lunar}
干支：{c_y} 年 {c_m} 月 {c_d} 日 {c_h} 時

本卦：{c_ben}
變卦：{c_bian}

六爻：滕蛇 妻財 (未土)
五爻：勾陳 官鬼 (酉金) 空亡
四爻【世爻】：朱雀 父母 (亥水)，伏神：子孫 (午火)
三爻：青龍 官鬼 (酉金) 空亡
二爻：玄武 父母 (亥水)，伏神：兄弟 (寅木)
初爻【應爻】：白虎 妻財 (丑土)，變爻：父母 (子水)
事由：{user_q}

請用繁體中文回答，依據易經與六爻學理分析"""
    st.text_area("提示詞內容", value=txt, height=300)
