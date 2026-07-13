from sentence_transformers import SentenceTransformer
import json
import numpy as np


DATA_FILE = "merged_modules.json"

EMBEDDING_FILE = "odoo_module_embeddings.npy"
METADATA_FILE = "module_metadata.json"


model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)


def load_modules():

    with open(
        DATA_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        modules = json.load(file)

    return modules



def prepare_text(module):

    text = f"""
    Title:
    {module.get('Title', '')}

    Source:
    {module.get('Source', '')}

    Category:
    {module.get('Category', '')}

    Summary:
    {module.get('Summary', '')}

    Features:
    {module.get('Features', '')}
    """

    return text



def create_embeddings():

    modules = load_modules()

    print(
        "Total modules:",
        len(modules)
    )


    documents = []

    for module in modules:

        documents.append(
            prepare_text(module)
        )


    embeddings = model.encode(
        documents,
        show_progress_bar=True
    )


    embeddings = np.array(
        embeddings
    )


    np.save(
        EMBEDDING_FILE,
        embeddings
    )


    with open(
        METADATA_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            modules,
            file,
            indent=4,
            ensure_ascii=False
        )


    print(
        "Embeddings created successfully"
    )

    print(
        "Shape:",
        embeddings.shape
    )



if __name__ == "__main__":
    create_embeddings()