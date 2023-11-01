from Tkinter_template.Assets.font import font_get, font_span
from Tkinter_template.Assets.image import tk_image
from tkinter.messagebox import *

from Tkinter_template.Assets.project_management import making_widget, canvas_reduction, new_window
from Tkinter_template.Assets.extend_widget import EffectButton, PlaceholderEntry
from Tkinter_template.Assets.universal import parse_json_to_property
from itertools import permutations
import datetime
import json
import os
import time
import random


class Built:
    standard_field = ("單字", "詞性", "重音", "意思", "例句", "標籤",
                      "相關", "備註")

    def __init__(self, app) -> None:
        self.app = app
        self.data = {}
        self.__tags = []
        self.__small_keyboard = None
        self.__var = []
        self.__number_select = 0
        self.__region_select = None
        parse_json_to_property(self.app, 'modules\\setting.json')

    def __file(self, number):
        def add_tag():
            def enter(e):
                tag = entry.get()
                if tag in self.__tags:
                    showerror("Repeat", f"The tag: {tag} is repeat!")
                else:
                    self.__tags.append(tag)

                    with open("modules\\setting.json", 'r', encoding='utf-8') as file:
                        data = json.load(file)
                    with open("modules\\setting.json", 'w', encoding='utf-8') as file:
                        data['tagsList'] = self.__tags
                        json.dump(data, file, indent=4)

                    parse_json_to_property(self.app, 'modules\\setting.json')
                    self.__file(self.standard_field.index("標籤"))
                win.destroy()
            win = new_window("Add new tag", "favicon.ico")
            entry = PlaceholderEntry(win, "輸入新標籤", width=20, font=font_get(50))
            entry.grid()
            entry.bind("<Return>", enter)

        def insert_accent():
            def insert(text):
                for widget in self.app.canvas.winfo_children():
                    if type(widget) == making_widget("Text"):
                        if widget.get("1.0", "end")[:-1] == "なし":
                            widget.delete("1.0", "end")
                        widget.insert('insert', text)
                win.destroy()

            def enter(a):
                a.config(bg="gold")

            def leave(a):
                a.config(bg="lightblue")
            if not self.data['重音']:
                return
            win = new_window("重音", "favicon.ico")

            accent = self.data['重音'].split(", ")
            for items in permutations(accent):
                text = f"重音 {' '.join(items)}"
                a = making_widget("Button")(win, text=text, font=font_get(24), bg="lightblue",
                                            command=lambda t=text: insert(t))
                a.bind("<Enter>", lambda e, w=a: enter(w))
                a.bind("<Leave>", lambda e, w=a: leave(w))
                a.grid()
            win.grab_set()

        ca = self.app.canvas
        a, b, c, d = ca.coords('rec')
        w, h = c - a, d - b
        if self.__region_select is not None:
            self.__region_select.unbind("<MouseWheel>")
        match self.standard_field[number]:
            case "單字" | "意思" | "例句" | "相關" | "備註" as option:
                self.__region_select = making_widget("Text")(ca, font=font_get(30), height=int(h//50),
                                                             width=int(w//34))
                if option != '單字':
                    stream = self.data.get(option, '')
                    if (not stream) or (stream.isspace()):
                        self.__region_select.insert(
                            '1.0', "なし")
                    else:
                        self.__region_select.insert('1.0', stream)
                else:
                    self.__region_select.insert('1.0', self.data.get("單字"))
                if option == "備註":

                    self.accent_label = making_widget("Button")(text="重", font=font_get(30), command=insert_accent, bg="gray"
                                                                )

                    ca.create_window(c-1, b+2, anchor='ne',
                                     window=self.accent_label, tags='input')
            case "詞性" | "重音" | "標籤" as option:
                if option == "詞性":
                    part_of_speech = []
                    count = 0
                    while True:
                        if hasattr(self.app, f"partOfSpeech_{count}"):
                            part_of_speech.append(
                                getattr(self.app, f"partOfSpeech_{count}").get())
                        else:
                            break
                        count += 1
                    self.__var = part_of_speech
                elif option == "標籤":
                    self.__tags = []
                    count = 0
                    while True:
                        if hasattr(self.app, f"tagsList_{count}"):
                            self.__tags.append(
                                getattr(self.app, f"tagsList_{count}").get())
                        else:
                            break
                        count += 1
                    self.__var = self.__tags
                    if len(self.__tags) > 10:
                        x_, y_ = (a+c)//2 - 300, (b+d)//2 - 240
                        ca.create_window(x_-20, y_, anchor='ne', window=EffectButton(('yellow', 'black'), image=tk_image(
                            "up.png", 72, 72, dirpath="images\\build_word"
                        ), command=lambda: self.__region_select.yview_scroll(-1, 'units')), tags='input')
                        ca.create_window(x_-20, y_+440, anchor='ne', window=EffectButton(('yellow', 'black'), image=tk_image(
                            "down.png", 72, 72, dirpath="images\\build_word"
                        ), command=lambda: self.__region_select.yview_scroll(1, 'units')), tags='input')
                    ca.create_window(c-1, b+2, anchor='ne', window=EffectButton(('yellow', 'black'), image=tk_image(
                        "Add.png", 48, 48, dirpath="images\\build_word"
                    ), command=add_tag), tags='input')

                else:
                    self.__var = [str(i) for i in range(10)]

                self.__region_select = making_widget("Listbox")(
                    ca, listvariable=making_widget("StringVar")(value=self.__var), font=font_get(30), activestyle='dotbox',
                    selectmode="multiple", selectbackground="gold", height=12)
                self.__region_select.bind('<MouseWheel>', lambda event: self.__region_select.yview_scroll(-(event.delta//120), 'units')
                                          )
                if option in self.data:
                    for selected in self.data[option].split(", "):
                        if selected in self.__var:
                            self.__region_select.selection_set(
                                self.__var.index(selected))
                self.__region_select.bind(
                    "<Double-Button-1>", lambda e: self.select(self.__number_select+1))

        ca.create_window((a+c)//2, (b+d)//2,
                         window=self.__region_select, tags=('input'))

    def __save(self, number):
        if self.__region_select is None:
            return
        match self.standard_field[number]:
            case "單字" | "意思" | "例句" | "相關" | "備註" as option:
                self.data[option] = self.__region_select.get('1.0', 'end')
                if self.data[option][-1] == '\n':
                    self.data[option] = self.data[option][:-1]
                if option == '單字':
                    w = self.data[option]
                    if "(" in w:
                        p = w.find("(")
                        words = w[:p]
                    elif "（" in w:
                        p = w.find("（")
                        words = w[:p]
                    else:
                        words = w
                    try:

                        self.__start_word = words[0]
                        finding = False
                        for name in self.app.hiragana_list + self.app.katakana_list:
                            if not name:
                                continue
                            if len(name) > 1:
                                for n in name:
                                    if self.__start_word == n:
                                        finding = True
                                        break
                                if finding:
                                    break
                                else:
                                    continue
                            if self.__start_word == name:
                                finding = True
                                break
                        if not finding:
                            try:
                                self.__start_word = w[p+1]
                            except:
                                self.__start_word = None
                        else:
                            self.__start_word = words[0]
                    except:
                        self.__start_word = None
                    self.app.set_bulletin_text(
                        f"Building:\n{words}", fontsize=24)
                    self.katakana_signal = False
                    if self.__start_word:
                        for name in self.app.katakana_list:
                            if not name:
                                continue
                            if len(name) > 1:
                                for n in name:
                                    if self.__start_word == n:
                                        self.katakana_signal = True
                            if self.katakana_signal:
                                break
                            if self.__start_word == name:
                                self.katakana_signal = True
                                break
                    self.signal_label = making_widget(
                        "Label"
                    )(self.app.canvas, text="カタ", font=font_get(font_span("カタ", 195)), fg="gold", bg='blue')
                    self.signal_timer = time.time()
                    if self.katakana_signal:
                        self.app.canvas.create_window(self.app.canvas_side[0], 200, anchor='ne',
                                                      window=self.signal_label, tags=("signal"))
                    else:
                        self.app.canvas.delete("signal")
            case "詞性" | "重音" | "標籤" as option:
                if sel := self.__region_select.curselection():
                    self.data[option] = ', '.join(
                        [self.__var[number] for number in sel])
                else:
                    self.data[option] = ''

                if option == "重音":
                    self.accent_timer = time.time()
                    if not self.data['重音']:
                        self.accent_state = False
                    else:
                        self.accent_state = True

    def __write(self, mode):
        def exe(name: str):
            path = os.path.join('data', '單字', name)
            if not os.path.exists(path):
                os.mkdir(path)
            no = len(os.listdir(path)) + 1

            self.data['no.'] = no
            self.data['built time'] = datetime.datetime.today().strftime(
                "%Y-%m-%dT%H:%M:%S")
            self.data['edit time'] = datetime.datetime.today().strftime(
                "%Y-%m-%dT%H:%M:%S")
            self.data['mistake count'] = 0
            self.data['marked'] = False
            self.data['author'] = self.app.author.get()

            with open(os.path.join(path, str(self.data['no.'])+'.json'), 'w') as file:
                json.dump(self.data, file, indent=4)
            # success
            showinfo(title="Success",
                     message=f"Build the {no} vocabulary into {name}!")
            self.app.main_page(False)
            win.destroy()
        self.__save(self.__number_select)
        if (not self.data['單字']) or (self.data['單字'].isspace()):
            showerror("Empty error", "單字不能為空白")
            self.select(self.standard_field.index("單字"))
            return
        if not self.data['詞性']:
            showerror("Empty error", "不能沒有詞性")
            self.select(self.standard_field.index("詞性"))
            return
        if mode == 'new':
            win = new_window("Select category", "favicon.ico")
            for i in range(len(self.app.hiragana_list)):
                if self.app.hiragana_list[i] == "":
                    continue
                if self.__start_word:
                    if self.__start_word in self.app.hiragana_list[i] + self.app.katakana_list[i]:
                        self.data['start word'] = self.app.hiragana_list[i][0]
                        EffectButton(("yellow", "#ff6b87"), win, font=font_get(20), text=self.app.hiragana_list[i][0], command=lambda args=self.app.hiragana_list[i][0]: exe(args),
                                     bg='#ff6b87'
                                     ).grid(row=i % 5, column=i//5)

                        continue
                EffectButton(("yellow", "#ff6b87"), win, font=font_get(
                    20), text=self.app.hiragana_list[i][0], command=lambda args=self.app.hiragana_list[i][0]: exe(args), bg='lightyellow').grid(row=i % 5, column=i//5)
            win.grab_set()
        elif mode == "save":
            self.data['edit time'] = datetime.datetime.today().strftime(
                "%Y-%m-%dT%H:%M:%S")
            path = self.data['path']
            del self.data['path']

            with open(path, 'w', encoding='utf-8') as file:
                json.dump(self.data, file, indent=4)

            showinfo(title="Edit",
                     message=f"Edit success!")

            self.app.Databases.last_result()

            # position
            target = self.app.canvas_side[1]/2 + \
                self.app.Wordcards.middle_height2
            delta = target - self.app.canvas_side[1]
            if delta > 0:
                self.app.canvas.yview_scroll(int(delta//84.0), "units")
            # click

            a, b, width, json_file = self.app.Wordcards.edit_info
            id_ = self.app.canvas.find_enclosed(a, b, a+width, b+width*5//8)[0]
            tags = self.app.canvas.gettags(id_)[-1]
            hi = tags.rfind("-")
            number = int(tags[hi+1:])
            self.app.Wordcards.left_press(a, b, width, json_file, number)

    def enter(self, exist_file=False, new=False):
        def select(num, save=True):
            self.select = select
            if num >= len(self.standard_field) or num < 0:
                return
            if save:
                self.__save(self.__number_select)
            c.delete('input')
            self.__number_select = num

            s = label_c.itemcget(f'label{num}', 'window')
            r, g, b = (120, 25, 25)
            max_ = max(r, g, b)
            del_ = (255 - max_) // len(self.standard_field)
            for child in label_c.winfo_children():
                if child.winfo_name() == s[s.rfind('.')+1:]:
                    child['bg'] = f'#{r+del_*num:02x}{g+del_*num:02x}{b+del_*num:02x}'
                    c.itemconfig(
                        'rec', fill=f'#{r+del_*num:02x}{g+del_*num:02x}{b+del_*num:02x}', )
                    while (label_c.coords(f'label{num}')[0]+150) > label_c.canvasx(cs[0]-10):
                        label_c.xview_scroll(1, 'units')
                    while (label_c.coords(f'label{num}')[0]) < label_c.canvasx(10):
                        label_c.xview_scroll(-1, 'units')

                else:
                    child['bg'] = '#FAFAD2'

            for i in range(len(self.standard_field)):
                if i == num:
                    if (label_c.coords(f'label{i}')[1]) >= 185:
                        label_c.move(f'label{i}', 0, -30)
                else:
                    if (label_c.coords(f'label{i}')[1]) <= 185:
                        label_c.move(f'label{i}', 0, 30)
            self.__file(num)
        if exist_file:
            with open(exist_file, encoding='utf-8') as file:
                self.data = json.load(file)
                if not new:
                    self.data['path'] = exist_file
        else:
            self.data = {string: "" for string in self.standard_field}
        self.__number_select = 0
        # render and point to one
        c = self.app.canvas
        cs = self.app.canvas_side
        canvas_reduction(c, cs)
        # rectangle
        c.create_rectangle(10, 200, cs[0] - 200, cs[1] - 10, outline="black",
                           width=3, fill="gray", tags=('rec'))
        # label frames
        label_f = making_widget("Frame")(
            c, width=cs[0], height=200, bg='lightblue')
        c.create_window(0, 0, window=label_f, anchor='nw')
        label_sc = making_widget("Scrollbar")(label_f, orient='horizontal')
        label_c = making_widget("Canvas")(
            label_f, width=cs[0], height=200-30, bg='#ff6b87', xscrollcommand=label_sc.set)
        label_sc['command'] = label_c.xview
        label_sc.grid(sticky='we')
        label_c.grid()
        label_c.bind('<MouseWheel>', lambda event: label_c.xview_scroll(-(event.delta//120), 'units')
                     )

        # build labels
        count = 0

        for name in self.standard_field:
            l = making_widget("Label")(
                label_c, font=font_get(48), text=name, bg='#FAFAD2')
            label_c.create_window(10+count*150, 200, anchor='sw',
                                  window=l, tags=(f'label{count}'))
            l.bind("<Button-1>", lambda e, args=count: select(args))
            count += 1
        label_c['scrollregion'] = (
            0, 0, 10+(count+1)*150, 170
        )
        # finish button
        if exist_file and (not new):
            c.create_window(cs[0], cs[1], anchor='se', window=EffectButton(("yellow", 'black'), c, image=tk_image(
                "save.png", 195, 100, dirpath="images\\edit"), command=lambda: self.__write("save")
            ))

        else:
            c.create_window(cs[0], cs[1], anchor='se', window=EffectButton(("yellow", 'black'), c, image=tk_image(
                "new.png", 195, 100, dirpath="images\\build_word"), command=lambda: self.__write("new")
            ))

        c.create_window(cs[0], cs[1]-105, anchor='se', window=EffectButton(("yellow", 'black'), c, image=tk_image(
            "right.png", 96, 96, dirpath="images\\build_word"), command=lambda: select(self.__number_select+1)
        ))
        c.create_window(cs[0]-97, cs[1]-105, anchor='se', window=EffectButton(("yellow", 'black'), c, image=tk_image(
            "left.png", 96, 96, dirpath="images\\build_word"), command=lambda: select(self.__number_select-1)
        ))
        c.create_window(cs[0], cs[1]-205, anchor='se', window=EffectButton(("yellow", 'black'), c, image=tk_image(
            "keyboard.png", 48, 48, dirpath="images\\build_word"), command=self.keyboard), tags=("standfor")
        )
        c.create_window(cs[0], cs[1]-255, anchor='se', window=EffectButton(("yellow", 'black'), c, image=tk_image(
            "glance.png", 48, 48, dirpath="images\\build_word"), command=self.glance)
        )
        select(self.__number_select, False)

    def keyboard(self):
        def insert(name):
            for widget in self.app.canvas.winfo_children():
                if type(widget) == making_widget("Text"):
                    widget.insert('insert', name)

        def close():
            self.__small_keyboard.destroy()
            self.__small_keyboard = None

        if (self.__small_keyboard is None) or (self.__small_keyboard.winfo_exists == False):
            self.__small_keyboard = new_window("Small keyboard", "favicon.ico")
            self.__small_keyboard.protocol("WM_DELETE_WINDOW", close)
        else:
            self.__small_keyboard.lift()
            self.__small_keyboard.deiconify()

        key = ["()", "（）", "、", "。"]
        count = 0
        for chr in key:

            EffectButton(("yellow", "#ff6b87"), self.__small_keyboard, font=font_get(20), text=chr, width=3, command=lambda args=chr: insert(args)
                         ).grid(row=count % 3, column=count//3)
            count += 1

    def glance(self):
        win = new_window("Glance", "favicon.ico")
        self.__save(self.__number_select)
        r = 0
        for option in self.standard_field:
            r += 1
            tag = making_widget("Label")(win, font=font_get(
                20), text=f"{option}  ")
            if self.data[option] in ['', 'なし']:
                tag['bg'] = 'red'
            tag.grid(row=r, column=1)
            making_widget("Label")(win, font=font_get(
                20), text=self.data[option], justify="left").grid(row=r, column=2, sticky="w")
        win.grab_set()

    def katakana_flush(self):
        if hasattr(self, "katakana_signal") and self.katakana_signal == True:
            if (t := time.time()) - self.signal_timer >= 0.5:
                if self.signal_label['bg'] == "blue":
                    self.signal_label['bg'] = "gray"
                    self.signal_label['fg'] = "white"
                else:
                    self.signal_label['bg'] = "blue"
                    self.signal_label['fg'] = "gold"

                self.signal_timer = t

    def accent_flush(self):
        if hasattr(self, "accent_state") and self.accent_state == True:
            if not hasattr(self, "accent_label"):
                return
            if (t := time.time()) - self.accent_timer >= 0.35:
                if self.accent_label['bg'] == "gray":
                    self.accent_label['bg'] = "#bfff00"

                else:
                    self.accent_label['bg'] = "gray"

                self.accent_timer = t
