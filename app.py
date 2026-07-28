import streamlit as st
import pandas as pd

# --------------------------------------------------
# Page Configuration
# --------------------------------------------------
st.set_page_config(
    page_title="Kerala College Predictor",
    page_icon="🎓",
    layout="wide"
)

st.markdown("""
<style>

/* -------------------------------
Main Heading
--------------------------------*/
h1{
    font-size:52px !important;
    font-weight:800 !important;
    color:#1f2937 !important;
}

/* -------------------------------
Caption
--------------------------------*/
[data-testid="stCaptionContainer"]{
    font-size:22px !important;
    font-weight:600 !important;
    color:#000000 !important;
}

/* -------------------------------
Input Labels
--------------------------------*/
label{
    font-size:22px !important;
    font-weight:700 !important;
    color:#000000 !important;
}

/* -------------------------------
Number Input
--------------------------------*/
.stNumberInput input{
    font-size:22px !important;
    font-weight:bold !important;
    color:#000000 !important;
}

/* -------------------------------
Select Box
--------------------------------*/
.stSelectbox div[data-baseweb="select"]{
    font-size:22px !important;
    font-weight:bold !important;
    color:#000000 !important;
}

/* -------------------------------
Dropdown Items
--------------------------------*/
div[role="listbox"] div{
    font-size:20px !important;
    color:#000000 !important;
}

/* -------------------------------
Metric Values
--------------------------------*/
[data-testid="stMetricValue"]{
    font-size:30px !important;
    font-weight:bold !important;
}

/* -------------------------------
Metric Labels
--------------------------------*/
[data-testid="stMetricLabel"]{
    font-size:20px !important;
    font-weight:700 !important;
}

/* -------------------------------
Sub Headers
--------------------------------*/
h3{
    font-size:30px !important;
    font-weight:700 !important;
}

/* -------------------------------
Buttons
--------------------------------*/
.stButton>button{

    font-size:22px !important;
    font-weight:bold !important;
    height:60px;
    border-radius:12px;

}

/* -------------------------------
Download Button
--------------------------------*/
.stDownloadButton>button{

    font-size:20px !important;
    font-weight:bold !important;
    height:55px;
    border-radius:12px;

}

</style>
""", unsafe_allow_html=True)


# --------------------------------------------------
# Title
# --------------------------------------------------
st.markdown("""
<h1>
🎓 Kerala College Predictor
</h1>

<p style="
font-size:22px;
font-weight:600;
color:#000000;
margin-top:-10px;
">
Predict colleges using previous year's Kerala allotment cutoff data.
</p>
""", unsafe_allow_html=True)
st.divider()

# --------------------------------------------------
# Load Dataset
# --------------------------------------------------
df = pd.read_excel("KERALA R1 ALLOT.xlsx")

# Clean Column Names
df.columns = df.columns.str.replace("\n", " ").str.strip()

# --------------------------------------------------
# User Inputs
# --------------------------------------------------
col1, col2, col3 = st.columns(3)

with col1:
    rank = st.number_input(
        "🏆 Enter Your Rank",
        min_value=1,
        step=1
    )

with col2:
    course = st.selectbox(
        "📚 Select Course",
        sorted(df["Course Name"].dropna().unique())
    )

with col3:
    category = st.selectbox(
        "👤 Select Category",
        sorted(df["Candidate Category"].dropna().unique())
    )

st.divider()

# --------------------------------------------------
# Predict Button
# --------------------------------------------------
if st.button("🎯 Predict Colleges", use_container_width=True):

    # Filter Dataset
    filtered = df[
        (df["Candidate Category"] == category) &
        (df["Course Name"] == course)
    ].copy()

    if filtered.empty:
        st.error("❌ No matching records found.")

    else:

        # ------------------------------------------
        # Gap Calculation
        # ------------------------------------------
        filtered["Gap"] = filtered["Rank"] - rank

        # ------------------------------------------
        # Best Match
        # ------------------------------------------
        closest_record = filtered.loc[
            filtered["Gap"].abs().idxmin()
        ]

        best_match_college = closest_record["College Name"]
        best_match_rank = int(closest_record["Rank"])

        # ------------------------------------------
        # Chance Function
        # ------------------------------------------
        def chance(gap):
            if gap > 300:
                return "🟢 High Chance"
            elif gap >= -300:
                return "🟡 Borderline"
            else:
                return "🔴 Tough Chance"

        filtered["Chance"] = filtered["Gap"].apply(chance)

        # ------------------------------------------
        # Keep One Record Per College
        # ------------------------------------------
        result = (
            filtered
            .sort_values("Rank", ascending=False)
            .drop_duplicates(subset="College Name", keep="first")
        )

        # Sort by Rank
        result = result.sort_values("Rank").reset_index(drop=True)

        # Serial Number
        result.insert(0, "S.No", range(1, len(result) + 1))

        # Rename
        result.rename(
            columns={
                "Candidate Category": "Category"
            },
            inplace=True
        )

        # Final Columns
        result = result[
            [
                "S.No",
                "Course Name",
                "Category",
                "Rank",
                "College Name",
                "Chance"
            ]
        ]

        # ------------------------------------------
        # Success Message
        # ------------------------------------------
        st.success("✅ Prediction Successful!")

        # ------------------------------------------
        # Prediction Summary
        # ------------------------------------------
        st.subheader("🎯 Prediction Summary")

        c1, c2 = st.columns(2)

        with c1:
            st.metric("🏆 Your Rank", int(rank))
            st.metric("📚 Course", course)
            st.metric("👤 Category", category)

        with c2:
            st.metric("🎓 Best Match College", best_match_college)
            st.metric("📈 Previous Year Cutoff", best_match_rank)

        st.divider()

        # ------------------------------------------
        # Statistics
        # ------------------------------------------
        high = (result["Chance"] == "🟢 High Chance").sum()
        border = (result["Chance"] == "🟡 Borderline").sum()
        tough = (result["Chance"] == "🔴 Tough Chance").sum()

        st.subheader("📊 Statistics")

        s1, s2, s3, s4 = st.columns(4)

        s1.metric("🏫 Colleges", len(result))
        s2.metric("🟢 High", high)
        s3.metric("🟡 Borderline", border)
        s4.metric("🔴 Tough", tough)

        st.divider()

        # ------------------------------------------
        # Recommended Colleges
        # ------------------------------------------
        st.subheader("📋 Recommended Colleges")

        st.dataframe(
            result,
            use_container_width=True,
            hide_index=True
        )

        # ------------------------------------------
        # Download CSV
        # ------------------------------------------
        csv = result.to_csv(index=False).encode("utf-8")

        st.download_button(
            label="📥 Download Results as CSV",
            data=csv,
            file_name="Kerala_College_Prediction.csv",
            mime="text/csv",
            use_container_width=True
        )

# --------------------------------------------------
# Footer
# --------------------------------------------------
st.divider()

st.caption(
    "Developed using ❤️ Python, Pandas & Streamlit | "
    "Kerala College Predictor"
)