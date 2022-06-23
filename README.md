# citation_clusters_evaluation/n
Code of the paper Academic information retrieval using citation clusters: In-depth evaluation based on systematic reviews\n

Warning:/n
For legal reasons, we do not provide the data that this code used./n

Content:
The .py files are modules that the .pynb files call, and the .pynb what is run.
The order to run the .pynb files is:
1- clean_references.pynb: This file remove the relevant documents of the systematic reviews. It requires the PubMed version of the Boolean queries and the citation networks. It removes documents that are not retrieved by the Boolean queries or are not present in the citation networks. After this process, it also removes the systematic reviews that have too few relevant documents left. This is the first step because the relevant documents indicate which clusters will get child clusters.
2- clustering.pynb: This file create the tree hierarchy of clusters for the citation networks. It requires the citation networks and the relevant documents of the systematic reviews. The clustering is performed on an igraph object. An extensive part of the code (within the .py files) is for merging the clusters. The code keeps track of the resolution parameter at each level. The creation of child clusters is a recursive process, and it stops on the 13th iteration or if there are no relevant documents in the parent cluster.
3- results.pynb: This files create the results of the paper. It requires the clustering results and the relevant documents of the systematic reviews. It calculates the metrics of each systematic review at the different beta values. It also obtains the title of the documents from the PubMed API and extracts the noun phrases from the titles. It has a stop and continue catcher on one of the PubMed API request because the connection was lost due to requesting too many titles.
4- create_data.pynb: This file generate the data available at the Zenodo repository.
