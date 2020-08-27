from PIL import Image
import sys
import numpy as np
import torchvision
import torch

from models import AENet


from detector import CelebASpoofDetector

def pretrain(model, state_dict):
    own_state = model.state_dict()

    for name, param in state_dict.items():
        realname = name.replace('module.','')
        if realname in own_state:
            if isinstance(param, torch.nn.Parameter):
                # backwards compatibility for serialized parameters
                param = param.data
            try:
                own_state[realname].copy_(param)
            except:
                print('While copying the parameter named {}, '
                      'whose dimensions in the model are {} and '
                      'whose dimensions in the checkpoint are {}.'
                      .format(realname, own_state[name].size(), param.size()))
                print("But don't worry about it. Continue pretraining.")

class TSNPredictor(CelebASpoofDetector):

    def __init__(self):
        self.num_class = 2
        self.net = AENet(num_classes = self.num_class)
        checkpoint = torch.load('./ckpt_iter.pth.tar')

        pretrain(self.net,checkpoint['state_dict'])

        self.new_width = self.new_height = 224

        self.transform = torchvision.transforms.Compose([
            torchvision.transforms.Resize((self.new_width, self.new_height)),
            torchvision.transforms.ToTensor(),
            ])

        
        self.net.cuda()
        self.net.eval()



    def preprocess_data(self, image):
        processed_data = Image.fromarray(image)
        processed_data = self.transform(processed_data)
        return processed_data

    def eval_image(self, image):
        data = torch.stack(image,dim=0)
        channel = 3
        input_var = data.view(-1, channel, data.size(2), data.size(3)).cuda()
        with torch.no_grad():
            rst = self.net(input_var).detach()
        return rst.reshape(-1, self.num_class)

    def predict(self, images):
        real_data = []
        for image in images:
            data = self.preprocess_data(image)
            real_data.append(data)
        rst = self.eval_image(real_data)
        rst = torch.nn.functional.softmax(rst, dim=1).cpu().numpy().copy()
        probability = np.array(rst)
        return probability
