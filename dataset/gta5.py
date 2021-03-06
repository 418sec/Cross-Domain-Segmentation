from dataset.base_dataset import BaseDataset
import os.path as osp
from dataset.data_transform import *
from torch.utils import data
import matplotlib.pyplot as plt


class GTAVDataset(BaseDataset):
    def __init__(self, root, list_path, max_iters=None, crop_size=(321, 321),
                 mean=(0.485, 0.456, 0.406), std=(0.229, 0.224, 0.225), set='train', ignore_label=255):
        super().__init__(root, list_path, max_iters, crop_size, mean, std, set)
        self.ignore_label = ignore_label
        self.id_to_trainid = {7: 0, 8: 1, 11: 2, 12: 3, 13: 4, 17: 5,
                              19: 6, 20: 7, 21: 8, 22: 9, 23: 10, 24: 11, 25: 12,
                              26: 13, 27: 14, 28: 15, 31: 16, 32: 17, 33: 18}

    def __len__(self):
        return len(self.data)

    def __getitem__(self, item):
        datafiles = self.data[item]
        example = {}
        example["image"] = Image.open(datafiles["image"]).convert('RGB')
        example["label"] = Image.open(datafiles["label"])
        result = self.augment(example)

        # re-assign labels
        label_copy = 255 * np.ones(result["label"].shape, dtype=np.float32)
        for k, v in self.id_to_trainid.items():
            label_copy[result["label"] == k] = v
        result["label"] = label_copy.copy()

        return result["image"].transpose(2, 0, 1), result["label"]

    def augment(self, example):
        composed_transform = Compose([
            Resize(self.crop_size[0], self.crop_size[1]),
            Normalize(mean=self.mean, std=self.std),
            # ToTensor()
        ])
        return composed_transform(example)

    def load_image_and_label(self):
        file = []
        for id in self.img_ids:
            image = osp.join(self.root, "images/%s" % id)
            label = osp.join(self.root, "labels/%s" % id)
            file.append({
                "image": image,
                "label": label
            })
        return file


if __name__ == '__main__':
    cityscapes_dataset = GTAVDataset("/media/sdb/duckie/dataset/GTAV",
                                     list_path="./gta5_list/train.txt")
    trainloader = data.DataLoader(cityscapes_dataset, batch_size=4)

    for i, data in enumerate(trainloader):
        imgs, labels = data
        if i == 0:
            img0 = imgs[0]
            img0 = img0.numpy()
            img0 = img0.transpose(1, 2, 0)

            img0 *= (0.229, 0.224, 0.225)
            img0 += (0.485, 0.456, 0.406)
            img0 *= 255.0
            img0 = img0.astype(np.uint8)

            plt.imshow(img0)
            plt.show()
            break
