import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Coffee Shop Sales Forecast Dashboard",
    page_icon="☕",
    layout="wide"
)


# ============================================================
# TITLE
# ============================================================

st.title("☕ Coffee Shop Sales Forecast Dashboard")


# ============================================================
# LOCAL FILE PATHS
# ============================================================
# IMPORTANT:
# These files must be in the same GitHub repository/folder
# as app.py.

DAILY_QUANTITY_FILE = "daily_quantity_forecast.csv"
DAILY_REVENUE_FILE = "daily_revenue_forecast.csv"
HOURLY_QUANTITY_FILE = "hourly_quantity_forecast.csv"
HOURLY_REVENUE_FILE = "hourly_revenue_forecast.csv"


# ============================================================
# CHECK FILES
# ============================================================

import os

required_files = [
    DAILY_QUANTITY_FILE,
    DAILY_REVENUE_FILE,
    HOURLY_QUANTITY_FILE,
    HOURLY_REVENUE_FILE
]

missing_files = [
    file for file in required_files
    if not os.path.exists(file)
]

if missing_files:

    st.error("Some forecast files are missing from the repository.")

    st.write("Missing files:")

    for file in missing_files:
        st.write("•", file)

    st.info(
        "Please upload these CSV files to the same GitHub repository "
        "where app.py is located."
    )

    st.stop()


# ============================================================
# LOAD FORECAST DATA
# ============================================================

@st.cache_data
def load_forecast_data():

    daily_quantity = pd.read_csv(
        DAILY_QUANTITY_FILE
    )

    daily_revenue = pd.read_csv(
        DAILY_REVENUE_FILE
    )

    hourly_quantity = pd.read_csv(
        HOURLY_QUANTITY_FILE
    )

    hourly_revenue = pd.read_csv(
        HOURLY_REVENUE_FILE
    )

    return (
        daily_quantity,
        daily_revenue,
        hourly_quantity,
        hourly_revenue
    )


(
    daily_quantity,
    daily_revenue,
    hourly_quantity,
    hourly_revenue
) = load_forecast_data()


# ============================================================
# STANDARDIZE COLUMN NAMES
# ============================================================

def standardize_columns(df):

    df = df.copy()

    df.columns = [
        str(column).strip()
        for column in df.columns
    ]

    return df


daily_quantity = standardize_columns(
    daily_quantity
)

daily_revenue = standardize_columns(
    daily_revenue
)

hourly_quantity = standardize_columns(
    hourly_quantity
)

hourly_revenue = standardize_columns(
    hourly_revenue
)


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def get_store_column(df):

    possible = [
        "Store",
        "store",
        "store_location",
        "Store Location"
    ]

    for column in possible:

        if column in df.columns:
            return column

    return None


def get_date_column(df):

    possible = [
        "Date",
        "date",
        "Datetime",
        "DateTime",
        "datetime"
    ]

    for column in possible:

        if column in df.columns:
            return column

    return None


def get_prediction_column(df, metric):

    if metric == "Quantity":

        possible = [
            "Predicted_quantity",
            "Predicted Quantity",
            "Predicted_qty",
            "Predicted_Hourly_Quantity",
            "prediction",
            "Prediction"
        ]

    else:

        possible = [
            "Predicted_revenue",
            "Predicted Revenue",
            "Predicted_Hourly_Revenue",
            "prediction",
            "Prediction"
        ]

    for column in possible:

        if column in df.columns:
            return column

    # Fallback search
    for column in df.columns:

        name = str(column).lower()

        if "predicted" in name:

            return column

    return None


def get_lower_column(df):

    possible = [
        "Lower_95",
        "lower_95",
        "lower_bound",
        "Lower Bound"
    ]

    for column in possible:

        if column in df.columns:
            return column

    return None


def get_upper_column(df):

    possible = [
        "Upper_95",
        "upper_95",
        "upper_bound",
        "Upper Bound"
    ]

    for column in possible:

        if column in df.columns:
            return column

    return None


# ============================================================
# CHECK STORE COLUMN
# ============================================================

dq_store_col = get_store_column(
    daily_quantity
)

if dq_store_col is None:

    st.error(
        "Store column was not found in daily quantity data."
    )

    st.write(
        daily_quantity.columns.tolist()
    )

    st.stop()


# ============================================================
# GET STORES
# ============================================================

stores = sorted(
    daily_quantity[dq_store_col]
    .dropna()
    .astype(str)
    .unique()
    .tolist()
)


if len(stores) == 0:

    st.error("No stores were found.")

    st.stop()


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.header(
    "☕ Dashboard Controls"
)


# ============================================================
# STORE SELECTOR
# ============================================================

st.sidebar.subheader(
    "Select Store"
)

selected_store = st.sidebar.radio(
    "Store",
    stores,
    index=0
)


# ============================================================
# FORECAST HORIZON
# ============================================================

st.sidebar.subheader(
    "Forecast Horizon"
)

forecast_horizon = st.sidebar.select_slider(
    "Forecast Horizon Days",
    options=[7, 14, 30],
    value=30
)


# ============================================================
# METRIC
# ============================================================

st.sidebar.subheader(
    "Metric"
)

metric = st.sidebar.radio(
    "Metric",
    ["Quantity", "Revenue"],
    index=0
)


# ============================================================
# SELECT DATA
# ============================================================

if metric == "Quantity":

    daily_data = daily_quantity
    hourly_data = hourly_quantity

else:

    daily_data = daily_revenue
    hourly_data = hourly_revenue


# ============================================================
# STORE COLUMNS
# ============================================================

store_col = get_store_column(
    daily_data
)

hourly_store_col = get_store_column(
    hourly_data
)


if store_col is None:

    st.error(
        f"Store column was not found in {metric} daily data."
    )

    st.stop()


if hourly_store_col is None:

    st.error(
        f"Store column was not found in {metric} hourly data."
    )

    st.stop()


# ============================================================
# FILTER SELECTED STORE
# ============================================================

daily_store = daily_data[
    daily_data[store_col].astype(str)
    == str(selected_store)
].copy()


hourly_store = hourly_data[
    hourly_data[hourly_store_col].astype(str)
    == str(selected_store)
].copy()


# ============================================================
# PREDICTION COLUMNS
# ============================================================

daily_pred_col = get_prediction_column(
    daily_store,
    metric
)

hourly_pred_col = get_prediction_column(
    hourly_store,
    metric
)


if daily_pred_col is None:

    st.error(
        "Daily prediction column was not found."
    )

    st.write(
        daily_store.columns.tolist()
    )

    st.stop()


if hourly_pred_col is None:

    st.error(
        "Hourly prediction column was not found."
    )

    st.write(
        hourly_store.columns.tolist()
    )

    st.stop()


# ============================================================
# DATE COLUMNS
# ============================================================

daily_date_col = get_date_column(
    daily_store
)

hourly_date_col = get_date_column(
    hourly_store
)


if daily_date_col is not None:

    daily_store[daily_date_col] = pd.to_datetime(
        daily_store[daily_date_col],
        errors="coerce"
    )

    daily_store = daily_store.sort_values(
        daily_date_col
    )


if hourly_date_col is not None:

    hourly_store[hourly_date_col] = pd.to_datetime(
        hourly_store[hourly_date_col],
        errors="coerce"
    )

    hourly_store = hourly_store.sort_values(
        hourly_date_col
    )


# ============================================================
# SUCCESS MESSAGE
# ============================================================

st.success(
    f"Forecast available for: {selected_store}"
)


# ============================================================
# DAILY FORECAST
# ============================================================

st.header(
    f"📦 {forecast_horizon}-Day Daily {metric} Forecast"
)


daily_display = daily_store.head(
    forecast_horizon
).copy()


# ============================================================
# DAILY CHART
# ============================================================

if daily_date_col is not None:

    chart_data = daily_display[
        [daily_date_col, daily_pred_col]
    ].copy()

    chart_data[daily_pred_col] = pd.to_numeric(
        chart_data[daily_pred_col],
        errors="coerce"
    )

    chart_data = chart_data.set_index(
        daily_date_col
    )

    chart_data.columns = [
        f"Predicted {metric}"
    ]

    st.line_chart(
        chart_data,
        use_container_width=True
    )


# ============================================================
# DAILY TABLE
# ============================================================

st.subheader(
    "Daily Forecast Values"
)


display_cols = []

if daily_date_col is not None:

    display_cols.append(
        daily_date_col
    )

display_cols.append(
    daily_pred_col
)


table = daily_display[
    display_cols
].copy()


if daily_date_col is not None:

    table.columns = [
        "Date",
        f"Predicted {metric}"
    ]

else:

    table.columns = [
        f"Predicted {metric}"
    ]


st.dataframe(
    table,
    use_container_width=True,
    hide_index=True
)


# ============================================================
# HOURLY FORECAST
# ============================================================

st.header(
    f"🕐 Next 24 Hours {metric} Forecast"
)


hourly_display = hourly_store.head(
    24
).copy()


if hourly_date_col is not None:

    hourly_chart = hourly_display[
        [hourly_date_col, hourly_pred_col]
    ].copy()

    hourly_chart[hourly_pred_col] = pd.to_numeric(
        hourly_chart[hourly_pred_col],
        errors="coerce"
    )

    hourly_chart = hourly_chart.set_index(
        hourly_date_col
    )

    hourly_chart.columns = [
        f"Predicted {metric}"
    ]

    st.line_chart(
        hourly_chart,
        use_container_width=True
    )


# ============================================================
# HOURLY DEMAND HEATMAP
# ============================================================

st.header(
    f"🔥 Hourly Demand Heatmap - {metric}"
)


heatmap_data = hourly_data.copy()

heatmap_store_col = get_store_column(
    heatmap_data
)


if metric == "Quantity":

    hourly_value_col = "Predicted_Hourly_Quantity"

else:

    hourly_value_col = "Predicted_Hourly_Revenue"


if hourly_value_col not in heatmap_data.columns:

    st.error(
        f"Column '{hourly_value_col}' was not found."
    )

    st.write(
        "Available hourly columns:",
        list(heatmap_data.columns)
    )

else:

    if "Datetime" not in heatmap_data.columns:

        st.error(
            "Datetime column was not found in hourly data."
        )

    else:

        heatmap_data["Datetime"] = pd.to_datetime(
            heatmap_data["Datetime"],
            errors="coerce"
        )

        heatmap_data = heatmap_data.dropna(
            subset=["Datetime"]
        )

        heatmap_data["Hour"] = (
            heatmap_data["Datetime"].dt.hour
        )

        heatmap_pivot = heatmap_data.pivot_table(
            index=heatmap_store_col,
            columns="Hour",
            values=hourly_value_col,
            aggfunc="mean"
        )

        heatmap_pivot = heatmap_pivot.reindex(
            columns=range(24)
        )

        fig, ax = plt.subplots(
            figsize=(14, 4.5)
        )

        im = ax.imshow(
            heatmap_pivot.values,
            aspect="auto"
        )

        ax.set_xticks(
            range(24)
        )

        ax.set_xticklabels(
            [f"{h:02d}:00" for h in range(24)],
            rotation=45
        )

        ax.set_yticks(
            range(len(heatmap_pivot.index))
        )

        ax.set_yticklabels(
            heatmap_pivot.index
        )

        ax.set_xlabel(
            "Hour of Day"
        )

        ax.set_ylabel(
            "Store"
        )

        ax.set_title(
            f"Hourly Predicted {metric} by Store"
        )

        cbar = fig.colorbar(
            im,
            ax=ax
        )

        cbar.set_label(
            f"Predicted {metric}"
        )

        plt.tight_layout()

        st.pyplot(
            fig,
            use_container_width=True
        )

        st.subheader(
            "Hourly Forecast Heatmap Data"
        )

        display_heatmap = heatmap_pivot.copy()

        display_heatmap.columns = [
            f"{h:02d}:00"
            for h in display_heatmap.columns
        ]

        st.dataframe(
            display_heatmap,
            use_container_width=True
        )


# ============================================================
# TOP 10 PEAK DAYS
# ============================================================

st.header(
    f"🔥 Top 10 Peak Days - {metric}"
)


daily_store[daily_pred_col] = pd.to_numeric(
    daily_store[daily_pred_col],
    errors="coerce"
)


peak_days = daily_store.sort_values(
    by=daily_pred_col,
    ascending=False
).head(10).copy()


peak_display_cols = []

if daily_date_col is not None:

    peak_display_cols.append(
        daily_date_col
    )

peak_display_cols.append(
    daily_pred_col
)


peak_table = peak_days[
    peak_display_cols
].copy()


if daily_date_col is not None:

    peak_table.columns = [
        "Date",
        f"Predicted {metric}"
    ]

else:

    peak_table.columns = [
        f"Predicted {metric}"
    ]


st.dataframe(
    peak_table,
    use_container_width=True,
    hide_index=True
)


# ============================================================
# TOP 10 BAR CHART
# ============================================================

if daily_date_col is not None:

    peak_chart = peak_days[
        [daily_date_col, daily_pred_col]
    ].copy()

    peak_chart[daily_date_col] = (
        peak_chart[daily_date_col]
        .dt.strftime("%d-%b")
    )

    peak_chart = peak_chart.set_index(
        daily_date_col
    )

    peak_chart.columns = [
        f"Predicted {metric}"
    ]

    st.bar_chart(
        peak_chart,
        use_container_width=True
    )


# ============================================================
# 95% PREDICTION INTERVAL
# ============================================================

st.header(
    f"📈 95% Prediction Interval - {metric}"
)

st.info(
    "The shaded region represents the estimated 95% prediction "
    "interval around the forecast."
)


lower_col = get_lower_column(
    daily_store
)

upper_col = get_upper_column(
    daily_store
)


if (
    lower_col is None
    or upper_col is None
    or daily_date_col is None
):

    st.warning(
        "95% prediction interval columns were not found, "
        "so the prediction interval chart cannot be displayed."
    )

else:

    interval_data = daily_store.copy()

    interval_data["Forecast"] = pd.to_numeric(
        interval_data[daily_pred_col],
        errors="coerce"
    )

    interval_data["Lower 95%"] = pd.to_numeric(
        interval_data[lower_col],
        errors="coerce"
    )

    interval_data["Upper 95%"] = pd.to_numeric(
        interval_data[upper_col],
        errors="coerce"
    )

    interval_data = interval_data.dropna(
        subset=[
            "Forecast",
            "Lower 95%",
            "Upper 95%"
        ]
    )

    interval_data["Lower 95%"] = (
        interval_data["Lower 95%"].clip(
            lower=0
        )
    )

    interval_data = interval_data.head(
        forecast_horizon
    )

    fig_interval = go.Figure()

    # Upper bound
    fig_interval.add_trace(
        go.Scatter(
            x=interval_data[daily_date_col],
            y=interval_data["Upper 95%"],
            mode="lines",
            line=dict(width=0),
            name="Upper 95%"
        )
    )

    # Lower bound and shaded area
    fig_interval.add_trace(
        go.Scatter(
            x=interval_data[daily_date_col],
            y=interval_data["Lower 95%"],
            mode="lines",
            line=dict(width=0),
            fill="tonexty",
            fillcolor="rgba(100, 149, 237, 0.20)",
            name="95% Prediction Interval"
        )
    )

    # Forecast line
    fig_interval.add_trace(
        go.Scatter(
            x=interval_data[daily_date_col],
            y=interval_data["Forecast"],
            mode="lines+markers",
            name=f"Forecast {metric}",
            line=dict(width=3)
        )
    )

    fig_interval.update_layout(
        title=(
            f"{forecast_horizon}-Day {metric} Forecast "
            f"with 95% Prediction Interval"
        ),
        xaxis_title="Forecast Date",
        yaxis_title=f"Predicted {metric}",
        template="plotly_white",
        hovermode="x unified",
        height=500,
        legend_title="Forecast"
    )

    st.plotly_chart(
        fig_interval,
        use_container_width=True
    )

    # Interval table
    st.subheader(
        "📋 Forecast and Prediction Interval Values"
    )

    interval_table = interval_data[
        [
            daily_date_col,
            "Forecast",
            "Lower 95%",
            "Upper 95%"
        ]
    ].copy()

    interval_table.columns = [
        "Date",
        f"Forecast {metric}",
        "Lower 95%",
        "Upper 95%"
    ]

    st.dataframe(
        interval_table,
        use_container_width=True,
        hide_index=True
    )


# ============================================================
# MODEL SELECTION & COMPARISON
# ============================================================

st.header(
    "📊 Model Selection & Comparison"
)

st.info(
    "Models are compared using MAE, RMSE, MAPE and R² "
    "calculated on the test set. Lower MAE, RMSE and MAPE "
    "indicate better performance, while higher R² is better."
)


performance_quantity = pd.DataFrame({

    "Model": [
        "Naive Forecast",
        "Moving Average",
        "ARIMA",
        "Gradient Boosting"
    ],

    "MAE": [
        120.533333,
        184.133333,
        213.264924,
        86.118527
    ],

    "RMSE": [
        161.566498,
        217.610049,
        245.184511,
        99.875346
    ],

    "MAPE": [
        7.202985,
        10.413888,
        12.101788,
        5.114135
    ],

    "R2": [
        -0.596103,
        -1.895452,
        -2.675737,
        0.390077
    ]
})


performance_revenue = pd.DataFrame({

    "Model": [
        "Naive",
        "Moving Average (3-Day)",
        "ARIMA",
        "Gradient Boosting"
    ],

    "MAE": [
        347.536333,
        3854.662667,
        859.546914,
        406.723246
    ],

    "RMSE": [
        488.858524,
        3882.370632,
        979.298067,
        462.837091
    ],

    "MAPE": [
        6.336938,
        69.273002,
        14.836441,
        7.435332
    ],

    "R2": [
        0.059701,
        -58.305321,
        -2.773371,
        0.157139
    ]
})


if metric == "Quantity":

    st.subheader(
        "☕ Quantity Forecast - Model Comparison"
    )

    st.dataframe(
        performance_quantity.style.format({
            "MAE": "{:.2f}",
            "RMSE": "{:.2f}",
            "MAPE": "{:.2f}%",
            "R2": "{:.2f}"
        }),
        use_container_width=True,
        hide_index=True
    )

    best_quantity = performance_quantity.loc[
        performance_quantity["MAPE"].idxmin()
    ]

    st.success(
        f"🏆 Best Quantity Model: **{best_quantity['Model']}**\n\n"
        f"MAE: **{best_quantity['MAE']:.2f}** | "
        f"RMSE: **{best_quantity['RMSE']:.2f}** | "
        f"MAPE: **{best_quantity['MAPE']:.2f}%** | "
        f"R²: **{best_quantity['R2']:.2f}**"
    )


else:

    st.subheader(
        "💰 Revenue Forecast - Model Comparison"
    )

    st.dataframe(
        performance_revenue.style.format({
            "MAE": "{:.2f}",
            "RMSE": "{:.2f}",
            "MAPE": "{:.2f}%",
            "R2": "{:.2f}"
        }),
        use_container_width=True,
        hide_index=True
    )

    best_revenue = performance_revenue.loc[
        performance_revenue["MAPE"].idxmin()
    ]

    st.success(
        f"🏆 Best Revenue Model: **{best_revenue['Model']}**\n\n"
        f"MAE: **{best_revenue['MAE']:.2f}** | "
        f"RMSE: **{best_revenue['RMSE']:.2f}** | "
        f"MAPE: **{best_revenue['MAPE']:.2f}%** | "
        f"R²: **{best_revenue['R2']:.2f}**"
    )


# ============================================================
# BUSINESS INSIGHTS & DECISION SUPPORT
# ============================================================

st.header(
    "💡 Business Insights & Decision Support"
)

st.info(
    "This section converts forecast results into actionable "
    "insights for store operations, staffing and inventory planning."
)


# ============================================================
# SELECT BUSINESS INSIGHT DATA
# ============================================================

selected_daily = daily_data.copy()
selected_hourly = hourly_data.copy()


if metric == "Quantity":

    daily_value_col = "Predicted_quantity"
    hourly_value_col = "Predicted_Hourly_Quantity"

    metric_title = "Quantity"
    metric_unit = "units"

else:

    daily_value_col = "Predicted_revenue"
    hourly_value_col = "Predicted_Hourly_Revenue"

    metric_title = "Revenue"
    metric_unit = "revenue"


# ============================================================
# VALIDATE BUSINESS DATA
# ============================================================

if (
    "Date" not in selected_daily.columns
    or "Store" not in selected_daily.columns
    or daily_value_col not in selected_daily.columns
):

    st.warning(
        f"Required columns for {metric_title} business insights "
        "were not found."
    )

else:

    selected_daily["Date"] = pd.to_datetime(
        selected_daily["Date"],
        errors="coerce"
    )

    selected_daily[daily_value_col] = pd.to_numeric(
        selected_daily[daily_value_col],
        errors="coerce"
    )

    selected_daily = selected_daily.dropna(
        subset=[
            "Date",
            daily_value_col
        ]
    )


    # ========================================================
    # EXECUTIVE FORECAST KPIs
    # ========================================================

    st.subheader(
        "📌 Forecast Overview"
    )

    total_forecast = (
        selected_daily[daily_value_col].sum()
    )

    average_daily = (
        selected_daily[daily_value_col].mean()
    )

    top_store_data = (
        selected_daily
        .groupby("Store")[daily_value_col]
        .sum()
        .sort_values(
            ascending=False
        )
    )

    top_store = top_store_data.index[0]

    top_store_value = top_store_data.iloc[0]

    number_of_stores = (
        selected_daily["Store"].nunique()
    )


    # ========================================================
    # KPI CARDS
    # ========================================================

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.metric(
            f"Total Forecast {metric_title}",
            f"{total_forecast:,.0f}"
        )

    with col2:

        st.metric(
            f"Average Daily {metric_title}",
            f"{average_daily:,.1f}"
        )

    with col3:

        st.metric(
            "Top Store",
            top_store
        )

    with col4:

        st.metric(
            "Stores Covered",
            number_of_stores
        )


    # ========================================================
    # STORE PERFORMANCE
    # ========================================================

    st.subheader(
        f"🏪 Store-wise Forecast {metric_title}"
    )

    store_summary = (
        selected_daily
        .groupby("Store")[daily_value_col]
        .sum()
        .reset_index()
        .sort_values(
            daily_value_col,
            ascending=False
        )
    )

    fig_store = px.bar(
        store_summary,
        x="Store",
        y=daily_value_col,
        text_auto=".1f",
        title=f"Forecast {metric_title} by Store",
        labels={
            daily_value_col: metric_title,
            "Store": "Store"
        }
    )

    fig_store.update_layout(
        template="plotly_white",
        height=450,
        hovermode="x unified"
    )

    st.plotly_chart(
        fig_store,
        use_container_width=True
    )


    # ========================================================
    # STORE CONTRIBUTION
    # ========================================================

    store_summary["Contribution (%)"] = (
        store_summary[daily_value_col]
        / store_summary[daily_value_col].sum()
        * 100
    )

    st.subheader(
        "Store Contribution"
    )

    contribution_display = store_summary.copy()

    contribution_display[daily_value_col] = (
        contribution_display[daily_value_col]
        .round(2)
    )

    contribution_display["Contribution (%)"] = (
        contribution_display["Contribution (%)"]
        .round(2)
    )

    contribution_display = contribution_display.rename(
        columns={
            daily_value_col:
            f"Forecast {metric_title}"
        }
    )

    st.dataframe(
        contribution_display,
        use_container_width=True,
        hide_index=True
    )


    # ========================================================
    # DAILY FORECAST TREND
    # ========================================================

    st.subheader(
        f"📈 Daily Forecast Trend - {metric_title}"
    )

    daily_trend = (
        selected_daily
        .groupby("Date")[daily_value_col]
        .sum()
        .reset_index()
    )

    fig_daily = px.line(
        daily_trend,
        x="Date",
        y=daily_value_col,
        markers=True,
        title=f"Total Daily Forecast {metric_title}",
        labels={
            daily_value_col: metric_title,
            "Date": "Forecast Date"
        }
    )

    fig_daily.update_layout(
        template="plotly_white",
        height=420,
        hovermode="x unified"
    )

    st.plotly_chart(
        fig_daily,
        use_container_width=True
    )


    # ========================================================
    # HOURLY BUSINESS ANALYSIS
    # ========================================================

    peak_hour = None
    low_hour = None
    peak_value = None
    low_value = None

    if (
        "Datetime" in selected_hourly.columns
        and "Store" in selected_hourly.columns
        and hourly_value_col in selected_hourly.columns
    ):

        selected_hourly["Datetime"] = pd.to_datetime(
            selected_hourly["Datetime"],
            errors="coerce"
        )

        selected_hourly[hourly_value_col] = pd.to_numeric(
            selected_hourly[hourly_value_col],
            errors="coerce"
        )

        selected_hourly = selected_hourly.dropna(
            subset=[
                "Datetime",
                hourly_value_col
            ]
        )

        selected_hourly["Hour"] = (
            selected_hourly["Datetime"].dt.hour
        )


        # ====================================================
        # HOURLY DEMAND PROFILE
        # ====================================================

        st.subheader(
            f"⏰ Hourly Forecast Profile - {metric_title}"
        )

        hourly_profile = (
            selected_hourly
            .groupby("Hour")[hourly_value_col]
            .mean()
            .reset_index()
        )

        peak_row = hourly_profile.loc[
            hourly_profile[hourly_value_col].idxmax()
        ]

        low_row = hourly_profile.loc[
            hourly_profile[hourly_value_col].idxmin()
        ]

        peak_hour = int(
            peak_row["Hour"]
        )

        peak_value = peak_row[
            hourly_value_col
        ]

        low_hour = int(
            low_row["Hour"]
        )

        low_value = low_row[
            hourly_value_col
        ]


        fig_hour = px.line(
            hourly_profile,
            x="Hour",
            y=hourly_value_col,
            markers=True,
            title=f"Average Forecast {metric_title} by Hour",
            labels={
                "Hour": "Hour of Day",
                hourly_value_col:
                f"Forecast {metric_title}"
            }
        )

        fig_hour.update_xaxes(
            dtick=1
        )

        fig_hour.update_layout(
            template="plotly_white",
            height=420,
            hovermode="x unified"
        )

        st.plotly_chart(
            fig_hour,
            use_container_width=True
        )


        # ====================================================
        # PEAK / LOW DEMAND KPIs
        # ====================================================

        col1, col2 = st.columns(2)

        with col1:

            st.metric(
                "🔥 Peak Hour",
                f"{peak_hour:02d}:00",
                f"{peak_value:,.1f}"
            )

        with col2:

            st.metric(
                "⬇️ Lowest Hour",
                f"{low_hour:02d}:00",
                f"{low_value:,.1f}"
            )


        # ====================================================
        # STORE × HOUR HEATMAP
        # ====================================================

        st.subheader(
            f"🌡️ Store × Hour Forecast Intensity - {metric_title}"
        )

        heatmap_data_business = (
            selected_hourly
            .groupby(
                ["Store", "Hour"]
            )[hourly_value_col]
            .mean()
            .reset_index()
        )

        heatmap_pivot_business = (
            heatmap_data_business
            .pivot(
                index="Store",
                columns="Hour",
                values=hourly_value_col
            )
        )

        fig_heatmap = px.imshow(
            heatmap_pivot_business,
            aspect="auto",
            text_auto=".1f",
            title=(
                f"Forecast {metric_title} Intensity "
                f"by Store and Hour"
            ),
            labels={
                "x": "Hour of Day",
                "y": "Store",
                "color": metric_title
            }
        )

        fig_heatmap.update_layout(
            height=450,
            template="plotly_white"
        )

        st.plotly_chart(
            fig_heatmap,
            use_container_width=True
        )


        # ====================================================
        # STORE PEAK HOURS
        # ====================================================

        st.subheader(
            "🏪 Peak Operating Hours by Store"
        )

        store_hour_peak = (
            selected_hourly
            .groupby(
                ["Store", "Hour"]
            )[hourly_value_col]
            .mean()
            .reset_index()
        )

        peak_by_store = (
            store_hour_peak
            .loc[
                store_hour_peak
                .groupby("Store")[hourly_value_col]
                .idxmax()
            ]
            .sort_values(
                hourly_value_col,
                ascending=False
            )
        )

        peak_by_store_display = (
            peak_by_store.copy()
        )

        peak_by_store_display["Peak Hour"] = (
            peak_by_store_display["Hour"]
            .apply(
                lambda x:
                f"{int(x):02d}:00"
            )
        )

        peak_by_store_display = (
            peak_by_store_display[
                [
                    "Store",
                    "Peak Hour",
                    hourly_value_col
                ]
            ]
            .rename(
                columns={
                    hourly_value_col:
                    f"Forecast {metric_title}"
                }
            )
        )

        st.dataframe(
            peak_by_store_display,
            use_container_width=True,
            hide_index=True
        )


    # ========================================================
    # AUTOMATED BUSINESS INSIGHTS
    # ========================================================

    st.subheader(
        "🔎 Key Forecast Insights"
    )

    st.markdown(
        f"""
        **1. Store Performance:**  
        **{top_store}** has the highest expected
        {metric_title.lower()} contribution over the forecast
        period, with approximately **{top_store_value:,.1f}**
        forecast {metric_unit}.
        """
    )


    if len(store_summary) >= 2:

        second_store = (
            store_summary.iloc[1]["Store"]
        )

        second_value = (
            store_summary.iloc[1][daily_value_col]
        )

        difference = (
            top_store_value - second_value
        )

        st.markdown(
            f"""
            **2. Store Comparison:**  
            The difference between **{top_store}** and
            **{second_store}** is approximately
            **{difference:,.1f} {metric_unit}**, indicating
            different levels of expected operational demand.
            """
        )


    if peak_hour is not None:

        st.markdown(
            f"""
            **3. Peak Period:**  
            Forecast results indicate that **{peak_hour:02d}:00**
            is the highest-demand hour on average. This period
            should receive additional operational attention.
            """
        )

        st.markdown(
            f"""
            **4. Lower-Demand Period:**  
            Forecast demand is lowest around **{low_hour:02d}:00**.
            This period can potentially be used for routine
            activities such as restocking, cleaning and preparation.
            """
        )


    # ========================================================
    # RECOMMENDED BUSINESS ACTIONS
    # ========================================================

    st.subheader(
        "🎯 Recommended Business Actions"
    )

    if peak_hour is not None:

        staff_action = (
            f"Prioritize staff availability around the "
            f"forecast peak period of {peak_hour:02d}:00."
        )

        low_demand_action = (
            f"Use lower-demand periods such as approximately "
            f"{low_hour:02d}:00 for routine operational activities."
        )

    else:

        staff_action = (
            "Align staffing levels with forecast store demand."
        )

        low_demand_action = (
            "Use lower-demand periods for routine operational activities."
        )


    recommendations = [

        (
            "Staff Planning",
            staff_action
        ),

        (
            "Inventory Planning",
            "Prepare inventory ahead of periods with elevated "
            "forecast demand to reduce stock-out risk."
        ),

        (
            "Store-level Allocation",
            f"Prioritize operational resources for {top_store}, "
            f"which has the highest forecast "
            f"{metric_title.lower()}."
        ),

        (
            "Low-demand Operations",
            low_demand_action
        ),

        (
            "Forecast Monitoring",
            "Continuously compare future actual sales with "
            "forecasts and retrain models when forecast "
            "performance declines."
        )
    ]


    for title, description in recommendations:

        st.markdown(
            f"""
            **{title}**  
            {description}
            """
        )


    # ========================================================
    # MANAGEMENT SUMMARY
    # ========================================================

    st.subheader(
        "📋 Management Summary"
    )

    if peak_hour is not None:

        summary_text = (
            f"The {metric_title.lower()} forecasting analysis "
            f"indicates that {top_store} is expected to contribute "
            f"the highest forecast {metric_title.lower()} during "
            f"the selected forecast period. The strongest hourly "
            f"demand is expected around {peak_hour:02d}:00, while "
            f"demand is comparatively lower around {low_hour:02d}:00. "
            f"These forecast patterns can support staffing, "
            f"inventory preparation and store-level operational planning."
        )

    else:

        summary_text = (
            f"The {metric_title.lower()} forecasting analysis "
            f"indicates that {top_store} is expected to contribute "
            f"the highest forecast {metric_title.lower()} during "
            f"the selected forecast period. These results can "
            f"support store-level staffing, inventory and "
            f"operational planning."
        )

    st.success(
        summary_text
    )


# ============================================================
# FOOTER
# ============================================================

st.markdown("---")

st.caption(
    "Coffee Shop Sales Forecast Dashboard | "
    "Daily and hourly forecasting"
)