# util.py
import audeer
import ast 
import sys
import glob_conf
import numpy as np
import os.path
import configparser
import audformat
import pandas as pd

class Util:
        
    def get_path(self, entry):
        root = glob_conf.config['EXP']['root']
        name = glob_conf.config['EXP']['name']
        try:
            entryn = glob_conf.config['EXP'][entry]
        except KeyError:
            # some default values
            if entry == 'fig_dir':
                entryn = './images/'
            elif entry == 'res_dir':
                entryn = './results/'
            elif entry == 'model_dir':
                entryn = './models/'
            else:
                entryn = './store/'

        # Expand image, model and result directories with run index
        if entry == 'fig_dir' or entry == 'res_dir' or entry == 'model_dir':
            run = self.config_val('EXP', 'run', 0)
            entryn = entryn +  f'run_{run}/'

        dir_name = f'{root}{name}/{entryn}'
        audeer.mkdir(dir_name)
        return dir_name
    

    def config_val_data(self, dataset, key, default):
        data_roots = self.config_val('DATA', 'root_folders', False)
        if data_roots:
            # if there is a global data rootfolder file, read from there
            if not os.path.isfile(data_roots):
                self.error(f'no such file: {data_roots}')
            configuration = configparser.ConfigParser()
            configuration.read(data_roots)
        else:
            configuration = glob_conf.config
        try:
            # strategy is either train_test (default)  or cross_data
            if len(key)>0:
                return configuration['DATA'][dataset+'.'+key]
            else:
                return configuration['DATA'][dataset]
        except KeyError:
            return default


    def get_save_name(self):
        """Return a relative path to a name to save the experiment"""
        store = self.get_path('store')
        return f'{store}/{self.get_exp_name()}.pkl'


    def get_res_dir(self):
        root = glob_conf.config['EXP']['root']
        name = glob_conf.config['EXP']['name']
        dir_name = f'{root}{name}/results/'
        audeer.mkdir(dir_name)
        return dir_name

    def make_segmented_index(self, df):
        if len(df)==0:
            return df
        if not isinstance(df.index, pd.MultiIndex):
            df.index = audformat.utils.to_segmented_index(df.index, allow_nat=False)
        return df

    def get_exp_name(self):
        ds = '_'.join(ast.literal_eval(glob_conf.config['DATA']['databases']))
        mt = glob_conf.config['MODEL']['type']
        ft = glob_conf.config['FEATS']['type']
        set = self.config_val('FEATS', 'set', False)
        if set:
            return f'{ds}_{mt}_{ft}_{set}'
        else:
            return f'{ds}_{mt}_{ft}'

    def get_plot_name(self):
        try:
            plot_name = glob_conf.config['PLOT']['name']
        except KeyError:
            plot_name = self.get_exp_name()
        return plot_name

    def exp_is_classification(self):
        type = self.config_val('EXP', 'type', 'classification')
        if type=='classification':
            return True
        return False

    def error(self, message):
        print(f'ERROR: {message}')
        sys.exit()

    def debug(self, message):
        print(f'DEBUG: {message}')

    def set_config_val(self, section, key, value):
        try:
            # does the section already exists?
            glob_conf.config[section][key] = str(value)
        except KeyError:
            glob_conf.config.add_section(section)
            glob_conf.config[section][key] = str(value)
    
    def check_df(self, i, df):
        """Check a dataframe"""
        print(f'check {i}: {df.shape}')
        print(df.head(1)
        )
    def config_val(self, section, key, default):
        try:
            # strategy is either train_test (default)  or cross_data
            return glob_conf.config[section][key]
        except KeyError:
            return default
            
    def get_labels(self):
        try:
            labels = glob_conf.label_encoder.classes_
        except AttributeError:
            labels = ast.literal_eval(glob_conf.config['DATA']['labels'])
        return labels

    def continuous_to_categorical(self, array):
        bins = ast.literal_eval(glob_conf.config['DATA']['bins'])
        result =  np.digitize(array, bins)-1
        return result

    def print_best_results(self, best_reports):
        res_dir = self.get_res_dir()
        # go one level up above the "run" level
        all = ''
        vals = np.empty(0)
        for report in best_reports:
            all += str(report.result.test) + ', '
            vals = np.append(vals, report.result.test)
        file_name = f'{res_dir}{self.get_exp_name()}_runs.txt'
        with open(file_name, "w") as text_file:
            text_file.write(all)
            text_file.write(f'\nmean: {vals.mean():.3f}, max: {vals.max():.3f}, max_index: {vals.argmax()}')
