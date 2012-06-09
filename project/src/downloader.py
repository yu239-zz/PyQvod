"""
    PyQvod_v0.5: a python wrapper for Qvod downloader + wine 
    Author: yu239
    Date: 06/06/2012

    downloader.py
    The worker thread in charge of downloading and file management
"""
import os
import subprocess
import Queue
import re
import thread
import time

import sys
reload(sys)
sys.setdefaultencoding('utf-8') 

_HOME_ = os.getenv('HOME')
_CONFIG_ = '../config'
_EXE_ = '../bin/qvoddownloader.exe'
_JOB_QUEUE_ = None

def read_config():
    # Check whether the configure file exists
    if not os.path.isfile(_CONFIG_):
        report('CONFIG =' + _CONFIG_ + '\n'+ \
               'Cannot find configure file "config", make sure it under PyQvod.', 0)
        report('Not Started', thread.get_ident())
        return False
    
    fin = open('../config', 'r')
    # Read the configuration lines, excluding comments and striping '\n'
    line_pairs = map(lambda l: l.split(':'), 
                     [l.strip() for l in fin.readlines() if not l.strip().startswith('#') and l.strip() != ''])
    # Convert the list pairs to a dictionary
    conf = dict([(pair[0], pair[1]) for pair in line_pairs])
    # Check the value for each item
    entries = ['VIDEO_PATH', 'CACHE_PATH', 'TIMEOUT']
    for key in conf:
        if not key in entries:
            report('Some entry in the configuration file has been changed!\n' + \
                   'ENTRY =' + key + '\n' + \
                   'The correct enties should be:\n' + str(entries), 0)
            report('Not Started', thread.get_ident())
            return False

        if 'PATH' in key:
            conf[key] = conf[key].replace('~', _HOME_)
            if not os.path.isdir(conf[key]):
                ret = os.system('mkdir ' + conf[key] + ' 2> /dev/null')
                if ret != 0:
                    report(conf[key] + '\n' + \
                           'Directory does not exist and cannot create.\n' + \
                           'Please check the permission and path!', 0)
                    report('Not Started', thread.get_ident())
                    return False
            
            # Get some disk usage information to the user
            if key == 'VIDEO_PATH':
                p = os.popen('ls ' + conf[key] + ' | wc -l')
                video_number = p.readline().strip()
                p.close()
                p = os.popen('ls -l ' + conf[key])
                video_disk_used = int(re.search('[0-9]+', p.readline()).group()) / 1024
                p.close()
            else:
                p = os.popen('ls -l ' + conf[key])
                cache_disk_used = int(re.search('[0-9]+', p.readline()).group()) / 1024
                p.close()
            
        if 'TIMEOUT' in key:
            if re.match('[0-9]+$', conf[key]) == None:
                report('TIMEOUT =' + conf[key] + '\n' + \
                       'The format of TIMEOUT is error! Should be an integer.', 0)
                report('Not Started', thread.get_ident())
                return False

    # Check whether the download exe is in the right position
    if not os.path.isfile(_EXE_):
        report('EXE =' + _EXE_ + '\n' + \
               'Cannot find downloader executable in "bin".', 0)
        report('Not Started', thread.get_ident())
        return False

    # Check whether the user has 'wine'
    ret = os.system('which wine 1> /dev/null 2> /dev/null')
    if ret != 0: 
        report('Sorry, you have to install wine first ..\n' + \
               'In Unbuntu, you can just type in terminal:\n' + \
               'sudo apt-get install wine\n' + \
               'For further information, see \n' + \
               'http://www.winehq.org/download/', 0)
        report('Not Started', thread.get_ident())
        return False
    else:
        p = os.popen('wine --version')
        wine_ver = p.readline().strip().split('-')[1]
        p.close()
        
    # Report some user information
    if re.match('[0-9]+\.[0-9]+.*', wine_ver) is None:
        wine_ver = 'unknown'
    report('*Wine version on your system: ' + wine_ver + '*\n' + \
           '*Downloaded: ' + video_number + \
           ' videos with ' + str(video_disk_used) + 'MB in total, ' + \
           'cache file size: ' + str(cache_disk_used) + 'MB*', 0)
    return conf

def valid_url(qvod_url):
    # A valid qvod url should have 3 trunks seperated by '|'
    qvod_valid_trunk_n = 3
    # Match the pattern: start with 'qvod://' and end with '|'
    # Before the last '|', a suffix should be a video type
    res = re.match('qvod://.+\|.*\.(avi|wmv|flv|mkv|mov|mp4|mpg|vob|rm|rmvb)\|$',  
                   qvod_url, 
                   re.IGNORECASE) 
    # Remove the empty runk between two '|' 
    trunks = [tr for tr in qvod_url.split('|') if not tr == '']
    
    if  res != None and len(trunks) == qvod_valid_trunk_n:
        return trunks
    return False

def report(string, code):
    """ code: ==0  error         --> report error
              !=0  thread id     --> Update progress
        """
    if _JOB_QUEUE_:
        _JOB_QUEUE_.put(str(code) + '$' + string)
    elif code == 0:
        print >> sys.stderr, string
    else:
        print string
        
def download(qvod_url, kill_queue = None, frename = ''):
    # Check whether the url is a valid QVOD url
    trunks = valid_url(qvod_url)
    if not trunks:
        report(qvod_url + '\n' + \
               'Qvod URL invalid!\n' + \
               'A sample url:\n' + \
               'qvod://193329377|F0B62C5BF0B62C5BF0B62C5BF0B62C5BF0B62C5B|soudy.org.rmvb|', 0)
        report('Not Started', thread.get_ident())
        return False
    # If valid, read the configure file
    conf = read_config()
    if not conf: return False

    movie_length, hash_code, movie = trunks
    movie_length = int(re.search('[0-9]+$', movie_length).group())
    video_path, cache_path, timeout = [conf['VIDEO_PATH'], conf['CACHE_PATH'], conf['TIMEOUT']]
    suffix = re.search('avi|wmv|flv|mkv|mov|mp4|mpg|vob|rmvb|rm', movie, re.IGNORECASE).group()
    # Initialize the cache directory
    if frename == '': 
        frename = movie.replace('.' + suffix, '')
    else: 
        frename = frename.replace('.' + suffix, '')
    
    frename = frename.decode('utf-8')
    cache_dir = cache_path + '/' + frename
    
    if not os.path.isdir(cache_dir):
        ret = os.system('mkdir ' + cache_dir + ' 2> /dev/null')
        if ret != 0:
            report(cache_dir + \
                   'Permission denied for this cache directory.\n' + \
                   'Make sure you have the right permission.', 0)
            report('Not Started', thread.get_ident())
            return False
        
    # Copy the downloader to the cache dir and rename it
    exe = hash_code + '+' + movie + '_' + hash_code + '.exe'
    os.system('cp ' + _EXE_ + ' ' + cache_dir + '/' + exe)
    # Start downloading!
    #print 'Start downloading ...'
    p_downloader = subprocess.Popen(['wine', cache_dir + '/' + exe], 
                                      stdout=subprocess.PIPE, 
                                      stderr=subprocess.PIPE)

    # Update the downloading progress
    cache = hash_code + '+' + movie + '.!qd'
    complete = cache.replace('.!qd', '')
    b_succeed = False
    last_length = 0
    start_time = time.time()
    last_update = start_time 
    timeout = int(timeout)
    while True:       
        # Check whether the kill_queue has a kill command
        if kill_queue and not kill_queue.empty():
            p_downloader.terminate()
            os.system('rm -rf ' + cache_dir)
            return True

        # Check whether the connection is timeout
        cur_time = time.time()
        passed_time = cur_time - start_time
        if cur_time - last_update >= timeout:
            p_downloader.terminate()
            b_succeed = False
            break

        # Not started yet
        if not os.path.isfile(cache_dir + '/' + cache) and not os.path.isfile(cache_dir + '/' + complete):
            progress = 0.00
            speed = 0.00
        else:
            # Check whether the download has completed
            # The .!qd file should be replaced by the actual video file now
            if os.path.isfile(cache_dir + '/' + complete):
                p_downloader.terminate()
                if os.system('mv ' + cache_dir + '/' + complete + ' ' + video_path + '/' + frename + '.' + suffix) == 0:
                    os.system('rm -rf ' + cache_dir)
                else:
                    report('Cannot move the cache file to video path you specified.\n' + \
                           'Please check the path and permission!.', 0)
                b_succeed = True
                break
            
            # Read the current length of t >he cache file
            p = os.popen('du ' + cache_dir + '/' + cache)
            cur_length = int(p.readline().strip().split('\t')[0]) * 1024  # in Bytes
            p.close()
            speed = int((cur_length - last_length) / (cur_time - last_update) / 1024) # in KB
            if cur_length > last_length: last_update = cur_time
            last_length = cur_length
            progress = round(float(cur_length) / movie_length * 100, 2)
                    
        status = str(progress) + '%' + ' ' + str(speed) + 'KB/s' + ' ' + str(int(passed_time/60)) + 'mins passed'
        if _JOB_QUEUE_ is None:
            sys.stdout.write("\r%s%%" % status)
            sys.stdout.flush()
        else:
            report(status, thread.get_ident())
        time.sleep(1)    
            
    if _JOB_QUEUE_ is None: sys.stdout.write("\r  \r\n")
    
    if b_succeed:
        report('Completed!' + ' Total time: ' + str(int((time.time() - start_time)/60)) + 'mins',
               thread.get_ident())
        return True
    else:
        report('Timeout! Download failed', thread.get_ident())           
        return False





    
    
