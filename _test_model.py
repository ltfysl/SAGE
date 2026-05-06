import torch; torch.set_num_threads(1)
print('step 1: torch OK')
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
print('step 2: transformers OK')
tok = AutoTokenizer.from_pretrained('google/flan-t5-small')
print('step 3: tokenizer OK')
model = AutoModelForSeq2SeqLM.from_pretrained('google/flan-t5-small')
print('step 4: model OK')
