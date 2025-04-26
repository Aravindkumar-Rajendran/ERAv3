import gradio as gr
import sentencepiece as spm
import random
import html

def get_random_color():
    # Generate pastel colors for better readability
    return f"hsl({random.randint(0, 360)}, 70%, 80%)"

def tokenize_text(text):
    sp = spm.SentencePieceProcessor()
    sp.load('Tamil10k_BPE.model')
    
    # Get token IDs and convert to tokens
    ids = sp.encode(text)
    tokens = [sp.id_to_piece(idx) for idx in ids]
    
    # Create colored HTML output
    colored_tokens = []
    for token in tokens:
        color = get_random_color()
        colored_token = f'<span style="background-color: {color}; color: black; padding: 2px 4px; margin: 2px; border-radius: 3px;">{html.escape(token)}</span>'
        colored_tokens.append(colored_token)
    
    # Join tokens with spaces
    result_html = ' '.join(colored_tokens)
    
    # Return both the HTML visualization and the token list
    return f"Tokens: {tokens}\nIds: {ids}", result_html

# Example inputs
examples = [
    ["தமிழ் மொழி பற்றி அறிந்து கொள்ளுங்கள்"],
    ["வணக்கம் நண்பர்களே! எப்படி இருக்கிறீர்கள்?"],
    ["தமிழ் இலக்கியம் மிகவும் பழமையானது மற்றும் செழுமையானது"]
]

# Create Gradio interface
iface = gr.Interface(
    fn=tokenize_text,
    inputs=gr.Textbox(label="Enter Tamil Text", lines=3),
    outputs=[
        gr.Textbox(label="Token List"),
        gr.HTML(label="Tokenized Text (Colored)")
    ],
    examples=examples,
    title="TamilBPE-10k Tokenizer",
    description="Enter Tamil text to see how it's split into tokens using the TamilBPE-10k tokenizer.",
    theme=gr.themes.Soft(),
    allow_flagging="never"
)

if __name__ == "__main__":
    iface.launch()
