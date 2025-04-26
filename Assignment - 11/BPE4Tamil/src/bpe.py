from collections import defaultdict, Counter
from typing import Dict, List, Tuple
import re
import json

class BytePairEncoder:
    def __init__(self, num_merges: int = 10):
        self.num_merges = num_merges
        self.vocab = {}
        self.merge_rules = {}
        self.inverse_merge_rules = {}  # Add this line to store inverse mappings
        
    def fit(self, text: str) -> None:
        # Initialize vocabulary with characters
        word_freqs = Counter(text.split())
        
        # Convert words into sequence of characters
        splits = {word: list(word) for word in word_freqs.keys()}
        
        # Perform merges
        for i in range(self.num_merges):
            # Count pair frequencies
            pair_freqs = defaultdict(int)
            for word, freq in word_freqs.items():
                chars = splits[word]
                for j in range(len(chars)-1):
                    pair = (chars[j], chars[j+1])
                    pair_freqs[pair] += freq
            
            if not pair_freqs:
                break
                
            # Find most frequent pair
            best_pair = max(pair_freqs.items(), key=lambda x: x[1])[0]
            
            # Add merge rule
            self.merge_rules[best_pair] = ''.join(best_pair)
            self.inverse_merge_rules[''.join(best_pair)] = best_pair  # Add this line
            
            # Apply the merge
            new_splits = {}
            for word in splits:
                chars = splits[word]
                while True:
                    # Find first occurrence of pair
                    for i in range(len(chars)-1):
                        if tuple(chars[i:i+2]) == best_pair:
                            chars = chars[:i] + [self.merge_rules[best_pair]] + chars[i+2:]
                            break
                    else:
                        break
                new_splits[word] = chars
            splits = new_splits

        # Store final vocabulary
        self.vocab = {token for splits_list in splits.values() for token in splits_list}

    def encode(self, text: str) -> List[str]:
        words = text.split()
        encoded_words = []
        
        for word in words:
            chars = list(word)
            while True:
                changed = False
                for i in range(len(chars)-1):
                    pair = tuple(chars[i:i+2])
                    if pair in self.merge_rules:
                        chars = chars[:i] + [self.merge_rules[pair]] + chars[i+2:]
                        changed = True
                        break
                if not changed:
                    break
            encoded_words.extend(chars)
        
        return encoded_words

    def decode(self, tokens: List[str]) -> str:
        """
        Decode the encoded tokens back to original text with spaces between words.
        Args:
            tokens: List of encoded tokens
        Returns:
            Decoded text string
        """
        decoded_parts = []
        current_word = []
        decode_cache = {}
        
        def decode_token(token):
            if token in decode_cache:
                return decode_cache[token]
                
            # Start with the token itself
            result = token
            
            # Keep track of processed tokens to prevent infinite loops
            processed = set()
            
            # Continue splitting until no more splits are possible
            while result in self.inverse_merge_rules and result not in processed:
                processed.add(result)
                pair = self.inverse_merge_rules[result]
                result = ''.join(pair)
                
            decode_cache[token] = result
            return result
        
        # Process each token
        for token in tokens:
            decoded_token = decode_token(token)
            
            # If we find a space, it marks a word boundary
            if decoded_token.isspace():
                if current_word:
                    decoded_parts.append(''.join(current_word))
                    current_word = []
                decoded_parts.append(decoded_token)
            else:
                current_word.append(decoded_token)
        
        # Add the last word if exists
        if current_word:
            decoded_parts.append(''.join(current_word))
            
        return ''.join(decoded_parts)

    def get_stats(self, text: str) -> Dict:
        original_tokens = len(text.split())
        original_chars = len(text)
        
        encoded = self.encode(text)
        encoded_tokens = len(encoded)
        
        return {
            'original_tokens': original_tokens,
            'original_chars': original_chars,
            'encoded_tokens': encoded_tokens,
            'compression_ratio': original_chars / (encoded_tokens * 2),  # assuming 2 bytes per token
            'vocabulary_size': len(self.vocab)
        }

    def save(self, filepath: str) -> None:
        """Save the trained tokenizer to a file"""
        model_data = {
            'num_merges': self.num_merges,
            'vocab': list(self.vocab),
            'merge_rules': {str(k): v for k, v in self.merge_rules.items()},
            'inverse_merge_rules': {k: list(v) for k, v in self.inverse_merge_rules.items()}
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(model_data, f, ensure_ascii=False, indent=2)
    
    @classmethod
    def load(cls, filepath: str) -> 'BytePairEncoder':
        """Load a trained tokenizer from a file"""
        with open(filepath, 'r', encoding='utf-8') as f:
            model_data = json.load(f)
            
        instance = cls(num_merges=model_data['num_merges'])
        instance.vocab = set(model_data['vocab'])
        instance.merge_rules = {tuple(eval(k)): v for k, v in model_data['merge_rules'].items()}
        instance.inverse_merge_rules = {k: tuple(v) for k, v in model_data['inverse_merge_rules'].items()}
        
        return instance

    def get_vocabulary(self) -> Dict[str, int]:
        """
        Returns a dictionary of vocabulary items with their frequency in merge rules.
        Returns:
            Dictionary with tokens as keys and their usage frequency as values
        """
        vocab_freq = defaultdict(int)
        
        # Count occurrences in merge rules
        for token in self.vocab:
            vocab_freq[token] = sum(1 for v in self.merge_rules.values() if v == token)
            
        # Add tokens that only appear as basic characters
        for token in self.vocab:
            if token not in vocab_freq:
                vocab_freq[token] = 0
                
        return dict(sorted(vocab_freq.items(), key=lambda x: x[1], reverse=True))

    def print_vocabulary(self, top_k: int = None) -> None:
        """
        Print vocabulary items sorted by their frequency.
        Args:
            top_k: Optional number of top items to show. If None, shows all.
        """
        vocab_freq = self.get_vocabulary()
        items = list(vocab_freq.items())
        
        if top_k:
            items = items[:top_k]
            
        print(f"\nVocabulary Size: {len(self.vocab)}")
        print("\nToken Frequencies:")
        print("-" * 30)
        for token, freq in items:
            print(f"Token: {token:15} Frequency: {freq}")
        print("-" * 30)
