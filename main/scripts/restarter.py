#!usr/bin/env python

'''
a small program to restart server services once there\'s fresh data
so users don\'t have to wait for the cache to turn over
'''


import subprocess

to_restart = ['apache2', 'varnish']


def restart(process):
    '''
    given the name of a process, uses subprocess to make the call
    '''
    command = ['/usr/sbin/service', process, 'restart']
    subprocess.call(command)


def call_restart(processes):
    '''
    args:
    an iterable of process-name strings to hand to the caller
    '''
    for p in processes:
        restart(p)


if __name__ == '__main__':
    call_restart(to_restart)
