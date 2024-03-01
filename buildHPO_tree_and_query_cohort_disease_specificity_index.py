import os
import numpy as np

# Create a class for building out each node
class Node:
    def __init__(self, node_id, name):
        self.node_id = node_id
        self.name = name
        self.children = []
        self.parent = None
        self.level = None  # Add level attribute

    def add_child(self, child):
        self.children.append(child)
        child.parent = self

# Function to parse the OBO file and return a list of terms
def parse_obo_file(file_path):
    terms = []
    current_term = None

    with open(file_path, 'r') as file:
        for line in file:
            line = line.strip()
            if line == '[Term]':
                if current_term:
                    terms.append(current_term)
                current_term = {"id": None, "name": None, "is_a": []}
            elif line.startswith('id:'):
                current_term['id'] = line.split('id:')[1].strip()
            elif line.startswith('name:'):
                current_term['name'] = line.split('name:')[1].strip()
            elif line.startswith('is_a:'):
                parent_id = line.split('is_a:')[1].strip().split('!')[0].strip()
                current_term['is_a'].append(parent_id)
        if current_term:
            terms.append(current_term)

    return terms

# Function to build the tree from the list of terms
def build_tree(terms):
    nodes = {}
    root_nodes = []

    for term in terms:
        node_id, name = term['id'], term['name']
        nodes[node_id] = Node(node_id, name)

    for term in terms:
        node_id = term['id']
        for parent_id in term.get('is_a', []):
            if parent_id in nodes:
                nodes[parent_id].add_child(nodes[node_id])

    for node_id, node in nodes.items():
        if node.parent is None:
            root_nodes.append(node)

    return root_nodes, nodes

# TODO: Go through the next three functions from ChatGPT
#  Add set_node_levels function
def set_node_levels(root_nodes):
    queue = [(node, 0) for node in root_nodes]
    while queue:
        current_node, level = queue.pop(0)
        current_node.level = level
        for child in current_node.children:
            queue.append((child, level + 1))

# Function to calculate the level distributions in the ontology
# This is done with all nodes, counts number of nodes at each 
def calculate_level_distributions(nodes):
    level_distribution = {}
    for node in nodes.values():
        if node.level in level_distribution:
            level_distribution[node.level] += 1
        else:
            level_distribution[node.level] = 1
    return level_distribution

def find_lmax(level_distribution):
    return max(level_distribution, key=level_distribution.get)

# Function to calculate the DsI score
def calculate_dsI(nodes, hpo_ids, Lmax, level_distribution):
    # Count terms per level in the cohort
    cohort_level_count = {}
    for hpo_id in hpo_ids:
        if hpo_id in nodes:
            level = nodes[hpo_id].level
            cohort_level_count[level] = cohort_level_count.get(level, 0) + 1

    # Calculate dL - the difference between the observed and expected probabilities (PobsL - PontL)
    dL_scores = {}
    for level, count in cohort_level_count.items():
        PobsL = count / len(hpo_ids)
        PontL = level_distribution.get(level, 0) / sum(level_distribution.values())
        dL_scores[level] = PobsL - PontL

    # Calculate LsS and HsS
    # The function calculates the LsS (Lower similarity score) by summing the product of each dL score and the difference between the maximum level (Lmax) and the current level.
    LsS = sum(dL * (Lmax - level + 1) for level, dL in dL_scores.items() if level <= Lmax and dL > 0)
    # It also calculates the HsS (Higher similarity score) by summing the product of each dL score and the difference between the maximum level in the reference ontology and the current level.
    HsS = sum(dL * (max(level_distribution.keys()) - level) for level, dL in dL_scores.items() if level > Lmax and dL > 0)

    # Calculate DsI
    DsI = HsS / LsS if LsS != 0 else float('inf')

    return DsI




# Assuming the functions `parse_obo_file`, `build_tree`, `set_node_levels`, `calculate_level_distributions`, `find_lmax`, and `calculate_dsI` are already defined as previously described

obo_file_path = '/mnt/atlas_local/guantong/home/New_manuscript/subset_patient_cases_by_difficulty/difficulty_subsets/hp.obo'
directory_path = '/mnt/atlas_local/guantong/home/New_manuscript/repeat_baseline_UDN_50'
output_file = '/mnt/atlas_local/guantong/home/New_manuscript/subset_patient_cases_by_difficulty/difficulty_subsets/UDN_HPO_ranks_dsi.txt'
#hpo_dir = '/mnt/atlas_local/guantong/home/HPO_wGPT/HPOs/BG_train/BG#_2020_HPO'
# hpo_dir is simply a dir containing mappings of hpo_id to hpo_name for each of the patients I process, you may need to supply your own
hpo_dir = '/mnt/atlas_local/guantong/home/New_manuscript/subset_patient_cases_by_difficulty/difficulty_subsets/hpo_data/udn'

# Parse the OBO file and build the tree
terms = parse_obo_file(obo_file_path)
root_nodes, all_nodes = build_tree(terms)
# Set levels for each node in the tree
set_node_levels(root_nodes)
# Calculate level distributions in the ontology
level_distribution = calculate_level_distributions(all_nodes)
# Find Lmax in the ontology
Lmax = find_lmax(level_distribution)

# Remove the output_file if it exists so we can create it anew
if os.path.exists(output_file):
    os.remove(output_file)

# Iterate over every file in the directory
for filename in os.listdir(directory_path):
    file_path = os.path.join(directory_path, filename)
    print(filename)

    #if filename == '607362_prompt.txt':
    #    print('Found file')

    if os.path.isfile(file_path):
        hpo_file = os.path.join(hpo_dir, (filename.split('_')[0] + '.HPO.txt'))

        if not os.path.exists(hpo_file):
            with open(output_file, 'a') as out:
                out.write(f"{filename}\tnp.nan\tnp.nan\tnp.nan\n")
            continue

        gdd = '0'  # Track presence of global developmental delay
        hpo_ids = []  # To store HPO IDs from the file

        with open(hpo_file, 'r') as hpos:
            for line in hpos:
                if line.startswith('HP:'):
                    hpo_id = line.strip().split('\t')[0]
                    hpo_ids.append(hpo_id)
                    if hpo_id == 'HP:0001263':
                        gdd = '1'
        
        # Calculate DsI for the current file
        DsI = calculate_dsI(all_nodes, hpo_ids, Lmax, level_distribution)
        
        # Write the results to the output file
        with open(output_file, 'a') as out:
            out.write(f"{filename}\t{DsI}\t{len(hpo_ids)}\t{gdd}\n")
