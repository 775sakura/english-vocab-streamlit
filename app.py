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
# Google GenAI クライアントの初期化
# ---------------------------------------------------------
def get_genai_client():
    # Streamlit Secrets から API キーを取得、なければ環境変数から取得
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
    st.session_state.word_list = [
        {"id": "1", "word": "abandon", "meaning": "〜を捨て去る、放棄する", "partOfSpeech": "動詞", "example": "He had to abandon his car in the snow.", "exampleMeaning": "彼は雪の中に車を乗り捨てなければならなかった。"},
        {"id": "2", "word": "abundant", "meaning": "豊富な、大量の", "partOfSpeech": "形容詞", "example": "The region is abundant in natural resources.", "exampleMeaning": "その地域は天然資源が豊富だ。"},
        {"id": "3", "word": "accumulate", "meaning": "蓄積する、積み上げる", "partOfSpeech": "動詞", "example": "Dust soon accumulates if the house is not cleaned.", "exampleMeaning": "家を掃除しないと、すぐにホコリがたまる。"},
        {"id": "4", "word": "adequate", "meaning": "適切な、十分な", "partOfSpeech": "形容詞", "example": "The supply is adequate for our needs.", "exampleMeaning": "供給は私たちのニーズに十分対応している。"},
        {"id": "5", "word": "advocate", "meaning": "〜を主張する、擁護者", "partOfSpeech": "動詞", "example": "She is a strong advocate for education reform.", "exampleMeaning": "彼女は教育改革の強力な支持者だ。"}
    ]

if "mode" not in st.session_state:
    st.session_state.mode = "manage"  # "manage" or "print"

# ---------------------------------------------------------
# AI 単語自動生成関数
# ---------------------------------------------------------
def generate_word_info(word_text, client):
    prompt = f"""
    英単語「{word_text}」の意味、主要な品詞、自然な例文、その例文の日本語訳をJSONフォーマットで出力してください。
    キー名:
    - meaning: 日本語の意味（短く簡潔に）
    - partOfSpeech: 品詞（名詞、動詞、形容詞、副詞など）
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
# サイドバーナビゲーション
# ---------------------------------------------------------
st.sidebar.title("📝 英単語テストメーカー")

# APIキー設定チェック
client = get_genai_client()
if not client:
    st.sidebar.warning("⚠️ GEMINI_API_KEY が設定されていません。\nSecrets設定画面で追加してください。")

page = st.sidebar.radio("機能を選択", ["単語の管理・登録", "AI単語自動生成", "テスト・印刷シート作成"])

# ---------------------------------------------------------
# ページ1: 単語の管理・登録
# ---------------------------------------------------------
if page == "単語の管理・登録":
    st.header("📚 単語の管理・編集")
    
    # 手動登録フォーム
    with st.expander("➕ 新しい単語を手動追加", expanded=False):
        with st.form("add_word_form"):
            col1, col2 = st.columns(2)
            with col1:
                new_word = st.text_input("英単語")
                new_meaning = st.text_input("意味 (日本語)")
                new_pos = st.selectbox("品詞", ["名詞", "動詞", "形容詞", "副詞", "熟語・その他"])
            with col2:
                new_example = st.text_area("例文 (英語)")
                new_ex_meaning = st.text_area("例文の訳 (日本語)")
            
            submit = st.form_submit_button("単語を追加")
            if submit and new_word:
                st.session_state.word_list.append({
                    "id": str(len(st.session_state.word_list) + 1),
                    "word": new_word,
                    "meaning": new_meaning,
                    "partOfSpeech": new_pos,
                    "example": new_example,
                    "exampleMeaning": new_ex_meaning
                })
                st.success(f"「{new_word}」を追加しました！")
                st.rerun()

    # 一覧表示・削除
    st.subheader(f"登録済み単語一覧 ({len(st.session_state.word_list)}件)")
    if st.session_state.word_list:
        df = pd.DataFrame(st.session_state.word_list)
        df_display = df.rename(columns={
            "word": "英単語",
            "meaning": "日本語の意味",
            "partOfSpeech": "品詞",
            "example": "例文",
            "exampleMeaning": "例文訳"
        })
        st.dataframe(df_display[["英単語", "日本語の意味", "品詞", "例文", "例文訳"]], use_container_width=True)
        
        if st.button("🗑️ 全単語をリセット"):
            st.session_state.word_list = []
            st.rerun()

# ---------------------------------------------------------
# ページ2: AI単語自動生成
# ---------------------------------------------------------
elif page == "AI単語自動生成":
    st.header("🤖 AI単語自動作成 (Gemini API)")
    st.write("英単語を入力すると、AIが意味・品詞・例文・例文訳を自動生成して追加します。")
    
    if not client:
        st.error("AI機能を使用するには Streamlit Cloud の Secrets で GEMINI_API_KEY を設定してください。")
    else:
        target_word = st.text_input("生成したい英単語を入力 (例: resilience)", key="ai_input")
        if st.button("✨ AIで自動作成") and target_word:
            with st.spinner("AIが情報を生成中..."):
                info = generate_word_info(target_word, client)
                if info:
                    st.session_state.word_list.append({
                        "id": str(len(st.session_state.word_list) + 1),
                        "word": target_word,
                        "meaning": info.get("meaning", ""),
                        "partOfSpeech": info.get("partOfSpeech", "名詞"),
                        "example": info.get("example", ""),
                        "exampleMeaning": info.get("exampleMeaning", "")
                    })
                    st.success(f"「{target_word}」の登録が完了しました！")
                    st.json(info)

# ---------------------------------------------------------
# ページ3: テスト・印刷シート作成
# ---------------------------------------------------------
elif page == "テスト・印刷シート作成":
    st.header("🖨️ A4 印刷テストシート作成")
    
    if not st.session_state.word_list:
        st.warning("単語が登録されていません。先に単語を登録してください。")
    else:
        col1, col2 = st.columns(2)
        with col1:
            title = st.text_input("テストのタイトル", "英単語確認テスト")
            test_type = st.selectbox("テスト形式", ["単語 → 意味を書く", "意味 → 単語を書く", "単語帳一覧"])
        with col2:
            shuffle = st.checkbox("問題をランダムにシャッフルする", value=True)
            show_answers = st.checkbox("解答欄を表示する（解答集として使用）", value=False)
            
        words = list(st.session_state.word_list)
        if shuffle:
            random.seed(42)  # 表示の安定化のため
            words = random.sample(words, len(words))

        st.subheader("印刷プレビュー")
        
        # A4用 HTML / CSS の構築
        table_rows = ""
        for idx, w in enumerate(words, 1):
            if test_type == "単語 → 意味を書く":
                c1 = f"<b>{w['word']}</b> <span style='font-size:11px;color:#666;'>({w['partOfSpeech']})</span>"
                c2 = w['meaning'] if show_answers else ""
            elif test_type == "意味 → 単語を書く":
                c1 = w['meaning']
                c2 = f"<b>{w['word']}</b>" if show_answers else ""
            else: # 単語帳一覧
                c1 = f"<b>{w['word']}</b>"
                c2 = f"({w['partOfSpeech']}) {w['meaning']}"

            table_rows += f"""
            <tr style="height: 35px; border-bottom: 1px solid #e2e8f0;">
                <td style="width: 8%; text-align: center; font-weight: bold; font-size: 13px;">{idx}</td>
                <td style="width: 42%; padding: 4px 8px; font-size: 14px;">{c1}</td>
                <td style="width: 50%; padding: 4px 8px; font-size: 14px;">{c2}</td>
            </tr>
            """

        html_code = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                @page {{
                    size: A4 portrait;
                    margin: 15mm;
                }}
                body {{
                    font-family: 'Helvetica Neue', Arial, 'Hiragino Kaku Gothic ProN', 'Hiragino Sans', Meiryo, sans-serif;
                    color: #1e293b;
                    margin: 0;
                    padding: 0;
                }}
                .print-container {{
                    max-width: 800px;
                    margin: 0 auto;
                    background: white;
                    padding: 20px;
                }}
                .header {{
                    display: flex;
                    justify-content: space-between;
                    align-items: flex-end;
                    border-bottom: 2px solid #0f172a;
                    padding-bottom: 10px;
                    margin-bottom: 20px;
                }}
                .title {{
                    font-size: 22px;
                    font-weight: bold;
                    color: #0f172a;
                }}
                .score-box {{
                    font-size: 14px;
                    border: 1px solid #64748b;
                    padding: 4px 12px;
                    border-radius: 4px;
                }}
                table {{
                    width: 100%;
                    border-collapse: collapse;
                }}
                @media print {{
                    .no-print {{ display: none !important; }}
                    .print-container {{ padding: 0; }}
                }}
            </style>
        </head>
        <body>
            <div class="no-print" style="margin-bottom: 15px;">
                <button onclick="window.print()" style="background-color: #2563eb; color: white; border: none; padding: 10px 20px; font-size: 16px; border-radius: 6px; cursor: pointer;">
                    🖨️ A4用紙に印刷 / PDF保存
                </button>
            </div>
            
            <div class="print-container">
                <div class="header">
                    <div class="title">{title} {"(解答シート)" if show_answers else ""}</div>
                    <div class="score-box">
                        得点: &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; / {len(words)}
                    </div>
                </div>
                
                <table>
                    <thead>
                        <tr style="background-color: #f8fafc; border-bottom: 2px solid #cbd5e1;">
                            <th style="padding: 6px; text-align: center; width: 8%;">No.</th>
                            <th style="padding: 6px; text-align: left; width: 42%;">問題</th>
                            <th style="padding: 6px; text-align: left; width: 50%;">解答欄</th>
                        </tr>
                    </thead>
                    <tbody>
                        {table_rows}
                    </tbody>
                </table>
            </div>
        </body>
        </html>
        """
        
        st.components.v1.html(html_code, height=900, scrolling=True)
