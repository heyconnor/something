#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import time
import csv
import numpy
import matplotlib.pyplot as plt
from matplotlib.ticker import FormatStrFormatter
from bitcoinrpc.authproxy import AuthServiceProxy

mainnet = {
    'rpc_user': 'bitcoinrpc',
    'rpc_password': '123456',
    'rpc_host': '127.0.0.1',
    'rpc_port': 7116
}

testnet = {
    'rpc_user': 'bitcoinrpc',
    'rpc_password': '123456',
    'rpc_host': '192.168.30.106',
    'rpc_port': 17116
}

bitcoinrpc = None
file_name = 'blocks.csv'


def set_net_type(network):
    global bitcoinrpc
    if network == 'mainnet':
        net = mainnet
    elif network == 'testnet':
        net = testnet
    else:
        return
    bitcoinrpc = AuthServiceProxy("http://%s:%s@%s:%s" % (net['rpc_user'], net['rpc_password'], net['rpc_host'], net['rpc_port']))


def time_stamp_to_string(seconds):
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(seconds))


def get_block(height):
    block_hash = bitcoinrpc.getblockhash(height)
    return bitcoinrpc.getblock(block_hash)


def get_lastest_blocks(count):
    chain_info = bitcoinrpc.getblockchaininfo()
    block_height = chain_info['blocks']
    step = 1
    block_list = []
    for height in range(block_height - count * step, block_height + 1, step):
        block_list.append(get_block(height))
        print('block %s got' % height)
        time.sleep(0.2)
    return block_list


def write_blocks_to_csv(block_list):
    with open(file_name, 'w', newline='') as csv_file:
        file_header = ['height', 'difficulty', 'time', 'mediantime']
        writer = csv.writer(csv_file)
        writer.writerow(file_header)
        for block in block_list:
            writer.writerow([block['height'], block['difficulty'], block['time'], block['mediantime']])


def read_blocks_from_csv():
    block_list = []
    with open(file_name, 'r') as csv_file:
        reader = csv.reader(csv_file)
        next(reader)
        for row in reader:
            block = {
                'height': int(row[0]),
                'difficulty': float(row[1]),
                'time': int(row[2]),
                'mediantime': int(row[3])
            }
            block_list.append(block)
    return block_list


def draw_solve_time_diagram(block_list):
    height_list = []
    solve_time_list = []
    for i in range(1, len(block_list)):
        height_list.append(block_list[i]['height'])
        solve_time_list.append((block_list[i]['time'] - block_list[i-1]['time'])/60)

    plt.subplot(211)
    plt.plot(height_list, solve_time_list, marker='o', label='solve time diagram')
    plt.xlabel('height')
    plt.ylabel('solve time/minutes')
    ax = plt.gca()
    ax.xaxis.set_major_formatter(FormatStrFormatter('%.0f'))

    x = []
    y = []
    solve_time_array = numpy.array(solve_time_list)
    for i in range(3):
        count = ((i*5 <= solve_time_array) & (solve_time_array < (i+1)*5)).sum()
        if count == 0:
            continue
        x.append(i*5)
        y.append(count)
    count = ((i+1) * 5 <= solve_time_array).sum()
    if count != 0:
        x.append((i+1)*5)
        y.append(count)

    plt.subplot(212)
    plt.bar([i + 2.5 for i in x], y, width=2.5)
    plt.xlabel('solve time')
    plt.ylabel('blocks')
    ax = plt.gca()
    ax.xaxis.set_major_formatter(FormatStrFormatter('%.1f'))

    plt.subplots_adjust(wspace=0, hspace=0.4)
    plt.show()


def draw_difficulty_diagram(block_list):
    height_list = []
    difficulty_list = []
    for i in range(1, len(block_list)):
        height_list.append(block_list[i]['height'])
        difficulty_list.append(block_list[i]['difficulty'])
    plt.plot(height_list, difficulty_list, marker='o', label='difficulty changes')
    plt.xlabel('height')
    plt.ylabel('difficulty')
    ax = plt.gca()
    ax.xaxis.set_major_formatter(FormatStrFormatter('%.0f'))
    plt.show()


def draw_solve_time_pie(block_list):
    solve_time_list = []
    for i in range(1, len(block_list)):
        solve_time_list.append((block_list[i]['time'] - block_list[i-1]['time'])/60)

    x = []
    labels = []
    solve_time_array = numpy.array(solve_time_list)
    for i in range(3):
        count = ((i*5 <= solve_time_array) & (solve_time_array < (i+1)*5)).sum()
        if count == 0:
            continue
        x.append(count)
        labels.append('%s~%s minutes' % (i * 5, (i + 1) * 5))
    count = ((i+1) * 5 <= solve_time_array).sum()
    if count != 0:
        x.append(count)
        labels.append('>%s minutes' % ((i + 1) * 5))

    plt.pie(x, labels=labels, autopct='%3.1f %%')
    plt.show()


def average_solve_time(block_list):
    solve_time_list = []
    for i in range(1, len(block_list)):
        solve_time_list.append((block_list[i]['time'] - block_list[i-1]['time'])/60)
    solve_time_array = numpy.array(solve_time_list)
    print(solve_time_array.mean())


def get_difficulty(target):
    n_shift = (target >> 24) & 0xff
    d_diff = 0x0000ffff / (target & 0x00ffffff)

    while n_shift < 29:
        d_diff *= 256.0
        n_shift = n_shift + 1
    while n_shift > 29:
        d_diff /= 256.0
        n_shift = n_shift - 1

    return d_diff


def draw_difficulty_cruve():
    x = [1090177, 1090321, 1090393, 1090465, 1090537, 1090609, 1090681, 1090753, 1090825]
    y1 = [486604799, 486604799, 486595646, 486592511, 486592446, 486586626, 486604799, 486598932, 486604799]
    y2 = [486604799, 486599772, 486596543, 486589027, 486595014, 486575028, 486583155, 486597636, 486603916]
    plt.plot(x, [get_difficulty(i) for i in y1], marker='o', label='legacy difficulty')
    plt.plot(x, [get_difficulty(i) for i in y2], marker='o', label='lwma difficulty')
    plt.xlabel('height')
    plt.ylabel('difficulty')
    plt.legend()
    ax = plt.gca()
    ax.xaxis.set_major_formatter(FormatStrFormatter('%.0f'))
    plt.show()


def draw_norm_curve(block_list):
    solve_time_list = []
    for i in range(1, len(block_list)):
        solve_time_list.append((block_list[i]['time'] - block_list[i-1]['time'])/60)
    plt.hist(solve_time_list, bins=50, density=True)
    plt.show()


set_net_type('testnet')
write_blocks_to_csv(get_lastest_blocks(100))
# draw_norm_curve(read_blocks_from_csv())
# draw_difficulty_cruve()
