import streamlit as st
import plotly.express as px

from app.data.datasets import (
    get_all_datasets,
    insert_dataset,
    delete_dataset,
    get_dataset_statistics,
)

st.set_page_config(page_title="Data Science Dashboard", page_icon="📊", layout="wide")

# ==================== AUTHENTICATION GUARD ====================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.error("🔒 You must be logged in to view this page")
    if st.button("Go to Login"):
        st.switch_page("Home.py")
    st.stop()

# ==================== DASHBOARD CONTENT ====================
st.title("📊 Data Science & Analytics Dashboard")
st.markdown(
    f"**Welcome, {st.session_state.username}** | Role: *{st.session_state.role}*"
)
st.divider()

with st.sidebar:
    st.header("🎛️ Controls")

    try:
        df_all = get_all_datasets()
        if len(df_all) > 0:
            unique_categories = df_all["category"].unique().tolist()
            category_filter = st.multiselect(
                "Filter by Category",
                unique_categories,
                default=unique_categories[: min(5, len(unique_categories))],
            )
        else:
            category_filter = []
    except:
        category_filter = []

    min_size = st.slider("Minimum Size (MB)", 0, 1000, 0)

    st.divider()
    st.subheader("📍 Navigate")
    if st.button("🏠 Home", use_container_width=True):
        st.switch_page("Home.py")
    if st.button("🛡️ Cyber Incidents", use_container_width=True):
        st.switch_page("pages/1_Cyber_Incidents.py")
    if st.button("⚙️ IT Operations", use_container_width=True):
        st.switch_page("pages/3_IT_Operations.py")

# ==================== METRICS ====================
st.subheader("📈 Key Metrics")

try:
    stats = get_dataset_statistics()

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Datasets", f"{stats['total']:,}")
    with col2:
        st.metric("Total Records", f"{stats['total_records']:,}")
    with col3:
        avg_size = stats["total_size_mb"] / stats["total"] if stats["total"] > 0 else 0
        st.metric("Avg Size", f"{avg_size:.1f} MB")
    with col4:
        st.metric("Total Storage", f"{stats['total_size_mb']:.0f} MB")
except Exception as e:
    st.error(f"Error loading statistics: {e}")

st.divider()

# ==================== MODEL PERFORMANCE (SIMULATED) ====================
st.subheader("🤖 ML Model Performance Metrics")

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Accuracy", "94.2%", delta="+2.1%")
with col2:
    st.metric("Precision", "91.8%", delta="+1.5%")
with col3:
    st.metric("Recall", "89.5%", delta="-0.3%")
with col4:
    st.metric("F1 Score", "90.6%", delta="+0.8%")

st.divider()

# ==================== VISUALIZATIONS ====================
try:
    df = get_all_datasets()

    if len(df) > 0:
        filtered_df = (
            df[df["category"].isin(category_filter)] if category_filter else df
        )
        filtered_df = filtered_df[filtered_df["file_size_mb"] >= min_size]

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("📊 Datasets by Category")
            category_counts = filtered_df["category"].value_counts().head(10)
            fig1 = px.bar(
                x=category_counts.values,
                y=category_counts.index,
                orientation="h",
                labels={"x": "Count", "y": "Category"},
                color=category_counts.values,
                color_continuous_scale="Blues",
            )
            st.plotly_chart(fig1, use_container_width=True)

        with col2:
            st.subheader("💾 Storage by Source")
            source_storage = (
                filtered_df.groupby("source")["file_size_mb"]
                .sum()
                .sort_values(ascending=False)
                .head(10)
            )
            fig2 = px.pie(
                values=source_storage.values, names=source_storage.index, hole=0.4
            )
            st.plotly_chart(fig2, use_container_width=True)

        st.subheader("📈 Dataset Size Analysis")
        fig3 = px.scatter(
            filtered_df.head(100),
            x="record_count",
            y="file_size_mb",
            color="category",
            size="file_size_mb",
            hover_data=["dataset_name", "source"],
            labels={
                "record_count": "Number of Records",
                "file_size_mb": "File Size (MB)",
            },
        )
        st.plotly_chart(fig3, use_container_width=True)

        st.divider()

        # ==================== DATASET TABLE ====================
        st.subheader("Datasets Overview")

        col1, col2 = st.columns([3, 1])
        with col1:
            st.write(f"Showing {len(filtered_df):,} of {len(df):,} datasets")
        with col2:
            rows_to_show = st.selectbox("Rows per page", [10, 25, 50, 100], index=1)

        st.dataframe(
            filtered_df.head(rows_to_show), use_container_width=True, hide_index=True
        )

        st.divider()

        # ==================== ADD NEW DATASET ====================
        st.subheader("➕ Add New Dataset")

        with st.form("new_dataset_form"):
            col1, col2, col3 = st.columns(3)

            with col1:
                dataset_name = st.text_input("Dataset Name")
                dataset_category = st.selectbox(
                    "Category",
                    [
                        "Marketing",
                        "Finance",
                        "Healthcare",
                        "Technology",
                        "E-commerce",
                        "IoT",
                        "Other",
                    ],
                )

            with col2:
                dataset_source = st.text_input(
                    "Source", placeholder="e.g., Kaggle, Internal"
                )
                dataset_size = st.number_input(
                    "Size (MB)", min_value=0.1, value=100.0, step=0.1
                )

            with col3:
                dataset_records = st.number_input(
                    "Number of Records", min_value=1, value=10000
                )
                last_update = st.date_input("Last Update")

            submitted = st.form_submit_button("📊 Add Dataset", type="primary")

            if submitted:
                if dataset_name and dataset_source:
                    try:
                        new_id = insert_dataset(
                            dataset_name,
                            dataset_category,
                            dataset_source,
                            last_update.strftime("%Y-%m-%d"),
                            dataset_records,
                            dataset_size,
                        )
                        st.success(f"✅ Dataset #{new_id} added successfully!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Error: {e}")
                else:
                    st.error("⚠️ Please fill in all required fields")

        # ==================== MANAGE DATASETS ====================
        st.divider()
        st.subheader("Manage Datasets")

        if len(df) > 0:
            dataset_options = [
                f"#{row['id']}: {row['dataset_name']}"
                for _, row in df.head(50).iterrows()
            ]
            selected_dataset = st.selectbox("Select Dataset", dataset_options)

            if selected_dataset:
                selected_id = int(selected_dataset.split(":")[0].replace("#", ""))
                dataset_data = df[df["id"] == selected_id].iloc[0]

                col1, col2 = st.columns(2)

                with col1:
                    st.write("**Dataset Details**")
                    st.json(
                        {
                            "Name": dataset_data["dataset_name"],
                            "Category": dataset_data["category"],
                            "Source": dataset_data["source"],
                            "Records": int(dataset_data["record_count"]),
                            "Size (MB)": float(dataset_data["file_size_mb"]),
                            "Last Update": dataset_data["last_update"],
                        }
                    )

                with col2:
                    st.write("**Delete Dataset**")
                    st.warning(f"⚠️ Delete: {dataset_data['dataset_name']}?")
                    if st.button(
                        "🗑️ Delete Dataset", type="primary", key=f"delete_{selected_id}"
                    ):
                        try:
                            if delete_dataset(selected_id):
                                st.success("✅ Dataset deleted!")
                                st.rerun()
                            else:
                                st.error("❌ Delete failed")
                        except Exception as e:
                            st.error(f"❌ Error: {e}")
        else:
            st.info("No datasets to manage")
    else:
        st.info("📭 No datasets found. Add your first dataset above!")

except Exception as e:
    st.error(f"❌ Error loading datasets: {e}")
    st.info("💡 Make sure you've run main.py to initialize the database")

st.divider()
if st.button("🚪 Logout"):
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.role = ""
    st.switch_page("Home.py")
