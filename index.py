import streamlit as st
import openai
import math
import time
import random

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
if 'current_question' not in st.session_state:
    st.session_state.current_question = None
if 'time_up' not in st.session_state:
    st.session_state.time_up = False
if 'questions' not in st.session_state:
    st.session_state.questions = [
        {
            'title': '問題：プログラミングに興味があるハヤトくん',
            'text': 'プログラミングに興味があるハヤトくん。一番プログラミングを教えるのが上手いと思うプログラミングスクールへ向かったハヤトくんは、「定員に達しましたため、受付を終了します」の札を見て喜んでいます。何故でしょうか？',
            'answer': 'ハヤトくんはそのプログラミングスクールの経営者であり、自分の経営するプログラミングスクールの募集状況を確認しに行ったところ、満員となっていることが分かったため喜んだ。',
            'difficulty': 'かんたん'
        },
        {
            'title': '問題：逆走するタクシー運転手のノリミネさん',
            'text': 'タクシー運転手をしているノリミネさん。ある時ノリミネさんは、一方通行の道を逆方向に走っていました。パトロール中の警察官に見られてしまいましたが、怒られませんでした。何故でしょうか？',
            'answer': 'ノリミネさんは車に乗っておらず、一方通行の道を徒歩で逆方向に進んでいただけだったため。',
            'difficulty': 'ふつう'
        },
        {
            'title': '問題：双子じゃない！？',
            'text': 'ある女性から生まれた子供2人は、同じ日の同じ時間に誕生しています。でも、なぜか2人は双子ではありませんでした。何故でしょうか？',
            'answer': '女性の子供は双子ではなく、三つ子だったため。',
            'difficulty': 'むずかしい'
        },
    ]

# 問題を取得する関数
def get_question(difficulty):
    available_questions = [q for q in st.session_state.questions if q['difficulty'] == difficulty]
    if available_questions:
        # リストからランダムに問題を選択
        selected_question = random.choice(available_questions)
        return selected_question
    return None

# 遊び方のページ
def display_how_to_play():
    st.markdown("""
        1. 出題者はあなたに「ふしぎな内容が書かれた問題」を出します。
        2. あなたはその問題について、自由に質問してください。
        3. 問題を出題者はその質問に「はい」「いいえ」で答えます。
        4. あなたは何度も質問しながら謎解きをして、答え（真相）を当てることができればゲームはクリアです！
    """)

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

# 問題をリセットする関数
def reset_question():
    st.session_state.current_question = None
    st.session_state.history = []
    st.session_state.start_time = None
    st.session_state.time_up = False

# 問題の正解をチェックする関数
def check_answer(user_answer):
    correct_answer = st.session_state.current_question['answer']
    return user_answer.strip().lower() == correct_answer.strip().lower()

# ChatGPTに質問を送信し、回答を取得する関数
def ask_question_to_gpt(question):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "あなたは「ウミガメのスープ」ゲームの出題者です。問題文と解答を確認した上で、ユーザーから送信される質問に対して適切な回答をしてください。以下の選択肢から回答してください: はい、いいえ、たぶんはい、たぶんいいえ、はい（回答にはあまり関係ない）、いいえ（回答にはあまり関係ない）、わからない。"},
                {"role": "user", "content": question},
            ]
        )
        return response.choices[0].message["content"].strip()
    except openai.error.OpenAIError as e:
        return f"エラーが発生しました: {e}"

# 問題を出題する関数
def present_question():
    if st.session_state.current_question is None:
        st.session_state.current_question = get_question(st.session_state.difficulty)
    if st.session_state.current_question is not None:
        st.write(st.session_state.current_question['title'])
        st.session_state.start_time = time.time()  # 問題開始時間をリセット

# メインページの表示
def main_page():
    # UIのタイトル
    st.title('ウミガメのスープアプリ')

    # 遊び方の説明を折りたたみ式で表示
    with st.expander("ウミガメのスープの遊び方"):
        display_how_to_play()

    
    # 経験値とレベルの表示
    st.sidebar.header(f"レベル: {st.session_state.level}")
    st.sidebar.progress((st.session_state.exp % 100) / 100)
    st.sidebar.text(f"経験値: {st.session_state.exp}")

    # 難易度の選択
    difficulty_options = ['かんたん', 'ふつう', 'むずかしい']
    st.session_state.difficulty = st.sidebar.radio("難易度", difficulty_options)

    # ゲーム開始前に問題のタイトルを表示
    if st.session_state.current_question is None or st.session_state.current_question['difficulty'] != st.session_state.difficulty:
        st.session_state.current_question = get_question(st.session_state.difficulty)
    if st.session_state.current_question:
        st.subheader(st.session_state.current_question['title'])
            
 # 問題の出題と制限時間の設定
    if st.button('この問題を解く') or st.session_state.start_time is not None:
        if st.session_state.current_question:
            st.write(st.session_state.current_question['text'])  # 問題のテキストを表示
            st.session_state.start_time = time.time()
            st.session_state.time_up = False

        # 質問と答えのUIを表示
        # ...

    # 残り時間があるときのみ質問履歴を表示
    if st.session_state.history and not st.session_state.time_up:
        st.subheader("質問履歴")
        for entry in st.session_state.history:
            st.text(f"Q: {entry['question']}")
            st.text(f"A: {entry['answer']}")

# 残り時間の管理とアラート表示の関数
def manage_time_limit():
    # time_left を初期値で初期化
    time_left = None

    if st.session_state.start_time is not None:
        time_limit = set_time_limit(st.session_state.difficulty)
        if time_limit is not None and st.session_state.start_time is not None:
            elapsed_time = time.time() - st.session_state.start_time
            time_left = max(time_limit - elapsed_time, 0)
            time_display = f"残り時間: {int(time_left // 60)}分{int(time_left % 60)}秒"
            st.sidebar.text(f"残り時間: {int(time_left // 60)}分{int(time_left % 60)}秒")
            st.sidebar.markdown(f"<h3 style='color:red;'>{time_display}</h3>", unsafe_allow_html=True)

    # time_left が値を持つ場合のみ以下のコードを実行
    if time_left is not None:
        if time_left <= 0:
            if not st.session_state.time_up:
                st.session_state.time_up = True
                st.error("制限時間です。次の問題に進んでください。")
        elif time_left < 30:   # 30秒未満
            st.error("残り30秒です！")
        elif time_left < 60:   # 1分未満
            st.error("残り1分です！")
        elif time_left < 180:  # 3分未満
            st.warning("残り3分です！")
            
# 制限時間の表示と管理
    manage_time_limit()

# 問題が出題されている場合は質問と答えの入力を許可
    if st.session_state.current_question:
        # 質問の送信
        question = st.text_input("質問を入力してください", key="question")
        if st.button('質問を送信'):
            if question:
                # 質問をAPIに送信して回答を取得
                answer = ask_question_to_gpt(question)
                # 履歴を更新
                st.session_state.history.append({'question': question, 'answer': answer})
                st.session_state['question'] = ""  # 質問入力欄をリセット
            else:
                st.error("質問を入力してください。")

        # 答えの送信
        user_answer = st.text_input("答えが分かったらここに入力してください", key="user_answer")
        if st.button('答えを送信'):
            if check_answer(user_answer):
                st.success("大正解！")
                add_experience(len(st.session_state.history))  # 正解したので経験値を追加
                reset_question()
            else:
                st.error("不正解です。もう一度考えてみてください。")

# メインページの呼び出し
if __name__ == "__main__":
    main_page()