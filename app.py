import streamlit as st
from functions import (
    extract_text_from_image,
    extract_functions_and_constraints,
    optimize_problem,
)


def main():
    st.title("Optimisation des problèmes de recherche opérationnelle")

    uploaded_file = st.file_uploader(
        "Téléchargez une image contenant le sujet", type=["jpg", "png", "jpeg"]
    )

    if uploaded_file is not None:
        try:
            # Extraire le texte de l'image
            text = extract_text_from_image(uploaded_file)
            st.write("Texte extrait de l'image :")
            st.write(text)
            print("Texte extrait de l'image :", text)  # Débogage

            # Extraire les fonctions objectives et les contraintes
            functions_and_constraints = extract_functions_and_constraints(text)
            st.write("Fonctions objectives et contraintes extraites :")
            st.write(functions_and_constraints.values())

            # Optimiser le problème en utilisant les fonctions et contraintes extraites
            optimization_result = optimize_problem(functions_and_constraints)


            print("Résultat de l'optimisation :", optimization_result)  # sur la console

            if optimization_result:
                optimal_values, optimal_objective = optimization_result
                if optimal_values is not None:
                    st.write("Valeurs optimales :")
                    for var, val in optimal_values.items():
                        st.write(f"{var} : {val}")
                    st.write(
                        f"Valeur optimale de la fonction objective : {optimal_objective}"
                    )
                else:
                    st.error("Aucune solution optimale n'a été trouvée.")
            else:
                st.error("Erreur dans l'optimisation du problème.")
        except Exception as e:
            st.error(f"Erreur : {e}")


if __name__ == "__main__":
    main()