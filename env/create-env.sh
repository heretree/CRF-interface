#! /bin/bash
set -e 

. config.sh
echo $PATH_TO_VENV
conda create --prefix $PATH_TO_VENV python=3.5

source $CONDA_PREFIX/etc/profile.d/conda.sh
conda activate $PATH_TO_VENV
pip install -r requirements.txt
conda deactivate