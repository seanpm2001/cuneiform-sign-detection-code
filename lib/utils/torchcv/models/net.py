import torch
import torch.nn as nn


# this should import a specific architecture for cuneiform sign detection


class FPNSSD(nn.Module):
    num_anchors = 12

    def __init__(self, fpn_model, num_classes):
        super(FPNSSD, self).__init__()
        self.fpn = fpn_model
        self.num_classes = num_classes
        self.loc_head = self._make_head(self.num_anchors * 4)
        self.cls_head = self._make_head(self.num_anchors * self.num_classes)

    def forward(self, x):
        loc_preds = []
        cls_preds = []
        fms = self.fpn(x)
        for fm in fms:
            loc_pred = self.loc_head(fm)
            cls_pred = self.cls_head(fm)
            loc_pred = loc_pred.permute(0, 2, 3, 1).reshape(x.size(0), -1,
                                                            4)  # [N, 9*4,H,W] -> [N,H,W, 9*4] -> [N,H*W*9, 4]
            cls_pred = cls_pred.permute(0, 2, 3, 1).reshape(x.size(0), -1,
                                                            self.num_classes)  # [N,9*NC,H,W] -> [N,H,W,9*NC] -> [N,H*W*9,NC]
            loc_preds.append(loc_pred)
            cls_preds.append(cls_pred)
        return torch.cat(loc_preds, 1), torch.cat(cls_preds, 1)

    def _make_head(self, out_planes):
        layers = []
        for _ in range(4):
            layers.append(nn.Conv2d(256, 256, kernel_size=3, stride=1, padding=1))
            layers.append(nn.ReLU(True))
        layers.append(nn.Conv2d(256, out_planes, kernel_size=3, stride=1, padding=1))
        return nn.Sequential(*layers)

    def freeze_bn(self):
        '''Freeze BatchNorm layers.'''
        for layer in self.modules():
            if isinstance(layer, nn.BatchNorm2d):
                layer.eval()


# def test():
#     net = FPNSSD(21)
#     loc_preds, cls_preds = net(torch.randn(1, 3, 512, 512))
#     print(loc_preds.size(), cls_preds.size())

# test()
