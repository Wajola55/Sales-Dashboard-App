import pandas as pd
import plotly.express as px
import streamlit as st
from PIL import Image



# emojis: https://www.webfx.com/tools/emoji-cheat-sheet/


st.set_page_config(page_title="Sales Dashboard")
st.markdown("*This dashboard displays sales data and insights for a supermarket.*")
layout="wide"



# Define a container to hold the main content
main_container = st.container()

@st.cache
def get_data_from_excel():
    df = pd.read_excel(
        io='supermarket_sales.xlsx',
        engine='openpyxl',
        sheet_name='Sales',
        usecols='B:R',
        nrows=1000,
    )

    # --- adding 'hour' column to dataframe ---
    df["hour"] = pd.to_datetime(df["Time"], format="%H:%M:%S").dt.hour
    return df

df = get_data_from_excel()

df.columns = df.columns.str.replace(' ', '_')

image = Image.open('sales.png')
st.sidebar.image(image,  width=100, use_column_width=True)



st.sidebar.header("Use the filters below to explore the sales data:")
city = st.sidebar.multiselect(
    "Select the City:",
    options=df["City"].unique(),
    default=df["City"].unique()
)

customer_type = st.sidebar.multiselect(
    "Select the Customer Type:",
    options=df["Customer_type"].unique(),
    default=df["Customer_type"].unique()
)

gender = st.sidebar.multiselect(
    "Select the Gender:",
    options=df["Gender"].unique(),
    default=df["Gender"].unique()
)

df_selection = df.query(
    "City == @city & Customer_type == @customer_type & Gender == @gender"
)

 # --- Main Page ----

st.title(":bar_chart: Sales Dashboard")
st.markdown('##')

# --- Top KPI's ----

total_sales = int(df_selection["Total"].sum())
average_rating = round(df_selection["Rating"].mean(), 1)
star_rating = ":star:" * int(round(average_rating, 0))
average_sale_by_transaction = round(df_selection["Total"].mean(), 2)

st.subheader("Top KPIs")


left_column, middle_column, right_column = st.columns(3)
with left_column:
    st.subheader("Total Sales:")

    st.subheader(f"US $ {total_sales:,}")
with middle_column:
    st.subheader("Average Rating:")
    st.subheader(f"{average_rating} {star_rating}")
with right_column:
    st.subheader("Average Sales Per Transaction:")
    st.subheader(f"US $ {average_sale_by_transaction}")


st.markdown("---")


# --- Date range filter ---

date_range = st.sidebar.date_input(
    label="Select Date Range:",
    value=[df_selection["Date"].min(), df_selection["Date"].max()],
    min_value=df_selection["Date"].min(),
    max_value=df_selection["Date"].max()
)

start_date = date_range[0]
end_date = date_range[1]

df_selection = df.query(
    "City == @city & Customer_type == @customer_type & Gender == @gender & Date >= @start_date & Date <= @end_date"
)


# --- Sales by product line ----

sales_by_product_line = (
    df_selection.groupby(by=["Product_line"]).sum()[["Total"]].sort_values(by="Total")
)

fig_product_sales = px.bar(
    sales_by_product_line,
    x="Total",
    y=sales_by_product_line.index,
    orientation="h",
    title="<b>Sales by Product Line</b>",
    color_discrete_sequence=["#00BFBF"] * len(sales_by_product_line),
    template="plotly_white",
)

fig_product_sales.update_layout(
    margin=dict(l=20, r=20, t=50, b=20),
    plot_bgcolor="rgba(0,0,0,0)",
    xaxis_title="Total Sales",
    yaxis_title="Product Line",
    font=dict(size=14),
    height=400,
)

# --- Sales by Payment Method ----

sales_by_payment_method = (
    df_selection.groupby(by=["Payment"]).sum()[["Total"]].sort_values(by="Total")
)

fig_payment_sales = px.bar(
    sales_by_payment_method,
    x="Total",
    y=sales_by_payment_method.index,
    orientation="h",
    color="Total",
    color_continuous_scale="Blues",
    labels={"x": "Total Sales", "y": "Payment Method"},
    title="<b>Sales by Payment Method</b>",
    template="plotly_white",
)

fig_payment_sales.update_layout(
    plot_bgcolor="rgba(0,0,0,0)",
    xaxis=dict(showgrid=False, showticklabels=True),
    yaxis=dict(showgrid=False, showticklabels=True),
    margin=dict(l=0, r=0, t=50, b=0),
    font=dict(size=14),
)

fig_payment_sales.update_traces(
    textposition="inside",
    textfont=dict(color="white"),
    hovertemplate="<b>%{y}</b><br>Total Sales: %{x:.2f}<extra></extra>",
)

st.plotly_chart(fig_payment_sales)


# --- Sales by hour ----

sales_by_hour = df_selection.groupby(by=["hour"]).sum()[["Total"]]
fig_hourly_sales = px.bar(
    sales_by_hour,
    x=sales_by_hour.index,
    y="Total",
    title="<b>Sales by hour</b>",
    color_discrete_sequence=["#00BFBF"] * len(sales_by_hour),
    template="plotly_white",
)

fig_hourly_sales.update_layout(
    margin=dict(l=20, r=20, t=50, b=20),
    plot_bgcolor="rgba(0,0,0,0)",
    xaxis=dict(title="Hour of the Day", tickmode="linear"),
    yaxis=dict(title="Total Sales"),
    font=dict(size=14),
    height=400,
)


left_column, right_column = st.columns(2)
left_column.plotly_chart(fig_hourly_sales, use_container_width=True)
right_column.plotly_chart(fig_product_sales, use_container_width=True)

streamlit_style = """
			<style>
			@import url('https://fonts.googleapis.com/css2?family=Phudu:wght@300&family=Shantell+Sans:wght@300&display=swap');

			html, body, [class*="css"]  {
			font-family: 'Phudu', cursive;
			}
			</style>
			"""
st.markdown(streamlit_style, unsafe_allow_html=True)
# --- hide streamlit style ---

hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """

st.markdown(hide_st_style, unsafe_allow_html=True)