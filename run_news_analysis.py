import os
import subprocess
import sys

if __name__ == "__main__":
    # Get the directory of the current script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    print(f"Script directory: {script_dir}")
    
    # Run R script for visualization
    r_script_path = os.path.join(script_dir, 'visualizations.R')
    print(f"R script path: {r_script_path}")
    
    # Change the working directory to the script directory
    os.chdir(script_dir)
    print(f"Changed working directory to: {os.getcwd()}")
    
    # List files in the current directory
    print("Files in the current directory:")
    for file in os.listdir():
        print(file)
    
    # Get the path to Rscript
    rscript_cmd = 'Rscript.exe' if sys.platform.startswith('win') else 'Rscript'
    
    try:
        result = subprocess.run([rscript_cmd, r_script_path], 
                                check=True, 
                                capture_output=True, 
                                text=True)
        print("R script output:")
        print(result.stdout)
        print("\nVisualization complete. Check the generated HTML files in the script directory.")
    except subprocess.CalledProcessError as e:
        print(f"Error running R script: {e}")
        print("R script output:")
        print(e.stdout)
        print("R script error:")
        print(e.stderr)
        print("You can try running the R script manually:")
        print(f"{rscript_cmd} {r_script_path}")
    except FileNotFoundError:
        print("Error: Rscript not found.")
        print("Please ensure R is installed and added to your system PATH.")
        print("You can also try running the R script manually:")
        print(f"{rscript_cmd} {r_script_path}")

    # Print current working directory and list files again
    print("\nFinal working directory:", os.getcwd())
    print("Files in the directory:")
    for file in os.listdir():
        print(file)
