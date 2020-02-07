# GetDanMu

[转换/下载各类视频弹幕的工具][1]

项目主页：https://github.com/xhlove/GetDanMu

## 网站支持
| Site | URL | 单集? | 合集? | 综艺合集? | 支持series? |
| :--: | :-- | :-----: | :-----: | :-----: | :-----: |
| **腾讯视频** | <https://v.qq.com/>    |✓|✓| |
| **爱奇艺** | <https://www.iqiyi.com/>    |✓|✓|✓|✓|
| **优酷** | <https://v.youku.com/>    |✓|✓|✓|✓|
| **搜狐视频** | <https://tv.sohu.com/>    |✓|✓|||
| **芒果TV** | <https://www.mgtv.com/>    |✓|✓|✓|✓|

# 使用示例
- 命令（建议）

> GetDanMu.exe -s mgtv -r 20,960 -series -u https://www.mgtv.com/b/334727/7452407.html

- 双击运行
> 提示逻辑有待完善

- 选项说明
>     -f或--font 指定输出字幕字体，默认微软雅黑)
>     -fs或--font-size 指定输出字幕字体大小，默认28)
>     -s或--site 使用非url方式下载需指定网站 支持的网站 -> ["qq", "iqiyi", "youku", "sohu", "mgtv"]
>     -r或--range 指定弹幕的纵向范围 默认0到720，请用逗号隔开
>     -cid或--cid 下载cid对应视频的弹幕（腾讯 芒果视频合集）
>     -vid或--vid 下载vid对应视频的弹幕，支持同时多个vid，需要用逗号隔开
>     -aid或--aid 下载aid对应视频的弹幕（爱奇艺合集）
>     -tvid或--tvid 下载tvid对应视频的弹幕，支持同时多个tvid，需要用逗号隔开
>     -series或--series 尝试通过单集得到合集的全部弹幕 默认不使用
>     -u或--url 下载视频链接所指向视频的弹幕
>     -y或--y 覆盖原有弹幕而不提示 默认不使用


# 效果示意（字幕与视频不相关）
![potplayer截屏](http://puui.qpic.cn/vshpic/0/5TLOX3WbgjudEj61IxYZ4tAuf2lFwl-ynf4S5T4sXkdjS9cd_0/0)
[查看使用演示视频点我][2]

注意有背景音乐

演示是直接使用的python命令，使用exe的话把python GetDanMu.py换成GetDanMu.exe即可

## 可能存在的问题
- 下载进度接近100%时暂时没有反应

这是因为在全部弹幕获取完后一次性处理所致，对于时间过长和弹幕过多的视频，处理耗时较多，属于正常现象。
- 命令组合未达到预期效果

当前的逻辑并不完善，如果出现这种现象请反馈给我。

# 更新日志

## 2020/2/7
- 完善说明
- 爱奇艺支持series选项，并完善地区判断
- 增加字体配置文件，建立字体名称与实际字体文件的映射关系，用于预先设定，方便更准确计算弹幕的分布
- 增加自定义弹幕区间选项，即-r或--range命令
- README完善

## 2020/1/28
- 增加芒果TV的支持（支持综艺合集、支持series命令）
- 爱奇艺bug修复

## 2020/1/16
- 增加搜狐视频的支持（剧集）
- 改进输入提示（双击运行时）
- 腾讯支持-series设定

## 2020/1/11
- 增加优酷弹幕下载，支持合集，支持通过单集直接下载合集弹幕（暂时仅限优酷）
- 改进去重方式
- 优酷的视频id用vid指代，若下载合集请使用连接或通过`-series`选项下载合集弹幕
- 加入下载进度显示，后续可能改进为单行刷新

## 2020/1/5

- 增加了通过链接下载爱奇艺视频弹幕的方法，支持综艺合集。
- 增加通过链接判断网站

[赞助点此][3]

  [1]: https://blog.weimo.info/archives/431/
  [2]: https://alime-customer-upload-cn-hangzhou.oss-cn-hangzhou.aliyuncs.com/customer-upload/1581073011183_8t14dpgg2bdc.mp4
  [3]: https://afdian.net/@vvtoolbox_dev