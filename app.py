import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


st.set_page_config(layout="wide")


# Step 1: Load the data with caching
@st.cache_data
def load_data():
    df = pd.read_csv("data\clean_hotel_booking.csv")
    df.drop_duplicates(inplace=True)
    return df

@st.cache_data
def make_hotel_col_filter(data,col,value):
    return data[data[col] == value]

@st.cache_data
def make_grouping(data,group_col,agg_col,agg_func):
    return data.groupby([group_col],as_index = False)[[agg_col]].agg(agg_func).rename(columns = {agg_col:agg_func})

# Step 2: Load data
df = load_data()
cancel_booking = make_hotel_col_filter(df,"is_canceled",1)
not_cancel_booking = make_hotel_col_filter(df,"is_canceled",0)

# Step 3: Title
st.title("🏢 Hotel Booking Analysis Dashboard")

st.sidebar.header("🔍 Filter Option")


# Hotel Booking Data Expander
with st.expander("📊 Show Hotel Booking Data"):
    data_selection = st.selectbox(
    "Data Selection",
    options = ['Random Data',"Whole Data"],
    index = 0       # make default "Random Data"
)
    if data_selection == "Random Data":
        Random_data_num = st.number_input(label = "Choose Number of Rows",min_value = 5,value = 5,max_value = df.shape[0])
        st.markdown(f'#### {Random_data_num} Random Data 📝')
        st.dataframe(df.sample(Random_data_num))
    else:
        st.markdown(f'#### Whole Dataset 📝')
        st.dataframe(df)



hotel_type = st.sidebar.multiselect(
    "Select Hotel Type",
    options = ['Resort Hotel', 'City Hotel'],
    default = ['Resort Hotel', 'City Hotel']
)

print(hotel_type)

# make df_cancel_filter which is affect from then hotel_type filter
if hotel_type == ["Resort Hotel"]:
    filter_df = make_hotel_col_filter(df,'hotel',"Resort Hotel")
elif hotel_type == ["City Hotel"]:
    filter_df = make_hotel_col_filter(df,'hotel',"City Hotel")
else:
    filter_df = df.copy()


cancel_status = st.sidebar.multiselect(
    "Customer Cancel Data Status",
    options = ['Cancelled Data', 'Not Cancelled Data'],
    default = ['Cancelled Data', 'Not Cancelled Data']
)

if cancel_status == ['Cancelled Data']:
    df_cancel_filter  = filter_df[filter_df['is_canceled'] == 1]
elif cancel_status == ['Not Cancelled Data']:
    df_cancel_filter  = filter_df[filter_df['is_canceled'] == 0]
else:
    df_cancel_filter = filter_df



assigned_room_status = st.sidebar.multiselect(
    "Assigned Correct Room",
    options = ['True', 'False'],
    default = ['True', 'False']
)

if assigned_room_status == ['True']:
    df_cancel_filter  = df_cancel_filter[df_cancel_filter['assigned_room_status']]
elif assigned_room_status == ['False']:
    df_cancel_filter  = df_cancel_filter[~df_cancel_filter['assigned_room_status']]


assigned_room_status = st.sidebar.multiselect(
    "Deposit Type",
    options = ['No Deposit', 'Non Refund','Refundable'],
    default = ['No Deposit', 'Non Refund','Refundable']
)

if assigned_room_status == ['No Deposit']:
    df_cancel_filter  = df_cancel_filter[df_cancel_filter['deposit_type'] == "No Deposit"]
elif assigned_room_status == ['Non Refund']:
    df_cancel_filter  = df_cancel_filter[df_cancel_filter['deposit_type'] == "Non Refund"]
elif assigned_room_status == ['Refundable']:
    df_cancel_filter  = df_cancel_filter[df_cancel_filter['deposit_type'] == "Refundable"]




# create column partition for Cards
card1,card2,card3,card4,card5 = st.columns(5)

with card1:
    st.metric("Average ADR",round(df_cancel_filter["adr"].mean(),2))
with card2:
    st.metric("Total Orders",df_cancel_filter['adr'].count())
with card3:
    booked_data_ration = round((len(df_cancel_filter[df_cancel_filter["is_canceled"] == 0])) / (len(df_cancel_filter)),2)
    st.metric("Booked Data Ratio",booked_data_ration)
with card4:
    st.metric("Total Countries",df_cancel_filter['country'].nunique())
with card5:
    st.metric("Avg ADR", round(df_cancel_filter['adr'].mean(),2))



assigned_room_status,cancellation_chart , repeated_customers_chart, deposit_type_chart = st.columns(4)

with assigned_room_status:
    assigned_room_status_group_data = make_grouping(df_cancel_filter,'assigned_room_status','adults','count')
    fig = px.pie(assigned_room_status_group_data, names='assigned_room_status', values='count', title='Assigned Room Status Chart',hole = 0.6)
    fig.update_traces(texttemplate='%{percent:.1%}')

    # Display in Streamlit
    st.plotly_chart(fig)

with cancellation_chart:
    cancelation_group_data = make_grouping(df_cancel_filter,"is_canceled",'adults','count')
    fig = px.pie(cancelation_group_data, names='is_canceled', values='count', title='Cancelation Status Chart',hole = 0.6)
    fig.update_traces(texttemplate='%{percent:.1%}')
    
    # Display in Streamlit
    st.plotly_chart(fig)

with repeated_customers_chart:
    repeated_customers_group_data = make_grouping(df_cancel_filter,"is_repeated_guest","adults","count")
    
    
    # Create pie chart
    fig = px.pie(repeated_customers_group_data, names='is_repeated_guest', values='count', title='Repeated Customers Chart',hole = 0.6)
    fig.update_traces(texttemplate='%{percent:.1%}')

    # Display in Streamlit
    st.plotly_chart(fig)


with deposit_type_chart:
    deposit_type_group_data = make_grouping(df_cancel_filter,"deposit_type",'adults','count')
    fig = px.pie(deposit_type_group_data, names='deposit_type', values='count', title='Deposit Type Chart',hole = 0.6)
    fig.update_traces(texttemplate='%{percent:.1%}')
    
    # Display in Streamlit
    st.plotly_chart(fig)



# create column partition for charts
meal_chart_area, market_segment_chart_area,customer_type_chart_area  = st.columns(3)

with meal_chart_area:
    meal_group_data = make_grouping(df_cancel_filter,"meal",'adults','count')
    
    # Create pie chart
    fig = px.pie(meal_group_data, names='meal', values='count', title='Market Segment Booking Share',hole = 0.6)
    fig.update_traces(texttemplate='%{percent:.1%}',rotation = 90)
    # Display in Streamlit
    st.plotly_chart(fig)
    
with market_segment_chart_area:
    market_segment_group_data = make_grouping(df_cancel_filter,"market_segment",'adults','count')
    # Create pie chart
    fig = px.pie(market_segment_group_data, names='market_segment', values='count', title='Market Segment Booking Share',hole = 0.6)
    fig.update_traces(texttemplate='%{percent:.1%}')

    # Display in Streamlit
    st.plotly_chart(fig)

with customer_type_chart_area:
    customer_type_group_data = make_grouping(df_cancel_filter,"customer_type",'adults','count')

    # Create pie chart
    fig = px.pie(customer_type_group_data, names='customer_type', values='count', title='Customer Type Booking Share',hole = 0.6)
    fig.update_traces(texttemplate='%{percent:.1%}',rotation = 90)

    # Display in Streamlit
    st.plotly_chart(fig)



st.title("Countries Wise Bookings")


country_wise_chart, country_wise_data = st.columns([2,3])

with country_wise_chart:

    country_grouped_data = make_grouping(df_cancel_filter,"country","hotel",'count')
    col1, col2 = st.columns(2)
    with col1:
        sort_value = st.selectbox(
            "Data Category",
            options = ['Top',"Bottom"],
            index = 0
        )

    if sort_value == "Top":
        sort_country_grouped_data = country_grouped_data.sort_values(by = ['count'], ascending = False).reset_index(drop = True)
    else:
        sort_country_grouped_data = country_grouped_data.sort_values(by = ['count'], ascending = True).reset_index(drop = True)

    with col2:
        selected_rows = st.number_input(label = "Choose Number of Rows",min_value = 5,value = 5,max_value = country_grouped_data.shape[0])

    # Create pie chart
    fig = px.pie(sort_country_grouped_data.iloc[:selected_rows], names='country', values='count',hole = 0.6)

    # Display in Streamlit
    st.plotly_chart(fig,use_container_width = True)

with country_wise_data:

    if hotel_type == ["Resort Hotel"]:
        cancel_df_cancel_filter = make_hotel_col_filter(cancel_booking,'hotel',"Resort Hotel")
    elif hotel_type == ["City Hotel"]:
        cancel_df_cancel_filter = make_hotel_col_filter(cancel_booking,'hotel',"City Hotel")
    else:
        cancel_df_cancel_filter = cancel_booking.copy()


    cancel_booking_country_group_data = make_grouping(cancel_df_cancel_filter,"country","is_canceled","count")           # cancelation group data by countries
    booking_country_group_data = make_grouping(df,'country',"is_canceled",'count')
    cancelation_by_country_data = pd.merge(cancel_booking_country_group_data,booking_country_group_data,on = "country").reset_index(drop = True)
    cancelation_by_country_data['rate %'] = round((cancelation_by_country_data['count_x'] / cancelation_by_country_data['count_y']) * 100,1)
    cancelation_by_country_data.rename(columns={"count_x":"Total_Cancelation","count_y":"Total_Bookings"},inplace = True)
    st.dataframe(cancelation_by_country_data,use_container_width = True,height = 492)  


st.title("Line Chart")


@st.cache_data
def new_group_func(data,group_col,col_name,**kwargs):
    data = data.groupby(group_col,as_index = False).agg(kwargs)
    for i,j in zip(kwargs,col_name):
        data.rename(columns = {i:j},inplace = True)
    return data.sort_values(by = 'arrival_month_num')




month_wise_cancel_booking = new_group_func(filter_df[filter_df['is_canceled'] == 1],['arrival_date_month','arrival_month_num'],["total_customers","avg_adr"],customer_type = "count",adr = "mean")
month_wise_not_cancel_booking = new_group_func(filter_df[filter_df['is_canceled'] == 0],['arrival_date_month','arrival_month_num'],["total_customers","avg_adr"],customer_type = "count",adr = "mean")

month_wise_total_booking = new_group_func(filter_df,['arrival_date_month','arrival_month_num'],['total_booking'],customer_type = "count")

merge_data = pd.merge(month_wise_cancel_booking,month_wise_total_booking,on = ["arrival_date_month","arrival_month_num"])
merge_data['cancelation_rate'] = round((merge_data['total_customers'] / merge_data['total_booking']) * 100,2)
merge_data['not_cancelation_rate'] = 100 - merge_data['cancelation_rate']

rating_data = merge_data[['arrival_date_month','avg_adr','cancelation_rate','not_cancelation_rate']]


# Add a label to identify booking status
month_wise_cancel_booking["Booking_Status"] = "Canceled"
month_wise_not_cancel_booking["Booking_Status"] = "Not Canceled"

# Combine both into a single DataFrame
combined_df = pd.concat([month_wise_cancel_booking, month_wise_not_cancel_booking])

# ================================
# Line Chart 1: Total Customers
# ================================

# 📈 Line Chart for Total Customers
fig1 = px.line(
    combined_df,
    x="arrival_date_month",
    y="total_customers",
    color="Booking_Status",
    markers=True,
    title="Total Customers by Month (Canceled vs Not Canceled)"
)


# ================================
# Line Chart 2: Average ADR
# ================================
# 📈 Line Chart for Average ADR
fig2 = px.line(
    combined_df,
    x="arrival_date_month",
    y="avg_adr",
    color="Booking_Status",
    markers=True,
    title="Average ADR by Month (Canceled vs Not Canceled)"
)


# Display in Streamlit
st.plotly_chart(fig1, use_container_width=True)
st.plotly_chart(fig2, use_container_width=True)


# Select only numeric columns for correlation
numeric_df = rating_data.select_dtypes(include='number') 

# Calculate correlation matrix
corr_matrix = numeric_df.corr()

# Create heatmap
fig = px.imshow(corr_matrix,
                text_auto=True,
                color_continuous_scale='RdBu_r',
                zmin=-1, zmax=1,
                labels=dict(x="Features", y="Features", color="Correlation"))

fig.update_layout(title="Feature Correlation Heatmap",
                  xaxis_title="Features",
                  yaxis_title="Features")
st.plotly_chart(fig, use_container_width=True)

