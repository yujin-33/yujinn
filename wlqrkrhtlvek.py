import streamlit as st
import pandas as pd

# GPT API 사용 여부 체크
try:
    import openai
    openai.api_key = st.secrets.get("OPENAI_API_KEY", "")
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

st.set_page_config(page_title="AI 수학 오답노트", layout="wide")
st.title("📘 AI 기반 수학 오답노트 생성기")

# 세션 초기화
if "custom_problems" not in st.session_state:
    st.session_state.custom_problems = []

st.header("1️⃣ 수학 문제 입력")
input_method = st.radio("문제 입력 방식", ["CSV 업로드", "직접 입력"], horizontal=True)

if input_method == "CSV 업로드":
    uploaded_file = st.file_uploader("CSV 파일 업로드", type="csv")
    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        st.session_state.custom_problems = df.to_dict(orient="records")
        st.success("CSV 업로드 완료!")
        st.dataframe(df)
else:
    with st.form("문제입력", clear_on_submit=True):
        qnum = st.text_input("문제 번호")
        qtext = st.text_area("문제 내용", height=100)
        correct = st.text_input("정답")
        user_ans = st.text_input("내가 푼 답")
        explanation = st.text_area("내 풀이 과정", height=150)
        submit = st.form_submit_button("문제 추가")
        if submit:
            st.session_state.custom_problems.append({
                "문제번호": qnum,
                "문제": qtext,
                "정답": correct,
                "사용자답안": user_ans,
                "풀이과정": explanation
            })
            st.success(f"{qnum}번 문제 추가됨!")

if st.session_state.custom_problems:
    df = pd.DataFrame(st.session_state.custom_problems)
    st.markdown("### ✅ 입력한 문제 목록")
    st.dataframe(df)

    st.markdown("---")
    st.header("2️⃣ 문제 선택 및 분석")

    selected = st.selectbox("분석할 문제 선택", df["문제번호"].tolist())
    prob = df[df["문제번호"] == selected].iloc[0]

    st.subheader(f"문제 {selected}")
    st.markdown(f"**문제:** {prob['문제']}")
    st.markdown(f"**정답:** {prob['정답']}")
    st.markdown(f"**내가 푼 답:** {prob['사용자답안']}")
    st.markdown(f"**풀이 과정:**\n{prob['풀이과정']}")

    feedback_key = f"ai_feedback_{selected}"
    if OPENAI_AVAILABLE:
        if st.button("🤖 AI 피드백 요청"):
            with st.spinner("AI 분석 중..."):
                prompt = f'''
[문제]
{prob["문제"]}

[정답]
{prob["정답"]}

[풀이]
{prob["풀이과정"]}

1. 사용자의 풀이에서 오류가 있다면 설명해줘.
2. 올바른 풀이 과정을 단계별로 제시해줘.
3. 오해한 개념이 있다면 짚어줘.
'''
                response = openai.ChatCompletion.create(
                    model="gpt-4",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.3
                )
                st.session_state[feedback_key] = response["choices"][0]["message"]["content"]
    else:
        st.warning("GPT 기능을 사용하려면 openai 모듈과 API 키가 필요합니다.")

    if feedback_key in st.session_state:
        st.markdown("### 🧠 AI 분석 결과")
        st.markdown(st.session_state[feedback_key])

    note_key = f"user_note_{selected}"
    note = st.text_area("✍️ 내가 정리한 깨달은 점", value=st.session_state.get(note_key, ""))
    if st.button("📝 메모 저장"):
        st.session_state[note_key] = note
        st.success("메모 저장 완료!")

    retry_key = f"retry_answer_{selected}"
    retry = st.text_area("🔁 다시 풀어보기", value=st.session_state.get(retry_key, ""))
    if st.button("✅ 다시 풀기 저장"):
        st.session_state[retry_key] = retry
        st.success("다시 푼 풀이 저장 완료!")

    st.markdown("---")
    st.header("3️⃣ 오답노트 저장")

    if st.button("📥 CSV 저장"):
        full_data = st.session_state.custom_problems
        for item in full_data:
            qid = item["문제번호"]
            item["AI 피드백"] = st.session_state.get(f"ai_feedback_{qid}", "")
            item["사용자 메모"] = st.session_state.get(f"user_note_{qid}", "")
            item["다시 풀기"] = st.session_state.get(f"retry_answer_{qid}", "")
        result_df = pd.DataFrame(full_data)
        csv = result_df.to_csv(index=False).encode("utf-8-sig")
        st.download_button("📄 오답노트 CSV 다운로드", data=csv, file_name="오답노트.csv", mime="text/csv")
