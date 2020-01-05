#!/usr/bin/env python3.7
# coding=utf-8
'''
# 作者: weimo
# 创建日期: 2020-01-04 19:14:47
# 上次编辑时间: 2020-01-05 14:46:51
# 一个人的命运啊,当然要靠自我奋斗,但是...
'''


from PIL.ImageFont import truetype

class SameHeight(object):
    '''
    # 等高弹幕 --> 矩形分割问题？
    '''
    def __init__(self, text, font_path="msyh.ttc", font_size=14):
        self.font = truetype(font=font_path, size=font_size)
        self.width, self.height = self.get_danmu_size(text)
        self.height_range = [0, 720]
        self.width_range = [0, 1920]
        self.lines_start_y = list(range(*(self.height_range + [self.height])))
        self.lines_width_used = [[y, 0] for y in self.lines_start_y]
        self.contents = []

    def get_xy(self, text, show_time):
        # 在此之前 务必现将弹幕按时间排序
        self.contents.append([text, show_time])
        width, height = self.get_danmu_size(text)
        lines_index = self.get_min_width_used()
        self.update_width_used(lines_index, width)
        start_y = self.lines_start_y[lines_index]
        return width, height, start_y

    def get_min_width_used(self):
        sorted_width_used = sorted(self.lines_width_used, key=lambda width_used: width_used[1])
        lines_index = self.lines_width_used.index(sorted_width_used[0])
        return lines_index

    def update_width_used(self, index, length):
        self.lines_width_used[index][1] += length

    def get_danmu_size(self, text):
        # 放在这 不太好 每一次计算都会load下字体
        text_width, text_height = self.font.getsize(text)
        return text_width + 2, text_height + 2


def main():
    text = "测试"
    show_time = 13
    sh = SameHeight(text)
    sh.get_xy(text, show_time)
    

if __name__ == "__main__":
    main()