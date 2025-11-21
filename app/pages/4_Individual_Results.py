### Codigo desarrollado e implementado por Jose Manuel Naveiro Gomez
### josemanuel.naveiro@endef.com

import streamlit as st
import datetime as dt
import numpy as np

import base64

import logging

from datetime import datetime, timedelta

from pages.pages_content.page3 import desenlace, obtencion_info_usuarios

from pages.pages_content.page4 import obtencion_datos_usr, datos_matriz, preparacion_lista, obtencion_indices, grafico_prod_total,matrices_meses
from pages.pages_content.page4 import dataframes_datos, graficado_energia, graficado_coef, coeficientes_intervalo,grafico_genera_tot

meses = ["01-Jan", "02-Feb", "03-Mar", "04-Apr", "05-May", "06-Jun", "07-Jul", "08-Aug", "09-Sep", "10-Oct", "11-Nov", "12-Dec"]

tipologiaSB = {
    6: "Apartment for one adult, electric heating",
    7: "Apartment for one adult, gas heating",
    9: "Apartment for two adults, one or two children, electric heating and air conditioning",
    8: "Apartment for two adults, one or two children, gas heating and air conditioning",
    12:"Apartment for two adults, gas heating and AC",
    10:"Detached house for two adults, one or two children, gas heating and AC"
}

st.sidebar.markdown(
    """<a href="https://endef.com/">
    <img src="data:;base64,{}" width="200">
    </a>""".format(
        base64.b64encode(open("path1.png", "rb").read()).decode()
    ),
    unsafe_allow_html=True,
)

st.markdown("# Results")

with st.expander("Download the information"):
    st.write("This document can be downloaded in PDF format by clicking on the three dots in the upper right corner of the webpage. A menu will appear with the print option, which is where you will find the option to download it as a PDF.")
    st.write("You can also download charts and tables by hovering your mouse over the upper right corner of the chart or table. For tables, you'll see options to maximize the image and three dots; clicking these will display options, including saving the image as a PNG. Hovering over tables will reveal three options in the upper right corner. The first of these allows you to download the table data in CSV format.")

meses2 = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]

st.write("Zaragoza, "+meses2[dt.datetime.today().month-1]+" "+str(dt.datetime.today().day)+","+str(dt.datetime.today().year))
# st.write(dt.datetime.today().__format__('%d %b %Y, %I:%M%p'))

try:
    st.markdown("## Community: "+str(st.session_state.nComunidad))
    st.markdown("## Simulation for the Year: "+str(st.session_state.anyo))

    datosUsr = obtencion_info_usuarios()

    redListaU, diccioUsr, mDatos, diccColu = datos_matriz(datosUsr)

    eleccion = preparacion_lista(redListaU)

    consu = mDatos[diccioUsr[eleccion],:,diccColu["Consumo"]].copy()
    mconsutot  = matrices_meses(consu)
    gener = mDatos[diccioUsr[eleccion],:,diccColu["Reparto"]].copy()
    mgentot  = matrices_meses(gener)

    grafico_genera_tot(mgentot, mconsutot, meses)
    
    fecha_min = datetime(st.session_state.anyo, 1, 1, 0, 0)
    fecha_max = datetime(st.session_state.anyo+1, 1, 1, 0, 0) 
    
    st.markdown("### Analysis for a specific date range")

    # col1, col2 = st.columns(2)
    # with col1:
    #     start_time = st.date_input("Fecha inicio",value = fecha_min, min_value = fecha_min, max_value = fecha_max)
    # with col2:
    #     deltat = fecha_max-datetime(start_time.year, start_time.month, start_time.day, 0, 0)
    #     incremento = st.number_input("Intervalo días", value = 1, min_value = 1, max_value = deltat.days, step=1, format="%d")

    end_time = fecha_min + timedelta(360)

    df0, df1, df2, df3, df4 = dataframes_datos(fecha_min, end_time, eleccion, diccioUsr, mDatos,diccColu)
    
    # indices = obtencion_indices(fecha_min, end_time)
    indices = meses.copy()
    
    st.markdown("### Graph of Corresponding Generation, Surpluses and Self-Consumption")
    st.markdown("The graph below shows the generation allocated to the selected community user and how its use is distributed between Surplus and Self-Consumed energy. Surplus energy is the energy fed into the grid (not consumed by the community), and Self-Consumed energy is the energy the community has been able to utilize. The sum of Surplus and Self-Consumed energy is the Corresponding Generation.")
    graficado_energia(df0, df2, df3, df4, indices)
    
    st.markdown("### Distribution coefficients")
    st.markdown("The distribution coefficients are the factors by which production is multiplied to determine the distribution of the energy produced. The choice of these coefficients is a decision made by the energy community and must be accepted by its members.")
    st.markdown("This analysis shows the average monthly coefficients, which do not necessarily coincide with the average annual coefficient per hour, which is calculated in the general results tab.")
    graficado_coef(df1,indices)

    # st.markdown("## Coeficientes del intervalo")
    # cups = st.text_input("CUPS", value="", max_chars=22)
    # if cups != "" and len(cups)==22:
    #     coeficientes_intervalo(start_time, end_time,indices,df1, cups)

    desenlace(meses2)

except Exception as e:
    logging.debug("Problem displaying user info:", exc_info=True)
    st.markdown("# Run the simulation to get the results for your community")
