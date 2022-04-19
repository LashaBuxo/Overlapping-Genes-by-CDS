import genome_tools as genome
import time

start_time = time.time()

coding_overlapped_genes = []

max_overlap_sums = 0
total_overlap_sum = 0
overlapped_merged_sequence = ""

for chr_id in range(1, genome.number_of_chromosomes + 1):
    # do we need only find overlaps by CDS?
    genome.preprocess_annotation_for_chr(chr_id, True)
    genes_cnt = genome.genes_count_on_chr(chr_id)

    genes = 0
    maxOverlap = -1
    desired_pair = (-1, -1)
    gene_fragments = []
    for i in range(0, genes_cnt):
        gene_fragments.append([])

    for i in range(0, genes_cnt):
        gene_fragments[i] = genome.get_fragments_on_gene(chr_id, genome.gene_by_ind(chr_id, i))

    for i in range(0, genes_cnt):
        for j in range(i + 1, genes_cnt):
            gene_A = genome.gene_by_ind(chr_id, i)
            gene_B = genome.gene_by_ind(chr_id, j)
            if not genome.are_genes_overlapped(gene_A, gene_B): continue

            # do we need same stranded overlaps?
            if gene_A.strand != gene_B.strand: continue

            # exclude same stranded overlaps which has same ORF?
            max_overlap, overlap_intervals = genome.max_fragments_overlap_length(gene_fragments[i], gene_fragments[j],
                                                                                 False)

            total_overlap = 0

            for interval in overlap_intervals:
                assert interval[1] >= interval[0]
                total_overlap += interval[1] - interval[0] + 1
                overlapped_merged_sequence += genome.retrieve_interval_sequence(chr_id, interval[0], interval[1],
                                                                                gene_A.strand)

            if max_overlap > 0:
                max_overlap_sums += max_overlap
                total_overlap_sum += total_overlap
                coding_overlapped_genes.append(
                    (chr_id, max_overlap, total_overlap, gene_A, gene_B))

    print("Overlaps Found: " + str(len(coding_overlapped_genes)))

sorted_by_second = sorted(coding_overlapped_genes, key=lambda tup: tup[1], reverse=True)
total_overlapping_composition = genome.sequence_composition(overlapped_merged_sequence)

# print data
with open('./results/cds_overlapped_genes_same_stranded_same_frame.txt', 'w') as f:
    for item in sorted_by_second:
        data = "chr-" + str(item[0]) + "  overlap_max-" + str(item[1]) + "  overlap_total-" + str(
            item[2]) + "  genes-[" + item[3].id + ";" + item[
                   4].id + "]";

        # # print genes description?
        # data += "\n"
        # if item[2].attributes.__contains__('Name') and item[2].attributes.__contains__('description'):
        #     data += item[2].attributes['Name'][0] + "; " + item[2].attributes['description'][0]
        # data += "\n"
        # if item[3].attributes.__contains__('Name') and item[3].attributes.__contains__('description'):
        #     data += item[3].attributes['Name'][0] + "; " + item[3].attributes['description'][0]
        # data += "\n"
        #
        # data += "\n"

        f.write("%s\n" % data)
    data2 = "max_overlap_sums: " + str(max_overlap_sums) + " total_overlap_sums: " + str(total_overlap_sum)
    f.write("%s\n" % data2)
    data3 = "Total Overlap Composition: C-" + str(total_overlapping_composition[0]) + " G-" + str(
        total_overlapping_composition[1]) + " A-" + str(total_overlapping_composition[2]) + " T-" + str(
        total_overlapping_composition[3])
    f.write("%s\n" % data3)
    print("--- %s seconds ---" % (time.time() - start_time))