# 🎓 TN Engineering Seat Matrix (2025) Analyzer

A powerful, interactive **Streamlit dashboard** to analyze engineering seat allocation across government and private colleges in Tamil Nadu.

This tool helps you:

- 📁 View and filter seat availability by college, branch, and category
- 🔄 Compare rounds to identify seat intake progression
- 📊 Track multi-round seat movement and cumulative fills
- 📈 Visualize trends and detect anomalies (e.g. underfilled branches, category imbalances)

---

## 🚀 Features

### 🧩 Modes

| Mode                       | Description                                                             |
| -------------------------- | ----------------------------------------------------------------------- |
| **📁 Single File Summary** | Upload any round’s seat matrix and analyze totals                       |
| **🔄 Compare Two Rounds**  | Upload two CSVs (e.g. before and after 1st round) and see seat movement |
| **🔮 College Predictor**   | Upload historical allotment/cutoff data to predict eligible colleges, and view historical score distribution patterns |

### 🎯 Highlights

- Smart filters: dynamic college/branch selection with multi-select and search
- Session persistence for filter selections
- Vacancy rate visualizations per category
- Excel export for round-wise deltas

---

## 📦 Setup Instructions

### ✅ Requirements

- Python 3.8+
- `pip` or `conda`

### 📥 Installation

```bash
# Clone the repo
git clone https://github.com/elumalaisuriyakanth/TNEA-2025.git
cd TNEA-2025

# Create virtual env (optional but recommended)
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt
```

### 🏃‍♂️ Running the App

To start the Streamlit application, run the following command in your terminal:

```bash
streamlit run app.py
```

The application will open automatically in your default web browser (usually at `http://localhost:8501`).

### 🔮 Using the College Predictor

1. Select the **🔮 College Predictor & Pattern Analysis** mode from the sidebar.
2. Upload a CSV file containing historical allotment data. **Note:** The CSV must contain the columns `College`, `Branch`, `Category`, and `Score`.
3. Enter your cutoff score and select your category.
4. (Optional) Filter by preferred colleges and branches.
5. The app will calculate closing scores, display predicted opportunities, and show a score distribution pattern for the top matched branches.
