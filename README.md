# CS 361 Portfolio Project — Person Generator & Life Generator

Two independent Python microservices that communicate asynchronously via RabbitMQ.

## Overview

| Microservice | Role | Description |
|---|---|---|
| `ppl-generator_consumer_refactored.py` | Consumer | Samples random street addresses from U.S. state datasets |
| `life-generator_producer.py` | Producer | Returns top-rated toy products for a selected category |

Each service runs independently and exchanges messages through RabbitMQ queues:

```
Life Generator ──[life_gen queue]──► Person Generator
Person Generator ──[ppl_gen queue]──► Life Generator
```

## Requirements

- Python 3.7+
- [RabbitMQ](https://www.rabbitmq.com/download.html) running on `localhost`

Install Python dependencies:
```
pip install -r requirements.txt
```

## Data Setup

Two datasets are required (not included due to size — download from Kaggle):

- **State address data** (Person Generator): [OpenAddresses US West](https://www.kaggle.com/datasets/openaddresses/openaddresses-us-west)
  - Extract the per-state `.csv` files (e.g. `WA.csv`, `CA.csv`)
- **Amazon toy products** (Life Generator): [Toy Products on Amazon](https://www.kaggle.com/datasets/PromptCloudHQ/toy-products-on-amazon)
  - File: `amazon_co-ecommerce_sample.csv`

By default the programs look for data files in the same directory as the scripts. To use a different location, set the `DATA_DIR` environment variable:

```bash
# Windows
set DATA_DIR=C:\path\to\data

# macOS / Linux
export DATA_DIR=/path/to/data
```

## Usage

### With GUI

```bash
python ppl-generator_consumer_refactored.py   # Person Generator
python life-generator_producer.py             # Life Generator
```

### With input file (no GUI interaction)

```bash
python ppl-generator_consumer_refactored.py input_ppl.csv
python life-generator_producer.py input.csv
```

Input file formats:

**`input_ppl.csv`** (Person Generator):
```
input_state,input_number_to_generate
HI,400
```

**`input.csv`** (Life Generator):
```
input_item_type,input_item_category,input_number_to_generate
toys,Arts & Crafts,10
```

## Output

- Person Generator writes `output_people_gen.csv`
- Life Generator writes `output.csv`
