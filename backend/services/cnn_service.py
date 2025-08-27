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
#     print('processed', preprocessed_images)

#     with torch.no_grad():
#         feature_vectors = [feature_extractor(img_tensor) for img_tensor in preprocessed_images]

#     fv_tensor = torch.vstack(feature_vectors)
#     fv_np = fv_tensor.numpy()

#     with open(pkl_path, 'wb') as f:
#         pickle.dump(fv_np, f)
    
#     return fv_np

# def preprocess_query(image_path):
#     query = preprocess_image(image_path)
#     print('query img', type(query), query)
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
from PIL import Image
import cv2
import numpy as np
import pickle
import os
from transformers import AutoImageProcessor, AutoModel

# 모델 불러오기 (DINOv2로 수정)
pretrained_model_name = "facebook/dinov2-vitg14-pretrain"
processor = AutoImageProcessor.from_pretrained(pretrained_model_name)

model = AutoModel.from_pretrained(
    pretrained_model_name,
    device_map="auto",
)

# 이미지 전처리 함수 (기존 코드와 동일)
def preprocess_image(image):
    if isinstance(image, str):
        image = Image.open(image).convert("RGB")
    elif isinstance(image, np.ndarray):
        image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    elif not isinstance(image, Image.Image):
        raise ValueError(f"Unsupported image type: {type(image)}")
    
    return image

# --- 수정된 create_fv 함수 ---
def create_fv(s3_file_list, download_image_func, pkl_path):
    preprocessed_images = [
        preprocess_image(download_image_func(s3_key))
        for s3_key in s3_file_list if s3_key[6:10] != "temp"
    ]
    
    # 1. 모든 이미지를 한 번에 전처리
    # Hugging Face processor는 이미지 리스트를 받아 한 번에 처리하는 데 최적화되어 있습니다.
    inputs = processor(images=preprocessed_images, return_tensors="pt")
    
    # 2. 전처리된 데이터를 GPU로 이동
    inputs = {k: v.to(model.device) for k, v in inputs.items()}
    
    with torch.no_grad():
        # 3. 모델에 전처리된 데이터 전달
        # model(**inputs)는 딕셔너리 형태로 출력을 반환합니다.
        outputs = model(**inputs)

    # 4. 출력에서 CLS 토큰(첫 번째 토큰)의 feature vector를 추출
    # outputs.last_hidden_state의 shape는 (배치 크기, 토큰 수, 차원) 입니다.
    # 첫 번째 토큰([:, 0, :])이 CLS 토큰입니다.
    feature_vectors = outputs.last_hidden_state[:, 0, :]
    
    # 5. 정규화 및 numpy 변환 (기존 코드와 동일)
    fv_tensor = feature_vectors / feature_vectors.norm(dim=1, keepdim=True)
    fv_np = fv_tensor.cpu().numpy()
    print('fv_np shape', fv_np.shape)

    with open(pkl_path, 'wb') as f:
        pickle.dump(fv_np, f)
    
    return fv_np

# --- 수정된 preprocess_query 함수 ---
def preprocess_query(image_path):
    query = preprocess_image(image_path)
    
    # 1. 단일 이미지를 전처리
    inputs = processor(images=query, return_tensors="pt")

    # 2. 전처리된 데이터를 GPU로 이동
    inputs = {k: v.to(model.device) for k, v in inputs.items()}

    with torch.no_grad():
        # 3. 모델에 전처리된 데이터 전달
        outputs = model(**inputs)

    # 4. CLS 토큰 추출
    query_fv = outputs.last_hidden_state[:, 0, :]

    # 5. 정규화 및 numpy 변환 (기존 코드와 동일)
    query_fv = query_fv / query_fv.norm()
    return query_fv.cpu().numpy()

# load_or_create_feature_vectors 함수는 수정할 필요 없음
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