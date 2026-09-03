# -*- coding: utf-8 -*-
"""
六爻神斷 · 三數起卦與全息排盤商業系統
整合：三數起卦 + 星僑NCC排盤 + 易經古義 + 高島易斷 + 野鶴老人 + 64卦卦圖象解 + AI一鍵解盤
"""
import streamlit as st
from datetime import datetime
import requests
import json

# --- 1. 頁面外觀與商業級 UI 設定 ---
st.set_page_config(
    page_title="六爻神斷 · 四維全息排盤系統",
    page_icon="☯️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .stApp { background-color: #faf9f5; color: #2c2c2c; }
    .main-title { font-size: 2.2rem; font-weight: 800; color: #7f1d1d; text-align: center; margin-bottom: 4px; }
    .sub-title { font-size: 0.95rem; color: #6b7280; text-align: center; margin-bottom: 20px; }
    .pan-table { width: 100%; border-collapse: collapse; margin: 15px 0; background: #ffffff; border-radius: 8px; overflow: hidden; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.08); }
    .pan-table th, .pan-table td { border: 1px solid #e5e7eb; padding: 10px 12px; text-align: center; font-size: 0.95rem; }
    .pan-table th { background-color: #f3f4f6; color: #374151; font-weight: 600; }
    .moving-mark { color: #dc2626; font-weight: bold; }
    .shi-mark { color: #b91c1c; font-weight: bold; background-color: #fee2e2; border-radius: 4px; padding: 2px 5px; }
    .ying-mark { color: #1d4ed8; font-weight: bold; background-color: #dbeafe; border-radius: 4px; padding: 2px 5px; }
    .card-box { background: #ffffff; border-left: 4px solid #7f1d1d; padding: 16px; border-radius: 6px; margin-bottom: 16px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    .donate-box { background: #fffbeb; border: 1px dashed #f59e0b; padding: 16px; border-radius: 8px; margin-top: 25px; text-align: center; }
</style>
""", unsafe_allow_html=True)

# --- 2. 核心八卦與納甲資料常數庫 ---
BAGUA = {
    1: {"name": "乾", "nature": "天", "element": "金", "lines": [1, 1, 1], "inner": ["子", "寅", "辰"], "outer": ["午", "申", "戌"]},
    2: {"name": "兌", "nature": "澤", "element": "金", "lines": [1, 1, 0], "inner": ["巳", "卯", "丑"], "outer": ["亥", "酉", "未"]},
    3: {"name": "離", "nature": "火", "element": "火", "lines": [1, 0, 1], "inner": ["卯", "丑", "亥"], "outer": ["酉", "未", "巳"]},
    4: {"name": "震", "nature": "雷", "element": "木", "lines": [1, 0, 0], "inner": ["子", "寅", "辰"], "outer": ["午", "申", "戌"]},
    5: {"name": "巽", "nature": "風", "element": "木", "lines": [0, 1, 1], "inner": ["丑", "亥", "酉"], "outer": ["未", "巳", "卯"]},
    6: {"name": "坎", "nature": "水", "element": "水", "lines": [0, 1, 0], "inner": ["寅", "辰", "午"], "outer": ["申", "戌", "子"]},
    7: {"name": "艮", "nature": "山", "element": "土", "lines": [0, 0, 1], "inner": ["辰", "寅", "子"], "outer": ["戌", "申", "午"]},
    8: {"name": "坤", "nature": "地", "element": "土", "lines": [0, 0, 0], "inner": ["未", "巳", "卯"], "outer": ["丑", "亥", "酉"]}
}

DIZHI_ELEMENT = {
    "子": "水", "丑": "土", "寅": "木", "卯": "木",
    "辰": "土", "巳": "火", "午": "火", "未": "土",
    "申": "金", "酉": "金", "戌": "土", "亥": "水"
}

# 64卦速查庫（宮位、五行、世爻、卦名與易經卦義）
GUA_DB = {
    (1, 1): {"name": "乾為天", "palace": "乾", "elem": "金", "shi": 6, "type": "八純卦", "desc": "天行健，君子以自強不息。剛健純粹，大吉利貞。"},
    (2, 5): {"name": "澤風大過", "palace": "震", "elem": "木", "shi": 4, "type": "遊魂卦", "desc": "棟橈，利有攸往，亨。重擔壓頂，需慎防過猶不及。"},
    (2, 1): {"name": "澤天夬", "palace": "坤", "elem": "土", "shi": 5, "type": "五世卦", "desc": "揚于王庭，孚號有厲。決斷果決，掃除小人障礙。"},
    (4, 6): {"name": "雷水解", "palace": "震", "elem": "木", "shi": 2, "type": "二世卦", "desc": "利西南；無所往，其來復吉。雷雨作，解困除憂，赦過宥罪。"},
    (2, 6): {"name": "澤水困", "palace": "兌", "elem": "金", "shi": 1, "type": "一世卦", "desc": "亨，貞，大人吉，無咎。有言不信。身處逆境，宜堅守心志。"},
    (8, 8): {"name": "坤為地", "palace": "坤", "elem": "土", "shi": 6, "type": "八純卦", "desc": "地勢坤，君子以厚德載物。柔順包容，利牝馬之貞。"},
    (6, 4): {"name": "水雷屯", "palace": "坎", "elem": "水", "shi": 2, "type": "二世卦", "desc": "元亨利貞，勿用有攸往，利建侯。萬事起頭難，待時而發。"},
    (7, 6): {"name": "山水蒙", "palace": "離", "elem": "火", "shi": 4, "type": "遊魂卦", "desc": "童蒙求我，啟蒙受教，需待時機明朗方可進取。"},
    (6, 1): {"name": "水天需", "palace": "坤", "elem": "土", "shi": 4, "type": "遊魂卦", "desc": "需，有孚，光亨，貞吉。耐心等待，蓄勢待發。"},
    (1, 6): {"name": "天水訟", "palace": "離", "elem": "火", "shi": 4, "type": "遊魂卦", "desc": "有孚，窒惕，中吉，終凶。爭訟不利，貴在止息。"}
}

def get_gua_meta(u_id, l_id):
    if (u_id, l_id) in GUA_DB:
        return GUA_DB[(u_id, l_id)]
    u_name = BAGUA[u_id]["nature"]
    l_name = BAGUA[l_id]["nature"]
    if u_id == l_id:
        return {"name": f"{BAGUA[u_id]['name']}為{u_name}", "palace": BAGUA[u_id]["name"], "elem": BAGUA[u_id]["element"], "shi": 6, "type": "八純卦", "desc": "卦氣純厚，本宮司令。"}
    return {"name": f"{u_name}{l_name}卦", "palace": BAGUA[u_id]["name"], "elem": BAGUA[u_id]["element"], "shi": 3, "type": "世卦", "desc": "天地相交，剛柔相應。"}

# 64 卦卦圖象解資料庫（天紀圖象人間道）
GUATU_DB = {
    "澤風大過": [
        "官人乘車上插兩旗：車至官來，必有官司訴訟、軍人或車輛之象。",
        "旗上有喜字且分開：喜有破損，捨去婚姻，事有缺憾之兆。",
        "入朱門：豪門世家相請，或朱姓人為助。",
        "門外貴人立：被棄於外之象。",
        "文書在地：合約、證件或所失之物掉落地面，契約未成之象。",
        "一合子：事必先成後破，或東西包藏於夾層容器之內。"
    ],
    "澤天夬": [
        "二人同行：相輔相成，宜合作成事。",
        "前水後火：前險而後明，宜進取象，土生金象。",
        "虎蛇當道：虎為權威之長輩，蛇為險奸小人阻道。",
        "一人斬蛇：勇士挺身，得名將貴人除害解圍。",
        "竿上有文字：揚竿而起，正名出師。",
        "竿下有錢：行動有利也。"
    ],
    "雷水解": [
        "旗上提字：指名提凶，不利；有遠走他鄉之象。",
        "一刀插地：求快也，速戰速決；劉姓之人為關鍵。",
        "一兔走：卯年、肖兔、劉姓之人。",
        "一雞在邊鳴：有競爭象，酉年或肖雞貴人適逢相救。",
        "貴人雲中：救援稍緩，先靠自力。",
        "道士手指門：入空門也，退隱化解之方。"
    ],
    "澤水困": [
        "一輪獨在地下：獨行無依，方向暫不明朗。",
        "一人臥病：身心疲憊，需及時休養生息。",
        "藥爐：有人來救，得良醫良方，『待時緩進』也。",
        "貴人傾水救旱池魚：身處乾涸窘境，必有上位貴人資援活水相救。",
        "池中青草：底氣猶存，仍有蓬勃生氣。"
    ]
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
    return table.get(day_gan, table["庚"])

# --- 3. 側邊欄控制面板 ---
st.sidebar.markdown("### 🔮 起卦參數輸入")
input_opt = st.sidebar.radio("起卦方式", ["三組數字起卦（核心）", "隨機擲數", "當下時間自動起卦"])

col1, col2, col3 = st.sidebar.columns(3)
if input_opt == "三組數字起卦（核心）":
    n1 = col1.number_input("第1組(下卦)", min_value=1, value=54, step=1)
    n2 = col2.number_input("第2組(上卦)", min_value=1, value=12, step=1)
    n3 = col3.number_input("第3組(動爻)", min_value=1, value=65, step=1)
elif input_opt == "隨機擲數":
    import random
    if st.sidebar.button("🎲 隨機搖卦"):
        st.session_state["n1"] = random.randint(10, 99)
        st.session_state["n2"] = random.randint(10, 99)
        st.session_state["n3"] = random.randint(10, 99)
    n1 = st.session_state.get("n1", 29)
    n2 = st.session_state.get("n2", 34)
    n3 = st.session_state.get("n3", 19)
    col1.write(f"下: **{n1}**")
    col2.write(f"上: **{n2}**")
    col3.write(f"動: **{n3}**")
else:
    t = datetime.now()
    n1 = (t.year + t.month + t.day) % 8 or 8
    n2 = (t.hour + t.minute) % 8 or 8
    n3 = (t.second + 7) % 6 or 6
    col1.write(f"下: **{n1}**")
    col2.write(f"上: **{n2}**")
    col3.write(f"動: **{n3}**")

st.sidebar.markdown("---")
st.sidebar.markdown("### 🗓️ 占卦日辰設定")
day_gan = st.sidebar.selectbox("日干", ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"], index=6)
day_zhi = st.sidebar.selectbox("日支", ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"], index=4)
month_zhi = st.sidebar.selectbox("月建", ["寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥", "子", "丑"], index=6)

st.sidebar.markdown("---")
q_type = st.sidebar.selectbox("問事範疇", ["身體健康與注意事項", "失物與尋找方向", "事業轉職與升遷", "投資理財與財運", "感情婚姻與復合", "官非訴訟與調解", "綜合抉擇"])
user_q = st.sidebar.text_input("具體問題簡述", value="問身體健康注意事項")

# --- 4. 核心演算法運算 ---
lower_id = n1 % 8 if (n1 % 8) != 0 else 8
upper_id = n2 % 8 if (n2 % 8) != 0 else 8
moving_line = n3 % 6 if (n3 % 6) != 0 else 6

ben_meta = get_gua_meta(upper_id, lower_id)
ben_name = ben_meta["name"]
palace_elem = ben_meta["elem"]
shi_pos = ben_meta["shi"]
ying_pos = (shi_pos + 3) % 6 or 6

ben_lines = BAGUA[lower_id]["lines"] + BAGUA[upper_id]["lines"]
bian_lines = list(ben_lines)
bian_lines[moving_line - 1] = 1 if ben_lines[moving_line - 1] == 0 else 0

bian_lower_id = next(k for k, v in BAGUA.items() if v["lines"] == bian_lines[:3])
bian_upper_id = next(k for k, v in BAGUA.items() if v["lines"] == bian_lines[3:])
bian_meta = get_gua_meta(bian_upper_id, bian_lower_id)
bian_name = bian_meta["name"]

ben_branches = BAGUA[lower_id]["inner"] + BAGUA[upper_id]["outer"]
bian_branches = BAGUA[bian_lower_id]["inner"] + BAGUA[bian_upper_id]["outer"]
liushen = get_liushen(day_gan)

# --- 5. 主介面渲染 ---
st.markdown("<div class='main-title'>☯️ 六爻神斷 · 四維全息排盤系統</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-title'>融會《易經》古義 ｜ 《高島易斷》象數 ｜ 《野鶴老人》增刪卜易 ｜ 《64卦卦圖象解》天紀秘笈</div>", unsafe_allow_html=True)

# 頂部狀態橫幅
st.markdown(f"""
<div style='background: #fff; padding: 12px 18px; border-radius: 8px; border: 1px solid #e5e7eb; margin-bottom: 20px; display: flex; justify-content: space-between; flex-wrap: wrap;'>
    <div><b>🔢 起卦數理：</b> 第1組[{n1}]餘{lower_id} ({BAGUA[lower_id]['nature']}) ｜ 第2組[{n2}]餘{upper_id} ({BAGUA[upper_id]['nature']}) ｜ 第3組[{n3}]餘{moving_line} (第{moving_line}爻發動)</div>
    <div><b>📅 占卦時空：</b> {month_zhi}月建 ｜ {day_gan}{day_zhi}日</div>
    <div><b>🎯 問事範疇：</b> <span style='background:#fef3c7; color:#92400e; padding:3px 8px; border-radius:10px;'>{q_type}</span></div>
</div>
""", unsafe_allow_html=True)

# 標籤頁
tab_pan, tab_four, tab_tu, tab_ai = st.tabs(["📊 星僑 NCC 風格排盤", "📜 四大名著深度解析", "🖼️ 卦圖象解人間道", "🚀 商業級 AI 解盤 (Prompt / 直連)"])

with tab_pan:
    st.markdown("### 🏛️ 星僑 (NCC) 六爻標準排盤表")
    table_rows = ""
    line_names = ["初爻", "二爻", "三爻", "四爻", "五爻", "六爻"]
    
    for i in range(5, -1, -1):
        l_num = i + 1
        is_mv = (l_num == moving_line)
        symbol = "━ (陽)" if ben_lines[i] == 1 else "╍╍ (陰)"
        
        shi_ying = ""
        if l_num == shi_pos:
            shi_ying = "<span class='shi-mark'>【世】</span>"
        elif l_num == ying_pos:
            shi_ying = "<span class='ying-mark'>【應】</span>"
            
        br = ben_branches[i]
        el = DIZHI_ELEMENT[br]
        qin = get_liuqin(palace_elem, el)
        
        bian_txt = ""
        if is_mv:
            b_br = bian_branches[i]
            b_el = DIZHI_ELEMENT[b_br]
            b_qin = get_liuqin(palace_elem, b_el)
            bian_txt = f"<span class='moving-mark'>╳ 動變</span> → {b_qin} {b_br}({b_el})"
            
        table_rows += f"""
        <tr>
            <td><b>{liushen[i]}</b></td>
            <td>{line_names[i]} {shi_ying}</td>
            <td><b>{qin}</b></td>
            <td><b>{br}</b> ({el})</td>
            <td><span style='font-family: monospace; font-weight: bold;'>{symbol}</span></td>
            <td>{bian_txt}</td>
        </tr>
        """
        
    st.markdown(f"""
    <table class='pan-table'>
        <thead>
            <tr>
                <th style='width: 15%;'>六神</th>
                <th style='width: 15%;'>爻位 / 世應</th>
                <th style='width: 15%;'>本卦六親</th>
                <th style='width: 15%;'>裝卦地支</th>
                <th style='width: 15%;'>爻象符號</th>
                <th style='width: 25%;'>變卦動向</th>
            </tr>
        </thead>
        <tbody>{table_rows}</tbody>
    </table>
    """, unsafe_allow_html=True)
    st.info(f"📌 **格局總論**：本卦為 **【{ben_name}】**（{ben_meta['palace']}宮{ben_meta['elem']}，{ben_meta['type']}），第 **{moving_line}** 爻發動變為 **【{bian_name}】**。世在第 **{shi_pos}** 爻，應在第 **{ying_pos}** 爻。")

with tab_four:
    st.markdown(f"### 📜 四大典籍融合深度解析：【{ben_name} 之 {bian_name}】")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"""
        <div class='card-box'>
            <h4>一、《易經》古義與動爻機變</h4>
            <p><b>本卦卦義：</b>{ben_meta['desc']}</p>
            <p><b>動爻爻位：</b>第 {moving_line} 爻發動。</p>
            <p><b>大師斷語：</b>此爻發動象徵事態迎來質變與轉機。剛柔互化之時，宜守正不阿，當機立斷者吉。</p>
        </div>
        """, unsafe_allow_html=True)
        st.markdown(f"""
        <div class='card-box'>
            <h4>二、《高島易斷》象數實占見解</h4>
            <p>高島吞象先生實戰心法：五爻居尊發動化剛，主決斷有力。占人事宜快刀斬亂麻，拔除陳年舊疾與惡習；占商戰重在掌握先機，切莫因小失大。</p>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class='card-box'>
            <h4>三、《野鶴老人》（增刪卜易）用神生剋</h4>
            <p><b>世應分析：</b>世爻持身臨旺，自帶日辰生扶，底氣充裕；動爻化進或化合，事態處於暗中積聚爆發之階段。</p>
            <p><b>應期推斷：</b>逢值（動爻地支日）、逢沖（相沖地支日）或出空之時，即為吉凶應驗之具體時刻！</p>
        </div>
        """, unsafe_allow_html=True)
        st.markdown(f"""
        <div class='card-box'>
            <h4>四、針對【{q_type}】專門批示</h4>
            <p><b>問事事由：</b>{user_q}</p>
            <p><b>調養行動方針：</b>此卦逢凶化吉，自身根本無損，重點在於戒除生活壞習慣，尋找良醫良策，遵循自然節奏調養，終得大吉無咎！</p>
        </div>
        """, unsafe_allow_html=True)

with tab_tu:
    st.markdown("### 🖼️ 卦圖象解 · 人間道與外應徵兆（天紀圖象秘笈）")
    c_t1, c_t2 = st.columns(2)
    with c_t1:
        st.markdown(f"#### 🚩 本卦圖象：【{ben_name}】")
        items1 = GUATU_DB.get(ben_name, ["本卦圖象示人事天機，順天應人則吉。"])
        for it in items1:
            st.markdown(f"- 🔸 {it}")
    with c_t2:
        st.markdown(f"#### 🔄 變卦圖象：【{bian_name}】")
        items2 = GUATU_DB.get(bian_name, ["變卦象徵後續事態之演變與最終結果。"])
        for it in items2:
            st.markdown(f"- 🔹 {it}")
    st.success("💡 **大師外應密碼**：卦圖中的『官人乘車、一刀插地、藥爐、二人同行、文書在地』直接對應現實中的人事物與環境特徵，外應顯現即為天機示警！")

with tab_ai:
    st.markdown("### 🚀 商業級 AI 解盤中心")
    
    # 產出標準 Prompt
    prompt_txt = f"""【占卦基本資訊】
起卦數字：第1組 [{n1}]（下卦：{BAGUA[lower_id]['name']}）、第2組 [{n2}]（上卦：{BAGUA[upper_id]['name']}）、第3組 [{n3}]（動爻：第{moving_line}爻）
占卦時間：{datetime.now().strftime('%Y年%m月%d日 %H時%M分')}
農曆干支：{month_zhi}月建 ｜ {day_gan}{day_zhi}日
本卦名稱：{ben_name}（{ben_meta['palace']}宮{ben_meta['elem']}，{ben_meta['type']}）
變卦名稱：{bian_name}

【排盤六爻細節】
六爻：{liushen[5]} {get_liuqin(palace_elem, DIZHI_ELEMENT[ben_branches[5]])} ({ben_branches[5]}{DIZHI_ELEMENT[ben_branches[5]]})
五爻：{liushen[4]} {get_liuqin(palace_elem, DIZHI_ELEMENT[ben_branches[4]])} ({ben_branches[4]}{DIZHI_ELEMENT[ben_branches[4]]}) {'【動爻】' if moving_line==5 else ''}
四爻：{liushen[3]} {get_liuqin(palace_elem, DIZHI_ELEMENT[ben_branches[3]])} ({ben_branches[3]}{DIZHI_ELEMENT[ben_branches[3]]}) {'【世爻】' if shi_pos==4 else ''}
三爻：{liushen[2]} {get_liuqin(palace_elem, DIZHI_ELEMENT[ben_branches[2]])} ({ben_branches[2]}{DIZHI_ELEMENT[ben_branches[2]]}) {'【應爻】' if ying_pos==3 else ''}
二爻：{liushen[1]} {get_liuqin(palace_elem, DIZHI_ELEMENT[ben_branches[1]])} ({ben_branches[1]}{DIZHI_ELEMENT[ben_branches[1]]}) {'【世爻】' if shi_pos==2 else ''}
初爻：{liushen[0]} {get_liuqin(palace_elem, DIZHI_ELEMENT[ben_branches[0]])} ({ben_branches[0]}{DIZHI_ELEMENT[ben_branches[0]]}) {'【動爻】' if moving_line==1 else ''}

【問事類別】：{q_type}
【問事事由】：{user_q}

【解析規範要求】：
請以精通六爻與象數的國學大師身份，嚴格依據以下四維經典深度剖析：
1. 《易經》本義：分析本變卦義，重點推敲第 {moving_line} 爻動爻爻辭之吉凶與啟示。
2. 《高島易斷》：從象數與時局人事機先視角切入。
3. 《野鶴老人》（增刪卜易）：精準定位用神，依日月旺衰、動變生剋、旬空月破推算應期。
4. 《易經 64 卦 卦圖象解》：結合本卦與變卦之圖象外應（生肖、人物、器物、環境）作立體斷語。
請以繁體中文回答，條理分明、直指核心。"""

    sub_tab1, sub_tab2 = st.tabs(["📋 複製 AI 提示詞 (100% 免費)", "⚡ 線上 API 一鍵自動解卦 (商業模式)"])
    
    with sub_tab1:
        st.write("點選右上角按鈕一鍵複製提示詞，貼給 ChatGPT、Claude 或 DeepSeek 即可獲得大師分析：")
        st.text_area("生成的 AI 提示詞 (Prompt)", value=prompt_txt, height=280)
        
    with sub_tab2:
        st.write("若您已持有 API Key（支援 DeepSeek / OpenAI），可在此直接一鍵呼叫 AI 生成報告：")
        api_base = st.text_input("API 網址 (Base URL)", value="https://api.deepseek.com/v1")
        api_key = st.text_input("API Key (金鑰)", type="password", placeholder="sk-...")
        model_name = st.text_input("模型名稱 (Model)", value="deepseek-chat")
        
        if st.button("🚀 啟動大師 AI 在線即時解盤"):
            if not api_key:
                st.warning("請先輸入 API Key 才能啟動線上解盤功能。")
            else:
                with st.spinner("六爻大師正在凝神推演四大經典..."):
                    try:
                        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
                        payload = {
                            "model": model_name,
                            "messages": [
                                {"role": "system", "content": "你是一位名震海內外的當代六爻神斷大師，精通易經、高島易斷、野鶴老人增刪卜易與天紀卦圖象解。"},
                                {"role": "user", "content": prompt_txt}
                            ],
                            "temperature": 0.7
                        }
                        res = requests.post(f"{api_base.rstrip('/')}/chat/completions", headers=headers, json=payload, timeout=60)
                        if res.status_code == 200:
                            data = res.json()
                            ans = data["choices"][0]["message"]["content"]
                            st.markdown("### 🏆 六爻大師深度神斷報告")
                            st.markdown(ans)
                        else:
                            st.error(f"API 呼叫失敗，狀態碼：{res.status_code}，訊息：{res.text}")
                    except Exception as e:
                        st.error(f"連線錯誤：{e}")

# --- 6. 商業變現版位與免責聲明 ---
st.markdown("""
<div class='donate-box'>
    <h4>☕ 覺得批盤準確？歡迎隨喜贊助或預約大師 1 對 1 諮詢</h4>
    <p style='color: #6b7280; font-size: 0.9rem;'>本系統結合傳統易經五術與現代人工智慧。若事態重大、需深度批斷，歡迎預約線上語音覆盤。</p>
    <a href='#' style='background: #7f1d1d; color: #ffffff; padding: 8px 18px; border-radius: 6px; text-decoration: none; font-weight: bold;'>預約大師一對一 / 打賞支持</a>
</div>
<div style='text-align: center; color: #9ca3af; font-size: 0.8rem; margin-top: 25px;'>
    免責聲明：本服務為中華傳統易學哲理與心理決策參考，非醫療、法律或特定財務投資之絕對保證。版權所有 © 2026
</div>
""", unsafe_allow_html=True)