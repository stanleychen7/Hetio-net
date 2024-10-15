from py2neo import Graph
import tkinter as tk
from tkinter import ttk
from dotenv import load_dotenv
import os


load_dotenv()
neo4j_pass = os.getenv('NEO4J_PASSWORD')
#Start connection to neo4j
graph = Graph("bolt://localhost:7687", auth=('neo4j', neo4j_pass))

def get_disease_info(disease_id):
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
    return result

def find_new_treatments(disease_id):
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
        return result

#Generate random list 
def get_random_disease ():
        query = """
            MATCH (d:Disease)
            WITH d, rand() AS random
            ORDER BY random
            RETURN d.id AS id
            LIMIT 20
        """
        result = graph.run(query).data()
        return [row['id'] for row in result]


#WINDOW GUI
#GUI COMMANDS
def get_info():
    disease_id = entry.get()
    info = get_disease_info(disease_id)
    output.delete(1.0, tk.END)
    
    if info:
        disease_info = info[0]
        result = f"Disease Name: {disease_info['Disease']}\n\n"
        
        result += "Drug Names (can treat or palliate):\n"
        result += ", ".join(disease_info['Drug_names']) if disease_info['Drug_names'] else "None"
        result += "\n\n"
        
        result += "Gene Names (associated with disease):\n"
        result += ", ".join(disease_info['Gene_names']) if disease_info['Gene_names'] else "None"
        result += "\n\n"
        
        result += "Locations (where disease occurs):\n"
        result += ", ".join(disease_info['locations']) if disease_info['locations'] else "None"
        
        output.insert(tk.END, result)
    else:
        output.insert(tk.END, "No disease found with the given ID.")

def new_treatments():
    disease_id = entry.get()
    treatments = find_new_treatments(disease_id)
    
    if treatments:
        treatment_list = "\n".join([f"Treatment: {treatment['treatment_name']}, ID: {treatment['treatment_id']}" for treatment in treatments])
        result = f"New potential treatments for disease ID {disease_id}:\n{treatment_list}"
    else:
        result = "No new potential treatments found."
    output.delete(1.0, tk.END)
    output.insert(tk.END, result)

def disease_list():
     rand_disease_list = get_random_disease()

     if rand_disease_list:
          for disease_id in rand_disease_list:
               listbox.insert(tk.END, disease_id)

def on_listbox_select(event):
     selected_index = listbox.curselection()
     if selected_index:
          disease_id = listbox.get(selected_index)
          entry.delete(0, tk.END)
          entry.insert(tk.END, disease_id)


# Create GUI
window = tk.Tk()
window.title("HetioNet Disease Information and Treatment Finder")
window.geometry("600x400")

# Set dark theme colors
bg_color = "#2B2B2B"
fg_color = "#FFFFFF"
button_bg = "#4A4A4A"
button_fg = "#FFFFFF"
button_hover_bg = "#5A5A5A"
entry_bg = "#3C3F41"
entry_fg = "#FFFFFF"
left_frame_bg = "#252525"  # Slightly darker than main background

window.configure(bg=bg_color)

# Create and configure a style
style = ttk.Style(window)
style.theme_use('clam')
style.configure('TButton', background=button_bg, foreground=button_fg)
style.map('TButton',
    background=[('active', button_hover_bg)],
    foreground=[('active', button_fg)]
)
style.configure('TEntry', fieldbackground=entry_bg, foreground=entry_fg)
style.configure('TLabel', background=bg_color, foreground=fg_color)
style.configure('Left.TFrame', background=left_frame_bg)

# Create main frame
main_frame = tk.Frame(window, bg=bg_color)
main_frame.pack(pady=20, padx=20, fill="both", expand=True)

# Create left frame for list
left_frame = ttk.Frame(main_frame, width=120, height=200, relief=tk.SUNKEN, padding="3 3 3 3", style='Left.TFrame')
left_frame.pack(side=tk.LEFT, fill=tk.Y, expand=False, padx=(0, 10))
left_frame.pack_propagate(False)
label = ttk.Label(left_frame, text="List of IDs")
label.pack(pady=(0, 5))

# Listbox in left frame
listbox = tk.Listbox(left_frame, bg=entry_bg, fg=fg_color, selectbackground=button_bg, selectforeground=button_fg)
listbox.pack(fill=tk.BOTH, expand=True)

#Populate left frame
disease_list()
# Bind the Listbox selection event
listbox.bind('<<ListboxSelect>>', on_listbox_select)

# Right content frame
right_frame = tk.Frame(main_frame, bg=bg_color)
right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

# Input field
label = ttk.Label(right_frame, text="Enter Disease ID:")
label.pack(pady=(0, 5))

entry = ttk.Entry(right_frame, width=30)
entry.pack(pady=(0, 10))

# Button frame
button_frame = tk.Frame(right_frame, bg=bg_color)
button_frame.pack(pady=10)

# Buttons
button_get_info = ttk.Button(button_frame, text="Get Disease Information", command=get_info)
button_get_info.pack(side="left", padx=5)

button_clear = ttk.Button(button_frame, text="Find New Treatments", command=new_treatments)
button_clear.pack(side="left", padx=5)

# Output field
output = tk.Text(right_frame, width=50, height=10, bg=entry_bg, fg=fg_color)
output.pack(pady=10, expand=True, fill=tk.BOTH)

# Start the main event loop
window.mainloop()