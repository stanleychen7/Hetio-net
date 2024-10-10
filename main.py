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
        RETURN d.name
    """

    result = graph.run(query, disease_id = disease_id).data()
    print(result)

if __name__== "__main__":
    start()
