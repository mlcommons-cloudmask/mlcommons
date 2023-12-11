# Draft: Using singulary with overlay

1. Implemented Singularity with Miniconda Overlay
2. switch to cloudmesh ee
3. Added early stopping feature
4. Improved visualizer.py, changed format to .ipynb, created leaderboard for experiment analysis (incomplete)

## Environmanet

Once logged into login you wll hve to set up the environment as follows:

```bash
loginnode>
  export USER_SCRATCH=~
  export PROJECT_DIR=$USER_SCRATCH/github/mlcommons/benchmarks/cloudmask
  export PYTHON_DIR=$USER_SCRATCH/ENV3
  export PROJECT_DATA=$USER_SCRATCH/data/cloudmask/data
  export TARGET=$PROJECT_DIR/target/rivanna_v0.5_early_stopping
  export CONTAINERDIR=${TARGET}
  export OUTPUTS_DIR="${TARGET}/project/{ee.identifier}"
  export CODE_DIR=$TARGET
```


## Singularity with Miniconda Overlay

```bash
loginnode> 
  cd $TARGET
  singularity pull docker://nvcr.io/nvidia/tensorflow:22.10-tf2-py3
  mv tensorflow_22.10-tf2-py3.sif cloudmask.sif
  singularity overlay create --size 15360 cloudmask-overlay.ext3
  singularity exec --overlay cloudmask-overlay.ext3:rw cloudmask.sif /bin/bash
```

Modify accordingly:

After running this command, you should see a bash shell inside the
referenced singularity container overlayed with the 
`cloudmask-overlay.ext3` file.

```bash
Singularity> 
  wget https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh
  bash Miniconda3-latest-Linux-x86_64.sh -b -p /ext3/miniconda3
  rm Miniconda3-latest-Linux-x86_64.sh
  exit
```

After we are done with the above, we need to copy an env.sh script into the overlay with

```bash
singularity exec -B cloudmask-overlay.ext3:/ext3 cloudmask.sif cp env.sh /ext3/env.sh
```

Now we log into the image again and update it

```bash
loginnode>
  singularity exec --overlay cloudmask-overlay.ext3:rw cloudmask.sif /bin/bash
  source /ext3/env.sh
  conda update -n base conda -y
  conda clean --all --yes
  conda install pip -y
  conda install ipykernel -y
  unset -f which
  which conda
  # output: /ext3/miniconda3/bin/conda
  which python
  # output: /ext3/miniconda3/bin/python
  python --version
  # output: Python 3.11.4
  which pip
  # output: /ext3/miniconda3/bin/pip
  exit
  # exit Singularity
```

### Run Singularity in Slurm

> Make sure you have setup virtual environment ENV3 in your $USER_SCRATCH path. tmptest-singularity.slurm has dependencies on ENV3, which you can refer to in README-Gregor.md</mark>

Rename the overlay image

```bash
[PROJ_DIR]> 
  mv overlay-15GB-500K.ext3 tmptest-overlay-image
```
Do a test run. 

* config_simple.yaml: change experiment.epoch in to 1
* config_simple.yaml: adjust model_file to fit your path
* config_simple.yaml: adjust output_dir to fit your path
* tmptest-singularity.slurm: change job-name epoch to 1
* tmptest-singularity.slurm: change to #SBATCH --time=00:30:00
* tmptest-singularity.slurm: adjust $USER_SCRATCH to fit your path

Create an outputs directory to gather outputs.
And submit the job to SLURM

```bash
[PROJ_DIR]> 
  mkdir -p outputs
  sbatch tmptest-singularity.slurm
  # You see how the job is processing
  make status
```

After the job is done, you can check the result in output/

## 3. Early_stoppage

### Toggle for early_stoppage

The toggle is in config_simple.yaml

```yaml
hyperparameter:
    early_stoppage: True
...
...
...
experiment:
    early_stoppage_tolerance: 25
```

To turn early_stoppage off, set early_stoppage to False, vice versa. Your can also change the tolerance (default is 25) to change the patience.

Once changing is done, you can run experiments with or without early stopping (also works for GRCtest_reproduce_experiments.sh).


## 4. Helper Scripts

There are two helper scripts: clean_outputs.sh and archive_outputs.sh

