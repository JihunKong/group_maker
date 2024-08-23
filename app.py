import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO
from openai import OpenAI

# OpenAI API 키 설정
try:
    openai_api_key = st.secrets["openai"]["api_key"]
except KeyError:
    st.error("OpenAI API 키가 올바르게 설정되지 않았습니다. Streamlit의 secrets에서 [openai] 섹션 아래에 api_key를 설정해주세요.")
    st.stop()

client = OpenAI(api_key=openai_api_key)

# 여기서부터 나머지 함수들 (create_groups, format_groups, get_gpt_instruction)은 이전과 동일...

def main():
    st.title("국어 모둠 편성 도우미")
    
    uploaded_file = st.file_uploader("엑셀 파일을 업로드하세요", type="xlsx")
    
    if uploaded_file is not None:
        df = pd.read_excel(uploaded_file)
        df.columns = ['이름', '성적']
        
        st.write("업로드된 데이터:")
        st.write(df)
        
        if st.button("모둠 편성하기"):
            groups = create_groups(df)
            
            st.write("모둠 편성 결과:")
            for i, group in enumerate(groups, 1):
                st.write(f"모둠 {i}:")
                group_df = pd.DataFrame(group)
                group_df = group_df.sort_values('성적', ascending=False)
                group_df['역할'] = ['모둠장'] + [''] * (len(group_df) - 1)
                st.write(group_df[['이름', '성적', '역할']])
            
            gpt_analysis = get_gpt_instruction(groups)
            st.write("GPT 분석 및 조언:")
            st.write(gpt_analysis)
            
            # 엑셀 파일로 저장
            output = BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                for i, group in enumerate(groups, 1):
                    group_df = pd.DataFrame(group)
                    group_df = group_df.sort_values('성적', ascending=False)
                    group_df['역할'] = ['모둠장'] + [''] * (len(group_df) - 1)
                    group_df[['이름', '성적', '역할']].to_excel(writer, sheet_name=f'모둠 {i}', index=False)
            
            output.seek(0)
            st.download_button(
                label="엑셀 파일 다운로드",
                data=output,
                file_name="모둠_편성_결과.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

if __name__ == "__main__":
    main()
