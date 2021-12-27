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


def calc_md5(file_path):
    with open(file_path, 'rb') as f:
        md5obj = hashlib.md5()
        md5obj.update(f.read())
        hash = md5obj.hexdigest()
        return hash


def move_to_trash(file_path):
    try:
        send2trash(file_path.replace('/', '\\'))
    except Exception as ex:
        logger.info(ex)


def remove_duplicate_files_by_md5(file_list):

    file_list_df = file_list[1]

    file_list_df['md5'] = file_list_df['file_path'].apply(lambda x: calc_md5(x))
    duplicate_md5_df = file_list_df.groupby('md5').filter(lambda group: len(group) > 1)
    duplicate_md5_count = len(duplicate_md5_df)
    if (duplicate_md5_count == 0):
        # logger.info('no duplicate file (by file md5) exists')
        return 0

    duplicate_md5_group = duplicate_md5_df.groupby('md5')

    for name, group in duplicate_md5_group:

        group.sort_values(by=['create_date', 'modify_date'], ascending=True, inplace=True)
        group['duplicate'] = group.duplicated(["md5"], keep="first")
        removal_files_df = group[group['duplicate'] == True]
        removal_files_df['file_path'].apply(lambda file: move_to_trash(file))

        return len(removal_files_df)

        # logger.info(f'remove {len(removal_files_df)} duplicate files by file md5')


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


class ScanFiles():
    def __init__(self, path):
        self.file_list = []
        self.scan(path)

    def scan(self, dir):
        try:
            for i in os.scandir(dir):
                if i.is_dir() and i.name[0] != '.' and i.name[0] != '$':
                    self.scan(i)
                else:
                    self.file_list.append(i.path)
        except Exception as ex:
            logger.info(ex)


class DuplicateFileRemoval(Thread):
    def __init__(self, path):
        super(DuplicateFileRemoval, self).__init__()
        self.path = path

    def run(self):

        logger.info(f'worker start: {self.path}')

        # collect file list
        df = pd.DataFrame(columns=['file_path', 'file_size', 'create_date', 'modify_date'])

        file_list = ScanFiles(self.path).file_list
        if (len(file_list) == 0):
            raise FileNotFoundError(f'Cannot find files in: {self.path}')

        # parse file list
        if len(file_list) <= 32:
            files_df = collect_file_info(file_list)
        else:
            NUM_USABLE_CPU = max(multiprocessing.cpu_count() - 2, 1)
            workers = min(NUM_USABLE_CPU, len(file_list))

            file_list_temp = np.array_split(file_list, workers)

            with Pool(processes=workers) as p:
                results = list(tqdm(p.imap(lambda x: collect_file_info(x), file_list_temp), total=len(file_list_temp),
                                    ncols=80))
            files_df = pd.concat(results)

        total_files_count = len(files_df)

        logger.info(f'Total Files: {total_files_count}')

        # find duplicate files by file size
        duplicate_file_size_df = files_df.groupby('file_size').filter(lambda group: len(group) > 1)
        duplicate_file_size_count = len(duplicate_file_size_df)
        if (duplicate_file_size_count == 0):
            logger.info('no duplicate file (by file size) exists')
            return

        logger.info(f'Duplicate Files by file size: {duplicate_file_size_count}')

        # remove duplicate files by file md5

        duplicate_file_size_group = duplicate_file_size_df.groupby('file_size')

        removal_duplicate_file_count = 0

        for duplicate_file_size_df in tqdm(duplicate_file_size_group, ncols=80):
            removal_duplicate_file_count += remove_duplicate_files_by_md5(duplicate_file_size_df)

        logger.info(f'Removal Duplicate Files: {removal_duplicate_file_count}')

        # NUM_USABLE_CPU = max(multiprocessing.cpu_count() - 2, 1)
        # workers = min(NUM_USABLE_CPU, len(duplicate_file_size_group))

        # with Pool(processes=workers) as p:
        #     results = list(
        #         tqdm(p.imap(lambda x: remove_duplicate_files_by_md5(x), duplicate_file_size_group),
        #              total=len(duplicate_file_size_group),
        #              ncols=80))

        logger.info(f'worker end')
