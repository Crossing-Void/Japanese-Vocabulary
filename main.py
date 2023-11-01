from Tkinter_template.Assets.project_management import create_menu, canvas_reduction, making_widget
from Tkinter_template.Assets.soundeffect import play_sound
from Tkinter_template.Assets.font import font_get, font_span
from Tkinter_template.Assets.image import tk_image
from modules.built_word import Built
from modules.database import Database
from modules.word_card import WordCard
from Tkinter_template.base import Interface
from Tkinter_template.Assets.universal import MoveBg
from Tkinter_template.Assets.extend_widget import SelectLabel, EffectButton
from modules.calendar import Calendar
from tkinter.messagebox import showinfo, askokcancel
import time
import os
import random


class Main(Interface):
    def __init__(self, title: str, icon=None, default_menu=True):
        super().__init__(title, icon, default_menu)

        self.move_bg_state = False
        self.move_bg_timer = None
        self.move_bg_start = 0
        self.move_bg_interval = 0.1
        self.move_bg_stop = 2.5
        self.__label_counter = []

        # modify
        self.dashboard['height'] = int(self.dashboard['height']) - 20
        self.dashboard_side = int(self.dashboard['width']), int(
            self.dashboard['height'])
        self.canvas['height'] = int(self.canvas['height']) - 20
        self.canvas_side = int(self.canvas['width']), int(
            self.canvas['height'])
        self.BuiltWords = Built(self)
        self.Databases = Database(self)
        self.Wordcards = WordCard(self)
        self.Calendars = Calendar(self)
        self.__expand_words()
        self.__words_counter = [making_widget("StringVar")(
            value="") for i in range(len(self.hiragana_list))]
        self.__total_counter = making_widget("StringVar")(
            value=""
        )
        # move bg
        words = ['words', []]
        for name in self.hiragana_list + self.katakana_list:
            if not name:
                continue
            if len(name) > 1:
                for n in name:
                    words[1].append([n, ''])
            else:
                words[1].append([name, ''])

        self.Moves = MoveBg(self.canvas, self.canvas_side, 15, words)
        self.__build_menu()
        self.__build_bulletin_board()
        self.__build_counter()
        self.main_page()

    def __expand_words(self):
        with open("modules\\hiragana.txt", encoding='utf-8') as file:
            self.hiragana_list = file.read().split("\n")
        with open("modules\\katakana.txt", encoding='utf-8') as file:
            self.katakana_list = file.read().split("\n")

    def __build_menu(self):
        # main_menu = create_menu(self.top_menu)
        # self.top_menu.add_cascade(label="Function", menu=main_menu)
        self.top_menu.add_command(label="Focus", command=self.canvas.focus_set)
        # --------------------------------------
        # main_menu.add_command(label="Build", command=self.BuiltWords.enter)

    def __build_bulletin_board(self):
        making_widget("Label")(self.dashboard, font=font_get(20),
                               bg='#FFF9A6', text='bulletin board'.upper()).grid(row=1, column=1, columnspan=5, sticky='we')
        self.bulletin_board = making_widget("Canvas")(
            self.dashboard, width=self.dashboard_side[0], height=120, bg='#FFF9A6')
        self.bulletin_board_side = int(
            self.bulletin_board['width']), int(self.bulletin_board['height'])
        self.bulletin_board.grid(row=2, column=1, columnspan=5)

    def __build_counter(self):
        def enter(args):
            args.config(fg="#ff6b87")
            play_sound("over")

        def sum():
            l.config(fg="gold")
            play_sound("over")

        size = self.dashboard_side[0] // 5 // 3
        count = 0
        for name in self.hiragana_list:
            l = making_widget("Label")(self.dashboard, textvariable=self.__words_counter[count], justify='center',
                                       font=font_get(size-3), relief='solid', width=4)
            self.__origin_color = l['bg']
            l.grid(row=count//5+3, column=count % 5+1)
            l.bind("<Enter>", lambda e, args=l: enter(args))
            l.bind("<Leave>", lambda e, args=l: args.config(
                fg="black"))
            l.bind("<Button-1>", lambda e,
                   args=name: self.Databases.external_get_50(args[0]))
            self.__label_counter.append(l)
            count += 1
        # total
        l = making_widget("Label")(self.dashboard, textvariable=self.__total_counter, justify='center',
                                   font=font_get(size-3), relief='solid', width=4, bg="#ff6b87")
        l.grid(row=count//5+3, column=count % 5+1)
        l.bind("<Enter>", lambda e: sum())
        l.bind("<Leave>", lambda e: l.config(fg="black"))
        l.bind("<Button-1>", lambda e: self.Databases.external_all())

    def __counter_words(self):
        sum = 0
        for i in range(len(self.hiragana_list)):
            if self.hiragana_list[i] == "":
                self.__words_counter[i].set(
                    f"{self.hiragana_list[i]}\n")
                continue
            path = f"data\\單字\\{self.hiragana_list[i][0]}"

            if os.path.exists(path):
                length = len([files for files in os.listdir(path)
                             if os.path.splitext(files)[1] == '.json'])
            else:
                length = 0
            self.__words_counter[i].set(
                f"{self.hiragana_list[i][0]}\n{length}")
            sum += length
        self.__total_counter.set(f"合計\n{sum}")
        # ranking
        dictionary = dict(
            zip(range(len(self.hiragana_list)), self.__words_counter))

        def temp(x):
            try:
                return int(dictionary[x].get()[2:])
            except:
                return 0
        rank = list(
            sorted(dictionary, key=temp, reverse=True))  # position

        # 1st
        ranking = 1
        target = temp(rank[0])
        for position in rank.copy():
            label = self.__label_counter[position]
            if temp(position) == target:
                del rank[0]
                if ranking == 1:
                    label['bg'] = 'gold'
                elif ranking == 2:
                    label['bg'] = 'silver'
                else:
                    label['bg'] = "#cd5832"
            else:
                ranking += 1
                if ranking == 4:
                    break
                del rank[0]
                if ranking == 1:
                    label['bg'] = 'gold'
                elif ranking == 2:
                    label['bg'] = 'silver'
                else:
                    label['bg'] = "#cd5832"
                target = temp(position)
        for position in rank:
            self.__label_counter[position]['bg'] = self.__origin_color

    def __main_function(self):
        def process(text):
            # self.move_bg_state = False
            self.canvas.unbind("<Down>")
            self.canvas.unbind("<Return>")
            self.canvas.unbind("<Up>")
            match text:
                case '新增單字':
                    self.BuiltWords.enter()
                case '單字庫':
                    self.Databases.enter()
                case '測驗':
                    showinfo("Not yet", "尚未實裝")
                case "月曆":
                    self.Calendars.enter()

        SelectLabel('main', self.canvas, text="新增單字", font=font_get(48))
        SelectLabel('main', self.canvas, text="單字庫", font=font_get(48))
        SelectLabel('main', self.canvas, text="測驗", font=font_get(48))
        SelectLabel('main', self.canvas, text="月曆", font=font_get(48))
        SelectLabel.embed_function('main', process)
        SelectLabel.show('main', self.canvas,
                         (self.canvas_side[0]//2-100, 500), 100)

    def __clear_card(self):
        if self.Wordcards.big_card:
            self.canvas.delete("show")
            self.Databases.show_availiable()
            self.Wordcards.big_card = False
            self.canvas.bind('<MouseWheel>', lambda event: self.canvas.yview_scroll(-(event.delta//120), 'units')
                             )
            if self.Databases.modify:
                self.Databases.last_result()  # last search

                # position
                target = self.canvas_side[1]/2 + self.Wordcards.middle_height
                delta = target - self.canvas_side[1]
                if delta > 0:
                    self.canvas.yview_scroll(int(delta//84.0), "units")
                # click

                a, b, width, json_file = self.Wordcards.press_info
                id_ = self.canvas.find_enclosed(a, b, a+width, b+width*5//8)[0]
                tags = self.canvas.gettags(id_)[-1]
                hi = tags.rfind("-")
                number = int(tags[hi+1:])
                self.Wordcards.left_press(a, b, width, json_file, number)

        else:
            play_sound("wrong")

    def main_page(self, popup=True):
        if popup:
            if self.canvas.find_withtag("standfor"):
                if not askokcancel("要離開嗎", "直接離開嗎"):
                    return
        canvas_reduction(self.canvas, self.canvas_side)
        self.bulletin_board.delete('text')
        SelectLabel.clear()
        self.__counter_words()
        self.move_bg_state = True
        self.move_bg_timer = time.time()
        self.move_bg_start = 0
        self.move_bg_interval = 0.1
        self.Wordcards.big_card = False
        self.BuiltWords.katakana_signal = False
        self.BuiltWords.accent_state = False
        half = self.canvas_side[0]//2
        # logo
        for i in range(10):
            self.canvas.create_image(half, 0, image=tk_image(
                f"{i}.png", 480, 480, dirpath='images\\welcome\\logo'), state='hidden',
                anchor='n', tags=(f'logo-{i}'))

        self.canvas.create_image(half-150, 280, image=tk_image(
            "book.png", 330, 330, dirpath='images\\welcome'), anchor='se')
        self.canvas.create_image(half+240, 450, image=tk_image(
            "db.png", 160, 280, dirpath='images\\welcome'), anchor='sw')

        # build home button and back button
        home = EffectButton(('gold', 'black'), self.dashboard, bg='lightblue', image=tk_image(
            'home.ico', 48, dirpath='images\\bitmaps'), command=self.main_page)
        home.place(x=self.dashboard_side[0],
                   y=self.dashboard_side[1], anchor='se')
        back = EffectButton(('gold', 'black'), self.dashboard, bg='lightblue', image=tk_image(
            'back.png', 42, dirpath='images\\card'), command=self.__clear_card)
        back.place(x=self.dashboard_side[0]-50,
                   y=self.dashboard_side[1], anchor='se')
        top = EffectButton(('gold', 'black'), self.dashboard, bg='lightblue', image=tk_image(
            'top.png', 48, dirpath='images\\database'), command=lambda: self.canvas.yview_moveto(0))
        top.place(x=self.dashboard_side[0]-96,
                  y=self.dashboard_side[1], anchor='se')

        self.__main_function()

    def change_logo(self):
        if (t := time.time()) - self.move_bg_timer > self.move_bg_interval:
            for x in range(10):
                if x == self.move_bg_start % 10:
                    if x == 9:
                        self.move_bg_interval = self.move_bg_stop
                    else:
                        self.move_bg_interval = 0.1
                    self.canvas.itemconfig(f'logo-{x}', state='normal')
                else:
                    self.canvas.itemconfig(f'logo-{x}', state='hidden')
            self.move_bg_start += 1
            self.move_bg_timer = t

    def set_bulletin_text(self, text, fontsize: int = None, color: str = 'black', delete=True):
        if delete:
            self.bulletin_board.delete('text')
        self.bulletin_board.create_text(0, 0, anchor='nw', text=text, font=font_get(font_span(text, int(self.bulletin_board['width'])) if fontsize is None else fontsize), fill=color,
                                        tags=('text'))
        self.bulletin_board.update()


if __name__ == "__main__":
    main = Main("Japanese Vocabulary", "favicon.ico", False)
    main.Moves.create_obj(15)
    while True:
        main.canvas.update()
        if main.move_bg_state:
            main.Moves.flush()
            main.change_logo()
        if main.canvas.find_withtag("card-nothing-text"):
            main.canvas.itemconfig("moveBg", state="hidden")
            main.Databases.nothing_flush()
        else:
            main.canvas.itemconfig("moveBg", state='normal')
        main.BuiltWords.katakana_flush()
        main.BuiltWords.accent_flush()
        time.sleep(0.01)
