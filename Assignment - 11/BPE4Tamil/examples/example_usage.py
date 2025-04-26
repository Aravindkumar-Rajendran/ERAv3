import os
import sys
from pathlib import Path

# Add the project root directory to Python path
project_root = str(Path(__file__).parent.parent)
sys.path.append(project_root)

from src.bpe import BytePairEncoder

# Example Tamil text (you can replace this with your own text)
tamil_text = """
வணக்கம் உலகம்
தமிழ் மொழி மிகவும் பழமையானது
நான் தமிழ் படிக்கிறேன்
"""

# Train the tokenizer
bpe = BytePairEncoder(num_merges=100)
bpe.fit(tamil_text)


# Save the tokenizer
bpe.save('tamil_tokenizer.json')

# Load the saved tokenizer
loaded_bpe = BytePairEncoder.load('tamil_tokenizer.json')

# Display vocabulary statistics
print("\nFull Vocabulary:")
loaded_bpe.print_vocabulary()

print("\nTop 10 most frequent tokens:")
loaded_bpe.print_vocabulary(top_k=10)


# Test text for the loaded tokenizer
test_text = "வணக்கம் தமிழ்"

# Compare original and loaded tokenizer results
original_encoded = bpe.encode(test_text)
loaded_encoded = loaded_bpe.encode(test_text)

print("\nTesting saved/loaded tokenizer:")
print(f"Original tokenizer output: {original_encoded}")
print(f"Loaded tokenizer output: {loaded_encoded}")
print(f"Outputs match: {original_encoded == loaded_encoded}")

# Test decode with loaded tokenizer
decoded = loaded_bpe.decode(loaded_encoded)
print(f"\nDecoded text: {decoded}")
print(f"Decoding successful: {decoded == test_text}")

# Add after existing code:
print("\nTesting decoder performance:")
# Create a larger test text by repeating the original
large_test = tamil_text * 100
print(f"Test text size: {len(large_test)} characters")

import time
start_time = time.time()
encoded_large = loaded_bpe.encode(large_test)
print(f"Encoding time: {time.time() - start_time:.2f} seconds")

start_time = time.time()
decoded_large = loaded_bpe.decode(encoded_large)
print(f"Decoding time: {time.time() - start_time:.2f} seconds")
print(f"Decoded text matches original: {decoded_large == large_test}")

# After the existing performance test, add these verification steps:
print("\nDetailed verification:")
print("Original text:", repr(test_text))
encoded = loaded_bpe.encode(test_text)
print("Encoded tokens:", encoded)
decoded = loaded_bpe.decode(encoded)
print("Decoded text:", repr(decoded))

# Test with different types of input
test_cases = [
    "வணக்கம்",  # Single word
    "வணக்கம் உலகம்",  # Two words
    "\n",  # Just newline
    " ",  # Just space
    "தமிழ் ",  # Word with trailing space
    " தமிழ்",  # Word with leading space
]

print("\nTesting various cases:")
for test in test_cases:
    encoded = loaded_bpe.encode(test)
    decoded = loaded_bpe.decode(encoded)
    print(f"\nTest: {repr(test)}")
    print(f"Encoded: {encoded}")
    print(f"Decoded: {repr(decoded)}")
    print(f"Match: {test == decoded}")
