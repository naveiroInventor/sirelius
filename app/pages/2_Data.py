### Codigo desarrollado e implementado por Jose Manuel Naveiro Gomez
### josemanuel.naveiro@endef.com

import streamlit as st
import datetime as dt
from string import punctuation

import base64
import logging

from pages.scripts.funcionesgrles import resetear
from pages.scripts.calculos import calcula2
from pages.pages_content.page2 import creacion_CE, instalacion_fv, instalacion_eo, confirmacion
from pages.pages_content.page2 import instalacion_bat, registro_usuarios, registro_coeficientes

# Comienza la pagina
try:
    st.title("Community data from: "+str(st.session_state.comunidades[-1][0]) + " [" + str(st.session_state.comunidades[-1][1]) + "]")
except:
    st.title("Enter the name and location of the Community.")


from zoneinfo import ZoneInfo
espana = ZoneInfo("Europe/Madrid")
st.write(dt.datetime.today().astimezone(espana).__format__('%d %b %Y, %I:%M%p'))
st.info("All required fields must be completed before uploading data and running the simulation. Pay attention to the warnings on each tab.")

st.sidebar.markdown(
    """<a href="https://endef.com/">
    <img src="data:;base64,{}" width="200">
    </a>""".format(
        base64.b64encode(open("path1.png", "rb").read()).decode()
    ),
    unsafe_allow_html=True,
)

tab1, tab2, tab3, tab4, tab5, tab6, tab7= st.tabs(["Photovoltaics","Wind", "Batteries", "Users","Coefficients", "Confirmation", "Simulate"])
try:
    ce = any(st.session_state["comunidades"])
except:
    ce = False

fv = False
eo = False
gen = False
bt = False
usr = False
sub = False

if ce:
    location = None
    comunidadEnerg = st.session_state.comunidad
    dfComu = st.session_state.comunidadDF

    with tab1:
        try:
            dfFV, numeroFV, fv = instalacion_fv(ce, fv)
        except Exception as e:
            logging.debug("In photovoltaics:", exc_info=True)
            st.error("Program execution error. Try going to the login tab, reloading the page, and re-entering your information. If the error persists, check the logs or contact your administrator.")

    with tab2:
        try:
            dfEO, numeroEO, eo = instalacion_eo(ce, eo)
        except Exception as e:
            logging.debug("In wind power:", exc_info=True)
            st.error("Program execution error. Try going to the login tab, reloading the page, and re-entering your information. If the error persists, check the logs or contact your administrator.")
            
    with tab3:
        try:
            dfBat, numeroBat = instalacion_bat(ce, fv, eo, gen)
    
        except Exception as e:
            logging.debug("In the batteries: ", exc_info=True)
            st.error("Program execution error. Try going to the login tab, reloading the page, and re-entering your information. If the error persists, check the logs or contact your administrator.")
            
    with tab4:
        if fv or eo:
            gen = True
        try:
            dfUs, numeroUsers, usr = registro_usuarios(ce, gen, usr)
        
        except Exception as e:
            logging.error("En los usuarios: ", exc_info=True)
            st.error("Program execution error. Try going to the login tab, reloading the page, and re-entering your information. If the error persists, check the logs or contact your administrator.")
    
    with tab5:
        try:
            registro_coeficientes(numeroUsers,comunidadEnerg)
        except Exception as e:
            logging.error("En los coeficinetes: ", exc_info=True)
            st.error("Program execution error. Try going to the login tab, reloading the page, and re-entering your information. If the error persists, check the logs or contact your administrator.")
    
    with tab6:
        datos=[comunidadEnerg, dfComu, ce, dfFV, numeroFV, dfEO, numeroEO, dfBat, numeroBat, gen, dfUs, numeroUsers, usr]
        try:
            confirmacion(datos)
        except Exception as e:
            logging.error("En la confirmación de los datos: ", exc_info=True)
            st.error("Program execution error. Try going to the login tab, reloading the page, and re-entering your information. If the error persists, check the logs or contact your administrator.")
        
    
    with tab7:
    
        st.info("Clarification note: The simulation should only be run after the data has been exported. You must select the year for which you want to run the simulation and then click the Simulate button.")
        try:
            st.markdown("""## Community name: {}""".format(str(st.session_state.comunidades[-1][0])))
            simulable = True
        except:
            st.write()
            simulable = False
    
        date_year = st.number_input("Simulation year", disabled= not simulable and not st.session_state.envioInfo, value = int(dt.datetime.now ().year), min_value=2020,step=1)
        
    
        if 'run_button' in st.session_state and st.session_state.run_button == True:
            st.session_state.running = True
        else:
            st.session_state.running = False
    
        if st.button('Simulate', disabled=((not any(st.session_state.procesosCurso)) or st.session_state.saltoSimu or st.session_state.running),     type="primary", key='run_button'):
            exitoSim, Objeto_comunidad = calcula2(st.session_state.procesosCurso,date_year)
            st.session_state.anyo = date_year
            st.session_state.saltoSimu = True
            
            if exitoSim:
                st.success("You can view the results by going to the General and Individual Results links in the sidebar.")
                st.write("Start time of the process:", st.session_state.procesosCurso)
                
                a_zero = ["comunidades","usuarios","fotovolt","eolicos","baterias","usuariosCE"]
                for i in a_zero:
                    resetear(i)
                st.session_state.contenidoComu = Objeto_comunidad

else:
    st.markdown("# Enter the name and location of your community")