# test streamlit program

import streamlit as st

st.set_page_config(page_title="My App",layout="wide") #initial in of streamlit code b4
                                                        #any other code

with st.sidebar:
    st.header("Controls") 
    option = st.selectbox("Choose",["A", "B", "C"])

with st.expander("See details"):
    st.write("Hidden content")
    
name = st.text_input("Name")
if st.button("Submit"):
    if name:
        st.success(f"Hello, {name}!")
    else:
        st.warning("Enter name")

# test streamlit code
st.title("Hi, I am Asad.")
st.write("My first streamlit program.")
st.button("Click me.")

st.markdown("**test for bold**")
st.markdown("*taking naruto image*")
st.divider()
st.image(r"C:\Users\ahmed\Downloads\naruto_fanart.jpg", caption="drawing", use_container_width="auto")

