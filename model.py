import os, glob
import torch
import numpy as np
from omegaconf import OmegaConf
from PIL import Image
from itertools import islice
from einops import rearrange
import time
from pytorch_lightning import seed_everything
from torch import autocast
from ldm.util import instantiate_from_config
from ldm.models.diffusion.ddim import DDIMSampler
from ldm.models.diffusion.plms import PLMSSampler


def chunk(it, size):
    it = iter(it)
    return iter(lambda: tuple(islice(it, size)), ())


def numpy_to_pil(images):
    """
    Convert a numpy image or a batch of images to a PIL image.
    """
    if images.ndim == 3:
        images = images[None, ...]
    images = (images * 255).round().astype("uint8")
    pil_images = [Image.fromarray(image) for image in images]

    return pil_images


def load_model_from_config(config, ckpt, verbose=False):
    print(f"Loading model from {ckpt}")
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    pl_sd = torch.load(ckpt, map_location=device)
    if "global_step" in pl_sd:
        print(f"Global Step: {pl_sd['global_step']}")
    sd = pl_sd["state_dict"]
    model = instantiate_from_config(config.model)
    m, u = model.load_state_dict(sd, strict=False)
    model.cuda()
    model.eval()
    return model


class Model:
    def __init__(self, checkpoint, model_config_path):
        config = OmegaConf.load(model_config_path)
        self.model = load_model_from_config(config, checkpoint)


    def _sample(self, sampler, time_steps, conditioning, shape, scale, uc):
        sample, _ = sampler.sample( S =                             time_steps,
                                    conditioning =                  conditioning,
                                    batch_size =                    1,
                                    shape =                         shape,
                                    verbose =                       False,
                                    unconditional_guidance_scale =  scale,
                                    unconditional_conditioning =    uc,
                                    eta =                           0.0)

        decoded_sample = self.model.decode_first_stage(sample)
        decoded_sample = torch.clamp((decoded_sample + 1.0) / 2.0, min=0.0, max=1.0)
        decoded_sample = decoded_sample.cpu().permute(0, 2, 3, 1).numpy()

        torch_sample = torch.from_numpy(decoded_sample).permute(0, 3, 1, 2)

        torch_sample = 255. * rearrange(torch_sample[0].cpu().numpy(), 'c h w -> h w c')
        return Image.fromarray(torch_sample.astype(np.uint8))


    def generate(self, prompt, params, config):
        print("\n-- Generating images --")
        imgs = list()
        uc = None

        shape = [4, int(params["height"]) // 8, int(params["width"]) // 8]

        tic = time.time()
        for n in range(int(params["n_samples"])):
            for scale in params["scale"]:
                for seed in params["seed"]:
                    for time_steps in params["time_steps"]:
                        if float(scale) != 1.0:
                            uc = self.model.get_learned_conditioning([""])
                        c = self.model.get_learned_conditioning([prompt])
                        
                        seed_everything(int(seed))
                        if params["plms"]:
                            sampler = PLMSSampler(self.model)
                        else:
                            sampler = DDIMSampler(self.model)
                        with torch.no_grad():
                            with autocast("cuda"):
                                with self.model.ema_scope():
                                    imgs.append(self._sample(sampler, int(time_steps), c, shape, float(scale), uc))

        toc = time.time()
        print(f"Done. Elapsed time: {toc-tic}sec")
        return imgs