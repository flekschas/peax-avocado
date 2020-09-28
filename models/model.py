from avocado import Avocado
import json
import keras
import math
import numpy as np
import os

NUM_WINDOWS_PER_BATCH = 10000 # Random number, 10000 just seem to work fine on my laptop
RESOLUTION = 25 # Base resolution of the Avocado model
LATENT_DIM = 110 # Number of dimensions of the genome embedding
CHROM_SIZES = { # Avocado uses hg19
    "chr1": 249250621,
    "chr2": 243199373,
    "chr3": 198022430,
    "chr4": 191154276,
    "chr5": 180915260,
    "chr6": 171115067,
    "chr7": 159138663,
    "chr8": 146364022,
    "chr9": 141213431,
    "chr10": 135534747,
    "chr11": 135006516,
    "chr12": 133851895,
    "chr13": 115169878,
    "chr14": 107349540,
    "chr15": 102531392,
    "chr16": 90354753,
    "chr17": 81195210,
    "chr18": 78077248,
    "chr19": 59128983,
    "chr20": 63025520,
    "chr21": 48129895,
    "chr22": 51304566,
    "chrX": 155270560,
    "chrY": 59373566,
    "chrM": 16571,
}

def find_index(l: list, q: str):
    q = q.lower()
    try:
        return next(i for i, v in enumerate(l) if v.lower() == q)
    except StopIteration:
        return -1

def get_num_windows(chrom_size, window_size, step_size):
    return np.ceil((chrom_size - window_size) / step_size).astype(int) + 1

class Model(Avocado):
    @property
    def is_data_agnostic(self):
        return True

    def get_genome_embedding(self, pos_from: int = 0, pos_to: int = math.inf):
        pos_from = int(max(0, min(self.n_genomic_positions, pos_from)))
        pos_to = int(max(pos_from, min(self.n_genomic_positions, pos_to)))
        n_genomic_positions = pos_to - pos_from

        genome_embedding = np.empty((
            n_genomic_positions,
            self.n_25bp_factors + self.n_250bp_factors + self.n_5kbp_factors
        ))

        for layer in self.model.layers:
            if layer.name == 'genome_25bp_embedding':
                genome_25bp_embedding = layer.get_weights()[0]
            elif layer.name == 'genome_250bp_embedding':
                genome_250bp_embedding = layer.get_weights()[0]
            elif layer.name == 'genome_5kbp_embedding':
                genome_5kbp_embedding = layer.get_weights()[0]

        n1 = self.n_25bp_factors
        n2 = self.n_25bp_factors + self.n_250bp_factors

        k = 0
        for i in range(pos_from, pos_to):
            genome_embedding[k, :n1] = genome_25bp_embedding[i]
            genome_embedding[k, n1:n2] = genome_250bp_embedding[i // 10]
            genome_embedding[k, n2:] = genome_5kbp_embedding[i // 200]
            k += 1

        return genome_embedding

    def predict_all(
        self,
        window_size: int = None,
        step_size: int = None,
    ):
        encoded_window_size = window_size // RESOLUTION
        encoded_step_size = step_size // RESOLUTION
        encoded_batch_size = (step_size * (NUM_WINDOWS_PER_BATCH - 1) + window_size) // RESOLUTION

        num_windows = get_num_windows(self.chromosome_size, window_size, step_size)
        num_batches = math.ceil(math.ceil(self.chromosome_size / RESOLUTION) / encoded_batch_size)

        embedding = np.zeros((num_windows, LATENT_DIM))

        for i in np.arange(num_batches):
            print(f'Extract batch {i} of {num_batches}:')

            batch_from = i * NUM_WINDOWS_PER_BATCH
            batch_to = min(num_windows, (i + 1) * NUM_WINDOWS_PER_BATCH)
            batch_size = batch_to - batch_from

            encoded_from = i * NUM_WINDOWS_PER_BATCH * encoded_step_size
            encoded_to = encoded_from + encoded_batch_size

            print('  Extract model embeddings... ', end='', flush=True)
            data = self.get_genome_embedding(encoded_from, encoded_to)
            batch = np.zeros((batch_size, LATENT_DIM))
            print('done!', flush=True)

            print('  Aggregate model embeddings... ', end='', flush=True)
            for j in np.arange(batch_size):
                data_from = j * encoded_step_size
                data_to = data_from + encoded_window_size
                batch[j] = data[data_from:data_to, :].mean(axis=0)
            print('done!', flush=True)

            embedding[batch_from:batch_to] = batch

        return embedding

    def predict_locus(
        self,
        start: int = None,
        end: int = None,
    ):
        pos_from = round(start / 25)
        pos_to = round(end / 25)

        return self.get_genome_embedding(pos_from, pos_to).mean(axis=0)


    def predict(
        self,
        chrom: str = None,
        start: int = None,
        end: int = None,
        window_size: int = None,
        step_size: int = None,
    ):
        if chrom != self.chromosome:
            return np.empty()

        if start is not None and end is not None:
            return self.predict_locus(start, end)

        return self.predict_all(window_size, step_size)

    @classmethod
    def load(cls, name):
        with open("{}.json".format(name), "r") as infile:
            d = json.load(infile)

        if 'experiments' in d:
            experiments = d['experiments']
            del d['experiments']
        else:
            experiments = []

        model = cls(**d)

        model.experiments = experiments
        model.model = keras.models.load_model('{}.h5'.format(name))

        _, chromosome = os.path.basename(name).split('-')
        model.chromosome = chromosome
        model.chromosome_size = CHROM_SIZES[chromosome]

        return model
