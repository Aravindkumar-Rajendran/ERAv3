# BPE4Tamil - Byte Pair Encoding for Tamil Text

A Python implementation of Byte Pair Encoding (BPE) specifically designed for Tamil text processing.

## Project Structure
```
BPE4Tamil/
├── README.md
├── requirements.txt
├── src/
│   ├── __init__.py
│   └── bpe.py
├── examples/
│   └── example_usage.py
├── data/
│   └── sample_texts/
│       └── tamil_sample.txt
└── tests/
    ├── __init__.py
    └── test_bpe.py
```

## Installation

```bash
git clone https://github.com/yourusername/BPE4Tamil.git
cd BPE4Tamil
pip install -r requirements.txt
```

## Usage

Basic usage example:

```python
from src.bpe import BytePairEncoder

# Initialize BPE
bpe = BytePairEncoder(num_merges=50)

# Load and prepare your Tamil text
with open('data/sample_texts/tamil_sample.txt', 'r', encoding='utf-8') as f:
    text = f.read()

# Train the BPE model
bpe.fit(text)

# Get encoding statistics
stats = bpe.get_stats(text)
print(f"Compression ratio: {stats['compression_ratio']:.2f}")
```

## Features

- Custom implementation of Byte Pair Encoding algorithm
- Specifically optimized for Tamil text
- Provides compression statistics
- Easy-to-use API
- Configurable number of merges

## Statistics Output

The encoder provides the following statistics:
- Original number of tokens
- Original character count
- Encoded token count
- Vocabulary size
- Compression ratio

## Requirements

- Python 3.7+
- collections
- typing

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## License

MIT License - feel free to use and modify as needed.