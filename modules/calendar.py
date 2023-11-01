from Tkinter_template.Assets.universal import CanvasCalendar
from Tkinter_template.Assets.project_management import canvas_reduction, progress_bar
from Tkinter_template.Assets.extend_widget import EffectButton
from Tkinter_template.Assets.image import tk_image
from Tkinter_template.Assets.font import font_get, font_span
from collections import defaultdict
import datetime
import json
import os


class Calendar:
    color_list = {
        "new word": "blue",
        "new word is zero": "red"
    }

    def __init__(self, app):
        self.app = app
        self.c = self.app.canvas
        self.cs = self.app.canvas_side
        self.calendar = CanvasCalendar(self.c)
        self.today = datetime.date.today()

        self.calendar.set_parameter({
            "zero rectangle": True,
            "active fill": "#FFEA00",
            "header list": ("月", "火", "水", "木", "金", "土", "日"),
            "bind function": {"<Button-1>": self.__press},
            "today highlight": ("red", "#98FF98")
        })

    def __press(self, args):
        date = args[args.find("-")+1:]
        self.app.Databases.external_get_built_date(date)

    def __write_info(self, date, text, fill, font_size=16):
        a, b, c, d = self.c.coords(f"calendar-{date}")
        self.c.create_text((a+c)/2, (b+d)/2, text=text,
                           font=font_get(font_size), fill=fill, tags=("calendar"))

    def __built_button_and_bind(self):
        def change(args):
            if args == "left":
                if self.calendar.month == 1:
                    self.calendar.set_date(self.calendar.year-1, 12)
                else:
                    self.calendar.set_date(
                        self.calendar.year, self.calendar.month-1)
            elif args == "right":
                if self.calendar.month == 12:
                    self.calendar.set_date(self.calendar.year+1, 1)
                else:
                    self.calendar.set_date(
                        self.calendar.year, self.calendar.month+1)
            elif args == "now":
                self.calendar.set_date(self.today.year, self.today.month)
            self.calendar.clear()
            self.__draw()

        left = EffectButton(("Yellow", "black"), self.c, image=tk_image(
            "left.png", 50, 50, dirpath="images\\build_word"), command=lambda: change("left"))
        now = EffectButton(("Yellow", "black"), self.c, image=tk_image(
            "now.png", 100, 50, dirpath="images\\calendar"), command=lambda: change("now"))
        right = EffectButton(("Yellow", "black"), self.c, image=tk_image(
            "right.png", 50, 50, dirpath="images\\build_word"), command=lambda: change("right"))
        self.c.create_window(*self.cs, anchor='se', window=right)
        self.c.create_window(
            self.cs[0]-60, self.cs[1], anchor='se', window=now)
        self.c.create_window(
            self.cs[0]-170, self.cs[1], anchor='se', window=left)
        self.c.bind("<Left>", lambda e: change("left"))
        self.c.bind("<Right>", lambda e: change("right"))
        self.c.bind("<space>", lambda e: change("now"))

    def __draw(self):
        self.c.update()
        self.calendar.calerdar_to_canvas(
            (20, 100), (self.cs[0]-40, self.cs[1]-160))
        self.__render(self)
        self.c.update()

    @progress_bar({
        "new window": False
    })
    def __render(self):
        path = "data\\單字"
        folders = os.listdir(path)
        self.__render.add_arg({"total": len(folders)})

        vocabulary_number = defaultdict(int)
        count = 1
        for folder_name in folders:
            path_ = os.path.join(path, folder_name)
            for files in os.listdir(path_):
                with open(os.path.join(path_, files), encoding="utf-8") as file:
                    data = json.load(file)
                built_time = data['built time']
                if (built_time[0:4] == str(self.calendar.year)) and (built_time[5:7] == f"{self.calendar.month:02d}"):
                    vocabulary_number[built_time[0:10]] += 1
            self.__render.compelete_part(count)
            count += 1

        max_day = list(range(1, max(self.calendar.monthdayscalendar(
            self.calendar.year, self.calendar.month)[-1])+1))

        for date in vocabulary_number:
            self.__write_info(
                date, f"{vocabulary_number[date]}", self.color_list['new word'], 26)
            max_day.remove(int(date[8:10]))

        for remain in max_day:
            if f"{self.today.year}-{self.today.month:02d}-{self.today.day:02d}" < f"{self.calendar.year}-{self.calendar.month:02d}-{remain:02d}":
                break

            self.__write_info(
                f"{self.calendar.year}-{self.calendar.month:02d}-{remain:02d}", "0", self.color_list['new word is zero'], 30)

    def enter(self):
        self.__render.add_arg({
            'canvas': self.app.bulletin_board,
            "size": self.app.bulletin_board_side
        })
        canvas_reduction(self.c, self.cs)
        self.__built_button_and_bind()
        self.__draw()
