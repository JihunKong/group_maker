import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO
from openai import OpenAI

# OpenAI API 키 설정
client = OpenAI(api_key=st.secrets["api_keys"]["openai"])

def create_groups(df, group_size=4):
    # 성적을 기준으로 학생들을 정렬
    df_sorted = df.sort_values('성적', ascending=False)
    
    # 그룹 수 계산
    num_students = len(df)
    num_groups = num_students // group_size
    if num_students % group_size != 0:
        num_groups += 1
    
    # 그룹 생성
    groups = [[] for _ in range(num_groups)]
    for i, (_, student) in enumerate(df_sorted.iterrows()):
        group_index = i % num_groups
        groups[group_index].append(student)
    
    return groups

def format_groups(groups):
    formatted_groups = []
    for i, group in enumerate(groups, 1):
        group_df = pd.DataFrame(group)
        group_df = group_df.sort_values('성적', ascending=False)
        group_df['역할'] = ['모둠장'] + [''] * (len(group_df) - 1)
        group_df = group_df[['이름', '성적', '역할']]
        formatted_groups.append(f"모둠 {i}:\n{group_df.to_string(index=False)}\n")
    return "\n".join(formatted_groups)

def get_gpt_instruction(groups):
    prompt = f"""
다음은 학생들의 국어 모둠 편성 결과입니다. 이를 바탕으로 각 모둠별 특징과 조언을 제공해주세요.
편성 결과:
{format_groups(groups)}

다음 사항들을 고려해주세요:
1. 각 모둠의 평균 성적
2. 모둠 내 성적 격차
3. 모둠장(성적 최상위자)의 역할
4. 모둠 활동을 위한 조언

각 모둠에 대해 간략한 분석과 조언을 제공해주세요.
"""
    
    response =openai.Chat.Completion.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "당신은 교육 전문가이며 학생들의 모둠 활동을 돕는 조언자입니다."},
            {"role": "user", "content": prompt}
        ]
    )
    
    return response.choices[0].message.content

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
