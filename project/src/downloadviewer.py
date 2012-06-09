"""
    PyQvod_v0.5: a python wrapper for Qvod downloader + wine 
    Author: yu239
    Date: 06/06/2012

    downloadviewer.py
    A download progress viewer, similar with firefox download manager
"""
import sys
import wx

class DownloadViewer(wx.ListCtrl):
    """
    A List Ctrl with gauages
    """
    def __init__(self, parent, pos=wx.DefaultPosition, size=wx.DefaultSize, 
                 style=wx.LC_REPORT|wx.LC_VRULES|wx.CLIP_CHILDREN, splits=[0.5,0.15,0.35]):       
        wx.ListCtrl.__init__(self, parent, wx.ID_ANY, pos=pos, size=size, style=style)
        self.parent = parent
        
        self.width, self.height = size
        filewidth, progwidth, detailwidth = splits
        # Progress bars
        self.progresses = []
        self.progressBars = []
        self.clearBars = False
        
        # Columns
        self.InsertColumn(0, 'Filename')
        self.InsertColumn(1, 'Progress')
        self.InsertColumn(2, 'Details')
        
        self.SetColumnWidth(0, int(filewidth*self.width))
        self.SetColumnWidth(1, int(progwidth*self.width))
        self.SetColumnWidth(2, int(detailwidth*self.width))
        
        # Events
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind (wx.EVT_LIST_COL_DRAGGING, self.OnPaint)
        self.Bind(wx.EVT_LIST_COL_END_DRAG, self.OnPaint)
        self.Bind(wx.EVT_SCROLL, self.OnPaint)

    def _GetAllSelectedItems(self):
        cnt = self.GetSelectedItemCount()
        idx = -1
        lst = []
        for i in range(cnt):
            idx = self.GetNextSelected(idx)
            if idx == -1: break
            lst.append(idx + i)
            idx = -1
        return lst
    #Interfaces to parent panel
    # Add a new download task 
    def _AddItem(self, filename):
        idx = self.InsertStringItem(sys.maxint, filename)
        self.progresses.append(0)
        self.SetStringItem(idx, 2, 'Not Started')
        self.OnPaint()
    
    # Delete all the selected tasks
    def _DeleteItem(self):
        lst = self._GetAllSelectedItems()
        idx = -1
        for i in range(len(lst)):
            idx = self.GetNextSelected(idx)
            if idx == -1: break
            self.DeleteItem(idx)  # Be careful! Each time a delete will change the index!
            self.progresses.pop(idx)
            idx = -1
            
        assert len(self.progresses) == self.GetItemCount()
        self.OnPaint()
        return lst  # Return the delete list to parent

    # Delete all items
    def _DeleteAllItems(self):
        for idx in range(self.GetItemCount()):
            self.SetItemState(idx, wx.LIST_STATE_SELECTED, wx.LIST_STATE_SELECTED)
        return self._DeleteItem()
        
    # Update the progress of task idx
    def _UpdateItemProgress(self, idx, progress, details):
        if progress != -1:
            self.progresses[idx] = int(progress)
        self.SetStringItem(idx, 2, details)
        self.OnPaint()
    
    # Paint methods on gaugectrl
    def OnPaint(self, event=None):
        """
        Handles the EVT_PAINT event
        """
        self._OnPaintBars()
        if event:
            event.Skip()
            
    def _OnPaintBars(self):
        """
        Actual drawing of progress bars
        """
        # General list info
        rank = 1                            # the column with the gauges
        itemCount = self.GetItemCount()     # number of items
        
            # No progress column or no items
        if rank == -1 or not itemCount:
            [p.Destroy() for p in self.progressBars]
            del self.progressBars [:]
            return False
        
        if self.clearBars:
            self.clearBars = False
            [p.Destroy() for p in self.progressBars]
            del self.progressBars[:]
            
            # Indexes
        topItem = self.GetTopItem() # top
        visibleIndexes = range(topItem, topItem + min(self.GetCountPerPage()+1, itemCount)) # to show
            
            # Make sure no extra bars
        while len(self.progressBars) > itemCount:
            progressBar = self.progressBars.pop()
            progressBar.Destroy()

            # Make sure enough bars
        while len(self.progressBars) < itemCount:
            progressBar = self._getProgressBar()
            self.progressBars.append(progressBar)

            # Update bars positions, size and value
        rect = self.GetItemRect(topItem)
        size = (self.GetColumnWidth(rank)-4, rect[3]-4)
        x = rect[0] + sum([self.GetColumnWidth(i) for i in range(0, rank)]) + 2
        y = rect[1] + 2
        inc = rect[3]
        
        for row in range(itemCount):
            if row in visibleIndexes:
                bar = self.progressBars[row]
                if bar.GetPosition () != (x, y):
                    if wx.Platform != "__WXMSW__":
                        bar.Hide()
                    bar.SetPosition((x, y))
                bar.SetSize(size)
                bar.SetValue(self.progresses[row])
                bar.Show()
                y += inc
            else:
                self.progressBars[row].Hide()

        return True
        
    def _getProgressBar(self):
        return wx.Gauge(self, -1, style = wx.NO_BORDER)

        
    
