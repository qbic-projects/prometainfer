import os
import subprocess

def generate_fileinfo(mzml_dir, output_dir):
    # Set direction with mzML files
    data_dir = mzml_dir

    # Set direction for fileinfo files
    fileinfo_dir = os.path.join(output_dir, 'fileinfo')
    if not os.path.exists(fileinfo_dir):
        os.makedirs(fileinfo_dir)
        print(f"Created default fileinfo directory in {fileinfo_dir}: fileinfo")

    # Read mzML files ending with '.mzML'
    mzml_files = [f for f in os.listdir(data_dir) if f.endswith('.mzML')]

    # Process each mzML file
    for mzml_file in mzml_files:
        file_name = mzml_file.split('.mzML')[0]
        fileinfo_file = f"{file_name}.txt"
        
        # Run Comet only if no corresponding fileinfo file exists
        if not os.path.exists(os.path.join(fileinfo_dir, fileinfo_file)):

            # Perform param search for file to receive adequate Comet results
            cmd = ["FileInfo",
                   "-in", os.path.join(data_dir, mzml_file), "-m", "-p", "-s", "-c",
                   "-out", os.path.join(fileinfo_dir, fileinfo_file)
            ]
            
            print(f"Running: {' '.join(cmd)}")
            
            try:
                result = subprocess.run(cmd, check=True)
            except subprocess.CalledProcessError:
                print(f"Error processing {mzml_file}. Skipping to the next file.")
        else:
            print(f"Fileinfo file for {mzml_file} already exists. Skipping to the next file.")
