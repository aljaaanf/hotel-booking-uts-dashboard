
from pathlib import Path
import pandas as pd
import plotly.express as px
import streamlit as st

# ============================================================
# 1. KONFIGURASI DASHBOARD
# ============================================================
st.set_page_config(
    page_title="Hotel Booking Demand Dashboard",
    page_icon="🏨",
    layout="wide",
    initial_sidebar_state="expanded",
)

ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"

MONTHS = [
    "January", "February", "March", "April",
    "May", "June", "July", "August",
    "September", "October", "November", "December"
]

st.markdown("""
<style>
.stApp {
    background-color: #f5f7fb;
}
.block-container {
    padding-top: 1.6rem;
    padding-bottom: 2rem;
}
[data-testid="stMetric"] {
    background: #ffffff;
    padding: 17px 18px;
    border-radius: 13px;
    border: 1px solid #e5eaf2;
    box-shadow: 0 2px 8px rgba(20,40,80,.04);
}
[data-testid="stMetricLabel"] {
    color: #596579;
}
div[data-testid="stAlert"] {
    border-radius: 10px;
}
h1, h2, h3 {
    color: #252b3a;
}
</style>
""", unsafe_allow_html=True)


# ============================================================
# 2. MEMUAT DAN MEMBERSIHKAN DATA
# ============================================================
@st.cache_data(show_spinner="Sedang membaca dataset...")
def load_data():

    candidates = [
        DATA_DIR / "hotel_bookings_clean.csv",
        DATA_DIR / "hotel_bookings.csv",
    ]

    file_path = next(
        (path for path in candidates if path.exists()),
        None
    )

    if file_path is None:
        return None, None

    data = pd.read_csv(file_path, low_memory=False)

    data.columns = [
        str(col).strip().lower().replace(" ", "_")
        for col in data.columns
    ]

    required = [
        "hotel",
        "is_canceled",
        "lead_time",
        "arrival_date_year",
        "arrival_date_month",
        "adults",
        "children",
        "babies",
        "adr",
        "stays_in_weekend_nights",
        "stays_in_week_nights",
        "market_segment",
        "customer_type",
    ]

    missing = [
        col for col in required
        if col not in data.columns
    ]

    if missing:
        raise ValueError(
            "Kolom wajib tidak ditemukan: " + ", ".join(missing)
        )

    numeric_cols = [
        "is_canceled",
        "lead_time",
        "arrival_date_year",
        "adults",
        "children",
        "babies",
        "adr",
        "stays_in_weekend_nights",
        "stays_in_week_nights",
    ]

    for col in numeric_cols:
        data[col] = pd.to_numeric(
            data[col],
            errors="coerce"
        )

    data = data.dropna(
        subset=[
            "hotel",
            "is_canceled",
            "arrival_date_year",
            "arrival_date_month",
            "adr",
        ]
    ).copy()

    data["is_canceled"] = data["is_canceled"].astype(int)
    data["arrival_date_year"] = (
        data["arrival_date_year"].astype(int)
    )

    data["arrival_date_month"] = (
        data["arrival_date_month"]
        .astype(str)
        .str.strip()
        .str.title()
    )

    for col in [
        "hotel",
        "market_segment",
        "customer_type"
    ]:
        data[col] = (
            data[col]
            .fillna("Unknown")
            .astype(str)
            .str.strip()
        )

        data.loc[
            data[col].str.lower().isin(
                ["", "nan", "none", "null"]
            ),
            col
        ] = "Unknown"

    if "country" in data.columns:
        data["country"] = (
            data["country"]
            .fillna("Unknown")
            .astype(str)
        )

    fill_columns = [
        "adults",
        "children",
        "babies",
        "stays_in_weekend_nights",
        "stays_in_week_nights",
    ]

    for col in fill_columns:
        data[col] = data[col].fillna(0)

    data["total_guests"] = data[
        ["adults", "children", "babies"]
    ].sum(axis=1)

    data["total_nights"] = (
        data["stays_in_weekend_nights"]
        + data["stays_in_week_nights"]
    )

    data["booking_status"] = data[
        "is_canceled"
    ].map({
        0: "Not Canceled",
        1: "Canceled"
    })

    data["arrival_date_month"] = pd.Categorical(
        data["arrival_date_month"],
        categories=MONTHS,
        ordered=True
    )

    data = data.dropna(
        subset=["arrival_date_month"]
    )

    return data, file_path.name


# ============================================================
# 3. JUDUL DAN PEMUATAN DATA
# ============================================================
st.title("🏨 Hotel Booking Demand Dashboard")

st.caption(
    "Dashboard interaktif untuk menganalisis pola pemesanan, "
    "pembatalan, jenis hotel, segmen pasar, dan harga kamar."
)

# IDENTITAS MAHASISWA
st.markdown("""
**Nama:** Al Zahra Nur Febrian

**NIM:** 241051006

**Program Studi:** Sistem Informasi
""")

try:
    df, source_name = load_data()

except Exception as error:
    st.error(f"Dataset gagal dibaca: {error}")
    st.stop()

if df is None:
    st.warning(
        "Dataset belum ditemukan. Simpan file "
        "hotel_bookings_clean.csv atau hotel_bookings.csv "
        "ke dalam folder data."
    )
    st.stop()

st.caption(
    f"Sumber data: `{source_name}` • "
    f"{len(df):,} baris siap dianalisis"
)


# ============================================================
# 4. FILTER DASHBOARD
# ============================================================
st.sidebar.header("🔎 Filter Dashboard")
st.sidebar.caption(
    "Pilih kategori untuk menyaring data dashboard."
)

hotel_options = sorted(
    df["hotel"].dropna().unique().tolist()
)

segment_options = sorted(
    df["market_segment"].dropna().unique().tolist()
)

year_options = sorted(
    df["arrival_date_year"].dropna().unique().tolist()
)

selected_hotels = st.sidebar.multiselect(
    "Jenis Hotel",
    options=hotel_options,
    default=hotel_options,
    key="filter_hotel"
)

selected_segments = st.sidebar.multiselect(
    "Segmen Pasar",
    options=segment_options,
    default=segment_options,
    key="filter_segment"
)

selected_years = st.sidebar.multiselect(
    "Tahun Kedatangan",
    options=year_options,
    default=year_options,
    key="filter_year"
)

if (
    not selected_hotels
    or not selected_segments
    or not selected_years
):
    st.warning(
        "Pilih minimal satu jenis hotel, "
        "segmen pasar, dan tahun kedatangan."
    )
    st.stop()

filtered = df[
    df["hotel"].isin(selected_hotels)
    & df["market_segment"].isin(selected_segments)
    & df["arrival_date_year"].isin(selected_years)
].copy()

if filtered.empty:
    st.warning(
        "Tidak ada data yang sesuai dengan kombinasi filter tersebut."
    )
    st.stop()


# ============================================================
# 5. KPI DASHBOARD
# ============================================================
total_bookings = len(filtered)

canceled_count = int(
    filtered["is_canceled"].eq(1).sum()
)

cancellation_rate = (
    filtered["is_canceled"].mean() * 100
)

average_adr = filtered["adr"].mean()

kpi1, kpi2, kpi3 = st.columns(3)

kpi1.metric(
    "Total Pemesanan",
    f"{total_bookings:,}"
)

kpi2.metric(
    "Tingkat Pembatalan",
    f"{cancellation_rate:.1f}%"
)

kpi3.metric(
    "Rata-rata ADR",
    f"{average_adr:,.2f}"
)

st.divider()


# ============================================================
# 6. GRAFIK 1: TREN PEMESANAN BULANAN
# ============================================================
chart_left, chart_right = st.columns(2)

with chart_left:

    trend = (
        filtered.groupby(
            ["arrival_date_year", "arrival_date_month"],
            observed=True
        )
        .size()
        .reset_index(name="bookings")
    )

    trend["month_number"] = (
        trend["arrival_date_month"]
        .astype(str)
        .map({
            month: index
            for index, month in enumerate(MONTHS, start=1)
        })
    )

    trend["period"] = pd.to_datetime(
        trend["arrival_date_year"].astype(str)
        + "-"
        + trend["month_number"].astype(str)
        + "-01",
        errors="coerce"
    )

    trend = trend.sort_values("period")
    trend["period_label"] = (
        trend["period"].dt.strftime("%b %Y")
    )

    fig_trend = px.line(
        trend,
        x="period_label",
        y="bookings",
        color="arrival_date_year",
        markers=True,
        title="Tren Pemesanan Berdasarkan Bulan",
        labels={
            "period_label": "Bulan dan Tahun",
            "bookings": "Jumlah Pemesanan",
            "arrival_date_year": "Tahun",
        }
    )

    fig_trend.update_layout(
        plot_bgcolor="white",
        paper_bgcolor="white",
        xaxis_tickangle=-40,
        legend_title_text="Tahun",
        margin=dict(l=10, r=10, t=55, b=10)
    )

    st.plotly_chart(
        fig_trend,
        use_container_width=True
    )


# ============================================================
# 7. GRAFIK 2: PROPORSI PEMBATALAN
# ============================================================
with chart_right:

    status_data = (
        filtered["booking_status"]
        .value_counts()
        .rename_axis("status")
        .reset_index(name="jumlah")
    )

    fig_status = px.pie(
        status_data,
        names="status",
        values="jumlah",
        hole=0.48,
        title="Proporsi Pembatalan Pemesanan",
        color="status",
        color_discrete_map={
            "Not Canceled": "#0875d1",
            "Canceled": "#80c8f5"
        }
    )

    fig_status.update_traces(
        textposition="inside",
        textinfo="percent"
    )

    fig_status.update_layout(
        paper_bgcolor="white",
        margin=dict(l=10, r=10, t=55, b=10),
        legend_title_text="Status Pemesanan"
    )

    st.plotly_chart(
        fig_status,
        use_container_width=True
    )


# ============================================================
# 8. GRAFIK 3: PEMESANAN BERDASARKAN JENIS HOTEL
# ============================================================
chart_left, chart_right = st.columns(2)

with chart_left:

    hotel_summary = (
        filtered.groupby("hotel", as_index=False)
        .agg(
            total_bookings=("hotel", "size")
        )
        .sort_values(
            "total_bookings",
            ascending=False
        )
    )

    fig_hotel = px.bar(
        hotel_summary,
        x="hotel",
        y="total_bookings",
        color="hotel",
        title="Jumlah Pemesanan Berdasarkan Jenis Hotel",
        labels={
            "hotel": "Jenis Hotel",
            "total_bookings": "Jumlah Pemesanan"
        },
        text_auto=","
    )

    fig_hotel.update_layout(
        showlegend=False,
        plot_bgcolor="white",
        paper_bgcolor="white",
        margin=dict(l=10, r=10, t=55, b=10)
    )

    st.plotly_chart(
        fig_hotel,
        use_container_width=True
    )


# ============================================================
# 9. GRAFIK 4: HUBUNGAN LEAD TIME DAN ADR
# ============================================================
with chart_right:

    scatter_data = filtered.dropna(
        subset=["lead_time", "adr"]
    ).copy()

    if len(scatter_data) > 5000:
        scatter_data = scatter_data.sample(
            5000,
            random_state=42
        )

    fig_scatter = px.scatter(
        scatter_data,
        x="lead_time",
        y="adr",
        color="booking_status",
        opacity=0.55,
        title="Hubungan Lead Time dan Harga Kamar (ADR)",
        labels={
            "lead_time": "Jarak Hari Pemesanan ke Kedatangan",
            "adr": "ADR (Harga Rata-rata Harian)",
            "booking_status": "Status Pemesanan"
        },
        color_discrete_map={
            "Not Canceled": "#0875d1",
            "Canceled": "#80c8f5"
        }
    )

    fig_scatter.update_layout(
        plot_bgcolor="white",
        paper_bgcolor="white",
        margin=dict(l=10, r=10, t=55, b=10)
    )

    st.plotly_chart(
        fig_scatter,
        use_container_width=True
    )


# ============================================================
# 10. INSIGHT OTOMATIS
# ============================================================
st.divider()
st.subheader("💡 Insight Otomatis")

# Statistik pembatalan berdasarkan jenis hotel
hotel_stats = (
    filtered.groupby("hotel", as_index=False)
    .agg(
        total_booking=("is_canceled", "size"),
        cancellation_rate=("is_canceled", "mean")
    )
)

hotel_stats = hotel_stats[
    hotel_stats["total_booking"] >= 100
]

# Membersihkan nama segmen pasar yang tidak valid
invalid_segment_names = {
    "undefined",
    "unknown",
    "nan",
    "none",
    "",
    "null"
}

segment_data = filtered[
    ~filtered["market_segment"]
    .astype(str)
    .str.strip()
    .str.lower()
    .isin(invalid_segment_names)
]

segment_stats = (
    segment_data.groupby(
        "market_segment",
        as_index=False
    )
    .agg(
        total_booking=("is_canceled", "size"),
        cancellation_rate=("is_canceled", "mean")
    )
)

segment_stats = segment_stats[
    segment_stats["total_booking"] >= 100
]

# Statistik periode dengan pemesanan terbanyak
monthly_stats = (
    filtered.groupby(
        ["arrival_date_year", "arrival_date_month"],
        observed=True
    )
    .size()
    .reset_index(name="total_booking")
)

insight1, insight2 = st.columns(2)

with insight1:

    st.info(
        f"Jumlah pemesanan yang dibatalkan: "
        f"**{canceled_count:,}** "
        f"({cancellation_rate:.1f}% dari data terfilter)."
    )

    if not hotel_stats.empty:

        highest_hotel = hotel_stats.sort_values(
            "cancellation_rate",
            ascending=False
        ).iloc[0]

        st.info(
            f"Jenis hotel dengan tingkat pembatalan tertinggi: "
            f"**{highest_hotel['hotel']}** "
            f"({highest_hotel['cancellation_rate']:.1%}; "
            f"{int(highest_hotel['total_booking']):,} pemesanan)."
        )

    else:
        st.info(
            "Data pemesanan per jenis hotel belum mencukupi "
            "untuk dibandingkan."
        )


with insight2:

    if not segment_stats.empty:

        highest_segment = segment_stats.sort_values(
            "cancellation_rate",
            ascending=False
        ).iloc[0]

        st.info(
            f"Segmen pasar dengan tingkat pembatalan tertinggi: "
            f"**{highest_segment['market_segment']}** "
            f"({highest_segment['cancellation_rate']:.1%}; "
            f"{int(highest_segment['total_booking']):,} pemesanan)."
        )

    else:
        st.info(
            "Belum ada segmen pasar valid dengan minimal "
            "100 pemesanan pada filter yang dipilih."
        )

    if not monthly_stats.empty:

        busiest = monthly_stats.sort_values(
            "total_booking",
            ascending=False
        ).iloc[0]

        st.info(
            f"Periode dengan pemesanan terbanyak: "
            f"**{str(busiest['arrival_date_month'])} "
            f"{int(busiest['arrival_date_year'])}** "
            f"({int(busiest['total_booking']):,} pemesanan)."
        )


# ============================================================
# 11. TABEL DATA PEMESANAN
# ============================================================
st.divider()
st.subheader("📋 Data Pemesanan")

display_columns = [
    "hotel",
    "is_canceled",
    "lead_time",
    "arrival_date_year",
    "arrival_date_month",
    "country",
    "market_segment",
    "customer_type",
    "adr",
    "total_nights",
    "total_guests"
]

display_columns = [
    col for col in display_columns
    if col in filtered.columns
]

st.dataframe(
    filtered[display_columns].head(1000),
    use_container_width=True,
    hide_index=True
)

st.caption(
    f"Tabel menampilkan maksimal 1.000 dari "
    f"{len(filtered):,} baris yang sesuai dengan filter."
)

st.caption(
    "Catatan: ADR merupakan Average Daily Rate "
    "(rata-rata tarif kamar per hari). "
    "KPI, grafik, dan insight berubah mengikuti filter."
)
