import streamlit as st
from streamlit_modal import Modal
import webbrowser
import plotly.express as px
import pandas as pd
from st_aggrid import AgGrid, GridUpdateMode, ColumnsAutoSizeMode, JsCode, DataReturnMode
from st_aggrid.grid_options_builder import GridOptionsBuilder
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


@st.cache_data
def load_dataframe():
    data = pd.read_csv("./data/data.csv")
    data = data.drop(columns=['mark.1', 'id'])
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
        if not filtered_data.empty:
            bar_graph(filtered_data)
    st.markdown("#### Decisions")
    # dialog = st.dialog("dialog_key_simplest_example")
    decisions = filtered_data.decision.unique().tolist()

    if len(decisions) > 0:
        for decision in decisions:

            students = filtered_data[filtered_data['decision']
                                     == decision].regnum.nunique()
            with st.expander(f'{decision} ({students})'):
                filtered_df = filtered_data[filtered_data['decision'] == decision].drop(
                    columns=['module', 'mark', 'grade', 'programmestatus', 'programmecode', 'surname', 'firstnames', 'programmetype'], axis=1)
                # Select specific columns and drop duplicates based on 'regnum' column
                selected_data = filtered_df.drop_duplicates(
                    subset='regnum')
                gd = GridOptionsBuilder.from_dataframe(selected_data)
                gd.configure_pagination(enabled=True)
                gd.configure_default_column(groupable=True)
                gd.configure_selection(selection_mode='single')
                # gd.configure_grid_options(onRowSelected=js, pre_selected_rows=[])
                gridOptions = gd.build()

                response = AgGrid(selected_data,
                                  gridOptions=gridOptions,
                                  enable_enterprise_modules=True,
                                  # fit_columns_on_grid_load=True,
                                  height=500,
                                  width='100%',
                                  # theme = "streamlit",
                                  update_mode=GridUpdateMode.MODEL_CHANGED,
                                  data_return_mode=DataReturnMode.AS_INPUT,
                                  reload_data=True,
                                  allow_unsafe_jscode=True,
                                  theme='balham',
                                  key=decision
                                  )
                if len(response['selected_rows']) > 0:
                    regnum = response['selected_rows'][0]['regnum']
                    webbrowser.open_new_tab(
                        f'http://localhost:8501/student_info?regnum={regnum}')


if __name__ == "__main__":
    main()
