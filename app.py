import os
import json
import random
import pandas as pd
import streamlit as st
from google import genai
from google.genai import types

# ---------------------------------------------------------
# ページ基本設定
# ---------------------------------------------------------
st.set_page_config(
    page_title="英単語テストメーカー",
    page_icon="📝",
    layout="wide"
)

# ---------------------------------------------------------
# 初期の111単語データ (initialWords.ts より抽出)
# ---------------------------------------------------------
INITIAL_WORDS = [
    {"id": "init-1", "word": "agreeable", "meaning": "快適な、感じの良い", "wrong_count": 0, "correct_count": 0},
    {"id": "init-2", "word": "ensemble", "meaning": "アンサンブル(少人数の合奏団)", "wrong_count": 0, "correct_count": 0},
    {"id": "init-3", "word": "accommodate", "meaning": "〜を収容する", "wrong_count": 0, "correct_count": 0},
    {"id": "init-4", "word": "acquire", "meaning": "〜を獲得する", "wrong_count": 0, "correct_count": 0},
    {"id": "init-5", "word": "emphatically", "meaning": "きっぱりと、強調して", "wrong_count": 0, "correct_count": 0},
    {"id": "init-6", "word": "nominal", "meaning": "ごくわずかの、名目だけの", "wrong_count": 0, "correct_count": 0},
    {"id": "init-7", "word": "file", "meaning": "〜を提出する", "wrong_count": 0, "correct_count": 0},
    {"id": "init-8", "word": "ensure", "meaning": "確実に〜するようになる", "wrong_count": 0, "correct_count": 0},
    {"id": "init-9", "word": "utility costs", "meaning": "光熱費", "wrong_count": 0, "correct_count": 0},
    {"id": "init-10", "word": "conventionally", "meaning": "従来の方法で、従来は", "wrong_count": 0, "correct_count": 0},
    {"id": "init-11", "word": "contractor", "meaning": "請負業者", "wrong_count": 0, "correct_count": 0},
    {"id": "init-12", "word": "solid", "meaning": "信頼できる、確かな", "wrong_count": 0, "correct_count": 0},
    {"id": "init-13", "word": "mature", "meaning": "成熟する、発達する", "wrong_count": 0, "correct_count": 0},
    {"id": "init-14", "word": "undertake", "meaning": "〜を引き受ける、〜に着手する", "wrong_count": 0, "correct_count": 0},
    {"id": "init-15", "word": "restoration", "meaning": "修復、補修", "wrong_count": 0, "correct_count": 0},
    {"id": "init-16", "word": "regrettably", "meaning": "残念ながら", "wrong_count": 0, "correct_count": 0},
    {"id": "init-17", "word": "defective", "meaning": "欠陥のある、不完全な", "wrong_count": 0, "correct_count": 0},
    {"id": "init-18", "word": "secretary", "meaning": "長官、幹事", "wrong_count": 0, "correct_count": 0},
    {"id": "init-19", "word": "inspector", "meaning": "監査官", "wrong_count": 0, "correct_count": 0},
    {"id": "init-20", "word": "exclusively", "meaning": "〜だけ", "wrong_count": 0, "correct_count": 0},
    {"id": "init-21", "word": "endorse", "meaning": "〜を支持する", "wrong_count": 0, "correct_count": 0},
    {"id": "init-22", "word": "enthusiastically", "meaning": "熱狂的に", "wrong_count": 0, "correct_count": 0},
    {"id": "init-23", "word": "net profit", "meaning": "純利益", "wrong_count": 0, "correct_count": 0},
    {"id": "init-24", "word": "in excess of X", "meaning": "Xを超えて、X以上に", "wrong_count": 0, "correct_count": 0},
    {"id": "init-25", "word": "insulation", "meaning": "断熱(材)", "wrong_count": 0, "correct_count": 0},
    {"id": "init-26", "word": "accessible", "meaning": "手に入れやすい、使える", "wrong_count": 0, "correct_count": 0},
    {"id": "init-27", "word": "readily", "meaning": "簡単に、すぐに", "wrong_count": 0, "correct_count": 0},
    {"id": "init-28", "word": "speculation", "meaning": "憶測、推測", "wrong_count": 0, "correct_count": 0},
    {"id": "init-29", "word": "adhere to X", "meaning": "Xに従う", "wrong_count": 0, "correct_count": 0},
    {"id": "init-30", "word": "diligently", "meaning": "勤勉に、入念に", "wrong_count": 0, "correct_count": 0},
    {"id": "init-31", "word": "overwhelmingly", "meaning": "圧倒的に", "wrong_count": 0, "correct_count": 0},
    {"id": "init-32", "word": "retool", "meaning": "(工場など)の機械を入れ替える", "wrong_count": 0, "correct_count": 0},
    {"id": "init-33", "word": "feasibility", "meaning": "実現可能性", "wrong_count": 0, "correct_count": 0},
    {"id": "init-34", "word": "dawn", "meaning": "始まり、幕開け", "wrong_count": 0, "correct_count": 0},
    {"id": "init-35", "word": "clerical error", "meaning": "事務的な誤り", "wrong_count": 0, "correct_count": 0},
    {"id": "init-36", "word": "preventable", "meaning": "予防可能な", "wrong_count": 0, "correct_count": 0},
    {"id": "init-37", "word": "conscientious", "meaning": "誠実な、入念な", "wrong_count": 0, "correct_count": 0},
    {"id": "init-38", "word": "considerably", "meaning": "大幅に、かなり", "wrong_count": 0, "correct_count": 0},
    {"id": "init-39", "word": "verify", "meaning": "〜が真実だと確かめる、検証する", "wrong_count": 0, "correct_count": 0},
    {"id": "init-40", "word": "address", "meaning": "〜に取り組む、対処する", "wrong_count": 0, "correct_count": 0},
    {"id": "init-41", "word": "distinctive", "meaning": "独特の", "wrong_count": 0, "correct_count": 0},
    {"id": "init-42", "word": "emulate", "meaning": "〜を見習う", "wrong_count": 0, "correct_count": 0},
    {"id": "init-43", "word": "dependable", "meaning": "信頼できる", "wrong_count": 0, "correct_count": 0},
    {"id": "init-44", "word": "vital", "meaning": "極めて重要な、不可欠な", "wrong_count": 0, "correct_count": 0},
    {"id": "init-45", "word": "rate", "meaning": "〜を評価する", "wrong_count": 0, "correct_count": 0},
    {"id": "init-46", "word": "attribute X to Y", "meaning": "XはYに起因すると考える", "wrong_count": 0, "correct_count": 0},
    {"id": "init-47", "word": "managerial", "meaning": "経営上の", "wrong_count": 0, "correct_count": 0},
    {"id": "init-48", "word": "acumen", "meaning": "洞察力、判断力", "wrong_count": 0, "correct_count": 0},
    {"id": "init-49", "word": "probationary", "meaning": "見習い中の、試用の", "wrong_count": 0, "correct_count": 0},
    {"id": "init-50", "word": "noticeable", "meaning": "目立つ、著しい", "wrong_count": 0, "correct_count": 0},
    {"id": "init-51", "word": "itinerary", "meaning": "旅行計画、旅程(表)", "wrong_count": 0, "correct_count": 0},
    {"id": "init-52", "word": "a round of X", "meaning": "一連のX", "wrong_count": 0, "correct_count": 0},
    {"id": "init-53", "word": "respondent", "meaning": "回答者", "wrong_count": 0, "correct_count": 0},
    {"id": "init-54", "word": "aid", "meaning": "支援", "wrong_count": 0, "correct_count": 0},
    {"id": "init-55", "word": "eligible", "meaning": "資格のある", "wrong_count": 0, "correct_count": 0},
    {"id": "init-56", "word": "competitive", "meaning": "競争力のある、他に負けない", "wrong_count": 0, "correct_count": 0},
    {"id": "init-57", "word": "mining", "meaning": "採掘", "wrong_count": 0, "correct_count": 0},
    {"id": "init-58", "word": "prestigious", "meaning": "一流の、権威ある", "wrong_count": 0, "correct_count": 0},
    {"id": "init-59", "word": "grant", "meaning": "助成金、補助金", "wrong_count": 0, "correct_count": 0},
    {"id": "init-60", "word": "set aside", "meaning": "(金、時間など)取っておく", "wrong_count": 0, "correct_count": 0},
    {"id": "init-61", "word": "undergo", "meaning": "〜を受ける", "wrong_count": 0, "correct_count": 0},
    {"id": "init-62", "word": "deliberation", "meaning": "審議、討議", "wrong_count": 0, "correct_count": 0},
    {"id": "init-63", "word": "correspondingly", "meaning": "それに応じて", "wrong_count": 0, "correct_count": 0},
    {"id": "init-64", "word": "commendably", "meaning": "立派に", "wrong_count": 0, "correct_count": 0},
    {"id": "init-65", "word": "predecessor", "meaning": "前任者", "wrong_count": 0, "correct_count": 0},
    {"id": "init-66", "word": "prominent", "meaning": "卓越した、著名な", "wrong_count": 0, "correct_count": 0},
    {"id": "init-67", "word": "diagnostic", "meaning": "診断の", "wrong_count": 0, "correct_count": 0},
    {"id": "init-68", "word": "pinpoint", "meaning": "(原因など)を正確に指摘する", "wrong_count": 0, "correct_count": 0},
    {"id": "init-69", "word": "durability", "meaning": "耐久性", "wrong_count": 0, "correct_count": 0},
    {"id": "init-70", "word": "anticipated", "meaning": "期待された", "wrong_count": 0, "correct_count": 0},
    {"id": "init-71", "word": "remarkable", "meaning": "驚くべき", "wrong_count": 0, "correct_count": 0},
    {"id": "init-72", "word": "faculty", "meaning": "(大学の)教員", "wrong_count": 0, "correct_count": 0},
    {"id": "init-73", "word": "maneuverable", "meaning": "操作しやすい", "wrong_count": 0, "correct_count": 0},
    {"id": "init-74", "word": "lawnmower", "meaning": "芝刈り機", "wrong_count": 0, "correct_count": 0},
    {"id": "init-75", "word": "precisely", "meaning": "ちょうど、正確に", "wrong_count": 0, "correct_count": 0},
    {"id": "init-76", "word": "exhaustively", "meaning": "徹底的に", "wrong_count": 0, "correct_count": 0},
    {"id": "init-77", "word": "exceedingly", "meaning": "非常に", "wrong_count": 0, "correct_count": 0},
    {"id": "init-78", "word": "noticeably", "meaning": "著しく、目立って", "wrong_count": 0, "correct_count": 0},
    {"id": "init-79", "word": "feature", "meaning": "〜を呼び物にする", "wrong_count": 0, "correct_count": 0},
    {"id": "init-80", "word": "extensive", "meaning": "広範囲の", "wrong_count": 0, "correct_count": 0},
    {"id": "init-81", "word": "notably", "meaning": "特に", "wrong_count": 0, "correct_count": 0},
    {"id": "init-82", "word": "chair", "meaning": "〜の議長を務める", "wrong_count": 0, "correct_count": 0},
    {"id": "init-83", "word": "contribution", "meaning": "貢献", "wrong_count": 0, "correct_count": 0},
    {"id": "init-84", "word": "evident", "meaning": "明白な、明らかな", "wrong_count": 0, "correct_count": 0},
    {"id": "init-85", "word": "revise", "meaning": "〜を修正する、見直す", "wrong_count": 0, "correct_count": 0},
    {"id": "init-86", "word": "reliable", "meaning": "信頼できる", "wrong_count": 0, "correct_count": 0},
    {"id": "init-87", "word": "acquaintance", "meaning": "知人", "wrong_count": 0, "correct_count": 0},
    {"id": "init-88", "word": "implement", "meaning": "〜を実行する", "wrong_count": 0, "correct_count": 0},
    {"id": "init-89", "word": "subsequently", "meaning": "その後で", "wrong_count": 0, "correct_count": 0},
    {"id": "init-90", "word": "recognition", "meaning": "評価", "wrong_count": 0, "correct_count": 0},
    {"id": "init-91", "word": "subordinate", "meaning": "部下", "wrong_count": 0, "correct_count": 0},
    {"id": "init-92", "word": "as of X", "meaning": "X(日時)以降", "wrong_count": 0, "correct_count": 0},
    {"id": "init-93", "word": "enforce", "meaning": "〜を施行する", "wrong_count": 0, "correct_count": 0},
    {"id": "init-94", "word": "intentionally", "meaning": "意図的に", "wrong_count": 0, "correct_count": 0},
    {"id": "init-95", "word": "cut back on X", "meaning": "Xを減らす", "wrong_count": 0, "correct_count": 0},
    {"id": "init-96", "word": "practically", "meaning": "ほとんど", "wrong_count": 0, "correct_count": 0},
    {"id": "init-97", "word": "complication", "meaning": "やっかいな問題、複雑さ", "wrong_count": 0, "correct_count": 0},
    {"id": "init-98", "word": "take on X", "meaning": "Xをしようと決める", "wrong_count": 0, "correct_count": 0},
    {"id": "init-99", "word": "retain", "meaning": "〜を維持する、持ち続ける", "wrong_count": 0, "correct_count": 0},
    {"id": "init-100", "word": "swiftly", "meaning": "素早く、迅速に", "wrong_count": 0, "correct_count": 0},
    {"id": "init-101", "word": "seemingly", "meaning": "見たところ、外見上は", "wrong_count": 0, "correct_count": 0},
    {"id": "init-102", "word": "grant", "meaning": "〜を与える、許可する", "wrong_count": 0, "correct_count": 0},
    {"id": "init-103", "word": "decline", "meaning": "(丁寧に)断る", "wrong_count": 0, "correct_count": 0},
    {"id": "init-104", "word": "respectfully", "meaning": "丁寧に", "wrong_count": 0, "correct_count": 0},
    {"id": "init-105", "word": "assure", "meaning": "〜を保証する、請け合う", "wrong_count": 0, "correct_count": 0},
    {"id": "init-106", "word": "accomplished", "meaning": "熟練の", "wrong_count": 0, "correct_count": 0},
    {"id": "init-107", "word": "impending", "meaning": "今にも起ころうとしている", "wrong_count": 0, "correct_count": 0},
    {"id": "init-108", "word": "confidential", "meaning": "内密の、機密の", "wrong_count": 0, "correct_count": 0},
    {"id": "init-109", "word": "managerial", "meaning": "管理職の", "wrong_count": 0, "correct_count": 0},
    {"id": "init-110", "word": "ventilate", "meaning": "〜を換気する", "wrong_count": 0, "correct_count": 0},
    {"id": "init-111", "word": "coal", "meaning": "石炭", "wrong_count": 0, "correct_count": 0}
]

DATA_FILE = "words_data.json"

# ---------------------------------------------------------
# データ永続化 (保存・読み込み) 関数
# ---------------------------------------------------------
def load_words():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list) and len(data) > 0:
                    for item in data:
                        item.setdefault("wrong_count", 0)
                        item.setdefault("correct_count", 0)
                    return data
        except Exception as e:
            st.error(f"データの読み込みに失敗しました: {e}")
    save_words(INITIAL_WORDS)
    return INITIAL_WORDS

def save_words(words_list):
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(words_list, f, ensure_ascii=False, indent=2)
    except Exception as e:
        st.error(f"データの保存に失敗しました: {e}")

# ---------------------------------------------------------
# Google GenAI クライアント初期化
# ---------------------------------------------------------
def get_genai_client():
    api_key = st.secrets.get("GEMINI_API_KEY", os.environ.get("GEMINI_API_KEY", ""))
    if not api_key:
        return None
    try:
        return genai.Client(api_key=api_key)
    except Exception as e:
        st.error(f"Gemini APIの初期化に失敗しました: {e}")
        return None

# ---------------------------------------------------------
# セッション状態の初期化
# ---------------------------------------------------------
if "word_list" not in st.session_state:
    st.session_state.word_list = load_words()

# ---------------------------------------------------------
# AI 単語情報生成 (AI自動生成機能用)
# ---------------------------------------------------------
def generate_word_info(word_text, client):
    prompt = f"""
    英単語または熟語「{word_text}」の意味をJSON形式で返してください。
    【キー名】
    - meaning: 日本語の意味（簡潔に）
    """
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json"
            )
        )
        data = json.loads(response.text)
        return data
    except Exception as e:
        st.error(f"AI生成エラー: {e}")
        return None

# ---------------------------------------------------------
# サイドバーナビゲーション
# ---------------------------------------------------------
st.sidebar.title("📘 英単語テストメーカー")

client = get_genai_client()
if not client:
    st.sidebar.info("💡 **Gemini APIキー設定ガイド**\nAI自動生成機能を使うには、Streamlit CloudのSecretsに `GEMINI_API_KEY` を設定してください。")

nav_choice = st.sidebar.radio(
    "メニューを選択",
    ["📚 単語の管理・一覧", "🤖 AI単語自動生成", "🎴 暗記カード・確認テスト", "🖨️ A4テスト印刷・PDF"]
)

# 保存されている単語数表示
st.sidebar.metric("全登録単語数", f"{len(st.session_state.word_list)} 件")

# ---------------------------------------------------------
# 1. 単語の管理・一覧
# ---------------------------------------------------------
if nav_choice == "📚 単語の管理・一覧":
    st.header("📚 単語の管理・一覧")
    
    # 検索フィルター
    search_query = st.text_input("🔍 単語・意味で検索", "").strip().lower()

    col_form1, col_form2 = st.columns(2)
    
    # 単語追加フォーム（英単語/熟語と意味のみ入力）
    with col_form1:
        with st.expander("➕ 新しい単語を手動追加", expanded=False):
            with st.form("add_form", clear_on_submit=True):
                w_input = st.text_input("英単語 / 熟語 *", placeholder="例: resilience")
                m_input = st.text_input("日本語の意味 *", placeholder="例: 回復力、復元力")
                
                submitted = st.form_submit_button("単語を追加・保存", use_container_width=True)
                if submitted:
                    if w_input and m_input:
                        new_item = {
                            "id": f"custom-{len(st.session_state.word_list) + 1}",
                            "word": w_input,
                            "meaning": m_input,
                            "wrong_count": 0,
                            "correct_count": 0
                        }
                        st.session_state.word_list.append(new_item)
                        save_words(st.session_state.word_list)
                        st.success(f"「{w_input}」を追加・保存しました！")
                        st.rerun()
                    else:
                        st.warning("英単語と日本語の意味は必須です。")

    # 単語編集・削除フォーム
    with col_form2:
        with st.expander("✏️ 登録済み単語の編集・削除", expanded=False):
            if not st.session_state.word_list:
                st.info("登録されている単語がありません。")
            else:
                # 編集・削除対象の単語を選択
                word_options = [f"{w['word']} : {w['meaning']}" for w in st.session_state.word_list]
                selected_word_str = st.selectbox("編集・削除する単語を選択", word_options)
                
                if selected_word_str:
                    # 選択中のインデックスとオブジェクトを特定
                    selected_idx = word_options.index(selected_word_str)
                    target_word_obj = st.session_state.word_list[selected_idx]

                    with st.form("edit_delete_form"):
                        edit_w = st.text_input("英単語 / 熟語", value=target_word_obj["word"])
                        edit_m = st.text_input("日本語の意味", value=target_word_obj["meaning"])
                        
                        btn_col1, btn_col2 = st.columns(2)
                        with btn_col1:
                            update_submitted = st.form_submit_button("✏️ 変更を保存", use_container_width=True)
                        with btn_col2:
                            delete_submitted = st.form_submit_button("🗑️ この単語を削除", type="secondary", use_container_width=True)

                        if update_submitted:
                            if edit_w and edit_m:
                                st.session_state.word_list[selected_idx]["word"] = edit_w
                                st.session_state.word_list[selected_idx]["meaning"] = edit_m
                                save_words(st.session_state.word_list)
                                st.success(f"「{edit_w}」の情報を更新しました！")
                                st.rerun()
                            else:
                                st.warning("英単語と意味の両方を入力してください。")
                                
                        if delete_submitted:
                            deleted_name = target_word_obj["word"]
                            st.session_state.word_list.pop(selected_idx)
                            save_words(st.session_state.word_list)
                            st.success(f"「{deleted_name}」を削除しました。")
                            st.rerun()

    # 一覧のフィルタリング
    filtered_words = [
        w for w in st.session_state.word_list
        if search_query in w["word"].lower() or search_query in w["meaning"].lower()
    ]
    
    st.subheader(f"単語リスト (全登録単語数: {len(st.session_state.word_list)} 件)")
    
    # 英単語と意味のみのシンプル一覧（インデックスは1からスタート）
    if filtered_words:
        df = pd.DataFrame(filtered_words)
        df_display = df.rename(columns={
            "word": "英単語",
            "meaning": "意味"
        })[["英単語", "意味"]]
        df_display.index = range(1, len(df_display) + 1)
        st.dataframe(df_display, use_container_width=True)
    else:
        st.info("該当する単語が見つかりません。")

    st.divider()
    
    col_a, col_b = st.columns(2)
    with col_a:
        json_str = json.dumps(st.session_state.word_list, ensure_ascii=False, indent=2)
        st.download_button(
            label="📥 単語リストをJSON保存 (バックアップ)",
            data=json_str,
            file_name="words_backup.json",
            mime="application/json"
        )
    with col_b:
        if st.button("⚠️ 初期状態 (111単語) にリセット", type="secondary"):
            st.session_state.word_list = [dict(item) for item in INITIAL_WORDS]
            save_words(st.session_state.word_list)
            st.success("初期単語データ (111件) にリセットしました！")
            st.rerun()

# ---------------------------------------------------------
# 2. AI単語自動生成 (Gemini API)
# ---------------------------------------------------------
elif nav_choice == "🤖 AI単語自動生成":
    st.header("🤖 AI単語自動生成 (Gemini API)")
    st.write("英単語を入力すると、Gemini AI が自動的に意味を作成してリストに保存します。")
    
    if not client:
        st.error("🔑 AI機能を利用するには、Streamlit Secrets または環境変数に `GEMINI_API_KEY` を設定してください。")
    else:
        target_w = st.text_input("自動生成したい英単語を入力 (例: resilience, sustainable)", "")
        if st.button("✨ AIで自動作成・保存") and target_w:
            with st.spinner(f"「{target_w}」の情報をGeminiで生成中..."):
                res = generate_word_info(target_w, client)
                if res:
                    new_item = {
                        "id": f"ai-{len(st.session_state.word_list) + 1}",
                        "word": target_w,
                        "meaning": res.get("meaning", ""),
                        "wrong_count": 0,
                        "correct_count": 0
                    }
                    st.session_state.word_list.append(new_item)
                    save_words(st.session_state.word_list)
                    st.success(f"「{target_w}」を自動生成し、単語帳に追加しました！")
                    st.json(res)

# ---------------------------------------------------------
# 3. 暗記カード・確認テスト
# ---------------------------------------------------------
elif nav_choice == "🎴 暗記カード・確認テスト":
    st.header("🎴 暗記カード & 確認テスト")
    
    if not st.session_state.word_list:
        st.warning("単語が登録されていません。管理画面から単語を追加してください。")
    else:
        tab1, tab2 = st.tabs(["🎴 フラッシュカード暗記", "✍️ 4択確認テスト"])
        
        # フラッシュカード (ランダム順表示・絵文字/品詞なし)
        with tab1:
            st.subheader("フラッシュカード暗記")
            
            # カード用シャッフルリストの管理
            if "flashcard_order" not in st.session_state or len(st.session_state.flashcard_order) != len(st.session_state.word_list):
                indices = list(range(len(st.session_state.word_list)))
                random.shuffle(indices)
                st.session_state.flashcard_order = indices
                st.session_state.card_idx = 0
                st.session_state.show_meaning = False

            if st.button("🔀 もう一度シャッフル"):
                indices = list(range(len(st.session_state.word_list)))
                random.shuffle(indices)
                st.session_state.flashcard_order = indices
                st.session_state.card_idx = 0
                st.session_state.show_meaning = False
                st.rerun()

            words_len = len(st.session_state.word_list)
            st.session_state.card_idx = st.session_state.card_idx % words_len
            
            curr_real_idx = st.session_state.flashcard_order[st.session_state.card_idx]
            curr_word = st.session_state.word_list[curr_real_idx]

            c1, c2, c3 = st.columns([1, 2, 1])
            with c2:
                st.markdown(f"**Card {st.session_state.card_idx + 1} / {words_len}**")
                
                # 絵文字や品詞なしのシンプルな表示
                st.info(f"### **{curr_word['word']}**")
                
                if st.session_state.show_meaning:
                    st.success(f"**意味**: {curr_word['meaning']}")
                
                col_btn1, col_btn2 = st.columns(2)
                with col_btn1:
                    if st.button("意味を表示 / 隠す", use_container_width=True):
                        st.session_state.show_meaning = not st.session_state.show_meaning
                        st.rerun()
                with col_btn2:
                    if st.button("次の単語へ ➡️", use_container_width=True):
                        st.session_state.card_idx = (st.session_state.card_idx + 1) % words_len
                        st.session_state.show_meaning = False
                        st.rerun()

        # 4択確認テスト (問題数選択・苦手優先・連続解答)
        with tab2:
            st.subheader("4択確認テスト")
            
            col_cfg1, col_cfg2 = st.columns(2)
            with col_cfg1:
                quiz_mode = st.radio("出題モード", ["ランダム出題", "苦手単語優先 (誤答が多い単語)"])
            with col_cfg2:
                max_q_count = len(st.session_state.word_list)
                num_options = [5, 10, 20, 30, 50, "全問"]
                num_options = [opt for opt in num_options if opt == "全問" or (isinstance(opt, int) and opt <= max_q_count)]
                if not num_options:
                    num_options = [max_q_count]
                selected_num = st.selectbox("問題数を選択", num_options)
                q_total = max_q_count if selected_num == "全問" else int(selected_num)

            if st.button("🚀 テストを開始する", type="primary"):
                # テスト用キューの作成
                words_pool = list(st.session_state.word_list)
                if quiz_mode == "苦手単語優先 (誤答が多い単語)":
                    random.shuffle(words_pool)
                    words_pool.sort(key=lambda x: x.get("wrong_count", 0), reverse=True)
                else:
                    random.shuffle(words_pool)
                
                selected_words = words_pool[:q_total]
                
                # クイズセッション構築
                st.session_state.quiz_queue = selected_words
                st.session_state.quiz_index = 0
                st.session_state.quiz_score = 0
                st.session_state.quiz_history = []  # 結果履歴
                st.session_state.quiz_active = True
                st.session_state.quiz_answered = False
                st.rerun()

            # テスト実行中の表示
            if st.session_state.get("quiz_active", False):
                queue = st.session_state.quiz_queue
                idx = st.session_state.quiz_index
                
                if idx < len(queue):
                    curr_q = queue[idx]
                    st.divider()
                    st.markdown(f"#### **第 {idx + 1} 問 / 全 {len(queue)} 問**")
                    st.markdown(f"### 問題: **{curr_q['word']}** の正しい意味は？")
                    
                    # 選択肢の生成
                    choice_key = f"quiz_choices_{idx}"
                    if choice_key not in st.session_state:
                        others = [w for w in st.session_state.word_list if w["id"] != curr_q["id"]]
                        wrong_samples = random.sample(others, min(3, len(others)))
                        choices = [curr_q["meaning"]] + [w["meaning"] for w in wrong_samples]
                        random.shuffle(choices)
                        st.session_state[choice_key] = choices

                    choices = st.session_state[choice_key]
                    
                    if not st.session_state.quiz_answered:
                        for c_i, choice_text in enumerate(choices):
                            if st.button(f"{c_i + 1}. {choice_text}", key=f"q_btn_{idx}_{c_i}", use_container_width=True):
                                is_correct = (choice_text == curr_q["meaning"])
                                st.session_state.quiz_answered = True
                                st.session_state.last_answer_correct = is_correct
                                st.session_state.last_selected_choice = choice_text
                                
                                # 正否カウントの更新 & 保存
                                for w in st.session_state.word_list:
                                    if w["id"] == curr_q["id"]:
                                        if is_correct:
                                            w["correct_count"] = w.get("correct_count", 0) + 1
                                        else:
                                            w["wrong_count"] = w.get("wrong_count", 0) + 1
                                        break
                                save_words(st.session_state.word_list)
                                
                                if is_correct:
                                    st.session_state.quiz_score += 1
                                
                                st.session_state.quiz_history.append({
                                    "word": curr_q["word"],
                                    "correct_meaning": curr_q["meaning"],
                                    "user_choice": choice_text,
                                    "is_correct": is_correct
                                })
                                st.rerun()
                    else:
                        # 解答後のフィードバック表示
                        if st.session_state.last_answer_correct:
                            st.success("⭕ 正解です！")
                        else:
                            st.error(f"❌ 不正解... 正解は「{curr_q['meaning']}」でした。")
                        
                        if st.button("次の問題へ ➡️", type="primary"):
                            st.session_state.quiz_index += 1
                            st.session_state.quiz_answered = False
                            st.rerun()
                else:
                    # テスト終了時のサマリー
                    st.divider()
                    st.success("🎉 テスト終了！お疲れ様でした。")
                    total_q = len(queue)
                    score = st.session_state.quiz_score
                    st.metric("スコア", f"{score} / {total_q} 点", f"{int(score/total_q*100)}%")
                    
                    # 誤答リストの振り返り
                    wrongs = [h for h in st.session_state.quiz_history if not h["is_correct"]]
                    if wrongs:
                        st.subheader("⚠️ 今回間違えた単語 (苦手単語リストに記録されました)")
                        for w_item in wrongs:
                            st.write(f"- **{w_item['word']}**: 正解「{w_item['correct_meaning']}」 (あなたの回答: {w_item['user_choice']})")
                    else:
                        st.balloons()
                        st.success("素晴らしい！全問正解です！")
                    
                    if st.button("🔄 もう一度テストする"):
                        st.session_state.quiz_active = False
                        st.rerun()

# ---------------------------------------------------------
# 4. A4テスト印刷・PDF出力 (タイトル固定・50問/1枚・セル左揃え・印刷時ボタン非表示)
# ---------------------------------------------------------
elif nav_choice == "🖨️ A4テスト印刷・PDF":
    st.header("🖨️ A4 印刷用テストシート作成")
    
    if not st.session_state.word_list:
        st.warning("単語が登録されていません。先に単語を登録してください。")
    else:
        col1, col2 = st.columns(2)
        with col1:
            # 「単語帳一覧シート」を削り、2種類の形式のみ
            test_mode = st.selectbox("テスト出力形式", ["英単語 → 日本語の意味", "日本語の意味 → 英単語"])
        with col2:
            is_shuffle = st.checkbox("問題をランダム順にする", value=True)
            show_ans = st.checkbox("解答をあらかじめ印字する (解答集)", value=False)
            
        print_words = list(st.session_state.word_list)
        if is_shuffle:
            random.seed(42)
            print_words = random.sample(print_words, len(print_words))

        FIXED_TITLE = "英単語確認テスト"

        # 50問/1枚(左右2列 25問ずつ)
        words_50 = print_words[:50]
        left_words = words_50[:25]
        right_words = words_50[25:50]

        def build_rows(words_subset, start_num):
            rows = ""
            for i, w in enumerate(words_subset, start_num):
                if test_mode == "英単語 → 日本語の意味":
                    col_q = f"<b>{w['word']}</b>"
                    col_a = w['meaning'] if show_ans else ""
                else:  # 日本語の意味 → 英単語
                    col_q = w['meaning']
                    col_a = f"<b>{w['word']}</b>" if show_ans else ""

                rows += f"""
                <tr class="item-row">
                    <td class="col-no">{i}</td>
                    <td class="col-q">{col_q}</td>
                    <td class="col-a">{col_a}</td>
                </tr>
                """
            return rows

        left_rows = build_rows(left_words, 1)
        right_rows = build_rows(right_words, 26) if right_words else ""

        full_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                @page {{
                    size: A4 portrait;
                    margin: 10mm 12mm;
                }}
                body {{
                    font-family: 'Helvetica Neue', Arial, 'Hiragino Kaku Gothic ProN', Meiryo, sans-serif;
                    color: #0f172a;
                    margin: 0;
                    padding: 0;
                    font-size: 11px;
                }}
                .print-box {{
                    width: 100%;
                    max-width: 800px;
                    margin: 0 auto;
                    background: #ffffff;
                }}
                .header-bar {{
                    display: flex;
                    justify-content: space-between;
                    align-items: flex-end;
                    border-bottom: 2px solid #0f172a;
                    padding-bottom: 6px;
                    margin-bottom: 12px;
                }}
                .title-text {{
                    font-size: 18px;
                    font-weight: bold;
                }}
                .score-area {{
                    font-size: 11px;
                    border: 1px solid #475569;
                    padding: 3px 10px;
                    border-radius: 4px;
                }}
                .columns-container {{
                    display: flex;
                    gap: 16px;
                }}
                .column {{
                    flex: 1;
                }}
                table {{
                    width: 100%;
                    border-collapse: collapse;
                }}
                th {{
                    background-color: #f1f5f9;
                    border-bottom: 1px solid #64748b;
                    padding: 5px;
                    font-size: 10px;
                    text-align: left; /* 表記をセル左揃えに設定 */
                }}
                th.col-no {{
                    text-align: center;
                }}
                .item-row {{
                    height: 33px; /* 50問でA4下部までピッタリ収まる高さ */
                    border-bottom: 1px solid #cbd5e1;
                }}
                .col-no {{
                    width: 8%;
                    text-align: center;
                    font-weight: bold;
                    font-size: 10px;
                }}
                .col-q {{
                    width: 44%;
                    padding: 4px 6px;
                    font-size: 11px;
                    text-align: left; /* 問題文を左揃え */
                }}
                .col-a {{
                    width: 48%;
                    padding: 4px 6px;
                    font-size: 11px;
                    text-align: left; /* 解答欄を左揃え */
                }}
                /* 印刷時・PDF出力時にボタンを消すためのスタイル */
                @media print {{
                    .no-print {{
                        display: none !important;
                    }}
                    @page {{
                        margin: 10mm 12mm;
                    }}
                }}
            </style>
        </head>
        <body>
            <div style="margin-bottom: 12px;" class="no-print">
                <button onclick="window.print()" style="background-color: #2563eb; color: #ffffff; border: none; padding: 8px 18px; font-size: 14px; font-weight: bold; border-radius: 6px; cursor: pointer;">
                    🖨️ A4用紙に印刷 / PDF保存
                </button>
            </div>
            
            <div class="print-box">
                <div class="header-bar">
                    <div class="title-text">{FIXED_TITLE} {"(解答集)" if show_ans else ""}</div>
                    <div class="score-area">
                        点数: &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; / {len(words_50)}
                    </div>
                </div>
                
                <div class="columns-container">
                    <div class="column">
                        <table>
                            <thead>
                                <tr>
                                    <th class="col-no">No.</th>
                                    <th class="col-q">問題</th>
                                    <th class="col-a">解答欄</th>
                                </tr>
                            </thead>
                            <tbody>
                                {left_rows}
                            </tbody>
                        </table>
                    </div>
                    
                    {"<div class='column'><table><thead><tr><th class='col-no'>No.</th><th class='col-q'>問題</th><th class='col-a'>解答欄</th></tr></thead><tbody>" + right_rows + "</tbody></table></div>" if right_rows else ""}
                </div>
            </div>
        </body>
        </html>
        """
        
        st.components.v1.html(full_html, height=1000, scrolling=True)
