# -*- coding: utf-8 -*-
"""
Created on Fri Jan 21 15:45:33 2022

@author: Caitlin
"""
import streamlit as st
import geemap
import ee
import datetime
from datetime import date

try:
        ee.Initialize()
except Exception as ee:
        ee.Authenticate()
        ee.Initialize()

# set up image collection

region = ee.Geometry.BBox(-105.89218, 40.27989, -105.17284, 40.72316)


# set of vis parameters

vizTC = {
    'bands' : ['B4', 'B3', 'B2'],
    'min': 0,
    'max': 3000
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

# Make the app interface

st.set_page_config(layout="wide")

st.title("Poudre Portal Sentinel Viewer")


# choose date
today = date.today()
#today = today.strftime("%Y-%m-%d")

# =============================================================================
d1 = st.sidebar.date_input(
    label="Start date:",
    value=datetime.date(2020, 1, 1),
    max_value=today)

d2 = st.sidebar.date_input(
    label="End date:",
    value=today,
    max_value=today)
# =============================================================================

# try date slider
dSlide = st.slider(
    label = "Select Date Range:",
    min_value = datetime.date(2020, 1, 1),
    max_value = today,
    value = (datetime.date(2021, 6, 1), datetime.date(2021, 8, 1)))

st.write(dSlide[0].strftime("%Y-%m-%d"), "-", dSlide[1].strftime("%Y-%m-%d"))
#if st.sidebar.checkbox('View Map'):
    #st.write(d)
    #Map.to_streamlit(height=1000)

#if st.button("Update Map!"):
collection = ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED") \
    .filterDate(dSlide[0].strftime("%Y-%m-%d"), dSlide[1].strftime("%Y-%m-%d")) \
    .filterBounds(region) \
    .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 70)) \
    .median()
Map = geemap.Map(add_google_map=False, layer_ctrl=True)
#center around region of interest
Map.centerObject(region, zoom=11)

Map.addLayer(collection, vizTC, 'True Color')
Map.addLayer(collection, vizSnow, "Snow Probability")
Map.addLayer(collection, vizFire, "Wildfire")

Map.to_streamlit(height=1000)
