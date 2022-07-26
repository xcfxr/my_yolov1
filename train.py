import os

import numpy as np

os.environ["CUDA_VISIBLE_DEVICES"] = "0"
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
import torchvision.transforms as transforms
from torchvision import models
from yoloLoss import yoloLoss
from myModel import resnet50
from dataset import yoloDataset

use_gpu = torch.cuda.is_available()
learning_rate = 0.001
num_epochs = 50
batch_size = 8
use_resnet = True
if use_resnet:
    resnet = models.resnet50(pretrained=True)
    net = resnet50()
    dd = net.state_dict()
    for k, v in resnet.state_dict().items():
        if k in dd.keys() and not k.startswith('fc'):
            print('yes')
            dd[k] = v
    net.load_state_dict(dd)
print('cuda', torch.cuda.current_device(), torch.cuda.device_count())
criterion = yoloLoss(7, 2, 5, 0.5)
if use_gpu:
    net.cuda()
net.train()

params = []
params_dict = dict(net.named_parameters())
for key,value in params_dict.items():
    if key.startswith('features'):
        params += [{'params':[value],'lr':learning_rate*1}]
    else:
        params += [{'params':[value],'lr':learning_rate}]

optimizer = torch.optim.SGD(params, lr=learning_rate, momentum=0.9, weight_decay=5e-4)
root = r'D:\BaiduNetdiskDownload\VOC07+12+test\VOCdevkit\VOC2007\JPEGImages\\'
train_dataset = yoloDataset(root=root, list_file='trainval.txt', train=True, transform=[transforms.ToTensor()])
train_loader = DataLoader(train_dataset,batch_size=batch_size,shuffle=True,num_workers=0)
test_dataset = yoloDataset(root=root, list_file='test.txt', train=False, transform=[transforms.ToTensor()])
test_loader = DataLoader(test_dataset,batch_size=batch_size,shuffle=False,num_workers=0)
print('the dataset has %d images' % (len(train_dataset)))
print('the batch_size is %d' % (batch_size))
logfile = open('log.txt', 'w')

num_iter = 0
best_test_loss = np.Inf
for epoch in range(num_epochs):
    net.train()
    if epoch == 30:
        learning_rate = 0.0001
    if epoch == 40:
        learning_rate = 0.00001
    for params in optimizer.param_groups:
        params['lr'] = learning_rate
    print('\n\nStarting epoch %d / %d' % (epoch+1, num_epochs))
    print('Learning Rate for this epoch: {}'.format(learning_rate))
    total_loss = 0

    for i, (images, target) in enumerate(train_loader):
        images, target = images.cuda(), target.cuda()
        pred = net(images)
        loss = criterion(pred, target)
        total_loss += loss.item()
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        if (i+1) % 5 == 0:
            print('Epoch [%d/%d], Iter [%d/%d] Loss: %.4f, average_loss:%.4f'
                  %(epoch+1, num_epochs, i+1, len(train_loader), loss.item(), total_loss / (i+1)))
            num_iter += 1
        validation_loss = 0.0
        net.eval()
        for i, (images, target) in enumerate(test_loader):
            images, target = images.cuda(), target.cuda()
            pred = net(images)
            loss = criterion(pred, target)
            validation_loss += loss.item()
        validation_loss /= len(test_loader)

        if best_test_loss > validation_loss:
            best_test_loss = validation_loss
            print('get best test loss %.5f' % best_test_loss)
            torch.save(net.state_dict(), 'best.pth')
        logfile.writelines(str(epoch) + '\t' + str(validation_loss) + '\n')
        logfile.flush()
        torch.save(net.state_dict(), 'yolo.pth')
