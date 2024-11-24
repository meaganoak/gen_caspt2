import argparse
import os
import re

def main():
    # Define argument parser
    parser = argparse.ArgumentParser(description="Generate multiple SS-, MS- or XMS-CASPT2 files")
    parser.add_argument("basename", type=str, help="Previously run SA-CASSCF output file")
    parser.add_argument("--roots", type=int, required=True, help="Number of roots to generate")
    parser.add_argument("--theory", choices=["caspt2", "ms-caspt2", "xms-caspt2"], required=True, help="Level of theory: caspt2, ms-caspt2, xms-caspt2")
    parser.add_argument("--output_dir", type=str, default=".", help="Optional directory to save input files")


    # Parse arguments
    args = parser.parse_args()

    # Extract base name from the filename argument
    if not args.basename.endswith(".out"):
        raise ValueError("The provided filename must have a .out extension")
    base_name = os.path.splitext(args.basename)[0]

    user = os.getenv("USER")
    if not user:
        raise EnvironmentError("USER environment variable not found")

    output_dir = args.output_dir
    os.makedirs(output_dir, exist_ok=True)

    # Define templates
    templates = {
        "xms-caspt2": """>>COPY /mnt/iusers01/chem01/{user}/scratch/{base_name}.OneRel $Project.OneRel
>>COPY /mnt/iusers01/chem01/{user}/scratch/{base_name}.RasOrb INPORB
>>COPY /mnt/iusers01/chem01/{user}/scratch/{base_name}.RunFile $Project.RunFile
>>COPY /mnt/iusers01/chem01/{user}/scratch/{base_name}.OneInt $Project.OneInt
>>COPY /mnt/iusers01/chem01/{user}/scratch/{base_name}.ChDiag $Project.ChDiag
>>COPY /mnt/iusers01/chem01/{user}/scratch/{base_name}.ChMap $Project.ChMap
>>COPY /mnt/iusers01/chem01/{user}/scratch/{base_name}.ChRed $Project.ChRed
>>COPY /mnt/iusers01/chem01/{user}/scratch/{base_name}.ChRst $Project.ChRst
>>COPY /mnt/iusers01/chem01/{user}/scratch/{base_name}.ChVec1 $Project.ChVec1
>>COPY /mnt/iusers01/chem01/{user}/scratch/{base_name}.NqGrid $Project.NqGrid
>>COPY /mnt/iusers01/chem01/{user}/scratch/{base_name}.JobIph $Project.JobIph

&CASPT2
XMulti=all
IMAG=0.2
Only={root}
MAXITER=100
""",
        "ms-caspt2": """>>COPY /mnt/iusers01/chem01/{user}/scratch/{base_name}.OneRel $Project.OneRel
>>COPY /mnt/iusers01/chem01/{user}/scratch/{base_name}.RasOrb INPORB
>>COPY /mnt/iusers01/chem01/{user}/scratch/{base_name}.RunFile $Project.RunFile
>>COPY /mnt/iusers01/chem01/{user}/scratch/{base_name}.OneInt $Project.OneInt
>>COPY /mnt/iusers01/chem01/{user}/scratch/{base_name}.ChDiag $Project.ChDiag
>>COPY /mnt/iusers01/chem01/{user}/scratch/{base_name}.ChMap $Project.ChMap
>>COPY /mnt/iusers01/chem01/{user}/scratch/{base_name}.ChRed $Project.ChRed
>>COPY /mnt/iusers01/chem01/{user}/scratch/{base_name}.ChRst $Project.ChRst
>>COPY /mnt/iusers01/chem01/{user}/scratch/{base_name}.ChVec1 $Project.ChVec1
>>COPY /mnt/iusers01/chem01/{user}/scratch/{base_name}.NqGrid $Project.NqGrid
>>COPY /mnt/iusers01/chem01/{user}/scratch/{base_name}.JobIph $Project.JobIph

&CASPT2
Multi=all
IMAG=0.2
Only={root}
MAXITER=100
""",
        "caspt2": """>>COPY /mnt/iusers01/chem01/{user}/scratch/{base_name}.OneRel $Project.OneRel
>>COPY /mnt/iusers01/chem01/{user}/scratch/{base_name}.RasOrb INPORB
>>COPY /mnt/iusers01/chem01/{user}/scratch/{base_name}.RunFile $Project.RunFile
>>COPY /mnt/iusers01/chem01/{user}/scratch/{base_name}.OneInt $Project.OneInt
>>COPY /mnt/iusers01/chem01/{user}/scratch/{base_name}.ChDiag $Project.ChDiag
>>COPY /mnt/iusers01/chem01/{user}/scratch/{base_name}.ChMap $Project.ChMap
>>COPY /mnt/iusers01/chem01/{user}/scratch/{base_name}.ChRed $Project.ChRed
>>COPY /mnt/iusers01/chem01/{user}/scratch/{base_name}.ChRst $Project.ChRst
>>COPY /mnt/iusers01/chem01/{user}/scratch/{base_name}.ChVec1 $Project.ChVec1
>>COPY /mnt/iusers01/chem01/{user}/scratch/{base_name}.NqGrid $Project.NqGrid
>>COPY /mnt/iusers01/chem01/{user}/scratch/{base_name}.JobIph $Project.JobIph

&CASPT2
Multi=all
NoMult
IMAG=0.2
Only={root}
MAXITER=100
"""


    }

    # Select the template based on --theory
    template = templates[args.theory]

    # Create input files
    for root in range(1, args.roots + 1):
        content = template.format(
            root=root,
            user=user,
            base_name=base_name,  # Pass the extracted base name
        )
        output_filename = os.path.join(output_dir, f"{base_name}_{args.theory}_root_{root}.inp")


        # Write content to file
        with open(output_filename, "w") as file:
            file.write(content)
        print(f"Created file: {output_filename}")

if __name__ == "__main__":
    main()
