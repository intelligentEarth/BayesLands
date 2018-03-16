##~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~##
##                                                                                   ##
##  This file forms part of the BayesLands surface processes modelling companion.      ##
##                                                                                   ##
##  For full license and copyright information, please refer to the LICENSE.md file  ##
##  located at the project root, or contact the authors.                             ##
##                                                                                   ##
##~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~##
"""
This script is intended to 
"""

import numpy as np
import random
import time
import math
import cmocean as cmo
from pylab import rcParams
import fnmatch
import shutil
from PIL import Image
from io import StringIO
from cycler import cycler
import os

import matplotlib as mpl
import matplotlib.mlab as mlab
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection

from scipy.spatial import cKDTree
from scipy import stats 
from pyBadlands.model import Model as badlandsModel
from mpl_toolkits.axes_grid1 import make_axes_locatable
from mpl_toolkits.mplot3d import Axes3D

import plotly
import plotly.plotly as py
import plotly.graph_objs as go
from plotly.graph_objs import *
plotly.offline.init_notebook_mode()
from plotly.offline.offline import _plot_html

def plotFunctions(fname, pos_likl, pos_rain, pos_erod, pos_taus):
	
	burnin = 0.05 * len(pos_likl)  # use post burn in samples
	pos_likl = pos_likl[int(burnin):,]
	pos_taus = pos_taus[int(burnin):, ]
	pos_erod = pos_erod[int(burnin):]
	pos_rain = pos_rain[int(burnin):]
	font = 9
	width = 1
	nb_bins=10
	slen = np.arange(0,len(pos_likl),1)
	
	######################################     RAIN      ################################

	rainmin, rainmax = min(pos_rain), max(pos_rain)
	rainspace = np.linspace(rainmin,rainmax,len(pos_rain))
	rainm,rains = stats.norm.fit(pos_rain)
	pdf_rain = stats.norm.pdf(rainspace,rainm,rains)
	print 'erodmin', rainmin
	print 'erodmax', rainmax

	
	rain_real_value = 1.0

	data = [go.Histogram(x=pos_rain, histnorm='probability')]

	layout = go.Layout(margin=dict(l=0,r=0,b=0,t=0))
	layout = {
	'shapes': [
		# Line Vertical
		{
			'type': 'line',
			'x0': rain_real_value,
			'y0': 0,
			'x1': rain_real_value,
			'y1': 0.5,
			'line': {
				'color': 'rgb(128, 0, 128)',
				'width': 4,
				'dash': 'dot',
			},
		}
	]
	}

	fig_rain = go.Figure(data=data, layout=layout)
	graph = plotly.offline.plot(fig_rain, auto_open = False, output_type = 'file', filename='%s/plot_image_rain.html' %(fname), validate=False)


	#####################################      EROD    ################################
	erodmin, erodmax = min(pos_erod), max(pos_erod)
	erodspace = np.linspace(erodmin,erodmax,len(pos_erod))
	erodm,erods = stats.norm.fit(pos_erod)
	pdf_erod = stats.norm.pdf(erodspace,erodm,erods)
	print 'erodmin', erodmin
	print 'erodmax', erodmax

	erod_real_value = 1.e-5

	data = [go.Histogram(x=pos_erod, histnorm='probability')]
	layout = {
	'shapes': [
		# Line Vertical
		{
			'type': 'line',
			'x0': erod_real_value,
			'y0': 0,
			'x1': erod_real_value,
			'y1': 0.5,
			'line': {
				'color': 'rgb(128, 0, 128)',
				'width': 4,
				'dash': 'dot',
			},
		}
	]
	}

	fig_erod = go.Figure(data=data, layout=layout)
	graph = plotly.offline.plot(fig_erod, auto_open = False, output_type = 'file', filename='%s/plot_image_erod.html' %(fname), validate=False)


	#####################################      likl    ################################
	liklmin, liklmax = min(pos_likl), max(pos_likl)
	liklspace = np.linspace(liklmin,liklmax,len(pos_likl))
	liklm,likls = stats.norm.fit(pos_likl)
	pdf_likl = stats.norm.pdf(liklspace,liklm,likls)
	liklmean=np.mean(pos_likl)
	liklmedian=np.median(pos_likl)

	fig = plt.figure(figsize=(8,10))
	ax = fig.add_subplot(111)
	ax.spines['top'].set_color('none')
	ax.spines['bottom'].set_color('none')
	ax.spines['left'].set_color('none')
	ax.spines['right'].set_color('none')
	ax.tick_params(labelcolor='w', top='off', bottom='off', left='off', right='off')
		
	ax1 = fig.add_subplot(211)
	#ax1.set_facecolor('#f2f2f3')
	ax1.set_axis_bgcolor("white")
	
	ax1.plot(slen,pos_likl,linestyle='-', linewidth= width, color='k', label=None)
	ax1.set_title(r'Trace of Likelihood',size= font+2)
	ax1.set_xlabel('Samples',size= font+1)
	ax1.set_ylabel(r'Likelihood', size= font+1)
	ax1.set_xlim([0,np.amax(slen)])
	
	tausmin, tausmax = min(pos_taus), max(pos_taus)
	tausspace = np.linspace(tausmin,tausmax,len(pos_taus))
	tausm,tauss = stats.norm.fit(pos_taus)
	pdf_taus = stats.norm.pdf(tausspace,tausm,tauss)
	tausmean=np.mean(pos_taus)
	tausmedian=np.median(pos_taus)

	ax2 = fig.add_subplot(212)
	#ax2.set_facecolor('#f2f2f3')
	ax2.set_axis_bgcolor("white")
	
	ax2.plot(slen,pos_taus,linestyle='-', linewidth= width, color='k', label=None)
	ax2.set_title(r'Trace of Tau sq',size= font+2)
	ax2.set_xlabel('Samples',size= font+1)
	ax2.set_ylabel(r'Tausq', size= font+1)
	ax2.set_xlim([0,np.amax(slen)])
	fig.tight_layout()
	fig.subplots_adjust(top=0.88)
	plt.savefig('%slik_tau.png'% (fname), bbox_inches='tight', dpi=300, transparent=False)
	plt.clf()

	####################################      Joint    ################################
	fig = plt.figure(figsize=(10,12))
	ax = fig.add_subplot(111)
	ax.spines['top'].set_color('none')
	ax.spines['bottom'].set_color('none')
	ax.spines['left'].set_color('none')
	ax.spines['right'].set_color('none')
	ax.tick_params(labelcolor='w', top='off', bottom='off', left='off', right='off')
	ax.set_title(' Rain Parameter', fontsize=  font+2)#, y=1.02)
	
	ax1 = fig.add_subplot(211, projection = '3d')
	#ax1.set_facecolor('#f2f2f3')
	ax1.set_axis_bgcolor("white")
	

	hist, rainedges, erodedges = np.histogram2d(pos_rain, pos_erod, bins = 15 , range = [[rainmin, rainmax],[erodmin, erodmax]])
	rainpos, erodpos = np.meshgrid(rainedges[:-1], erodedges[:-1])
	rainpos = rainpos.flatten('F')
	erodpos = erodpos.flatten('F')
	zpos = np.zeros_like(rainpos)
	drain = 0.5* np.ones_like(zpos)
	derod = drain.copy()
	dz = hist.flatten()
	ax1.bar3d(rainpos, erodpos, zpos, drain, derod, dz, color = 'g', zsort = 'average')
	#plt.savefig('%sjoint.png'% (fname), bbox_inches='tight', dpi=300, transparent=False)
	#plt.clf()

	trace1 = go.Scatter3d(x=rainpos, y=erodpos, z=dz, mode='markers', marker=dict(size=12, color = dz, colorscale='Portland', showscale=True))
	data = [trace1]
	layout = go.Layout(title='Joint distribution rain, erod',autosize=True,width=1000,height=1000, scene=Scene(
				xaxis=XAxis(title = 'Rain', nticks=10,gridcolor='rgb(255, 255, 255)',gridwidth=2,zerolinecolor='rgb(255, 255, 255)',zerolinewidth=2),
				yaxis=YAxis(title = 'Erodibility', nticks=10,gridcolor='rgb(255, 255, 255)',gridwidth=2,zerolinecolor='rgb(255, 255, 255)',zerolinewidth=2),
				bgcolor="rgb(244, 244, 248)"
			))
	fig = go.Figure(data=data, layout=layout)
	graph = plotly.offline.plot(fig, auto_open=False, output_type='file', filename='%s/plots/plot_image_joint3d.html' %(fname), validate=False)

	trace = go.Scattergl(x= pos_rain, y = pos_erod, mode = 'markers', marker = dict(color = '#FFBAD2',line = dict(width = 1)))
	data = [trace]
	layout = go.Layout(margin=dict(l=0,r=0,b=0,t=0))
	fig = go.Figure(data=data, layout=layout)
	graph = plotly.offline.plot(fig, auto_open = False, output_type = 'file', filename='%s/plots/plot_image_jointscatter.html' %(fname), validate=False)

def main():

	run_nb = input('Please enter the folder number i.e. mcmcresults_% ')

	fname = 'mcmcresults_%s/' % (run_nb)
	likl_filename = 'mcmcresults_%s/accept_likl.txt' % (run_nb)
	rain_filename = 'mcmcresults_%s/accept_rain.txt' % (run_nb)
	erod_filename = 'mcmcresults_%s/accept_erod.txt' % (run_nb)
	taus_filename = 'mcmcresults_%s/accept_tau_elev.txt' % (run_nb)
	#m_filename = 'mcmcresults_%s/accept_m.txt' % (run_nb)
	#n_filename = 'mcmcresults_%s/accept_n.txt' % (run_nb)
	
	filename_list = []
	filename_list.append(likl_filename)
	filename_list.append(rain_filename)
	filename_list.append(erod_filename)
	filename_list.append(taus_filename)
	#filename_list.append(m_filename)
	#filename_list.append(n_filename)

	likl = []
	rain = []
	erod = []
	taus = []
	#m = []
	#n = []

	for list_name in filename_list:
		with open(list_name) as f:
			next(f)
			next(f)
			for line in f:
				words = line.split()
				error = words[2]
				lname =  list_name[-8:-4]
				if lname == 'likl':
					likl.append(error)
				elif lname == 'rain':
					rain.append(error)
				elif lname == 'erod':
					erod.append(error)
				elif lname == 'elev':
					taus.append(error)	

	print 'length of likl', len(likl)
	print 'length of rain', len(rain)
	print 'length of erod', len(erod)
	print 'length of taus', len(taus)

	likl_ = np.asarray(likl, dtype = float)
	rain_ = np.asarray(rain, dtype = float)
	erod_ = np.asarray(erod, dtype = float)
	taus_ = np.asarray(taus, dtype = float)

	plotFunctions(fname, likl_, rain_, erod_, taus_)
	
	print '\nFinished plotting'

if __name__ == "__main__": main()

