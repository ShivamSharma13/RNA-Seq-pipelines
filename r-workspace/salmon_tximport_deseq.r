library(tximport)
library(readr)

quantified_dirs = "../salmon/quants"
sys_dir <- system.file("extdata", package = "tximportData")

samples = dir(file.path(quantified_dirs))

files <- file.path(quantified_dirs, samples, "quant.sf")
print(files)

names(files) <- paste0("sample", 1:4)

tx2gene <- read_csv(file.path(dir, "tx2gene.gencode.v27.csv"))
print(head(tx2gene))

txi.salmon <- tximport(files, type = "salmon", txOut = TRUE, tx2gene = tx2gene)

print(head(txi.salmon$counts))

#Import DESeq
library(DESeq2)

sampleTable <- data.frame(condition = factor(c(rep("Normal",3), "Ischemic")))
rownames(sampleTable) <- colnames(txi.salmon$counts)

dds <- DESeqDataSetFromTximport(txi.salmon, sampleTable, ~condition)

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
write.table(resdata, file='salmon_deseq.tsv', quote=FALSE, sep='\t', col.names = NA)

