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
    {"id": "init-1", "word": "agreeable", "meaning": "快適な、感じの良い", "partOfSpeech": "形容詞", "example": "", "exampleMeaning": ""},
    {"id": "init-2", "word": "ensemble", "meaning": "アンサンブル(少人数の合奏団)", "partOfSpeech": "名詞", "example": "", "exampleMeaning": ""},
    {"id": "init-3", "word": "accommodate", "meaning": "〜を収容する", "partOfSpeech": "動詞", "example": "", "exampleMeaning": ""},
    {"id": "init-4", "word": "acquire", "meaning": "〜を獲得する", "partOfSpeech": "動詞", "example": "", "exampleMeaning": ""},
    {"id": "init-5", "word": "emphatically", "meaning": "きっぱりと、強調して", "partOfSpeech": "副詞", "example": "", "exampleMeaning": ""},
    {"id": "init-6", "word": "nominal", "meaning": "ごくわずかの、名目だけの", "partOfSpeech": "形容詞", "example": "", "exampleMeaning": ""},
    {"id": "init-7", "word": "file", "meaning": "〜を提出する", "partOfSpeech": "動詞", "example": "", "exampleMeaning": ""},
    {"id": "init-8", "word": "ensure", "meaning": "確実に〜するようになる", "partOfSpeech": "動詞", "example": "", "exampleMeaning": ""},
    {"id": "init-9", "word": "utility costs", "meaning": "光熱費", "partOfSpeech": "名詞", "example": "", "exampleMeaning": ""},
    {"id": "init-10", "word": "conventionally", "meaning": "従来の方法で、従来は", "partOfSpeech": "副詞", "example": "", "exampleMeaning": ""},
    {"id": "init-11", "word": "contractor", "meaning": "請負業者", "partOfSpeech": "名詞", "example": "", "exampleMeaning": ""},
    {"id": "init-12", "word": "solid", "meaning": "信頼できる、確かな", "partOfSpeech": "形容詞", "example": "", "exampleMeaning": ""},
    {"id": "init-13", "word": "mature", "meaning": "成熟する、発達する", "partOfSpeech": "動詞", "example": "", "exampleMeaning": ""},
    {"id": "init-14", "word": "undertake", "meaning": "〜を引き受ける、〜に着手する", "partOfSpeech": "動詞", "example": "", "exampleMeaning": ""},
    {"id": "init-15", "word": "restoration", "meaning": "修復、補修", "partOfSpeech": "名詞", "example": "", "exampleMeaning": ""},
    {"id": "init-16", "word": "regrettably", "meaning": "残念ながら", "partOfSpeech": "副詞", "example": "", "exampleMeaning": ""},
    {"id": "init-17", "word": "defective", "meaning": "欠陥のある、不完全な", "partOfSpeech": "形容詞", "example": "", "exampleMeaning": ""},
    {"id": "init-18", "word": "secretary", "meaning": "長官、幹事", "partOfSpeech": "名詞", "example": "", "exampleMeaning": ""},
    {"id": "init-19", "word": "inspector", "meaning": "監査官", "partOfSpeech": "名詞", "example": "", "exampleMeaning": ""},
    {"id": "init-20", "word": "exclusively", "meaning": "〜だけ", "partOfSpeech": "副詞", "example": "", "exampleMeaning": ""},
    {"id": "init-21", "word": "endorse", "meaning": "〜を支持する", "partOfSpeech": "動詞", "example": "", "exampleMeaning": ""},
    {"id": "init-22", "word": "enthusiastically", "meaning": "熱狂的に", "partOfSpeech": "副詞", "example": "", "exampleMeaning": ""},
    {"id": "init-23", "word": "net profit", "meaning": "純利益", "partOfSpeech": "名詞", "example": "", "exampleMeaning": ""},
    {"id": "init-24", "word": "in excess of X", "meaning": "Xを超えて、X以上に", "partOfSpeech": "熟語", "example": "", "exampleMeaning": ""},
    {"id": "init-25", "word": "insulation", "meaning": "断熱(材)", "partOfSpeech": "名詞", "example": "", "exampleMeaning": ""},
    {"id": "init-26", "word": "accessible", "meaning": "手に入れやすい、使える", "partOfSpeech": "形容詞", "example": "", "exampleMeaning": ""},
    {"id": "init-27", "word": "readily", "meaning": "簡単に、すぐに", "partOfSpeech": "副詞", "example": "", "exampleMeaning": ""},
    {"id": "init-28", "word": "speculation", "meaning": "憶測、推測", "partOfSpeech": "名詞", "example": "", "exampleMeaning": ""},
    {"id": "init-29", "word": "adhere to X", "meaning": "Xに従う", "partOfSpeech": "熟語", "example": "", "exampleMeaning": ""},
    {"id": "init-30", "word": "diligently", "meaning": "勤勉に、入念に", "partOfSpeech": "副詞", "example": "", "exampleMeaning": ""},
    {"id": "init-31", "word": "overwhelmingly", "meaning": "圧倒的に", "partOfSpeech": "副詞", "example": "", "exampleMeaning": ""},
    {"id": "init-32", "word": "retool", "meaning": "(工場など)の機械を入れ替える", "partOfSpeech": "動詞", "example": "", "exampleMeaning": ""},
    {"id": "init-33", "word": "feasibility", "meaning": "実現可能性", "partOfSpeech": "名詞", "example": "", "exampleMeaning": ""},
    {"id": "init-34", "word": "dawn", "meaning": "始まり、幕開け", "partOfSpeech": "名詞", "example": "", "exampleMeaning": ""},
    {"id": "init-35", "word": "clerical error", "meaning": "事務的な誤り", "partOfSpeech": "名詞", "example": "", "exampleMeaning": ""},
    {"id": "init-36", "word": "preventable", "meaning": "予防可能な", "partOfSpeech": "形容詞", "example": "", "exampleMeaning": ""},
    {"id": "init-37", "word": "conscientious", "meaning": "誠実な、入念な", "partOfSpeech": "形容詞", "example": "", "exampleMeaning": ""},
    {"id": "init-38", "word": "considerably", "meaning": "大幅に、かなり", "partOfSpeech": "副詞", "example": "", "exampleMeaning": ""},
    {"id": "init-39", "word": "verify", "meaning": "〜が真実だと確かめる、検証する", "partOfSpeech": "動詞", "example": "", "exampleMeaning": ""},
    {"id": "init-40", "word": "address", "meaning": "〜に取り組む、対処する", "partOfSpeech": "動詞", "example": "", "exampleMeaning": ""},
    {"id": "init-41", "word": "distinctive", "meaning": "独特の", "partOfSpeech": "形容詞", "example": "", "exampleMeaning": ""},
    {"id": "init-42", "word": "emulate", "meaning": "〜を見習う", "partOfSpeech": "動詞", "example": "", "exampleMeaning": ""},
    {"id": "init-43", "word": "dependable", "meaning": "信頼できる", "partOfSpeech": "形容詞", "example": "", "exampleMeaning": ""},
    {"id": "init-44", "word": "vital", "meaning": "極めて重要な、不可欠な", "partOfSpeech": "形容詞", "example": "", "exampleMeaning": ""},
    {"id": "init-45", "word": "rate", "meaning": "〜を評価する", "partOfSpeech": "動詞", "example": "", "exampleMeaning": ""},
    {"id": "init-46", "word": "attribute X to Y", "meaning": "XはYに起因すると考える", "partOfSpeech": "熟語", "example": "", "exampleMeaning": ""},
    {"id": "init-47", "word": "managerial", "meaning": "経営上の", "partOfSpeech": "形容詞", "example": "", "exampleMeaning": ""},
    {"id": "init-48", "word": "acumen", "meaning": "洞察力、判断力", "partOfSpeech": "名詞", "example": "", "exampleMeaning": ""},
    {"id": "init-49", "word": "probationary", "meaning": "見習い中の、試用の", "partOfSpeech": "形容詞", "example": "", "exampleMeaning": ""},
    {"id": "init-50", "word": "noticeable", "meaning": "目立つ、著しい", "partOfSpeech": "形容詞", "example": "", "exampleMeaning": ""},
    {"id": "init-51", "word": "itinerary", "meaning": "旅行計画、旅程(表)", "partOfSpeech": "名詞", "example": "", "exampleMeaning": ""},
    {"id": "init-52", "word": "a round of X", "meaning": "一連のX", "partOfSpeech": "熟語", "example": "", "exampleMeaning": ""},
    {"id": "init-53", "word": "respondent", "meaning": "回答者", "partOfSpeech": "名詞", "example": "", "exampleMeaning": ""},
    {"id": "init-54", "word": "aid", "meaning": "支援", "partOfSpeech": "名詞", "example": "", "exampleMeaning": ""},
    {"id": "init-55", "word": "eligible", "meaning": "資格のある", "partOfSpeech": "形容詞", "example": "", "exampleMeaning": ""},
    {"id": "init-56", "word": "competitive", "meaning": "競争力のある、他に負けない", "partOfSpeech": "形容詞", "example": "", "exampleMeaning": ""},
    {"id": "init-57", "word": "mining", "meaning": "採掘", "partOfSpeech": "名詞", "example": "", "exampleMeaning": ""},
    {"id": "init-58", "word": "prestigious", "meaning": "一流の、権威ある", "partOfSpeech": "形容詞", "example": "", "exampleMeaning": ""},
    {"id": "init-59", "word": "grant", "meaning": "助成金、補助金", "partOfSpeech": "名詞", "example": "", "exampleMeaning": ""},
    {"id": "init-60", "word": "set aside", "meaning": "(金、時間など)取っておく", "partOfSpeech": "動詞", "example": "", "exampleMeaning": ""},
    {"id": "init-61", "word": "undergo", "meaning": "〜を受ける", "partOfSpeech": "動詞", "example": "", "exampleMeaning": ""},
    {"id": "init-62", "word": "deliberation", "meaning": "審議、討議", "partOfSpeech": "名詞", "example": "", "exampleMeaning": ""},
    {"id": "init-63", "word": "correspondingly", "meaning": "それに応じて", "partOfSpeech": "副詞", "example": "", "exampleMeaning": ""},
    {"id": "init-64", "word": "commendably", "meaning": "立派に", "partOfSpeech": "副詞", "example": "", "exampleMeaning": ""},
    {"id": "init-65", "word": "predecessor", "meaning": "前任者", "partOfSpeech": "名詞", "example": "", "exampleMeaning": ""},
    {"id": "init-66", "word": "prominent", "meaning": "卓越した、著名な", "partOfSpeech": "形容詞", "example": "", "exampleMeaning": ""},
    {"id": "init-67", "word": "diagnostic", "meaning": "診断の", "partOfSpeech": "形容詞", "example": "", "exampleMeaning": ""},
    {"id": "init-68", "word": "pinpoint", "meaning": "(原因など)を正確に指摘する", "partOfSpeech": "動詞", "example": "", "exampleMeaning": ""},
    {"id": "init-69", "word": "durability", "meaning": "耐久性", "partOfSpeech": "名詞", "example": "", "exampleMeaning": ""},
    {"id": "init-70", "word": "anticipated", "meaning": "期待された", "partOfSpeech": "形容詞", "example": "", "exampleMeaning": ""},
    {"id": "init-71", "word": "remarkable", "meaning": "驚くべき", "partOfSpeech": "形容詞", "example": "", "exampleMeaning": ""},
    {"id": "init-72", "word": "faculty", "meaning": "(大学の)教員", "partOfSpeech": "名詞", "example": "", "exampleMeaning": ""},
    {"id": "init-73", "word": "maneuverable", "meaning": "操作しやすい", "partOfSpeech": "形容詞", "example": "", "exampleMeaning": ""},
    {"id": "init-74", "word": "lawnmower", "meaning": "芝刈り機", "partOfSpeech": "名詞", "example": "", "exampleMeaning": ""},
    {"id": "init-75", "word": "precisely", "meaning": "ちょうど、正確に", "partOfSpeech": "副詞", "example": "", "exampleMeaning": ""},
    {"id": "init-76", "word": "exhaustively", "meaning": "徹底的に", "partOfSpeech": "副詞", "example": "", "exampleMeaning": ""},
    {"id": "init-77", "word": "exceedingly", "meaning": "非常に", "partOfSpeech": "副詞", "example": "", "exampleMeaning": ""},
    {"id": "init-78", "word": "noticeably", "meaning": "著しく、目立って", "partOfSpeech": "副詞", "example": "", "exampleMeaning": ""},
    {"id": "init-79", "word": "feature", "meaning": "〜を呼び物にする", "partOfSpeech": "動詞", "example": "", "exampleMeaning": ""},
    {"id": "init-80", "word": "extensive", "meaning": "広範囲の", "partOfSpeech": "形容詞", "example": "", "exampleMeaning": ""},
    {"id": "init-81", "word": "notably", "meaning": "特に", "partOfSpeech": "副詞", "example": "", "exampleMeaning": ""},
    {"id": "init-82", "word": "chair", "meaning": "〜の議長を務める", "partOfSpeech": "動詞", "example": "", "exampleMeaning": ""},
    {"id": "init-83", "word": "contribution", "meaning": "貢献", "partOfSpeech": "名詞", "example": "", "exampleMeaning": ""},
    {"id": "init-84", "word": "evident", "meaning": "明白な、明らかな", "partOfSpeech": "形容詞", "example": "", "exampleMeaning": ""},
    {"id": "init-85", "word": "revise", "meaning": "〜を修正する、見直す", "partOfSpeech": "動詞", "example": "", "exampleMeaning": ""},
    {"id": "init-86", "word": "reliable", "meaning": "信頼できる", "partOfSpeech": "形容詞", "example": "", "exampleMeaning": ""},
    {"id": "init-87", "word": "acquaintance", "meaning": "知人", "partOfSpeech": "名詞", "example": "", "exampleMeaning": ""},
    {"id": "init-88", "word": "implement", "meaning": "〜を実行する", "partOfSpeech": "動詞", "example": "", "exampleMeaning": ""},
    {"id": "init-89", "word": "subsequently", "meaning": "その後で", "partOfSpeech": "副詞", "example": "", "exampleMeaning": ""},
    {"id": "init-90", "word": "recognition", "meaning": "評価", "partOfSpeech": "名詞", "example": "", "exampleMeaning": ""},
    {"id": "init-91", "word": "subordinate", "meaning": "部下", "partOfSpeech": "名詞", "example": "", "exampleMeaning": ""},
    {"id": "init-92", "word": "as of X", "meaning": "X(日時)以降", "partOfSpeech": "熟語", "example": "", "exampleMeaning": ""},
    {"id": "init-93", "word": "enforce", "meaning": "〜を施行する", "partOfSpeech": "動詞", "example": "", "exampleMeaning": ""},
    {"id": "init-94", "word": "intentionally", "meaning": "意図的に", "partOfSpeech": "副詞", "example": "", "exampleMeaning": ""},
    {"id": "init-95", "word": "cut back on X", "meaning": "Xを減らす", "partOfSpeech": "熟語", "example": "", "exampleMeaning": ""},
    {"id": "init-96", "word": "practically", "meaning": "ほとんど", "partOfSpeech": "副詞", "example": "", "exampleMeaning": ""},
    {"id": "init-97", "word": "complication", "meaning": "やっかいな問題、複雑さ", "partOfSpeech": "名詞", "example": "", "exampleMeaning": ""},
    {"id": "init-98", "word": "take on X", "meaning": "Xをしようと決める", "partOfSpeech": "熟語", "example": "", "exampleMeaning": ""},
    {"id": "init-99", "word": "retain", "meaning": "〜を維持する、持ち続ける", "partOfSpeech": "動詞", "example": "", "exampleMeaning": ""},
    {"id": "init-100", "word": "swiftly", "meaning": "素早く、迅速に", "partOfSpeech": "副詞", "example": "", "exampleMeaning": ""},
    {"id": "init-101", "word": "seemingly", "meaning": "見たところ、外見上は", "partOfSpeech": "副詞", "example": "", "exampleMeaning": ""},
    {"id": "init-102", "word": "grant", "meaning": "〜を与える、許可する", "partOfSpeech": "動詞", "example": "", "exampleMeaning": ""},
    {"id": "init-103", "word": "decline", "meaning": "(丁寧に)断る", "partOfSpeech": "動詞", "example": "", "exampleMeaning": ""},
    {"id": "init-104", "word": "respectfully", "meaning": "丁寧に", "partOfSpeech": "副詞", "example": "", "exampleMeaning": ""},
    {"id": "init-105", "word": "assure", "meaning": "〜を保証する、請け合う", "partOfSpeech": "動詞", "example": "", "exampleMeaning": ""},
    {"id": "init-106", "word": "accomplished", "meaning": "熟練の", "partOfSpeech": "形容詞", "example": "", "exampleMeaning": ""},
    {"id": "init-107", "word": "impending", "meaning": "今にも起ころうとしている", "partOfSpeech": "形容詞", "example": "", "exampleMeaning": ""},
    {"id": "init-108", "word": "confidential", "meaning": "内密の、機密の", "partOfSpeech": "形容詞", "example": "", "exampleMeaning": ""},
    {"id": "init-109", "word": "managerial", "meaning": "管理職の", "partOfSpeech": "形容詞", "example": "", "exampleMeaning": ""},
    {"id": "init-110", "word": "ventilate", "meaning": "〜を換気する", "partOfSpeech": "動詞", "example": "", "exampleMeaning": ""},
    {"id": "init-111", "word": "coal", "meaning": "石炭", "partOfSpeech": "名詞", "example": "", "exampleMeaning": ""}
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
                    return data
        except Exception as e:
            st.error(f"データの読み込みに失敗しました: {e}")
    # ファイルが存在しない、または破損している場合は初期111単語を登録して保存
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
# AI 単語情報生成 (単語から全体を自動生成)
# ---------------------------------------------------------
def generate_word_info(word_text, client):
    prompt = f"""
    英単語または熟語「{word_text}」の意味、主要な品詞、自然な例文、その例文の日本語訳をJSON形式で返してください。
    【キー名】
    - meaning: 日本語の意味（簡潔に）
    - partOfSpeech: 品詞（名詞, 動詞, 形容詞, 副詞, 熟語 など）
    - example: 英語の例文
    - exampleMeaning: 例文の日本語訳
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
# AI 例文自動生成 (単語と意味から例文・例文訳のみ生成)
# ---------------------------------------------------------
def generate_example_info(word_text, meaning_text, client):
    if not client:
        return {"example": "", "exampleMeaning": ""}
    
    prompt = f"""
    英単語/熟語「{word_text}」（意味: {meaning_text}）を使った自然でわかりやすい英語の例文と、その例文の日本語訳をJSON形式で生成してください。
    【キー名】
    - example: 英語の例文
    - exampleMeaning: 例文の日本語訳
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
        st.warning(f"例文の自動生成でエラーが発生したため、例文なしで登録します: {e}")
        return {"example": "", "exampleMeaning": ""}

# ---------------------------------------------------------
# サイドバーナビゲーション
# ---------------------------------------------------------
st.sidebar.title("📘 英単語テストメーカー")

client = get_genai_client()
if not client:
    st.sidebar.info("💡 **Gemini APIキー設定ガイド**\nAI生成機能を使うには、Streamlit CloudのSecretsに `GEMINI_API_KEY` を設定してください。")

nav_choice = st.sidebar.radio(
    "メニューを選択",
    ["📚 単語の管理・一覧", "🤖 AI単語自動生成", "🎴 暗記カード・確認テスト", "🖨️ A4テスト印刷・PDF"]
)

# 保存されている単語数表示
st.sidebar.metric("登録単語数", f"{len(st.session_state.word_list)} 件")

# ---------------------------------------------------------
# 1. 単語の管理・一覧
# ---------------------------------------------------------
if nav_choice == "📚 単語の管理・一覧":
    st.header("📚 単語の管理・一覧")
    
    # 検索フィルター
    search_query = st.text_input("🔍 単語・意味で検索", "").strip().lower()
    
    # 単語追加フォーム（英単語/熟語と意味のみ入力）
    with st.expander("➕ 新しい単語を手動追加", expanded=False):
        st.caption("※ 英単語と意味を入力すると、AIが自動で例文とその日本語訳を生成して追加します。")
        with st.form("add_form", clear_on_submit=True):
            col_w, col_m = st.columns(2)
            with col_w:
                w_input = st.text_input("英単語 / 熟語 *", placeholder="例: resilience")
            with col_m:
                m_input = st.text_input("日本語の意味 *", placeholder="例: 回復力、復元力")
            
            submitted = st.form_submit_button("単語を追加・保存 (例文を自動生成)")
            if submitted:
                if w_input and m_input:
                    with st.spinner("例文と日本語訳をAIで自動生成中..."):
                        ex_info = generate_example_info(w_input, m_input, client)
                        new_item = {
                            "id": f"custom-{len(st.session_state.word_list) + 1}",
                            "word": w_input,
                            "meaning": m_input,
                            "partOfSpeech": "",
                            "example": ex_info.get("example", ""),
                            "exampleMeaning": ex_info.get("exampleMeaning", "")
                        }
                        st.session_state.word_list.append(new_item)
                        save_words(st.session_state.word_list)
                        st.success(f"「{w_input}」を追加・保存しました！ (例文と日本語訳を自動作成しました)")
                        st.rerun()
                else:
                    st.warning("英単語と日本語の意味は必須です。")

    # 一覧のフィルタリング
    filtered_words = [
        w for w in st.session_state.word_list
        if search_query in w["word"].lower() or search_query in w["meaning"].lower()
    ]
    
    st.subheader(f"単語リスト ({len(filtered_words)} / {len(st.session_state.word_list)} 件)")
    
    # 品詞の欄を除いた一覧表（英単語, 意味, 例文, 例文訳）
    if filtered_words:
        df = pd.DataFrame(filtered_words)
        df_display = df.rename(columns={
            "word": "英単語",
            "meaning": "意味",
            "example": "例文",
            "exampleMeaning": "例文訳"
        })
        st.dataframe(df_display[["英単語", "意味", "例文", "例文訳"]], use_container_width=True)
    else:
        st.info("該当する単語が見つかりません。")

    st.divider()
    
    col_a, col_b = st.columns(2)
    with col_a:
        # バックアップ・エクスポート
        json_str = json.dumps(st.session_state.word_list, ensure_ascii=False, indent=2)
        st.download_button(
            label="📥 単語リストをJSON保存 (バックアップ)",
            data=json_str,
            file_name="words_backup.json",
            mime="application/json"
        )
    with col_b:
        # リセットボタン
        if st.button("⚠️ 初期状態 (111単語) にリセット", type="secondary"):
            st.session_state.word_list = list(INITIAL_WORDS)
            save_words(st.session_state.word_list)
            st.success("初期単語データ (111件) にリセットしました！")
            st.rerun()

# ---------------------------------------------------------
# 2. AI単語自動生成 (Gemini API)
# ---------------------------------------------------------
elif nav_choice == "🤖 AI単語自動生成":
    st.header("🤖 AI単語自動生成 (Gemini API)")
    st.write("英単語を入力すると、Gemini AI が自動的に意味・例文・例文訳を作成してリストに自動保存します。")
    
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
                        "partOfSpeech": res.get("partOfSpeech", ""),
                        "example": res.get("example", ""),
                        "exampleMeaning": res.get("exampleMeaning", "")
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
        
        # フラッシュカード
        with tab1:
            st.subheader("フラッシュカード暗記")
            if "card_idx" not in st.session_state:
                st.session_state.card_idx = 0
            if "show_meaning" not in st.session_state:
                st.session_state.show_meaning = False

            words_len = len(st.session_state.word_list)
            st.session_state.card_idx = st.session_state.card_idx % words_len
            curr_word = st.session_state.word_list[st.session_state.card_idx]

            c1, c2, c3 = st.columns([1, 2, 1])
            with c2:
                st.markdown(f"**Card {st.session_state.card_idx + 1} / {words_len}**")
                
                pos_info = f"\n\n*品詞: {curr_word['partOfSpeech']}*" if curr_word.get('partOfSpeech') else ""
                st.info(f"### 🔤 **{curr_word['word']}**{pos_info}")
                
                if st.session_state.show_meaning:
                    ex_str = f"\n\n📝 **例文**: {curr_word['example']}" if curr_word.get('example') else ""
                    ex_m_str = f"\n\n🗣️ **訳**: {curr_word['exampleMeaning']}" if curr_word.get('exampleMeaning') else ""
                    st.success(f"💡 **意味**: {curr_word['meaning']}{ex_str}{ex_m_str}")
                
                col_btn1, col_btn2 = st.columns(2)
                with col_btn1:
                    if st.button("👁️ 意味を表示 / 隠す", use_container_width=True):
                        st.session_state.show_meaning = not st.session_state.show_meaning
                        st.rerun()
                with col_btn2:
                    if st.button("次へ ➡️", use_container_width=True):
                        st.session_state.card_idx = (st.session_state.card_idx + 1) % words_len
                        st.session_state.show_meaning = False
                        st.rerun()

        # 4択確認テスト
        with tab2:
            st.subheader("4択確認テスト")
            if "quiz_score" not in st.session_state:
                st.session_state.quiz_score = 0
            if "quiz_count" not in st.session_state:
                st.session_state.quiz_count = 0

            if len(st.session_state.word_list) < 4:
                st.warning("4択テストを行うには最低4個以上の単語が必要です。")
            else:
                if st.button("🎲 新しいクイズを出題"):
                    target = random.choice(st.session_state.word_list)
                    others = random.sample([w for w in st.session_state.word_list if w["id"] != target["id"]], 3)
                    choices = [target["meaning"]] + [o["meaning"] for o in others]
                    random.shuffle(choices)
                    st.session_state.quiz_target = target
                    st.session_state.quiz_choices = choices
                    st.session_state.quiz_answered = False

                if "quiz_target" in st.session_state:
                    q_target = st.session_state.quiz_target
                    st.markdown(f"### 問題: **{q_target['word']}** の正しい意味は？")
                    
                    for idx, choice in enumerate(st.session_state.quiz_choices):
                        if st.button(f"{idx+1}. {choice}", key=f"choice_{idx}"):
                            st.session_state.quiz_count += 1
                            if choice == q_target["meaning"]:
                                st.session_state.quiz_score += 1
                                st.balloons()
                                st.success("⭕ 正解です！")
                            else:
                                st.error(f"❌ 不正解... 正解は「{q_target['meaning']}」でした。")
                    
                    st.write(f"現在のスコア: {st.session_state.quiz_score} / {st.session_state.quiz_count}")

# ---------------------------------------------------------
# 4. A4テスト印刷・PDF出力
# ---------------------------------------------------------
elif nav_choice == "🖨️ A4テスト印刷・PDF":
    st.header("🖨️ A4 印刷用テストシート作成")
    
    if not st.session_state.word_list:
        st.warning("単語が登録されていません。先に単語を登録してください。")
    else:
        col1, col2 = st.columns(2)
        with col1:
            print_title = st.text_input("テストタイトル", "英単語確認テスト")
            test_mode = st.selectbox("テスト出力形式", ["英単語 → 日本語の意味", "日本語の意味 → 英単語", "単語帳一覧シート"])
        with col2:
            is_shuffle = st.checkbox("問題をランダム順にする", value=True)
            show_ans = st.checkbox("解答をあらかじめ印字する (解答集)", value=False)
            
        print_words = list(st.session_state.word_list)
        if is_shuffle:
            random.seed(123)
            print_words = random.sample(print_words, len(print_words))

        # テーブル行作成
        rows_html = ""
        for i, w in enumerate(print_words, 1):
            pos_label = f" <span style='font-size:11px;color:#64748b;'>({w['partOfSpeech']})</span>" if w.get('partOfSpeech') else ""
            if test_mode == "英単語 → 日本語の意味":
                col_q = f"<b>{w['word']}</b>{pos_label}"
                col_a = w['meaning'] if show_ans else ""
            elif test_mode == "日本語の意味 → 英単語":
                col_q = w['meaning']
                col_a = f"<b>{w['word']}</b>" if show_ans else ""
            else:
                col_q = f"<b>{w['word']}</b>"
                col_a = f"{w['meaning']}"

            rows_html += f"""
            <tr style="height: 35px; border-bottom: 1px solid #e2e8f0;">
                <td style="width: 8%; text-align: center; font-weight: bold; font-size: 13px;">{i}</td>
                <td style="width: 42%; padding: 4px 8px; font-size: 14px;">{col_q}</td>
                <td style="width: 50%; padding: 4px 8px; font-size: 14px;">{col_a}</td>
            </tr>
            """

        full_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                @page {{
                    size: A4 portrait;
                    margin: 12mm;
                }}
                body {{
                    font-family: 'Helvetica Neue', Arial, 'Hiragino Kaku Gothic ProN', Meiryo, sans-serif;
                    color: #0f172a;
                    margin: 0;
                    padding: 0;
                }}
                .print-box {{
                    max-width: 800px;
                    margin: 0 auto;
                    background: #ffffff;
                    padding: 10px;
                }}
                .header-bar {{
                    display: flex;
                    justify-content: space-between;
                    align-items: flex-end;
                    border-bottom: 2px solid #0f172a;
                    padding-bottom: 8px;
                    margin-bottom: 15px;
                }}
                .title-text {{
                    font-size: 20px;
                    font-weight: bold;
                }}
                .score-area {{
                    font-size: 13px;
                    border: 1px solid #475569;
                    padding: 4px 10px;
                    border-radius: 4px;
                }}
                table {{
                    width: 100%;
                    border-collapse: collapse;
                }}
            </style>
        </head>
        <body>
            <div style="margin-bottom: 15px;">
                <button onclick="window.print()" style="background-color: #2563eb; color: #ffffff; border: none; padding: 10px 22px; font-size: 15px; font-weight: bold; border-radius: 6px; cursor: pointer;">
                    🖨️ A4で印刷 / PDFとして保存
                </button>
            </div>
            
            <div class="print-box">
                <div class="header-bar">
                    <div class="title-text">{print_title} {"(解答集)" if show_ans else ""}</div>
                    <div class="score-area">
                        点数: &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; / {len(print_words)}
                    </div>
                </div>
                
                <table>
                    <thead>
                        <tr style="background-color: #f1f5f9; border-bottom: 2px solid #94a3b8;">
                            <th style="padding: 6px; text-align: center; width: 8%;">No.</th>
                            <th style="padding: 6px; text-align: left; width: 42%;">問題</th>
                            <th style="padding: 6px; text-align: left; width: 50%;">解答欄</th>
                        </tr>
                    </thead>
                    <tbody>
                        {rows_html}
                    </tbody>
                </table>
            </div>
        </body>
        </html>
        """
        
        st.components.v1.html(full_html, height=900, scrolling=True)
