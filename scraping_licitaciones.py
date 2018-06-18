from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
import requests
from xml.etree import ElementTree
from time import sleep
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
from dateutil.relativedelta import relativedelta

url = 'https://contrataciondelestado.es/wps/poc?uri=deeplink%3Abusqueda_licitacion_vis&ubicacionOrganica=VWI4MQOJzFM%3D'
browser = webdriver.Chrome('/home/josemolina/programs_python/chromedriver')
#'/home/josemolina/programs_python/geckodriver'
browser.implicitly_wait(10)
browser.get(url)

#search = browser.find_element_by_css_selector('.divLogo2')
#search.click()

startDate = browser.find_element_by_id('viewns_Z7_AVEQAI930OBRD02JPMTPG21004_:form1:textMinFecAnuncioMAQ2')
startDate.clear()
startDate.send_keys('01-01-2013')

endDate = browser.find_element_by_id('viewns_Z7_AVEQAI930OBRD02JPMTPG21004_:form1:textMaxFecAnuncioMAQ')
endDate.clear()
endDate.send_keys('31-12-2017')

select = Select(browser.find_element_by_id('viewns_Z7_AVEQAI930OBRD02JPMTPG21004_:form1:menu111MAQ'))
select.select_by_visible_text('Contrato menor')

submit = browser.find_element_by_id('viewns_Z7_AVEQAI930OBRD02JPMTPG21004_:form1:button1')
submit.click()

#listas para almacenar datos
expediente_save = []
adjudicatario_save = []
objeto_save = []
preciocon_save = []
preciosin_save = []
fechaadj_save = []
paisejec_save = []
org_save = []
link_save = []
origenadj_save = []
duracion_save=[]
unidadt_save = []
nif_save = []
tipoempresa_save = []
tramit_save = []
firmante_save = []
contador = 0
#beautifulsoup es para cosas estaticas
#con selenium, enlaces
next = True
#cada vez que empieza el bucle se recorre una página entera
while next == True:
    times = 0
    html = BeautifulSoup(browser.page_source, 'html.parser')
    results_table = html.find('table',{'id': 'myTablaBusquedaCustom'})
    body = results_table.find('tbody')
    all_rows=body.find_all('tr')
    for row in all_rows:
        idItem = row.find('td', class_='tdExpediente')
        if (idItem):
            link = idItem.find('a')
            expediente = browser.find_element_by_id(link['id'])
            expediente.click()
			# a partir de este punto, se sacan datos de licitaciones
			
            licitacion_html = BeautifulSoup(browser.page_source,'html.parser')
            div_licitacion = licitacion_html.find('div',class_='capaAtributos')
            name_li = div_licitacion.find('li',{'id':'fila2_columna2'})
            name = name_li.find('span')
            print(name.text)
            link2 = browser.find_elements_by_css_selector('a.celdaTam2')
            #coger id de ventana actual
            #main_window = browser.current_window_handle
            #comando de chrome/firefox para abrir nueva ventana
#####################################################################################################################################
            browser.get(link2[1].get_attribute('href'))
            browser.get(browser.current_url)
            xml_source = browser.execute_script('return document.getElementById("webkit-xml-viewer-source-xml").innerHTML')
            bs = BeautifulSoup(xml_source,'xml')
            
            #set de etiquetas existentes
            tags= set()
            for child in bs:
                tipo_anuncio = child.name
            parent_tag = bs.find(tipo_anuncio)
            for child in parent_tag:
                tags.add(child.name)
            #parsear datos
            if('ContractFolderID' in tags):   
                codigo = (bs.find('cbc:ContractFolderID'))
            else:
                codigo = 'NAN'
            if('TenderResult' in tags):
                fecha_adj = (bs.find('cac:TenderResult')).find('cbc:AwardDate')
                adjudicatario = (bs.find('cac:TenderResult')).find('cbc:Name')
                origen_adj = (bs.find('cac:TenderResult')).find('cbc:IdentificationCode')
                nif = (bs.find('cac:TenderResult')).find('cbc:ID')
                tipo_empresa = (bs.find('cac:TenderResult')).find('cbc:ID')
            else:
                fecha_adj,adjudicatario,origen_adj,nif,tipo_empresa = 'NAN','NAN','NAN','NAN','NAN'
            if('ProcurementProject' in tags):
                objeto = (bs.find('cac:ProcurementProject')).find('cbc:Name')
                precio_con = ((bs.find('cac:ProcurementProject')).find('cac:BudgetAmount')).find('cbc:TotalAmount')
                precio_sin = ((bs.find('cac:ProcurementProject')).find('cac:BudgetAmount')).find('cbc:TaxExclusiveAmount')          
                duracion = (bs.find('cac:ProcurementProject')).find('cbc:DurationMeasure')
                unidad_t = (bs.find('cac:ProcurementProject')).find('cbc:DurationMeasure')                        
                pais_ejec1 = (bs.find('cac:ProcurementProject')).find('cac:RealizedLocation')
                etiquetas = set()
                for child in pais_ejec1:
                    etiquetas.add(child.name)
                if ('Address' in etiquetas):
                    pais_ejec = ((pais_ejec1.find('cac:Address').find('cac:Country')).find('cbc:Name'))
                else:
                    pais_ejec = 'NAN'
            else:
                objeto,precio_con,precio_sin,duracion,unidad_t,pais_ejec = 'NAN','NAN','NAN','NAN','NAN','NAN'
            if('ContractingParty' in tags):    
                organizacion = (((bs.find('cac:ContractingParty')).find('cac:Party')).find('cac:PartyName')).find('cbc:Name')
                firmante = ((bs.find('cac:ContractingParty')).find('cac:Party')).find('cbc:JobTitle')
            else:
                organizacion, firmante = 'NAN', 'NAN'
            if('TenderingProcess' in tags):
                link = ((((bs.find('cac:TenderingProcess')).find('cac:AdditionalDocumentReference')).find('cac:Attachment')).find('cac:ExternalReference')).find('cbc:URI')
                tramit = (bs.find('cac:TenderingProcess')).find('cbc:UrgencyCode')
            else:
                link,tramit = 'NAN','NAN'
            
            #check para comprobar si ha sacado texto o no
            if(tramit!= 'NAN' and tramit is not None):
                tramit_save.append(tramit.attrs['name'])
            else:
                tramit_save.append('NAN')
            if(firmante!= 'NAN' and firmante is not None):
                firmante_save.append(firmante.text)
            else:
                firmante_save.append('NAN')
            if(codigo!= 'NAN' and codigo is not None):
                expediente_save.append(codigo.text)
            else:
                expediente_save.append('NAN')
            if(adjudicatario != 'NAN' and adjudicatario is not None):
                adjudicatario_save.append(adjudicatario.text)
            else:
                adjudicatario_save.append('NAN')
            if(origen_adj!= 'NAN' and origen_adj is not None):    
                origenadj_save.append(origen_adj.attrs['name'])
            else:
                origenadj_save.append('NAN')
            if(objeto != 'NAN' and objeto is not None):
                objeto_save.append(objeto.text)
            else:
                objeto_save.append('NAN')
            if(precio_con != 'NAN' and precio_con is not None):
                preciocon_save.append(precio_con.text)
            else:
                preciocon_save.append('NAN')
            if(precio_sin != 'NAN' and precio_sin is not None):    
                preciosin_save.append(precio_sin.text)
            else:
                preciosin_save.append('NAN')
            if(fecha_adj != 'NAN' and fecha_adj is not None):    
                fechaadj_save.append(fecha_adj.text)
            else:
                fechaadj_save.append('NAN')
            if(pais_ejec != 'NAN' and pais_ejec is not None ):   
                paisejec_save.append(pais_ejec)
            else:
                paisejec_save.append('NAN')
            if(organizacion != 'NAN' and organizacion is not None):
                org_save.append(organizacion.text)
            else:
                org_save.append('NAN')
            if(link != 'NAN' and link is not None):
                link_save.append(link.text)
            else:
                link_save.append('NAN')
            if(duracion != 'NAN' and duracion is not None):
                duracion_save.append(duracion.text)
            else:
                duracion_save.append('NAN')
            if(unidad_t != 'NAN' and unidad_t is not None):
                unidadt_save.append(unidad_t.attrs['unitCode'])
            else:
                unidadt_save.append('NAN')
            if(nif != 'NAN' and nif is not None):
                nif_save.append(nif.text)
            else:
                nif_save.append('NAN')
            if(tipo_empresa != 'NAN' and tipo_empresa is not None):
                tipoempresa_save.append(tipo_empresa.attrs['schemeName'])
            else:
                tipoempresa_save.append('NAN')

            contador+=1
            print(f'Contrato numero: {contador}')
#####################################################################################################################################

# Close current tab
            #browser.find_element_by_tag_name('body').send_keys(Keys.CONTROL + 'w')
            #browser.quit()
            #browser.close()
			#la primera vez que entro en un elemento de la table en una pagina y vuelvo hacia atras se obtiene un error de envio de formulario
            browser.execute_script('window.history.go(-2)')
			#if (times == 0):
            browser.get(browser.current_url)
			#	times = 1
    try:
        nextpage = browser.find_element_by_id('viewns_Z7_AVEQAI930OBRD02JPMTPG21004_:form1:footerSiguiente')
        if (nextpage):
            nextpage.click()
        else: 
            next = False
    except:
        next = False
browser.close()
#crea un dataframe y almacena en xslx
articleData = pd.DataFrame({'expediente':expediente_save,
                            'objeto':objeto_save,
                            'importe_adj_sin':preciosin_save,
                            'importe_adj_con':preciocon_save,
                            'fecha_adj':fechaadj_save,
                            'org_contratacion':org_save,
                            'firmante':firmante_save,
                            'pais_ajecucion':paisejec_save,
                            'adjudicatario':adjudicatario_save,
                            'nif':nif_save,
                            'tipo_empresa':tipoempresa_save,
                            'origen_adjudicatario':origenadj_save,
                            'tramitacion':tramit_save,
                            'plazo_duracion':duracion_save,
                            'unidad_tiempo':unidadt_save,
                            'link':link_save})  
articleData.to_excel("menores_scraping.xlsx", index = False)

