import faiss
import pickle

def make_faiss_idx(fv, idx_path):
    index = faiss.IndexFlatIP(fv.shape[1])
    faiss.normalize_L2(fv)
    index.add(fv)
    faiss.write_index(index, idx_path)
    print(idx_path, "saved!")

def search_faiss(top_k, index, query):
    distance, indices = index.search(query.numpy(), top_k)
    return distance, indices