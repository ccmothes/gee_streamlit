# -*- coding: utf-8 -*-
"""
Created on Mon May  2 13:17:59 2022

@author: ccmothes
"""

import streamlit as st
import geemap
import ee
import datetime
from datetime import date
from datetime import datetime

try:
        ee.Initialize()
except Exception as ee:
        ee.Authenticate()
        ee.Initialize()

# set up image collection

region = ee.Geometry.BBox(-105.89218, 40.27989, -105.17284, 40.72316)


# need to use Harmonized Sentinel collection because post Jan 2022 bands are different
sent2 = ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED") \
  .filterBounds(region)
    
land8 = ee.ImageCollection('LANDSAT/LC08/C02/T1_L2') \
    .filterBounds(region)


land9 = ee.ImageCollection('LANDSAT/LC09/C02/T1_L2') \
    .filterBounds(region)
    
    
# add "SPACECRAFT_ID" attribute to match landsat so can pull spacecraft name from chosen image
sent2 = sent2.map(lambda x: x.set('SPACECRAFT_ID', 'Sentinel-2A'))


# merge the collection
collection = sent2.merge(land8).merge(land9)


# Make the app interface

st.set_page_config(layout="wide")

st.title("Poudre Portal Earth Engine Viewer")


# choose date
today = datetime.today()
#today = today.strftime("%Y-%m-%d")


d1 = st.sidebar.date_input(
    label="Choose date:",
    value=today,
    max_value=today)


#st.write(d1.strftime("%Y-%m-%d"))
st.write(d1)

#create date function to get image closest to chosen date
def date_fun(image):
    return image.set(
    'dateDist',
    ee.Number(image.get('system:time_start')).subtract(dateOfInterest).abs()
    )

## Reformat d1 and define dateOfInterest
d2 = d1.strftime("%Y-%m-%d")
dateOfInterest = datetime.strptime(d2, '%Y-%m-%d').timestamp()*1000



# calculate dateDist and sort based on chosen dateOfInterest
collectionSort = collection.map(date_fun).sort('dateDist')


#Print aircraft and date of nearest image
st.write(collectionSort.first().date().format('YYYY-MM-dd').getInfo())

st.write(collectionSort.first().get('SPACECRAFT_ID').getInfo())


# add image to map
Map = geemap.Map(add_google_map=False, layer_ctrl=True)
#center around region of interest
Map.centerObject(region, zoom=11)


# set of vis parameters depending on spacecraft
spacecraft = collectionSort.first().get('SPACECRAFT_ID').getInfo()


if spacecraft == 'Sentinel-2A':
    vizTC = {
    'bands' : ['B4', 'B3', 'B2'],
    'min': 0,
    'max': 8000
    } 
else:
     vizTC = {
    'bands' : ['SR_B4', 'SR_B3', 'SR_B2'],
    'min': 6000,
    'max': 12000
    } 


vizSnow = {
    'bands': ['MSK_SNWPRB'],
    'min': 0,
    'max': 1,
    'palette': ['FFFFFF', 'FF0000']
}

vizFire = {
    'bands': ['B12', 'B8', 'B4'],
    'min': 0,
    'max': 3000
}

Map.addLayer(collectionSort.first(), vizTC, 'True Color')
#Map.addLayer(collection, vizSnow, "Snow Probability")
#Map.addLayer(collection, vizFire, "Wildfire")

Map.to_streamlit(height=1000)
