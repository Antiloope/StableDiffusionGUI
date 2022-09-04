import PySimpleGUI as sg
import os.path
import os

class GUI:
    def __init__(self, preset):
        file_list_column = [
            [
                sg.Text("Image Folder"),
                sg.In(size=(25, 1), enable_events=True, key="-FOLDER-"),
                sg.FolderBrowse(),
            ],
            [
                sg.Listbox(
                    values=[], enable_events=True, size=(40, 10), key="-FILE LIST-"
                )
            ],
            [
                sg.Text(
                    text="Prompt",size=(40, 1)
                )
            ],
            [
                sg.Input(
                    default_text="", size=(40, 3), key="-PROMPT-"
                )
            ],
            [
                sg.Text(
                    text="Prompts preset",size=(15, 1) 
                ),
                sg.Combo(
                    [*preset], default_value="None", size=(25, 1), key="-PRESET-"
                )
            ],
            [
                sg.Text(
                    text="DDIM steps",size=(20, 1)
                ),
                sg.Text(
                    text="Scale",size=(20, 1)
                )
            ],
            [
                sg.Input(
                    default_text="20", size=(20, 1), key="-TIME_STEPS-"
                ),
                sg.Input(
                    default_text="7", size=(20, 1), key="-SCALE-"
                )
            ],
            [
                sg.Text(
                    text="Width",size=(20, 1)
                ),
                sg.Text(
                    text="Height",size=(20, 1)
                )
            ],
            [
                sg.Combo(
                    [512,640,704,768,832,1024,1536], default_value=512, size=(20, 1), key="-WIDTH-"
                ),
                sg.Combo(
                    [512,640,704,768,832,1024,1536], default_value=512, size=(20, 1), key="-HEIGHT-"
                )
            ],
            [
                sg.Text(
                    text="Seed",size=(20, 1)
                ),
                sg.Text(
                    text="N samples",size=(20, 1)
                )
            ],
            [
                sg.Input(
                    default_text="24", size=(20, 1), key="-SEED-"
                ),
                sg.Input(
                    default_text="1", size=(20, 1), key="-N_SAMPLES-"
                )
            ],
            [
                sg.Text(
                    text="Group name",size=(20, 1)
                ),
                sg.Input(
                    default_text="", size=(20, 1), key="-GROUP-"
                )
            ],
            [
                sg.Checkbox(
                    text="PLMS", default=False, size=(40, 1), key="-PLMS-"
                )
            ],
            [
                sg.Button(
                    button_text="Generate!", enable_events=True, size=(40, 2), key="-GENERATE-"
                )
            ],
        ]

        image_viewer_column = [
            [sg.Text("Choose an image from list on left:")],
            [sg.Text(size=(40, 1), key="-TOUT-")],
            [sg.Image(key="-IMAGE-")],
        ]

        layout = [
            [
                sg.Column(file_list_column),
                sg.VSeperator(),
                sg.Column(image_viewer_column),
            ]
        ]

        self.window = sg.Window("Stable Diffusion GUI", layout)
        self.event_callbacks = {}

    def listen_events(self):
        while True:
            event, values = self.window.read()
            if event == "Exit" or event == sg.WIN_CLOSED:
                break

            try:
                # Get list of files in folder
                file_list = os.listdir(folder)
            except:
                file_list = []
            fnames = [
                f
                for f in file_list
                if os.path.isfile(os.path.join(folder, f))
                and f.lower().endswith((".png", ".gif"))
            ]
            self.window["-FILE LIST-"].update(fnames)

            # Folder name was filled in, make a list of files in the folder
            if event == "-FOLDER-":
                folder = values["-FOLDER-"]
                try:
                    # Get list of files in folder
                    file_list = os.listdir(folder)
                except:
                    file_list = []

                fnames = [
                    f
                    for f in file_list
                    if os.path.isfile(os.path.join(folder, f))
                    and f.lower().endswith((".png", ".gif"))
                ]
                self.window["-FILE LIST-"].update(fnames)
            elif event == "-FILE LIST-":  # A file was chosen from the listbox
                try:
                    filename = os.path.join(
                        values["-FOLDER-"], values["-FILE LIST-"][0]
                    )
                    self.window["-TOUT-"].update(filename)
                    self.window["-IMAGE-"].update(filename=filename)
                except:
                    pass
            else:
                for event_name, callback in self.event_callbacks.items():
                    if event_name == event:
                        params = {
                            "n_samples":    values["-N_SAMPLES-"],
                            "time_steps":   values["-TIME_STEPS-"],
                            "height":       values["-HEIGHT-"],
                            "width":        values["-WIDTH-"],
                            "scale":        values["-SCALE-"],
                            "seed":         values["-SEED-"],
                            "plms":         values["-PLMS-"],
                        }
                        config = {
                            "group":        values["-GROUP-"],
                            "prompt_preset":values["-PRESET-"],
                        }
                        callback(prompt=values["-PROMPT-"], params=params, config=config)


                # prompt = values["-PROMPT-"]
                # if values["-PRESET_PROMPT-"] == 'Digital art Colorfull':
                #     prompt += " digital art painting fantasy vibrant in style of yoji shinkawa and hyung - tae kim illustration character design concept colorful joy atmospheric lighting"
                # if values["-PRESET_PROMPT-"] == 'Digital art Dark souls':
                #     prompt += " darksouls concept art, ultra-realistic, 4k, featured on artstation"
                # if values["-PRESET_PROMPT-"] == 'Character design':
                #     prompt += " character design, character sheet, moebius, greg rutkowski, zabrocki, karlkka, jayison devadas, phuoc quan, trending on artstation, 8k, ultra wide angle, zenith view, pincushion lens effect"
                # if values["-PRESET_PROMPT-"] == 'Volumetric lightning dnd':
                #     prompt += " mist, sunrays, dust in the air, dnd character, unreal engine, octane render, dramatic lighting, pond, digital art, by stanley artgerm lau, greg rutkowski, thomas kindkade, alphonse mucha, loish, norman rockwell"
                # if values["-PRESET_PROMPT-"] == 'Volumetric lightning dnd':
                #     prompt += " , colorful, contrast, depth of field, 3 d scene, render, greg rutkowski, zabrocki, karlkka, jayison devadas, trending on artstation, 8 k, ultra wide angle, zenith view, pincushion lens effect"
                # if values["-PRESET_PROMPT-"] == 'Studio ghibli':
                #     prompt += " ,trending on pixiv fanbox, painted by greg rutkowski makoto shinkai takashi takeuchi studio ghibli"
                # if values["-PRESET_PROMPT-"] == 'Portrait fantasy digital art':
                #     prompt += " portrait, fantasy intricate elegant headshot portrait detailed face coherent face highly detailed digital painting artstation concept art smooth sharp focus illustration art by artgerm and greg rutkowski and alphonse mucha"
                # command = "cd /c/Users/rodri/stable-diffusion\n"
                # command+= "conda activate ldm\n"
                # command+= "python C:/Users/rodri/stable-diffusion/scripts/test.py "
                # command+= "--prompt \""+ prompt + "\" "
                # command+= "--plms "
                # command+= "--outdir \"C:/Users/rodri/Pictures/StableDiffusionImages\" "
                # command+= "--ckpt sd-v1-4.ckpt "
                # command+= "--skip_grid "
                # command+= "--n_iter " + values["-N_SAMPLES-"] + " "
                # command+= "--ddim_steps " + values["-DDIM_STEPS-"] + " "
                # command+= "--H " + str(values["-HEIGHT-"]) + " "
                # command+= "--W " + str(values["-WIDTH-"]) + " "
                # command+= "--scale " + values["-SCALE-"] + " "
                # command+= "--seed " + values["-SEED-"] + " "

                # if values["-GROUP-"]:
                #     command+= "--group " + values["-GROUP-"] + " "
                #     newpath = 'C:/Users/rodri/Pictures/StableDiffusionImages/' + values["-GROUP-"]
                #     if not os.path.exists(newpath):
                #         os.makedirs(newpath)

                # command+= "\nsleep 20"

                # f = open("C:/Users/rodri/Documents/command.sh", "w")
                # f.write(command)
                # f.close()

                # si = subprocess.STARTUPINFO()
                # si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                # subprocess.Popen(["C:/Program Files/Git/git-bash.exe", "C:/Users/rodri/Documents/command.sh"],startupinfo=si)



    def on_event(self, event_name, event_callback):
        self.event_callbacks[event_name] = event_callback


    def close(self):
        self.window.close()
