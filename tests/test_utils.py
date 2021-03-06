"""Tests for utility functions"""

from chop.utils import closure
import torch
from torch import nn
from chop import utils


# Set up random regression problem
alpha = 1.
n_samples, n_features = 20, 15
X = torch.rand((n_samples, n_features))
w = torch.rand(n_features)
w = alpha * w / sum(abs(w))
y = X.mv(w)
# Logistic regression: \|y\|_\infty <= 1
y = abs(y / y.max())

tol = 4e-3

batch_size = 20
d1 = 10
d2 = 5
x0 = torch.ones(batch_size, d1, d2)

def test_jacobian_batch():
    def loss(x):
        return (x.view(x.size(0), -1) ** 2).sum(-1)

    val, jac = utils.get_func_and_jac(loss, x0)

    assert jac.eq(2 * x0).all()


def test_jacobian_single_sample():
    def loss(x):
        return (x ** 2).sum()

    x0 = torch.rand(1, d1, d2)
    val, jac = utils.get_func_and_jac(loss, x0)

def test_closure():

    @utils.closure
    def loss(x):
        return (x.view(x.size(0), -1) ** 2).sum(-1)

    val, grad = loss(x0)
    assert val.eq(torch.ones(batch_size) * (d1 * d2)).all()
    assert grad.eq(2 * x0).all()


def test_init_lipschitz():
    criterion = nn.MSELoss(reduction='none')

    @closure
    def loss_fun(X):
        return criterion(X.mv(w), y)

    L = utils.init_lipschitz(loss_fun, X.detach().clone().requires_grad_(True))
    print(L)

