
import os
import json
import random
import datetime

import pandas as pd

class HPNetworkAugmentation:
    
    def __init__(self):
        self.base=''
        self.target_taxon=''
        self.string_mapp_taxon=self._get_string_taxon_mapping()
    
    def _get_string_taxon_mapping(self):
        mapp={}
        f=open('mapping_taxons_ok_string.tsv','r')
        for line in f:
            l=line.replace('\n','').split('\t')
            mapp[l[0]]=l[1]
        f.close()
        return mapp
    
    def _map_genome_taxon(self, params):
        map_taxon={}
        taxons=list(params['target_taxon'])
        i=0
        for g in params['genome']:
           map_taxon[g]=str(taxons[i])
           i+=1
        return map_taxon
    
    def _merge_positive_hp_dataset(self, train_folder, size):
        print(self.base+'hpidb_pos.tsv')
        df=pd.read_csv(self.base+'hpidb_pos.tsv', sep='\s+')
        df.columns=['p1', 'p2', 't1', 't2', 'class']
        df=df[ df['t1']==int(self.target_taxon) ]
        
        if(len(df)>0):
            sample=list(df.index)
            if(len(df)>size):
                sample=random.sample( set(df.index), size)    
            for i in sample:
                dat=[]
                try:
                    for el in df.iloc[i,:]:
                        dat.append( str(el) )
                        
                    with open(train_folder+'trainsub_positive.tsv', 'a') as gf:
                        gf.write( '\t'.join(dat)+'\n' )
                    with open(train_folder+'trainsub_dataset.tsv', 'a') as gf:
                        gf.write( '\t'.join(dat)+'\n' )
                except:
                    pass
        return size
        
    def _merge_false_hp_dataset(self, train_folder, size):
        t=self.target_taxon
        t=self.string_mapp_taxon[t]
        df=pd.read_csv('taxon_interactions/'+t+'_neg.tsv', sep='\s+')
        df.columns=['p1', 'p2', 't1', 't2', 'class']
        df=df[ df['t1']==int(self.target_taxon) ]
        
        sample=list(df.index)
        if(len(df)>size):
            sample=random.sample( set(df.index), size)    
        
        for i in sample:
            dat=[]
            try:
                for el in df.iloc[i,:]:
                    dat.append( str(el) )
                    
                with open(train_folder+'trainsub_false.tsv', 'a') as gf:
                    gf.write( '\t'.join(dat)+'\n' )
                with open(train_folder+'trainsub_dataset.tsv', 'a') as gf:
                    gf.write( '\t'.join(dat)+'\n' )
            except:
                pass
    
    def prepare_training_data(self, main_folder, paramsIn):
        train_folder=main_folder+'training_data/'
        if( not os.path.isdir(train_folder) ):
            os.system('mkdir '+train_folder)
        
        map_taxon=self._map_genome_taxon(paramsIn)
        
        params={}
        params['name']="Training - Experiment for context-based PPI network construction hostpathogen predppi "
        params['description']="experiment predprin "
        params['email']="ycfrenchgirl2@gmail.com"
        params['owner']="Yasmmin"
        
        datasets=[]
        ds={}
        ds['name'] = "predprin training"
        ds["prefix"]="trainsub_"
        ds["folder"]=train_folder
        ds["description"]="train individual ppis "
        datasets.append(ds)
        
        params["datasets"]=datasets
        with open(main_folder+'training_params_predprin.json', 'w') as fp:
            json.dump(params, fp)
            
        total_genomes=len(paramsIn['genome'])
        all_subsample=100000
        sample_size=all_subsample//total_genomes
        for g in paramsIn['genome']:
            self.base=main_folder+g+'/'
            self.target_taxon=map_taxon[g]
            
            if( os.path.isfile(self.base+'hpidb_pos.tsv') and os.path.getsize(self.base+'hpidb_pos.tsv') ):
                size_pos=self._merge_positive_hp_dataset(train_folder, sample_size)
                self._merge_false_hp_dataset(train_folder, size_pos)
        
    def _get_protein_partners(self, taxons):
        partners_pathogen={}
        partners_host={}
        
        taxons.add(self.target_taxon)
        for t in taxons:
            if(t in self.string_mapp_taxon.keys()):
                t=self.string_mapp_taxon[t]
        
                aux=partners_host
                if(t==self.target_taxon):
                    aux=partners_pathogen
                    
                f=open('taxon_interactions/'+t+'_pos.tsv','r')
                for line in f:
                    l=line.replace('\n','').split('\t')
                    
                    if (not l[0] in aux.keys()):
                        aux[l[0]] = set()
                    if (not l[1] in aux[l[0]] ):
                        aux[l[0]].add(l[1])
                    
                    if (not l[1] in aux.keys()):
                        aux[l[1]] = set()
                    if (not l[0] in aux[l[1]] ):
                        aux[l[1]].add(l[0])
                f.close()
                
                if(t==self.target_taxon):
                    partners_pathogen=aux
                else:
                    partners_host=aux
                    
        return partners_host, partners_pathogen
    
    def _prepare_taxon_new_ppis(self):
        ppis=set()
        host_taxons=set()
        pathogen_seeds=set()
        seeds=set()
        f=open(self.base+'hpidb_pos.tsv','r')
        for line in f:
            l=line.replace('\n','').split('\t')
            ppis.add(l[0]+'-'+l[1])
            ppis.add(l[1]+'-'+l[0])
            
            seeds.add(l[0]+'-'+l[1])
            
            if(l[2]==self.target_taxon):
                if(not l[3] in host_taxons):
                    host_taxons.add(l[3])
        f.close()
        
        partners_host, partners_pathogen = self._get_protein_partners(host_taxons)
        
        print('Pathogen seeds: ', len(partners_pathogen.keys()) )
        print('Host seeds: ', len(partners_host.keys()) )
        
        f=open(self.base+'log_candidate_generation.tsv','w')
        f.write('name_pathogen\tname_host\tnumber_partners_pathogen\tnumber_partners_host\ttime\n')
        f.close()
        
        newcand=set()
        cnt=1
        #for w in pathogen_seeds:
        for s in seeds:
            k=s.split('-')[0]
            w=s.split('-')[1]
            nh=0
            #for w in host_seeds:
            if( k in partners_pathogen.keys() and w in partners_host.keys() ):
                before = datetime.datetime.now()
                a=0
                for i in partners_pathogen[k]:
                    b=0
                    for j in partners_host[w]:
                        if(not i+"-"+j in ppis and not i+"_"+j in newcand and len(newcand)<250000 ):
                            newcand.add(i+"_"+j)
                    b+=1
                a+=1
                print('\tpartners pathogen: ', len(partners_pathogen[k]) )
                print('\tpartners host: ', len(partners_host[w]) )
                after = datetime.datetime.now()  
                  
                delta = after-before    
                formatted=str(datetime.timedelta(seconds=delta.seconds))
                with open(self.base+'log_candidate_generation.tsv','a') as f:
                    f.write('%s\t%s\t%s\t%s\t%s\n' %(k, w, len(partners_pathogen[k]), len(partners_host[w]), formatted ) )
            
            nh+=1
            print(cnt, '/', len(partners_pathogen.keys()) )
            cnt+=1
            
        ds={}
        if(len(newcand)>0):
            ds['name'] = "predprin new ppis from "+self.target_taxon
            ds["prefix"]="predprin_"
            ds["folder"]=self.base+"new_candidates/"
            ds["description"]="test individual ppis "
            
            listnew=list(newcand)
            cut=round(len(newcand)/2)
            
            g=open(self.base+"new_candidates/predprin_dataset.txt","w")
            
            f=open(self.base+"new_candidates/predprin_positive.txt","w")
            for i in range(cut):
                p1=listnew[i].split("_")[0]
                p2=listnew[i].split("_")[1]
                f.write("%s\t%s\t1\n" %(p1, p2) )
                g.write("%s\t%s\t1\n" %(p1, p2) )
            f.close()
            
            f=open(self.base+"new_candidates/predprin_false.txt","w")
            for i in range(cut, len(newcand)):
                p1=listnew[i].split("_")[0]
                p2=listnew[i].split("_")[1]
                f.write("%s\t%s\t0\n" %(p1, p2) )
                g.write("%s\t%s\t0\n" %(p1, p2) )
            f.close()
            
            g.close()
        return ds    
        
    def prepare_new_ppis(self, main_folder, paramsIn):
        params={}
        params['name']="Evaluation - Experiment for context-based PPI network construction hostpathogen predppi "
        params['description']="experiment predprin "
        params['email']="ycfrenchgirl2@gmail.com"
        params['owner']="Yasmmin"
        datasets=[]
        
        map_taxon=self._map_genome_taxon(paramsIn)
           
        for g in paramsIn['genome']:
            print('======> ', g)
            self.base=main_folder+g+'/'
            self.target_taxon=map_taxon[g]
            
            if( not os.path.isdir(self.base+'new_candidates') ):
                os.system('mkdir '+self.base+'new_candidates')
            
            ds=self._prepare_taxon_new_ppis()
            if( len(ds.keys())>0):
                datasets.append(ds)
                
        params["datasets"]=datasets
        with open(main_folder+'evaluation_params_predprin.json', 'w') as fp:
            json.dump(params, fp)
       
    def execute_training(self, main_folder):
        f=open(main_folder+"execute_predppi.sh","w")
        f.write("#!/bin/bash\n")
        f.write("cd predprin/\n")
        f.write("python3 -m luigi --module main RunPPIExperiment --parameters-file "+main_folder+"training_params_predprin.json --mode train --model None --workers 1")
        f.close()

        os.system("rm predprin/run_experiment.txt")
        print("Executing training with host pathogen pairs ")
        os.system('bash '+main_folder+'execute_predppi.sh')   
        
        
