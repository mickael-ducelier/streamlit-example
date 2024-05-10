import streamlit as st
from PyPDF2 import PdfReader
from openai import OpenAI
import os

# Définissez votre clé API OpenAI ici
OPENAI_API_KEY = ""


def extract_text_from_pdf_using_pypdf2(pdf_file_path):
    reader = PdfReader(pdf_file_path)
    pages_text = [page.extract_text() + "\n" for page in reader.pages if page.extract_text()]
    return pages_text

def generate_script_for_each_page(pages_text, tonality, target, objectif,openai_api_key, progress_bar ):
    OPENAI_API_KEY = openai_api_key
    client = OpenAI(api_key=OPENAI_API_KEY)
    context_memory = set()
    scripts = []
    for i, page_text in enumerate(pages_text, start=1):
        prompt = (
            f"Sur la base du contenu suivant de la page {i}, en évitant de répéter les sujets déjà abordés {context_memory}, "
            f"créez un script de 1000 mots {tonality} pour les {target} qui doivent connaître {objectif}"
            f"Le script doit contenir seulement le texte dit par le narrateur. :\n\n{page_text}"
        )

        
        response = client.chat.completions.create(model="gpt-3.5-turbo",
        messages=[{"role": "system", "content": prompt}],
        max_tokens=1024)
        script = response.choices[0].message.content.strip()
        scripts.append((i, script))
        update_context_memory(page_text, context_memory)

        # Update progress bar after each script is generated
        progress_bar.progress(i / len(pages_text))
    return scripts

def update_context_memory(page_text, context_memory):
    # Simulez l'extraction des thèmes ou des mots clés pour la mise à jour de la mémoire
    words = page_text.split()
    for word in words:
        if word.lower() in ['bail', 'commercial', 'locataire', 'propriétaire']:  # Exemple simpliste
            context_memory.add(word.lower())

def save_scripts_to_txt(scripts):
    txt_file_name = "generated_scripts.txt"
    with open(txt_file_name, "w", encoding="utf-8") as txt_file:
        for page_number, script in scripts:
            txt_file.write(f"Script pour la page {page_number} :\n{script}\n\n")
    return txt_file_name

st.title("Générateur de script à partir d'un PDF ")

# Inputs for script parameters
tonality = st.text_input("Entrer le ton du script ")
target = st.text_input("Entrer la cible du script :")
objective = st.text_input("Entrer les objectifs du script :")

uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")
if uploaded_file is not None:
    pdf_file_path = "temp_uploaded_file.pdf"
    with open(pdf_file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    pages_text = extract_text_from_pdf_using_pypdf2(pdf_file_path)
    openai_api_key = st.text_input("Enter your OpenAI API Key", type="password")


    if st.button("Générer le script") and openai_api_key and tonality and target and objective:
        progress_bar = st.progress(0)  # Initialize the progress bar
        with st.spinner('Génération du script en cours...'):
            scripts = generate_script_for_each_page(pages_text, tonality, target, objective,openai_api_key, progress_bar)
            txt_file_name = save_scripts_to_txt(scripts)
            st.success("Le script est généré !")
            with open(txt_file_name, "rb") as file:
                btn = st.download_button(
                    label="Télécharger le script en format .txt",
                    data=file,
                    file_name="generated_scripts.txt",
                    mime="text/plain"
                )

    if os.path.exists(pdf_file_path):
        os.remove(pdf_file_path)
