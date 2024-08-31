import torch
import torchvision.models as models
import torchvision.transforms as transforms
import cv2
import numpy as np
import os
import pickle

# vgg16의 마지막 layer feature 값 불러오기 위함
class VGG16_FeatureExtractor(torch.nn.Module):
    def __init__(self, original_model):
        super(VGG16_FeatureExtractor, self).__init__()
        self.features = original_model.features
        self.avgpool = original_model.avgpool
        self.fc6 = original_model.classifier[0]
        self.relu = original_model.classifier[1]
        self.dropout = original_model.classifier[2]
        self.fc7 = original_model.classifier[3]

    def forward(self, x):
        x = self.features(x)
        x = self.avgpool(x)
        x = torch.flatten(x, 1)
        x = self.fc6(x)
        x = self.relu(x)
        x = self.dropout(x)
        x = self.fc7(x)
        return x

# 이미지를 preprocessing (size, normalize)    
def preprocess_image(image_path):
    #print('path', image_path)
    img = cv2.imread(image_path)
    img = cv2.resize(img, (256,256))
    center_crop_size = 224
    h, w, _ = img.shape
    startx = w//2 - (center_crop_size//2)
    starty = h//2 - (center_crop_size//2)
    img = img[starty:starty+center_crop_size, startx:startx+center_crop_size]

    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = transforms.ToTensor()(img)
    img = transforms.Normalize(mean = [0.485, 0.456, 0.406], std = [0.229, 0.224, 0.225])(img)
    img = img.unsqueeze(0)
    return img

def load_images_from_folder(folder_path):
    images = []
    #print('listdir', os.listdir(folder_path))
    filetype = ['jpg','JPG','png','PNG']
    file_list = sorted([i for i in os.listdir(folder_path) if (i[-3:] in filetype)])
    #print('filelist', file_list)
    for filename in file_list:
        img_path = os.path.join(folder_path, filename)
        images.append(preprocess_image(img_path))
    return images

def save_as_pkl(features, pickle_path):
    with open(pickle_path, 'wb') as f:
        pickle.dump(features, f)

vgg16 = models.vgg16(pretrained = True)
feature_extractor = VGG16_FeatureExtractor(vgg16)

def create_fv(img_folder_path, pkl_path):
    preprocessed_images = load_images_from_folder(img_folder_path)

    with torch.no_grad():
        feature_vectors = [feature_extractor(img_tensor) for img_tensor in preprocessed_images]

    fv_tensor = torch.vstack(feature_vectors)
    fv_np = fv_tensor.numpy()

    save_as_pkl(fv_np, pkl_path)
    print('feature vector saved as',pkl_path)

    return fv_np

def preprocess_query(query_path):
    query = preprocess_image(query_path)
    with torch.no_grad():
        query_fv = feature_extractor(query)
    return query_fv