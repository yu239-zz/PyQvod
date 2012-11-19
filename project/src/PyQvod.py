# -*- coding: utf-8 -*-
""" 
    PyQvod_v0.5: a python wrapper for Qvod downloader + wine 
    Author: yu239
    Date: 06/06/2012

    PyQvod.py
    The mainframe GUI for user interatcion
"""

import os
import wx
import re
import thread
import Queue
import time
import downloader
import downloadviewer
import listenURL

# Generate a bunch of button ids
_ID_BTN_ADD_ = wx.NewId()
_ID_BTN_DELETE_ = wx.NewId()
_ID_BTN_START_ = wx.NewId()
_ID_BTN_EXIT_ = wx.NewId()
_ID_BTN_PLAY_ = wx.NewId()
_ID_BTN_CONFIG_ = wx.NewId()
_ID_BTN_VIDEO_ = wx.NewId()
_ID_BTN_LICENSE_ = wx.NewId()
_ID_BTN_PAUSE_ = wx.NewId()
_ID_BTN_DELETEALL_ = wx.NewId()

_LICENSE_ = 'This software is under MIT license,\n' + \
            'essentially a "do whatever you want with this software,\n' + \
            'just don\'t blame me if something goes wrong" license.\n' + \
            'http://en.wikipedia.org/wiki/MIT_License'
 
class FileNameDialog(wx.Dialog):
    def __init__(self, parent, title, string):
        self.width, self.height = (350, 120)
        wx.Dialog.__init__(self, parent=parent, title=title, size=(self.width, self.height))
        self.string = string

        panel = wx.Panel(self)        
        delta = 10
        bn_width, bn_height = 80, 25

        rt_label = wx.Rect(delta, delta, self.width-2*delta, 20)
        st_label = wx.StaticText(panel, pos=rt_label.GetPosition(), size=rt_label.GetSize(), 
                                 label='Change filename to:')
        
        rt_filename = wx.Rect(delta, rt_label.GetBottom()+delta, rt_label.GetWidth(), 25)
        self.tc_filename = wx.TextCtrl(panel, pos=rt_filename.GetPosition(), 
                                       size=rt_filename.GetSize())
        self.tc_filename.WriteText(self.string)

        rt_ok = wx.Rect(delta, rt_filename.GetBottom()+2*delta, bn_width, bn_height)
        bn_ok = wx.Button(panel, pos=rt_ok.GetPosition(), size=rt_ok.GetSize(), id=wx.ID_OK)
        rt_cancel = wx.Rect(rt_ok.GetRight()+delta/2, rt_ok.GetTop(), bn_width, bn_height)
        bn_cancel = wx.Button(panel, pos=rt_cancel.GetPosition(), size=rt_cancel.GetSize(), id=wx.ID_CANCEL)
        bn_ok.Bind(wx.EVT_BUTTON, self.OnClose)
        bn_cancel.Bind(wx.EVT_BUTTON, self.OnClose)
        bn_ok.SetFocus()
        
    def OnClose(self, e):
        if e.GetId() == wx.ID_OK:
            tmp_str = self.tc_filename.GetValue()
            if tmp_str.strip() != '': self.string = tmp_str
        self.Destroy()

class MainFrame(wx.Frame):
    def __init__(self, title):
        self.width, self.height = (600, 330) # fixed size, nonresizable
        wx.Frame.__init__(self, None, title=title, size=(self.width, self.height),
                          style=wx.DEFAULT_FRAME_STYLE^wx.RESIZE_BORDER)
        self._InitUI()
        self._Init()
        self.Center()
        self.Show()

    # Initialize
    def _Init(self):
        # All the jobs information added into the list, each element a turple (thread_id, url, queue)
        # thread_id is the thread that manages the job. If the job hasn't started, it's -1
        # url is the Qvod URL with respect to the job
        # queue is used to kill a downloader thread
        self.jobs_info = []
        # Start a thread to listen the javascript qvodurlfinder
        self.url_queue = Queue.Queue(0)
        listenURL._URL_QUEUE_ = self.url_queue
        thread.start_new_thread(listenURL.listenURL, ())
        # Set a timer for checking url queue
        self.url_timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.OnCheckURLQueue, self.url_timer)
        self.url_timer.Start(100)  # Check every 100 ms
        # Set a timer for updating job progress
        self.job_queue = Queue.Queue(0)
        downloader._JOB_QUEUE_ = self.job_queue
        self.job_timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.OnCheckJobQueue, self.job_timer)
        self.job_timer.Start(100)
        # Read the configure file and do a check
        self.conf = downloader.read_config()
        if not self.conf:
            self._Alert('Configure file invalid!')
        
    # Initialize UI
    def _InitUI(self):
        # Put a panel ontop of mainframe first
        panel = wx.Panel(self)
        delta = 10
        bn_width, bn_height = 80, 25
        dv_height = self.height - 130
        # Create a noneditable text control to display Qvod URL
        rt_url = wx.Rect(delta, delta, self.width-2*delta, 20)
        self.tc_url = wx.TextCtrl(panel, pos=rt_url.GetPosition(), size=rt_url.GetSize(), 
                             style=wx.BORDER_NONE|wx.TE_DONTWRAP)
        self.tc_url.WriteText('qvod://108941476|E756EFBB467FFD37A36225B180CF29F1BE8BEAB0|[www.qvod123.com]名侦探柯南_662.rmvb|')
        
        # Add a download manager
        rt_dv = wx.Rect(delta, rt_url.GetBottom()+2*delta, rt_url.GetWidth(), dv_height)
        self.lc_dv = downloadviewer.DownloadViewer(panel, pos=rt_dv.GetPosition(), size=rt_dv.GetSize())
        
        # Add a 'add' button
        rt_add = wx.Rect(delta/2, rt_dv.GetBottom()+2*delta, bn_width, bn_height)
        self.bn_add = wx.Button(panel, pos=rt_add.GetPosition(), size=rt_add.GetSize(), 
                                id=_ID_BTN_ADD_, label='Add url')
        self.bn_add.Bind(wx.EVT_BUTTON, self.OnAddTask)
        rt_prev = rt_add
        
        # Add a 'start' button
        rt_start = wx.Rect(rt_prev.GetRight()+delta/2, rt_prev.GetTop(), bn_width-delta, bn_height)
        self.bn_start = wx.Button(panel, pos=rt_start.GetPosition(), size=rt_start.GetSize(), 
                                id=_ID_BTN_START_, label='Start')
        self.bn_start.Bind(wx.EVT_BUTTON, self.OnStart)
        rt_prev = rt_start
        # Add a 'pause' button
        rt_pause = wx.Rect(rt_prev.GetRight()+delta/2, rt_prev.GetTop(), bn_width-delta, bn_height)
        self.bn_pause = wx.Button(panel, pos=rt_pause.GetPosition(), size=rt_pause.GetSize(), 
                                id=_ID_BTN_PAUSE_, label='Pause')
        self.bn_pause.Bind(wx.EVT_BUTTON, self.OnPause)
        rt_prev = rt_pause
        # Add a 'delete' button
        rt_del = wx.Rect(rt_prev.GetRight()+delta/2, rt_prev.GetTop(), bn_width, bn_height)
        self.bn_del = wx.Button(panel, pos=rt_del.GetPosition(), size=rt_del.GetSize(), 
                                id=_ID_BTN_DELETE_, label='Delete')
        self.bn_del.Bind(wx.EVT_BUTTON, self.OnDeleteTasks)
        rt_prev = rt_del

        # Add a 'deleteall' button
        rt_delall = wx.Rect(rt_prev.GetRight()+delta/2, rt_prev.GetTop(), bn_width+delta, bn_height)
        self.bn_delall = wx.Button(panel, pos=rt_delall.GetPosition(), size=rt_delall.GetSize(), 
                                id=_ID_BTN_DELETEALL_, label='Delete All')
        self.bn_delall.Bind(wx.EVT_BUTTON, self.OnDeleteTasks)
        rt_prev = rt_delall
        # Add a 'video' button
        rt_video = wx.Rect(rt_prev.GetRight()+delta/2, rt_prev.GetTop(), bn_width, bn_height)
        self.bn_video = wx.Button(panel, pos=rt_video.GetPosition(), size=rt_video.GetSize(), 
                                id=_ID_BTN_VIDEO_, label='Videos')
        self.bn_video.Bind(wx.EVT_BUTTON, self.OnOpenVideos)
        rt_prev = rt_video
        # Add a 'configure' button
        rt_conf = wx.Rect(rt_prev.GetRight()+delta/2, rt_prev.GetTop(), bn_width+delta, bn_height)
        self.bn_conf = wx.Button(panel, pos=rt_conf.GetPosition(), size=rt_conf.GetSize(), 
                                id=_ID_BTN_CONFIG_, label='Congifure')
        self.bn_conf.Bind(wx.EVT_BUTTON, self.OnConfigure)
        rt_prev = rt_conf

        # Add a 'license' button
        rt_license = wx.Rect(rt_add.GetLeft(), rt_prev.GetBottom()+delta/2, bn_width, bn_height)
        self.bn_license = wx.Button(panel, pos=rt_license.GetPosition(), size=rt_license.GetSize(), 
                                    id=_ID_BTN_LICENSE_, label='License')
        self.bn_license.Bind(wx.EVT_BUTTON, self.OnShowLicense)
        rt_prev = rt_license

        # Add a 'Play' button
        rt_play = wx.Rect(rt_video.GetLeft(), rt_prev.GetTop(), bn_width, bn_height)
        self.bn_play = wx.Button(panel, pos=rt_play.GetPosition(), size=rt_play.GetSize(), 
                                id=_ID_BTN_PLAY_, label='Play')
        self.bn_play.Bind(wx.EVT_BUTTON, self.OnPlay)
        rt_prev = rt_play

        # Add a 'exit' button
        rt_exit = wx.Rect(rt_video.GetRight()+delta/2, rt_prev.GetTop(), bn_width+delta, bn_height)
        self.bn_exit = wx.Button(panel, pos=rt_exit.GetPosition(), size=rt_exit.GetSize(), 
                                id=_ID_BTN_EXIT_, label='Exit')
        self.bn_exit.Bind(wx.EVT_BUTTON, self.OnExit)
        rt_prev = rt_exit
        # Add an 'info' static text
        rt_info = wx.Rect(rt_license.GetRight()+delta, rt_license.GetTop(), 
                          rt_exit.GetLeft()-rt_license.GetRight()-2*delta, bn_height+delta)
        self.st_info = wx.StaticText(panel, pos=rt_info.GetPosition(), size=rt_info.GetSize(), 
                                     label='')
        self.st_info.SetFont(wx.Font(8, wx.DEFAULT, wx.DEFAULT, wx.DEFAULT))

    def _Alert(self, msg):
        wx.MessageBox(msg, 'error', wx.OK | wx.ICON_ERROR)

    def _AddUrl(self, url):
        self.tc_url.Clear()
        self.tc_url.WriteText(url)

    def OnAddTask(self, e):
        url = self.tc_url.GetValue()
        trunks = downloader.valid_url(url)
        if not trunks:
            self._Alert('Invalid URL!')
        elif url in [t[1] for t in self.jobs_info]:
            self._Alert('You have already added an identical URL!')
        else:
            self.filename = trunks[2]
            dlg_filename = FileNameDialog(None, 'Video name', self.filename)
            dlg_filename.ShowModal()
            self.filename = dlg_filename.string
            dlg_filename.Destroy()
            self.jobs_info.append((-1, url, Queue.Queue(0)))  # Create a new queue for this thread
            self.lc_dv._AddItem(self.filename) # Add a task with the video name
        
    def OnDeleteTasks(self, e):
        if e.GetId() == _ID_BTN_DELETEALL_:
            del_lst = self.lc_dv._DeleteAllItems()
        else:
            del_lst = self.lc_dv._DeleteItem()
        
        # Send a kill signal to worker thread
        for idx in del_lst:
            self.jobs_info[idx][2].put(0)
        self.jobs_info = [t for i, t in enumerate(self.jobs_info) if not i in del_lst]
    
    def OnConfigure(self, e):
        os.system('xdg-open ../config 1> /dev/null 2> /dev/null')

    def OnStart(self, e):
        lst = self.lc_dv._GetAllSelectedItems()
        for idx in lst:
            job_id, url, que = self.jobs_info[idx]
            if job_id != -1: continue   # If this job has been started, skip it
            job_id = thread.start_new_thread(downloader.download, (url, que, self.filename, ))
            self.jobs_info[idx] = (job_id, url, que)

    def OnPause(self, e):
        lst = self.lc_dv._GetAllSelectedItems()
        for idx in lst:
            self.jobs_info[idx][2].put(-1) 
            self.jobs_info[idx] = (-1, self.jobs_info[idx][1], Queue.Queue(0)) # A queue can be used for only once
            self.lc_dv._UpdateItemProgress(idx, -1, 'Paused')
            
    def OnPlay(self, e):
        lst = self.lc_dv._GetAllSelectedItems()
        for idx in lst:
            self.jobs_info[idx][2].put(-2) 

    def OnExit(self, e):
        self.Close()

    def OnOpenVideos(self, e):
        ret = os.system('xdg-open ' + self.conf['VIDEO_PATH'] + ' 1> /dev/null 2> /dev/null')
        if ret != 0:
            self._Alert('Make sure you have configured a valid video path!')

    def OnCheckURLQueue(self, e):
        if not self.url_queue.empty():
            url = self.url_queue.get()
            self._AddUrl(url)
            
    def OnCheckJobQueue(self, e):
        if not self.job_queue.empty():
            msg = self.job_queue.get()
            code, string = msg.split('$')
            if int(code) == 0:
                if string.startswith('*'):
                    self.st_info.SetLabel(string)
                else:
                    self._Alert(string)
            else:
                res = re.search('([0-9]*.[0-9]*)%', string)
                if not res is None:
                    progress = int(float(res.group(1)))
                else: 
                    progress = -1  # Detail doesn't contain progress, just set it to -1
                
                job_ids = [t[0] for t in self.jobs_info]
                assert int(code) in job_ids
                idx = job_ids.index(int(code))
                if res is None: 
                    # Enable this task again
                    self.jobs_info[idx] = (-1, self.jobs_info[idx][1], Queue.Queue(0))
                self.lc_dv._UpdateItemProgress(idx, progress, string)
    
    def OnShowLicense(self, e):
        wx.MessageBox(_LICENSE_, 'LICENSE', wx.OK | wx.ICON_INFORMATION)

if __name__ == '__main__':
    # Create a new app, and start the main loop
    app = wx.App(False)  
    MainFrame("PyQvod_v0.5\t\t\t Qvod for linux!")
    app.MainLoop()
