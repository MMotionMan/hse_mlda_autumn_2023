# -*- coding: utf-8 -*-
"""hw3_kirichenko_mlda.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1ZR8iQbzYGPgcdFWVMOrnvuKoDG2mfVcm
"""

from scipy import sparse
from sklearn.cluster import DBSCAN
import numpy as np
from tqdm import tqdm
from sklearn.decomposition import TruncatedSVD
from sklearn.preprocessing import StandardScaler

!pip install umap

from scipy import sparse

path = '/kaggle/input/hw3-mlda/train.npz'

data = sparse.load_npz(path)

data.shape

tsvd = TruncatedSVD(n_components=10000)
data = tsvd.fit_transform(data)

# scaler = StandardScaler()
# data = scaler.fit_transform(data)

import torch
from torch import nn, optim
from torch.utils.data import TensorDataset, DataLoader, Dataset
import numpy as np
from matplotlib import pyplot as plt
from sklearn.preprocessing import MinMaxScaler

"""**Reduced dimensions with AutoEncoder**

Не хватает оперативной памяти, чтобы полностью снизить размерность при помощи автоэнкодера. Возможно не получается набрать качества из-за плохого качества снижения размерности при помощи TruncatedSVD
"""

class Autoencoder(nn.Module):

    def __init__(self, in_shape, enc_shape):
        super(Autoencoder, self).__init__()

        self.encode = nn.Sequential(
            nn.Linear(in_shape, 5000),
            nn.ReLU(),
            nn.Linear(5000, 2048),
            nn.BatchNorm1d(num_features=2048),
            nn.ReLU(),
            nn.Linear(2048, 1024),
            nn.ReLU(),
            nn.Linear(1024, 512),
            nn.BatchNorm1d(num_features=512),
            nn.ReLU(),
            nn.Linear(512, 256),
            nn.BatchNorm1d(num_features=256),
            nn.ReLU(),
            nn.Linear(256, enc_shape),
        )

        self.decode = nn.Sequential(
            nn.Linear(enc_shape, 256),
            nn.BatchNorm1d(num_features=256),
            nn.ReLU(),
            nn.Linear(256, 512),
            nn.BatchNorm1d(num_features=512),
            nn.ReLU(),
            nn.Linear(512, 1024),
            nn.ReLU(),
            nn.Linear(1024, 2048),
            nn.BatchNorm1d(num_features=2048),
            nn.ReLU(),
            nn.Linear(2048, 5000),
            nn.ReLU(),
            nn.Linear(5000, in_shape),
        )

    def forward(self, x):
        x = self.encode(x)
        x = self.decode(x)
        return x

in_shape = data.shape[1]

outp_shape = 128

print(f'input shape: {in_shape}\noutput shape: {outp_shape}')

device = ('cuda' if torch.cuda.is_available() else 'cpu')

model = Autoencoder(in_shape, outp_shape).to(device)
loss_function = torch.nn.MSELoss()
optimizer = optim.Adam(model.parameters(), lr=1e-5, weight_decay=1e-8)

from torch.utils.data import Dataset, DataLoader

class DataBuilder(Dataset):
    def __init__(self, data):
        self.x = data.astype(np.float32)
        self.x = torch.from_numpy(self.x).to(device)
        self.len=self.x.shape[0]
    def __getitem__(self,index):
        return self.x[index]
    def __len__(self):
        return self.len

data_set=DataBuilder(data)
trainloader=DataLoader(dataset=data_set, batch_size=256)

for batch_idx, data in enumerate(trainloader):
    print(data)
    break

from tqdm import tqdm

def train(epoch):
    loss_function = nn.MSELoss()
    model.train()
    train_loss = 0
    for batch_idx, data in enumerate(trainloader):
        data = data.to(device)
        optimizer.zero_grad()
        recon_batch = model(data)
        loss = loss_function(recon_batch, data)
        loss.backward()
        train_loss += loss.item()
        optimizer.step()

    if epoch % 20 == 0:
        print('====> Epoch: {} Average loss: {:.4f}'.format(
            epoch, train_loss / len(trainloader.dataset)))
        train_losses.append(train_loss / len(trainloader.dataset))

epochs = 1000

val_losses = []
train_losses = []

for epoch in range(1, epochs + 1):
    train(epoch)

outp_emb = []
with torch.no_grad():
    for i, (data) in enumerate(trainloader):
        data = data.to(device)
        outp_emb.append(model.encode(data))
        result_emb = torch.cat(outp_emb, dim=0)

result_emb = result_emb.cpu().numpy()



result_emb.shape

"""**AgglomerativeClustering**"""

from sklearn.cluster import AgglomerativeClustering
from tqdm import tqdm
from time import time

subm = []

for linkage in tqdm(['ward', 'average', 'complete', 'single']):
    clustering = AgglomerativeClustering(linkage=linkage, n_clusters=3)
    clustering = clustering.fit(reduced_embedding)
    subm.append(clustering.labels_)

np.unique(subm[0], return_counts=True)

np.unique(subm[0], return_counts=True)

"""**end clust**"""

!pip install umap

from umap.umap_ import UMAP

reducer = UMAP(n_components=64)
reduced_embedding = reducer.fit_transform(result_emb)

np.array(reduced_embedding).shape

!pip install hdbscan

import hdbscan

labels = hdbscan.HDBSCAN(algorithm='best', alpha=1.0, approx_min_span_tree=True,
    gen_min_span_tree=False, leaf_size=40,
    metric='minkowski', min_cluster_size=3500, min_samples=1000, p=1).fit_predict(reduced_embedding)

np.unique(labels)

import pandas as pd



idx = []
label = []
for i in range(len(subm[0])):
    idx.append(i)
    label.append(subm[0][i])

df = pd.DataFrame({'ID': idx, 'TARGET': label})
df.to_csv(f'subm_kirichenko_scaled_640.csv', index=False)

"""**Spectral Clustering**"""

from sklearn.cluster import SpectralClustering

from scipy import sparse

path = '/kaggle/input/hw3-mlda/train.npz'

data = sparse.load_npz(path)

tsvd = TruncatedSVD(n_components=15000)
data = tsvd.fit_transform(data)

data

clustering = SpectralClustering(n_clusters=3)

labels = clustering.fit_predict(data)

labels

labels

import pandas as pd

df = pd.DataFrame({'ID': [i for i in range(len(labels))], 'TARGET': labels})
df.to_csv(f'subm_kirichenko_scaled_lastTochnoReduced.csv', index=False)

data

"""**Reduce dimensions with UMAP and SpectarlClustering**"""

from scipy import sparse

path = '/kaggle/input/hw3-mlda/train.npz'

data = sparse.load_npz(path)

from umap.umap_ import UMAP

reducer = UMAP(n_components=10000)
reduced_embedding = reducer.fit_transform(data)

clustering = SpectralClustering(n_clusters=3)

labels = clustering.fit_predict(reduced_embedding)