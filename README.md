# Mercora Commerce Intelligence

An internal daily analytics application built from the anonymized Olist Brazilian e-commerce dataset. The case demonstrates how an analyst can turn operational CSV files into a governed decision product using Python, SQL, DuckDB, Dash and Plotly.

**Live demo:** [Mercora Commerce Intelligence](https://ba9ba428-78e2-4e6e-ac79-8a6dfe44fc99.plotly.app/)

The interface is available in Portuguese and English. Direct links may use `?page=revenue&lang=en`.

## Business problem

Commercial and operations leaders need one place to monitor revenue, repeat purchasing, delivery quality and the teams or categories behind each deviation. Mercora uses a selectable historical operating date so the 2016-2018 source is never presented as current data.

## Data flow

`Olist CSV -> Python ingestion -> DuckDB facts and dimensions -> SQL marts -> Dash application`

Orders, items and payments remain separate facts. Revenue is calculated from order items and aggregated before joins, preventing payment installments or multi-item orders from multiplying values.

## Application areas

- **Command Center:** daily situation, deviations and action queue.
- **Revenue Explorer:** category, geography, seller and payment mix.
- **Retention:** repeat purchasing, cohorts, RFM and recovery candidates.
- **Customer Explorer:** anonymous customer history and behavior.
- **Data Trust:** source lineage, tests, reconciliation and metric definitions.

![Mercora Command Center](docs/images/en/command.png)

Verified views: [Revenue Explorer](docs/images/en/revenue.png), [Retention](docs/images/en/retention.png), [Customer Explorer](docs/images/en/customers.png), and [Data Trust](docs/images/en/trust.png).

## Run locally

```powershell
copy .env.example .env
run.cmd -m pipeline download
run.cmd -m pipeline build
run.cmd -m pipeline validate
run.cmd -m pipeline capture
run.cmd -m pipeline package
run.cmd app.py
```

Open `http://127.0.0.1:8050`.

## Tests

```powershell
run.cmd -m pytest
```

The pipeline includes 14 deterministic quality checks covering revenue reconciliation, referential integrity, historical date boundaries, and the absence of sensitive columns. The suite covers metrics, filters, drill-down, internationalization, packaging, and application startup.

## Data and license

The source is the [Olist Brazilian E-Commerce Public Dataset](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce), licensed under CC BY-NC-SA 4.0. Raw CSV files are excluded from version control. Published artifacts contain anonymous analytical marts only and remain subject to the dataset license. This portfolio is non-commercial and is not affiliated with Olist.

See [metric definitions](docs/METRIC_DICTIONARY.md), [data model](docs/DATA_MODEL.md), [insights](docs/INSIGHTS.md), [demo and interview guide](docs/DEMO_GUIDE.md), and [deployment](docs/DEPLOYMENT.md).
