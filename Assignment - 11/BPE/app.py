# app.py

import os
import gradio as gr
from bpe.tokenizer import BPETokenizer

# Initialize the tokenizer and load artifacts from the 'artifacts' directory.
tokenizer = BPETokenizer()
artifacts_dir = "artifacts"
if os.path.exists(artifacts_dir):
    tokenizer.load(artifacts_dir)
else:
    # If the artifacts are not present, print a warning.
    print("Artifacts not found. Please train the tokenizer and save the artifacts before launching the app.")

def process_text(input_text):
    """
    Tokenize and then decode the input text.
    Returns a string showing the tokens, token ids, and the decoded text.
    """
    token_ids = tokenizer.encode(input_text)
    tokens = [tokenizer.id2token.get(token_id, "<unk>") for token_id in token_ids]
    decoded_text = tokenizer.decode(token_ids)
    result = (
        f"Tokens: {' '.join(tokens)}\n\n"
        f"Token IDs: {token_ids}\n\n"
        f"Decoded Text: {decoded_text}"
    )
    return result

# Create the Gradio interface.
iface = gr.Interface(
    fn=process_text,
    inputs=gr.components.Textbox(lines=5, label="Input Text"),
    outputs=gr.components.Textbox(label="Output"),
    title="BPE Tokenizer",
    description="Enter text to see the BPE tokenization, token ids, and decoded output."
)

if __name__ == "__main__":
    iface.launch()
