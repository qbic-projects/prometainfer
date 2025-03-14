# ProMetaInfer

NOTE: Pipeline is still in the making.

Official repository for ProMetaInfer: A tool for inferring missing metadata in proteomics data using machine learning and database search.


Run pipeline with: 
python infer_metadata.py --mzml_dir ../automation_test/mzml --output_dir ../automation_test/output --idxml_dir ../automation_test/output/idxml --database "../../data/proteomes/uniprot_sprot.fasta" --comet_exe "/mnt/volume/elisa/orphan_test/master_thesis/Comet/comet.exe"



- give complete path for comet executable

- download swissprot database and speficy path to it