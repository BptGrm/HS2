import numpy as np
from matplotlib import pyplot as plt
from probes.readUtils import read_flat
from probes.readUtils import openHDF5file, getHDF5params
from probes.readUtils import readHDF5t_100, readHDF5t_101
from sklearn.neighbors import KDTree


class NeuralProbe(object):
    def __init__(self, num_channels, spike_delay,
                 spike_peak_duration, noise_duration, noise_amp_percent,
                 fps, positions_file_path, neighbors_file_path=None,
                 neighborhood_radius=None):
        self.num_channels = num_channels
        self.spike_delay = spike_delay
        self.spike_peak_duration = spike_peak_duration
        self.noise_duration = noise_duration
        self.noise_amp_percent = noise_amp_percent
        self.fps = fps
        self.positions_file_path = positions_file_path
        self.neighbors_file_path = neighbors_file_path

        self.loadPositions(positions_file_path)
        if neighbors_file_path is not None:
            self.loadNeighbors(neighbors_file_path)
        else:
            self.computeNeighbors(neighborhood_radius)

    # Load in neighbor and positions files
    def loadNeighbors(self, neighbors_file_path):
        neighbor_file = open(neighbors_file_path, 'r')
        neighbors = []
        for neighbor in neighbor_file.readlines():
            neighbors.append(np.array(neighbor[:-2].split(',')).astype(int))
        neighbor_file.close()
        # assert len(neighbors) == len(pos)
        self.num_recording_channels = len(neighbors)
        self.neighbors = neighbors
        self.max_neighbors = max([len(n) for n in neighbors])

    def computeNeighbors(self, radius):
        tree = KDTree(self.positions)
        self.neighbors = list(tree.query_radius(self.positions, r=radius))
        return self.neighbors

    def loadPositions(self, positions_file_path):
        position_file = open(positions_file_path, 'r')
        positions = []
        for position in position_file.readlines():
            positions.append(np.array(position[:-2].split(',')).astype(int))
        self.positions = np.asarray(positions)
        position_file.close()

    # Show visualization of probe
    def show(self, show_neighbors=[10], figwidth=3):
        xmax, ymax = self.positions.max(0)
        xmin, ymin = self.positions.min(0)
        ratio = ymax/xmax
        plt.figure(figsize=(figwidth, figwidth*ratio))
        for ch in show_neighbors:
            for neighbor in self.neighbors[ch]:
                plt.plot([self.positions[ch, 0], self.positions[neighbor, 0]],
                         [self.positions[ch, 1], self.positions[neighbor, 1]],
                         '--k', alpha=.7)
        plt.scatter(*self.positions.T)
        for i, pos in enumerate(self.positions):
            plt.annotate(i, pos)
        plt.ylim([0, ymax+ymin])
        plt.xlim([0, xmax+xmin])

    def Read(self, t0, t1):
        raise NotImplementedError("The Read function is not implemented for \
            this probe")


class NeuroPixel(NeuralProbe):
    def __init__(self, data_file_path, fps=30000):
        # can also use computeNeighbors(radius=78.)
        NeuralProbe.__init__(
            self, num_channels=385, spike_delay=5,
            spike_peak_duration=5, noise_duration=2,
            noise_amp_percent=.95, fps=fps,
            positions_file_path='probes/positions_neuropixel',
            neighbors_file_path='probes/neighbormatrix_neuropixel')
        self.d = np.memmap(data_file_path, dtype=np.int16, mode='r')
        assert len(self.d)/self.num_channels == len(self.d)//self.num_channels,\
            'Data not multiple of channel number'
        self.nFrames = len(self.d)//self.num_channels

    def Read(self, t0, t1):
        return read_flat(self.d, t0, t1, self.num_channels)


class BioCam(NeuralProbe):
    def __init__(self, data_file_path, fps=0):
        # can also use computeNeighbors(radius=2.)
        NeuralProbe.__init__(self, num_channels=None, spike_delay=5,
                             spike_peak_duration=5, noise_duration=2,
                             noise_amp_percent=.95, fps=fps,
                             positions_file_path='probes/positions_biocam',
                             neighbors_file_path='probes/neighbormatrix_biocam')
        self.d = openHDF5file(data_file_path)
        self.nFrames, sfd, nRecCh, chIndices, file_format = getHDF5params(
            self.d)
        self.num_channels = nRecCh
        assert self.num_recording_channels == self.num_channels
        if file_format == 100:
            self.read_function = readHDF5t_100
        else:
            self.read_function = readHDF5t_101

    def Read(self, t0, t1):
        return self.read_function(self.d, t0, t1, self.num_channels)