import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy import text
import pandas as pd
import streamlit as st

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

