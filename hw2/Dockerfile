FROM conda/miniconda3
ADD . .
RUN ls
RUN apt update && apt-get install texlive-latex-base -y
RUN conda create --name pythonhw --file requirements.txt
# RUN conda activate pythonhw
RUN conda install -c nekpot codetreegen
CMD python medium.py

