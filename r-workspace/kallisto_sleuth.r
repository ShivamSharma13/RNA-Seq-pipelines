setwd("/Users/shivam/Desktop/Fall 2019/BIOL6150/rna-seq-project/r-workspace")

print("Setting working directory to...")
print(getwd())

library("sleuth")
print("Hitting biomaRT to obtain mapping data to join transcript IDs to gene names...")

#Make a table that maps transcript ID to gene names.
tx2gene <- function(){
	
	mart <- biomaRt::useMart(biomart = "ensembl", dataset = "hsapiens_gene_ensembl")
	t2g <- biomaRt::getBM(attributes = c("ensembl_transcript_id", "ensembl_gene_id", "external_gene_name"), mart = mart)
	t2g <- dplyr::rename(t2g, target_id = ensembl_transcript_id, ens_gene = ensembl_gene_id, ext_gene = external_gene_name)
	#print(t2g[1:10,])
	return(t2g)
	
}

t2g <- tx2gene()

#Path to directory which contains the folders named by sample IDs of GSM fastq files. 
fastq_dir <- "../data/Ira"

sample_id <- dir(file.path(fastq_dir))

#These sample ID directories have an output directory which holds the tsv and h5 abundance files produced by kallisto.
kal_dirs <- file.path(fastq_dir, sample_id)

print("Kallisto Directories...")
print(kal_dirs)

meta <- read.table("meta.tab", header=TRUE)

#Intorduce a path column in the data frame object obtained from meta.tab file.
s2c = dplyr::mutate(meta, path = kal_dirs)

print("Data Frame Object...")
print(s2c)

so <- sleuth_prep(s2c, target_mapping=t2g, max_bootstrap=1)

#The following step fits kallisto's abundance estimates into a linear model pivoted around normal vs control.
so <- sleuth_fit(so, ~condition, 'full')

#Following fit is used for diffrential analysis of gene expression. 
#Making the sleuth model presume that abundances are equal in the two conditions.
#A model which is based on the assumption that gene expression is not dependent on any other factor.
so <- sleuth_fit(so, ~1, 'reduced')

#Likelyhood ratio performed to find the statistical significance of diffrential expression estimates.

so <- sleuth_lrt(so, 'reduced', 'full')

#Get a summary of model.
models(so)

#Storing the results.
sleuth_table <- sleuth_results(so, 'reduced:full', 'lrt')

#Remove the false positives by filtering thing on q-value.
sleuth_significant <- dplyr::filter(sleuth_table, qval <= 0.5)

#Show the first 20 genes.
print(head(sleuth_significant, 20))
