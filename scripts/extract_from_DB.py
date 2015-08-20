#extract_from_DB.py
#Author: Azedine Zoufir
# CMI -  University of Cambridge
#19/8/2015

import MySQLdb
import pandas as pd


DATA_DIR = '/scratch/az338/ucc-fileserver/ucc_az/azoles_synergistic_tox_Nina/data/'

# import molecules
azoles = pd.read_excel(DATA_DIR+'List of azoles.xlsx','Ark1')
compounds = azoles['Name'][1:].tolist()

# conect to chembl 20 
db=MySQLdb.connect(host="localhost",user="az338",passwd="pleasechange",db="chembl_20")
cursor = db.cursor()

# extract compound ids, smiles and properties corresponding to the above compounds
molregno = []
smiles = []
properties = []
for c in compounds:
    cursor.execute("select molregno from molecule_dictionary where pref_name='"+c+"'")
    m = cursor.fetchone()[0]
    molregno.append(m)
    cursor.execute("select canonical_smiles from compound_structures where molregno="+str(m))
    smiles.append(cursor.fetchone()[0])
    cursor.execute('select * from compound_properties where molregno='+str(m))
    properties.append(cursor.fetchone())
    
properties = [[str(p) for p in tmp] for tmp in properties]
cursor.execute('show columns from compound_properties')
prop_names = [r[0] for r in cursor.fetchall()]

# export to file 
f = open(DATA_DIR+'compound_properties.txt','w')
f.write('compound'+'\t'+'smiles'+'\t'+'\t'.join(prop_names)+'\n')
for i in xrange(len(properties)):
    f.write(compounds[i]+'\t'+smiles[i]+'\t'+'\t'.join(list(properties[i]))+'\n')
f.close()



# get bioactivities  for the above compounds 
# running time: 5mn approx.
i = 0
activities = []
for c in molregno:
    i+=1
    if i%5 == 0: print 'Extracting bioactivity... compound',i
    cursor.execute("select activity_id, molregno, assay_id, doc_id, concat(standard_relation,round(standard_value,3), standard_units) as activity, standard_relation,round(standard_value,3),standard_units, published_type, activity_comment, potential_duplicate as previously_reported,data_validity_comment from activities where data_validity_comment!='Potential author error' and data_validity_comment!='Outside typical range' and data_validity_comment!='Non standard unit for type' and data_validity_comment!='Author confirmed error' and molregno="+str(c))
    res = cursor.fetchall()
    if len(res) > 0:
        activities.append(res)

assayIDs = []
for a1 in activities:
    for a2 in a1:
        assayIDs.append(str(a2[2]))

assays = []
for a in assayIDs :
    res = cursor.execute('select assay_id, tid, description, assay_type, assay_test_type, assay_organism, confidence_score from assays where assay_id='+a)
    assays.append(cursor.fetchall()[0])
   
targets = [] 
targetIDs = [str(a[1]) for a in assays]
for t in targetIDs :
    res = cursor.execute('select tid, target_type, pref_name, organism from target_dictionary where tid='+t)
    targets.append(cursor.fetchall()[0])

# Create target dictionary (key= tid, value=[target,organism])
target_d = {id:[target,org] for id,type,target,org in targets}

# Similarly create assay dictionary (key= aid, value=[target,target_organism,description,assay_type,assay_organism, confidence_score])
assay_d  = {id:[target_d[tid][0],target_d[tid][1],desc,type,test,org,conf] for id,tid,desc,type,test,org,conf in assays}

# and finally compound dictionary
compound_d = {id:c for id,c in zip(molregno,compounds)}

# Merge and export results in a single file
f= open(DATA_DIR+'azoles_bioactivities.txt','w')
f.write('activity_id\tcompound_id\tcompound\ttarget\ttarget_org\tassay_id\tassay_desc\tassay_org\tconfidence_score\tdoc_id\tactivity\ttype\tcomment\tquality_flag\tpreviously_reported\n')
for a in activities:
    for r in a:
        r = list(r)
        if str(r[4]).startswith('='): r[4]=str(r[4]).lstrip('=')
        row = [r[0],r[1],compound_d[r[1]],assay_d[r[2]][0],assay_d[r[2]][1],r[2],assay_d[r[2]][2],assay_d[r[2]][5],assay_d[r[2]][6],r[3],r[4],r[8],r[9],r[11],r[10]]
        f.write('\t'.join([str(x) for x in row])+'\n')
f.close()

