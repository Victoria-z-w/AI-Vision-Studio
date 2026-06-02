FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 libglib2.0-0 libsm6 libxext6 libxrender-dev libgomp1 curl \
    && rm -rf /var/lib/apt/lists/*

COPY . .

# Default: CPU-only inference (onnxruntime + paddlepaddle CPU).
# For GPU support, build with:

#   docker compose -f docker-compose.yml -f docker-compose.gpu.yml up -d --build
ARG PIP_EXTRAS=".[dev,cpu]"

# ── cuDNN for PaddlePaddle GPU (PyTorch's bundled cuDNN is incompatible) ──
RUN if echo "${PIP_EXTRAS}" | grep -q "gpu"; then \
      apt-get update && apt-get install -y --no-install-recommends \
      wget ca-certificates && \
      wget -q "https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/cuda-keyring_1.1-1_all.deb" \
      -O /tmp/cuda-keyring.deb && \
      dpkg -i /tmp/cuda-keyring.deb && \
      sed -i 's/^deb \[/deb [trusted=yes /' /etc/apt/sources.list.d/cuda-ubuntu2204-x86_64.list && \
      apt-get update && \
      apt-get install -y --no-install-recommends \
      libcudnn8 libcudnn8-dev && \
      rm -f /tmp/cuda-keyring.deb && \
      rm -rf /var/lib/apt/lists/*; \
    fi

RUN pip install --no-cache-dir -e "${PIP_EXTRAS}"

# ── Make pip-installed NVIDIA CUDA libs visible to PaddlePaddle ──
# PyTorch locates them internally; PaddlePaddle needs LD_LIBRARY_PATH + unversioned .so symlinks.
ENV NVIDIA_PIP_LIBS="/usr/local/lib/python3.12/site-packages/nvidia/cublas/lib:/usr/local/lib/python3.12/site-packages/nvidia/cuda_runtime/lib:/usr/local/lib/python3.12/site-packages/nvidia/cufft/lib:/usr/local/lib/python3.12/site-packages/nvidia/curand/lib:/usr/local/lib/python3.12/site-packages/nvidia/cusolver/lib:/usr/local/lib/python3.12/site-packages/nvidia/cusparse/lib:/usr/local/lib/python3.12/site-packages/nvidia/nvrtc/lib:/usr/local/lib/python3.12/site-packages/nvidia/nvjitlink/lib:/usr/local/lib/python3.12/site-packages/nvidia/nccl/lib"
ENV LD_LIBRARY_PATH="${NVIDIA_PIP_LIBS}:${LD_LIBRARY_PATH}"

# Create unversioned .so symlinks (e.g. libcublas.so -> libcublas.so.12)
RUN find /usr/local/lib/python3.12/site-packages/nvidia -name '*.so.*' -type f \
      | while read f; do \
          dir="$$(dirname "$$f")"; \
          base="$$(basename "$$f")"; \
          soname="$$(echo "$$base" | sed 's/\.so\..*/.so/')"; \
          [ -e "$$dir/$$soname" ] || ln -s "$$base" "$$dir/$$soname"; \
        done

RUN mkdir -p /app/data/uploads

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
