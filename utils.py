from modeling_gemma import PaliGemmaForConditionalGeneration, PaliGemmaConfig
from transformers import AutoTokenizer
import json
import glob
from safetensors import safe_open
from typing import Tuple
import os 

def load_hf_model(model_path, device):
    # load tokenizer
    tokenizer = AutoTokenizer.from_pretrained(model_path, padding_side="right")
    assert tokenizer.padding_side == "right"

    # find all the *.safetensor files
    safetensors_files = glob.glob(os.path.join(model_path, "*.safetensors"))

    # load then one by one in the tensors dictionary
    tensors = {}
    for safetensor_file in safetensors_files:
        with safe_open(safetensor_file, framework="pt", device="cpu") as f:
            for key in f.keys():
                tensors[key] = f.get_tensor(key)
    # load the model's config
    with open(os.path.join(model_path, "config.json"), "r") as f:
        model_config_file = json.load(f)
        config = PaliGemmaConfig(**model_config_file)
    
    # create the model using the configuration
    model = PaliGemmaForConditionalGeneration(config).to(device)
    # load the state dict of the model
    model.load_state_dict(tensors, strict=False)
    # tie weights
    model.tie_weights()
    return (model, tokenizer)

