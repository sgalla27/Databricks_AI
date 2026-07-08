import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy import text
import pandas as pd
import streamlit as st


st.set_page_config(
    page_title="Policy Search",
    page_icon="📄",
    layout="wide"
)

st.markdown("""
<style>
.stButton > button {
    background-color: #0078D4;
    color: white;
}
</style>
""", unsafe_allow_html=True)

load_dotenv()

user = os.getenv("PGUSER")
password = os.getenv("PGPASSWORD")

host = "ep-purple-union-d81ngh8h.database.us-east-2.cloud.databricks.com"
database = "databricks_postgres"

DB_URL = (
    f"postgresql://{user}:{password}@{host}/{database}"
    "?sslmode=require"
)

engine = create_engine(DB_URL)

USERS = {
    "Sean": "admin",
    "Underwriter": "underwriter",
    "Viewer": "viewer"
}

current_user = st.sidebar.selectbox(
    "Current User",
    USERS.keys()
)

USER_ROLE = USERS[current_user]

st.sidebar.success(
    f"Role: {USER_ROLE}"
)

search_tab, submit_tab = st.tabs(
    ["🔍 Policy Search", "📝 New Submission"]
)

with search_tab:
    st.title("Policy Search")

    search_term = st.text_input(
        "Search by Policy ID or Product Description",
    )


    if st.button("Search"):

        with st.spinner("Searching..."):

            query = """
            SELECT fp.policy_id, fp.policy_number, di.named_insured, dp.description, di.dba_name, di.email
            FROM master.dim_product dp
            JOIN transactional.fact_policy fp
                ON dp.product_id = fp.product_id
            JOIN master.dim_insured di
                ON fp.insured_id = di.insured_id
            WHERE
                CAST(fp.policy_id AS TEXT) ILIKE %(term)s
                OR dp.description ILIKE %(term)s
            """

            df = pd.read_sql(
                query,
                engine,
                params={
                    "term": f"%{search_term}%"
                }
            )

        if df.empty:
            st.warning("No results found")
        else:
            st.success(f"{len(df)} result(s) found")
            st.dataframe(
                df,
                use_container_width=True
            )

with submit_tab:
    st.title("📝 New Policy Submission")

    if USER_ROLE not in ["admin", "underwriter"]:

        st.error(
            "You do not have permission to create policy submissions."
        )

    else:

        submission_number = st.text_input(
            "Submission Number"
        )

        entity_name = st.text_input(
            "Entity Name"
        )

        product_description = st.text_input(
            "Product Description"
        )

        status = st.selectbox(
            "Status",
            ["Pending", "Quoted", "Bound"]
        )

        premium = st.number_input(
            "Premium",
            min_value=0.0
        )

