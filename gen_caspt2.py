import argparse
import os
import re

def create_slurm_job_array(output_dir, base_name, theory, num_roots, multiplicity):
    """Generate a SLURM job array script."""
    script_filename = os.path.join(output_dir, f"{base_name}_{theory}_job_array.slurm")
    with open(script_filename, "w") as script:
        script.write("#!/bin/bash\n")
        script.write(f"#SBATCH --job-name={base_name}_{theory}\n")
        script.write(f"#SBATCH --array=1-{num_roots}\n")
        script.write("#SBATCH --cpus-per-task=4\n")
        script.write("#SBATCH -p multicore\n")
        script.write("#SBATCH --mem=12G\n")
        script.write(f"#SBATCH --output={base_name}_{theory}_root_%a.out\n")
        script.write(f"#SBATCH --error={base_name}_{theory}_root_%a.err\n")
        script.write("\n")
        script.write("### Set up environment\n")
        script.write("module load oakleygroup/openmolcas/24.06\n")  # Adjust module name if needed
        script.write("export OMP_NUM_THREADS=$SLURM_CPUS_PER_TASK\n")
        script.write("TASK_ID=$SLURM_ARRAY_TASK_ID\n")
        script.write("\n")
        script.write(f"export MOLCAS_PROJECT={base_name}_{theory}_root_$TASK_ID\n")
        script.write("export MOLCAS_MEM=12000\n")
        script.write("export MOLCAS_DISK=20000\n")
        script.write("export MOLCAS_PRINT=2\n")
        script.write("export MOLCAS_MOLDEN=ON\n")
        script.write("export CurrDir=$(pwd -P)\n")
        script.write(f"export WorkDir=/scratch/$USER/$MOLCAS_PROJECT/{multiplicity}\n")
        script.write("\n")
        script.write("### Main body\n")
        script.write("mkdir -p $WorkDir\n")
        script.write(f"python /mnt/chem01-rds/OakleyRDS/software/csf4/openmolcas/24.06/pymolcas {base_name}_{theory}_{multiplicity}_root_$TASK_ID.inp 2>> {base_name}_{theory}_{multiplicity}_root_$TASK_ID.err 1>> {base_name}_{theory}_{multiplicity}_root_$TASK_ID.out\n")

    print(f"SLURM job array script created: {script_filename}")


def create_sge_job_array(output_dir, base_name, theory, num_roots, multiplicity):
    """Generate an SGE job array script."""
    script_filename = os.path.join(output_dir, f"{base_name}_{theory}_{multiplicity}_job_array.sh")
    with open(script_filename, "w") as script:
        script.write("#!/bin/bash --login\n")
        script.write("#$ -cwd\n")
        script.write("#$ -V\n")
        script.write(f"#$ -N {base_name}_{theory}_{multiplicity}\n")
        script.write(f"#$ -t 1-{num_roots}\n")
        script.write("#$ -pe smp.pe 4\n")  # Adjust parallel environment as needed
        script.write("\n")
        script.write("### Set up environment\n")
        script.write("module load apps/gcc/openmolcas/21.02\n")  # Adjust for correct module
        script.write("export OMP_NUM_THREADS=$NSLOTS\n")
        script.write("TASK_ID=$SGE_TASK_ID\n")
        script.write("\n")
        script.write(f"export MOLCAS_PROJECT={base_name}_{theory}_{multiplicity}_root_$SGE_TASK_ID\n")
        script.write("export MOLCAS_MEM=12000\n")
        script.write("export MOLCAS_DISK=20000\n")
        script.write("export MOLCAS_PRINT=2\n")
        script.write("export MOLCAS_MOLDEN=ON\n")
        script.write("export CurrDir=$(pwd -P)\n")
        script.write(f"export WorkDir=/scratch/$USER/$MOLCAS_PROJECT/{multiplicity}\n")
        script.write("\n")
        script.write("### Main body\n")
        script.write("mkdir -p $WorkDir\n")
        script.write(f"pymolcas {base_name}_{theory}_{multiplicity}_root_$SGE_TASK_ID.inp 2>> {base_name}_{theory}_{multiplicity}_root_$SGE_TASK_ID.err 1>> {base_name}_{theory}_{multiplicity}_root_$SGE_TASK_ID.out\n")

    print(f"SGE job array script created: {script_filename}")


def main():
    parser = argparse.ArgumentParser(description="Generate multiple CASPT2 input files and SGE job script")
    parser.add_argument("basename", type=str, help="Previously run SA-CASSCF output file")
    parser.add_argument("--roots", type=int, required=True, help="Number of roots to generate")
    parser.add_argument("--theory", choices=["caspt2", "ms-caspt2", "xms-caspt2"], required=True, help="CASPT2 variant")
    parser.add_argument("--output_dir", type=str, default=".", help="Output directory")
    parser.add_argument("--mult", type=str, help="Multiplicity, for scratch dir separation")

    args = parser.parse_args()
    base_name = os.path.splitext(args.basename)[0]
    user = os.getenv("USER")
    if not user:
        raise EnvironmentError("USER environment variable not found")
    os.makedirs(args.output_dir, exist_ok=True)

    # Define templates
    templates = {
        "xms-caspt2": """>>COPY /mnt/iusers01/chem01/{user}/scratch/{base_name}/{base_name}.OneRel $Project.OneRel
>>COPY /mnt/iusers01/chem01/{user}/scratch/{base_name}/{base_name}.RasOrb INPORB
>>COPY /mnt/iusers01/chem01/{user}/scratch/{base_name}/{base_name}.RunFile $Project.RunFile
>>COPY /mnt/iusers01/chem01/{user}/scratch/{base_name}/{base_name}.OneInt $Project.OneInt
>>COPY /mnt/iusers01/chem01/{user}/scratch/{base_name}/{base_name}.ChDiag $Project.ChDiag
>>COPY /mnt/iusers01/chem01/{user}/scratch/{base_name}/{base_name}.ChMap $Project.ChMap
>>COPY /mnt/iusers01/chem01/{user}/scratch/{base_name}/{base_name}.ChRed $Project.ChRed
>>COPY /mnt/iusers01/chem01/{user}/scratch/{base_name}/{base_name}.ChRst $Project.ChRst
>>COPY /mnt/iusers01/chem01/{user}/scratch/{base_name}/{base_name}.ChVec1 $Project.ChVec1
>>COPY /mnt/iusers01/chem01/{user}/scratch/{base_name}/{base_name}.NqGrid $Project.NqGrid
>>COPY /mnt/iusers01/chem01/{user}/scratch/{base_name}/{base_name}.JobIph $Project.JobIph

&CASPT2
XMulti=all
IMAG=0.2
Only={root}
MAXITER=100
""",
        "ms-caspt2": """>>COPY /mnt/iusers01/chem01/{user}/scratch/{base_name}/{base_name}.OneRel $Project.OneRel
>>COPY /mnt/iusers01/chem01/{user}/scratch/{base_name}/{base_name}.RasOrb INPORB
>>COPY /mnt/iusers01/chem01/{user}/scratch/{base_name}/{base_name}.RunFile $Project.RunFile
>>COPY /mnt/iusers01/chem01/{user}/scratch/{base_name}/{base_name}.OneInt $Project.OneInt
>>COPY /mnt/iusers01/chem01/{user}/scratch/{base_name}/{base_name}.ChDiag $Project.ChDiag
>>COPY /mnt/iusers01/chem01/{user}/scratch/{base_name}/{base_name}.ChMap $Project.ChMap
>>COPY /mnt/iusers01/chem01/{user}/scratch/{base_name}/{base_name}.ChRed $Project.ChRed
>>COPY /mnt/iusers01/chem01/{user}/scratch/{base_name}/{base_name}.ChRst $Project.ChRst
>>COPY /mnt/iusers01/chem01/{user}/scratch/{base_name}/{base_name}.ChVec1 $Project.ChVec1
>>COPY /mnt/iusers01/chem01/{user}/scratch/{base_name}/{base_name}.NqGrid $Project.NqGrid
>>COPY /mnt/iusers01/chem01/{user}/scratch/{base_name}/{base_name}.JobIph $Project.JobIph

&CASPT2
Multi=all
IMAG=0.2
Only={root}
MAXITER=100
""",
        "caspt2": """>>COPY /mnt/iusers01/chem01/{user}/scratch/{base_name}/{base_name}.OneRel $Project.OneRel
>>COPY /mnt/iusers01/chem01/{user}/scratch/{base_name}/{base_name}.RasOrb INPORB
>>COPY /mnt/iusers01/chem01/{user}/scratch/{base_name}/{base_name}.RunFile $Project.RunFile
>>COPY /mnt/iusers01/chem01/{user}/scratch/{base_name}/{base_name}.OneInt $Project.OneInt
>>COPY /mnt/iusers01/chem01/{user}/scratch/{base_name}/{base_name}.ChDiag $Project.ChDiag
>>COPY /mnt/iusers01/chem01/{user}/scratch/{base_name}/{base_name}.ChMap $Project.ChMap
>>COPY /mnt/iusers01/chem01/{user}/scratch/{base_name}/{base_name}.ChRed $Project.ChRed
>>COPY /mnt/iusers01/chem01/{user}/scratch/{base_name}/{base_name}.ChRst $Project.ChRst
>>COPY /mnt/iusers01/chem01/{user}/scratch/{base_name}/{base_name}.ChVec1 $Project.ChVec1
>>COPY /mnt/iusers01/chem01/{user}/scratch/{base_name}/{base_name}.NqGrid $Project.NqGrid
>>COPY /mnt/iusers01/chem01/{user}/scratch/{base_name}/{base_name}.JobIph $Project.JobIph

&CASPT2
Multi=all
NoMult
IMAG=0.2
Only={root}
MAXITER=100
"""
    }

    template = templates[args.theory]
    for root in range(1, args.roots + 1):
        content = template.format(root=root, user=user, base_name=base_name)
        output_filename = os.path.join(args.output_dir, f"{base_name}_{args.theory}_{args.mult}_root_{root}.inp")
        with open(output_filename, "w") as file:
            file.write(content)
        print(f"Created file: {output_filename}")

    create_slurm_job_array(args.output_dir, base_name, args.theory, args.roots, args.mult)

if __name__ == "__main__":
    main()

