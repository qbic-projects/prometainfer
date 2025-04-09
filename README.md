# ProMetaInfer

Official repository for ProMetaInfer: A tool for inferring missing metadata in proteomics data using machine learning and database search.


### Requirements:

- Python >= 3
- Install OpenMS
- Install Docker
- Download Swissprot database as fasta and speficy path to it (https://www.uniprot.org/uniprotkb?query=reviewed:true)
- Download Comet and specify comet.exe file (make sure it is executable, https://github.com/UWPR/Comet/releases/tag/v2025.01.0)
- Pull docker container for param-medic predictions with (https://hub.docker.com/r/elisamaske/predict_tolerances_container)

  ```
  docker pull elisamaske/predict_tolerances_container
  ```

### Recommended Setup:

We recommend running ProMetaInfer in a dedicated Conda environment for better reproducibility and dependency management.

To set it up, run the following:

  ```
  conda create -n prometa_env python=3.10
  conda activate prometa_env
  pip install -r requirements.txt
  ```

Make sure all additional tools and databases (OpenMS, Docker, SwissProt FASTA, Comet) are properly installed and configured as described above.

### Run Pipeline with: 

```
python infer_metadata.py --mzml_dir <path_to_mzml_files> \
                         --output_dir <path_to_output_directory> \
                         --idxml_dir <path_to_idxml_directory> \
                         --database <path_to_protein_database> \
                         --comet_exe <path_to_comet_executable>
```



> [!IMPORTANT]
> Give complete path to comet executable
