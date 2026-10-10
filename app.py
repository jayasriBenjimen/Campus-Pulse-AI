
import streamlit as st
import pandas as pd
import plotly.express as px

# ---------------- PAGE CONFIGURATION ----------------
st.set_page_config(
    page_title="CampusPulse AI",
    page_icon="🎓",
    layout="wide"
)

# ---------------- LOAD STUDENT DATA ----------------
@st.cache_data
def load_data():
    df = pd.read_csv("students.csv")
    df.columns = df.columns.str.strip()
    df["name"] = df["name"].str.strip()
    return df


df = load_data()

# ---------------- STUDENT SUCCESS SCORE ----------------
df["success_score"] = (
    (df["cgpa"] / 10) * 25
    + (df["attendance"] / 100) * 20
    + ((5 - df["backlogs"].clip(upper=5)) / 5) * 15
    + (df["lms_completion"] / 100) * 10
    + (df["aptitude_score"] / 100) * 10
    + (df["coding_score"] / 100) * 10
    + (df["mock_interview"] / 100) * 5
    + (df["engagement_score"] / 100) * 5
).round(1)

# ---------------- RISK IDENTIFICATION ----------------
def identify_risk(row):
    if (
        row["attendance"] < 65
        or row["backlogs"] >= 3
        or row["success_score"] < 50
    ):
        return "High Risk"

    elif (
        row["attendance"] < 75
        or row["backlogs"] >= 2
        or row["success_score"] < 65
    ):
        return "Medium Risk"

    return "Low Risk"


df["risk_level"] = df.apply(identify_risk, axis=1)

# ---------------- STUDENT SEGMENTATION ----------------
def identify_segment(row):
    if row["attendance"] < 65 or row["backlogs"] >= 3:
        return "Academic Support Needed"

    if row["cgpa"] >= 8 and (
        row["aptitude_score"] < 60
        or row["coding_score"] < 60
        or row["mock_interview"] < 60
    ):
        return "Placement Training Needed"

    if (
        row["aptitude_score"] >= 70
        and row["coding_score"] >= 70
        and row["mock_interview"] >= 70
    ):
        return "Placement Ready"

    if row["lms_completion"] < 60:
        return "Engagement Improvement Needed"

    return "General Development"


df["student_segment"] = df.apply(identify_segment, axis=1)

# ---------------- PLACEMENT READINESS ----------------
df["placement_ready"] = (
    (df["aptitude_score"] >= 70)
    & (df["coding_score"] >= 70)
    & (df["mock_interview"] >= 70)
)

# ---------------- SIDEBAR ----------------
st.sidebar.title("🎓 CampusPulse AI")
st.sidebar.caption("Smart Campus Analytics")

page = st.sidebar.radio(
    "Navigation",
    [
        "Dashboard",
        "Student Explorer",
        "Placement Readiness",
        "Insights"
    ]
)

# ---------------- HEADER ----------------
st.title("🎓 CampusPulse AI")
st.write(
    "Predict, optimize and improve student success "
    "using academic and engagement analytics."
)

st.info(
    "Prototype using fictional student records. "
    "Risk flags are preliminary indicators, not final judgments."
)

# ====================================================
# PAGE 1: DASHBOARD
# ====================================================
if page == "Dashboard":

    st.header("📊 Campus Dashboard")

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Total Students", len(df))

    c2.metric(
        "Average Success Score",
        f"{df['success_score'].mean():.1f}/100"
    )

    c3.metric(
        "High Risk Students",
        int((df["risk_level"] == "High Risk").sum())
    )

    c4.metric(
        "Placement Ready",
        int(df["placement_ready"].sum())
    )

    st.subheader("Student Success Overview")

    col1, col2 = st.columns(2)

    with col1:
        fig = px.histogram(
            df,
            x="success_score",
            color="risk_level",
            nbins=10,
            title="Student Success Score Distribution",
            labels={
                "success_score": "Success Score",
                "risk_level": "Risk Level"
            }
        )

        st.plotly_chart(fig, use_container_width=True)

    with col2:
        risk_counts = (
            df["risk_level"]
            .value_counts()
            .rename_axis("Risk Level")
            .reset_index(name="Students")
        )

        fig = px.pie(
            risk_counts,
            names="Risk Level",
            values="Students",
            title="Student Risk Distribution",
            hole=0.45
        )

        st.plotly_chart(fig, use_container_width=True)

    st.subheader("⚠️ Students Requiring Attention")

    at_risk = (
        df[df["risk_level"] != "Low Risk"]
        .sort_values("success_score")
    )

    st.dataframe(
        at_risk[
            [
                "student_id",
                "name",
                "department",
                "success_score",
                "attendance",
                "backlogs",
                "risk_level",
                "student_segment"
            ]
        ],
        use_container_width=True,
        hide_index=True
    )

# ====================================================
# PAGE 2: STUDENT EXPLORER
# ====================================================
elif page == "Student Explorer":

    st.header("🔎 Student Explorer")

    departments = ["All"] + sorted(
        df["department"].unique().tolist()
    )

    selected_dept = st.selectbox(
        "Select Department",
        departments
    )

    filtered = df.copy()

    if selected_dept != "All":
        filtered = filtered[
            filtered["department"] == selected_dept
        ]

    selected_name = st.selectbox(
        "Select Student",
        filtered["name"].tolist()
    )

    student = filtered[
        filtered["name"] == selected_name
    ].iloc[0]

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Success Score",
        f"{student['success_score']}/100"
    )

    c2.metric(
        "Attendance",
        f"{student['attendance']}%"
    )

    c3.metric(
        "Risk Level",
        student["risk_level"]
    )

    st.write("**Student Segment:**", student["student_segment"])

    st.subheader("Student Performance Indicators")

    indicators = {
        "CGPA": student["cgpa"],
        "Attendance (%)": student["attendance"],
        "LMS Completion (%)": student["lms_completion"],
        "Aptitude Score": student["aptitude_score"],
        "Coding Score": student["coding_score"],
        "Mock Interview": student["mock_interview"],
        "Engagement Score": student["engagement_score"],
        "Backlogs": student["backlogs"]
    }

    indicator_df = pd.DataFrame(
        list(indicators.items()),
        columns=["Indicator", "Value"]
    )

    st.dataframe(
        indicator_df,
        use_container_width=True,
        hide_index=True
    )

    st.subheader("💡 Explainable Insights")

    reasons = []

    if student["attendance"] < 75:
        reasons.append(
            "Attendance is below 75%."
        )

    if student["backlogs"] > 0:
        reasons.append(
            f"{int(student['backlogs'])} backlogs recorded."
        )

    if student["lms_completion"] < 60:
        reasons.append(
            "LMS completion is low; assignment support may help."
        )

    if student["aptitude_score"] < 60:
        reasons.append(
            "Additional aptitude practice may help."
        )

    if student["coding_score"] < 60:
        reasons.append(
            "Additional coding practice may help."
        )

    if student["mock_interview"] < 60:
        reasons.append(
            "More mock interview practice may help."
        )

    if reasons:
        for reason in reasons:
            st.warning(reason)
    else:
        st.success(
            "No major warning indicators in this sample record."
        )

    st.caption(
        "These insights are generated using predefined rules."
    )

# ====================================================
# PAGE 3: PLACEMENT READINESS
# ====================================================
elif page == "Placement Readiness":

    st.header("💼 Placement Readiness Analysis")

    fig = px.scatter(
        df,
        x="coding_score",
        y="aptitude_score",
        size="mock_interview",
        color="department",
        hover_name="name",
        hover_data=[
            "success_score",
            "risk_level",
            "student_segment"
        ],
        title="Coding vs Aptitude Performance",
        labels={
            "coding_score": "Coding Score",
            "aptitude_score": "Aptitude Score"
        }
    )

    st.plotly_chart(fig, use_container_width=True)

    ready = df[df["placement_ready"]]

    not_ready = df[~df["placement_ready"]]

    c1, c2 = st.columns(2)

    c1.metric(
        "Meeting Readiness Criteria",
        len(ready)
    )

    c2.metric(
        "Need Further Preparation",
        len(not_ready)
    )

    st.subheader("Students Meeting Sample Readiness Criteria")

    st.dataframe(
        ready[
            [
                "name",
                "department",
                "aptitude_score",
                "coding_score",
                "mock_interview"
            ]
        ],
        use_container_width=True,
        hide_index=True
    )

    st.subheader("Students Needing Placement Support")

    st.dataframe(
        not_ready[
            [
                "name",
                "department",
                "aptitude_score",
                "coding_score",
                "mock_interview",
                "student_segment"
            ]
        ],
        use_container_width=True,
        hide_index=True
    )

    st.caption(
        "Readiness is estimated using sample thresholds: "
        "aptitude, coding and mock interview scores of at least 70. "
        "Actual placement outcomes must be used to validate these rules."
    )

# ====================================================
# PAGE 4: INSIGHTS
# ====================================================
elif page == "Insights":

    st.header("💡 Campus Insights")

    # Student segmentation
    st.subheader("🎯 Student Segmentation")

    segment_counts = (
        df["student_segment"]
        .value_counts()
        .rename_axis("Student Segment")
        .reset_index(name="Number of Students")
    )

    st.dataframe(
        segment_counts,
        use_container_width=True,
        hide_index=True
    )

    fig_segments = px.bar(
        segment_counts,
        x="Student Segment",
        y="Number of Students",
        color="Student Segment",
        title="Student Groups Requiring Different Support"
    )

    st.plotly_chart(
        fig_segments,
        use_container_width=True
    )

    # Department statistics
    st.subheader("🏫 Department Performance")

    department_stats = (
        df.groupby("department")
        .agg(
            Average_Success=("success_score", "mean"),
            Average_Attendance=("attendance", "mean"),
            Average_Coding=("coding_score", "mean"),
            Students=("student_id", "count")
        )
        .round(1)
        .reset_index()
    )

    st.dataframe(
        department_stats,
        use_container_width=True,
        hide_index=True
    )

    fig_department = px.bar(
        department_stats,
        x="department",
        y="Average_Success",
        color="department",
        title="Average Success Score by Department",
        labels={
            "department": "Department",
            "Average_Success": "Average Success Score"
        }
    )

    st.plotly_chart(
        fig_department,
        use_container_width=True
    )

    # Suggested interventions
    st.subheader("🛠️ Suggested Interventions")

    interventions = {
        "Academic Support Needed":
            "Offer faculty mentoring, attendance follow-up and backlog support.",

        "Placement Training Needed":
            "Provide coding practice, aptitude sessions and mock interviews.",

        "Placement Ready":
            "Offer advanced placement opportunities and interview preparation.",

        "Engagement Improvement Needed":
            "Encourage LMS participation and provide assignment reminders.",

        "General Development":
            "Continue regular mentoring and skill development."
    }

    for segment, recommendation in interventions.items():
        count = int(
            (df["student_segment"] == segment).sum()
        )

        if count > 0:
            with st.expander(f"{segment} — {count} students"):
                st.write(recommendation)

    st.caption(
        "Insights use predefined rules and fictional data. "
        "They are not validated AI predictions."
    )

# ---------------- FOOTER ----------------
st.divider()

st.caption(
    "CampusPulse AI | Student Success Analytics Prototype"
)
