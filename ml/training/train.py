import json
from pathlib import Path
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from torchvision import transforms, datasets, models


ML_DIR = Path(__file__).resolve().parent.parent



# adjusting the image before it enters in model
norm = transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])

train_transform = transforms.Compose([
    transforms.RandomResizedCrop(224, scale=(0.65, 1.0)),
    transforms.RandomHorizontalFlip(),
    transforms.ToTensor(),
    norm
])

val_transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    norm
])


# loading images
train_data = datasets.ImageFolder(ML_DIR / "dataset/train", transform=train_transform)
val_data = datasets.ImageFolder(ML_DIR / "dataset/val", transform=val_transform)

train_loader = DataLoader(train_data, batch_size=15, shuffle=True)
val_loader = DataLoader(val_data, batch_size=15)

classes = train_data.classes
print(f"Classes found: {classes}")


# checking for gpu
device = "mps" if torch.backends.mps.is_available() else "cpu"

# loading and editing model
model = models.efficientnet_b0(weights="DEFAULT")

model.classifier[1] = nn.Linear(model.classifier[1].in_features,len(classes))

# sending model to gpu
model = model.to(device)

# traning
loss_fxn = nn.CrossEntropyLoss(label_smoothing=0.05)
optimizer = torch.optim.AdamW(model.parameters(), lr=0.0001, weight_decay=0.01)

for epoch in range(20):
    model.train()
    for images, labels in train_loader:
        images, labels = images.to(device), labels.to(device)
        optimizer.zero_grad()
        predictions = model(images)
        loss = loss_fxn(predictions, labels)
        loss.backward()
        optimizer.step()
    print(f"Round: {epoch+1} / 20, Loss: {loss.item():.3f}")


# model evaluation
model.eval()
correct = 0
with torch.no_grad():
    for images, labels in val_loader:
        images, labels = images.to(device), labels.to(device)
        correct += (model(images).argmax(1) == labels).sum().item()

print(f"Accuracy: {correct}/{len(val_data)}\n Percentage: {(correct/len(val_data))*100:.1f}%")


#exporting model
model.to("cpu")
torch.onnx.export(
    model,
    torch.randn(1,3,224,224),
    (ML_DIR / "models" / "sharingan_ai.onnx"),
    input_names = ["input"],
    output_names = ["logits"],
    opset_version=17,
    dynamo=False,
    )
with open(ML_DIR / "models" / "classes.json", "w") as f:
    json.dump(classes, f, indent=2)
