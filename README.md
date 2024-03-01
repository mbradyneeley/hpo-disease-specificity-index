# HPO Tree Builder and Disease Specificity Index Calculator

This repository contains a Python script for parsing the Human Phenotype Ontology (HPO) to build a hierarchical tree structure and calculate a disease-specificity index (DsI) for given cohorts based on their phenotype profiles.

The disease specificity index is calculated similarly as done in this paper: https://www.ncbi.nlm.nih.gov/pmc/articles/PMC8398478/

## Overview

The script `buildHPO_tree_and_query_cohort_disease_specificity_index.py` performs several key functions:

- Parses an OBO-formatted file to extract phenotype data and construct a hierarchical tree of phenotypes.
- Calculates the level of each node in the tree to understand the depth of phenotypes within the ontology.
- Evaluates the disease specificity of a given cohort by calculating the DsI, which considers the distribution of phenotype levels within the cohort compared to the overall distribution in the HPO.

## Requirements

- Python 3.x
- NumPy

## Usage

1. Ensure you have the required OBO file containing the HPO data. This is easily found on the human phenotype ontology website.

2. Place your cohort data in a directory, ensuring that each file contains the HPO IDs relevant to that cohort.

3. Adjust the `obo_file_path`, `directory_path`, and `output_file` variables in the script to point to your OBO file, cohort directory, and desired output file, respectively.

4. Run the script:
   `python buildHPO_tree_and_query_cohort_disease_specificity_index.py`



Additional initial notes:
I used the file buildHPO_tree_query.py to build the tree of nodes from hp.obo
- Then I used that framework and modified it in the *cohort_analyzer_modified.py extension
	This extension calculates the disease specificity score based on a number of factors surrounded node level based on this paper https://www.ncbi.nlm.nih.gov/pmc/articles/PMC8398478/
- The visualize_Disease_specificity_index.ipynb visualizes the dsi's across each dataset, BG, UDN, DDD and splits the data
  median.

Brady Neeley 2-29-2024
