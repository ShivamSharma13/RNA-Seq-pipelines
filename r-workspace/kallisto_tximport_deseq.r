library(tximport)
library(readr)

fastq = "../data/Ira"
sys_dir <- system.file("extdata", package = "tximportData")

samples = dir(file.path(fastq))

files <- file.path(fastq, samples, "abundance.h5")

names(files) <- paste0(c("Sample1", "Sample2", "Sample3", "Sample4", "Sample5","Sample6","Sample7","Sample8","Sample9","Sample10","Sample11"))

all(file.exists(files))

#tx2gene <- read_csv(file.path(dir, "tx2gene.gencode.v27.csv"))
#print(head(tx2gene))

txi.kallisto <- tximport(files, type = "kallisto", txOut = TRUE)
print(head(txi.kallisto$counts))

library(DESeq2)

sampleTable <- data.frame(condition = factor(c(rep("Test",7), rep("Ischemic", 4))))
rownames(sampleTable) <- colnames(txi.kallisto$counts)

dds <- DESeqDataSetFromTximport(txi.kallisto, sampleTable, ~condition)

# Run the DESeq pipeline
dds <- DESeq(dds)

# Get differential expression results
res <- results(dds)
table(res$padj<0.05)
## Order by adjusted p-value
res <- res[order(res$padj), ]
## Merge with normalized count data
resdata <- merge(as.data.frame(res), as.data.frame(counts(dds, normalized=TRUE)), by="row.names", sort=FALSE)
names(resdata)[1] <- "Gene ID"
head(resdata)

## Write results
write.csv(resdata, file="results.csv")

library(annotate)
library(org.Hs.eg.db)
df <- read.csv("results.csv")
df$GeneNames=getSYMBOL(as.character(as.numeric(unlist(df[2]))), data='org.Hs.eg')

write.table(df, file='kallisto_tximport_deseq.tsv', quote=FALSE, sep='\t', col.names = NA)

