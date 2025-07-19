# import torch
# import torchvision.transforms as transforms
# import torchvision.models as models
# import cv2
# import pickle
# import os
# from PIL import Image
# import numpy as np

# # VGG16 모델 설정
# class VGG16_FeatureExtractor(torch.nn.Module):
#     def __init__(self, original_model):
#         super(VGG16_FeatureExtractor, self).__init__()
#         self.features = original_model.features
#         self.avgpool = original_model.avgpool
#         self.fc6 = original_model.classifier[0]
#         self.relu = original_model.classifier[1]
#         self.dropout = original_model.classifier[2]
#         self.fc7 = original_model.classifier[3]

#     def forward(self, x):
#         x = self.features(x)
#         x = self.avgpool(x)
#         x = torch.flatten(x, 1)
#         x = self.fc6(x)
#         x = self.relu(x)
#         x = self.dropout(x)
#         x = self.fc7(x)
#         return x

# vgg16 = models.vgg16(pretrained=True)
# feature_extractor = VGG16_FeatureExtractor(vgg16)

# def preprocess_image(image):
#     if isinstance(image, str):
#         img = cv2.imread(image)
#     elif isinstance(image, Image.Image):
#         img = np.array(image)
#         img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
#     else:
#         raise ValueError(f"Unsupported image type: {type(image)}")
    
#     img = cv2.resize(img, (256,256))
#     center_crop_size = 224
#     h, w, _ = img.shape
#     startx = w//2 - (center_crop_size//2)
#     starty = h//2 - (center_crop_size//2)
#     img = img[starty:starty+center_crop_size, startx:startx+center_crop_size]

#     img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
#     img = transforms.ToTensor()(img)
#     img = transforms.Normalize(mean = [0.485, 0.456, 0.406], std = [0.229, 0.224, 0.225])(img)
#     img = img.unsqueeze(0)
#     return img

# def create_fv(s3_file_list, download_image_func, pkl_path):
#     preprocessed_images = [preprocess_image(download_image_func(s3_key)) for s3_key in s3_file_list if s3_key[6:10] != "temp"]

#     with torch.no_grad():
#         feature_vectors = [feature_extractor(img_tensor) for img_tensor in preprocessed_images]

#     fv_tensor = torch.vstack(feature_vectors)
#     fv_np = fv_tensor.numpy()

#     with open(pkl_path, 'wb') as f:
#         pickle.dump(fv_np, f)
    
#     return fv_np

# def preprocess_query(image_path):
#     query = preprocess_image(image_path)
#     with torch.no_grad():
#         query_fv = feature_extractor(query)
#     return query_fv

# def load_or_create_feature_vectors(fv_pkl_path, s3_file_list, download_image_func):
#     if os.path.isfile(fv_pkl_path):
#         with open(fv_pkl_path, 'rb') as file:
#             fv = pickle.load(file)
#     else:
#         feature_dir = os.path.dirname(fv_pkl_path)
#         if not os.path.exists(feature_dir):
#             os.makedirs(feature_dir)
#             print(f"Directory {feature_dir} created.")
            
#         fv = create_fv(s3_file_list, download_image_func, fv_pkl_path)
#     return fv

import torch
import clip
from PIL import Image
import cv2
import numpy as np
import pickle
import os

device = "cuda" if torch.cuda.is_available() else "cpu"

# CLIP 모델 불러오기
clip_model, clip_preprocess = clip.load("ViT-B/32", device=device)

# 이미지 전처리 함수
def preprocess_image(image):
    if isinstance(image, str):
        image = Image.open(image).convert("RGB")
    elif isinstance(image, np.ndarray):
        image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    elif not isinstance(image, Image.Image):
        raise ValueError(f"Unsupported image type: {type(image)}")
    
    return clip_preprocess(image).unsqueeze(0).to(device)

# feature vector 생성 함수
def create_fv(s3_file_list, download_image_func, pkl_path):
    preprocessed_images = [
        preprocess_image(download_image_func(s3_key))
        for s3_key in s3_file_list if s3_key[6:10] != "temp"
    ]

    with torch.no_grad():
        feature_vectors = [clip_model.encode_image(img_tensor) for img_tensor in preprocessed_images]

    fv_tensor = torch.vstack(feature_vectors)
    fv_tensor = fv_tensor / fv_tensor.norm(dim=1, keepdim=True)  # 정규화 (cosine similarity용)
    fv_np = fv_tensor.cpu().numpy()

    with open(pkl_path, 'wb') as f:
        pickle.dump(fv_np, f)
    
    return fv_np

# 쿼리 이미지 처리
def preprocess_query(image_path):
    query = preprocess_image(image_path)
    with torch.no_grad():
        query_fv = clip_model.encode_image(query)
        query_fv = query_fv / query_fv.norm()  # 정규화
    return query_fv.cpu().numpy()

# 피처 벡터 불러오거나 생성
def load_or_create_feature_vectors(fv_pkl_path, s3_file_list, download_image_func):
    if os.path.isfile(fv_pkl_path):
        with open(fv_pkl_path, 'rb') as file:
            fv = pickle.load(file)
    else:
        feature_dir = os.path.dirname(fv_pkl_path)
        if not os.path.exists(feature_dir):
            os.makedirs(feature_dir)
            print(f"Directory {feature_dir} created.")
            
        fv = create_fv(s3_file_list, download_image_func, fv_pkl_path)
    return fv