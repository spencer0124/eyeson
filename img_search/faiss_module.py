import faiss
import os
import pickle

def make_faiss_idx(fv, idx_path):
    index = faiss.IndexFlatL2(fv.shape[1])
    index.add(fv)
    faiss.write_index(index, idx_path)
    return index

def load_or_create_faiss_index(idx_path, fv):
    if os.path.isfile(idx_path):
        idx = faiss.read_index(idx_path)
    else:
        idx = make_faiss_idx(fv, idx_path)
    return idx

def search_faiss(top_k, idx, query_fv):
    D, I = idx.search(query_fv.numpy(), top_k)
    return D, I