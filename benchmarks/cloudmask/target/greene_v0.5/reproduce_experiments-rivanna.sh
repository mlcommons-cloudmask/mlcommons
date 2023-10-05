#!/bin/bash
#
# significantly modified by Gregor von Laszewski
#

 Check if a parameter is provided
if [ $# -eq 0 ]; then
    # If no parameter is provided, set it to 1
    RUN=1
else
    # Use the provided parameter
    RUN="$1"
fi

# ####################################
# Runtime Variable
# ####################################

# Array of epochs and times required for jobs
epochsArray=(1 5 10 20 30 50 80 100 200)
timesArray=("00:30:00" "00:40:00" "00:50:00" "01:10:00" "01:30:00" "02:30:00" "3:00:00" "4:00:00" "13:00:00")
REPEAT=5

epochsArray=(2)
timesArray=("00:30:00")
REPEAT=1

# GPU

GPU="v100"
# GPU="a100"

print_header() {
    echo
    echo "# ###################################################################################"
    echo "# $1"
    echo "# ###################################################################################"
    echo
}

#
# #####################################

# Experiments with v100, 1 GPU

# Initial setup for gpu and time for one epoch in simple.slurm file
sed -i 's/--gres=.*/--gres=gpu:'"${GPU}"':1/' simple.slurm

# Initial setup for parameters in config_simple.yaml
sed -i 's/card_name.*/card_name: '"${GPU}"'/' config_simple.yaml
sed -i 's/gpu_count.*/gpu_count: 1/' config_simple.yaml



# Running 5 jobs and then waiting for them to complete before other commands

SLURM_SCRIPT="simple.rivanna.slurm"
SCRIPT="tmp.slurm"
CONFIG="config_simple.yaml"


for((i=1; i<=$REPEAT; i++)); do
    for j in ${!epochsArray[@]}; do
        cp $SLURM_SCRIPT $SCRIPT
        EXPERIMENT_ID=${epochsArray[$j]}_epochs_${i}
        CONFIG_YAML=config_simple_${EXPERIMENT_ID}.yaml

        # Creating script and config copies
        cp ${SCRIPT} simple_${EXPERIMENT_ID}.slurm
        cp $CONFIG $CONFIG_YAML

        # Modifying the copies
        print_header $EXPERIMENT_ID

        # Modify the config file
        sed -i 's/epoch:.*/epoch: '"${epochsArray[$j]}"'/' $CONFIG_YAML
        sed -i 's/log_file:.*/log_file: \.\/cloudmask_'"${EXPERIMENT_ID}"'.log/' $CONFIG_YAML
        sed -i 's/mlperf_logfile:.*/mlperf_logfile: \.\/mlperf_cloudmask_'"${EXPERIMENT_ID}"'.log/' $CONFIG_YAML
        sed -i 's/repeat:.*/repeat: "'"$i"'"/' $CONFIG_YAML

        # modify the slurm script
        sed -i 's/--job-name=.*/--job-name=cloudmask-gpu-greene-epoch-'"${epochsArray[$j]}"'/' ${SCRIPT}
        sed -i 's/--time=.*/--time='"${timesArray[$j]}"'/' ${SCRIPT}
        sed -i 's/gpu0.log/'"gpu0-${EXPERIMENT_ID}.log"'/' ${SCRIPT}
        sed -i 's/--config config_simple\.yaml*/--config config_simple_'"${experiment_ID}"'\.yaml/g' simple_${EXPERIMENT_ID}.slurm

        # RUN

        if [ "$RUN" = "1" ]; then
          sbatch simple_${EXPERIMENT_ID}.slurm
        else
          print_header simple_${EXPERIMENT_ID}.slurm
          cat simple_${EXPERIMENT_ID}.slurm

          print_header $CONFIG_YAML
          cat $CONFIG_YAML
	  
        fi

    done;
done;

