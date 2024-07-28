import json
import re
from altair import value
from pyomo.environ import (
    ConcreteModel,
    Var,
    Objective,
    Constraint,
    SolverFactory,
    NonNegativeReals,
    maximize,
)
from os import getenv
from dotenv import load_dotenv

load_dotenv()


from PIL import Image
import pytesseract
import google.generativeai as genai


# Extraction du texte de l'image
def extract_text_from_image(image_path):
    image = Image.open(image_path)
    text = pytesseract.image_to_string(image)
    return text


# Configuration des informations d'authentification pour l'API de Gemini Provision
genai.configure(api_key=getenv("GOOGLE_API_KEY"))


def extract_functions_and_constraints(text):
    input_text = """
    Solve this problem by following the instructions below:
    - Put on the first line the objective function
    example:
        Max ax + by + c 
    - Put next the constraints functions
    example: 
        Constraints: 
            inequalities systems
    """

    input_prompt1 = """
    You are an expert in solving operational research problems. Please give the 
    mathematics equation to solve the problem in the picture. Don't tell anything else
    apart from the mathematics equation, don't give any solution.
    Your output must be:
        first: always a maximization objective function, and if the problem is a minimization
        case, do the necessary transformation to change it into a maximization objective function.
        second: All the constraints must be less than or equal constraints, and if it is a greater than or
        equal constraint, do the necessary transformation to change it into less than or equal except the 
        positivity constraint.
    """

    # Combiner le texte extrait de l'image avec les instructions et le prompt
    prompt = input_text + text + input_prompt1

    # Appeler l'API pour générer les fonctions objectives et les contraintes
    response = genai.generate_text(prompt=prompt)

    # Traitement de la réponse de l'API pour extraire les données nécessaires
    print(response.result)
    return parse_response(json.dumps(response.result))


def parse_response(response):
    response_dict = {}

    # Utilisation d'une expression régulière pour trouver la fonction objective dans la réponse
    obj_match = re.search(r"Max\s+([\d\w\s\+\-]+)", response)
    if obj_match:
        # Si une correspondance est trouvée, extraire la chaîne de caractères représentant la fonction objective
        objective_str = obj_match.group(1).strip()
        # Utiliser une autre expression régulière pour trouver tous les termes de la fonction objective
        terms = re.findall(r"(\d+)([a-zA-Z]+)", objective_str)
        # Construire un dictionnaire où les clés sont les variables (par ex. 'x1', 'x2') et les valeurs sont les coefficients (par ex. 2, 3)
        response_dict["objective"] = {term[1]: int(term[0]) for term in terms}

    # Extraction des contraintes
    constraints = {}
    all_vars = set(response_dict["objective"].keys())
    constraint_matches = re.findall(r"([\d\w\s\+\-]+)\s*(<=|>=)\s*(\d+)", response)
    for i, cstr in enumerate(constraint_matches):
        lhs, operator, rhs = cstr
        terms = re.findall(r"(\d*)([a-zA-Z]+)", lhs)
        constraint = {term[1]: int(term[0] if term[0] else 1) for term in terms}
        all_vars.update(constraint.keys())
        constraint["rhs"] = int(rhs)
        constraint["operator"] = operator
        constraints[f"constraint_{i+1}"] = constraint

    response_dict.update(constraints)
    response_dict["all_vars"] = list(
        all_vars
    )  # Ajouter toutes les variables collectées
    return response_dict


# Optimisation des problèmes
def optimize_problem(functions_and_constraints):
    model = ConcreteModel()
    all_vars = set()

    # Collecter tous les noms de variables utilisés dans l'objectif et les contraintes
    for key, expr in functions_and_constraints.items():
        for var in expr:
            if var not in ["rhs", "operator"]:
                all_vars.add(var)

    # Définir les variables dans le modèle
    model_vars = {var: Var(domain=NonNegativeReals) for var in all_vars}
    for var, var_obj in model_vars.items():
        setattr(model, var, var_obj)

    # Définir l'objectif
    objective = functions_and_constraints.get("objective", {})
    model.objective = Objective(
        expr=sum(coef * model_vars[var] for var, coef in objective.items()),
        sense=maximize,
    )

    # Définir les contraintes
    constraints = {
        name: con
        for name, con in functions_and_constraints.items()
        if name.startswith("constraint")
    }
    for name, constraint in constraints.items():
        expr_terms = []
        for var, coef in constraint.items():
            if var not in ["rhs", "operator"]:
                expr_terms.append(coef * model_vars[var])
        expr = sum(expr_terms)
        rhs = constraint["rhs"]
        if constraint.get("operator") == ">=":
            constraint_obj = Constraint(expr=(expr >= rhs))
        else:
            constraint_obj = Constraint(expr=(expr <= rhs))
        setattr(model, f"constraint_{name}", constraint_obj)

    # Résoudre le problème
    solver = SolverFactory("glpk", executable=getenv("GLPK_PATH"))
    result = solver.solve(model)

    # Vérifier si le solveur a trouvé une solution optimale
    if result.solver.termination_condition == "optimal":
        optimal_values = {var: value(var_obj) for var, var_obj in model_vars.items()}
        optimal_objective = value(model.objective)
        return optimal_values, optimal_objective
    else:
        print("Le solveur n'a pas trouvé de solution optimale.")
        return None, None
