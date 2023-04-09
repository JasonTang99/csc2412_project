import torch
import torch.nn as nn
import torch.nn.functional as F

from models import Discriminator

# Given parameter clip bounds c_p, compute maximal ReLU gradient bounds c_g
def compute_ReLU_bounds(model, c_p, input_size=(784,), input_bounds=1.0, B_sigma_p=1.0):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    sample = torch.ones(input_size[0]).to(device) * input_bounds
    B_sigma = 0.0
    sum_mk_mkp1 = 0
    skip_first = True

    for layer in model.modules():
        if isinstance(layer, nn.Linear):
            W = torch.ones_like(layer.weight) * c_p
            sample = W @ sample
            
            B_sigma = max(B_sigma, sample.max().detach().item())
            
            if skip_first:
                skip_first = False
            else:
                sum_mk_mkp1 += W.shape[0] * W.shape[1]
    
    c_g = 2 * c_p * B_sigma * (B_sigma_p ** 2) * sum_mk_mkp1
    print("B_sigma", B_sigma)
    print("sum_mk_mkp1", sum_mk_mkp1)
    print("c_g", c_g)
    return c_g

# Given parameter clip bounds c_p, compute maximal Tanh gradient bounds c_g
def compute_Tanh_bounds(model, c_p, input_size=(784,), input_bounds=1.0, B_sigma_p=1.0):
    B_sigma = 1.0
    sum_mk_mkp1 = 0
    skip_first = True

    for layer in model.modules():
        if isinstance(layer, nn.Linear):
            if skip_first:
                skip_first = False
            else:
                sum_mk_mkp1 += layer.weight.shape[0] * layer.weight.shape[1]
    
    c_g = 2 * c_p * B_sigma * (B_sigma_p ** 2) * sum_mk_mkp1
    print("B_sigma", B_sigma)
    print("sum_mk_mkp1", sum_mk_mkp1)
    print("c_g", c_g)
    return c_g


if __name__ == "__main__":
    # Test bounds
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    c_p = 0.01

    netD = Discriminator([16, 12], input_size=784).to(device)
    compute_ReLU_bounds(netD, c_p)

    netD = Discriminator([16, 12], input_size=784, activation=nn.Tanh()).to(device)
    compute_Tanh_bounds(netD, c_p)