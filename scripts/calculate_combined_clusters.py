import argparse
import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
import scipy as sp
import scipy.stats
import mdshare
import pyemma
from pyemma.util.contexts import settings
import MDAnalysis as mda

# My own functions
from pensa import *




# -------------#
# --- MAIN --- #
# -------------#

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--ref_file_a",   type=str, default='traj/rhodopsin_arrbound_receptor.gro')
    parser.add_argument("--trj_file_a",   type=str, default='traj/rhodopsin_arrbound_receptor.xtc')
    parser.add_argument("--ref_file_b",   type=str, default='traj/rhodopsin_gibound_receptor.gro')
    parser.add_argument("--trj_file_b",   type=str, default='traj/rhodopsin_gibound_receptor.xtc')
    parser.add_argument("--label_a",      type=str, default='Sim A')
    parser.add_argument("--label_b",      type=str, default='Sim B')
    parser.add_argument("--out_plots",    type=str, default='plots/rhodopsin_receptor' )
    parser.add_argument("--out_frames_a", type=str, default='clusters/rhodopsin_arrbound_receptor' )
    parser.add_argument("--out_frames_b", type=str, default='clusters/rhodopsin_gibound_receptor' )
    parser.add_argument("--start_frame",  type=int, default=0 )
    parser.add_argument("--feature_type", type=str, default='bb-torsions' )
    parser.add_argument("--algorithm",    type=str, default='kmeans' )
    parser.add_argument("--max_num_clusters",   type=int, default=12 )
    parser.add_argument("--write_num_clusters", type=int, default=2 )
    parser.add_argument('--write',    dest='write', action='store_true')
    parser.add_argument('--no-write', dest='write', action='store_false')
    parser.add_argument('--wss',      dest='wss',   action='store_true')
    parser.add_argument('--no-wss',   dest='wss',   action='store_false')
    parser.set_defaults(write=True, wss=False)
    args = parser.parse_args()


    # -- FEATURES --

    # Load Features 
    feat_a, data_a = get_features(args.ref_file_a, args.trj_file_a, args.start_frame)
    feat_b, data_b = get_features(args.ref_file_b, args.trj_file_b, args.start_frame)
    # Report dimensions
    print('Feature dimensions from', args.trj_file_a)
    for k in data_a.keys(): 
        print(k, data_a[k].shape)
    print('Feature dimensions from', args.trj_file_b)
    for k in data_b.keys():            
        print(k, data_b[k].shape)


    # -- CLUSTERING THE COMBINED DATA --

    ftype = args.feature_type

    # Calculate clusters from the combined data
    cc = obtain_combined_clusters(data_a[ftype], data_b[ftype], args.start_frame, args.label_a, args.label_b, 
                                  args.algorithm, max_iter=100, num_clusters=args.write_num_clusters, min_dist=12,
                                  saveas=args.out_plots+'_combined-clusters_'+ftype+'.pdf')
    cidx, cond, oidx, wss, centroids = cc
    # Write out frames for each cluster for each simulation
    if args.write:
        write_cluster_traj(cidx[cond==0], args.ref_file_a, args.trj_file_a, 
                           args.out_frames_a, args.start_frame )
        write_cluster_traj(cidx[cond==0], args.ref_file_b, args.trj_file_b, 
                           args.out_frames_b, args.start_frame )

    # -- Within-Sum-of-Squares (WSS) analysis --
    if args.wss:
        print('WSS analysis not yet implemented.')
