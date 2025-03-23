# Telegraph User Journey Analysis

A Python pipeline for analyzing user journeys on the Telegraph website to identify influential articles that lead to user registrations. This tool provides various attribution models to understand user behavior and content effectiveness.

## Features

- **Multiple Attribution Models**:
  - First Touch: Credits the first article in the user's journey
  - Last Touch: Credits the last article before registration
  - Linear: Distributes credit evenly across all articles
  - Position-based: Assigns different weights based on article position (40% first, 40% last, 20% middle)
  - Time Decay: Gives more credit to articles closer to registration
  - Count: Credits each article equally

- **Data Generation**:
  - Synthetic data generation for testing and development
  - Configurable parameters for users, articles, and registration rates
  - Realistic timestamp generation

## Project Structure

```
.
├── README.md
├── requirements.txt
├── src/
│   ├── __init__.py
│   └── pipeline.py
└── tests/
    ├── __init__.py
    └─ test_pipeline.py
```

## Requirements

- Python 3.8+
- pandas
- pytest (for testing)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd telegraph-analysis
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage

1. Generate synthetic data (optional):
```python
from src.pipeline import generate_synthetic_data

# Generate 1000 users, 50 articles, with 30% registration rate
df = generate_synthetic_data(
    num_users=1000,
    num_articles=50,
    registration_rate=0.3,
    output_path="synthetic_hitlog.csv"
)
```

2. Analyze user journeys:
```python
from src.pipeline import analyze_user_journeys

# Analyze with time decay attribution
results = analyze_user_journeys(
    "synthetic_hitlog.csv",
    attribution_method="time_decay",
    top_n=5
)
```

### Command Line Usage

Run the pipeline with default settings:
```bash
python src/pipeline.py
```

This will:
1. Generate synthetic data
2. Analyze the data using the count attribution method
3. Print the top 3 influential articles

## Testing

Run the test suite:
```bash
pytest
```

The tests cover:
- Data generation
- Attribution calculations
- Journey analysis
- Edge cases and error handling

## Attribution Methods

1. **Count**
   - Counts the number of occurrences of each article in a successfully registered user journey.

2. **First Touch**
   - Credits 100% to the first article in the journey
   - Best for understanding initial user acquisition

3. **Last Touch**
   - Credits 100% to the last article before registration
   - Best for identifying final conversion drivers

4. **Linear**
   - Distributes credit evenly across all articles
   - Best for understanding overall content effectiveness

5. **Position-based**
   - First article: 40%
   - Last article: 40%
   - Middle articles: 20%
   - Best for understanding the importance of position

6. **Time Decay**
   - Uses exponential decay based on position
   - Later articles receive more credit
   - Best for understanding recency effects
