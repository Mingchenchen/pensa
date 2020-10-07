import numpy as np
import scipy as sp
import scipy.stats
import mdshare
import pyemma
from pyemma.util.contexts import settings
import MDAnalysis as mda
import matplotlib.pyplot as plt



# --- METHODS FOR FEATURE DIFFERENCE ANALYSIS ---


def relative_entropy_analysis(features_a, features_g, all_data_a, all_data_g, bin_width=0.001, verbose=True):
    """
    Calculates Jensen-Shannon distance and Kullback-Leibler divergences for two distributions.
    """
    
    # Assert that features are the same and data sets have same number of features
    assert features_a.describe() == features_g.describe()
    assert all_data_a.shape[0] == all_data_g.shape[0] 
    
    # Extract names of features
    data_names = features_a.active_features[0].describe()

    # Initialize relative entropy and average value
    data_jsdist = np.zeros(len(data_names))
    data_kld_ag = np.zeros(len(data_names))
    data_kld_ga = np.zeros(len(data_names))
    data_avg    = np.zeros(len(data_names))

    for i in range(len(all_data_a)):

        data_a = all_data_a[i]
        data_g = all_data_g[i]
        
        # Combine both data sets
        data_both = np.concatenate((data_a,data_g))
        data_avg[i] = np.mean(data_both)
        
        # Get bin values for all histograms from the combined data set
        bins_min = np.min( data_both )
        bins_max = np.max( data_both )
        bins = np.arange(bins_min,bins_max,bin_width)

        # Calculate histograms for combined and single data sets
        histo_both = np.histogram(data_both, density = True)
        histo_a = np.histogram(data_a, density = True, bins = histo_both[1])
        distr_a = histo_a[0] / np.sum(histo_a[0])
        histo_g = np.histogram(data_g, density = True, bins = histo_both[1])
        distr_g = histo_g[0] / np.sum(histo_g[0])
        
        # Calculate relative entropies between the two data sets (Kullback-Leibler divergence)
        data_kld_ag[i] = np.sum( sp.special.kl_div(distr_a,distr_g) )
        data_kld_ga[i] = np.sum( sp.special.kl_div(distr_g,distr_a) )
        
        # Calculate the Jensen-Shannon distance
        data_jsdist[i] = scipy.spatial.distance.jensenshannon(distr_a, distr_g, base=2.0)
        
        if verbose:
            print(i,'/',len(all_data_a),':', data_names[i]," %1.2f"%data_avg[i],
                  " %1.2f %1.2f %1.2f"%(js_dist,rel_ent_ag,rel_ent_ga))
        
    return data_names, data_jsdist, data_kld_ag, data_kld_ga



def kolmogorov_smirnov_analysis(features_a, features_g, all_data_a, all_data_g, bin_width=0.001, verbose=True):
    """
    Calculates Kolmogorov-Smirnov statistic for two distributions.
    """
    
    # Assert that features are the same and data sets have same number of features
    assert features_a.describe() == features_g.describe()
    assert all_data_a.shape[0] == all_data_g.shape[0] 
    
    # Extract names of features
    data_names = features_a.active_features[0].describe()

    # Initialize relative entropy and average value
    data_avg = np.zeros(len(data_names))
    data_kss = np.zeros(len(data_names))
    data_ksp = np.zeros(len(data_names))

    for i in range(len(all_data_a)):

        data_a = all_data_a[i]
        data_g = all_data_g[i]
        
        # Perform Kolmogorov-Smirnov test
        ks = sp.stats.ks_2samp(data_a,data_g)
        data_kss[i] = ks.statistic
        data_ksp[i] = ks.pvalue
        
        # Combine both data sets
        data_both = np.concatenate((data_a,data_g))
        data_avg[i] = np.mean(data_both)
        
        if verbose:
            print(i,'/',len(all_data_a),':', data_names[i]," %1.2f"%data_avg[i],
                  " %1.2f %1.2f"%(ks.statistic,ks.pvalue) )
        
    return data_names, data_kss, data_ksp



def mean_difference_analysis(features_a, features_g, all_data_a, all_data_g, verbose=True):
    """
    Compares the arithmetic means of two distance distributions.
    """
    
    # Assert that features are the same and data sets have same number of features
    assert features_a.describe() == features_g.describe()
    assert all_data_a.shape[0] == all_data_g.shape[0] 
    
    # Extract names of features
    data_names = features_a.active_features[0].describe()

    # Initialize relative entropy and average value
    data_diff = np.zeros(len(data_names))
    data_avg  = np.zeros(len(data_names))

    for i in range(len(all_data_a)):

        data_a = all_data_a[i]
        data_g = all_data_g[i]

        # Calculate means of the data sets
        mean_a = np.mean(data_a)
        mean_g = np.mean(data_g)

        # Calculate difference of means between the two data sets
        diff_ag = mean_a-mean_g
        mean_ag = 0.5*(mean_a+mean_g)

        # Update the output arrays
        data_avg[i]  = mean_ag
        data_diff[i] = diff_ag
        
        if verbose:
            print(i,'/',len(all_data_a),':', data_names[i]," %1.2f"%data_avg[i],
                  " %1.2f"%data_diff[i])
        
    return data_names, data_avg, data_diff



def get_feature_timeseries(feat, data, feature_type, feature_name):
    
    index = np.where( np.array( feat[feature_type].describe() ) == feature_name )[0][0]

    timeseries = data[feature_type][:,index]
    
    return timeseries



def sort_features(names, sortby):
    """
    Sort features by a list of values.
    
    Parameters
    ----------
    names: str array
        array of feature names.
    sortby: float array
        array of the values to sort the names by.
        
    Returns
    -------
    sort: array of tuples (str, float)
        array of sorted tuples with feature and value
    
    """

    sort_id = np.argsort(sortby)[::-1]  
    
    sorted_names = []
    sorted_values = []
    
    for i in sort_id:
        sorted_names.append(np.array(names)[i])
        sorted_values.append(sortby[i])
        
    sn, sv = np.array(sorted_names), np.array(sorted_values)
    
    sort = np.array([sn,sv]).T
    
    return sort



def residue_visualization(names, data, ref_filename, pdf_filename, pdb_filename, 
                          selection='max', y_label='max. JS dist. of BB torsions'):
    """
    Visualizes features per residue as plot and in PDB files, assuming values from 0 to 1. 
    
    Parameters
    ----------
    names: str array
        Names of the features in PyEMMA nomenclaturre (contain residue ID).
    data: float array
        Data to project onto the structure.
    ref_filename: str
        Name of the file for the reference structure.
    pdf_filename: str
        Name of the PDF file to save the plot.
    pdb_filename: str
        Name of the PDB file to save the structure with the values to visualize.
    selection: str ['max', 'min']
        How to select the value to visualize for each residue from all its features.
    y_label: str
        Label of the y axis of the plot.
        
    """
    
    # -- INITIALIZATION --
    
    # Structure to use for visualization
    u = mda.Universe(ref_filename)
    vis_resids = u.residues.resids
    # Output values
    default = 0 if selection=='max' else 1
    vis_values = default*np.ones(len(vis_resids))
    
    # -- VALUE ASSIGNMENT --

    for i,name in enumerate(names):
        # To each residue ...
        resid = int( name.split(' ')[-1][:-1] )
        index = np.where(vis_resids == resid)[0][0]
        # ... assign the difference measures of the torsion angle with the higher (or lower) value
        if selection == 'max':
            vis_values[index] = np.maximum(vis_values[index], data[i])
        elif selection == 'min':
            vis_values[index] = np.minimum(vis_values[index], data[i])

    # -- FIGURE --
    
    fig,ax = plt.subplots(1,1,figsize=[4,3],dpi=300)
    # Plot values against residue number
    ax.plot(vis_resids, vis_values, '.')
    ax.set_ylim(0,1)
    # Labels
    ax.set_xlabel('residue number')
    ax.set_ylabel(y_label)
    fig.tight_layout()
    # Save the figure
    fig.savefig(pdf_filename)
    
    # -- PDB FILE --
    
    u.add_TopologyAttr('tempfactors')
    # Write values as beta-factors ("tempfactors") to a PDB file
    for res in range(len(vis_values)):
        u.residues[res].atoms.tempfactors = vis_values[res]
    u.atoms.write(pdb_filename)
        
    return vis_resids, vis_values



def sort_distances(dist_names, dist_avg, dist_relen, dist_id):

    # Define the criteria
    min_rel_ent = 0.2
    min_av_dist = 0.0 # [nm]
    max_av_dist = 2.5 # [nm] 
    min_id_diff = 300 # minimum difference of the atom numbers 

    # Extract IDs of the atoms used
    dist_id_diff = dist_id[:,1] - dist_id[:,0]

    # Combine the criteria
    criteria =  (dist_id_diff > min_id_diff) 
    criteria *= (dist_relen > min_rel_ent)
    criteria *= (dist_avg < max_av_dist)
    criteria *= (dist_avg > min_av_dist)

    # Sort the distances not filtered out by the criteria
    sort_id = np.argsort(dist_relen[criteria])[::-1]

    # ... and print them
    for i in sort_id:
        print(np.array(dist_names)[criteria][i], 
              '; %1.3f'%dist_avg[criteria][i], 
              '; %1.3f'%dist_relen[criteria][i] )
        
        

def distances_visualization(dist_names, dist_diff, out_filename, 
                            vmin=None, vmax=None):
        
    # Distance Matrix
    firstres = int(dist_names[0].split(' ')[2])
    lastres  = int(dist_names[-1].split(' ')[2])
    print('first:',firstres,', last:',lastres)
    size = lastres-firstres+2
    diff = np.zeros([size,size])
    for n,name in enumerate(dist_names):
        splitname = name.split(' ')
        resi,resj = int(splitname[2]),int(splitname[7])
        i = resi - firstres
        j = resj - firstres
        diff[i,j] = dist_diff[n]
        diff[j,i] = dist_diff[n]
            
    # Plot
    fig,ax = plt.subplots(1,1,figsize=[6,4],dpi=300)
    img = ax.imshow(diff, vmin=vmin, vmax=vmax)
    ax.xaxis.set_ticks_position('top')
    ax.set_xticks(np.arange(50-firstres,450,50))
    ax.set_yticks(np.arange(50-firstres,450,50))
    ax.set_xticklabels(np.arange(50,451,50))
    ax.set_yticklabels(np.arange(50,451,50))
    fig.colorbar(img,ax=ax)
    fig.tight_layout()
    fig.savefig(out_filename,dpi=300)  
    
    return diff




# --- METHODS FOR PRINCIPAL COMPONENT ANALYSIS ---


def calculate_pca(data):
    '''Performs a PyEMMA PCA on the provided data
    
    Parameters
    ----------
    data: float array.
        Trajectory data [frames,frame_data]
    '''
    
    pca = pyemma.coordinates.pca(data)
    
    # Plot the eigenvalues
    fig,ax = plt.subplots(1,1,figsize=[4,3],dpi=100)
    ax.plot(pca.eigenvalues[:12],'o')
    plt.show()   
    
    return pca


def pca_features(pca,features,num,threshold):
    '''Prints relevant features and plots feature correlations.
    
    Parameters
    ----------
    pca: pyemma PCA object.
        The PCA of which to plot the features.
    features: list of strings
        Features for which the PCA was performed (obtained from features object via .describe()).
    num: float.
        Number of feature correlations to plot.
    threshold: float.
        Features with a correlation above this will be printed.
    '''
    
    # Plot the highest PC correlations and print relevant features
    fig,ax = plt.subplots(num,1,figsize=[4,num*3],dpi=100,sharex=True)
    for i in range(num):
        relevant = pca.feature_PC_correlation[:,i]**2 > threshold
        print(np.array(features)[relevant])
        ax[i].plot(pca.feature_PC_correlation[:,i])
    plt.show()
    
    
def project_on_pc(data,ev_idx,pca=None):
    '''Projects a trajectory onto an eigenvector of its PCA.
    
    Parameters
    ----------
    data: float array.
        Trajectory data [frames,frame_data]
    ev_idx: int
        Index of the eigenvector to project on
    pca (opt.): pyemma PCA object.
        Pre-calculated PCA. Must be calculated for the same features (but not necessarily the same trajectory)
    '''
    
    if pca is None:
        pca = pyemma.coordinates.pca(data) #,dim=3)

    projection = np.zeros(data.shape[0])
    for ti in range(data.shape[0]):
        projection[ti] = np.dot(data[ti],pca.eigenvectors[:,ev_idx])
        
    return projection
    

def sort_traj_along_pc(data, pca, start_frame, ref, name, out_name, num_pc=3):
    '''Sort a trajectory along given principal components.
    
    Parameters
    ----------
    data: float array.
        Trajectory data [frames,frame_data]
    pca: PCA object.
        principal compoenents information
    num_pc: int
        sort along the first num_pc principal components
    start_frame: int
        offset of the data with respect to the trajectories (defined below)
    ref: string.
        reference topology for the first trajectory (g-bound). 
    name: string.
        first of the trajetories from which the frames are picked (g-bound). 
        Should be the same as data_g was from.
    out_name: string.
        core part of the name of the output files
    '''
    
    # Remember the index in the simulation (taking into account cutoff)
    oidx = np.arange(len(data))+start_frame

    # Define the MDAnalysis trajectories from where the frames come
    u = mda.Universe("traj/"+ref+".gro","traj/"+name+".xtc")
    a = u.select_atoms('all')

    for evi in range(num_pc):

        # Project the combined data on the principal component
        proj = project_on_pc(data,evi,pca=pca)

        # Sort everything along the projection on th resp. PC
        sort_idx  = np.argsort(proj)
        proj_sort = proj[sort_idx] 
        oidx_sort = oidx[sort_idx]

        with mda.Writer("pca/"+out_name+"_pc"+str(evi)+".xtc", a.n_atoms) as W:
            for i in range(data.shape[0]):
                ts = u.trajectory[oidx_sort[i]]
                W.write(a)
                
                
def sort_trajs_along_common_pc(data_g, data_a, start_frame, ref_g, ref_a, name_g, name_a, out_name):
    '''Sort two trajectories along the 12 highest principal components.
    
    Parameters
    ----------
    data_g: float array.
        Trajectory data [frames,frame_data]
    data_a: float array.
        Trajectory data [frames,frame_data]
    start_frame: int
        offset of the data with respect to the trajectories (defined below)
    ref_g: string.
        reference topology for the first trajectory (g-bound). 
    ref_a: string.
        reference topology for the second trajectory (arr-bound). 
    name_g: string.
        first of the trajetories from which the frames are picked (g-bound). 
        Should be the same as data_g was from.
    name_a: string.
        second of the trajetories from which the frames are picked (arr-bound). 
        Should be the same as data_g was from.
    out_name: string.
        core part of the name of the output files
    '''
    
    # Combine the data
    data = np.concatenate([data_g,data_a],0)
    
    # Remember which simulation the data came frome
    cond = np.concatenate([np.ones(len(data_g)), np.zeros(len(data_a))])

    # Remember the index in the respective simulation (taking into account cutoff)
    oidx = np.concatenate([np.arange(len(data_g))+start_frame, 
                           np.arange(len(data_a))+start_frame])
    
    # Calculate the principal components
    pca = pyemma.coordinates.pca(data,dim=3)

    # Define the MDAnalysis trajectories from where the frames come
    ug = mda.Universe("traj/"+ref_g+".gro","traj/"+name_g+".xtc")
    ua = mda.Universe("traj/"+ref_a+".gro","traj/"+name_a+".xtc")

    ag = ug.select_atoms('all')
    aa = ua.select_atoms('all')

    for evi in range(12):

        # Project the combined data on the principal component
        proj = project_on_pc(data,evi,pca=pca)

        # Sort everything along the projection on th resp. PC
        sort_idx  = np.argsort(proj)
        proj_sort = proj[sort_idx] 
        cond_sort = cond[sort_idx]
        oidx_sort = oidx[sort_idx]

        with mda.Writer("pca/"+out_name+"_pc"+str(evi)+".xtc", ag.n_atoms) as W:
            for i in range(data.shape[0]):
                if cond_sort[i] == 1: # G-protein bound
                    ts = ug.trajectory[oidx_sort[i]]
                    W.write(ag)
                elif cond_sort[i] == 0: # arrestin bound
                    ts = ua.trajectory[oidx_sort[i]]
                    W.write(aa)
                    
     
    
# --- METHODS FOR CLUSTERING ---
    
    
def obtain_clusters(data,algorithm='kmeans',num_clusters=2,min_dist=12,max_iter=100):
    '''Performs a PyEMMA clustering on the provided data
    
    Parameters
    ----------
    data: float array.
        Trajectory data [frames,frame_data]
    algorithm: string
        The algorithm to use for the clustering. 
        Options: kmeans, rspace. Default: kmeans
    num_clusters: int.
        Number of clusters for k-means clustering
    min_dist: float.
        Minimum distance for regspace clustering
    max_iter (opt.): int.
        Maximum number of iterations.
    '''
    
    # Perform PyEMMA clustering
    assert algorithm in ['kmeans','rspace']
    if algorithm == 'kmeans':
        clusters = pyemma.coordinates.cluster_kmeans(data,num_clusters,max_iter=max_iter)
    elif algorithm == 'rspace':
        clusters = pyemma.coordinates.cluster_regspace(data,min_dist)
    
    # Extract cluster indices
    cl_idx = clusters.get_output()[0][:,0]
    
    # Count and plot
    fig,ax = plt.subplots(1,1,figsize=[4,3])
    c, nc = np.unique(cl_idx,return_counts=True)
    ax.bar(c,nc)
    
    return cl_idx


def obtain_combined_clusters(data_g, data_a, start_frame, label_g, label_a,
                             algorithm='kmeans',num_clusters=2,min_dist=12,max_iter=100,plot=True,saveas=None):
    '''Performs a PyEMMA clustering on a combination of two data sets.
    
    Parameters
    ----------
    data_g: float array.
        Trajectory data [frames,frame_data]
    data_a: float array.
        Trajectory data [frames,frame_data]
    start_frame: int.
        Frame from which the clustering data starts.
    label_g: str.
        Label for the plot.
    label_a: str.
        Label for the plot.
    algorithm: string
        The algorithm to use for the clustering. 
        Options: kmeans, rspace. Default: kmeans
    num_clusters: int.
        Number of clusters for k-means clustering
    min_dist: float.
        Minimum distance for regspace clustering
    max_iter (opt.): int.
        Maximum number of iterations.
    saveas (opt.): str.
        Name of the file to save the plot
    '''
    
    # Combine the data
    data = np.concatenate([data_g,data_a],0)

    # Remember which simulation the data came frome
    cond = np.concatenate([np.ones(len(data_g)), np.zeros(len(data_a))])

    # Remember the index in the respective simulation (taking into account cutoff)
    oidx = np.concatenate([np.arange(len(data_g))+start_frame, np.arange(len(data_a))+start_frame])

    # Perform PyEMMA clustering
    assert algorithm in ['kmeans','rspace']
    if algorithm == 'kmeans':
        clusters = pyemma.coordinates.cluster_kmeans(data,k=num_clusters,max_iter=100)
    elif algorithm == 'rspace':
        clusters = pyemma.coordinates.cluster_regspace(data,min_dist)

    # Extract cluster indices
    cidx = clusters.get_output()[0][:,0]

    # Calculate centroids and total within-cluster sum of square
    centroids = []
    total_wss = 0
    for i in np.unique(cidx):
        # get the data for this cluster
        cluster_data = data[np.where(cidx==i)]
        # calcualte the centroid
        cluster_centroid = np.mean(cluster_data,0)
        centroids.append(cluster_centroid)
        # calculate the within-cluster sum of square
        cluster_wss = np.sum( (cluster_data - cluster_centroid)**2 )
        total_wss += cluster_wss
    
    # Count and plot
    if plot:
        fig,ax = plt.subplots(1,1,figsize=[4,3],sharex=True,dpi=100)
        c, nc   = np.unique(cidx,return_counts=True)
        cg, ncg = np.unique(cidx[cond==1],return_counts=True)
        ca, nca = np.unique(cidx[cond==0],return_counts=True)
        ax.bar(cg-0.15,ncg,0.3,label=label_g)
        ax.bar(ca+0.15,nca,0.3,label=label_a)
        ax.legend()
        ax.set_xticks(c)
        ax.set_xlabel('clusters')
        ax.set_ylabel('population')
        fig.tight_layout()
        if saveas is not None:
            fig.savefig(saveas,dpi=300)
    
    return cidx, cond, oidx, total_wss, centroids


def write_cluster_traj(cluster_idx, top_file, trj_file, out_name, start_frame):
    '''Writes a trajectory into a separate file for each cluster.'''
    
    u = mda.Universe(top_file, trj_file)
    protein = u.select_atoms('all')
    
    num_clusters = np.max(cluster_idx)+1
    
    for nr in range(num_clusters):
        with mda.Writer(out_name+"_c"+str(nr)+".xtc", protein.n_atoms) as W:
            for ts in u.trajectory:
                if ts.frame >= start_frame and cluster_idx[ts.frame-start_frame] == nr: 
                    W.write(protein)
                    
                    