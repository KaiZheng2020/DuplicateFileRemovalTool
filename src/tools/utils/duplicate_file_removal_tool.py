import hashlib
import multiprocessing
import os
from glob import glob
from threading import Thread

import numpy as np
import pandas as pd
from loguru import logger
from multiprocess import Pool
from send2trash import send2trash
from tqdm import tqdm


def calc_md5(path):
    with open(path, 'rb') as f:
        md5obj = hashlib.md5()
        md5obj.update(f.read())
        hash = md5obj.hexdigest()
        return hash


def collect_file_info(file_list):
    df = pd.DataFrame(columns=['file_path', 'file_size', 'create_date', 'modify_date'])

    for file_path in file_list:

        file_size = os.path.getsize(file_path)

        if os.path.isdir(file_path) or file_size == 0:
            continue

        create_date = os.path.getctime(file_path)
        modify_date = os.path.getmtime(file_path)

        df = df.append({
            'file_path': file_path,
            'file_size': file_size,
            'create_date': create_date,
            'modify_date': modify_date
        },
                       ignore_index=True)

    return df


class DuplicateFileRemoval(Thread):
    def __init__(self, path, trash_flag):
        super(DuplicateFileRemoval, self).__init__()
        self.path = path
        self.trash_flag = trash_flag

    def run(self):

        logger.info(f'worker start: {self.path}')

        # collect file list
        df = pd.DataFrame(columns=['file_path', 'file_size', 'create_date', 'modify_date'])
        file_list = glob(self.path + '/**', recursive=True)
        if (len(file_list) == 0):
            raise FileNotFoundError(f'Cannot find files in: {self.path}')

        logger.info(f'1. Total Files: {len(file_list)}')

        # parse file list
        if len(file_list) <= 32:
            workers = 1
        else:
            NUM_USABLE_CPU = max(multiprocessing.cpu_count() - 2, 1)
            workers = min(NUM_USABLE_CPU, len(file_list))

        file_list_temp = np.array_split(file_list, workers)

        with Pool(processes=workers) as p:
            results = list(tqdm(p.imap(lambda x: collect_file_info(x), file_list_temp), total=len(file_list_temp), ncols=80))

        files_df = pd.concat(results)
        total_files_count = len(files_df)

        logger.info(f'2. Parsed Files: {total_files_count}')

        # find duplicate files by file_size and md5
        temp_df = files_df.groupby('file_size')
        source_file_size_count = len(temp_df)
        if (source_file_size_count == 0 or source_file_size_count == total_files_count):
            logger.info('no duplicate file (by file size) exists')
            return

        logger.info(f'3. Collect Duplicate Files by File Size')

        duplicate_file_size_df = pd.concat(g for _, g in temp_df if len(g) > 1)
        duplicate_file_size_count = len(duplicate_file_size_df)
        duplicate_file_size_df['md5'] = duplicate_file_size_df['file_path'].apply(lambda x: calc_md5(x))
        temp_df = duplicate_file_size_df.groupby('md5')
        source_md5_count = len(temp_df)
        if (source_md5_count == 0 or source_md5_count == duplicate_file_size_count):
            logger.info('no duplicate file (by file md5) exists')
            return

        logger.info(f'4. Collect Duplicate Files by File MD5')

        duplicate_md5_df = pd.concat(g for _, g in temp_df if len(g) > 1)
        duplicate_md5_df.sort_values(by=['create_date', 'modify_date'], ascending=True, inplace=True)

        duplicate_md5_count = len(duplicate_md5_df)
        duplicate_md5_df['duplicate'] = duplicate_md5_df.duplicated(["md5"], keep="first")

        removal_files_df = duplicate_md5_df[duplicate_md5_df['duplicate'] == True]
        removal_files_count = len(removal_files_df)

        logger.info(f'5. Removed Duplicate Files: {removal_files_count} ')

        if self.trash_flag == True:
            removal_files_df['file_path'].apply(lambda file: send2trash(file.replace('/', '\\')))
        else:
            removal_files_df['file_path'].apply(lambda file: os.remove(file))

        logger.info(f'6. Duplicate Files Removal finished!')
        logger.info(f'worker end')
