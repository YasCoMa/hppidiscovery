import os

g=open('count_proteins_by_genome.tsv','w')
folder='../data_targetpathogen_genomes/structures/'
for f in os.listdir(folder):
    if(os.path.isdir(folder+f) and f.startswith('all-')):
        pdbs=0
        for p in os.listdir(folder+f):
            if( p.endswith('.pdb.gz') ):
                pdbs+=1
        
        g.write("%s\t%i\n" %(f, pdbs) )
g.close()
