import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import os

from matplotlib.ticker import (MultipleLocator, FormatStrFormatter, AutoMinorLocator)

data_color = "black"
fit_color  = "xkcd:azure"
sig_color  = "xkcd:coral"
bck_color  = "xkcd:teal"
diff_color = "xkcd:red"

def set_lhcb_style(grid = True, size = 10, usetex = "auto", font = "serif") : 
  """
    Set matplotlib plotting style close to "official" LHCb style
    (serif fonts, tick sizes and location, etc.)
  """
  if usetex == "auto" : 
    plt.rc('text', usetex=os.path.isfile("/usr/bin/latex"))
  else : 
    plt.rc('text', usetex=usetex)
  plt.rc('font', family=font, size=size)
  plt.rcParams['axes.linewidth']=1.3
  plt.rcParams['axes.grid']=grid
  plt.rcParams['grid.alpha']=0.3
  plt.rcParams["axes.axisbelow"] = False
  plt.rcParams['xtick.major.width']=1
  plt.rcParams['ytick.major.width']=1
  plt.rcParams['xtick.minor.width']=1
  plt.rcParams['ytick.minor.width']=1
  plt.rcParams['xtick.major.size']=6
  plt.rcParams['ytick.major.size']=6
  plt.rcParams['xtick.minor.size']=3
  plt.rcParams['ytick.minor.size']=3
  plt.rcParams['xtick.direction']="in"
  plt.rcParams['ytick.direction']="in"
  plt.rcParams['xtick.minor.visible']=True
  plt.rcParams['ytick.minor.visible']=True
  plt.rcParams['xtick.bottom']=True
  plt.rcParams['xtick.top']=True
  plt.rcParams['ytick.left']=True
  plt.rcParams['ytick.right']=True

def label_title(title, units = None) : 
  label = title
  if units : title += " (" + units + ")"
  return title

def y_label_title(range, bins, units = None) : 
  binw = (range[1]-range[0])/bins
  if units == None : 
    title = f"Entries/{binw}"
  else : 
    title = f"Entries/({binw:g} {units})"
  return title

def plot_distr2d(xarr, yarr, bins, ranges, fig, ax, labels, cmap = "YlOrBr", 
                 log = False, ztitle = None, title = None, units = (None, None), 
                 weights = None, colorbar = True) : 
  """
    Plot 2D distribution including colorbox.
      hist   : histogram to be plotted
      fig    : matplotlib figure object
      ax     : matplotlib axis object
      labels : Axis label titles (2-element list)
      cmap   : matplotlib colormap
      log    : if True, use log z scale
      ztitle : x axis title (default is "Entries")
      title : plot title
      units : 2-element list for x axis and y axis units
  """
  #print(xarr.shape, yarr.shape, bins)
  #print("hist2d start")
  def fasthist2d(xvals, yvals, bins, ranges, weights) : 
    vals = (xvals, yvals)
    cuts = (vals[0]>=ranges[0][0]) & (vals[0]<ranges[0][1]) & (vals[1]>=ranges[1][0]) & (vals[1]<ranges[1][1])
    c = ((vals[0][cuts] - ranges[0][0]) / (ranges[0][1] - ranges[0][0]) * bins[0]).astype(np.int_)
    c += bins[0]*((vals[1][cuts] - ranges[1][0]) / (ranges[1][1] - ranges[1][0]) * bins[1]).astype(np.int_)
    H = np.bincount(c, minlength=bins[0]*bins[1], weights = weights).reshape(bins[1], bins[0])
    return H, np.linspace(ranges[0][0], ranges[0][1], bins[0]+1), np.linspace(ranges[1][0], ranges[1][1], bins[1]+1)

  #counts, xedges, yedges = np.histogram2d(xarr, yarr, bins = bins, range = ranges, weights = weights)
  counts, xedges, yedges = fasthist2d(xarr, yarr, bins = bins, ranges = ranges, weights = weights)

  #print("hist2d end")
  norm = None
  if log : 
    vmax = np.max(counts)
    vmin = np.min(counts)
    if vmin <= 0. : vmin = 1.
    if vmax <= vmin : vmax = vmin
    norm = matplotlib.colors.LogNorm(vmin = vmin, vmax = vmax)

  X, Y = np.meshgrid(xedges, yedges)
  #print(xedges.shape)
  #print(yedges.shape)
  #print(X.shape)
  #print(Y.shape)
  #print(counts.shape)
  p = ax.pcolormesh(X, Y, counts, cmap = cmap, norm = norm, linewidth=0, rasterized=True)
  ax.set_xlabel(label_title(labels[0], units[0]), ha='right', x=1.0)
  ax.set_ylabel(label_title(labels[1], units[1]), ha='right', y=1.0)
  if title : ax.set_title(title)
  zt = ztitle
  if not ztitle : zt = r"Entries"
  if colorbar : 
    cb = fig.colorbar(p, pad = 0.01, ax = ax)
    cb.ax.set_ylabel(zt, ha='right', y=1.0)
    if log : 
      cb.ax.set_yscale("log")

def plot_distr1d(arr, bins, range, ax, label, log = False, units = None, weights = None, 
                 title = None, color = None, legend = None, errors = False) : 
  """
    Plot 1D histogram and its fit result. 
      hist : histogram to be plotted
      func : fitting function in the same format as fitting.fit_hist1d
      pars : list of fitted parameter values (output of fitting.fit_hist2d)
      ax   : matplotlib axis object
      label : x axis label title
      units : Units for x axis
  """
  if isinstance(weights, list) : 
    xarr = None
    for i,w in enumerate(weights) : 
      hist, edges = np.histogram(arr, bins = bins, range = range, weights = w)
      if xarr is None : 
        left,right = edges[:-1],edges[1:]
        xarr = np.array([left,right]).T.flatten()
      dataarr = np.array([hist,hist]).T.flatten()
      if color : this_color = color[i]
      else : this_color = f"C{i}"
      if legend : lab = legend[i]
      else : lab = None
      ax.plot(xarr, dataarr, color = this_color, label = lab)
      ax.fill_between( xarr, dataarr, 0., color = this_color, alpha = 0.1)
  elif isinstance(arr, list) : 
    xarr = None
    for i,a in enumerate(arr) : 
      hist, edges = np.histogram(a, bins = bins, range = range, weights = weights)
      if xarr is None : 
        left,right = edges[:-1],edges[1:]
        xarr = np.array([left,right]).T.flatten()
      dataarr = np.array([hist,hist]).T.flatten()
      if color : this_color = color[i]
      else : this_color = f"C{i}"
      if legend : lab = legend[i]
      else : lab = None
      ax.plot(xarr, dataarr, color = this_color, label = lab)
      ax.fill_between( xarr, dataarr, 0., color = this_color, alpha = 0.1)
  else : 
    if color : this_color = color
    else : this_color = data_color
    hist, edges = np.histogram(arr, bins = bins, range = range, weights = weights)
    left,right = edges[:-1],edges[1:]
    xarr = np.array([left,right]).T.flatten()
    dataarr = np.array([hist,hist]).T.flatten()
    if errors : 
      xarr = (left+right)/2.
      ax.errorbar(xarr, hist, np.sqrt(hist), color = this_color, marker = ".", linestyle = '')
    else : 
      ax.plot(xarr, dataarr, color = this_color)
      ax.fill_between( xarr, dataarr, 0., color = this_color, alpha = 0.1)
  ax.set_ylim(bottom = 0.)
  ax.set_xlabel(label_title(label, units), ha='right', x=1.0)
  ax.set_ylabel(y_label_title(range, bins, units), ha='right', y=1.0)
  if title is None : 
    ax.set_title(label + r" distribution")
  elif title : 
    ax.set_title(title)
  if legend : ax.legend(loc = "best")

  #ax.hist( arr, bins = bins, range = range, color = data_color, histtype = "step", weights = weights )
  #ax.set_ylim(bottom = 0.)
  #ax.set_xlabel(label_title(label, units), ha='right', x=1.0)
  #ax.set_ylabel(r"Entries", ha='right', y=1.0)
  #ax.set_title(label + r" distribution")

def plot_distr1d_comparison(data, fit, bins, range, ax, label, log = False, units = None, 
                            weights = None, pull = False, cweights = None, title = None, 
                            legend = None, color = None, data_alpha = 1., legend_ax = None) : 
  """
    Plot 1D histogram and its fit result. 
      hist : histogram to be plotted
      func : fitting function in the same format as fitting.fit_hist1d
      pars : list of fitted parameter values (output of fitting.fit_hist2d)
      ax   : matplotlib axis object
      label : x axis label title
      units : Units for x axis
  """
  if not legend == False : 
    dlab, flab = "Data", "Fit"
  else : 
    dlab, flab = None, None
  datahist, _ = np.histogram(data, bins = bins, range = range)
  fithist1, edges = np.histogram(fit, bins = bins, range = range, weights = weights)
  fitscale = np.sum(datahist)/np.sum(fithist1)
  fithist = fithist1*fitscale
  left,right = edges[:-1],edges[1:]
  fitarr = np.array([fithist,fithist]).T.flatten()
  dataarr = np.array([datahist,datahist]).T.flatten()
  xarr = np.array([left,right]).T.flatten()
  ax.plot(xarr, fitarr, label = flab, color = fit_color)

  if isinstance(cweights, list) : 
    cxarr = None
    for i,w in enumerate(cweights) : 
      if weights : w2 = w*weights
      else : w2 = w
      chist, cedges = np.histogram(fit, bins = bins, range = range, weights = w2)
      if cxarr is None : 
        cleft,cright = cedges[:-1],cedges[1:]
        cxarr = (cleft+cright)/2.
      fitarr = chist*fitscale
      if color : this_color = color[i]
      else : this_color = f"C{i+1}"
      if legend : lab = legend[i]
      else : lab = None
      ax.plot(cxarr, fitarr, color = this_color, label = lab)
      ax.fill_between( cxarr, fitarr, 0., color = this_color, alpha = 0.1)

  xarr = (left+right)/2.
  ax.errorbar(xarr, datahist, np.sqrt(datahist), label = dlab, color = data_color, marker = ".", 
              linestyle = '', alpha = data_alpha)

  if not legend == False : 
    if legend_ax : 
      h, l = ax.get_legend_handles_labels()
      legend_ax.legend(h, l, borderaxespad=0)
      legend_ax.axis("off")
    else : ax.legend(loc = "best")
  ax.set_ylim(bottom = 0.)
  ax.set_xlabel(label_title(label, units), ha='right', x=1.0)
  ax.set_ylabel(y_label_title(range, bins, units), ha='right', y=1.0)
  if title is None : 
    ax.set_title(label + r" distribution")
  elif title : 
    ax.set_title(title)
  if pull : 
    xarr = np.array([left,right]).T.flatten()
    with np.errstate(divide='ignore'):
      pullhist = (datahist-fithist)/np.sqrt(datahist)
      pullhist[datahist == 0] = 0
    pullarr = np.array([pullhist,pullhist]).T.flatten()
    ax2 = ax.twinx()
    ax2.set_ylim(bottom = -10.)
    ax2.set_ylim(top =  10.)
    ax2.plot(xarr, pullarr, color = diff_color, alpha = 0.3)
    ax2.grid(False)
    ax2.set_ylabel(r"Pull", ha='right', y=1.0)
    return [ ax2 ]
  return []

def plot_distr_comparison(arr1, arr2, bins, ranges, labels, fig, axes, units = None, cmap = "jet") : 
  dim = arr1.shape[1]

  for i in range(dim) : 
    plot_distr1d_comparison(arr1[:,i], arr2[:,i], bins[i], ranges[i], axes[0,i], labels[i], pull = True)

  n = 0
  for i in range(dim) : 
    for j in range(i) : 
      if dim%2 == 0 : 
        ax1 = axes[n // (dim//2) + 1, n % (dim//2)]
        ax2 = axes[n // (dim//2) + 1, n % (dim//2)+1]
      else : 
        ax1 = axes[2*(n // dim) + 1, n % dim]
        ax2 = axes[2*(n // dim) + 2, n % dim]
      plot_distr2d(arr1[:,i], arr1[:,j], bins = (bins[i], bins[j]), 
                   ranges = (ranges[i], ranges[j]), fig = fig, ax = ax1, labels = (labels[i], labels[j]), cmap = cmap )
      plot_distr2d(arr2[:,i], arr2[:,j], bins = (bins[i], bins[j]), 
                   ranges = (ranges[i], ranges[j]), fig = fig, ax = ax2, labels = (labels[i], labels[j]), cmap = cmap )
      n += 1

class MultidimDisplay : 
  def __init__(self, data, norm, bins, ranges, labels, fig, axes, units = None, cmap = "jet") : 
    self.dim = data.shape[1]
    self.data = data
    self.norm = norm
    self.bins = bins
    self.ranges = ranges
    self.labels = labels
    self.fig = fig
    self.axes = axes
    self.units = units
    self.cmap = cmap
    self.size = data.shape[0]
    self.first = True
    self.newaxes = []
    n = 0
    for i in range(self.dim) : 
      for j in range(i) : 
        if self.dim%2 == 0 : 
          ax1 = axes[(n // (self.dim//2)) + 1, 2*(n % (self.dim//2))]
        else : 
          ax1 = axes[2*(n // self.dim) + 1, n % self.dim]
        plot_distr2d(data[:,i], data[:,j], bins = (bins[i], bins[j]), 
                   ranges = (ranges[i], ranges[j]), fig = fig, ax = ax1, 
                   labels = (labels[i], labels[j]), cmap = cmap )
        n += 1

  def draw(self, weights) : 

    scale = float(self.size)/np.sum(weights)
    for a in self.newaxes : a.remove()
    self.newaxes = []

    for i in range(self.dim) : 
      self.axes[0,i].clear()
      newax = plot_distr1d_comparison(self.data[:,i], self.norm[:,i], self.bins[i], 
                              self.ranges[i], self.axes[0,i], self.labels[i], 
                              weights = scale*weights, pull = True, data_alpha = 0.3)
      self.newaxes += newax

    n = 0
    for i in range(self.dim) : 
      for j in range(i) : 
        if self.dim%2 == 0 : 
          ax2 = self.axes[(n // (self.dim//2)) + 1, 2*(n % (self.dim//2)) + 1]
        else : 
          ax2 = self.axes[2*(n // self.dim) + 2, n % self.dim ]
        ax2.clear()
        plot_distr2d(self.norm[:,i], self.norm[:,j], bins = (self.bins[i], self.bins[j]), 
                     ranges = (self.ranges[i], self.ranges[j]), fig = self.fig, ax = ax2, 
                     labels = (self.labels[i], self.labels[j]), cmap = self.cmap, 
                     weights = scale*weights, colorbar = self.first )
        n += 1

    self.first = False
