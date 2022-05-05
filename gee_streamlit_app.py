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
import pandas as pd


#try:
#        ee.Initialize()
#except Exception as ee:
#        ee.Authenticate()
#        ee.Initialize()

# set up data/image collection

# read in csv of study sites
#sites = pd.read_csv("C:/Users/ccmothes/Desktop/poudrePortal/data/poudreportal_sites.csv")
sites = pd.read_csv("https://raw.githubusercontent.com/ccmothes/gee_streamlit/master/poudreportal_sites.csv")


# region to clip collection to
region = ee.Geometry.BBox(-105.89218, 40.417183, -105.140642, 40.72316)


# function to mask clouds using Sentinel-2 QA band: https://developers.google.com/earth-engine/datasets/catalog/COPERNICUS_S2_SR
def maskS2clouds(image):
    qa = image.select('QA60')
    # Bits 10 and 11 are clouds and cirrus, respectively.
    cloudBitMask = 1 << 10
    cirrusBitMask = 1 << 11
    # Both flags should be set to zero, indicating clear conditions.
    mask = qa.bitwiseAnd(cloudBitMask).eq(0)
    mask = mask.bitwiseAnd(cirrusBitMask).eq(0)
    return image.updateMask(mask).divide(10000)


# need to use Harmonized Sentinel collection because post Jan 2022 bands are different
sent2 = ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED") \
  .filterBounds(region)
  
#function to apply scaling factors for viz: https://geemap.org/notebooks/99_landsat_9/
def apply_scale_factors(image):
    opticalBands = image.select('SR_B.').multiply(0.0000275).add(-0.2)
    thermalBands = image.select('ST_B.*').multiply(0.00341802).add(149.0)
    return image.addBands(opticalBands, None, True).addBands(thermalBands, None, True)
    
land8 = ee.ImageCollection('LANDSAT/LC08/C02/T1_L2') \
    .filterBounds(region) \
    .map(apply_scale_factors)


land9 = ee.ImageCollection('LANDSAT/LC09/C02/T1_L2') \
    .filterBounds(region) \
    .map(apply_scale_factors)
    
    
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
#st.write(d1)

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
st.write("**Date of Observation:** " + collectionSort.first().date().format('YYYY-MM-dd').getInfo())

st.write("**Spacecraft:** " + collectionSort.first().get('SPACECRAFT_ID').getInfo())


#add checkbox to choose viz parameters
viz = st.radio("Choose Visualization Parameters: ",
               ('True Color', 'Wildfire Damage', "Snow Probability"))

# add image to map
Map = geemap.Map(add_google_map=False, layer_ctrl=True)
#center around region of interest
Map.centerObject(region, zoom=11)


#add study sites
Map.add_points_from_xy(sites, x="long", y="lat", layer_name = "Study Sites")


# set of vis parameters depending on spacecraft
spacecraft = collectionSort.first().get('SPACECRAFT_ID').getInfo()

plotImage = collectionSort.first()

if spacecraft == 'Sentinel-2A':
    if viz == 'True Color':
        vizParams = {
        'bands': ['B4', 'B3', 'B2'],
        'min': 0,
        'max': 0.3}
        Map.addLayer(maskS2clouds(plotImage), vizParams, viz)
    elif viz == 'Wildfire Damage':
        vizParams = {
        'bands': ['B12', 'B8', 'B4'],
        'min': 0,
        'max': 0.3
            }
        Map.addLayer(maskS2clouds(plotImage), vizParams, viz)
    else:
        vizParams = {
        'bands': ['MSK_SNWPRB'],
        'min': -1,
        'max': 1,
        'palette': ['green', 'white']
            }
        Map.addLayer(plotImage, vizParams, viz)
    
else:
    #snow probability for landsat (NDSI) is the normalized difference between B3 and B6
    if viz == 'True Color':
        vizParams = {
        'bands': ['SR_B4', 'SR_B3', 'SR_B2'],
        'min': 0,
        'max': 0.3}
        Map.addLayer(plotImage, vizParams, viz)

    elif viz == 'Wildfire Damage':
        vizParams = {
        'bands': ['SR_B7', 'SR_B5', 'SR_B4'],
        'min': 0,
        'max': 0.3}
        Map.addLayer(plotImage, vizParams, viz)

    else:
        plotImage2 = plotImage.normalizedDifference(['SR_B3', 'SR_B6'])
        vizParams = {
        'min': -1,
        'max': 1,
        'palette': ['green', 'white']
            }
        Map.addLayer(plotImage2, vizParams, viz)
   

#Map.addLayer(plotImage, vizTC, 'True Color')
#Map.addLayer(collection, vizSnow, "Snow Probability")
#Map.addLayer(collection, vizFire, "Wildfire")

Map.to_streamlit(height=1000)
