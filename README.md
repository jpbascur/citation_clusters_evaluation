# citation_clusters_evaluation

This repository contains the code of the paper 'Academic information retrieval using citation clusters: In-depth evaluation based on systematic reviews' by Juan Pablo Bascur, Suzan Verberne, Nees Jan van Eck, and Ludo Waltman.

## Content

The repository consists of four Jupyter notebooks (`.pynb` files) and the Python modules (`.py` files) used by the notebooks. The order to run the notebooks is as follows:

1. `clean_references.pynb`: This notebook removes the relevant documents of the systematic reviews. It requires the PubMed version of the Boolean queries and the citation networks. It removes documents that are not retrieved by the Boolean queries or that are not present in the citation networks. After this process, it also removes the systematic reviews that have too few relevant documents left. This is an important step, because the relevant documents indicate which clusters will get child clusters.

2. `clustering.pynb`: This notebook creates the tree hierarchy of clusters for the citation networks. It requires the citation networks and the relevant documents of the systematic reviews. The clustering is performed on an [igraph](https://igraph.org) object. An extensive part of the code (within the `.py` files) is for merging the clusters. The code keeps track of the resolution parameter at each level. The creation of child clusters is a recursive process, and it stops after 13 iterations or if there are no relevant documents in the parent cluster.

3. `results.pynb`: This notebook creates the results for the paper. It requires the clustering results and the relevant documents of the systematic reviews. It calculates the metrics of each systematic review for the different beta values. It also obtains the title of the documents from the PubMed API and extracts the noun phrases from the titles. It has a stop and continue catcher on one of the PubMed API requests since the connection can be lost due to requesting too many titles.

4. `create_data.pynb`: This notebook generates the data for the Zenodo repository.

## Disclaimer

Due to license restrictions, this repository does not contain the data that was used to run the code.
