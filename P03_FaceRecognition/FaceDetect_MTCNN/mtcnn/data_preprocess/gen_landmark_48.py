# coding: utf-8
import os
import cv2
import random
import sys
import numpy as np
import time
REPO_DIR = os.getcwd()
MTCNN_DIR = os.path.join(REPO_DIR, 'P03_FaceRecognition', 'FaceDetect_MTCNN', 'mtcnn')
MTCNN_CORE_DIR = os.path.join(MTCNN_DIR, 'core')
sys.path.append(MTCNN_DIR)
sys.path.append(MTCNN_CORE_DIR)
import core_utils as utils

ROOT_DIR = os.path.dirname(MTCNN_DIR)
prefix_path = os.path.join(ROOT_DIR, 'data_set', 'face_landmark', 'CelebA', 'Img')
traindata_store = os.path.join(ROOT_DIR, 'data_set', 'train')
annotation_file = os.path.join(ROOT_DIR, 'data_set', 'face_landmark', 'CelebA', 'Anno', 'list_face_train_mtcnn_bbx_landmark.txt')
#annotation_file = "./data_set/face_landmark/CNN_FacePoint/train/trainImageList.txt"

def gen_data(anno_file, data_dir, prefix):

    size = 48
    image_id = 0

    landmark_imgs_save_dir = os.path.join(data_dir,"48", "landmark")
    if not os.path.exists(landmark_imgs_save_dir):
        os.makedirs(landmark_imgs_save_dir)

    anno_dir = os.path.join(ROOT_DIR, 'anno_store')
    if not os.path.exists(anno_dir):
        os.makedirs(anno_dir)

    landmark_anno_filename = "landmark_48.txt"
    save_landmark_anno = os.path.join(anno_dir, landmark_anno_filename)

    # print(save_landmark_anno)
    # time.sleep(5)
    f = open(save_landmark_anno, 'w')
    # dstdir = "train_landmark_few"

    with open(anno_file, 'r') as f2:
        annotations = f2.readlines()

    num = len(annotations)
    print("%d total images" % num)

    l_idx =0
    idx = 0
    # image_path bbox landmark(5*2)
    for annotation in annotations:
        # print imgPath

        annotation = annotation.strip().split(' ')

        assert len(annotation)==15,"each line should have 15 element"

        im_path = os.path.join(prefix_path, annotation[0].replace("\\", "/"))

        gt_box = list(map(float, annotation[1:5]))
        # gt_box = [gt_box[0], gt_box[2], gt_box[1], gt_box[3]]


        gt_box = np.array(gt_box, dtype=np.int32)

        landmark = list(map(float, annotation[5:]))
        landmark = np.array(landmark, dtype=np.float)

        img = cv2.imread(im_path)
        assert (img is not None)

        height, width, channel = img.shape
        # crop_face = img[gt_box[1]:gt_box[3]+1, gt_box[0]:gt_box[2]+1]
        # crop_face = cv2.resize(crop_face,(size,size))

        idx = idx + 1
        if idx % 100 == 0:
            print("%d images done, landmark images: %d"%(idx,l_idx))
        # print(im_path)
        # print(gt_box)
        x1, y1, x2, y2 = gt_box
        #print("x1 %d" % x1)
        #print("x2 %d" % x2)
        gt_box[1] = y1
        gt_box[2] = x2
        # time.sleep(5)

        # gt's width
        w = x2 - x1 + 1
        # gt's height
        h = y2 - y1 + 1
        if max(w, h) < 40 or x1 < 0 or y1 < 0:
            continue
        # random shift
        for i in range(10):
            bbox_size = np.random.randint(int(min(w, h) * 0.8), np.ceil(1.25 * max(w, h)))
            delta_x = np.random.randint(-w * 0.2, w * 0.2)
            delta_y = np.random.randint(-h * 0.2, h * 0.2)
            nx1 = max(x1 + w / 2 - bbox_size / 2 + delta_x, 0)
            ny1 = max(y1 + h / 2 - bbox_size / 2 + delta_y, 0)

            nx2 = nx1 + bbox_size
            ny2 = ny1 + bbox_size
            if nx2 > width or ny2 > height:
                continue
            crop_box = np.array([nx1, ny1, nx2, ny2])
            cropped_im = img[int(ny1):int(ny2) + 1, int(nx1):int(nx2) + 1, :]
            resized_im = cv2.resize(cropped_im, (size, size),interpolation=cv2.INTER_LINEAR)

            offset_x1 = (x1 - nx1) / float(bbox_size)
            offset_y1 = (y1 - ny1) / float(bbox_size)
            offset_x2 = (x2 - nx2) / float(bbox_size)
            offset_y2 = (y2 - ny2) / float(bbox_size)

            offset_left_eye_x = (landmark[0] - nx1) / float(bbox_size)
            offset_left_eye_y = (landmark[1] - ny1) / float(bbox_size)

            offset_right_eye_x = (landmark[2] - nx1) / float(bbox_size)
            offset_right_eye_y = (landmark[3] - ny1) / float(bbox_size)

            offset_nose_x = (landmark[4] - nx1) / float(bbox_size)
            offset_nose_y = (landmark[5] - ny1) / float(bbox_size)

            offset_left_mouth_x = (landmark[6] - nx1) / float(bbox_size)
            offset_left_mouth_y = (landmark[7] - ny1) / float(bbox_size)

            offset_right_mouth_x = (landmark[8] - nx1) / float(bbox_size)
            offset_right_mouth_y = (landmark[9] - ny1) / float(bbox_size)


            # cal iou
            iou = utils.IoU(crop_box.astype(np.float), np.expand_dims(gt_box.astype(np.float), 0))
            # print(iou)
            if iou > 0.65:
                save_file = os.path.join(landmark_imgs_save_dir, "%s.jpg" % l_idx)
                cv2.imwrite(save_file, resized_im)

                f.write(save_file + ' -2 %.2f %.2f %.2f %.2f %.2f %.2f %.2f %.2f %.2f %.2f %.2f %.2f %.2f %.2f \n' % \
                (offset_x1, offset_y1, offset_x2, offset_y2, \
                offset_left_eye_x,offset_left_eye_y,offset_right_eye_x,offset_right_eye_y,offset_nose_x,offset_nose_y,offset_left_mouth_x,offset_left_mouth_y,offset_right_mouth_x,offset_right_mouth_y))
                # print(save_file)
                # print(save_landmark_anno)
                l_idx += 1

    f.close()


if __name__ == '__main__':

    gen_data(annotation_file, traindata_store, prefix_path)


