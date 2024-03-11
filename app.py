import streamlit as st
import pickle
from pathlib import Path
import streamlit_authenticator as stauth
import plotly.express as px
import pandas as pd
from st_aggrid import AgGrid, GridUpdateMode, ColumnsAutoSizeMode, JsCode, DataReturnMode
from streamlit_extras.metric_cards import style_metric_cards
from st_aggrid.grid_options_builder import GridOptionsBuilder
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


@st.cache_data
def load_dataframe():
    data = pd.read_csv("./data/data.csv")
    data = data.drop(columns=['mark.1', 'id'])
    data = data.drop_duplicates(['regnum', 'module'], keep='last')
    return data


def statistic_cards(data):
    decisions = data.decision.unique().tolist()
    cols = st.columns(len(decisions))

    for i, x in enumerate(cols):
        if decisions[i] == 'RETAKE' or decisions[i] == 'REPEAT' or decisions[i] == 'REPEAT LEVEL':
            x.metric(label=f"{decisions[i]}",
                     value=data[data['decision'] == decisions[i]].regnum.nunique(), delta=-data[data['decision'] == decisions[i]].regnum.nunique())
        else:
            x.metric(label=f"{decisions[i]}",
                     value=data[data['decision'] == decisions[i]].regnum.nunique(), delta=data[data['decision'] == decisions[i]].regnum.nunique())
    style_metric_cards()


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


def pass_rate_distribution(data):
    # number of students who passed

    pass_rate = data.groupby('module')['mark'].apply(
        lambda x: (x >= 50).mean() * 100)
    pass_rate = pass_rate.reset_index(
        name="pass_rate")
    fig_pass_rate = px.bar(
        pass_rate,
        x="module",
        y="pass_rate",
        title="<b> Pass Rates By Module <b>",
        color_discrete_sequence=["#0083B8"] * len(pass_rate),
        template="plotly_white"

    )
    st.plotly_chart(fig_pass_rate)


def bar_graph(data):

    grouped_data = data.groupby(by=["grade"])['regnum'].count()
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


def ag_grid(data):
    js = JsCode("""
                        function(e) {
                            var selectedRowData = e.api.getSelectedRows();
                            var selectedIds = selectedRowData.map(function(row) {
                                return row.id;
                            });

                            if (selectedRowData.length > 0 && e.data.regnum === selectedRowData[0]['regnum']) {
                                return {
                                    color: 'black',
                                    backgroundColor: 'pink'
                                };
                            }
                        }
                        """)

    gd = GridOptionsBuilder.from_dataframe(data)
    gd.configure_pagination(enabled=True)
    gd.configure_default_column(groupable=True)
    gd.configure_selection(selection_mode='single')
    gd.configure_grid_options(
        onRowSelected=js, pre_selected_rows=[])
    gridOptions = gd.build()

    response = AgGrid(data,
                      gridOptions=gridOptions,
                      enable_enterprise_modules=True,
                      # fit_columns_on_grid_load=True,
                      # theme = "streamlit",
                      update_mode=GridUpdateMode.SELECTION_CHANGED,
                      # update_mode=GridUpdateMode.MODEL_CHANGED,
                      data_return_mode=DataReturnMode.AS_INPUT,
                      reload_data=True,
                      allow_unsafe_jscode=True,
                      theme='balham',
                      )
    return response


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
    st.title(f"{faculty}({data[data['faculty']== faculty].regnum.nunique()})")
    statistic_cards(data[data['faculty'] == faculty])
    with st.expander(f'Faculty Decisions'):
        decisions = data[data['faculty'] == faculty].decision.unique().tolist()
        decision = st.selectbox(
            'Select Decision',
            decisions,
            index=0
        )
        response = ag_grid(data[(data['faculty'] == faculty) & (data['decision'] == decision)].drop_duplicates(
            subset='regnum')[['regnum', 'firstnames', 'surname']])
        if len(response['selected_rows']) > 0:
            regnum = response['selected_rows'][0]['regnum']
            if not st.session_state.get('regnum'):
                st.session_state['regnum'] = regnum
                url = f"https://academicbody.streamlit.app/student_info?regnum={regnum}"
                st.markdown(
                    f"[Open Student Info](javascript:window.open('{url}'))")
            else:
                if regnum != st.session_state.regnum:
                    st.session_state['regnum'] = regnum
                    url = f"https://academicbody.streamlit.app/student_info?regnum={regnum}"
                    st.markdown(
                        f"[Open Student Info](javascript:window.open('{url}'))")

        st.info(
            f"{data[(data['faculty'] == faculty) & (data['decision']== decision)].regnum.nunique()} Students")
    st.subheader(
        f"{programme}({data[data['programme']==programme].regnum.nunique()})")
    statistic_cards(data[data['programme'] == programme])

    # st.info(
    #    f"{data[data['programme'] == programme].regnum.nunique()} Students")

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
        if len(filtered_data):
            pie_chart(filtered_data)
        else:
            st.info("There is no data to display")

    # dialog = st.dialog("dialog_key_simplest_example")
    with col2:
        decisions = filtered_data.decision.unique().tolist()

        if len(decisions) > 0:
            st.markdown("#### Decisions")
            for decision in decisions:

                students = filtered_data[filtered_data['decision']
                                         == decision].regnum.nunique()
                with st.expander(f'{decision} ({students})'):
                    filtered_df = filtered_data[filtered_data['decision'] == decision]
                    result = ag_grid(filtered_df[['regnum', 'firstnames', 'surname']].drop_duplicates(
                        ['regnum'], keep='last'))
                    if len(result['selected_rows']) > 0:
                        regnum = result['selected_rows'][0]['regnum']
                        if not st.session_state.get('regnum'):
                            st.session_state['regnum'] = regnum
                            url = f"https://academicbody.streamlit.app/student_info?regnum={regnum}"
                            st.markdown(
                                f"[Open Student Info](javascript:window.open('{url}'))")
                        else:
                            if regnum != st.session_state.regnum:
                                st.session_state['regnum'] = regnum
                                url = f"https://academicbody.streamlit.app/student_info?regnum={regnum}"
                                st.markdown(
                                    f"[Open Student Info](javascript:window.open('{url}'))")
                        # response.clearSelectedRows()
        else:
            st.info("There are no decisions Available!!")


names = ['Westonmf', 'mukute', 'chaibva']
usernames = ['westonmufudza@gmail.com',
             'mukute@staff.msu.ac.zw', 'chaibvan@staff.msu.ac.zw']
file_path = Path(__file__).parent / 'hashed_pw.pkl'
with file_path.open('rb') as file:
    hashed_passwords = pickle.load(file)

credentials = {"usernames": {}}
for index in range(len(names)):
    credentials["usernames"][usernames[index]] = {
        "name": names[index],
        "password": hashed_passwords[index]
    }

authenticator = stauth.Authenticate(
    credentials, cookie_name="streamlit", key="abcdef", cookie_expiry_days=30)
name, authentication_status, username = authenticator.login("Login", "main")

if authentication_status == False:
    st.error("Invalid user credentials")
if authentication_status is None:
    st.warning("Please fill in the required fields")
if authentication_status:
    authenticator.logout("Logout", "sidebar")
    st.sidebar.markdown(f"<h3> Hi {username}", unsafe_allow_html=True)
    main()
