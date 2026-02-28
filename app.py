from dotenv import dotenv_values
import streamlit as st
from openai import OpenAI

env = dotenv_values(".env")
openai_client = OpenAI(api_key=env["OPENAI_API_KEY"])


def streamlit_app():
    st.title("Generator przepisów")

    st.subheader("Wpisz nazwy produktów")
    product_name = st.text_input("Nazwy produktów", "")

    product_type_label = "Czy produkt jest słodki bądź wytrawny?"
    product_type = st.selectbox(product_type_label, ("Słodki", "Wytrawny"))

    st.subheader("Produkty, na które jesteś uczulony (opcjonalnie)")
    allergic_products = st.text_input(
        "Wpisz składniki oddzielone przecinkami", ""
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

Jeśli typ to "Słodki" – stwórz przepis na ciasto.
Jeśli typ to "Wytrawny" – stwórz danie główne obiadowe.

WAŻNE:
- Nie używaj żadnego składnika, na który użytkownik jest uczulony.
- Jeśli któryś z podanych produktów zawiera alergen, zaproponuj bezpieczną alternatywę.

Podaj:
- nazwę dania
- listę składników
- instrukcję krok po kroku
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