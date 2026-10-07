# Public Transfers to Non-Profits: São Paulo Metro West

An interactive dashboard that analyzes public money paid by municipal
governments to third-sector organizations (non-profits) in the western part of
Greater São Paulo, Brazil.

The dataset holds 7,711 payment records from 2019 to 2024 across six
municipalities: Barueri, Carapicuíba, Taboão da Serra, Cotia, Itapevi and
Jandira.

## Questions it answers

- How did the amount transferred change year over year?
- Which government functions receive the most?
- Which organizations receive the most, and how concentrated is the spending?
- How does one municipality compare with its neighbors?

## Pages

| Page | Content |
| --- | --- |
| Main dashboard | Cotia: totals, yearly evolution, distribution by government function, top recipients, value statistics |
| Tables | Raw records with breakdowns by year, function and organization |
| Comparison | Side-by-side metrics, yearly evolution, function distribution and top recipients across municipalities |

## Stack

Python, Streamlit, pandas, Plotly, NumPy.

## Running it

```bash
git clone https://github.com/VicktzZ/analise-repasses-sp
cd analise-repasses-sp
pip install -r requirements.txt
streamlit run dashboard.py
```

## Project layout

```
dashboard.py            Main page
pages/                  Tables and comparison pages
utils/data_manager.py   Cached loading, filtering and currency formatting
scripts/cotia.py        Standalone exploratory analysis
data/repasses.xlsx      Source records
```

## Data

Each record carries the fiscal year, municipality, paying body, recipient
organization (name and CNPJ), government function, transfer type, funding
source and amount paid.

The interface is in Portuguese.
