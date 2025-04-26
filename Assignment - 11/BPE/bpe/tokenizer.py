# bpe/tokenizer.py

import os
import json

class BPETokenizer:
    def __init__(self, num_merges=100):
        """
        Initialize the BPE tokenizer.
        :param num_merges: Maximum number of merge operations to perform during training.
        """
        self.num_merges = num_merges
        self.merges = []       # List of merge operations (each is a tuple of two symbols)
        self.token2id = {}     # Mapping from token string to unique id
        self.id2token = {}     # Inverse mapping from id to token

    def fit(self, corpus):
        """
        Train the BPE tokenizer on a corpus (list of words).
        Each word is split into characters.
        :param corpus: List of words (strings).
        """
        # Build initial vocabulary: each word is a tuple of characters
        vocab = {}
        for word in corpus:
            symbols = list(word)
            vocab[tuple(symbols)] = vocab.get(tuple(symbols), 0) + 1

        # Learn merge operations
        for i in range(self.num_merges):
            pairs = self.get_stats(vocab)
            if not pairs:
                break
            best = max(pairs, key=pairs.get)
            vocab = self.merge_vocab(best, vocab)
            self.merges.append(best)

        # Build final vocabulary tokens from the merged subword units
        tokens = set()
        for word in vocab:
            tokens.update(word)
        tokens = sorted(tokens)
        self.token2id = {token: idx for idx, token in enumerate(tokens)}
        self.id2token = {idx: token for token, idx in self.token2id.items()}

    def get_stats(self, vocab):
        """
        Count frequency of each adjacent symbol pair in the vocabulary.
        :param vocab: Dictionary with keys as tuples of symbols and values as frequency.
        :return: Dictionary mapping symbol pairs (tuple) to frequency.
        """
        stats = {}
        for word, freq in vocab.items():
            for i in range(len(word) - 1):
                pair = (word[i], word[i + 1])
                stats[pair] = stats.get(pair, 0) + freq
        return stats

    def merge_vocab(self, pair, vocab):
        """
        Merge all occurrences of the given pair in the vocabulary.
        :param pair: The symbol pair to merge (tuple of two strings).
        :param vocab: Current vocabulary.
        :return: New vocabulary with the pair merged.
        """
        merged_vocab = {}
        for word, freq in vocab.items():
            new_word = []
            i = 0
            while i < len(word):
                # If the pair is found, merge it
                if i < len(word) - 1 and (word[i], word[i + 1]) == pair:
                    new_word.append(word[i] + word[i + 1])
                    i += 2
                else:
                    new_word.append(word[i])
                    i += 1
            merged_vocab[tuple(new_word)] = freq
        return merged_vocab

    def get_pairs(self, symbols):
        """
        Get all adjacent symbol pairs from a list of symbols.
        :param symbols: List of symbols (strings).
        :return: A set of symbol pairs (tuples).
        """
        pairs = set()
        for i in range(len(symbols) - 1):
            pairs.add((symbols[i], symbols[i + 1]))
        return pairs

    def apply_merges(self, symbols):
        """
        Given a list of symbols (for a word), apply the learned merges.
        :param symbols: List of symbols representing a word.
        :return: List of merged symbols (subword tokens).
        """
        pairs = self.get_pairs(symbols)
        while True:
            merge_candidate = None
            # Process merges in the order they were learned
            for merge in self.merges:
                if merge in pairs:
                    merge_candidate = merge
                    break
            if merge_candidate is None:
                break

            new_symbols = []
            i = 0
            while i < len(symbols):
                if i < len(symbols) - 1 and (symbols[i], symbols[i + 1]) == merge_candidate:
                    new_symbols.append(symbols[i] + symbols[i + 1])
                    i += 2
                else:
                    new_symbols.append(symbols[i])
                    i += 1
            symbols = new_symbols
            pairs = self.get_pairs(symbols)
        return symbols

    def encode(self, text):
        """
        Encode an input string into a list of token ids.
        :param text: Input string (can be multiple words).
        :return: List of token ids.
        """
        token_ids = []
        for word in text.split():
            symbols = list(word)
            symbols = self.apply_merges(symbols)
            for token in symbols:
                token_id = self.token2id.get(token, self.token2id.get('<unk>'))
                token_ids.append(token_id)
            # Add a special token ID to mark word boundaries
            if len(token_ids) > 0:
                token_ids.append(-1)  # Use -1 as word boundary marker
        return token_ids[:-1]  # Remove the last boundary marker

    def decode(self, token_ids):
        """
        Decode a list of token ids back into a string.
        :param token_ids: List of token ids.
        :return: Decoded string.
        """
        decoded = ""
        current_word = ""
        
        for token_id in token_ids:
            if token_id == -1:
                # Word boundary reached
                decoded += current_word + " "
                current_word = ""
            else:
                token = self.id2token.get(token_id, '')
                current_word += token
        
        # Add the last word if exists
        if current_word:
            decoded += current_word
            
        return decoded.strip()

    def save(self, directory):
        """
        Save the tokenizer artifacts (vocab and merges) to files.
        :param directory: Directory where the artifacts will be stored.
        """
        if not os.path.exists(directory):
            os.makedirs(directory)
        vocab_path = os.path.join(directory, "vocab.json")
        merges_path = os.path.join(directory, "merges.txt")
        with open(vocab_path, "w", encoding="utf-8") as f:
            json.dump(self.token2id, f, ensure_ascii=False, indent=4)
        with open(merges_path, "w", encoding="utf-8") as f:
            for merge in self.merges:
                f.write(f"{merge[0]} {merge[1]}\n")

    def load(self, directory):
        """
        Load the tokenizer artifacts from files.
        :param directory: Directory where the artifacts are stored.
        """
        vocab_path = os.path.join(directory, "vocab.json")
        merges_path = os.path.join(directory, "merges.txt")
        with open(vocab_path, "r", encoding="utf-8") as f:
            self.token2id = json.load(f)
        # Ensure token ids are integers
        self.token2id = {k: int(v) for k, v in self.token2id.items()}
        self.id2token = {v: k for k, v in self.token2id.items()}
        self.merges = []
        if os.path.exists(merges_path):
            with open(merges_path, "r", encoding="utf-8") as f:
                for line in f:
                    parts = line.strip().split()
                    if len(parts) == 2:
                        self.merges.append(tuple(parts))
