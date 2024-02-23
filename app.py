import streamlit as st
import plotly.express as px
import pandas as pd

st.set_page_config(layout="wide", page_icon=":bar_chat:",
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


def show_decision_table(data):
    st.dataframe(data)


@st.cache_data
def load_dataframe():
    data = pd.read_csv("./data/data.csv")
    # data = data.drop(columns=['Unnamed: 12', 'Unnamed: 13', 'ONGOING', '72'])
    return data


def pie_chart(data):
    distribution_by_decision = data.groupby(
        by="decision")['regnum'].nunique()
    distribution_by_decision = distribution_by_decision.reset_index(
        name="Students")
    plot1 = px.pie(
        distribution_by_decision,
        values='Students',
        names="decision",
        color_discrete_sequence=px.colors.sequential.RdBu_r,
        title=f"Student Distribution By Decision ({data.regnum.nunique()})"
    )
    st.plotly_chart(plot1, use_container_width=True)


def bar_graph(data):
    grouped_data = data.groupby(by=["grade"])['regnum'].nunique()
    grouped_data = grouped_data.reset_index(
        name="Students")
    fig_student_grades = px.bar(
        grouped_data,
        x="grade",
        y="Students",
        title="<b> Grade Distribution of Student Population <b>",
        color_discrete_sequence=["#0083B8"] * len(grouped_data),
        template="plotly_white"

    )

    st.plotly_chart(fig_student_grades)


def main():
    st.markdown(hide_streamlit_styles, unsafe_allow_html=True)

    st.sidebar.markdown(f"<h3>AGENDA</h3>", unsafe_allow_html=True)
    data = load_dataframe()

    faculties = data['faculty'].unique().tolist()
    default_ix = faculties[0]
    faculty = st.sidebar.selectbox(
        'Select Faculty',
        faculties,
        index=faculties.index(default_ix)
    )
    programmes = data[data['faculty'] == faculty].programme.unique().tolist()
    default_programme = programmes[0]
    programme = st.sidebar.selectbox(
        'Select Programme',
        programmes,
        index=programmes.index(default_programme)
    )
    st.title(f"Faculty of {faculty}")
    st.markdown(f"### {programme}")
    col1, col2, col3 = st.columns(3, gap="small")
    with col1:
        attendance_types = data[(data['programme'] == programme)
                                & (data['faculty'] == faculty)].attendancetype.unique().tolist()
        attendance_type = st.selectbox(
            'Select Attendance Type',
            attendance_types,
            index=0
        )
    with col2:
        academic_years = data[(data['programme'] == programme)
                              & (data['faculty'] == faculty) & (data['attendancetype'] == attendance_type)].academicyear.unique().tolist()
        academic_year = st.selectbox(
            'Select Academic Year',
            academic_years,
            index=0
        )

    with col3:
        sem = data[(data['programme'] == programme)
                   & (data['faculty'] == faculty) & (data['attendancetype'] == attendance_type)].semester.unique().tolist()
        semester = st.selectbox(
            'Select Semester',
            sem,
            index=0
        )

    st.markdown("---")
    filtered_data = data[(data['programme'] == programme)
                         & (data['faculty'] == faculty) & (data['attendancetype'] == attendance_type) & (data['academicyear'] == academic_year) & (data['semester'] == semester)]
    col1, col2 = st.columns([2, 3])
    with col1:
        pie_chart(filtered_data)
    with col2:
        bar_graph(filtered_data)
    st.markdown("#### Decisions")
    decisions = filtered_data.decision.unique().tolist()
    if len(decisions) > 0:
        for decision in decisions:
            students = filtered_data[filtered_data['decision']
                                     == decision].regnum.nunique()
            with st.expander(f'{decision} ({students})'):
                show_data = st.dataframe(
                    filtered_data[filtered_data['decision'] == decision])


if __name__ == "__main__":
    main()
