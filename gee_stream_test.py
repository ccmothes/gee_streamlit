# -*- coding: utf-8 -*-
"""
Created on Fri Jan 21 15:45:33 2022

@author: Caitlin
"""
import streamlit as st
import geemap
import datetime
from datetime import date


st.title("Poudre Portal Sentinel Viewer")


# choose date
today = date.today()
d1 = today.strftime("%Y-%m-%d")

d = st.sidebar.date_input(
    "Start date:",
    datetime.date(2020, 1, 1))

Map = geemap.Map()

if st.sidebar.checkbox('View Map'):
    #st.write(d)
    Map.to_streamlit()



#Map.to_streamlit()

