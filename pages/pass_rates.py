import streamlit as st
import plotly.express as px
import pandas as pd
from app import load_dataframe
st.set_page_config(layout="wide", initial_sidebar_state="collapsed", page_icon=":bar_chat:",
                   page_title="Academic Body")
hide_streamlit_styles = """
<style>
#MainMenu{
    visibility: hidden;
}
footer{
    visibility: hidden;
}
header{
    visibility: hidden;
}
</style>
"""


def programme_pass_rate(df):
    faculties = df.faculty.unique().tolist()
    faculty = st.selectbox(
        'Select Faculty',
        faculties,
        index=0
    )
    programme_pass_rate = df[df['faculty'] == faculty].groupby(
        'programmecode')['mark'].apply(lambda x: (x >= 50).mean() * 100)
    programme_pass_rate = programme_pass_rate.reset_index(
        name="pass_rate")
    fig_programme_pass_rate = px.bar(
        programme_pass_rate[:20],
        x="programmecode",
        y="pass_rate",
        title=f"<b> Pass Rates by Programme ({faculty})<b>",
        color_discrete_sequence=["#0083B8"] * len(programme_pass_rate),
        template="plotly_white"

    )
    st.plotly_chart(fig_programme_pass_rate)


def faculty_pass_rate(df):
    faculty_pass_rate = df.groupby('faculty')['mark'].apply(
        lambda x: (x >= 50).mean() * 100)
    faculty_pass_rate = faculty_pass_rate.reset_index(
        name="pass_rate")
    fig_faculty_pass_rate = px.bar(
        faculty_pass_rate,
        x="faculty",
        y="pass_rate",
        title=f"<b> Pass Rates by Faculty<b>",
        color_discrete_sequence=["#0083B8"] * len(faculty_pass_rate),
        template="plotly_white"
    )
    st.plotly_chart(fig_faculty_pass_rate)


def pass_rates():
    data = load_dataframe()
    st.markdown(hide_streamlit_styles, unsafe_allow_html=True)
    st.markdown(f"<h3>PASS RATES</h3>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3, gap="small")
    with col1:
        attendance_types = data.attendancetype.unique().tolist()
        attendance_type = st.selectbox(
            'Select Attendance Type',
            attendance_types,
            index=0
        )
    with col2:
        academic_years = data[(data['attendancetype'] ==
                               attendance_type)].academicyear.unique().tolist()
        academic_year = st.selectbox(
            'Select Academic Year',
            academic_years,
            index=0
        )

    with col3:
        sem = data[(data['attendancetype'] == attendance_type)
                   ].semester.unique().tolist()
        semester = st.selectbox(
            'Select Semester',
            sem,
            index=0
        )

    st.markdown("---")
    selected_data = data[(data['attendancetype'] == attendance_type) & (
        data['academicyear'] == academic_year) & (data['semester'] == semester)]
    programme_pass_rate(selected_data)
    st.markdown("---")
    faculty_pass_rate(selected_data)


if __name__ == "__main__":
    pass_rates()
