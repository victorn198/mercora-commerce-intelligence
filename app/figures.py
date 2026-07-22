from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


NAVY = "#12346b"
BLUE = "#0b6bdc"
TEAL = "#0b6bdc"
GREEN = "#15966a"
AMBER = "#d99327"
RED = "#df554d"
MUTED = "#68758a"
GRID = "#edf0f5"
PAYMENT_LABELS = {
    "credit_card": "Cartão de crédito",
    "boleto": "Boleto",
    "debit_card": "Cartão de débito",
    "voucher": "Voucher",
    "not_defined": "Não definido",
}


def _compact_currency(value: float, lang: str = "pt") -> str:
    value = float(value)
    if abs(value) >= 1_000_000:
        return f"R$ {value / 1_000_000:.0f} {'M' if lang == 'en' else 'mi'}"
    if abs(value) >= 1_000:
        return f"R$ {value / 1_000:.0f} {'K' if lang == 'en' else 'mil'}"
    return f"R$ {value:.0f}"


def _whole_number(value: float, lang: str = "pt") -> str:
    formatted = f"{float(value):,.0f}"
    return formatted if lang == "en" else formatted.replace(",", ".")


def _base(figure: go.Figure, height: int = 285, bottom_margin: int = 26) -> go.Figure:
    figure.update_layout(
        height=height,
        margin=dict(l=12, r=18, t=12, b=bottom_margin),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Segoe UI, Inter, sans-serif", color=NAVY, size=10),
        hoverlabel=dict(bgcolor="white", font_color=NAVY),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0),
    )
    figure.update_xaxes(showgrid=False, zeroline=False, linecolor=GRID)
    figure.update_yaxes(gridcolor=GRID, zeroline=False)
    return figure


def empty_figure(message: str = "Sem dados para o recorte selecionado", lang: str = "pt") -> go.Figure:
    if lang == "en" and message == "Sem dados para o recorte selecionado":
        message = "No data for the selected scope"
    figure = go.Figure()
    figure.add_annotation(text=message, x=0.5, y=0.5, showarrow=False, font=dict(color=MUTED, size=14))
    figure.update_xaxes(visible=False)
    figure.update_yaxes(visible=False)
    return _base(figure)


def trend_figure(frame: pd.DataFrame, lang: str = "pt") -> go.Figure:
    if frame.empty:
        return empty_figure(lang=lang)
    figure = go.Figure()
    figure.add_trace(
        go.Scatter(
            x=frame["purchase_date"],
            y=frame["revenue"],
            mode="lines",
            name="Revenue" if lang == "en" else "Receita",
            line=dict(color=BLUE, width=2),
            fill="tozeroy",
            fillcolor="rgba(11,107,220,0.06)",
            hovertemplate=("%{x|%m/%d/%Y}<br>Revenue: R$ %{y:,.0f}<extra></extra>" if lang == "en" else "%{x|%d/%m/%Y}<br>Receita: R$ %{y:,.0f}<extra></extra>"),
        )
    )
    figure.update_yaxes(tickformat=",.0f")
    return _base(figure)


def horizontal_bar(frame: pd.DataFrame, color: str = BLUE, click_key: str | None = None, lang: str = "pt") -> go.Figure:
    if frame.empty:
        return empty_figure(lang=lang)
    ordered = frame.sort_values("revenue", ascending=True)
    figure = px.bar(ordered, x="revenue", y="dimension", orientation="h")
    labels = [_compact_currency(value, lang) for value in ordered["revenue"]]
    figure.update_traces(
        marker_color=color,
        customdata=ordered[["dimension", "orders", "customers"]],
        text=labels,
        textposition="outside",
        textfont=dict(color=NAVY, size=9),
        cliponaxis=False,
        hovertemplate=("%{customdata[0]}<br>Revenue: R$ %{x:,.0f}<br>Orders: %{customdata[1]:,.0f}<br>Customers: %{customdata[2]:,.0f}<extra></extra>" if lang == "en" else "%{customdata[0]}<br>Receita: R$ %{x:,.0f}<br>Pedidos: %{customdata[1]:,.0f}<br>Clientes: %{customdata[2]:,.0f}<extra></extra>"),
    )
    maximum = float(ordered["revenue"].max())
    figure.update_xaxes(title=None, tickprefix="R$ ", tickformat="~s", range=[0, maximum * 1.22 if maximum else 1])
    figure.update_yaxes(title=None)
    figure.update_layout(uniformtext_minsize=8, uniformtext_mode="show")
    return _base(figure, height=max(285, 74 + len(ordered) * 20), bottom_margin=38)


def payment_donut(frame: pd.DataFrame, lang: str = "pt") -> go.Figure:
    if frame.empty:
        return empty_figure(lang=lang)
    ordered = frame.copy()
    ordered["label"] = ordered["dimension"].map(PAYMENT_LABELS).fillna(ordered["dimension"])
    if lang == "en":
        ordered["label"] = ordered["dimension"].map({"credit_card": "Credit card", "boleto": "Bank slip", "debit_card": "Debit card", "voucher": "Voucher", "not_defined": "Not defined"}).fillna(ordered["dimension"])
    total = float(ordered["value"].sum())
    ordered["share"] = ordered["value"] / total if total else 0
    ordered = ordered.sort_values("share", ascending=True)
    figure = go.Figure(
        go.Bar(
            x=ordered["share"],
            y=ordered["label"],
            orientation="h",
            marker_color=BLUE,
            text=[f"{value:.0%}" for value in ordered["share"]],
            textposition="outside",
            textfont=dict(color=NAVY, size=9),
            cliponaxis=False,
            customdata=ordered[["value"]],
            hovertemplate=("%{y}<br>Share: %{x:.0%}<br>Payments: R$ %{customdata[0]:,.0f}<extra></extra>" if lang == "en" else "%{y}<br>Participação: %{x:.0%}<br>Pagamentos: R$ %{customdata[0]:,.0f}<extra></extra>"),
        )
    )
    figure.update_xaxes(range=[0, max(float(ordered["share"].max()) * 1.22, 0.1)], tickformat=".0%", showgrid=False)
    figure.update_yaxes(title=None)
    figure.update_layout(showlegend=False, uniformtext_minsize=8, uniformtext_mode="show")
    return _base(figure, height=max(285, 92 + len(ordered) * 34), bottom_margin=34)


def cohort_heatmap(frame: pd.DataFrame, lang: str = "pt") -> go.Figure:
    if frame.empty:
        return empty_figure(lang=lang)
    matrix = frame.pivot(index="cohort_month", columns="month_number", values="retention_rate").sort_index()
    figure = go.Figure(
        go.Heatmap(
            z=matrix.values,
            x=[f"M{int(column)}" for column in matrix.columns],
            y=[value.strftime("%Y-%m") for value in matrix.index],
            colorscale=[[0, "#eef5ff"], [0.45, "#84b8ec"], [1, NAVY]],
            zmin=0,
            zmax=1,
            text=[[f"{value:.0%}" if pd.notna(value) else "" for value in row] for row in matrix.values],
            texttemplate="%{text}",
            hovertemplate=(("Cohort" if lang == "en" else "Coorte") + " %{y}<br>%{x}: %{z:.0%}<extra></extra>"),
            colorbar=dict(title="Retention" if lang == "en" else "Retenção", tickformat=".0%"),
        )
    )
    return _base(figure, height=390, bottom_margin=42)


def segment_bar(frame: pd.DataFrame, lang: str = "pt") -> go.Figure:
    if frame.empty:
        return empty_figure(lang=lang)
    ordered = frame.sort_values("customers", ascending=True)
    figure = px.bar(ordered, x="customers", y="dimension", orientation="h")
    figure.update_traces(
        marker_color=TEAL,
        text=[_whole_number(value, lang) for value in ordered["customers"]],
        textposition="outside",
        textfont=dict(color=NAVY, size=9),
        cliponaxis=False,
        hovertemplate=("%{y}<br>Customers: %{x:,.0f}<extra></extra>" if lang == "en" else "%{y}<br>Clientes: %{x:,.0f}<extra></extra>"),
    )
    figure.update_yaxes(title=None)
    maximum = float(ordered["customers"].max())
    figure.update_xaxes(title=None, tickformat=",.0f", range=[0, maximum * 1.18 if maximum else 1])
    figure.update_layout(uniformtext_minsize=8, uniformtext_mode="show")
    return _base(figure, height=max(285, 82 + len(ordered) * 28), bottom_margin=38)
