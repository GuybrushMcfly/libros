
import streamlit as st
import pandas as pd
import numpy as np

# --- Page Configuration ---
st.set_page_config(
    layout="wide",
    page_title="Top Navigation Demo",
    page_icon=":material/home:"
)

# Add the Streamlit logo
st.logo("https://www.streamlit.io/images/brand/streamlit-mark-color.svg", link="https://streamlit.io")


# --- Sidebar Content ---
with st.sidebar:
    st.header("Top Navigation Demo")
    st.write("This app demonstrates the **top navigation bar** feature in Streamlit. \n\n Briefly, this is implemented using the `st.navigation()` method with the `position='top'` parameter.")


# --- Page Functions ---
def home_page():
    st.title("Home Page")
    st.write("Welcome to the home page!")
    st.write("""
        Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor
        incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud
        exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute
        irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla
        pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia
        deserunt mollit anim id est laborum.
    """)
    st.write("""
        Curabitur pretium tincidunt lacus, eget pretium justo cursus nec. Praesent
        facilisis, urna at consectetur lacinia, urna libero varius velit, nec bibendum
        lectus justo vitae libero. Integer convallis, mi vitae feugiat accumsan, massa
        nibh vulputate justo, vitae iaculis est urna vel justo.
    """)

def dashboard_page():
    st.title("Dashboard")
    st.write("Overview of key metrics and data visualizations.")

    # Metrics
    st.subheader("Key Metrics")
    metric_cols = st.columns(5)

    with metric_cols[0]:
        st.metric(label="Total Sales", value="$1.2M", delta="$12K", delta_color="normal", border=True)
    with metric_cols[1]:
        st.metric(label="Customers", value="5,800", delta="200", delta_color="normal", border=True)
    with metric_cols[2]:
        st.metric(label="Avg. Order Value", value="$207", delta="-$5", delta_color="inverse", border=True)
    with metric_cols[3]:
        st.metric(label="Conversion Rate", value="3.5%", delta="0.2%", delta_color="normal", border=True)
    with metric_cols[4]:
        st.metric(label="Active Users", value="1,234", delta="15%", delta_color="normal", border=True)

    # Charts
    chart_cols = st.columns(2)

    bar_chart_data = pd.DataFrame({
        'Category': ['A', 'B', 'C', 'D', 'E', 'A', 'B', 'C', 'D', 'E'],
        'Value': [150, 220, 180, 260, 190, 100, 120, 90, 110, 130],
        'Group': ['Group X', 'Group X', 'Group X', 'Group X', 'Group X', 'Group Y', 'Group Y', 'Group Y', 'Group Y', 'Group Y']
    })

    with chart_cols[0]:
        st.subheader("Sales by Category")
        st.bar_chart(bar_chart_data, x='Category', y='Value', color='Group')

    np.random.seed(42)
    scatter_data = pd.DataFrame({
        'Number of Customers': np.random.rand(50) * 100,
        'Revenue Generated': np.random.rand(50) * 100,
        'Avg Order Value': np.random.rand(50) * 10 + 5,
        'Conversion Efficiency': np.random.rand(50) * 100
    })

    with chart_cols[1]:
        st.subheader("Customers vs. Revenue")
        st.scatter_chart(
            scatter_data,
            x='Number of Customers',
            y='Revenue Generated',
            size='Avg Order Value',
            color='Conversion Efficiency',
            height=350
        )


def about_page():
    st.title("About Us")
    st.write("Learn more about our simple app.")
    st.write("""
        Proin eget tortor risus. Curabitur non nulla sit amet nisl tempus convallis quis
        ac lectus. Mauris blandit aliquet elit, eget tincidunt nibh pulvinar a. Curabitur
        arcu erat, accumsan id imperdiet et, porttitor at sem. Vestibulum ac diam sit amet
        quam vehicula elementum sed sit amet dui. Quisque velit nisi, pretium et in,
        vulputate at, lorem.
    """)
    st.write("""
        Donec rutrum congue leo eget malesuada. Nulla porttitor accumsan tincidunt.
        Sed porttitor lectus nibh. Nulla quis lorem ut libero malesuada feugiat.
        Cras ultricies ligula sed magna dictum porta. Pellentesque in ipsum id orci porta
        dapibus. Vestibulum ante ipsum primis in faucibus orci luctus et ultrices posuere
        cubilia Curae; Donec velit neque, auctor sit amet aliquam vel, ullamcorper sit amet
        ligula.
    """)

def contact_page():
    st.title("Contact Us")
    st.write("Feel free to reach out.")
    st.text_input("Your Email")
    st.text_area("Your Message")
    st.button("Send")

# Create pages using Material icons for navigation
pages = [
    st.Page(home_page, title="Home", icon=":material/home:", default=True),
    st.Page(dashboard_page, title="Dashboard", icon=":material/dashboard:"),
    st.Page(about_page, title="About", icon=":material/info:"),
    st.Page(contact_page, title="Contact", icon=":material/mail:"),
]

# Set up top navigation
current_page = st.navigation(pages, position="top")

# Run the selected page
current_page.run()
