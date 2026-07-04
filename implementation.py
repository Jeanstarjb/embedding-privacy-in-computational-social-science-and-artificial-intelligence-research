import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np

class DifferentialPrivacyMechanism:
    def __init__(self, epsilon, delta=1e-5):
        self.epsilon = epsilon
        self.delta = delta

    def add_laplace_noise(self, data, sensitivity):
        scale = sensitivity / self.epsilon
        noise = np.random.laplace(0, scale, data.shape)
        return data + noise

    def add_gaussian_noise(self, data, sensitivity):
        sigma = np.sqrt(2 * np.log(1.25 / self.delta)) * sensitivity / self.epsilon
        noise = np.random.normal(0, sigma, data.shape)
        return data + noise

class PrivacyPreservingMLP(nn.Module):
    def __init__(self, input_size, hidden_size, output_size):
        super(PrivacyPreservingMLP, self).__init__()
        self.fc1 = nn.Linear(input_size, hidden_size)
        self.relu = nn.ReLU()
        self.fc2 = nn.Linear(hidden_size, output_size)

    def forward(self, x):
        x = self.fc1(x)
        x = self.relu(x)
        x = self.fc2(x)
        return x

def train_model_with_privacy(model, data, labels, epsilon, sensitivity, epochs=10, lr=0.01):
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.SGD(model.parameters(), lr=lr)
    dp_mechanism = DifferentialPrivacyMechanism(epsilon)

    for epoch in range(epochs):
        model.train()
        optimizer.zero_grad()

        # Add noise to the data for privacy
        noisy_data = torch.tensor(dp_mechanism.add_gaussian_noise(data.numpy(), sensitivity), dtype=torch.float32)

        # Forward pass
        outputs = model(noisy_data)
        loss = criterion(outputs, labels)

        # Backward pass and optimization
        loss.backward()
        optimizer.step()

        print(f"Epoch [{epoch+1}/{epochs}], Loss: {loss.item():.4f}")

if __name__ == '__main__':
    # Dummy data
    np.random.seed(42)
    torch.manual_seed(42)
    input_size = 10
    hidden_size = 5
    output_size = 3
    num_samples = 100

    # Generate random data
    data = torch.tensor(np.random.rand(num_samples, input_size), dtype=torch.float32)
    labels = torch.tensor(np.random.randint(0, output_size, num_samples), dtype=torch.long)

    # Model initialization
    model = PrivacyPreservingMLP(input_size, hidden_size, output_size)

    # Privacy parameters
    epsilon = 1.0
    sensitivity = 1.0

    # Train the model with privacy-preserving mechanism
    train_model_with_privacy(model, data, labels, epsilon, sensitivity)