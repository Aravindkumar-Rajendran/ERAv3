from bpe import BytePairEncoder

def test_bpe_training():
	# Test data
	text = """வணக்கம் உலகம்
தமிழ் மொழி மிகவும் பழமையானது
நான் தமிழ் படிக்கிறேன்."""
	
	# Initialize and train BPE
	bpe = BytePairEncoder(num_merges=10)
	bpe.fit(text)
	
	# Verify training results
	print("Training Results:")
	print("-" * 50)
	
	# 1. Check if vocabulary was created
	print(f"Vocabulary size: {len(bpe.vocab)}")
	print("\nVocabulary items:")
	bpe.print_vocabulary(top_k=10)
	
	# 2. Test encoding
	encoded = bpe.encode(text)
	print("\nEncoded text (first 10 tokens):")
	print(encoded[:10])
	
	# 3. Test decoding
	decoded = bpe.decode(encoded)
	print("\nDecoded text:")
	print(decoded)
	
	# 4. Verify compression stats
	stats = bpe.get_stats(text)
	print("\nCompression Statistics:")
	for key, value in stats.items():
		print(f"{key}: {value}")
	
	# 5. Test save and load functionality
	bpe.save("test_model.json")
	loaded_bpe = BytePairEncoder.load("test_model.json")
	
	# Verify loaded model produces same results
	loaded_encoded = loaded_bpe.encode(text)
	assert encoded == loaded_encoded, "Loaded model produces different encodings"
	print("\nModel save/load test passed!")

if __name__ == "__main__":
	test_bpe_training()