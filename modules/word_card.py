from Tkinter_template.Assets.project_management import create_menu, canvas_reduction
from Tkinter_template.Assets.soundeffect import play_sound
from Tkinter_template.Assets.image import tk_image
from Tkinter_template.Assets.font import font_get, measure
import json
import re


class WordCard:
    counter = 0

    def __init__(self, app) -> None:
        self.app = app
        self.c = self.app.canvas
        self.cs = self.app.canvas_side
        self.big_card = False

    def __mark_change(self, json_file):
        self.app.Databases.modify = True
        with open(json_file, encoding='utf-8') as file:
            data = json.load(file)
        data['marked'] = not data['marked']
        if data['marked']:
            self.c.itemconfig("star-on", state="normal")
            self.c.itemconfig("star-off", state="hidden")
            play_sound("marked")
        else:
            self.c.itemconfig("star-off", state="normal")
            self.c.itemconfig("star-on", state="hidden")
        with open(json_file, 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=4)

    def __marked(self, count, json_file):
        with open(json_file, encoding='utf-8') as file:
            data = json.load(file)
        if self.c.itemcget(f"star-on-{count}", "state") == "normal":
            # to off
            self.c.itemconfig(f"star-on-{count}", state="hidden")
            self.c.itemconfig(f"star-off-{count}", state="normal")
            data['marked'] = False
        else:
            # to on
            self.c.itemconfig(f"star-on-{count}", state="normal")
            self.c.itemconfig(f"star-off-{count}", state="hidden")
            data['marked'] = True
            play_sound("marked")
        with open(json_file, 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=4)

    def left_press(self, a, b, width, json_file, count):
        self.c.delete("select-rec")
        self.c.create_rectangle(
            a, b, a+width, b+width*5//8, outline='gold', width=7, tags=('select-rec', "card"))

        for id_ in self.c.find_withtag("stamp"):
            for tag in self.c.gettags(id_):
                search = re.search("stamp-(\\d+)", tag)
                if search:
                    number = int(search.group(1))
            self.c.itemconfig(id_, state='normal' if count ==
                              number else "hidden")

    def __right_press(self, e, a, b, width, json_file, count):
        def check():
            self.middle_height = b + width*2.5//8
            self.press_info = a, b, width, json_file
            self.check_card(json_file)

        def edit():
            self.app.BuiltWords.enter(json_file)
            self.middle_height2 = b + width*2.5//8
            self.edit_info = a, b, width, json_file

        def template():
            self.app.BuiltWords.enter(json_file, True)
        self.left_press(a, b, width, json_file, count)

        menu = create_menu(self.c)
        menu.add_command(label="顯示", command=check)
        menu.add_command(label="編輯", command=edit)
        menu.add_command(label="樣板", command=template)
        menu.post(e.x, e.y)

    def json_to_card(self, json_file, params: dict):
        "point, width"
        WordCard.counter += 1
        with open(json_file, encoding='utf-8') as file:
            data = json.load(file)
        if 'start word' in data:
            for i in range(len(self.app.hiragana_list)):
                if not self.app.hiragana_list[i]:
                    continue
                if data['start word'] == (self.app.hiragana_list[i] if len(self.app.hiragana_list[i]) == 1 else self.app.hiragana_list[i][0]):
                    break
        else:
            i = 0
        width = params['width']
        height = int(width * 5 // 8)
        embed_size = int(height//5)
        font_size = int(embed_size*3/4)
        # outline
        self.c.create_image(*params['point'], image=tk_image(f"{i%5+1}.png", width, height, dirpath="images\\card"),
                            anchor='nw', tags=("card", f"card-{self.counter}"))
        if 'start word' in data:

            self.c.create_image(params['point'][0]+width-width//80, params['point'][1]+width//80, image=tk_image(f"embed.png", embed_size, embed_size, dirpath="images\\card"),
                                anchor='ne', tags=(f'embed-{data["author"]}-{data["no."]}-{data["built time"]}', 'card', f"card-{self.counter}"))

            # start word
            a, b = self.c.coords(
                f'embed-{data["author"]}-{data["no."]}-{data["built time"]}')
            self.c.create_text(
                a, b, anchor='ne', text=data['start word'], font=font_get(font_size), fill="#ff6b87", tags=("card", f"card-{self.counter}"))

        x, y = params['point']
        # title

        w = data['單字']
        if "(" in w:
            p = w.find("(")
            words = w[:p]
            ends = w[p+1:]
            ends = ends.replace("(", " ")
            ends = ends.replace(")", " ")
        elif "（" in w:
            p = w.find("（")
            words = w[:p]
            ends = w[p+1:]
            ends = ends.replace("（", " ")
            ends = ends.replace("）", " ")
        else:
            words = w
            ends = ''
        x += width//40
        y += width//80
        self.c.create_text(
            x, y, anchor='nw', text=words, font=font_get(font_size), fill="#90ee90", tags=(f'word-{data["author"]}-{data["no."]}-{data["built time"]}', 'card', f"card-{self.counter}"))

        y += font_size*4//3
        self.c.create_text(
            x, y, anchor='nw', text=ends, font=font_get(int(font_size*0.5)), fill="#90ee90", tags=("card", f"card-{self.counter}"))

        # meaning

        y += font_size*4//3*0.5+5
        self.c.create_line(params['point'][0]+width//80, y,
                           params['point'][0]+width-width//80, y, width=2, fill='pink', tags=("card", f"card-{self.counter}", f"sep-line-{self.counter}"))
        y += 2
        self.c.create_text(
            x, y, anchor='nw', text=data['意思'], font=font_get(int(font_size*0.7)), fill="#90ee90", tags=("card", f"card-{self.counter}"))

        # star
        aa, bb, *_ = self.c.coords(f"sep-line-{self.counter}")
        self.c.create_image(params['point'][0]+width-width//80, bb, image=tk_image(f"star-off.png", int(embed_size), int(embed_size), dirpath="images\\card"),
                            anchor='ne', tags=('card', f"card-{self.counter}", f"star-off-{self.counter}", f"star-{self.counter}"),
                            state="hidden" if data['marked'] else "normal")
        self.c.create_image(params['point'][0]+width-width//80, bb, image=tk_image(f"star-on.png", int(embed_size), int(embed_size), dirpath="images\\card"),
                            anchor='ne', tags=('card', f"card-{self.counter}", f"star-on-{self.counter}", f"star-{self.counter}"),
                            state="normal" if data['marked'] else "hidden")
        self.c.tag_bind(f"star-{self.counter}", "<Button-1>", lambda e,
                        count=self.counter, j=json_file: self.__marked(count, j))

        # stress

        aa, bb = self.c.coords(
            f'word-{data["author"]}-{data["no."]}-{data["built time"]}')
        temp_text = data['重音'].split(", ")
        temp_text = list(map(lambda x: f"[{x}]", temp_text))
        self.c.create_text(
            aa + measure(words, font_size), bb+font_size*4//3, fill="#acdfa4", anchor='sw', text=" ".join(temp_text), font=font_get(int(font_size*0.4)), tags=("card", f"card-{self.counter}")
        )
        # part
        y += font_size*4//3*0.7+5
        temp = data['詞性'].split(", ")
        temp_x = x
        for i in range(len(temp)):
            self.c.create_image(temp_x+width//80, y, image=tk_image(f"part.png",
                                                                    measure(temp[i], int(
                                                                        font_size*0.6)),
                                                                    int(font_size *
                                                                        0.5*5/3),
                                                                    dirpath="images\\card"),
                                anchor='nw', tags=("card", f"card-{self.counter}"))
            self.c.create_text(
                temp_x+width//40, y+font_size*0.8//6, anchor='nw', text=temp[i], font=font_get(int(font_size*0.5)), tags=("card", f"card-{self.counter}")
            )
            temp_x += measure(temp[i], int(font_size*0.6))+5

        # tag
        y += int(font_size * 0.5*5/3)*1.2
        x += width // 80
        ttemp_x = x
        ccount = 0
        if data['標籤']:
            for name in data['標籤'].split(", "):
                if ccount == 3:
                    y += int(font_size*0.4)*6//3
                    x = ttemp_x
                self.c.create_image(x, y, image=tk_image(f"block.png",
                                                         measure(name, int(
                                                             font_size*0.4)),
                                                         int(font_size *
                                                             0.4*5/3),
                                                         dirpath="images\\card"),
                                    anchor='nw', tags=("card", f"card-{self.counter}"))
                self.c.create_text(
                    x, y+font_size*0.4//6, anchor='nw', text=name, font=font_get(int(font_size*0.4)), tags=("card", f"card-{self.counter}")
                )
                x += measure(name, int(font_size*0.4))*1.2
                ccount += 1
        # stamp
        self.c.create_image(params['point'][0] + params['width'] - params['width']//80,
                            params['point'][1] + params['width'] *
                            5//8 - params['width']//80,
                            image=tk_image(f"stamp.png",
                                           int(embed_size*1.5),
                                           int(embed_size*1.5),
                                           dirpath="images\\card"),
                            anchor='se', tags=("card", f"card-{self.counter}", f"stamp-{self.counter}", "stamp"), state="hidden")
        # bind show
        self.c.tag_bind(f"card-{self.counter}", "<Button-1>",
                        lambda e, a=params['point'][0], b=params['point'][1], w=params['width'], j=json_file, count=self.counter:
                        self.left_press(a, b, w, j, count))
        self.c.tag_bind(f"card-{self.counter}", "<Button-3>",
                        lambda e, a=params['point'][0], b=params['point'][1], w=params['width'], j=json_file, count=self.counter:
                        self.__right_press(e, a, b, w, j, count))

    def check_card(self, json_file):
        j = json_file
        with open(json_file, encoding='utf-8') as file:
            json_file = json.load(file)
        self.c.delete("select-button")
        self.big_card = True
        self.c.unbind("<MouseWheel>")
        image_width = 668
        image_height = 622
        image_boundary_height = 48
        width = self.cs[0]
        height = self.cs[1]
        boundary_height = image_boundary_height * (
            (image_height/image_width) / (height/width)
        )

        # outline
        self.c.create_image(0, self.c.canvasy(0), image=tk_image(f"check_board.png", *self.cs,
                                                                 dirpath="images\\card"),
                            anchor='nw', tags=("show", "show-outline"))

        # word and meaning
        self.c.create_text(13, self.c.canvasy(0), text=json_file['單字'], font=font_get(int(boundary_height*3//4)), fill="#90ee90",
                           anchor='nw', tags=("show", "show-word"))
        # stress
        temp_text = json_file['重音'].split(", ")
        temp_text = list(map(lambda x: f"[{x}]", temp_text))
        self.c.create_text(13+measure(json_file['單字'], int(boundary_height*3//4)), self.c.canvasy(0),
                           text=" ".join(temp_text), font=font_get(int(boundary_height*3//4*0.9)), fill="#90ee90",
                           anchor='nw', tags=("show", "show-stress"))
        # start word
        self.c.create_image(width-10, self.c.canvasy(boundary_height)+10,
                            image=tk_image(f"embed.png",
                                           int((boundary_height*3//4)*1.3),
                                           int((boundary_height*3//4)*1.3),
                                           dirpath="images\\card"),
                            anchor='ne', tags=("show", "show-start-word-image"))
        if 'start word' in json_file:

            self.c.create_text(width-10, self.c.canvasy(boundary_height)+10, text=json_file['start word'],
                               font=font_get(int(boundary_height*3//4)), fill="#ff6b87",
                               anchor='ne', tags=("show", "show-start-word"))
        # star
        aa, bb = self.c.coords("show-start-word-image")
        self.c.create_image(aa-int((boundary_height*3//4)*1.3), bb, image=tk_image(f"star-off.png", int((boundary_height*3//4)*1.3), int((boundary_height*3//4)*1.3), dirpath="images\\card"),
                            anchor='ne', tags=('show', "star-off", "star"),
                            state="hidden" if json_file['marked'] else "normal")
        self.c.create_image(aa-int((boundary_height*3//4)*1.3), bb, image=tk_image(f"star-on.png", int((boundary_height*3//4)*1.3), int((boundary_height*3//4)*1.3), dirpath="images\\card"),
                            anchor='ne', tags=('show', "star-on", "star"),
                            state="normal" if json_file['marked'] else "hidden")
        self.c.tag_bind("star", "<Button-1>", lambda e,
                        j=j: self.__mark_change(j))

        # meaning
        self.c.create_text(13, self.c.canvasy(boundary_height)+10, text=json_file['意思'],
                           font=font_get(int(boundary_height*3//4)),
                           anchor='nw', tags=("show", "show-meaning"))
        # example
        a, b = self.c.coords("show-meaning")
        interval = boundary_height*0.4

        self.c.create_image(13, b+boundary_height+15,
                            image=tk_image(f"example.png",
                                           width-25,
                                           int(6*interval+4*boundary_height),
                                           dirpath="images\\card"),
                            anchor='nw', tags=("show", "show-example-image"))

        self.c.create_text(width//2, b+boundary_height+5+interval, text="例文",
                           font=font_get(int(boundary_height*3//4)), fill='lightyellow',
                           anchor='n', tags=("show", "show-example-title"))

        text = json_file['例句'].split("\n")
        for i in range(1, len(text)+1):
            self.c.create_text(13+interval+2*boundary_height, b+boundary_height+5+interval*(i+1)+boundary_height*3*i//4, text=text[i-1],
                               font=font_get(int(boundary_height*3//4)), fill="#ff6b87",
                               anchor='nw', tags=("show", f"show-example-text{i}"))
            if i == 1:
                self.c.create_image(13+interval+2*boundary_height, b+boundary_height+5+interval*(i+1)+boundary_height*3*i//4,
                                    image=tk_image(f"ex-1.png",
                                                   height=int(
                                                       interval+2*boundary_height),
                                                   dirpath="images\\card"),
                                    anchor='ne', tags=("show", "show-example-image-1"))
            if i == 3:
                self.c.create_line(
                    13, b+boundary_height+5+interval *
                        (i+1)+boundary_height*3*i//4,
                    width-10, b+boundary_height+5+interval *
                        (i+1)+boundary_height*3*i//4, width=3, fill='gold',
                        tags=("show", "show-example-separate"))
                self.c.create_image(13+interval+2*boundary_height, b+boundary_height+5+interval*(i+1)+boundary_height*3*i//4,
                                    image=tk_image(f"ex-2.png",
                                                   height=int(
                                                       interval+2*boundary_height),
                                                   dirpath="images\\card"),
                                    anchor='ne', tags=("show", "show-example-image-2"))

        # three outline
        part_width = (width - 20) // 3
        aa, bb = self.c.coords("show-example-image")
        self.c.create_image(13, bb+int(6*interval+4*boundary_height),
                            image=tk_image(f"block.png",
                                           int(part_width),
                                           int(self.c.canvasy(height)-18-bb-int(6 *
                                               interval+4*boundary_height)),
                                           dirpath="images\\card"),
                            anchor='nw', tags=("show", "show-partAndTag-outline"))
        self.c.create_line(
            13, bb+int(6*interval+4*boundary_height) + int(self.c.canvasy(height)-18-bb-int(6 * interval+4*boundary_height))*0.5, 13 +
            part_width, bb+int(6*interval+4*boundary_height) +
            int(self.c.canvasy(height)-18-bb -
                int(6 * interval+4*boundary_height))*0.5,
            width=3, fill="gold", tags=("show", "show-partAndTag-line"))
        self.c.create_image(13+part_width, bb+int(6*interval+4*boundary_height),
                            image=tk_image(f"block.png",
                                           int(part_width),
                                           int(self.c.canvasy(height)-18-bb-int(6 *
                                               interval+4*boundary_height)),
                                           dirpath="images\\card"),
                            anchor='nw', tags=("show", "show-noteAndRelation-outline"))
        self.c.create_line(
            13+part_width, bb+int(6*interval+4*boundary_height) + int(self.c.canvasy(height)-18-bb-int(6 * interval+4*boundary_height)) *
            0.5, 13+2*part_width, bb+int(6*interval+4*boundary_height) +
            int(self.c.canvasy(height)-18-bb -
                int(6 * interval+4*boundary_height))*0.5,
            width=3, fill="gold", tags=("show", "show-noteAndRelation-line"))
        self.c.create_image(13+part_width*2, bb+int(6*interval+4*boundary_height),
                            image=tk_image(f"block.png",
                                           int(part_width),
                                           int(self.c.canvasy(height)-18-bb-int(6 *
                                               interval+4*boundary_height)),
                                           dirpath="images\\card"),
                            anchor='nw', tags=("show", "show-setting-outline"))
        # tags and part
        a, b = self.c.coords("show-partAndTag-outline")
        self.c.create_text(a+part_width//2, b, text="詞性", fill="#ff6b87",
                           font=font_get(int(boundary_height*3//4*0.4)),
                           anchor='n', tags=("show", "show-part-title"))
        self.c.create_text(a+3, b+int(boundary_height*0.4), text='\n'.join(json_file['詞性'].split(", ")[0:4]),
                           font=font_get(int(boundary_height*3//4*0.35)),
                           anchor='nw', tags=("show", "show-part-text"))
        self.c.create_text(a+3+part_width//2, b+int(boundary_height*0.4), text='\n'.join(json_file['詞性'].split(", ")[4:]),
                           font=font_get(int(boundary_height*3//4*0.35)),
                           anchor='nw', tags=("show", "show-part-text"))

        a, b, c, d = self.c.coords("show-partAndTag-line")
        self.c.create_text(a+part_width//2, b+5, text="標籤", fill="#ff6b87",
                           font=font_get(int(boundary_height*3//4*0.4)),
                           anchor='n', tags=("show", "show-tag-title"))
        self.c.create_text(a+3, b+5+int(boundary_height*0.4), text='\n'.join(json_file['標籤'].split(", ")[0:4]),
                           font=font_get(int(boundary_height*3//4*0.35)),
                           anchor='nw', tags=("show", "show-tag-text"))
        self.c.create_text(a+3+part_width//2, b+5+int(boundary_height*0.4), text='\n'.join(json_file['標籤'].split(", ")[4:]),
                           font=font_get(int(boundary_height*3//4*0.35)),
                           anchor='nw', tags=("show", "show-tag-text"))

        # note and relation
        a, b = self.c.coords("show-noteAndRelation-outline")
        self.c.create_text(a+part_width//2, b, text="相關", fill="#ff6b87",
                           font=font_get(int(boundary_height*3//4*0.4)),
                           anchor='n', tags=("show", "show-relation-title"))
        self.c.create_text(a+3, b+int(boundary_height*0.4), text=json_file['相關'],
                           font=font_get(int(boundary_height*3//4*0.35)),
                           anchor='nw', tags=("show", "show-relation-text"))

        a, b, c, d = self.c.coords("show-noteAndRelation-line")
        self.c.create_text(a+part_width//2, b+5, text="備註", fill="#ff6b87",
                           font=font_get(int(boundary_height*3//4*0.4)),
                           anchor='n', tags=("show", "show-relation-title"))
        self.c.create_text(a+3, b+5+int(boundary_height*0.4), text=json_file['備註'],
                           font=font_get(int(boundary_height*3//4*0.35)),
                           anchor='nw', tags=("show", "show-relation-text"))
        # arguments
        a, b = self.c.coords("show-setting-outline")
        self.c.create_text(a+part_width//2, b, text="參數", fill="#ff6b87",
                           font=font_get(int(boundary_height*3//4*0.4)),
                           anchor='n', tags=("show", "show-setting-title"))
        self.c.create_text(a+3, b+int(boundary_height*3//4*0.4),
                           text=f'編號:\n  {json_file["no."]}\n建立時間:\n  {json_file["built time"]}\n上次修改時間:\n  {json_file["edit time"]}\n作者:\n  {json_file["author"]}\n錯誤數:\n  {json_file["mistake count"]}',
                           font=font_get(int(boundary_height*3//4*0.35)),
                           anchor='nw', tags=("show", "show-setting-text"))
