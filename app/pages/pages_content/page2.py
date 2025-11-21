### Codigo desarrollado e implementado por Jose Manuel Naveiro Gomez
### josemanuel.naveiro@endef.com

import streamlit as st
from pages.scripts.envios import envioDatos
from pages.scripts.funcionesgrles import comprobarStrings, camposDataframe, borrar

import datetime as dt
import numpy as np
import pandas as pd
import logging

def creacion_CE(geolocator,ce):
    st.info("Clarification note: Community Name and Location are required. Do not use punctuation marks.")
    st.header("Community")
    st.markdown("### General Data")
    nombreCE = st.text_input("Community name *",help="Enter the name of the community.")
    ubicacion = st.text_input("Location *",help="Enter the name of the city or town. For example: Zaragoza.")
    coste = 100000.00
    amortizacion = 1000.00
    dfComu = pd.DataFrame([])

    deshabilitadoCE = True
    gralComu = None
    if nombreCE=="":
        st.write("The name is missing.")
    elif comprobarStrings(nombreCE):
        st.warning("Invalid name. Remove punctuation marks.")
    elif comprobarStrings(ubicacion):
        st.warning("Invalid location. Remove punctuation marks.")
    elif ubicacion == "":
        st.write("Location is missing")
    else:
        deshabilitadoCE = False
        gralComu = (nombreCE,ubicacion,coste,amortizacion)

    comunidadEnerg = {}
    colums = ("Name","Location","Cost","Amortization")
    if st.button("Create community",type="primary", disabled = deshabilitadoCE):
        try:
            if gralComu != None:
                dfComu = camposDataframe("comunidades",gralComu,colums)
                conceptos = ["name", "location", "inst_cost", "inst_monthly_fee"]
                for i,j in zip(conceptos,gralComu):
                    comunidadEnerg[i] = j
                comunidadEnerg["id_administrator"] = 1
                ce = True
        
            st.info("Data completed")
            st.session_state.nComunidad = nombreCE
            st.session_state.saltoSimu = False
            st.success('You can now go to the Data page and fill in the installation details.', icon="✅")
            try:
                st.session_state.localizador = geolocator.geocode(ubicacion)
            except:
                logging.debug("It was not possible to include the location in the creation of the EC.")
        except Exception as e:
            logging.error("The community could not be included: ", exc_info=True)    
    
    return comunidadEnerg, dfComu, ce

def instalacion_fv(ce,fv):
    st.info("Clarification note: If there is wind power but no PV, you can proceed to defining wind power generation.")
    tipologiasFV = {
        "Monocristalino":1,
        "Policristalino":2
    }
    location = st.session_state.localizador
    st.header("PV Generators")
    st.markdown("### PV Generator Incorporation Form")
    descFV = st.text_input("Description of PV generators", value = "FV1",help="Include a brief description to differentiate it from other generators, as you can run the simulation with more than one photovoltaic plant. Do not use punctuation.", disabled= not ce)
 
    latiFV = st.number_input("Latitude", help = "You can get the Google Maps coordinates by right-clicking on the location of the panels.", disabled= not ce, value = location.latitude, max_value=90.0, min_value=-90.0,format="%2.6f")
    longFV = st.number_input("Longitude", help = "You can get the Google Maps coordinates by right-clicking on the location of the panels.", disabled= not ce, value = location.longitude, max_value=180.0, min_value=-180.0, format="%2.6f")
    
    df = pd.DataFrame(
        {
            "col1": np.array([latiFV]),
            "col2": np.array([longFV]),
        }
    )

    st.map(df, latitude="col1", longitude="col2")
    nModulos = 10
    pPicoFV = st.number_input("Total peak PV power [kW]",help="Set the peak power of the entire photovoltaic plant located at the coordinates indicated.",min_value=0.0, disabled= not ce)
    tipoMod = "Monocristalino"
    azimuth = st.number_input("Azimuth in degrees[-90 E, 0 S, 90 O, 180 N]", disabled= not ce,min_value=-90,max_value=180,value=0,step=1)
    inclinacion = st.number_input("Tilt in degrees[0 horizontal, 90 vertical]", disabled= not ce,min_value=0,max_value=90,value=30,step=1)

    deshabilitadoFV = True

    if descFV=="":
        st.warning("Description is missing")
    elif pPicoFV == 0.0:
        st.warning("Peak power is missing")
    elif comprobarStrings(descFV):
        st.warning("Invalid description. Remove punctuation marks.")
    else:
        deshabilitadoFV = False
        st.info("You can now add the photovoltaic plant. Make sure the data is correct before moving to the next field.")

    AddGenFv = st.button("Add Photovoltaics",type="primary", disabled= (not ce or deshabilitadoFV))

    aux = (descFV,latiFV,longFV,nModulos,pPicoFV,tipologiasFV[tipoMod],int(azimuth),int(inclinacion))
    colums = ("Description", "latitude", "longitude", "quantity", "Total Wp", "Type", "azimuth", "tilt")
    
    dfFV = camposDataframe("fotovolt",aux,colums,AddGenFv)

    if len(st.session_state["fotovolt"]) == 0:
        st.write("There is no PV generating plant")
    else:
        fv = True
        st.success("There is at least one PV generating plant in the community. Please ensure the information is correct before proceeding to the next field. Once verified, you can move on to the next tab: Wind.")

    numeroFV = 0.0
    infoFV = st.session_state["fotovolt"]
    for i in infoFV:
        numeroFV += i[4]
    st.write("Total installed PV capacity: ",numeroFV)
    st.dataframe(dfFV)

    if st.button("Delete PV plant"):
        borrar("fotovolt",aux)
        st.rerun()
    
    return dfFV, numeroFV, fv

def instalacion_eo(ce,eo):
    location = st.session_state.localizador
    st.info("Clarification note: If there is PV and no wind power, you can skip to the next tab")
    st.header("Wind turbines")
    st.markdown("### Wind Turbine Application Form")
    descEo = st.text_input("Description of wind turbines", value = "EO1",help="Include a brief description to differentiate it from other generators, as you can run the simulation with more than one wind turbine. Do not use punctuation.", disabled= not ce)
    latiEo = st.number_input("Latitude wind turbine", help = "You can get the Google Maps coordinates by right-clicking on the location of the wind turbines.", disabled= not ce,value = location.latitude,max_value=90.0,min_value=-90.0,format="%2.6f")
    longEo = st.number_input("Longitude wind turbine", help = "You can get the Google Maps coordinates by right-clicking on the location of the wind turbines.", disabled= not ce,value = location.longitude,max_value=180.0,min_value=-180.0,format="%2.6f")
    df = pd.DataFrame(
        {
            "col1": np.array([latiEo]),
            "col2": np.array([longEo]),
        }
    )

    st.map(df, latitude="col1", longitude="col2")
    pPicoEo = st.number_input("Peak wind power [kW]",help="Peak power of the wind turbine.", disabled= not ce, min_value= 0.0)

    deshabilitadoEO = True

    if descEo=="":
        st.warning("Description is missing")
    elif comprobarStrings(descEo):
        st.warning("Invalid description. Remove punctuation marks.")
    elif pPicoEo == 0.0:
        st.warning("Peak power is missing")
    else:
        deshabilitadoEO = False
        st.info("You can now add the wind turbine. Make sure the information is correct before moving to the next field.")

    AddGenEo = st.button("Add Wind Power",type="primary", disabled= (not ce or deshabilitadoEO))

    aux = (descEo,latiEo,longEo,pPicoEo)
    colums = ("Description", "latitude", "longitude", "Wp")

    dfEO = camposDataframe("eolicos",aux,colums,AddGenEo)

    if len(st.session_state["eolicos"]) == 0:
        st.write("There is no wind power plant")
    else:
        eo = True
        st.success("There is at least one wind turbine in the community. Please ensure the information is correct before proceeding to the next field. Once verified, you can move on to the next tab: Batteries.")

    numeroEO = 0.0
    infoEo = st.session_state["eolicos"]
    for i in infoEo:
        numeroEO += i[3]
    st.write("Total installed wind power:",numeroEO)
    st.dataframe(dfEO)

    if st.button("Delete wind turbines"):
        borrar("eolicos",aux)
        st.rerun()
    
    return dfEO, numeroEO, eo

def instalacion_bat(ce, fv, eo, gen):
    st.info("If there are no batteries, you can skip to the user section.")
    if fv or eo:
        gen = True
    tipologiasBat = {
        "Litio":1,
        "Otras":2
    }
    st.header("Batteries")
    st.markdown("### Battery Description")
    descBat = st.text_input("Battery Description", value = "BAT1", help="Include a brief description to differentiate the batteries you want to use, as you can run the simulation with more than one battery. Do not use punctuation.",disabled= not (gen and ce))
    tipoBat = "Litio"
    st.markdown("### Technical specifications")

    voltajeBat =   220
    capacidadBat = st.number_input("Battery capacity [kWh]", help = "Nominal battery capacity in kWh" , value = 0.0, disabled= not (gen and ce), min_value=0.0)
    cargaMaxBat =  capacidadBat
    cargaMinBat =  0.1*capacidadBat
    arranquedBat = st.number_input("Power [kW]", help = "Battery power is obtained by multiplying the nominal voltage and the nominal current. If you are unsure of these values, use half the capacity." ,disabled= not (gen and ce), value = capacidadBat/2.,min_value = 0.0)
    descMaxBat =  arranquedBat*1.0

    deshabilitadoBat = True

    if descBat=="":
        st.warning("Description is missing")
    elif comprobarStrings(descBat):
        st.warning("Invalid description. Remove punctuation marks.")
    elif tipoBat == "":
        st.warning("The battery type is missing.")
    elif capacidadBat == 0.0:
        st.warning("The battery capacity is missing.")
    elif arranquedBat == 0.0:
        st.write("Power is missing")
    else:
        deshabilitadoBat = False
        st.info("You can now add the energy storage. Make sure the information is correct before moving to the next field.")

    AddAlmBat = st.button("Add Energy Storage",type="primary", disabled= (not ce or (not gen or deshabilitadoBat)))

    aux = (descBat,tipologiasBat[tipoBat],voltajeBat,capacidadBat,cargaMaxBat,cargaMinBat,arranquedBat,descMaxBat)
    colums = ("Description", "Type", "Voltage", "Capacity", "Maximum Load", "Minimum Load", "Power", "Maximum Discharge")

    dfBat = camposDataframe("baterias",aux,colums,AddAlmBat)

    if len(st.session_state["baterias"]) == 0:
        st.write("No Energy Storage")
    else:
        bt = True
        st.success("There is energy storage available in the community. Please ensure the information is correct. Once reviewed, you can proceed to the next tab: Users.")
    numeroBat = 0.0
    infBat = st.session_state["baterias"]
    for i in infBat:
        numeroBat += float(i[3])
    st.write("Total installed storage: ",numeroBat)
    st.dataframe(dfBat)

    if st.button("Delete Storage"):
        borrar("baterias",aux)
        st.rerun()

    return dfBat, numeroBat

def registro_usuarios(ce, gen, usr):
    st.info("Clarification note: Once all users are present, you can proceed to the next part of the data upload.")
    tipologias = [
        "Apartamento_1adulto_calef_electrica",
        "Apartamento_1adulto_calef_gas",
        "Piso_2adultos_1-2niños_calef_electrica_aire_ac",
        "Piso_2adultos_1-2niños_calef_gas_aire_ac",
        "Piso_2adultos_calef_gas_aire_ac",
        "Viv_unif_2adultos_1-2niños_calef_gas_aire_ac"]
    
    tipologiaSB = [
        "(1924.326 kWh/year)Apartment for one adult, electric heating",
        "(745.992 kWh/year)Apartment for one adult, gas heating",
        "(5931.25 kWh/year)Apartment for two adults, one or two children, electric heating and air conditioning",
        "(3059.416 kWh/year)Apartment for two adults, one or two children, gas heating and air conditioning",
        "(1916.711 kWh/year)Apartment for two adults, gas heating and AC",
        "(3889.858 kWh/year)Detached house for two adults, one or two children, gas heating and AC"
    ]

    st.header("Users")
    tipoUser = st.selectbox("User typology",tipologiaSB, help="Select a housing typology for the types of community members." , disabled= not (gen and ce))
    cantUser = st.number_input("Number of users with this typology", help="Indicate how many users there are with the selected type.",disabled= not (gen and ce), min_value=1,step=1)

    AddUser = st.button("Add Users",type="primary", disabled= not (gen and ce))

    aux = [tipologias[tipologiaSB.index(tipoUser)],cantUser]

    dfUs = camposDataframe("usuarios",aux,("User type","quantity"),AddUser)

    if len(st.session_state["usuarios"]) == 0:
        st.warning("No users")
    else:
        usr = True
        st.success("There are users in the community. Make sure all users are included and that the data is correct before moving to the next tab: Coefficients.")

    numeroUsers = 0
    infoUsers = st.session_state["usuarios"]
    for i in infoUsers:
        numeroUsers += i[1]
    st.write("Total Users: ",numeroUsers)
    st.dataframe(dfUs)

    if st.button("Delete Users"):
        borrar("usuarios",aux)
        st.rerun()

    return dfUs, numeroUsers, usr

def registro_coeficientes(numeroUsers,comunidadEnerg):
    st.info("Clarification note: You can leave the distribution coefficients as they are or modify the maximum, minimum, and energy poverty values ​​to calculate the distribution of the energy produced. If everything is correct, you can proceed to the next tab: Confirmation.")
    st.header("Distribution coefficients")
    
    with st.expander("Explanation"):
        st.write("The distribution coefficients are the factors by which production is multiplied to determine how the energy produced is distributed. The energy community decides on these coefficients and must accept them. This simulation proposes possible distribution coefficients to minimize the surplus fed into the grid and maximize the return on production.")

    pobrezaE = st.number_input("Percentage for energy poverty",min_value=0.0, max_value=100.0,step=1.0,help = "The percentage dedicated to energy poverty is the percentage of energy that will be reserved for cases selected by the community.")
    try:
        valorAux = (100.0-pobrezaE)/numeroUsers
    except ZeroDivisionError:
        valorAux = 50.0
    coefMax = st.number_input("Maximum coefficient", min_value = valorAux, max_value = 100.0,value=100.0,step=1.0,help="The maximum coefficient is the highest value the distribution coefficient can take in the simulation for a single user. This restriction can be applied in cases where a user's consumption is significantly higher, preventing them from monopolizing all the production.")
    coefmin = st.number_input("Minimum coefficient", min_value = 0.0, max_value = valorAux,value=0.0,step=1.0,help="The minimum coefficient is the smallest value the distribution coefficient can take in the simulation for a single user. This restriction can be imposed to prevent a user from having very little share due to low consumption.")

    comunidadEnerg["max_participation"]=coefMax
    comunidadEnerg["min_participation"]=coefmin
    comunidadEnerg["energy_poverty"]=pobrezaE

def confirmacion(datos):
    comunidadEnerg, dfComu, ce, dfFV, numeroFV, dfEO, numeroEO, dfBat, numeroBat, gen, dfUs, numeroUsers, usr = datos
    diccioTipo = {  "Apartamento_1adulto_calef_electrica" : 6,
                    "Apartamento_1adulto_calef_gas" : 7,
                    "Piso_2adultos_1-2niños_calef_electrica_aire_ac" : 9,
                    "Piso_2adultos_1-2niños_calef_gas_aire_ac" : 8,
                    "Piso_2adultos_calef_gas_aire_ac" : 12,
                    "Viv_unif_2adultos_1-2niños_calef_gas_aire_ac" : 10
    }

    st.info("Clarification note: The simulation will only run correctly after you have confirmed the data summarized in this tab by clicking the Confirm Data button at the bottom of this page.")
    st.header("Datos finales")
    try:
        st.markdown("""### Community name: {}""".format(str(st.session_state.comunidades[-1][0])))
    except:
        st.write()
    st.write("")
    try:
        st.markdown("""### Community location: {}""".format(str(st.session_state.comunidades[-1][1])))
    except:
        st.write()
    

    conceptos= ["description", "latitude", "longitude", "pv_num_modules", "pv_peak_power", "pv_module_type","pv_module_orientation","pv_module_tilt"]

    # Diccionarios de las instalaciones fotovoltaicas
    fotovoltaicos = []
    auxFV = st.session_state["fotovolt"].copy()
    try:
        if any(auxFV):
            for i in auxFV:
                diccioFVaux = {}
                for j,k in zip(conceptos,i):
                    diccioFVaux[j] = k
                fotovoltaicos.append(diccioFVaux)
    except:
        st.write("There are no photovoltaic generators assigned")

    # Diccionarios de las instalaciones eolicas
    conceptos= ["description", "latitude", "longitude", "wind_peak_power"]
    eolicos = []
    try:
        auxEO = st.session_state["eolicos"].copy()
        if any(auxEO):
            for i in auxEO:
                diccioEOaux = {}
                for j,k in zip(conceptos,i):
                    diccioEOaux[j] = k
                eolicos.append(diccioEOaux)

    except:
        st.write("There are no wind turbines assigned")

    # Diccionarios de las baterias
    conceptos= ["ds_storage_system","id_battery_type", "voltage", "nominal_capacity", "max_limit", "min_limit", "init_capacity", "max_hour_discharge"]
    baterias = []
    try:
        auxBat = st.session_state["baterias"].copy()
        if any(auxBat):
            for i in auxBat:
                diccioBataux = {}
                for j,k in zip(conceptos,i):
                    diccioBataux[j] = k
                baterias.append(diccioBataux)
    except:
        st.write("No batteries assigned")

    # Diccionarios de los usuarios
    conceptos = ["id_consumer_profile"]
    usuarios = []
    try:
        auxUser = st.session_state["usuarios"].copy()
        if any(auxUser):
            for us in auxUser:
                valor = diccioTipo[us[0]]
                for i in range(us[1]):
                    usuarios.append(valor)
    except:
        st.write("There are no assigned users")


    st.header("Data summary")

    st.write("PV Generators:")
    st.dataframe(dfFV)
    
    dfaux = pd.DataFrame(
        {
            "col1": dfFV["latitude"],
            "col2": dfFV["longitude"],
        }
    )

    st.map(dfaux, latitude="col1", longitude="col2", color = (0.2, 0.2, 0.5, 0.5))

    st.write("Wind turbines:")
    st.dataframe(dfEO)

    
    dfaux2 = pd.DataFrame(
        {
            "col1": dfEO["latitude"],
            "col2": dfEO["longitude"],
        }
    )

    st.map(dfaux2, latitude="col1", longitude="col2", color = (0.2, 0.5, 0.2, 0.5))
    st.write("Energy storage:")
    st.dataframe(dfBat)

    st.write("Users:")
    st.dataframe(dfUs)

    idComunidad = 0

    col1, col2, col3 = st.columns(3)
    with col1:
        # Reset button
        if st.button("Reset all"):
            st.session_state.clear()  # Rerun the script
            st.session_state["authentication_status"] = None
            st.rerun(scope="app")
    with col3:
        sub = False
        if st.button("Confirm Data",type="primary", disabled= not ((usr and gen) and ce)):
            currentDateTime = dt.datetime.now()
            start = currentDateTime.strftime('%Y-%m-%d %H:%M:%S')
            st.session_state.procesosCurso = start
            if any(comunidadEnerg) and (any(fotovoltaicos) or any(eolicos)) and any(usuarios):
                try:
                    st.session_state.datoscomunidad["max_participation"]=comunidadEnerg["max_participation"]
                    st.session_state.datoscomunidad["min_participation"]=comunidadEnerg["min_participation"]
                    st.session_state.datoscomunidad["energy_poverty"]=comunidadEnerg["energy_poverty"]
                    idComunidad,start = envioDatos(comunidadEnerg,fotovoltaicos,eolicos,baterias,usuarios,start)
                    logging.info("ID de la comunidad: "+str(idComunidad))
                    st.session_state.idComunidad = idComunidad
                    st.session_state.informe["cantidadFV"] = numeroFV
                    st.session_state.informe["cantidadEO"] = numeroEO
                    st.session_state.informe["cantidadBat"] = numeroBat
                    st.session_state.informe["cantidadUsers"] = numeroUsers

                    st.write("Export completed, community ID: ",idComunidad)
                    sub = True
                    st.session_state.envioInfo = True
                except Exception as e:
                    logging.error("In sending the data: ", exc_info=True)
                    st.error("Program execution error. Try going to the login tab, reloading the page, and re-entering your information. If the error persists, check the logs or contact your administrator.")
                    st.write("Error in sending")
            
    if sub:
        st.success("You can go to the simulation tab to perform the simulation of production, consumption and energy distribution for the year you select.")






