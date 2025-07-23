import streamlit as st
import pandas as pd

st.set_page_config(page_title="수학 채점기", layout="wide")
st.title("🧮 수학 채점기")

# 세션 초기화
if "custom_problems" not in st.session_state:
    st.session_state.custom_problems = []

if "final_answers" not in st.session_state:
    st.session_state.final_answers = {}

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
        submit = st.form_submit_button("문제 추가")
        if submit:
            st.session_state.custom_problems.append({
                "문제번호": qnum,
                "문제": qtext,
                "정답": correct,
                "사용자답안": user_ans
            })
            st.success(f"{qnum}번 문제 추가됨!")

if st.session_state.custom_problems:
    df = pd.DataFrame(st.session_state.custom_problems)
    st.markdown("### ✅ 입력한 문제 목록")
    st.dataframe(df)

    st.markdown("---")
    st.header("2️⃣ 채점 및 고쳐보기")

    selected = st.selectbox("채점할 문제 선택", df["문제번호"].tolist())
    prob = df[df["문제번호"] == selected].iloc[0]

    st.subheader(f"문제 {selected}")
    st.markdown(f"**문제:** {prob['문제']}")
    st.markdown(f"**정답:** {prob['정답']}")
    st.markdown(f"**내가 푼 답:** {prob['사용자답안']}")

    # 1차 채점
    if prob["정답"].strip() == prob["사용자답안"].strip():
        st.success("⭕ 정답입니다!")
        st.session_state.final_answers[selected] = {
            "문제": prob['문제'],
            "정답": prob['정답'],
            "최종답안": prob['사용자답안'],
            "성찰": "",
            "틀린이유": ""
        }
    else:
        st.error("❌ 오답입니다.")
        st.info(f"정답은 **{prob['정답']}** 입니다.")

        # 고쳐보기 입력
        fix_key = f"fix_answer_{selected}"
        fix = st.text_input("🔁 고쳐보기 (다시 풀어보세요)", value=st.session_state.get(fix_key, ""))
        if st.button("✅ 고쳐 쓴 답 채점"):
            st.session_state[fix_key] = fix
            if fix.strip() == prob["정답"].strip():
                st.success("⭕ 정답입니다! 다시 풀기에 성공했어요.")
                reason_key = f"reason_{selected}"
                reflection_key = f"reflection_{selected}"
                reason = st.text_area("📌 왜 틀렸는지 적어보세요", value=st.session_state.get(reason_key, ""))
                reflection = st.text_area("🧠 이번 문제에서 깨달은 점은?", value=st.session_state.get(reflection_key, ""))
                if st.button("📝 성찰 저장"):
                    st.session_state[reason_key] = reason
                    st.session_state[reflection_key] = reflection
                    st.session_state.final_answers[selected] = {
                        "문제": prob['문제'],
                        "정답": prob['정답'],
                        "최종답안": fix,
                        "틀린이유": reason,
                        "성찰": reflection
                    }
                    st.success("성찰과 정답이 저장되었습니다!")
            else:
                st.error("❌ 여전히 오답입니다. 다시 한 번 생각해보세요!")

    st.markdown("---")
    st.header("3️⃣ 최종 저장된 결과 보기")

    if st.session_state.final_answers:
        final_df = pd.DataFrame.from_dict(st.session_state.final_answers, orient="index")
        st.dataframe(final_df)
    else:
        st.info("아직 최종적으로 정답 처리된 문제가 없습니다.")
