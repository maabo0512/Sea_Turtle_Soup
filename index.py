import streamlit as st
import openai
import math
import time

# アクセスのためのキーを設定
openai.api_key = st.secrets["openai"]["api_key"]

# セッション状態の初期化
if 'history' not in st.session_state:
    st.session_state.history = []
if 'exp' not in st.session_state:
    st.session_state.exp = 0
if 'level' not in st.session_state:
    st.session_state.level = 1
if 'start_time' not in st.session_state:
    st.session_state.start_time = None
if 'difficulty' not in st.session_state:
    st.session_state.difficulty = 'かんたん'

# 経験値とレベルの計算式
def calculate_level(exp):
    return math.floor(exp ** (1/3))

# 経験値を追加する関数
def add_experience(num_questions):
    difficulty_multiplier = {
        'かんたん': 1,
        'ふつう': 2,
        'むずかしい': 3
    }
    base_exp = 10
    # 質問数が少ないほど高い経験値を獲得する
    exp_gained = base_exp * difficulty_multiplier[st.session_state.difficulty] * (10 / num_questions)
    st.session_state.exp += exp_gained
    new_level = calculate_level(st.session_state.exp)
    if new_level > st.session_state.level:
        st.session_state.level = new_level
        st.balloons()
        st.success(f"レベルアップしました！ 新しいレベル: {st.session_state.level}")

# 制限時間を設定する関数
def set_time_limit(difficulty):
    if difficulty == 'かんたん':
        return None  # 制限時間なし
    elif difficulty == 'ふつう':
        return 20 * 60  # 制限時間20分
    elif difficulty == 'むずかしい':
        return 5 * 60  # 制限時間5分
    else:
        return None

# UIのタイトル
st.title('ウミガメのスープアプリ')

# 経験値とレベルの表示
st.sidebar.header(f"レベル: {st.session_state.level}")
st.sidebar.progress((st.session_state.exp % 100) / 100)
st.sidebar.text(f"経験値: {st.session_state.exp}")

# 難易度の選択
difficulty_options = ['かんたん', 'ふつう', 'むずかしい']
st.session_state.difficulty = st.sidebar.radio("難易度", difficulty_options)

# 制限時間の表示
time_limit = set_time_limit(st.session_state.difficulty)
if time_limit is not None:
    if st.session_state.start_time is None:
        st.session_state.start_time = time.time()
    elapsed_time = time.time() - st.session_state.start_time
    time_left = max(time_limit - elapsed_time, 0)
    st.sidebar.text(f"残り時間: {int(time_left // 60)}分{int(time_left % 60)}秒")
    if time_left <= 0:
        st.error("制限時間です。次の問題に進んでください。")
        # 問題をリセットするコードをここに追加

# 以下、質問入力、質問送信ボタン、履歴の表示などのコードはそのまま...

# 質問送信ボタン
if st.button('質問する'):
    if question:
        # 質問をAPIに送信して回答を取得
        answer = ask_question_to_gpt(question)
        # 履歴を更新
        st.session_state.history.append({'question': question, 'answer': answer})
        # 経験値を追加
        add_experience(len(st.session_state.history))
    else:
        st.error("質問を入力してください。")
