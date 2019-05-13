# -*- coding: utf-8 -*-
"""

"""
import os
import subprocess as sp
from csv import reader

from Tools import Flatten, ParseMatchtable, TryMkDirs


def MakeWorkingDirs():
    """
    Tries to make work directory if not already present.
    """
    tdir = "go"
    TryMkDirs(tdir)


def GenerateAnnoDict(ips):
    """
    Load InterProScan output (must be tsv format), and generate dictionary of GO annotation data.
    """
    with open(ips) as infile:
        anno_dict = {}
        for line in reader(infile, delimiter="\t"):
            protein = line[0]
            if protein not in anno_dict:
                if len(line) == 14:
                    if line[13]:
                        anno_dict[protein] = [go for go in line[13].split("|") if go]
    return anno_dict


def GenerateAssociations(annos):
    """
    Given GO annotation dictionary, write associations file for use in GOATools.
    """
    with open("go/associations.txt", "w") as assocs:
        for gene in annos:
            if annos[gene]:
                assocs.write("{0}\t{1}\n".format(gene, ";".join(annos[gene])))


def GeneratePopulations(annos, matchtable):
    """
    Write out background (full) population and study (core, accessory) population files for use in GOATools.
    """
    core, acc = ParseMatchtable(matchtable)
    c_pop = [val for val in Flatten(core.values()) if val in annos]
    a_pop = [val for val in Flatten(acc.values()) if val in annos]
    full_pop = c_pop + a_pop
    with open("go/core_pop.txt", "w") as cp_file, open("go/acc_pop.txt", "w") as ap_file,\
         open("go/full_pop.txt", "w") as fp_file:
        cp_file.write("\n".join(c_pop))
        ap_file.write("\n".join(a_pop))
        fp_file.write("\n".join(full_pop))


def GenerateSlimData(assocs, go_obo, slim_obo):
    """
    Runs map_to_slim.py from GOATools to generate GO-slimmed association file.
    """
    sp.call(["map_to_slim.py", "--association_file={0}".format(assocs), go_obo, slim_obo],
            stdout=open("go/pangenome_slim_temp.txt", "w"))
    with open("go/pangenome_slim.txt", "w") as slim:
        for line in open("go/pangenome_slim_temp.txt").readlines():
            if "|" in line:
                slim.write(line)

def CoreEnrichment(go_obo, core_pop, full_pop, slimmed_assoc):
    """
    """
    sp.call(["find_enrichment.py", "--pval=0.05", "--method=fdr", "--obo", go_obo, core_pop,
             full_pop, slimmed_assoc, "--outfile=core_enrichment.tsv"])

def AccessoryEnrichment(go_obo, acc_pop, full_pop, slimmed_assoc):
    """

    """
    sp.call(["find_enrichment.py", "--pval=0.05", "--method=fdr", "--obo", go_obo, acc_pop,
             full_pop, slimmed_assoc, "--outfile=noncore_enrichment.tsv"])
