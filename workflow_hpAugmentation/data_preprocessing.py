
import os
import wget
import zipfile
import gzip
import json
import time

import pandas as pd

import urllib.request
import urllib.parse
from urllib import request, parse

from ete3 import NCBITaxa

class DataPreprocessing:
    def __init__(self):
        self.taxonomy=NCBITaxa()
        self.loaded_taxons=self._get_locally_available_string_taxons()
        self.string_mapp_taxon=self._get_string_taxon_mapping()
    
    def _get_string_taxon_mapping(self):
        mapp={}
        if ( os.path.isfile('mapping_taxons_ok_string.tsv') ):
            f=open('mapping_taxons_ok_string.tsv','r')
            for line in f:
                l=line.replace('\n','').split('\t')
                mapp[l[0]]=l[1]
            f.close()
        return mapp
    
    def _get_locally_available_string_taxons(self):
        taxons=set()
        if(not os.path.isdir('taxon_interactions')):
            os.system('mkdir taxon_interactions')
            
        for f in os.listdir('taxon_interactions'):
            taxon=f.split('_')[0]
            if(not taxon in taxons):
                taxons.add(taxon)
        return taxons
    
    def ___feed_taxon_mapping(self, tquery, tok):
        self.string_mapp_taxon[str(tquery)]=str(tok)
        with open('mapping_taxons_ok_string.tsv','a') as gf:
            gf.write("%s\t%s\n" %(tquery, tok) )
            
    
    def __check_taxonomy_string(self, original):
        if( str(original) in self.string_mapp_taxon.keys()):
            return True, self.string_mapp_taxon[str(original)]
        else:
            proteins={}
            flag=True
            taxon_ok=False
            t=original
            lineage=self.taxonomy.get_lineage(int(t))
            j=2
            while(flag):
                try:
                    t=str(t)
                    if(not os.path.isfile('taxon_interactions/'+t+'_string.gz')):
                        name=wget.download('https://stringdb-static.org/download/protein.links.v11.5/'+t+'.protein.links.v11.5.txt.gz', out='taxon_interactions/'+t+'_string.gz')
                    
                    if( not os.path.isfile('taxon_interactions/'+t+'_pos_raw.tsv') or os.path.getsize('taxon_interactions/'+t+'_pos_raw.tsv')==0 ):
                        for group in ['pos','neg']:
                            f=open('taxon_interactions/'+t+'_'+group+'_raw.tsv','w')
                            f.close()
                        
                        with gzip.open('taxon_interactions/'+t+'_string.gz', 'rb') as f:
                            temp=f.read()
                        ppis=str(temp).replace("'",'').split('\\n')[1:]
                        for p in ppis:
                            l=p.split(' ')
                            if( len(l)>1 ):
                                if(l[0] != l[1]):
                                    if( float(l[-1])>=800 or float(l[-1])<=300 ):
                                        if(not l[0] in proteins):
                                            proteins[l[0]]=t
                                        if(not l[1] in proteins):
                                            proteins[l[1]]=t
                                            
                                    if(float(l[-1])>=800):
                                        with open('taxon_interactions/'+t+'_pos_raw.tsv','a') as g:
                                            g.write('%s\t%s\t1\n' %(l[0], l[1]) )
                                            
                                    if(float(l[-1])<=300):
                                        with open('taxon_interactions/'+t+'_neg_raw.tsv','a') as g:
                                            g.write('%s\t%s\t0\n' %(l[0], l[1]) )
                                
                    flag=False
                    taxon_ok=True
                    
                    os.system('rm taxon_interactions/'+t+'_string.gz')
                    self.loaded_taxons.add(str(original))
                    self.___feed_taxon_mapping( str(original), t)
                except:
                    t=lineage[(-1)*j]
                    if(j==3):
                        flag=False
                    j+=1
                    
            if (len(proteins)>0):
                with open(self.main_folder+"string_entries.tsv","a") as g:
                    for p in proteins.keys():
                        g.write("%s\t%s\n" %(p, proteins[p]) )
        
        return taxon_ok, t
    
    def _parse_combined_result(self, df):
        
        if(not str(self.target_taxon) in self.loaded_taxons):
            flag, taxont=self.__check_taxonomy_string(self.target_taxon)
        else:
            taxont=self.string_mapp_taxon[str(self.target_taxon)]
                
        taxons={}
        proteins={}
        pairs=set()
        if( 'Qry_ID' in df.columns ):
            query='Qry_ID'
        if( 'Pathogen_Input_ID' in df.columns ):
            query='Pathogen_Input_ID'
        df=df[ ['HPIDB_Pathogen_ID', 'HPIDB_Host_ID', 'HPIDB_Pathogen_Taxon', 'HPIDB_Host_Taxon', query] ]
        g=open(self.base+'hpidb_pos.tsv', 'w')
        for i in range(len(df)):
            p1=df.iloc[i, 0]
            p2=df.iloc[i, 1]
            if( p1.startswith('UNIPROT_AC') and p2.startswith('UNIPROT_AC') ):
                p1=p1.split(':')[-1]
                p2=p2.split(':')[-1]
                
                if(p1 != p2):
                    taxon1=str(df.iloc[i, 2]).split('|')[-1].split(' (')[0]
                    taxon2=str(df.iloc[i, 3]).split('|')[-1].split(' (')[0]
                    
                    flag_tax=True
                    taxid=self.taxonomy.get_name_translator([taxon1])
                    if(len(taxid)>0):
                        taxon1=str(taxid[taxon1][0])
                        
                        if(not taxon1 in taxons.keys()):
                            flag=True
                            if(not str(taxon1) in self.loaded_taxons):
                                flag, taxon=self.__check_taxonomy_string(taxon1)
                            if(flag):
                                if(not str(taxon1) in self.string_mapp_taxon.keys()):
                                    self.string_mapp_taxon[str(taxon1)]=str(taxon1)
                                taxons[str(taxon1)]=self.string_mapp_taxon[str(taxon1)]
                            else:
                                taxons[str(taxon1)]=None
                                flag_tax=flag_tax and False  
                        else:
                            taxon1=taxons[str(taxon1)]
                            if(taxon1==None):
                                flag_tax=flag_tax and False        
                    else:
                        flag_tax=flag_tax and False
                            
                    taxid=self.taxonomy.get_name_translator([taxon2])
                    if(len(taxid)>0):
                        taxon2=str(taxid[taxon2][0])
                        
                        if(not str(taxon2) in taxons.keys()):
                            flag=True
                            if(not str(taxon2) in self.loaded_taxons):
                                flag, taxon=self.__check_taxonomy_string(str(taxon2))
                            if(flag):
                                if(not str(taxon2) in self.string_mapp_taxon.keys()):
                                    self.string_mapp_taxon[str(taxon2)]=str(taxon2)
                                taxons[str(taxon2)]=self.string_mapp_taxon[str(taxon2)]
                            else:
                                taxons[str(taxon2)]=None
                                flag_tax=flag_tax and False  
                        else:
                            taxon2=taxons[str(taxon2)]
                            if(taxon2==None):
                                flag_tax=flag_tax and False   
                    else:
                        flag_tax=flag_tax and False 
                        
                    if(flag_tax):
                        ide=p1+'-'+p2
                        if (not ide in pairs):
                            if(not p1 in proteins.keys()):
                                proteins[p1]=taxon1
                            if(not p2 in proteins.keys()):
                                proteins[p2]=taxon2
                                
                            pairs.add(ide)
                            g.write("%s\t%s\t%s\t%s\t1\n" %(p1, p2, taxon1, taxon2)) 
                            
                        p1=df.iloc[i,4]
                        ide=p1+'-'+p2
                        if (not ide in pairs):
                            if(not p1 in proteins.keys()):
                                proteins[p1]=self.target_taxon
                            pairs.add(ide)
                            g.write("%s\t%s\t%s\t%s\t1\n" %(p1, p2, taxont, taxon2))
        g.close()
                
        if (len(proteins)>0):
            with open(self.main_folder+"hpidb_entries.tsv","a") as g:
                for p in proteins.keys():
                    g.write("%s\n" %(p) )
    
    def _parse_mitab(self, df):
                
        taxons={}
        proteins=set()
        pairs=set()
        df=df[ ['protein_xref_2', 'protein_xref_1', 'protein_taxid_2', 'protein_taxid_1', 'protein_xref_2'] ]
        g=open(self.base+'hpidb_pos.tsv', 'w')
        for i in range(len(df)):
            p1=df.iloc[i, 0]
            p2=df.iloc[i, 1]
            if( p1.startswith('uniprotkb') and p2.startswith('uniprotkb') ):
                p1=p1.split(':')[-1]
                p2=p2.split(':')[-1]
                
                if(p1 != p2):
                    taxon1=str(df.iloc[i, 2]).split('|')[-1].split(' (')[0]
                    taxon2=str(df.iloc[i, 3]).split('|')[-1].split(' (')[0]
                    
                    flag_tax=True
                    if(not str(taxon1) in taxons.keys()):
                        flag=True
                        if(not str(taxon1) in self.loaded_taxons):
                            flag, taxon=self.__check_taxonomy_string(str(taxon1))
                        if(flag):
                            if(not str(taxon1) in self.string_mapp_taxon.keys()):
                                self.string_mapp_taxon[str(taxon1)]=str(taxon1)
                            taxons[str(taxon1)]=self.string_mapp_taxon[str(taxon1)]
                        else:
                            taxons[str(taxon1)]=None
                            flag_tax=flag_tax and False    
                    else:
                        taxon1=taxons[taxon1]
                        if(taxon1==None):
                            flag_tax=flag_tax and False      
                            
                    if(not str(taxon2) in taxons.keys()):
                        flag=True
                        if(not str(taxon2) in self.loaded_taxons):
                            flag, taxon=self.__check_taxonomy_string(str(taxon2))
                        if(flag):
                            if(not str(taxon2) in self.string_mapp_taxon.keys()):
                                self.string_mapp_taxon[str(taxon2)]=str(taxon2)
                            taxons[str(taxon2)]=self.string_mapp_taxon[str(taxon2)]
                        else:
                            taxons[str(taxon2)]=None
                            flag_tax=flag_tax and False  
                    else:
                        taxon2=taxons[str(taxon2)]
                        if(taxon2==None):
                            flag_tax=flag_tax and False  
                    
                    if(flag_tax):    
                        ide=p1+'-'+p2
                        if ( (not ide in pairs) and flag_tax ):
                            if(not p1 in proteins):
                                proteins.add(p1)
                            if(not p2 in proteins):
                                proteins.add(p2)
                                
                            pairs.add(ide)
                            g.write("%s\t%s\t%s\t%s\t1\n" %(p1, p2, taxon1, taxon2)) 
                            
        g.close()
        print(self.base, len(pairs))
        
        if (len(proteins)>0):
            with open(self.main_folder+"hpidb_entries.tsv","a") as g:
                for p in proteins:
                    g.write("%s\n" %(p) )
        
    def parse_hpidb_results_batch(self, main_folder, data_config):
        if(not os.path.isfile(main_folder+"string_entries.tsv")):
            f=open(main_folder+"string_entries.tsv","w")
            f.close()
        
        if(not os.path.isfile(main_folder+"hpidb_entries.tsv")):
            f=open(main_folder+"hpidb_entries.tsv","w")
            f.close()
        
        for i in range( len(data_config) ):
            self.base=main_folder+'/'+data_config.iloc[i,0]+'/'
            self.hpnet=data_config.iloc[i,1]
            self.method=data_config.iloc[i,2]
            self.target_taxon=data_config.iloc[i,3]
            self.main_folder=main_folder
            
            self.parse_hpidb_results()
    
    def parse_hpidb_results(self):
        with zipfile.ZipFile(self.base+self.hpnet, 'r') as zip_ref:
            zip_ref.extractall(self.base+'hpidb')
        
        for f in os.listdir(self.base+'hpidb'):
            if(f.endswith('_res.tsv')):
                df=pd.read_csv(self.base+'hpidb/'+f, sep='\t')
                self._parse_combined_result(df)
                
            if(f.endswith('mitab.txt')):
                df=pd.read_csv(self.base+'hpidb/'+f, sep='\t')
                self._parse_mitab(df)
        
    def _prepare_predprin_data(self, dat):
        if(not os.path.isfile('predprin/sequence_data/'+dat[1]+".fasta" )):
            f=open('predprin/sequence_data/'+dat[1]+'.fasta','a')
            f.write(">%s\n%s\n" %(dat[1], dat[-1]) )
            f.close()
            
        if(not os.path.isfile('predprin/annotation_data/'+dat[1]+".tsv" )):
            car=[]
            cc=dat[6]
            if(cc!=''):
                for a in cc.split(';'):
                    car.append(a.split(" ")[-1].replace('[','').replace(']','') )
            if(len(car)==0):
                car='None'
            else:
                car=' '.join(car)
            
            far=[]
            mf=dat[7]
            if(mf!=''):
                for a in mf.split(';'):
                    far.append(a.split(" ")[-1].replace('[','').replace(']','') )
            if(len(far)==0):
                far='None'
            else:
                far=' '.join(far)
            
            par=[]
            bp=dat[8]
            if(bp!=''):
                for a in bp.split(';'):
                    par.append(a.split(" ")[-1].replace('[','').replace(']','') )
            if(len(par)==0):
                par='None'
            else:
                par=' '.join(par)
            
            kk=[]
            kos=dat[9]
            if(kos!=''):
                for a in kos.split(';'):
                    if(a!=''):
                        kk.append(a)
            if(len(kk)==0):
                kk='None'
            else:
                kk=' '.join(kk)
            
            pfam=[]
            pf=dat[10]
            if(pf!=''):
                for a in pf.split(';'):
                    if(a!=''):
                        pfam.append(a)
            if(len(pfam)==0):
                pfam='None'
            else:
                pfam=' '.join(pfam)
            
            drugs=[]
            dr=dat[11]
            if(pf!=''):
                for a in dr.split(';'):
                    if(a!=''):
                        drugs.append(a)
            if(len(drugs)==0):
                drugs='None'
            else:
                drugs=' '.join(drugs)
            
            data=[dat[1], car, far, par, kk, pfam, drugs]
                        
            f=open('predprin/annotation_data/'+dat[1]+'.tsv','a')
            f.write( ('\t'.join(data))+"\n" )
            f.close()
    
    def _get_uniprot_identifiers_batch(self, source_db, identifiers, annotated):
        if(source_db=='STRING'):
            ids=list(identifiers.keys())
        if(source_db=='UniProtKB_AC-ID'):
            ids=list(identifiers)
        
        j=1
        for i in range(0,len(ids),10000):
            subids=ids[i:i+10000]
            
            dat={}
            dat['ids']=','.join(subids)
            dat['from']=source_db
            dat['to']='UniProtKB'
            data = parse.urlencode(dat).encode()
            req =  request.Request('https://rest.uniprot.org/idmapping/run', data=data) # this will make the method "POST"
            resp = request.urlopen(req)
            parsed=json.loads(resp.read().decode("utf-8"))
            job=parsed['jobId'] 
            #print(job)
            
            time.sleep(10)
            check=False
            text=[]
            while(not check):
                try:
                    link="https://rest.uniprot.org/idmapping/uniprotkb/results/stream/"+job+"?fields=accession%2Creviewed%2Cid%2Cgene_names%2Cec%2Cgo_c%2Cgo_f%2Cgo_p%2Cxref_ko%2Cxref_pfam%2Cxref_drugbank%2Csequence&format=tsv"
                    resp= urllib.request.urlopen(link)
                    data=resp.read()
                    encoding = resp.info().get_content_charset('utf-8')
                    
                    text=data.decode(encoding).split('\n')[1:]
                    check=True
                    #print('ok')
                except:
                    #print('not ok')
                    check=False
                    
            #print('ids input:', len(subids), 'ids received:', len(text) )    
            #print('\tlength data uniprot: ', len(text))
            for line in text:
                l=line.split("\t")
                
                if( len(l)>1 ):
                    if(not l[1] in annotated):
                        self._prepare_predprin_data(l)
                            
                    with open('mapping_geneName_uniprot.tsv', 'a') as g:
                        g.write('%s\t%s\n' %(l[1], l[4] ) )
                        
                    if(source_db=='STRING'):
                        with open('mapping_string_uniprot.tsv', 'a') as g:
                            g.write('%s\t%s\t%s\t%s\n' %(l[0], l[1], l[4], identifiers[l[0]] ) )
                            
                    
            j+=1
    
    def __get_mapped_taxons(self):
        mapped_taxons=set()
        if(not os.path.isfile('mapping_string_uniprot.tsv')):
            f=open('mapping_string_uniprot.tsv','w')
            f.close()
        else:
            f=open('mapping_string_uniprot.tsv','r')
            for line in f:
                l=line.replace('\n','').split('\t') # string_id, uniprot_id, gene_name, taxon_id
                mapped_taxons.add(l[3])
            f.close()
        return mapped_taxons
    
    def __get_annotated_proteins(self):
        proteins_annotated=set()
        for f in os.listdir('predprin/annotation_data'):
            name=f.split('.')[0]
            if(not name in proteins_annotated):
                proteins_annotated.add(name)
        return proteins_annotated
        
    def _get_annotations_string(self):
        mapped_taxons=self.__get_mapped_taxons()
        proteins_annotated = self.__get_annotated_proteins()
        
        string_ids={}  
        f=open(self.main_folder+'string_entries.tsv','r')
        for line in f:
            l=line.replace('\n','').split('\t')
            if(not l[1] in mapped_taxons):
                string_ids[l[0]]=l[1]
        f.close()
        self._get_uniprot_identifiers_batch('STRING', string_ids, proteins_annotated)    
    
    def _get_annotations_hpidb(self):
        proteins_annotated = self.__get_annotated_proteins()
        
        hpidb_ids=set()       
        f=open(self.main_folder+'hpidb_entries.tsv','r')
        for line in f:
            l=line.replace('\n','')
            if(not l in proteins_annotated):
                hpidb_ids.add(l)
        f.close()
        self._get_uniprot_identifiers_batch('UniProtKB_AC-ID', hpidb_ids, proteins_annotated)
        
    def prepare_protein_annotations_data_batch(self, main_folder, data_config):
        if(not os.path.isdir('predprin/annotation_data')):
            os.system('mkdir predprin/annotation_data')
            
        if(not os.path.isdir('predprin/sequence_data')):
            os.system('mkdir predprin/sequence_data')
            
        self.main_folder=main_folder
        """
        for i in range( len(data_config) ):
            self.base=main_folder+'/'+data_config.iloc[i,0]+'/'
            self.hpnet=data_config.iloc[i,1]
            self.method=data_config.iloc[i,2]
            self.target_taxon=data_config.iloc[i,3]
            self.main_folder=main_folder
            
        """
        self.prepare_protein_annotations_data()
              
    def prepare_protein_annotations_data(self):
        self._get_annotations_string()
        self._get_annotations_hpidb()
    
    def _get_mapped_string_ids_by_taxon(self):
        mapped_string_ids={}
        f=open('mapping_string_uniprot.tsv','r')
        for line in f:
            l=line.replace('\n','').split('\t') # string_id, uniprot_id, gene_name, taxon_id
            
            if(not l[3] in mapped_string_ids.keys()):
                mapped_string_ids[l[3]]={}
            mapped_string_ids[l[3]][l[0]]=l[1]
        f.close()
        
        return mapped_string_ids
        
    def handle_singleOrganism_interactions_string_mapping(self):
        taxon_interactions = self._get_mapped_string_ids_by_taxon()
                
        for taxon in taxon_interactions.keys():
            mapp=taxon_interactions[taxon]
            
            for group in ['pos','neg']:
                if( not os.path.isfile('taxon_interactions/'+taxon+'_'+group+'.tsv') and os.path.isfile('taxon_interactions/'+taxon+'_'+group+'_raw.tsv') ):
                    clas=1
                    if(group=='neg'):
                        clas=0
                        
                    gf=open('taxon_interactions/'+taxon+'_'+group+'.tsv','w')
                    f=open('taxon_interactions/'+taxon+'_'+group+'_raw.tsv','r')
                    for line in f:
                        l=line.replace('\n','').split('\t')
                        if(l[0] in mapp.keys() and l[1] in mapp.keys()):
                            gf.write('%s\t%s\t%s\t%s\t%i\n' %( mapp[l[0]], mapp[l[1]], taxon, taxon, clas) )
                    f.close()
                    gf.close()
                    
                    os.system('rm taxon_interactions/'+taxon+'_'+group+'_raw.tsv')
                
            
