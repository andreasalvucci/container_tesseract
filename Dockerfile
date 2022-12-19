FROM python

RUN apt-get update && apt-get install -y --no-install-recommends \
      bzip2 \
      g++ \
      git \
      graphviz \
      libgl1-mesa-glx \
      libhdf5-dev \
      openmpi-bin \
      tesseract-ocr \
      wget \
      python3-tk && \
    rm -rf /var/lib/apt/lists/*
    
# Setting up working directory 
RUN mkdir /src
WORKDIR /src
COPY . .
RUN pip install --upgrade pip
RUN pip install opencv-python

RUN pip install -r requirements.txt

RUN (apt-get autoremove -y; \
     apt-get autoclean -y)

ENV QT_X11_NO_MITSHM=1

EXPOSE 1312


COPY . .

COPY ita.traineddata /usr/share/tesseract-ocr/4.00/tessdata/
CMD [ "python", "-u","./script.py" , "--ip", "127.0.0.1"]