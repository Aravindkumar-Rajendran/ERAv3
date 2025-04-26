# Byte Pair Encoding for Tamil Language Corpus

This project implements a Byte Pair Encoding (BPE) tokenizer with saving/loading functionality.  
It also provides a Hugging Face Space app for testing the tokenizer.

## 🛠 Installation
1. Clone the repo

2. Install dependencies:
```pip install -r requirements.txt```

## 📖 Usage
### Train & Save Tokenizer
```python
from bpe.tokenizer import BPETokenizer

# Read training data
with open("data/corpus.txt", "r", encoding="utf-8") as f:
    corpus = [line.strip() for line in f if line.strip()]

tokenizer = BPETokenizer(num_merges=5000)
tokenizer.fit(corpus)
tokenizer.save("artifacts")
```
### Load and Run Tokenizer

```python
from bpe import BPETokenizer

tokenizer = BPETokenizer()
tokenizer.load("artifacts")

encoded = tokenizer.encode("hello")
print("Encoded:", encoded)

decoded = tokenizer.decode(encoded)
print("Decoded:", decoded)
```


---

### **🔹 How to Use**
1. **Train BPE on `corpus.txt`**
2. **Save `vocab.json` & `merges.txt`**
3. **Host tokenizer on Hugging Face Spaces using `app.py`**



---

## How to Deploy on Hugging Face Spaces

1. Push your repository (with the structure above) to a GitHub repository.
2. Create a new Space on [Hugging Face Spaces](https://huggingface.co/spaces) and connect it to your repository.
3. Hugging Face will automatically detect and run `app.py` using Gradio.

---

This example provides a minimal yet complete project for a BPE tokenizer along with a deployable web app. You can further improve the tokenizer (e.g., handling unknown tokens, more robust training, etc.) and customize the interface as needed. Happy coding!



