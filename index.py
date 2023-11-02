import streamlit as st
from google.cloud import vision
from google.oauth2 import service_account
import io

# Vision APIを認証してリクエストを行う関数
def detect_labels(image_bytes):
    credentials = service_account.Credentials.from_service_account_info(st.secrets["gcp_service_account"])
    client = vision.ImageAnnotatorClient(credentials=credentials)
    
    image = vision.Image(content=image_bytes)
    response = client.label_detection(image=image)
    labels = response.label_annotations
    return labels

# Streamlitアプリ
def main():
    st.title('Google Vision APIを利用した画像認識')

    uploaded_file = st.file_uploader("画像を選択してください...", type=["jpg", "jpeg", "png"])
    if uploaded_file is not None:
        image_bytes = uploaded_file.getvalue()
        
        # アップロードされた画像を表示
        st.image(uploaded_file, caption='アップロードされた画像', use_column_width=True)
        
        # Google Vision APIを呼び出してラベルを検出
        labels = detect_labels(image_bytes)
        
        # 結果を表示
        if labels:
            st.write('検出されたラベル:')
            for label in labels:
                st.write(f"{label.description} : {round(label.score * 100, 4)}%")
        else:
            st.write("ラベルは検出されませんでした。")

# Streamlitアプリを実行
if __name__ == '__main__':
    main()
