from Tkinter_template.Assets.project_management import canvas_reduction, new_window, progress_bar, making_widget
from Tkinter_template.Assets.universal import CanvasCalendar
from Tkinter_template.Assets.soundeffect import play_sound
from Tkinter_template.Assets.extend_widget import PlaceholderEntry, EffectButton
from Tkinter_template.Assets.font import font_get, measure
from Tkinter_template.Assets.image import tk_image
import time
import random
import os
import json
from tkinter.messagebox import askokcancel


class Database:
    options = ("50音", "詞性", "標籤")
    card_per_row = 3
    card_padding = 10

    def __init__(self, app) -> None:
        self.app = app
        self.c = self.app.canvas
        self.cs = self.app.canvas_side

    def __show_card(self, num, json_file):
        width = (self.cs[0] - (self.card_per_row+1) *
                 self.card_padding) // self.card_per_row
        x = self.card_padding * \
            (num % self.card_per_row + 1) + width * (num % self.card_per_row)
        y = self.card_padding * (num//self.card_per_row + 1) + \
            (width*5//8) * (num//self.card_per_row)
        self.app.Wordcards.json_to_card(
            json_file, {'point': (x, 200+y), 'width': width})
        self.card_width = width

    def show_nothing(self):
        self.nothing_timer = time.time()
        self.mode = random.randint(0, 2)
        self.velocity = int(self.cs[0]/70) * random.choice([1, -1])
        self.c.create_image(self.cs[0]//2, 200+(self.cs[1]-200)//2,
                            image=tk_image("error.png", int((self.cs[1]-200)//2), int((self.cs[1]-200)//2),
                                           dirpath="images\\database"), tags=('card', "card-nothing"))
        aa, bb = self.c.coords("card-nothing")
        self.c.create_text(
            self.cs[0]//2, bb-(self.cs[1]-200)//4, text="沒有匹配", anchor="s", font=font_get(62, True), fill="#ff6b87",
            tags=("card", "card-nothing-text1", "card-nothing-text"))

        self.c.create_text(
            self.cs[0]//2-self.cs[0], bb-(self.cs[1]-200)//4, text="沒有匹配", anchor="s", font=font_get(62, True), fill="#ff6b87",
            tags=("card", "card-nothing-text2", "card-nothing-text"))

    @progress_bar({
        "new window": False,
    })
    def __do_search(self, search_type, keyword):
        self.app.bulletin_board.delete('all')
        self.app.bulletin_board.update()
        if search_type != 'word':
            try:
                self.win.destroy()
            except:
                pass
        self.c.delete('card')
        match search_type:
            case "50":
                path = os.path.join('data', '單字', keyword)
                if not os.path.exists(path):
                    self.__do_search.add_arg({
                        "total": 0
                    })
                    self.c.create_text(
                        0, 200, anchor="sw", text=f"匹配: 0", font=font_get(42), fill="#ff6b87", tags=("card"))
                    self.show_nothing()
                else:
                    self.__do_search.add_arg({
                        "total": len(os.listdir(path))
                    })
                    for i in range(len(os.listdir(path))):
                        self.__show_card(i, os.path.join(
                            path, os.listdir(path)[i]))
                        self.__do_search.compelete_part(i+1)
                    self.c['scrollregion'] = (
                        0, 0, self.cs[0],
                        self.card_width *
                        (len(os.listdir(path)) // self.card_per_row + 1)
                    )
                    self.c.create_text(
                        0, 200, anchor="sw", text=f"匹配: {len(os.listdir(path))}", font=font_get(42), fill="#ff6b87", tags=("card"))
                    self.c.bind('<MouseWheel>', lambda event: self.c.yview_scroll(-(event.delta//120), 'units')
                                )
            case "part" | "tags" | "word" | "marked" | "建立時間" | "修改時間" | "all" as option:
                self.__do_search.add_arg({
                    "total": len(os.listdir('data\\單字'))
                })
                count = 0
                num = 0
                for dirname in os.listdir("data\\單字"):

                    for filename in os.listdir(f"data\\單字\\{dirname}"):

                        with open(os.path.join(f"data\\單字\\{dirname}", filename), encoding='utf-8') as file:
                            cmp = json.load(file)
                            if option == 'part':
                                if keyword in cmp['詞性'].split(", "):
                                    self.__show_card(
                                        num, os.path.join(f"data\\單字\\{dirname}", filename))
                                    num += 1
                            elif option == 'tags':
                                if keyword in cmp['標籤']:
                                    self.__show_card(
                                        num, os.path.join(f"data\\單字\\{dirname}", filename))
                                    num += 1
                            elif option == 'word':
                                if (keyword in cmp['單字']) or (keyword in cmp['意思']):
                                    self.__show_card(
                                        num, os.path.join(f"data\\單字\\{dirname}", filename))
                                    num += 1
                            elif option == "marked":
                                if (cmp['marked']):
                                    self.__show_card(
                                        num, os.path.join(f"data\\單字\\{dirname}", filename))
                                    num += 1
                            elif option == "建立時間":
                                if keyword in cmp["built time"]:
                                    self.__show_card(
                                        num, os.path.join(f"data\\單字\\{dirname}", filename))
                                    num += 1
                            elif option == "修改時間":
                                if keyword in cmp["edit time"]:
                                    self.__show_card(
                                        num, os.path.join(f"data\\單字\\{dirname}", filename))
                                    num += 1
                            elif option == "all":
                                self.__show_card(
                                    num, os.path.join(f"data\\單字\\{dirname}", filename))
                                num += 1
                    count += 1
                    self.__do_search.compelete_part(count)
                self.c.create_text(
                    0, 200, anchor="sw", text=f"匹配: {num}", font=font_get(42), fill="#ff6b87", tags=("card"))

                if num != 0:
                    self.c['scrollregion'] = (
                        0, 0, self.cs[0],
                        self.card_width *
                        (num // self.card_per_row + 1)
                    )
                else:
                    self.show_nothing()
                self.c.bind('<MouseWheel>', lambda event: self.c.yview_scroll(-(event.delta//120), 'units')
                            )

    def exe(self, category, word):
        corr = {"marked": "收藏", "all": "全部"}
        self.app.Wordcards.big_card = False
        self.category_last = category
        self.keyword_last = word
        self.__do_search(self, category, word)
        if category in ['建立時間', "修改時間"]:
            self.app.set_bulletin_text(
                f"Search: {category} {word}")
        else:
            self.app.set_bulletin_text(
                f"Search: {word if word != None else corr[category]}")
        self.modify = False

    def show_availiable(self):
        def search(word):
            if (not word) or (word == '輸入:'):
                return
            self.exe("word", entry.get())
            entry.delete(0, 'end')

        def category(category):
            win = new_window(category, "favicon.ico")
            self.win = win
            match category:
                case "50音":
                    for i in range(len(self.app.hiragana_list)):
                        if self.app.hiragana_list[i] == "":
                            continue
                        EffectButton(("yellow", "#ff6b87"), win, font=font_get(20), text=self.app.hiragana_list[i][0],
                                     command=lambda args=self.app.hiragana_list[i][0]: self.exe(
                            "50", args),
                            bg="lightyellow").grid(row=i % 5, column=i//5)
                case "詞性":
                    part_of_speech = []
                    count = 0
                    while True:
                        if hasattr(self.app, f"partOfSpeech_{count}"):
                            part_of_speech.append(
                                getattr(self.app, f"partOfSpeech_{count}").get())
                        else:
                            break
                        count += 1

                    for part in range(len(part_of_speech)):
                        EffectButton(("yellow", "#ff6b87"), win, font=font_get(20), text=part_of_speech[part],
                                     command=lambda args=part_of_speech[part]: self.exe(
                                         "part", args),
                                     ).grid(row=part % 5, column=part//5, sticky='we')

                case "標籤":

                    tags = []
                    count = 0
                    while True:
                        if hasattr(self.app, f"tagsList_{count}"):
                            tags.append(
                                getattr(self.app, f"tagsList_{count}").get())
                        else:
                            break
                        count += 1

                    for i in range(len(tags)):
                        EffectButton(("yellow", "#ff6b87"), win, font=font_get(20), width=8, text=tags[i],
                                     command=lambda args=tags[i]: self.exe(
                                         "tags", args),
                                     ).grid(row=i % 8, column=i//8, sticky='we')

        def calendar():
            def change(args):
                if args == "left":
                    if cal.month == 1:
                        cal.set_date(cal.year-1, 12)
                    else:
                        cal.set_date(cal.year, cal.month-1)
                elif args == "right":
                    if cal.month == 12:
                        cal.set_date(cal.year+1, 1)
                    else:
                        cal.set_date(cal.year, cal.month+1)
                cal.clear()
                cal.calerdar_to_canvas((50, 100), (700, 500))
                c.update()

            def enter(args):
                date = args[args.find("-")+1:]
                play_sound("calendar_enter")
                self.app.set_bulletin_text(f"Select {date}")

            def press(args):
                date = args[args.find("-")+1:]
                self.exe(o.get(), date)

            def switch():
                if o.get() == "建立時間":
                    o.set("修改時間")
                else:
                    o.set("建立時間")

            win = new_window("Calendar", "favicon.ico")
            self.win = win
            EffectButton(("Yellow", "black"), win, image=tk_image(
                "left.png", 50, 50, dirpath="images\\build_word"), command=lambda: change("left")).grid(row=1, column=1)
            EffectButton(("Yellow", "black"), win, image=tk_image(
                "right.png", 50, 50, dirpath="images\\build_word"), command=lambda: change("right")).grid(row=1, column=2)
            c = making_widget("Canvas")(win, width=800, height=680)
            o = making_widget("StringVar")(value="建立時間")
            option = EffectButton(("Yellow", "black"), c,
                                  textvariable=o, font=font_get(20), command=switch, bg="#ff6b87")
            c.create_window(800, 600, anchor="se", window=option)
            c.grid(row=2, column=1, columnspan=2)
            cal = CanvasCalendar(c)
            cal.set_parameter({"header list": ("月", "火", "水", "木", "金", "土", "日"),
                               "bind function": {"<Enter>": enter, "<Button-1>": press},
                               "active fill": "#FFEA00",
                               "today highlight": ("lightblue", "#ff6b87")
                               })
            cal.calerdar_to_canvas((50, 100), (700, 500))

        # search
        self.c.create_line(0, 200, self.cs[0], 200, width=3)
        entry = PlaceholderEntry(
            self.c, '輸入:', width=20, font=font_get(20))
        self.app.canvas.create_window(
            10, 5, anchor='nw', window=entry, tags=("select-button"))
        entry_button = EffectButton(('gray', 'black'), self.app.canvas, image=tk_image(
            'search_icon.png', int(20*4/3), int(20*4/3), dirpath='images\\database'), command=lambda: search(entry.get()))
        self.app.canvas.create_window(10+measure('あ'*int(14), 20), 5, anchor='nw',
                                      window=entry_button, tags=("select-button"))
        entry.bind('<Return>', lambda e: search(entry.get()))

        # category
        font_size = 198 // 9
        count = 0
        for name in self.options:
            self.c.create_window(self.cs[0]-(font_size*4)*(count//3), 0+(font_size*8.5//3)*(count % 3),
                                 anchor='ne', window=EffectButton(("Yellow", "black"), self.c, font=font_get(font_size), text=name,
                                                                  command=lambda args=name: category(args)), tags=('select-button')
                                 )
            count += 1
        # star
        self.c.create_window(self.cs[0]-measure("50音", font_size)-30, 0,
                             anchor='ne', window=EffectButton(("Yellow", "black"), self.c, image=tk_image("star-on.png", 50, 50, dirpath="images\\card"),
                                                              command=lambda: self.exe("marked", None)), tags=('select-button'))
        # clock
        self.c.create_window(self.cs[0]-measure("50音", font_size)-30, 0+(font_size*8.5//3),
                             anchor='ne', window=EffectButton(("Yellow", "black"), self.c, image=tk_image("clock.png", 50, 50, dirpath="images\\database"),
                                                              command=calendar), tags=('select-button')
                             )
        # all
        self.c.create_window(self.cs[0]-measure("50音", font_size)-30, 0+(font_size*8.5//3)*2,
                             anchor='ne', window=EffectButton(("Yellow", "black"), self.c, image=tk_image("all.png", 50, 50, dirpath="images\\database"),
                                                              command=lambda: self.exe("all", None)), tags=('select-button')
                             )

    def enter(self):
        self.__do_search.add_arg({
            'canvas': self.app.bulletin_board,
            "size": self.app.bulletin_board_side
        })
        canvas_reduction(self.c)
        self.show_availiable()

    def external_get_50(self, char):
        if self.app.canvas.find_withtag("standfor"):
            if not askokcancel("要離開嗎", "直接離開嗎"):
                return
        self.enter()
        self.exe("50", char)
        self.app.BuiltWords.katakana_signal = False
        self.app.BuiltWords.accent_state = False

    def external_get_built_date(self, date):
        self.enter()
        self.exe("建立時間", date)

    def external_all(self):
        if self.app.canvas.find_withtag("standfor"):
            if not askokcancel("要離開嗎", "直接離開嗎"):
                return
        self.enter()
        self.exe("all", None)
        self.app.BuiltWords.katakana_signal = False
        self.app.BuiltWords.accent_state = False

    def last_result(self):
        self.enter()
        self.exe(self.category_last, self.keyword_last)

    def nothing_flush(self):
        if (t := time.time()) - self.nothing_timer > 0.1:
            if self.mode == 0:
                # to right
                self.c.move("card-nothing-text", int(self.cs[0]/70), 0)
                if self.c.coords("card-nothing-text1")[0] - measure("沒有匹配", 62) / 2 > self.cs[0]:
                    self.c.move("card-nothing-text1", -2*self.cs[0], 0)
                if self.c.coords("card-nothing-text2")[0] - measure("沒有匹配", 62) / 2 > self.cs[0]:
                    self.c.move("card-nothing-text2", -2*self.cs[0], 0)
            elif self.mode == 1:
                # to left
                self.c.move("card-nothing-text", -int(self.cs[0]/70), 0)
                if self.c.coords("card-nothing-text1")[0] + measure("沒有匹配", 62) / 2 < 0:
                    self.c.move("card-nothing-text1", 2*self.cs[0], 0)
                if self.c.coords("card-nothing-text2")[0] + measure("沒有匹配", 62) / 2 < 0:
                    self.c.move("card-nothing-text2", 2*self.cs[0], 0)
            elif self.mode == 2:
                self.c.move("card-nothing-text", self.velocity, 0)
                if self.c.coords("card-nothing-text1")[0] + measure("沒有匹配", 62) / 2 > self.cs[0]:
                    self.velocity *= -1
                if self.c.coords("card-nothing-text1")[0] - measure("沒有匹配", 62) / 2 < 0:
                    self.velocity *= -1
            self.nothing_timer = t
