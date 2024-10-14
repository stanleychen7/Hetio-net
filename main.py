import sys
from py2neo import Graph
import tkinter as tk

def main():
    graph = None
    while True:
        user_input = input ("Enter 1 to start, 2 to exit: ")
        if user_input == '1':
            if not graph:
                graph = start_connection()
                while True:
                    disease_id = get_user_input()
                    get_disease_info(disease_id, graph)
                    find_new_treatments(disease_id, graph)
                    another_input = input("Enter another disease ID? (y/n): ")
                    if another_input.lower() != 'y':
                        break
        elif user_input == '2':
            print('Exiting program')
            sys.exit(0)
        else:
            print('Invalid input, try again')


def start_connection():
    try:
        graph = Graph("bolt://localhost:7687", auth=('neo4j', 'lucky238'))
        print("Connected to Neo4j database successfully.")
        return graph
    except Exception as e:
        print(f"Error connecting to the database: {e}")
        print("Please check your Neo4j connection settings and ensure the database is running.")
        sys.exit(1)

def get_user_input():
    return input("Enter disease ID: ")

def get_disease_info(disease_id, graph):
    query = """
        MATCH (d:Disease {id: $disease_id})
        OPTIONAL MATCH (drug:Compound) -[rel] -(d)
        WHERE type(rel) = 'treats_CtD' or type(rel) = 'palliates_CpD'
        OPTIONAL MATCH (gene:Gene) - [rel2] - (d)
        WHERE type(rel2) = 'associates_DaG'
        OPTIONAL MATCH (location:Anatomy) - [rel3] - (d)
        WHERE type(rel3) = 'localizes_DlA'
        RETURN d.name AS Disease,
            COLLECT (DISTINCT drug.name) AS Drug_names,
            COLLECT (DISTINCT gene.name) AS Gene_names,
            COLLECT (DISTINCT location.name) AS locations

    """
    result = graph.run(query, disease_id=disease_id).data()
    if result:
            disease_info = result[0]
            print(f"Disease Name: {disease_info['Disease']}")
            print("\nDrug Names (can treat or palliate):")
            print(", ".join(disease_info['Drug_names']) if disease_info['Drug_names'] else "None")

            print("\nGene Names (associated with disease):")
            print(", ".join(disease_info['Gene_names']) if disease_info['Gene_names'] else "None")

            print("\nLocations (where disease occurs):")
            print(", ".join(disease_info['locations']) if disease_info['locations'] else "None")
    else:
        print("No disease found")


def find_new_treatments(disease_id, graph):
    try:
        # Print disease ID to ensure it's passed correctly
        print(f"Finding new treatments for disease ID: {disease_id}")

        query = """
            MATCH (d:Disease{id: $disease_id}) - [:downregulates_DdG] -> (gene:Gene)
            OPTIONAL MATCH (drug:Compound) - [rel] - (gene)
            WHERE type(rel) = 'upregulates_CuG' OR type(rel) = 'downregulates_CdG'
            OPTIONAL MATCH (d) - [:localizes_DlA] - (anatomy:Anatomy) - [anatomyRel] - (gene)
            WHERE type(anatomyRel) = 'upregulates_AuG' OR type(anatomyRel) = 'downregulates_AdG'

            WITH drug, d, gene, rel, anatomyRel,
            CASE
                WHEN type(rel) = 'downregulates_CdG' AND type(anatomyRel) = 'upregulates_AuG' THEN 1
                WHEN type(rel) = 'upregulates_CuG' AND type(anatomyRel) = 'downregulates_AdG' THEN 1
                ELSE 0
            END AS oppositeRegulation

            WHERE oppositeRegulation = 1
            AND NOT (drug) - [:treats_CtD] - (d)
            AND NOT (drug) - [:palliates_CpD] - (d)

            RETURN DISTINCT drug.name AS treatment_name, drug.id AS treatment_id
        """
        
        # Run the query and fetch data
        result = graph.run(query, disease_id=disease_id).data()
        
        # Check if results exist
        if result:
            print(f"\nNew potential treatments for disease ID {disease_id}:")
            for i, treatment in enumerate(result, 1):
                print(f"{i}. Treatment: {treatment['treatment_name']}, ID: {treatment['treatment_id']}")
        else:
            print("No new potential treatments found.")

    except Exception as e:
        # Catch any exceptions and print an error message
        print(f"An error occurred: {e}")



if __name__== "__main__":
    main()


#WINDOW GUI
# GUI Setup
window = tk.Tk()
window.title("HetioNet Disease Information and Treatment Finder")
window.geometry("600x400")


window.mainloop()