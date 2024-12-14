# Generate video-editor compatible **furigana** subtitles

This implementation transforms RUBY html (default in ANKI and other Japanese learning tools) into a timeline element compatible, at least, with Davinci Resolve and Premiere Pro.

> Example of the output: [Eir Aoi - Ignite (Cover)](https://youtu.be/86kll8ww1rk)

# Steps
This is an example of the usage I did for my cover song. It should be of use as a blueprint for you. And it's also easier to explain.

## Step n° 1: Initial setup
As I go in more detail in [this video](https://youtu.be/eKQJcncVvR8), you should have a **target video** (locally), basic configurations on ABSPlayer, YomiTan and this [subtitle web app](https://www.happyscribe.com/subtitle-tools/online-subtitle-editor/free) open.

Once you have the requirements, you start sentence mining every line. *You might not care for the specific words* but following this method produces a very decent HTML-Ruby furigana that you can manually access in your new ANKI cards.

> You might also save your new `.srt` subtitle file and use it on your editor to adjust whatever needed. Then export the subtitles again.

## Step n° 2: Copy paste every *reading* field on the cards.
You will look for the **reading** field on each card, activate the <> option, which enables *code editing*, and copy it's contents into an empty `.txt` file. In this case im going for `subtitles_ignite.txt`.

Example of what a HTML-Ruby furigana code block might look like:

```html
<span class="term"><ruby>赤<rt>あか</rt></ruby>い</span><span class="term"><ruby>涙<rt>なみだ</rt></ruby></span><span class="term">で</span><span class="term"> </span><span class="term"><ruby>覆<rt>おお</rt></ruby>われた</span><span class="term"><ruby>悲<rt>かな</rt></ruby>しみ</span><span class="term">を</span>
```

> Default ruby blocks are very badly formated, it's a characteristic.

My `subtitles_ignite.txt` looks like this:

```txt
<span class="term"><ruby>零<rt>くぼ</rt></ruby>れた</span><span class="term"><ruby>涙<rt>なみだ</rt></ruby></span><span class="term">の</span><span class="term"><ruby>温<rt>ぬく</rt></ruby>もり</span><span class="term">で</span>
<span class="term"><ruby>優<rt>やさ</rt></ruby>しさ</span><span class="term">を</span><span class="term"><ruby>知<rt>し</rt></ruby>った<span class="term"><ruby>筈<rt>はず</rt></ruby></span></span><span class="term">なのに</span>
<span class="term">どうして</span><span class="term"> </span><span class="term">また</span><span class="term"><ruby>傷<rt>きず</rt></ruby>つけ</span><span class="term"><ruby>合<rt>あ</rt></ruby>って</span>
<span class="term"><ruby>憎<rt>にく</rt></ruby>しみ</span><span class="term">を</span><span class="term"><ruby>生<rt>う</rt></ruby>み<ruby>出<rt>だ</rt></ruby>して</span><span class="term">ゆく</span><span class="term">んだ</span><span class="term">ろう</span>
```

> Be sure your `.txt` file has the exact same amout of sentences than your `.str` file. Otherwise, further operations won't work.

## Step n° 3: Tranform to JSON array
Transform the text file into a json with `py convert_quotes.py <YOUR_FILE_NAME.txt>`.

In my case: `py convert_quotes.py subtitles_ignite.txt`.

## Step n° 4: Create the subtitle PNG images
To create the images for the furigana subs we run this command:

```shell
py generate_png_furigana.py subtitles_ignite.json ignite_subs --font <CUSTOM_FONT_FILE> --font-size <FONT_SIZE> --ruby-size <FURIGANA_FONT_SIZE> --vertical-margin <SUBTITLE_BOTTOM_MARGIN> --text-color <TEXT_COLOR> --stroke-color <STROKE_COLOR> --stroke-width <STROKE_WIDTH>
```

In my case:

```shell
py generate_png_furigana.py subtitles_ignite.json ignite_subs --font "MochiyPopPOne-Regular" --font-size 100 --ruby-size 60 --vertical-margin 250 --text-color "white" --stroke-color "black" --stroke-width 0
```

This will generated a folder called `\ignite_subs` where numerically sorted PNG images will be stored.

## Step n° 5: Create a timeline using the images and subtitles
To generate a video editor compatible timeline we will use the `.srt` subtitle file and the folder with the PNG images.

Run: `py generate_xml.py -i <IMAGE_FOLDER> -s <SRT_SUBTITLE_FILE> -o <OUTPUT_XML_TIMELINE_FILE> -f <FRAMERATE>`

In my case: `py generate_xml.py -i ignite_subs -s subtitles_ignite_video_placeholder.srt -o ignite_resolve_subs.xml -f 24`

This will generate a `XML` editor compatible file.

> Be aware that some editors have their **starting point** for the timelines set at 0 and others at 1, this means that **if you don't find your clips in the timeline** search the 1H time mark.

## Step n° 6 (optional): Create aditional subtitles in romaji
This command will transform the RUBY-HTML JSON array we created into basic `.str` subtitles.

Run: `py generate_srt_romaji.py <SUBTITLE_JSON_FILE> <ROMAJI_OUTPUT_SRT_SUBTITLE_FILE> <ORIGINAL_STR_SUBTITLE_FILE>`

In my case: `py generate_srt_romaji.py subtitles_ignite.json subtitles_ignite_romaji.srt subtitles_ignite_placeholder.srt`

> The script currently handles bad HTML tags pretty bad, so use it at your own risk. Ot works +80% of the scenarios.


# Other considerations
- If you try to use it vertically, it could still work, just consider creating the subtitles shorter or ask a *chatbot* to do it for you. And then zoom on the video.
- XML generation might cause "file/resource not found" in your video editor on import. Just search and find the PNG images folder manually.
- Timelines should start at 1, but some editors start counting at 0, this causes Davinci Resolve imports to appear at the 1 hour mark. Be aware of this when importing.
- Romaji subtitles is not yet fixed for all RUBY poorly formated tags, so it might contain errors, **double-check**. Feel free to fix it.