from __future__ import annotations

from typing import Dict, List

import pandas as pd
import streamlit as st

from nutri_meal_guide.services.nhs_ods import fetch_all_nhs_gp_practices


def render_gp_finder() -> None:
    st.title("Find GP Practices in the UK")
    st.caption(
        "Powered by NHS Organisation Data Service (open data). "
        "Load all GP practices across the UK, then filter or download."
    )

    st.markdown(
        """
### Need medical guidance?
If you have questions about your health, diet, diabetes management, or if you think you’re having an **allergic reaction**, use this page to find a nearby GP practice.

If symptoms are severe or getting worse, seek urgent medical help immediately.
        """
    )

    if "gp_all_list" not in st.session_state:
        st.session_state["gp_all_list"] = []

    col_name, col_post = st.columns(2)
    with col_name:
        name_filter = st.text_input("Filter by practice name (optional)", value="")
    with col_post:
        postcode_filter = st.text_input("Filter by postcode (optional)", value="")

    if st.button("Load all GP practices (UK)"):
        with st.spinner("Fetching GP practices from NHS…"):
            all_rows, err = fetch_all_nhs_gp_practices()
            if err:
                st.error(f"Could not load GP data: {err}")
            elif not all_rows:
                st.warning("NHS API returned no practices. Try again later.")
            else:
                st.session_state["gp_all_list"] = all_rows
                st.success(f"Loaded **{len(all_rows)}** GP practices.")

    all_rows: List[Dict[str, str]] = st.session_state["gp_all_list"]
    if not all_rows:
        st.info(
            "Click **Load all GP practices (UK)** to fetch every GP practice from the NHS directory."
        )
        return

    filtered = all_rows
    if name_filter:
        name_lower = name_filter.lower()
        filtered = [r for r in filtered if name_lower in r["Name"].lower()]
    if postcode_filter:
        pc_lower = postcode_filter.lower()
        filtered = [r for r in filtered if pc_lower in (r["Postcode"] or "").lower()]

    st.metric("GP practices shown", len(filtered))
    df = pd.DataFrame(filtered)
    st.dataframe(df, width="stretch", height=400)

    if not df.empty:
        st.download_button(
            "Download as CSV",
            data=df.to_csv(index=False),
            file_name="nhs_gp_practices_uk.csv",
            mime="text/csv",
        )

