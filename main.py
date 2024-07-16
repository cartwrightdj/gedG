import ged4py.parser as parser
import argparse
import networkx as nx
import os

# Function to get individual details
def get_individual_details(individual):
    if not individual:
        return None
    
    indi_id = individual.xref_id
    indi_details = {
        "Type": "INDI",  
        "Name": individual.name.format() if individual.name else "Unknown",
        "Surame": individual.name.surname if individual.name.surname else "Unknown",
        "Given": individual.name.given if individual.name.given else "Unknown",
        "Maiden": individual.name.maiden if individual.name.maiden else "Unknown",
        "Sex": individual.sex if individual.sex else "Unknown",
        "Birth_Date": str(individual.sub_tag_value("BIRT/DATE")) if individual.sub_tag_value("BIRT/DATE") else "Unknown",
        "Birth_Place": individual.sub_tag_value("BIRT/PLAC") if individual.sub_tag_value("BIRT/PLAC") else "Unknown",
        "Death_Date": str(individual.sub_tag_value("DEAT/DATE")) if individual.sub_tag_value("DEAT/DATE") else "Unknown",
        "Death_Place": individual.sub_tag_value("DEAT/PLAC") if individual.sub_tag_value("DEAT/PLAC") else "Unknown",
        "DD": ''
    }

    return indi_id, indi_details


def main():

    argparser = argparse.ArgumentParser(description="Process a .ged file.")
    argparser.add_argument("filename", type=str, help="The path to the .ged file")
    args = argparser.parse_args()
    try:
        if not args.filename.endswith('.ged'):
            raise ValueError("The file must have a .ged extension.")
    
        if not os.path.isfile(args.filename):
            raise FileNotFoundError(f"The file {args.filename} does not exist.")
    except (ValueError, FileNotFoundError) as e:
        print(e)
    

    gedcom = parser.GedcomReader(args.filename)
    G = nx.DiGraph()
           
    for individual in gedcom.records0("INDI"):
        indi_id, indi_details = get_individual_details(individual)
        if indi_details:
            G.add_node(indi_id, **indi_details)  # Add node with ID as an attribute

    parent_list = []
    for family in gedcom.records0("FAM"):
        if family:
            family_id = family.xref_id
            husband, wife = family.sub_tag("HUSB"), family.sub_tag("WIFE")
            if not husband is None:
                husband_id = husband.xref_id
                parent_list.append(husband_id)
                nx.set_node_attributes(G, {husband_id: {'famid': family_id}})
            else:
                husband_id = ""
            if not wife is None:
                wife_id = wife.xref_id
                parent_list.append(wife_id)
                nx.set_node_attributes(G, {wife_id: {'famid': family_id}})
            else:
                wife_id = ""

            if wife_id != '' and husband_id != '':
                G.add_edge(wife_id, husband_id, relationship='wife')
                G.add_edge(husband_id, wife_id, relationship='husband')

            children = family.sub_tags("CHIL")
            for child in children:
                child_id = child.xref_id
                if child_id not in parent_list:
                    nx.set_node_attributes(G, {child_id: {'famid': family_id}})

                if husband_id != '':
                    G.add_edge(husband_id, child_id, relationship='father-child')
                if wife_id != '':
                    G.add_edge(wife_id, child_id, relationship='mother-child')
                
       
    isolated_nodes = [node for node in G.nodes if G.degree(node) == 0]
    if isolated_nodes:
        print("Removing Isolated Nodes:")   
        G.remove_nodes_from(isolated_nodes)
        print(f"Removed {len(isolated_nodes)} Isolated Nodes:")
    
    parent_path = os.path.dirname(os.path.abspath(args.filename))
    graphFilePath = os.path.join(parent_path,'graph.gml')
    try:
        nx.write_gml(G, graphFilePath)
        print(f"Graph created at {graphFilePath}")
    except FileNotFoundError as e:
        print(f"Could not write Graph to {graphFilePath} ({e.strerror})")

    

if __name__ == "__main__":
    main()


