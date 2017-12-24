#!/bin/python

from ArticleEngine import evaluateArticles
from entrez import pubmedSearch, pubmedFetchArticles
from Options import options, args
import pkg_resources

from nalaf.utils.readers import TextFilesReader, PMIDReader
from nalaf.structures.dataset_pipelines import PrepareDatasetPipeline
from nalaf.utils.writers import ConsoleWriter, TagTogFormat, PubTatorFormat
from nalaf.domain.bio.gnormplus import GNormPlusGeneTagger
from nalaf.learning.taggers import StubSameSentenceRelationExtractor
from nalaf.learning.crfsuite import PyCRFSuite

def getAbstracts(Query):
    IDS = pubmedSearch(Query)
    Articles = pubmedFetchArticles(IDS)
    Articles = evaluateArticles(Articles, options)

    return Articles

if __name__ == '__main__':
    IDS = pubmedSearch(options.Filter)
    dataset = PMIDReader(IDS).read()

    ENT1_CLASS_ID = 'e_x'
    ENT2_CLASS_ID = 'e_y'
    REL_ENT1_ENT2_CLASS_ID = 'r_z'
    ENTREZ_GENE_ID = 'n_w'
    UNIPROT_ID = 'n_v'

    print(dataset)
    PrepareDatasetPipeline().execute(dataset)
    crf = PyCRFSuite()
    crf.tag(dataset,
            pkg_resources.resource_filename('nalaf.data', 'example_entity_model'),
            class_id=ENT2_CLASS_ID)

    GNormPlusGeneTagger(ENT1_CLASS_ID, ENTREZ_GENE_ID, UNIPROT_ID).tag(dataset, uniprot=True)

    StubSameSentenceRelationExtractor(ENT1_CLASS_ID,
                                      ENT2_CLASS_ID,
                                      REL_ENT1_ENT2_CLASS_ID).annotate(dataset)

    ConsoleWriter(ENT1_CLASS_ID, ENT2_CLASS_ID, 'blue').write(dataset)
