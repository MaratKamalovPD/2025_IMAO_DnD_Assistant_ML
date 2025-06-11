import torch

def test_cuda():
    print("PyTorch version:", torch.__version__)
    print("CUDA available:", torch.cuda.is_available())

    if torch.cuda.is_available():
        print("GPU name:", torch.cuda.get_device_name(0))
        print("CUDA version:", torch.version.cuda)
        print("Current device:", torch.cuda.current_device())
        print("Device count:", torch.cuda.device_count())
    else:
        print("❌ CUDA не доступен. Проверь установку драйвера и библиотеки.")

test_cuda()
