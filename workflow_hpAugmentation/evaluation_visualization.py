import os 
import multiprocessing
import pandas as pd
import networkx as nx

import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt

class EvaluationResultsExportation:
    def __init__(self):
        self.target_taxon=''
        self.drug_targets={}
        
    def execute_new_ppis_prediction(self, main_folder):
        cpus=multiprocessing.cpu_count()
        n=cpus-4
        if(cpus<=6):
            n=2
            
        f=open(main_folder+"execute_predppi.sh","w")
        f.write("#!/bin/bash\n")
        f.write("cd predprin/\n")
        f.write("python3 -m luigi --module main RunPPIExperiment --parameters-file "+main_folder+"evaluation_params_predprin.json --mode test --model "+main_folder+"training_data/model_trained.joblib --workers "+str(n))
        f.close()

        os.system("rm predprin/run_experiment.txt")
        print("Executing prediction with host pathogen pairs ")
        os.system('bash '+main_folder+'execute_predppi.sh')
        
    def merge_network(self, main_folder, params):
        i=0
        targets=list(params['target_taxon'])
        for gr in params['genome']:
            self.target_taxon=str(targets[i])
            folder=main_folder+gr
            
            g=nx.Graph()
            ppis=set()
            for t in ['hpidb', 'predprin']:
                nameFile= folder+"/new_candidates/predictions.tsv"
                if(t=='hpidb'):
                    nameFile=folder+'/hpidb_pos.tsv'
                    
                if(os.path.isfile(nameFile)):
                    f=open(nameFile,'r')
                    for line in f:
                        l=line.replace('\n','').split('\t')
                        
                        if(t=='hpidb'):
                            if(l[2]==self.target_taxon and not l[0]+'-'+l[1] in ppis):
                                g.add_edge(l[0], l[1])
                                ppis.add(l[0]+'-'+l[1])
                                ppis.add(l[1]+'-'+l[0])
                        else:
                            score = float(l[2])
                            if( not l[0]+'-'+l[1] in ppis and score>0.8):
                                g.add_edge(l[0], l[1])
                                ppis.add(l[0]+'-'+l[1])
                                ppis.add(l[1]+'-'+l[0])
                    f.close()
            
            if( len(ppis)>0):  
               nx.write_graphml_lxml(g, folder+"/merged_ppinet.graphml")
            i+=1
        
    def separate_ppis_virulence_factors(self, main_folder, params):
        df=pd.read_csv('list_virulence_factors_full.tsv', sep='\t')
        vfs=df['uniprot']
        i=0
        targets=list(params['target_taxon'])
        for g in params['genome']:
            self.target_taxon=str(targets[i])
            
            folder=main_folder+g
            ppis=set()
            
            x=open(folder+'/virulence_factor_ppis.tsv','w')
            x.write('protein_pathogen\tprotein_host\tvirulence_factor\tsource\n')
            for t in ['hpidb', 'predprin']:
                nameFile=folder+"/new_candidates/predictions.tsv"
                if(t=='hpidb'):
                    nameFile=main_folder+g+'hpidb_pos.tsv'
                    
                if(os.path.isfile(nameFile)):
                    f=open(nameFile,'r')
                    for line in f:
                        l=line.replace('\n','').split('\t')
                        
                        if(t=='hpidb'):
                            if( (l[2]==self.target_taxon) and (not l[0]+'-'+l[1] in ppis) and (l[0] in vfs or l[1] in vfs) ):
                                vf=l[0]
                                if(l[1] in vfs):
                                    vf=l[1]
                                x.write("%s\t%s\t%s\n" %(l[0], l[1], vf, 'hpidb') )
                                
                                ppis.add(l[0]+'-'+l[1])
                                ppis.add(l[1]+'-'+l[0])
                        else:
                            score = float(l[2])
                            if( (not l[0]+'-'+l[1] in ppis) and (l[0] in vfs or l[1] in vfs) and score>0.8 ):
                                vf=l[0]
                                if(l[1] in vfs):
                                    vf=l[1]
                                x.write("%s\t%s\t%s\n" %(l[0], l[1], vf, 'predprin') )
                                
                                ppis.add(l[0]+'-'+l[1])
                                ppis.add(l[1]+'-'+l[0])
                    f.close()
            x.close()
            
            i+=1
            
    def _checa_drug_target(self, protein):
        if(protein in self.drug_targets.keys()):
            return self.drug_targets[protein]!=''
        else:
            self.drug_targets[protein]=''
            if( os.path.isfile('predprin/annotation_data/'+protein+'.tsv') ):
                f=open('predprin/annotation_data/'+protein+'.tsv','r')
                for line in f:
                    if(line!=''):
                        l=line.replace('\n','').split('\t')[-1]
                        if(l!='' and l!='None'):
                            self.drug_targets[protein]=l.replace(' ',',')
                            return True
                f.close()
        return False
        
    def separate_ppis_drug_targets(self, main_folder, params):
        df=pd.read_csv('list_virulence_factors_full.tsv', sep='\t')
        vfs=df['uniprot']
        i=0
        targets=list(params['target_taxon'])
        for g in params['genome']:
            folder=main_folder+g
            self.target_taxon=str(targets[i])
            i+=1
            
            ppis=set()  
            
            x=open(folder+'/drug_target_ppis.tsv','w')
            x.write('protein_pathogen\tprotein_host\tdrug_protein_pathogen\tdrug_protein_host\tsource\n')
            for t in ['hpidb', 'predprin']:
                nameFile=folder+"/new_candidates/predictions.tsv"
                if(t=='hpidb'):
                    nameFile=main_folder+g+'hpidb_pos.tsv'
                    
                if(os.path.isfile(nameFile)):
                    f=open(nameFile,'r')
                    for line in f:
                        l=line.replace('\n','').split('\t')
                        
                        if(t=='hpidb'):
                            if( (l[2]==self.target_taxon) and (not l[0]+'-'+l[1] in ppis) and ( self._checa_drug_target(l[0]) or self._checa_drug_target(l[1]) ) ):
                                dt1=''
                                if(l[0] in self.drug_targets):
                                    dt1=self.drug_targets[l[0]]
                                    
                                dt2=''
                                if(l[1] in self.drug_targets):
                                    dt2=self.drug_targets[l[1]]
                                x.write("%s\t%s\t%s\t%s\t%s\n" %(l[0], l[1], dt1, dt2, 'hpidb') )
                                
                                ppis.add(l[0]+'-'+l[1])
                                ppis.add(l[1]+'-'+l[0])
                        else:
                            score = float(l[2])
                            if( (not l[0]+'-'+l[1] in ppis) and ( self._checa_drug_target(l[0]) or self._checa_drug_target(l[1]) )  and score>0.8 ):
                                dt1=''
                                if(l[0] in self.drug_targets):
                                    dt1=self.drug_targets[l[0]]
                                    
                                dt2=''
                                if(l[1] in self.drug_targets):
                                    dt2=self.drug_targets[l[1]]
                                x.write("%s\t%s\t%s\t%s\t%s\n" %(l[0], l[1], dt1, dt2, 'predprin') )
                                
                                ppis.add(l[0]+'-'+l[1])
                                ppis.add(l[1]+'-'+l[0])
                    f.close()
            x.close()
    
    def generate_enrichment_plots(self, main_folder, params):
        i=0
        targets=list(params['target_taxon'])
        for g in params['genome']:
            self.target_taxon=str(targets[i])
            i+=1
            
            folder=main_folder+g
            ppis=set()  
            
            info={}
            for color in ['HPIDB', 'PredPrIn', 'HPIDB+PredPrIn']:
                info[color]={ 'nodesh': set(), 'nodesp': set(), 'edges': 0}
            
            cnt=0
            for t in ['hpidb', 'predprin']:
                nameFile=folder+"/new_candidates/predictions.tsv"
                if(t=='hpidb'):
                    nameFile=folder+'/hpidb_pos.tsv'
                 
                if(os.path.isfile(nameFile)):
                    f=open(nameFile,'r')
                    for line in f:
                        l=line.replace('\n','').split('\t')
                        
                        if(t=='hpidb'):
                            if(l[2]==self.target_taxon and not l[0]+'-'+l[1] in ppis):
                                info['HPIDB']['nodesp'].add(l[0])
                                info['HPIDB']['nodesh'].add(l[1])
                                info['HPIDB']['edges']+=1
                                
                                info['HPIDB+PredPrIn']['nodesp'].add(l[0])
                                info['HPIDB+PredPrIn']['nodesh'].add(l[1])
                                info['HPIDB+PredPrIn']['edges']+=1
                                
                                ppis.add(l[0]+'-'+l[1])
                                ppis.add(l[1]+'-'+l[0])
                        else:
                            score = float(l[2])
                            if( not l[0]+'-'+l[1] in ppis and score>0.8 ):
                                info['PredPrIn']['nodesp'].add(l[0])
                                info['PredPrIn']['nodesh'].add(l[1])
                                info['PredPrIn']['edges']+=1
                                
                                info['HPIDB+PredPrIn']['nodesp'].add(l[0])
                                info['HPIDB+PredPrIn']['nodesh'].add(l[1])
                                info['HPIDB+PredPrIn']['edges']+=1
                                
                                ppis.add(l[0]+'-'+l[1])
                                ppis.add(l[1]+'-'+l[0])
                        cnt+=1
                    f.close()
            
            if(cnt>0):
                x=['Nodes-Host','Nodes-Pathogen','Edges']
                dat=[]
                for k in info.keys():
                    y=[ len(info[k]['nodesh']), len(info[k]['nodesp']), info[k]['edges'] ]
                    dat.append( go.Bar(name=k, x=x, y=y, text=y, textposition='auto' ) )
                fig = go.Figure(dat)
                fig.update_layout(barmode='group', xaxis_title="Main Metrics", yaxis_title="Count", width=600, height=400 )
                fig.write_image(folder+'/summary_nodes_edges_enrichment.png')
       
