### Codigo desarrollado e implementado por Jose Manuel Naveiro Gomez
### josemanuel.naveiro@endef.com

import streamlit as st
import datetime as dt

import base64

from pages.pages_content.page3 import introduccion, desarrollo, contenido_graficos, desenlace

st.sidebar.markdown(
    """<a href="https://endef.com/">
    <img src="data:;base64,{}" width="200">
    </a>""".format(
        base64.b64encode(open("path1.png", "rb").read()).decode()
    ),
    unsafe_allow_html=True,
)

st.markdown("# Community analysis")

with st.expander("Download the information"):
    st.write("This document can be downloaded in PDF format by clicking on the three dots in the upper right corner of the webpage. A menu will appear with the print option, which is where you will find the option to download it as a PDF.")
    st.write("You can also download the charts and tables by hovering your mouse over the upper right corner of the chart or table. For tables, you'll see options to maximize the image and three dots; clicking these will display options, including saving the image as a PNG. Hovering over tables will reveal three options in the upper right corner. The first of these allows you to download the table data in CSV format.")

meses = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]

st.write("Zaragoza, "+meses[dt.datetime.today().month-1]+" "+str(dt.datetime.today().day)+","+str(dt.datetime.today().year))

try:
    st.markdown("## Community "+str(st.session_state.nComunidad))

    introduccion()

    st.markdown("## Simulation for the year "+str(st.session_state.anyo))

    desarrollo()

    if st.session_state.idComunidad>0:
        contenido_graficos()
    else:
        st.markdown("# Run the simulation to get the results for your community")

    desenlace(meses)
except:
    st.markdown("# Run the simulation to get the results for your community")
