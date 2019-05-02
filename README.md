### About

This is set of tools to:
 - search NCBI's pubmed articles through straight text queries,
 - get articles related to nucleotide polymorphisms found on target gene via dbSNP,
 - get articles contained inside a page (polymorphism or gene) on SNPedia,
 - view a summary of articles gathered on those searches.


### Usage

Designed for Python 3;

```
$sudo pip install -r requirements.txt
$sudo pip install .


$pmcc "Tropical Diseases"    //search and view results on terminal
$pmcc "Aromatic Acids" -P    //same as above, also store results as a list of PMIDs
```
