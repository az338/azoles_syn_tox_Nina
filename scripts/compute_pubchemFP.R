library(Rcpi)

DATA_DIR='/scratch/az338/ucc-fileserver/ucc_az/azoles_synergistic_tox_Nina/data/'
mols = readMolFromSmi(file.path(DATA_DIR,'standardised_azoles_smiles.smi'),type='mol')

pb_fp = extractDrugPubChemComplete(mols)
write.table(pb_fp,file.path(DATA_DIR,'azoles_pubchemFP'),row.names=F,col.names=F,quote=F,sep='\t')
