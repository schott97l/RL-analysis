import matplotlib.pyplot as plt
import os
import re
import argparse
import numpy as np
import gym_hypercube
from gym_hypercube.visualization import vis_2d
import matplotlib.animation as animation


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--directory",default="results/")
    parser.add_argument("--batch_size",default=1,type=int)
    parser.add_argument("--eval_freq",default=1,type=int)
    parser.add_argument("--epsilon",default=0.01,type=float)
    parser.add_argument("--title",default="")
    
    parser.set_defaults(log_scale=False)

    args = parser.parse_args()
    
    if not os.path.exists(args.directory + "/visualizations"):
        os.makedirs(args.directory + "/visualizations")

    xs = []
    evaluations = []
    
    for result in os.listdir(args.directory):

        print(result)
        if re.search(r'^.*visualizations.*$', result):
            continue

        evaluation = np.load("{}{}/logs/evaluations.npy".format(
            args.directory,result))

        regex = re.search(r'^.*n([0-9.]*)_([0-9]*)$',result)
        
        if not float(regex.group(1)) in xs:
            xs.append(float(regex.group(1)))
            print(len(xs)-1)
            print(regex.group(2))
            eval_vect = np.zeros(args.batch_size).tolist()
            eval_vect[int(regex.group(2))] = evaluation[:,0]
            evaluations.append(eval_vect)
            print(evaluation.shape)
        else:
            idx = xs.index(float(regex.group(1)))
            print(idx)
            print(regex.group(2))
            evaluations[idx][int(regex.group(2))] = evaluation[:,0]
            print(evaluation.shape)

    evaluations = np.array(evaluations)
    mean = np.mean(evaluations,axis=1)
    if args.batch_size==1:
        std = mean
    else:
        std = np.std(evaluations,axis=1)
    
    xs = list(map(float,xs))
    ys = list(mean)
    zs = list(std)
    data = np.array([xs,ys,zs],dtype=object).transpose()
    data2 = []
    for row in data:
        data2.append(tuple(row))

    data2 = sorted(data2,key=lambda tup: tup[0])
    data = np.array(data2,dtype=object)
    xs = data[:,0]
    mean = data[:,1]
    std = data[:,2]
    
    new = []
    for m in mean:
        new.append(m)
    mean = np.array(new)
    new = []
    for s in std:
        new.append(s)
    std = np.array(new)
    
    mean_convergences=[]
    std_convergences=[]
    for i,x in enumerate(xs):
        convergences = []
        for curve in evaluations[i]:
            convergence=-1
            for j,val in enumerate(curve):
                if val >= 0.1-args.epsilon:
                    convergence = j
                    continue
                if convergence == -1:
                    convergence = len(curve)
            convergences.append(convergence)
        mean_convergences.append(np.mean(convergences))
        std_convergences.append(np.std(convergences))
    mean_convergences=np.array(mean_convergences)
    mean_convergences*=eval_freq
    std_convergences=np.array(std_convergences)
    std_convergences*=eval_freq

    plt.figure()
    plt.errorbar(xs, mean_convergences, std_convergences, fmt="--o")
    plt.title("$\eps$ = ".format(args.epsilon),fontsize=12)
    plt.xlabel(args.title,fontsize=12)
    plt.ylabel("convergence timesteps",fontsize=12)
    plt.tick_params(labelsize=12)

    plt.savefig(args.directory + "/visualizations/convergences.png")
