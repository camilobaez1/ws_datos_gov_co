#Importación de librerias
import os
import requests
import csv
from bs4 import BeautifulSoup
import bs4
from selenium import webdriver

#Creación de función para 
def consultaPaginaWeb(queryURL, elementList, cantidad):
  browser = webdriver.Chrome()
  response= requests.get(queryURL)
  soup = BeautifulSoup(response.text,"html.parser")

  #Se obtienen todos los div contenedores con nombre de clase "browse2-result", si encuentra elementos los procesa
  if len(soup.findAll("div", {"class": "browse2-result"}))>0:
    for item in soup.findAll("div", {"class": "browse2-result"}):
      #Se obtiene el nombre del dataset
      nombre=item.find("a").string
      #Se obtiene la descripción del dataset
      descripcion="Sin descripción reportada en el sitio"
      if len(item.findAll("div",{"class":"browse2-result-description"}))>0: #Valida si existe descripción
        descripcion=item.find("div",{"class":"browse2-result-description"}).div.string
      
      #Se obtiene el enlace del dataset
      url=item.find("a")["href"]
    
      #Se obtienen las categorias del item, span con nombre de clase "browse2-result-type-name"
      categorias=""
      for categoria in item.findAll("span",{"class": "browse2-result-type-name"}):
        categorias=categoria.string+"/"+categorias
        if len(categorias)>0:
          categorias=categorias[:len(categorias)-1]
      
      #Se obtiene fecha de creación
      creado=item.find("span",{"class":"dateLocalize"}).string
      #Se obtiene cantidad de visitas
      visitas=item.find("div",{"class":"browse2-result-view-count-value"}).string.replace("\n            ","").replace("\n          ","")
      #Se obtienen topics
      temas=""
      for topic in item.find("div",{"class":"browse2-result-topics"}).findAll("a"):
        temas=topic.span.string+"/"+temas
        if len(temas)>0:
          temas=temas[:len(temas)-1]
        
      #Se obtiene la información del tipo de datos "Conjunto de Datos" en la variable "categorias"
      #Los datos a obtener son: ,"Area o Dependencia","Nombre de la Entidad","Departamento","Municipio",
      #"Orden","Sector","Idioma","Cobertura Geográfica","Frecuencia de Actualización","Categoría","Descargas"
      area=""
      entidad=""
      departamento=""
      municipio=""
      orden=""
      sector=""
      idioma=""
      cobertura=""
      frecuencia=""
      cat=""
      descargas=""
      filas=""
      columnas=""
      if categorias=="Conjunto de Datos":
        #Al tratarse de un sitio web con contenido dinamico cargado con Ajax, se debe utilizar Selenium con el controlador
        #del navegador Google Chrome para obtener el sitio web completo mediante la función .page_source
        browser.get(url)
        soup2 = BeautifulSoup(browser.page_source,"html5lib")
        for metadata in soup2.findAll("div",{"class":"metadata-table"}):
          try:
              if metadata.find("h3",{"class","metadata-table-title"}).string=="Información de la Entidad":
                area=metadata.find("table").find("tbody").findAll("tr")[0].findAll("td")[1].span.string
                entidad=metadata.find("table").find("tbody").findAll("tr")[1].findAll("td")[1].span.string
                departamento=metadata.find("table").find("tbody").findAll("tr")[2].findAll("td")[1].span.string
                municipio=metadata.find("table").find("tbody").findAll("tr")[3].findAll("td")[1].span.string
                orden=metadata.find("table").find("tbody").findAll("tr")[4].findAll("td")[1].span.string
                sector=metadata.find("table").find("tbody").findAll("tr")[5].findAll("td")[1].span.string
              elif metadata.find("h3",{"class","metadata-table-title"}).string=="Información de Datos":
                idioma=metadata.find("table").find("tbody").findAll("tr")[0].findAll("td")[1].span.string
                cobertura=metadata.find("table").find("tbody").findAll("tr")[1].findAll("td")[1].span.string
                frecuencia=metadata.find("table").find("tbody").findAll("tr")[2].findAll("td")[1].span.string
              elif metadata.find("h3",{"class","metadata-table-title"}).string=="Temas":
                cat=metadata.find("table").find("tbody").findAll("tr")[0].findAll("td")[1].string
          except:
            error=""
        descargas=soup2.find("div",{"class":"metadata-pair download-count"}).dd.string
        try:
          filas=soup2.find("section",{"class":"landing-page-section dataset-contents"}).findAll("dd")[0].string
          columnas=soup2.find("section",{"class":"landing-page-section dataset-contents"}).findAll("dd")[1].string
        except:
          filas="Sin dato recolectado"
          columnas="Sin dato recolectado"
                        
      #Se agrega el elemento
      element=[cantidad,nombre,descripcion,url,categorias,creado,visitas,temas,area,entidad,departamento,municipio,
               orden,sector,idioma,cobertura,frecuencia,cat,descargas,filas,columnas]
      elementList.append(element)
      cantidad=cantidad+1
  else: #Sino, ordena parar el ciclo
    return False
  browser.close()
  return True

#Codigo principal del Scrapper
queryUrl="https://www.datos.gov.co/browse?sortBy=newest&page="

dataList=[]
headerList=["ID","Nombre","Descripción","URL","Categorias","Creado","# Visitas","Temas","Area o Dependencia",
            "Nombre de la Entidad","Departamento","Municipio","Orden","Sector","Idioma","Cobertura Geográfica",
            "Frecuencia de Actualización","Categoría","Descargas","Filas","Columnas"]
dataList.append(headerList)

continuar=True
page=1

while continuar:
  continuar=consultaPaginaWeb(queryUrl+str(page),dataList,(page-1)*10+1) #Se calcula el contador de acuerdo a la pagina actual
  page=page+1

#Creación del archivo CSV con la información recolectada
import numpy as np
import pandas as pd

filename = "open_data_colombia.csv"
df=pd.DataFrame.from_dict(dataList)
df.to_csv(filename,index=False,encoding="utf-8")
