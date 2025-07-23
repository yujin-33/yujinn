import streamlit as st
import pandas as pd

st.set_page_config(page_title="수학 오답노트", layout="wide")
st.title("📘 수학 오답노트 생성기 (GPT 없이)")

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
    st.header("2️⃣ 오답 확인 및 정리")

    selected = st.selectbox("분석할 문제 선택", df["문제번호"].tolist())
    prob = df[df["문제번호"] == selected].iloc[0]

    st.subheader(f"문제 {selected}")
    st.markdown(f"**문제:** {prob['문제']}")
    st.markdown(f"**정답:** {prob['정답']}")
    st.markdown(f"**내가 푼 답:** {prob['사용자답안']}")
    st.markdown(f"**풀이 과정:**\n{prob['풀이과정']}")

    # 오답 여부 판정
    if prob["정답"].strip() == prob["사용자답안"].strip():
        st.success("⭕ 정답입니다!")
    else:
        st.error("❌ 오답입니다.")
        st.info(f"정답은 **{prob['정답']}** 입니다.")

    # 오답 이유 직접 작성
    reason_key = f"wrong_reason_{selected}"
    wrong_reason = st.text_area("❗ 내가 왜 틀렸는지 정리해보기", value=st.session_state.get(reason_key, ""))
    if st.button("📌 오답 이유 저장"):
        st.session_state[reason_key] = wrong_reason
        st.success("오답 이유 저장 완료!")

    # 깨달은 점
    note_key = f"user_note_{selected}"
    note = st.text_area("✍️ 내가 정리한 깨달은 점", value=st.session_state.get(note_key, ""))
    if st.button("📝 메모 저장"):
        st.session_state[note_key] = note
        st.success("메모 저장 완료!")

    # 다시 풀기
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
            item["오답 이유"] = st.session_state.get(f"wrong_reason_{qid}", "")
            item["사용자 메모"] = st.session_state.get(f"user_note_{qid}", "")
            item["다시 풀기"] = st.session_state.get(f"retry_answer_{qid}", "")
        result_df = pd.DataFrame(full_data)
        csv = result_df.to_csv(index=False).encode("utf-8-sig")
        st.download_button("📄 오답노트 CSV 다운로드", data=csv, file_name="오답노트.csv", mime="text/csv")
