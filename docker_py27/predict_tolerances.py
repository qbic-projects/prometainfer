import os
import subprocess
import argparse

### IMPORTANT: Python 2.7 required.
def main():
    parser = argparse.ArgumentParser(description="Predict mass tolerances for proteomics data using param-medic.")
    parser.add_argument('--mzml_dir', type=str, required=True, help="Folder path containing mzML files.")
    parser.add_argument('--output_dir', type=str, required=True, help="Directory where the param-medic output .csv files will be stored.")
    args = parser.parse_args()

    # Set direction with mzML files
    data_dir =  args.mzml_dir

    # Set direction for param-medic tolerance predictions
    pred_dir = os.path.join(args.output_dir, 'tolerances')
    if not os.path.exists(pred_dir):
        os.makedirs(pred_dir)
        print("Created default tolerances directory in {}: tolerances".format(''.join(args.output_dir)))

    # Read mzML files ending with '.mzML'
    mzml_files = [f for f in os.listdir(data_dir) if f.endswith('.mzML')]

    # Process each mzML file
    for mzml_file in mzml_files:
        file_name = mzml_file.split('.mz')[0]
        params_file = "{}_params.txt".format(file_name)
        
        # Run param-medic only if file wasn't already created
        if not os.path.exists(os.path.join(pred_dir, params_file)):

            # Perform param search for file to receive mass tolerances for more adequate 
            # peptide identification results
            cmd = [
                "param-medic",
                os.path.join(data_dir, mzml_file)
            ]
            
            print("Running: {}".format(' '.join(cmd)))
            
            try:
                with open(os.path.join(pred_dir, params_file), "w") as outfile:
                    subprocess.check_call(cmd, stdout=outfile)
            except subprocess.CalledProcessError:
                print("Error processing {}. Skipping to the next file.".format(mzml_file))
        else:
            print("Tolerances file for {} already exists. Skipping to the next file.".format(mzml_file))

if __name__ == "__main__":
    main()