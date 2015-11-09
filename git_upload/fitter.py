import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import sigmaclip
import copy
import time

from IPython.core.debugger import Tracer

def fitter(wavelength_in,data_in,error_in,models_in,options):

	"""
	The essential ingredient of FIREFLY!

	Taking each base model as an initial guess, the fitter iteratively
	creates combinations of these base models when they improve the
	modified chi-squared value:
	value = chi-squared + BIC term - exploration term
	See thesis / documentation for details.

	Input: data, base models, wavelength (for plotting) [, options]
			(data must be an array of length N)
			(base models must be a matrix of num_models x N)


	Options: plot_eps: True/False (plot to fit.eps if True, X if False)

	Output: a set of model weight combinations and their associated chi-squared values,
			via an array of 'fit' objects.
			Weights are arrays with length num_models.
			Fit arrays may be any size up to 10000.

	"""

	global models 		
	models 		= models_in
	global data 		
	data 		= data_in
	global error 		
	error 		= error_in
	global wavelength 	
	wavelength 	= wavelength_in

	global index_count
	index_count = 0
	global iterate_count
	iterate_count = 0

	# Set options manually here for testing
	plot_eps,upper_limit_fit,fit_cap = options['plot_eps'],options['max_iterations'],options['fit_per_iteration_cap']
	# plot_eps 		= False
	# upper_limit_fit = 10 # maximum number of iterations before it gives up!
	# fit_cap			= 1000 # maximum number of fit objects to be created per iteration

	num_models 	= len(models)
	num_wave 	= len(wavelength)
	
	global num_models	
	global bic_n
	bic_n = np.log(num_wave)

	chi_models = np.zeros(np.shape(models))
	for m in range(num_models):
		chi_models[m] = (models[m]-data)/error
	global chi_models

	class fit(object):

		"""
		A fit object contains:
			- index number in array (useful for clipping later)
			- branch number (i.e. first iteration is 0, second is 1, etc.)
			- index number of previous element in list (the 'parent', useful to check for improvement in chi-squared)
			- base model weights (array of weights matching the input model array)
			- raw chi-squared value
		and the following in-built functions:
			- spawn children iteratively
			- plot the model combinations compared to the data

		When initialises it:
			- makes the weights, branch number, index number and previous index based on inputs

		"""
		def __init__(self, weights, branch_num):
			if branch_num > 1:
				global clipped_arr
			global index_count
			super(fit, self).__init__()
			self.weights 		= weights
			self.branch_num 	= branch_num
			self.index 			= index_count
			#self.parent_index 	= parent_index
			
			# Auto-calculate chi-squared
			index_weights 		= np.nonzero(self.weights) # saves time!
			#chi_arr 			= ((np.dot(self.weights,models))	- data) / error
			chi_arr = np.dot(self.weights[index_weights],chi_models[index_weights])
			
			if branch_num == 0:
				chi_clipped_arr 	= sigmaclip(chi_arr, low=3.0, high=3.0)
				chi_clip_sq 		= np.square(chi_clipped_arr[0])
				clipped_arr 		= (chi_arr > chi_clipped_arr[1]) & (chi_arr < chi_clipped_arr[2])
				self.clipped_arr 	= clipped_arr
			else:
				chi_clip_sq 		= np.square(chi_arr[clipped_arr])
			#print time.time()-time_begin
			chi_squared 		= np.sum(chi_clip_sq)
			#print chi_squared
			self.chi_squared 	= chi_squared 

			index_count += 1


		def spawn_children(self,branch_num):

			# Auto-produce an array of children with iteratively increased weights
			fit_list = []
			new_weights = self.weights*branch_num

			sum_weights = np.sum(new_weights)+1

			for im in range(num_models):
				new_weights[im]+= 1
				fit_add 		= fit(new_weights/sum_weights,branch_num)
				fit_list.append(fit_add)
				new_weights[im]-= 1

			return fit_list


		def plot(self,plot_eps):

			fit_plot 	= np.dot((self.weights) , models)

			fig,ax 		= plt.subplots()
			ax.plot(wavelength,data,color='k',linewidth=2.0) #k is black in matplotlib
			ax.plot(wavelength,fit_plot,color='r',linewidth=1.0)
			ax.set_xlabel(r'Wavelength / $\AA$',fontsize=22)
			ax.set_ylabel('Flux density / arbitrary units',fontsize=22)
			ax.tick_params(axis='x',labelsize=22)
			ax.tick_params(axis='y',labelleft='off')
			out_plot_string = '/users/wilkinda/Desktop/example_fit/new_fit.eps'
			if plot_eps:
				plt.savefig(out_plot_string,format='eps',transparent=True)
			else:
				plt.show()
			plt.close()



	def retrieve_properties(fit_list):
		# Return an array of all weights and chi-squared of the fits (mainly used for testing)
		lf = len(fit_list)
		returned_weights 	= np.zeros((lf,num_models))
		returned_chis		= np.zeros(lf)
		returned_branch		= np.zeros(lf)

		for f in range(len(fit_list)):
			returned_weights[f] = fit_list[f].weights 
			returned_branch[f]	= fit_list[f].branch_num
			returned_chis[f] 	= fit_list[f].chi_squared

		return returned_weights,returned_chis,returned_branch

	def bic_term():
		# For convergence
		global bic_n
		return bic_n# * self.branch_num

	def previous_chi(branch_num,fit_list):
		# To ensure exploration
		returned_chis = [o.chi_squared for o in fit_list]
		diff = np.min(returned_chis)#diff = 	np.percentile(returned_chis[np.where(returned_branch == branch_num-1)],percentile_use)
				
		return diff
	
	def iterate(fit_list):

		global iterate_count		
		iterate_count += 1
		print "Iteration step: "+str(iterate_count)

		count_new = 0

		len_list = len(copy.copy(fit_list))
		save_bic		= bic_term()
		previous_chis 	= previous_chi(iterate_count,fit_list)
		for f in range(len_list):
			new_list = fit_list[f].spawn_children(iterate_count)
			len_new = len(new_list)
			for n in range(len_new):

				# Check if any of the new spawned children represent better solutions
				new_chi 		= new_list[n].chi_squared
				extra_term 		= save_bic
				check_better 	= new_chi < previous_chis-extra_term

				if check_better:
					# If they do, add them to the fit list!
					count_new += 1
					if count_new > fit_cap:
						break
					fit_list.append(new_list[n])

			if count_new > fit_cap:
				print "Capped solutions at "+str(fit_cap)
				break
		if count_new == 0:
			# If they don't, we have finished the iteration process and may return.
			print "Converged!"
			print "Fit list with this many elements:"
			print len(fit_list)
			return fit_list
		else:
			if iterate_count == 10:
				print "Fit has not converged within user-defined number of iterations."
				print "Make sure this is a reasonable number."
				print "Returning all fits up to this stage."
				return fit_list
			else:
				print "Found "+str(count_new)+" new solutions. Iterate further..."
			fit_list_new = iterate(fit_list)
			return fit_list_new
	

	def mix(fit_list,full_fit_list,min_chi):
		"""
		Mix the best solutions together to improve error estimations.
		Never go more than 100 best solutions!
		"""
		# Importance check:
		important_chi 	= min_chi + 10.0
		extra_fit_list 	= []#copy.copy(fit_list)

		print "Mixing best solutions to improve estimate."
		#print str(len(fit_list))+' fits to cross-check!'
		for f1 in range(len(fit_list)):
			for f2 in range(len(full_fit_list)):
				for q in [0.0000001,0.000001,0.00001,0.0001,0.001,0.01,0.1,1.0]:

					new_fit = fit(	(fit_list[f1].weights+q*full_fit_list[f2].weights) / (1.0+q),\
									fit_list[f1].branch_num+full_fit_list[f2].branch_num)
					#if new_fit.chi_squared < important_chi:
					extra_fit_list.append(new_fit)

		print "Added "+str(len(extra_fit_list))+" solutions!"
		return extra_fit_list


	# Initialise fit objects over initial set of models
	fit_list = []
	int_chi  = []

	zero_weights = np.zeros(len(models))


	print "Initiating fits..."
	for im in range(len(models)):
		zero_weights[im]+= 1
		fit_first = fit(copy.copy(zero_weights),0)
		fit_list.append(fit_first)
		int_chi.append(fit_first.chi_squared)
		zero_weights[im]-= 1
		
	# Find clipped array to remove artefacts:
	global clipped_arr

	clipped_arr = fit_list[np.argmin(int_chi)].clipped_arr

	# Fit_list is our initial guesses from which we will iterate
	print "Calculated initial chi-squared values."
	print "Begin iterative process."

	


	final_fit_list = iterate(fit_list)
	junk,chis,more_junk = retrieve_properties(final_fit_list)

	best_fits = np.argsort(chis)	

	# print "Best chi (raw, reduced) is:"
	# print min(chis)
	# print min(chis)/len(wavelength)
	bf = len(best_fits)
	if bf>10:
		bf=10
	extra_fit_list 		= mix(np.asarray(final_fit_list)[best_fits[:bf]].tolist(),final_fit_list,np.min(chis))
	total_fit_list 		= final_fit_list+extra_fit_list
	#junk,chis,more_junk = retrieve_properties(total_fit_list)
	#total_fit_list[np.argmin(chis)].plot(plot_eps)

	return retrieve_properties(total_fit_list)



