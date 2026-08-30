import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="TNEA 2025", layout="wide")
st.title("🎓 TN Engineering Seat Matrix Dashboard")

categories = ['OC', 'BC', 'BCM', 'MBC', 'SC', 'SCA', 'ST', 'Total']
mode = st.sidebar.radio("Select Mode", ["📁 Single File Summary", "🔄 Compare Two Rounds", "🔮 College Predictor & Pattern Analysis"])

# === MODE 1: Single File Summary ===
if mode == "📁 Single File Summary":
    st.header("📊 Seat Summary From One File")
    file = st.file_uploader("Upload a single seat matrix CSV", type="csv", key="single")

    if file:
        df = pd.read_csv(file)
        for col in categories:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)

        # Dynamic filters
        colleges = sorted(df['college_name'].unique())
        sel_colleges = st.sidebar.multiselect("🎓 Filter by Colleges", colleges, default=colleges)

        if len(sel_colleges) == 1:
            branches = sorted(df[df['college_name'].isin(sel_colleges)]['branch_name'].unique())
        else:
            branches = sorted(df['branch_name'].unique())

        sel_branches = st.sidebar.multiselect("📘 Filter by Branches", branches, default=branches)

        filtered = df[df['college_name'].isin(sel_colleges) & df['branch_name'].isin(sel_branches)]

        # Group by field
        summary_by = st.sidebar.radio("Group Summary By", ["College", "Branch"])
        if summary_by == "College":
            group_fields = ['college_code', 'college_name']
        else:
            group_fields = ['branch_name']

        st.subheader(f"📋 Total Seats Grouped by {summary_by}")
        summary = filtered.groupby(group_fields)[categories].sum().reset_index()
        summary['TotalSeats'] = summary['Total']
        display_df = summary.sort_values('TotalSeats', ascending=False)
        st.dataframe(display_df, use_container_width=True)

        # Chart
        st.subheader("📈 Total Seat Distribution")
        fig, ax = plt.subplots(figsize=(10, 6))
        plot_labels = display_df[group_fields[-1]].astype(str)
        ax.barh(plot_labels, display_df['TotalSeats'], color="#3b82f6")
        ax.set_xlabel("Total Seats")
        ax.invert_yaxis()
        st.pyplot(fig)

        # Filled vs Remaining (all are unfilled here)
        st.subheader("📊 Remaining Capacity by Category")
        remaining = filtered[categories].sum()
        fig2, ax2 = plt.subplots(figsize=(8, 4))
        remaining.plot(kind='bar', ax=ax2, color='#f59e0b')
        ax2.set_ylabel("Available Seats")
        ax2.set_title("Remaining Seats (Capacity View)")
        st.pyplot(fig2)

        # Vacancy rate (just 100% everywhere)
        st.subheader("🧮 Vacancy Rate by Category (%)")
        vacancy_df = pd.DataFrame({'Remaining': remaining})
        vacancy_df['Vacancy Rate (%)'] = 100.0
        styled_vacancy = vacancy_df.style.applymap(lambda v: "background-color: #fca5a5" if v > 50 else "")
        st.dataframe(styled_vacancy, use_container_width=True)

        # Download
        st.download_button(
            "⬇️ Download Summary CSV",
            display_df.to_csv(index=False),
            f"seat_summary_by_{summary_by.lower()}.csv",
            "text/csv"
        )

    else:
        st.info("Please upload a CSV file.")

# === MODE 2: Compare Two Rounds ===
elif mode == "🔄 Compare Two Rounds":
    st.header("🔄 Seat Movement Between Two Rounds")

    before_file = st.file_uploader("Upload Before Round CSV", type="csv", key="before2")
    after_file = st.file_uploader("Upload After Round CSV", type="csv", key="after2")

    if before_file and after_file:
        df_before = pd.read_csv(before_file)
        df_after = pd.read_csv(after_file)
        for df0 in [df_before, df_after]:
            for col in categories:
                df0[col] = pd.to_numeric(df0[col], errors='coerce').fillna(0).astype(int)

        df = pd.merge(
            df_before[['college_code', 'branch_code', 'college_name', 'branch_name'] + categories],
            df_after[['college_code', 'branch_code'] + categories],
            on=['college_code', 'branch_code'],
            suffixes=('_before', '_after')
        )

        for col in categories:
            df[f'{col}_taken'] = df[f'{col}_before'] - df[f'{col}_after']

        colleges = sorted(df['college_name'].unique())
        sel_college = st.sidebar.selectbox("🎓 Select College", ['All'] + colleges)

        if sel_college != 'All':
            filtered_branches = sorted(df[df['college_name'] == sel_college]['branch_name'].unique())
        else:
            filtered_branches = sorted(df['branch_name'].unique())

        sel_branch = st.sidebar.selectbox("📘 Select Branch", ['All'] + filtered_branches)

        filtered = df.copy()
        if sel_college != 'All':
            filtered = filtered[filtered['college_name'] == sel_college]
        if sel_branch != 'All':
            filtered = filtered[filtered['branch_name'] == sel_branch]

        # Display table
        st.subheader("📊 Seats Taken per Category")
        result = filtered[['college_code', 'college_name', 'branch_name'] + [f'{c}_taken' for c in categories]].copy()
        rename_map = {f'{c}_taken': c for c in categories}
        rename_map.update({'college_code': 'Code', 'college_name': 'College', 'branch_name': 'Course'})
        result = result.rename(columns=rename_map)
        st.dataframe(result, use_container_width=True)

        # Bar chart for taken
        st.subheader("📉 Total Seats Taken by Category")
        summary = filtered[[f'{c}_taken' for c in categories]].sum()
        summary.index = categories
        fig, ax = plt.subplots(figsize=(8, 4))
        summary.plot(kind='bar', ax=ax, color="#ef4444")
        ax.set_ylabel("Seats Taken")
        st.pyplot(fig)
    else:
        st.info("Please upload both files to compare.")

# === MODE 3: College Predictor & Pattern Analysis ===
elif mode == "🔮 College Predictor & Pattern Analysis":
    st.header("🔮 College Predictor & Pattern Analysis")
    st.markdown("Upload historical allotment data to predict college availability based on cutoff scores.")

    predictor_file = st.file_uploader("Upload Allotment/Cutoff CSV Data", type="csv", key="predictor")

    if predictor_file:
        try:
            df_pred = pd.read_csv(predictor_file)

            # Basic validation of columns - adjust as needed based on the actual CSV format you'll upload
            required_cols = ['College', 'Branch', 'Category', 'Score']
            missing_cols = [col for col in required_cols if col not in df_pred.columns]

            if missing_cols:
                st.error(f"The uploaded CSV is missing required columns: {', '.join(missing_cols)}")
                st.info("Expected columns: 'College', 'Branch', 'Category', 'Score'. Please map your CSV to match these.")
            else:
                # Clean up score column
                df_pred['Score'] = pd.to_numeric(df_pred['Score'], errors='coerce')
                df_pred = df_pred.dropna(subset=['Score'])

                # Calculate closing scores
                closing_scores = df_pred.groupby(['College', 'Branch', 'Category'])['Score'].min().reset_index()
                closing_scores = closing_scores.rename(columns={'Score': 'Closing Score'})

                st.success("Data processed successfully!")

                st.markdown("### 🧑‍🎓 Enter Your Details")

                # Student inputs
                col1, col2 = st.columns(2)
                with col1:
                    student_score = st.number_input("Your Cutoff Score", min_value=0.0, max_value=200.0, value=180.0, step=0.5)
                with col2:
                    student_category = st.selectbox("Your Category", categories[:-1]) # exclude 'Total'

                # Optional filters
                colleges_list = sorted(df_pred['College'].unique())
                sel_colleges_pred = st.sidebar.multiselect("🎓 Preferred Colleges (Optional)", colleges_list)

                if sel_colleges_pred:
                    branches_list = sorted(df_pred[df_pred['College'].isin(sel_colleges_pred)]['Branch'].unique())
                else:
                    branches_list = sorted(df_pred['Branch'].unique())

                sel_branches_pred = st.sidebar.multiselect("📘 Preferred Branches (Optional)", branches_list)

                st.markdown("### 🎯 Predicted Opportunities")

                # Filter by Category and Score
                predicted_df = closing_scores[
                    (closing_scores['Category'] == student_category) &
                    (closing_scores['Closing Score'] <= student_score)
                ]

                # Apply optional filters
                if sel_colleges_pred:
                    predicted_df = predicted_df[predicted_df['College'].isin(sel_colleges_pred)]
                if sel_branches_pred:
                    predicted_df = predicted_df[predicted_df['Branch'].isin(sel_branches_pred)]

                if predicted_df.empty:
                    st.warning("No colleges found matching your criteria. Try adjusting your preferences or score.")
                else:
                    st.success(f"Found {len(predicted_df)} possible opportunities!")

                    # Sort by closing score descending (best possible options based on cutoff)
                    predicted_df = predicted_df.sort_values(by="Closing Score", ascending=False)
                    st.dataframe(predicted_df, use_container_width=True)

                    st.markdown("### 📈 Score Distribution by Branch (Pattern Analysis)")

                    # Top branches by number of matches
                    top_branches = predicted_df['Branch'].value_counts().head(10).index

                    # Use original df_pred for distribution of those specific branches and category
                    dist_df = df_pred[
                        (df_pred['Category'] == student_category) &
                        (df_pred['Branch'].isin(top_branches))
                    ]

                    if sel_colleges_pred:
                        dist_df = dist_df[dist_df['College'].isin(sel_colleges_pred)]

                    if not dist_df.empty:
                        fig, ax = plt.subplots(figsize=(10, 6))
                        # Create a simple scatter/strip plot to show score spread
                        for branch in top_branches:
                            branch_scores = dist_df[dist_df['Branch'] == branch]['Score']
                            ax.scatter(
                                [branch] * len(branch_scores),
                                branch_scores,
                                alpha=0.6,
                                label=branch if branch not in ax.get_legend_handles_labels()[1] else ""
                            )

                        ax.axhline(y=student_score, color='r', linestyle='--', label=f"Your Score ({student_score})")

                        plt.xticks(rotation=45, ha='right')
                        ax.set_ylabel("Allotted Scores")
                        ax.set_title(f"Score Spread for Top Matched Branches ({student_category})")
                        # plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
                        plt.tight_layout()
                        st.pyplot(fig)
                    else:
                        st.info("Not enough data to plot distribution.")

        except Exception as e:
            st.error(f"Error processing file: {e}")
    else:
        st.info("Please upload historical allotment data to proceed.")
