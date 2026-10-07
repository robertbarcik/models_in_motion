# AWS Lambda base image for Python. It brings the Lambda runtime interface,
# so our only jobs are: install dependencies, copy code, copy the model.
FROM public.ecr.aws/lambda/python:3.12

# Torch first and CPU-only: the default torch wheel drags CUDA libraries
# we cannot use on Lambda, tripling the image size.
# Versions PINNED to the ones the code was tested with. An unpinned build
# grabbed transformers 5.x and broke - the exact lesson of chapter 3.
RUN pip install --no-cache-dir torch==2.8.0 --index-url https://download.pytorch.org/whl/cpu
RUN pip install --no-cache-dir transformers==4.57.6 accelerate==1.10.1

COPY predict.py lambda_function.py ${LAMBDA_TASK_ROOT}/
COPY model ${LAMBDA_TASK_ROOT}/model

CMD ["lambda_function.handler"]
