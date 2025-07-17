import os
import streamlit as st
from supabase import create_client, Client

@st.cache_resource
def init_connection() -> Client:
    url = os.environ.get("SUPABASE_URL", st.secrets.get("SUPABASE_URL"))
    key = os.environ.get("SUPABASE_SERVICE_KEY", st.secrets.get("SUPABASE_SERVICE_KEY"))
    return create_client(url, key)

supabase = init_connection()
