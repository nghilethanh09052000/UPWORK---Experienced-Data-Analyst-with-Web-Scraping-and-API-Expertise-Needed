# UK Independent Training Providers (ITPs) Research Project

This project aims to build a comprehensive database of UK Independent Training Providers by collecting and analyzing data from multiple sources.

## Project Structure

```
project_root/
├── src/                    # Source code
│   ├── collectors/        # Data collection modules
│   ├── processors/        # Data processing modules
│   └── utils/            # Utility functions
├── config/                # Configuration files
├── data/                  # Data storage
│   ├── raw/              # Raw input data
│   ├── processed/        # Processed data
│   └── output/           # Final output
├── tests/                # Test files
└── scripts/              # Utility scripts
```

## Data Sources

1. Register of Apprenticeship Providers (APAR)
2. Ofsted inspection data
3. Companies House financial data
4. LinkedIn company data
5. Other sources (Apollo, SalesQL)

## Features

- Provider name and UKPRN tracking
- Owner and contact details collection
- Ofsted rating and inspection date tracking
- Financial data analysis (turnover, net profit)
- Regional breakdown and profit band categorization

## Setup

1. Create a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure settings:
- Copy `config/settings.example.py` to `config/settings.py`
- Update API keys and configuration settings

## Usage

Run the main script:
```bash
python main.py
```

## Data Processing Pipeline

1. Data Collection
   - APAR data collection
   - Ofsted inspection data retrieval
   - Companies House financial data extraction
   - LinkedIn data collection

2. Data Processing
   - Name standardization
   - Address cleaning
   - Financial data normalization
   - Region mapping
   - Profit band calculation

3. Data Enrichment
   - Contact information enrichment
   - Financial metrics calculation
   - Regional categorization
   - Quality scoring

## Output

The processed data is saved in two formats:
1. JSON file with detailed records
2. Excel file with summary statistics

## Testing

Run tests:
```bash
pytest
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request 