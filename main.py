import sys
from py2neo import Graph

def start():
    graph = None
    while True:
        user_input = input ("Enter 1 to start, 2 to exit: ")
        if user_input == '1':
            if not graph:
                graph = start_connection()
                while True:
                    disease_id = get_user_input()
                    get_disease_info(disease_id, graph)
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

if __name__== "__main__":
    start()
