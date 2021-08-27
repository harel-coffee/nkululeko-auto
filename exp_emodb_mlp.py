# main.py
# Demonstration code to use the ML-experiment framework

import sys
sys.path.append("/home/felix/data/research/nkululeko/src")
import experiment as exp
import dataset as ds
import configparser
import matplotlib.pyplot as plt
import numpy as np
from util import Util

def main(config_file):
    # load one configuration per experiment
    config = configparser.ConfigParser()
    config.read(config_file)
    util = Util()

    # create a new experiment
    expr = exp.Experiment(config)
    print(f'running {expr.name}')

    # load the data
    expr.load_datasets()

    # split into train and test
    expr.fill_train_and_tests()
    util.debug(f'train shape : {expr.df_train.shape}, test shape:{expr.df_test.shape}')

    # extract features
    expr.extract_feats()
    util.debug(f'train feats shape : {expr.feats_train.df.shape}, test feats shape:{expr.feats_test.df.shape}')

    # initialize a run manager
    expr.init_runmanager()

    # run the experiment
    uars_dev, uars_train, losses = expr.run()

    # plot the results
    plot_name = util.get_exp_name()
    fig_dir = util.get_path('fig_dir')

    plot_results(uars_dev,uars_train, losses, fig_dir+plot_name+'_epochs.png')

    util.debug('DONE')

def plot_results(uars_dev, uars_train, losses, name):
    # do a plot per run
    # scale the losses so they fit on the picture
    losses = np.asarray(losses)/2
    plt.figure(dpi=200)
    plt.plot(uars_train, 'green', label='train set') 
    plt.plot(uars_dev, 'red', label='dev set')
    plt.plot(losses, 'grey', label='losses/2')
    plt.xlabel('epochs')
    plt.ylabel('UAR')
    plt.legend()
    plt.savefig(name)
    plt.close()

if __name__ == "__main__":
    main(sys.argv[1])
