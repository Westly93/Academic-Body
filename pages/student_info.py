import streamlit as st
import plotly.express as px
import pandas as pd
from st_aggrid import AgGrid, GridUpdateMode
from st_aggrid.grid_options_builder import GridOptionsBuilder
from app import load_dataframe


def student_info():
    data = load_dataframe()
    regnum = data.regnum.iloc[0]
    if len(st.query_params.get_all('regnum')) > 0:
        regnum = st.query_params.get_all('regnum')[0]
    df = data[data['regnum'] == regnum].drop_duplicates(subset='module')
    st.title(
        f"{df.firstnames.iloc[0]} {df.surname.iloc[0]}")
    st.markdown("---")
    col1, col2 = st.columns(2, gap="small")
    with col1:
        st.markdown('#### Reg No')
    with col2:
        st.write(df.regnum.iloc[0])

    col1, col2 = st.columns(2, gap="small")
    with col1:
        st.markdown('#### Faculty')
    with col2:
        st.write(df.faculty.iloc[0])
    col1, col2 = st.columns(2, gap="small")
    with col1:
        st.markdown('#### Programme')
    with col2:
        st.write(df.programme.iloc[0])
    col1, col2 = st.columns(2, gap="small")
    with col1:
        st.markdown('#### Programme Status')
    with col2:
        st.write(df.programmestatus.iloc[0])
    col1, col2 = st.columns(2, gap="small")
    with col1:
        st.markdown('#### Attendance Type')
    with col2:
        st.write(df.attendancetype.iloc[0])
    col1, col2 = st.columns(2, gap="small")
    with col1:
        st.markdown('#### Academic Year')
    with col2:
        st.write(df.academicyear.iloc[0])
    col1, col2 = st.columns(2, gap="small")
    with col1:
        st.markdown('#### Semester')
    with col2:
        st.write(df.semester.iloc[0])
    col1, col2 = st.columns(2, gap="small")
    with col1:
        st.markdown('#### Program Type')
    with col2:
        st.write(df.programmetype.iloc[0])
    col1, col2 = st.columns(2, gap="small")
    with col1:
        st.markdown('#### Decision')
    with col2:
        st.write(df.decision.iloc[0])

    st.markdown('---')
    st.markdown(f'#### Modules({df.module.nunique()})')
    # st.dataframe(df)
    new_df = df.drop(columns=['regnum', 'decision', 'firstnames', 'surname', 'faculty',
                     'programme', 'academicyear', 'semester', 'programmetype', 'attendancetype'], axis=1)
    gd = GridOptionsBuilder.from_dataframe(new_df)
    gd.configure_pagination(enabled=True)
    gd.configure_default_column(groupable=True)
    gd.configure_selection(selection_mode='single')
    # gd.configure_grid_options(onRowSelected=js, pre_selected_rows=[])
    gridOptions = gd.build()

    # st.dataframe(new_df)
    response = AgGrid(new_df,
                      gridOptions=gridOptions,
                      enable_enterprise_modules=True,
                      # fit_columns_on_grid_load=True,
                      # theme = "streamlit",
                      width='100%',
                      height=300,
                      update_mode=GridUpdateMode.MODEL_CHANGED,
                      reload_data=True,
                      allow_unsafe_jscode=True,
                      theme='balham',
                      )


if __name__ == "__main__":
    student_info()
