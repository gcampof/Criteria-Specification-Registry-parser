import requests
import json
import math
import os

gene_set = {"APC", "ATM", "CDH1", "CHEK2", "MLH1", "MSH2", "MSH6", "PMS2", "PTEN", "TP53", "BRCA1", "BRCA2", "DICER1", "RUNX1",
         "VHL"}

# Gets the ids that uses ClinGen internailly
def get_gene_ids(gene_set):
    gene_dict = {}
    match_genes = []

    # Gets teh total number of genes in ClinGen
    url_total = "https://cspec.genome.network/cspec/srvc"
    response = requests.get(url_total)
    data = response.json()
    total_genes = data['data']['entTypes']['Gene']['entCount']

    # Set page size
    pgSize = 1000
    maxPg = math.ceil(total_genes / pgSize)

    for pg in range(1, maxPg + 1):
        # parses the output
        url_genes = f"https://cspec.genome.network/cspec/Gene/id?detail=med&pg={pg}&pgSize={pgSize}"
        response = requests.get(url_genes)
        data = response.json()

        # Saves the matching entry and removes the Gene from the set
        for gene in data['data']:
            if gene['entId'] in gene_set:
                match_genes.append(gene)
                gene_set.remove(gene['entId'])

    # extract the Gene ID
    for match in match_genes:
        gene_symbol = match['entId']
        guideline_id = match['ldFor']['SequenceVariantInterpretation'][0]['entId']
        gene_dict.update({gene_symbol: guideline_id})

    return gene_dict


# Download guidelines
def download_all_gene_guidelines(gene_dict):
    if not os.path.exists('guidelines'):
        os.makedirs('guidelines')

    for gene in gene_dict:
        gene_folder = os.path.join('guidelines', gene)
        os.makedirs(gene_folder, exist_ok=True)

        # Fetch all the versions
        url_versions = f"https://cspec.genome.network/cspec/SequenceVariantInterpretation/id/{gene_dict[gene]}/version"
        response = requests.get(url_versions)
        data = response.json()

        # Get the list of versions for the gene
        versions = data.get('data', [])

        for version in versions:
            version_url = version['@id']
            version_filename = version_url.split('/')[-1]
            version_filepath = os.path.join(gene_folder, f"{version_filename}.json")

            # Download the content of the version URL
            version_response = requests.get(version_url)
            if version_response.status_code == 200:
                # Save the response content as a JSON file
                with open(version_filepath, 'w') as file:
                    json.dump(version_response.json(), file, indent=2)
                    print(f"Downloaded {version_filename} for gene {gene}")
            else:
                print(f"Failed to download version {version_filename} for gene {gene}")


# gene_dict = {'APC': 'GN089', 'ATM': 'GN020'}
gene_dict = get_gene_ids(gene_set)
download_all_gene_guidelines(gene_dict)

