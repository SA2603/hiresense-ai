import plotly.graph_objects as go


def make_gauge_chart(value: float, title: str, suffix: str = "",
                      thresholds: tuple = (50, 70)) -> go.Figure:
    """
    Builds a standardized gauge chart, reused across ATS Score, Skill Gap,
    and Resume Similarity pages (previously duplicated three times).

    value: the number to display (0-100 scale expected)
    title: chart title, e.g. "Overall ATS Score"
    suffix: appended after the number, e.g. "%" or " / 100"
    thresholds: (low, high) cutoffs for red/amber/green coloring -
                below thresholds[0] = red, between = amber, above thresholds[1] = green
    """
    low, high = thresholds
    color = "#2ecc71" if value >= high else "#f39c12" if value >= low else "#e74c3c"

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        number={"suffix": suffix},
        gauge={
            "axis": {"range": [0, 100]},
            "bar": {"color": color},
        },
        title={"text": title}
    ))
    fig.update_layout(height=300, margin=dict(t=50, b=10, l=30, r=30))
    return fig


def make_breakdown_bar_chart(labels: list, values: list) -> go.Figure:
    """
    Builds a standardized horizontal breakdown bar chart, extracted from
    the ATS Score page (Step 5.2) so it can be reused on the dashboard too.
    """
    fig = go.Figure(go.Bar(
        x=values,
        y=labels,
        orientation="h",
        marker_color=["#2ecc71" if v >= 70 else "#f39c12" if v >= 50 else "#e74c3c" for v in values],
        text=[f"{v}" for v in values],
        textposition="outside"
    ))
    fig.update_layout(
        xaxis=dict(range=[0, 100], title="Score"),
        height=350,
        margin=dict(t=20, b=20, l=20, r=20)
    )
    return fig