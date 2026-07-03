import plotly.graph_objects as go

def create_gauge(value, title, min_val=0, max_val=100, reverse=False):
    if reverse:
        value = max_val - value
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = value,
        title = {'text': title, 'font': {'color': "#E8EDF2", 'size': 14}},
        domain = {'x': [0, 1], 'y': [0, 1]},
        gauge = {
            'axis': {'range': [min_val, max_val], 'tickfont': {'color': "white"}},
            'bar': {'color': "#00D4AA" if value > 70 else "#F5A623" if value > 40 else "#FF4757"},
            'bgcolor': "#141A26",
            'borderwidth': 0,
            'steps': [
                {'range': [0, 33], 'color': '#1A2332'},
                {'range': [33, 66], 'color': '#1A2332'},
                {'range': [66, 100], 'color': '#1A2332'}
            ],
            'threshold': {
                'line': {'color': "white", 'width': 2},
                'thickness': 0.75,
                'value': value
            }
        }
    ))
    fig.update_layout(paper_bgcolor="#0A0E17", font={'color': "white"}, height=200)
    return fig