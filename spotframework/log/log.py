
import os
import datetime
import spotframework.net.const as const

logentries = []


def log(entry, *args):

    timestamp = datetime.datetime.now()

    output = str(timestamp) + ' ' + entry + ' ' + ' '.join([str(i) for i in args])

    logentries.append(output)

    print(output)


def dump_log():

    if not os.path.exists(os.path.join(const.config_path, 'log')):
        os.makedirs(os.path.join(const.config_path, 'log'))

    with open(os.path.join(const.config_path, 'log', '{}_log'.format(datetime.datetime.now().strftime('%m_%y'))), 'a+') as file_obj:
        for entry in logentries:

            file_obj.write(entry + '\n')
