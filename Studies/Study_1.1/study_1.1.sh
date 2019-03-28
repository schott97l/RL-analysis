#!/bin/bash

## Performance en fonction du nombre de dimensions avec moitié high et moitié low reward

PARALLEL_MAX=1

MEAN_BATCH_SIZE=2 #8

POLICY_NAME="DDPG"

EXPLORATION_TIMESTEPS=50000

LEARNING_TIMESTEPS=2000

BUFFER_SIZE=50000

EVAL_FREQ=100

RESET_RADIUS=0.1

ROOT_DIR="$(pwd)/"

RESULT_DIR="results/"

TITLE="dimensions"

X_LABEL="dimensions"

Y_LABEL="reward/step"

HIGH_REWARD_COUNT="half"

LOW_REWARD_COUNT="half"

run_training()
{
  OUTPUT_DIR="${ROOT_DIR}${RESULT_DIR}${POLICY_NAME}_n$1_$2"

  COMMAND="python ../../learn_multidimensional.py\
    --policy_name=$POLICY_NAME\
    --exploration_timesteps=$EXPLORATION_TIMESTEPS\
    --learning_timesteps=$LEARNING_TIMESTEPS\
    --buffer_size=$BUFFER_SIZE\
    --eval_freq=$EVAL_FREQ\
    --dimensions=$1\
    --save\
    --no-render\
    --high_reward_count=$HIGH_REWARD_COUNT\
    --low_reward_count=$LOW_REWARD_COUNT\
    --output=${OUTPUT_DIR}\
    --reset_radius=$RESET_RADIUS"

  eval ${COMMAND}
}


PARALLEL=0
PIDS=()

for i in 2 4 8 16
	#32 64 128 256
do
    for j in $(seq 0 $(($MEAN_BATCH_SIZE-1)))
    do
	echo "Training $i $j"
	run_training $i $j &
	PIDS[$j]=$!

        PARALLEL=$(($PARALLEL+1))
        if [ $PARALLEL -ge $PARALLEL_MAX ]
        then
            PARALLEL=0
	    wait ${PIDS[@]}
	    PIDS=()
        fi
    done
done
wait ${PIDS[@]}


COMMAND2="python ../plot_evaluations.py\
    --directory=$RESULT_DIR\
    --batch_size=$MEAN_BATCH_SIZE\
    --title='$TITLE'\
    --x_label='$X_LABEL'\
    --y_label='$Y_LABEL'\
    --log_scale"

eval ${COMMAND2}

COMMAND3="python ../plot_average_learning_curve.py\
    --directory=$RESULT_DIR\
    --batch_size=$MEAN_BATCH_SIZE\
    --eval_freq=$EVAL_FREQ\
    --title='$TITLE'"

eval ${COMMAND3}
