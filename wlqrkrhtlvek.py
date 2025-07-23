import streamlit as st
st.title('웹 사이트 만들기')
import streamlit as st
import pandas as pd
import openai

# --- 초기 설정 ---
openai.api_key = st.secrets.get("OPENAI_API_KEY", "sk-...")

st.set_page_config(page_title="AI 수학 오답노트", layout="wide")
st.title("📘 AI 기반 수학 오답노트 생성기")

# --- 문제 입력 방식 선택 ---
st.header("1️⃣ 수학 문제 입력")
input_method = st.radio("문제 입력 방식", ["CSV 업로드", "직접 입력"], horizontal=True)

# 세션 초기화
data_key = "custom_problems"
if data_key not in st.session_state:
    st.session_state[data_key] = []

# --- CSV 업로드 ---
if input_method == "CSV 업로드":
    uploaded_file = st.file_uploader("CSV 파일 업로드", type="csv")
    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        st.session_state[data_key] = df.to_dict(orient="records")
        st.success("CSV 파일 업로드 완료!")
        st.dataframe(df)

# --- 직접 입력 ---
else:
    with st.form("문제입력", clear_on_submit=True):
        qnum = st.text_input("문제 번호")
        qtext = st.text_area("문제 내용", height=100)
        correct = st.text_input("정답")
        user_ans = st.text_input("내가 푼 답")
        explanation = st.text_area("내가 쓴 풀이 과정", height=150)
        submit = st.form_submit_button("문제 추가")

        if submit:
            st.session_state[data_key].append({
                "문제번호": qnum,
                "문제": qtext,
                "정답": correct,
                "사용자답안": user_ans,
                "풀이과정": explanation
            })
            st.success(f"{qnum}번 문제 추가 완료!")

# --- 문제 목록 확인 ---
if st.session_state[data_key]:
    st.markdown("### ✅ 입력한 문제 목록")
    df = pd.DataFrame(st.session_state[data_key])
    st.dataframe(df)

    st.markdown("---")
    st.header("2️⃣ 오답 분석 및 다시 풀기")
    qnums = df["문제번호"].tolist()
    selected = st.selectbox("분석할 문제 선택", qnums)
    prob = df[df["문제번호"] == selected].iloc[0]

    # 문제 정보 표시
    st.subheader(f"문제 {selected}")
    st.markdown(f"**문제:** {prob['문제']}")
    st.markdown(f"**정답:** {prob['정답']}")
    st.markdown(f"**내가 쓴 답:** {prob['사용자답안']}")
    st.markdown(f"**풀이 과정:**\n{prob['풀이과정']}")

    # GPT 분석 요청
    feedback_key = f"ai_feedback_{selected}"
    if st.button("🤖 AI 피드백 요청"):
        with st.spinner("AI가 분석 중입니다..."):
            prompt = f"""
[문제]
{prob['문제']}

[정답]
{prob['정답']}

[사용자의 풀이]
{prob['풀이과정']}

1. 사용자의 풀이에서 잘못된 부분이 있다면 구체적으로 설명해주세요.
2. 올바른 수학적 풀이 과정을 단계별로 제시해주세요.
3. 사용자가 오해하고 있을 수 있는 개념이 있다면 설명해주세요.
"""
            res = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3
            )
            st.session_state[feedback_key] = res["choices"][0]["message"]["content"]

    # 피드백 출력
    if feedback_key in st.session_state:
        st.markdown("### 🧠 AI 분석 결과")
        st.markdown(st.session_state[feedback_key])

    # 사용자 메모
    note_key = f"user_note_{selected}"
    note = st.text_area("✍️ 내가 깨달은 점 정리하기", value=st.session_state.get(note_key, ""))
    if st.button("📝 메모 저장"):
        st.session_state[note_key] = note
        st.success("메모 저장 완료!")

    # 다시 풀기 입력
    retry_key = f"retry_answer_{selected}"
    retry = st.text_area("🔁 다시 풀어보기", value=st.session_state.get(retry_key, ""))
    if st.button("✅ 다시 푼 풀이 저장"):
        st.session_state[retry_key] = retry
        st.success("다시 푼 풀이 저장 완료!")

    st.markdown("---")
    st.header("3️⃣ 오답노트 저장")
    if st.button("📥 CSV로 저장하기"):
        all_data = st.session_state[data_key]
        for item in all_data:
            qid = item["문제번호"]
            item["AI 피드백"] = st.session_state.get(f"ai_feedback_{qid}", "")
            item["사용자 메모"] = st.session_state.get(f"user_note_{qid}", "")
            item["다시 풀기"] = st.session_state.get(f"retry_answer_{qid}", "")

        result_df = pd.DataFrame(all_data)
        csv = result_df.to_csv(index=False).encode("utf-8-sig")
        st.download_button("📄 오답노트 CSV 다운로드", data=csv, file_name="오답노트.csv", mime="text/csv")
