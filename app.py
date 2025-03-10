import pandas as pd
import numpy as np
import os
import streamlit as st
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences

# Define file paths
MODEL_PATH = "roman_urdu_lstm_model.h5"
DATA_PATH = "Roman-Urdu-Poetry.csv"

# Check if dataset exists
if not os.path.exists(DATA_PATH):
    st.error(f"Dataset file '{DATA_PATH}' not found! Please upload it.")
    st.stop()

# Load dataset
poetry_df = pd.read_csv(DATA_PATH)  # Ensure CSV file is available

# Initialize and fit the tokenizer
tokenizer = Tokenizer()
tokenizer.fit_on_texts(poetry_df['Poetry'])  # Assuming 'Poetry' is the column

# Check if model exists before loading
if not os.path.exists(MODEL_PATH):
    st.error(f"Model file '{MODEL_PATH}' not found! Please upload it.")
    st.stop()

# Load the pre-trained model
model = load_model(MODEL_PATH)

# Function to generate poetry in stanzas
def generate_poetry(model, tokenizer, start_word, num_stanzas=2, num_words_per_line=6):
    poem = ""
    sequence = tokenizer.texts_to_sequences([start_word])
    sequence = pad_sequences(sequence, maxlen=model.input_shape[1], padding='pre')

    for stanza in range(num_stanzas):
        stanza_text = ""

        for line_num in range(2):  # Two lines per stanza
            line = start_word if stanza == 0 and line_num == 0 else ""  # Start word only for first line

            for _ in range(num_words_per_line - (1 if line else 0)):  # Adjust for first word
                pred_probs = model.predict(sequence)[0]
                predicted_word_index = np.argmax(pred_probs)
                predicted_word = tokenizer.index_word.get(predicted_word_index, "")

                if not predicted_word:
                    predicted_word = "..."  # Placeholder if model fails

                line += ' ' + predicted_word
                sequence = np.append(sequence[:, 1:], predicted_word_index).reshape(1, -1)

            stanza_text += line.strip() + '\n'

        poem += stanza_text.strip() + '\n\n'  # Ensure correct spacing

    return poem.strip()  # Remove trailing newlines

# Streamlit UI
st.title("✨ Urdu Poetry Generator 🎤")
st.write("Generate **beautiful Urdu poetry** in stanza format!")

start_word = st.text_input("🌟 Enter the starting word:", value="")
num_stanzas = st.slider("📜 Number of stanzas:", min_value=1, max_value=5, value=2)
num_words_per_line = st.slider("✍️ Words per line:", min_value=5, max_value=20, value=6)

# Generate poetry when button is clicked
if st.button("📝 Generate Poetry"):
    if start_word:
        generated_poem = generate_poetry(model, tokenizer, start_word, num_stanzas, num_words_per_line)
        st.subheader("🎶 Generated Poetry:")
        st.text(generated_poem)
    else:
        st.error("🚨 Please enter a starting word!")
