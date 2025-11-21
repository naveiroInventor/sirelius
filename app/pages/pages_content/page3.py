### Codigo desarrollado e implementado por Jose Manuel Naveiro Gomez
### josemanuel.naveiro@endef.com

import streamlit as st
import datetime as dt

import base64

import numpy as np
import pandas as pd

from pages.coef_scripts.agente_Basico import Agente_MySql

meses = ["01-Ene", "02-Feb", "03-Mar", "04-Apr", "05-May", "06-Jun", "07-Jul", "08-Aug", "09-Sep", "10-Oct", "11-Nov", "12-Dec"]

diccioTipo = {  "Apartamento_1adulto_calef_electrica" : 6,
                "Apartamento_1adulto_calef_gas" : 7,
                "Piso_2adultos_1-2niños_calef_electrica_aire_ac" : 9,
                "Piso_2adultos_1-2niños_calef_gas_aire_ac" : 8,
                "Piso_2adultos_calef_gas_aire_ac" : 12,
                "Viv_unif_2adultos_1-2niños_calef_gas_aire_ac" : 10
            }

listaDiccioTipo = list(diccioTipo)

tipologiaSB0 = [
            "(1924.326 kWh/year) Apartment for one adult, electric heating",
            "( 745.992 kWh/year) Apartment for one adult, gas heating",
            "( 5931.25 kWh/year) Apartment for two adults, one or two children, electric heating and air conditioning",
            "(3059.416 kWh/year) Apartment for two adults, one or two children, gas heating and air conditioning",
            "(1916.711 kWh/year) Apartment for two adults, gas heating and AC",
            "(3889.858 kWh/year) Detached house for two adults, one or two children, gas heating and AC"
        ]

tipologiaSB = {
    6: "(1924.326 kWh/year) Apartment for one adult, electric heating",
    7: "( 745.992 kWh/year) Apartment for one adult, gas heating",
    9: "( 5931.25 kWh/year) Apartment for two adults, one or two children, electric heating and air conditioning",
    8: "(3059.416 kWh/year) Apartment for two adults, one or two children, gas heating and air conditioning",
    12:"(1916.711 kWh/year) Apartment for two adults, gas heating and AC",
    10:"(3889.858 kWh/year) Detached house for two adults, one or two children, gas heating and AC"
}


def introduccion():
    st.markdown("Energy communities are legal entities based on open and voluntary participation, autonomous and effectively controlled by partners or members who are located in the vicinity of renewable energy projects owned and developed by said legal entities, whose partners or members are natural persons, SMEs or local authorities, including municipalities and whose primary purpose is to provide environmental, economic or social benefits to their partners or members or to the local areas where they operate, rather than financial gains.")

def desarrollo():
    st.markdown("The results in this report are forecasts based on typical consumption patterns that may not reflect actual user consumption. It is an approximation intended as a guide to help inform community decisions.")

def desenlace(meses2):
    st.write("\n")
    st.write("\n")
    st.markdown("###### Responsibilities")
    st.markdown("###### This information is provided by Endef using open-source software developed to support energy communities. This app is a computer tool designed to run simulations for informational and educational purposes. While rigorous methodologies have been implemented to improve the accuracy of the results, Endef does not guarantee the accuracy or suitability of the generated data.")

    st.markdown("###### The user acknowledges and accepts that:")

    st.markdown("###### - Use at Your Own Risk: The user is solely responsible for the application of the results.")

    st.markdown("###### - Limitation of Liability: In no event shall Endef be liable for any direct, indirect, incidental, special or consequential damages, including, but not limited to, economic losses, business interruptions, damage to equipment or any other injury arising out of the use of or inability to use the software.")
    st.markdown("###### By using this app, the user accepts this disclaimer in its entirety.")
    
    col1,col2,col3 = st.columns(3)

    with col1:
        st.write("Zaragoza, "+meses2[dt.datetime.today().month-1]+" "+str(dt.datetime.today().day)+","+str(dt.datetime.today().year))
    
    with col3:
        st.write("\n")
        st.write("\n")
        st.write("\n")
        st.write("\n")
        st.markdown(
            """<a href="https://endef.com/">
            <img src="data:;base64,{}" width="200">
            </a>""".format(
                base64.b64encode(open("path1.png", "rb").read()).decode()
            ),
            unsafe_allow_html=True,
        )

def obtencion_info_usuarios():
    usuarios = st.session_state.contenidoComu.getUsuariosComunidad()

    datosUsr = []

    for i in usuarios:
        datosUsr.append((i.cupsUsuario,i))
        
    return datosUsr

def paso_matriz(datosUsr):
    redListaU = []

    # mdatos[nusuarios,nhoras,ncolumnasdatos]
    mDatos = np.zeros((len(datosUsr),len(datosUsr[0][1].consumos)*24,4))

    for i in range(len(datosUsr)):
        claveUsr = datosUsr[i][0]

        if claveUsr not in redListaU:
            redListaU.append(claveUsr)

        consum = datosUsr[i][1].consumos
        coefic = datosUsr[i][1].coeficientesReparto
        repart = datosUsr[i][1].energiaReparto
        excede = datosUsr[i][1].energiaReparto_excedentes

        fila = 0
        for j in range(len(consum)):
            for k in range(24):
                mDatos[i,fila,0] = float(consum[j][k].valorDatoConsumoHorario)
                mDatos[i,fila,1] = float(coefic[j][k])
                mDatos[i,fila,2] = float(repart[j][k])
                mDatos[i,fila,3] = float(excede[j][k])
                fila += 1

    return redListaU, mDatos

def preparacion_desplegable(redListaU):
    # Obtenemos los distintos usuarios de la informacion
    redLista = sorted(redListaU)
    redLista2 = []
    posiRedLista = []

    # Se obtienen los valores no repetidos de tipologias
    for j,i in enumerate(redLista):
        if int(i.split("-")[0]) not in redLista2:
            redLista2.append(int(i.split("-")[0]))
            posiRedLista.append(j)
    
    indicesUsr = [str(i)+"-"+str(tipologiaSB[int(j.split("-")[0])]) for i,j in enumerate(redListaU)]

    return indicesUsr

def texto_propio():
    st.markdown("### Total Annual Consumption Per User")
    texto = "The community of "+str(st.session_state.nComunidad)
    if st.session_state.informe["cantidadFV"] > 0.0:
        texto = texto + " It has an installed photovoltaic capacity of "+str(st.session_state.informe["cantidadFV"])+"kW"
    if st.session_state.informe["cantidadEO"] > 0.0:
        texto = texto + ", the installed wind power is "+str(st.session_state.informe["cantidadEO"])+"kW"
    if st.session_state.informe["cantidadBat"] > 0.0:
        texto = texto + " y "+str(st.session_state.informe["cantidadBat"])+"kWh of storage"
    texto += "."

    st.markdown(texto)
    
    st.markdown("The following bar chart shows the values ​​of consumption, corresponding generation and self-consumed energy, in total annual values, for each user in the community, in kWh, for the year specified in the simulation("+str(st.session_state.anyo)+").")

def grafico_tabla_consumos(indicesUsr,mConsumos,mReparto,mExcedentes):
    dfCon = pd.DataFrame(mConsumos,index=indicesUsr,columns=["2_Consumptions"])
    dfRep = pd.DataFrame(mReparto,index=indicesUsr,columns=["1_Corresponding Generations"])
    dfExc = pd.DataFrame(mExcedentes,index=indicesUsr,columns=["3_self-consumed"])
    dfF = dfRep.join(dfCon)
    dfF = dfF.join(dfExc)
    dfF2 = dfF.copy()
    dfF2.index = [i for i in range(len(mConsumos))]

    st.markdown("")
    st.markdown("*Figure 1. Values ​​of energy consumed, corresponding generation and self-consumed energy*")
    st.bar_chart(dfF2, horizontal = False, height = 500, width = 500, stack=False,color= [  "#FF9943","#4343FF","#28D06C"], x_label="Users", y_label="kWh")

    indice = st.column_config.TextColumn(label="Users",width="medium",required=True)
    consumos = st.column_config.NumberColumn(label="Consumption",width="small", format="%d kWh",required=True)
    autoconsumida = st.column_config.NumberColumn(label="Self-consumed",width="small", format="%d kWh",required=True)
    generacion = st.column_config.NumberColumn(label="Generation",width="small", format="%d kWh",required=True)

    st.markdown("In tabular form, the total annual values ​​would be as follows:")
    st.data_editor( 
                    dfF,
                    height = 43 * len(mConsumos),
                    width= 800,
                    hide_index=False,
                    column_config={
                        "_index": indice,
                        "1_Corresponding Generation":generacion,
                        "2_Consumption":consumos,
                        "3_Self-consumed":autoconsumida,
                    },
                )
    st.markdown("*Table 1. Consumption values, corresponding generation and self-consumption*")

def texto_coef():
    st.markdown("### Distribution coefficients")
    st.markdown("The distribution coefficients are the factors by which production is multiplied to determine the distribution of the energy produced. The choice of these coefficients is a decision made by the energy community and must be accepted by its members.")
    st.markdown("This simulation proposes possible distribution coefficients based on the consumption of the community's users, distributing the energy produced proportionally to this consumption. This calculation aims to minimize the surplus fed into the grid, thus maximizing the efficiency of production.")
    st.markdown("The maximum coefficient selected for the simulation is **"+str(st.session_state.datoscomunidad["max_participation"])+"%**. This represents the maximum value that the distribution coefficient can take in the simulation for a single user. This restriction can be applied in cases where a user has a significantly higher consumption, preventing them from monopolizing all the production.")
    st.markdown("The minimum coefficient selected for the simulation is **"+str(st.session_state.datoscomunidad["min_participation"])+"%**. This represents the minimum value that the distribution coefficient can take in the simulation for a single user. This restriction can be imposed to prevent a user from having very little share due to low consumption.")
    st.markdown("The percentage dedicated to energy poverty is **"+str(st.session_state.datoscomunidad["energy_poverty"])+"%** which is the percentage of energy that will be dedicated to the selected cases.")

def grafico_genera_tot(mgentot, mconsutot, indicesgen):
    st.write("The following graph shows the total consumption of users and photovoltaic generation for the generating plants included in the community.")

    dfGen = pd.DataFrame(mgentot,index=indicesgen,columns=["Generation"])
    dfCon = pd.DataFrame(mconsutot,index=indicesgen,columns=["Consumption"])
    dfCoef = dfCon.join(dfGen)

    indice = st.column_config.TextColumn(label="Month",width="small",required=True)
    consumo = st.column_config.NumberColumn(label="Consumption",width="medium", format="%d kWh",required=True)
    generacion = st.column_config.NumberColumn(label="Generation",width="medium", format="%d kWh",required=True)

    st.markdown("*Chart 0. Consumption and generation by month of the power plant*")
    st.bar_chart(dfCoef, horizontal = False, stack=False, height = 500, width = 500,color = [ "#4343FF", "#FF9943"], x_label="Months", y_label="kWh",)

    st.markdown("In tabular form, the generation values ​​and the total monthly consumption of the community would be as indicated below:")

    st.data_editor(
                    dfCoef,
                    column_config={
                        "_index": indice,
                        "Consumption": consumo,
                        "Generation": generacion,
                    },
                    hide_index=False,
                    height = 43 * len(indicesgen),
                )
    st.markdown("*Table 0. Consumption and generation values ​​by month*")

def grafico_tabla_coef(mCoef,indicesUsr):
    dfCoef = pd.DataFrame(mCoef,index=indicesUsr,columns=["%"])
        
    dfCoef2 = dfCoef.copy()
    dfCoef2.index = [i for i in range(len(indicesUsr))]
    st.markdown("*Chart 2. Average annual values ​​of distribution coefficients per user*")
    st.bar_chart(dfCoef2, horizontal = False, height = 500, width = 500,color = "#4343FF", x_label="Usuario", y_label="%",)

    st.markdown("In tabular form, the average annual values ​​would be as follows:")

    indice = st.column_config.TextColumn(label="Users",width="medium",required=True)
    porcentaje = st.column_config.NumberColumn(label="Coefficient [%]",width="medium", format="%.4f",required=True)

    st.data_editor(
                    dfCoef,
                    column_config={
                        "_index":indice,
                        "%": porcentaje,
                    },
                    hide_index=False,
                    height = 43 * len(indicesUsr),
                )
    st.markdown("*Table 2. Average annual values ​​of distribution coefficients per user.*")

def contenido_graficos():

    # Obtencion de la informacion de los usuarios
    datosUsr = obtencion_info_usuarios()

    # Paso de la informacion  de los usuarios a una matriz de 3 dimensiones
    redListaU, mDatos = paso_matriz(datosUsr)
    
    # mDatos[nhoras,nusuarios,(consumos,coeficientes,reparto energetico,excedentes)]
    mConsumos = [mDatos[i,:,0].sum(0) for i in range(len(datosUsr))]
    mCoef = [mDatos[i,:,1].mean(0) for i in range(len(datosUsr))]
    mReparto = [mDatos[i,:,2].sum(0) for i in range(len(datosUsr))]
    # mExcedentes = [mDatos[i,:,3].sum(0) for i in range(len(datosUsr))]
    mAutocons = [(mDatos[i,:,2].sum(0) - mDatos[i,:,3].sum(0)) for i in range(len(datosUsr))]

    mConsumo12T = np.sum(mDatos[:,:,0].copy(),axis = 0)
    mReparto12T = np.sum(mDatos[:,:,2].copy(),axis = 0)
    repartotot = np.zeros(12)
    consutotot = np.zeros(12)
    for i in range(1,13):
        fechacero = dt.datetime(st.session_state.anyo,1,1,0,0)
        horaini = 24 * (dt.datetime(st.session_state.anyo + (i)//13,((i)%13) + ((i)//13),1,0,0)-fechacero).days
        horafin = 24 * (dt.datetime(st.session_state.anyo + (i+1)//13,((i+1)%13) + ((i+1)//13),1,0,0)-fechacero).days
        repartotot[i-1] = np.sum(mReparto12T[horaini:horafin])
        consutotot[i-1] = np.sum(mConsumo12T[horaini:horafin])

    # se prepara la lista de usuarios para el desplegable
    indicesUsr = preparacion_desplegable(redListaU)
    st.sidebar.write("")

    # Intentamos esta parte porque no sabemos si existen aun todas las variables
    try:
        # Grafico de la generación anual Total
        grafico_genera_tot(repartotot, consutotot, meses)

        # Texto personalizado para la comunidad de la simulacion
        texto_propio()

        # Contenido con graficos con los consumos, reparto y excedentes
        grafico_tabla_consumos(indicesUsr,mConsumos,mReparto,mAutocons)
        
        # Texto coeficientes de reparto
        texto_coef()

        # Grafico de los coeficientes de reparto
        grafico_tabla_coef(mCoef,indicesUsr)
        
    except:
        st.markdown("# Run the simulation to see the results.")
