from dotenv import dotenv_values
import streamlit as st
from openai import OpenAI

# Użytkownik wpisuje swój klucz OpenAI
user_api_key = st.text_input("Wpisz swój klucz OpenAI", type="password")

# Sprawdzenie czy klucz został wpisany
if not user_api_key:
    st.warning("Musisz podać swój klucz OpenAI, aby wygenerować przepis.")
    st.stop()  # zatrzymuje dalsze działanie aplikacji, dopóki nie wpisze klucza

# Utworzenie klienta OpenAI
openai_client = OpenAI(api_key=user_api_key)

#env = dotenv_values(".env")

### Secrets using Streamlit Cloud Mechanism
# https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/secrets-management
if 'QDRANT_URL' in st.secrets:
    env['QDRANT_URL'] = st.secrets['QDRANT_URL']
if 'QDRANT_API_KEY' in st.secrets:
    env['QDRANT_API_KEY'] = st.secrets['QDRANT_API_KEY']
###

#openai_client = OpenAI(api_key=env["OPENAI_API_KEY"])


def streamlit_app():
    st.title("Generator przepisów Z tego co mam w lodówce")

    st.subheader("Wpisz nazwy produktów")
    product_name = st.text_input("Nazwy produktów", "")

    product_type_label = "Czy produkt ma być wytrawny czy deserem?"
    product_type = st.selectbox(product_type_label, ("Wytrawny", "Deser"))

    st.subheader("Produkty, na które jesteś uczulony")
    allergic_products = st.text_input(
        "Wpisz składniki", ""
    )

    if st.button("Stwórz przepis"):
        if product_name:
            recipe = generate_recipe(
                product_name,
                product_type,
                allergic_products
            )
            st.markdown(recipe)   
        else:
            st.write("Proszę wprowadź nazwy produktów")


def generate_recipe(product, product_type, allergic_products):

    allergy_info = (
        f"Użytkownik jest uczulony na: {allergic_products}. "
        "Bezwzględnie wyklucz te składniki z przepisu."
        if allergic_products
        else "Użytkownik nie zgłosił alergii pokarmowych."
    )

    prompt = f"""
Stwórz przepis na danie z następujących produktów: {product}.

Typ dania: {product_type}.

{allergy_info}

Jeśli typ to "Deser" - stwórz przepis na ciasto.
Jeśli typ to "Wytrawny" - stwórz danie główne obiadowe.

WAŻNE:
- Nie używaj żadnego składnika, na który użytkownik jest uczulony.
- Jeśli któryś z podanych produktów zawiera alergen, zaproponuj bezpieczną alternatywę.

Podaj:
- nazwę dania
- listę składników
- szacowany czas przygotowania
- instrukcję krok po kroku
- na końcu podsumuj ilość makroskładników (białko, wędlowodany, tłuszcze w gramach oraz procentowo w nawiasie) i ilość kalorii
"""

    response = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Jesteś profesjonalnym kucharzem i dbasz o bezpieczeństwo żywieniowe."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.6,
        max_tokens=600,
    )

    return response.choices[0].message.content


if __name__ == "__main__":
    streamlit_app()
