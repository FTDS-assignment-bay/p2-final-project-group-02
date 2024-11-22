# import libraries
import streamlit as st
import eda
import chatme

# navigation section
navigation = st.sidebar.selectbox("Choose Page", ("Chat Me","EDA"))

# page
if navigation == "Chat Me":
    chatme.run()
else:
    eda.run()