import os.path
import os
from gui import GUI
from model import Model
import time

prompt_preset = {
    "None":                         "",
    "Digital art Colorfull":        " , digital art painting fantasy vibrant in style of yoji shinkawa and hyung - tae kim illustration character design concept colorful joy atmospheric lighting",
    "Digital art Dark souls":       " , darksouls concept art, ultra-realistic, 4k, featured on artstation",
    "Character design":             " , character design, character sheet, moebius, greg rutkowski, zabrocki, karlkka, jayison devadas, phuoc quan, trending on artstation, 8k, ultra wide angle, zenith view, pincushion lens effect",
    "Volumetric lightning dnd":     " , mist, sunrays, dust in the air, dnd character, unreal engine, octane render, dramatic lighting, pond, digital art, by stanley artgerm lau, greg rutkowski, thomas kindkade, alphonse mucha, loish, norman rockwell",
    "Colorfull draw uw":            " , colorful, contrast, depth of field, 3 d scene, render, greg rutkowski, zabrocki, karlkka, jayison devadas, trending on artstation, 8 k, ultra wide angle, zenith view, pincushion lens effect",
    "Studio ghibli":                " , trending on pixiv fanbox, painted by greg rutkowski makoto shinkai takashi takeuchi studio ghibli",
    "Portrait fantasy digital art": " , portrait, fantasy intricate elegant headshot portrait detailed face coherent face highly detailed digital painting artstation concept art smooth sharp focus illustration art by artgerm and greg rutkowski and alphonse mucha",
}

checkpoint = "sd-v1-4.ckpt"
model_config_path = "configs/v1-inference.yaml"
output_path = "output"

class StableDiffusion:

    def __init__(self):
        # Load model in memory
        self.model = Model(checkpoint, model_config_path)
        # Generate GUI
        self.gui = GUI(preset=prompt_preset)


    def generate_image(self, prompt, params, config):
        path = output_path
        if config["group"]:
            path = os.path.join(output_path, config["group"])
            if not os.path.exists(path):
                os.makedirs(path)

        prompt += prompt_preset[config["prompt_preset"]]

        params["scale"] = params["scale"].split(',')
        params["seed"] = params["seed"].split(',')
        params["time_steps"] = params["time_steps"].split(',')

        img = self.model.generate(prompt, params, config)

        seconds = int(time.time()) % 1000000
        count = 0
        for i in img:
            i.save(os.path.join(path, f"{seconds:05}{count}.png"))
            
            prompt_file = open(os.path.join(path, f"{seconds:05}{count}.txt"), "w")
            prompt_file.write("Prompt: "    + prompt + "\n")
            prompt_file.write("Steps: "     + str(params["time_steps"]) + "\n")
            prompt_file.write("Scale: "     + str(params["scale"]) + "\n")
            prompt_file.write("Seed: "      + str(params["seed"]) + "\n")
            prompt_file.write("Height: "    + str(params["height"]) + "\n")
            prompt_file.write("Width: "     + str(params["width"]) + "\n")
            prompt_file.write("Plms: "      + str(params["plms"]) + "\n")
            prompt_file.close()
            count += 1


    def run(self):
        # Listen events
        self.gui.on_event("-GENERATE-", self.generate_image)
        self.gui.listen_events()
        self.gui.close()


def main():
    sd = StableDiffusion()
    sd.run()

if __name__ == "__main__":
    main()
