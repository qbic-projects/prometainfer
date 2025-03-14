# ProMetaInfer

> [!NOTE]
> Pipeline is still in the making.

Official repository for ProMetaInfer: A tool for inferring missing metadata in proteomics data using machine learning and database search.


Run pipeline with: 

```
python infer_metadata.py --mzml_dir <path_to_mzml_files> \
                         --output_dir <path_to_output_directory> \
                         --idxml_dir <path_to_idxml_directory> \
                         --database <path_to_protein_database> \
                         --comet_exe <path_to_comet_executable>
```



> [!NOTE]
> Give complete path to comet executable


Requirements to run the tool:

- Python >= 3
- Install OpenMS
- Install Docker
- Download swissprot database and speficy path to it
- Download Comet and specify comet.exe file (make sure it is executable)
- pull docker container (https://hub.docker.com/r/elisamaske/predict_tolerances_container) for param-medic predictions with:

  ```
  docker pull elisamaske/predict_tolerances_container
  ```
