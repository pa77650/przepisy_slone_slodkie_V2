from dotenv import dotenv_values
import streamlit as st
from openai import OpenAI
import base64

# Użytkownik wpisuje swój klucz OpenAI
user_api_key = st.text_input("Wpisz swój klucz OpenAI", type="password")

# Sprawdzenie czy klucz został wpisany
if not user_api_key:
    st.warning("Musisz podać swój klucz OpenAI, aby wygenerować przepis.")
    st.stop()  # zatrzymuje dalsze działanie aplikacji, dopóki nie wpisze klucza

# Utworzenie klienta OpenAI
openai_client = OpenAI(api_key=user_api_key)

env = dotenv_values(".env")
# ### Secrets using Streamlit Cloud Mechanism
# # https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/secrets-management
# if 'QDRANT_URL' in st.secrets:
#     env['QDRANT_URL'] = st.secrets['QDRANT_URL']
# if 'QDRANT_API_KEY' in st.secrets:
#     env['QDRANT_API_KEY'] = st.secrets['QDRANT_API_KEY']
# ###

#openai_client = OpenAI(api_key=env["OPENAI_API_KEY"])


def streamlit_app():
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.image("plate", width=150)

    st.title("Generator przepisów z tego co mam w lodówce")

    st.subheader("Wpisz nazwy produktów (opcjonalne)")
    product_name = st.text_input("Nazwy produktów", "")

    st.subheader("Lub wrzuć zdjęcie produktów")
    uploaded_file = st.file_uploader(
        "Dodaj zdjęcie (jpg/png)", 
        type=["jpg", "jpeg", "png"]
    )

    product_type = st.selectbox(
        "Czy produkt ma być wytrawny czy deserem?",
        ("Wytrawny", "Deser")
    )

    allergic_products = st.text_input(
        "Produkty, na które jesteś uczulony",
        ""
    )

    if st.button("Stwórz przepis"):

        if not product_name and not uploaded_file:
            st.warning("Podaj składniki lub dodaj zdjęcie.")
            return

        recipe = generate_recipe(
            product_name,
            product_type,
            allergic_products,
            uploaded_file
        )

        st.markdown(recipe)


def generate_recipe(product, product_type, allergic_products, uploaded_file):

    allergy_info = (
        f"Użytkownik jest uczulony na: {allergic_products}. "
        "Bezwzględnie wyklucz te składniki z przepisu."
        if allergic_products
        else "Użytkownik nie zgłosił alergii pokarmowych."
    )

    prompt = f"""
Stwórz przepis na podstawie dostarczonych informacji.

Tekstowe składniki: {product}

Typ dania: {product_type}

{allergy_info}

Jeśli typ to "Deser" - stwórz przepis na ciasto.
Jeśli typ to "Wytrawny" - stwórz danie główne obiadowe.

Podaj:
- nazwę dania
- listę składników
- szacowany czas przygotowania
- instrukcję krok po kroku
- makroskładniki i kalorie
"""

    content = [
        {"type": "text", "text": prompt}
    ]

    # Jeśli użytkownik dodał zdjęcie
    if uploaded_file is not None:
        image_bytes = uploaded_file.read()
        base64_image = base64.b64encode(image_bytes).decode("utf-8")

        content.append({
            "type": "image_url",
            "image_url": {
                "url": f"data:image/jpeg;base64,{base64_image}"
            }
        })

    response = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "Jesteś profesjonalnym kucharzem i analizujesz również zdjęcia produktów."
            },
            {
                "role": "user",
                "content": content
            }
        ],
        max_tokens=800,
        temperature=0.6,
    )

    return response.choices[0].message.content


if __name__ == "__main__":
    streamlit_app()
