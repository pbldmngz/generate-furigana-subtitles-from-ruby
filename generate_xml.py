import os
import argparse
from xml.etree.ElementTree import Element, SubElement, ElementTree
from datetime import timedelta
import platform

def timecode_to_frames(timecode, fps=24):
    """Convert SRT timecode to frames."""
    h, m, s = map(float, timecode.replace(",", ".").split(":"))
    total_seconds = timedelta(hours=h, minutes=m, seconds=s).total_seconds()
    return int(total_seconds * fps)

def create_xmeml(images_folder, srt_file, output_xml, fps=24, width=1920, height=1080):
    # Parse SRT file to get subtitles timing
    subtitles = []
    with open(srt_file, "r", encoding="utf-8") as file:
        lines = file.readlines()
        for i in range(0, len(lines), 4):  # SRT format blocks
            start, end = lines[i+1].strip().split(" --> ")
            start_frame = timecode_to_frames(start, fps)
            end_frame = timecode_to_frames(end, fps)
            subtitles.append((start_frame, end_frame))

    # Fetch images in the folder
    images = sorted(
    [img for img in os.listdir(images_folder) if img.lower().endswith(('png'))],
        key=lambda x: int(x.split("_")[-1].split(".")[0])  # Extract the number and sort numerically
    )
    if len(images) != len(subtitles):
        raise ValueError(f"Number of images ({len(images)}) and subtitles ({len(subtitles)}) do not match!")

    # Create XML structure
    xmeml = Element("xmeml", version="5")
    sequence = SubElement(xmeml, "sequence")
    SubElement(sequence, "name").text = "Subtitle Project"
    SubElement(sequence, "duration").text = str(subtitles[-1][1])
    rate = SubElement(sequence, "rate")
    SubElement(rate, "timebase").text = str(fps)
    SubElement(rate, "ntsc").text = "false"

    media = SubElement(sequence, "media")
    video = SubElement(media, "video")
    format_elem = SubElement(video, "format")
    sample_characteristics = SubElement(format_elem, "samplecharacteristics")
    SubElement(sample_characteristics, "width").text = str(width)
    SubElement(sample_characteristics, "height").text = str(height)
    SubElement(sample_characteristics, "pixelaspectratio").text = "square"
    SubElement(sample_characteristics, "fielddominance").text = "none"
    rate_elem = SubElement(sample_characteristics, "rate")
    SubElement(rate_elem, "timebase").text = str(fps)
    SubElement(rate_elem, "ntsc").text = "false"

    track = SubElement(video, "track")

    # Offset all clips to start from 0
    timeline_offset = subtitles[0][0]  # First subtitle's start time (in frames)

    for i, (start, end) in enumerate(subtitles):
        duration = end - start
        clip_start = start - timeline_offset  # Adjust start by offset
        clip_end = end - timeline_offset  # Adjust end by offset

        clipitem = SubElement(track, "clipitem", id=f"Clip-{i + 1}")
        SubElement(clipitem, "name").text = f"Clip-{i + 1}"
        SubElement(clipitem, "start").text = str(clip_start)
        SubElement(clipitem, "end").text = str(clip_end)
        SubElement(clipitem, "in").text = "0"
        SubElement(clipitem, "out").text = str(duration)

        file_elem = SubElement(clipitem, "file", id=f"file-{i + 1}")
        SubElement(file_elem, "name").text = images[i]

        if platform.system() == "Windows":
            image_path = os.path.abspath(os.path.join(images_folder, images[i])).replace("\\", "/")
        else:
            image_path = f"file:///{os.path.abspath(os.path.join(images_folder, images[i])).replace('\\', '/')}"
        SubElement(file_elem, "pathurl").text = image_path
        rate_elem = SubElement(file_elem, "rate")
        SubElement(rate_elem, "timebase").text = str(fps)
        SubElement(rate_elem, "ntsc").text = "false"
        SubElement(file_elem, "duration").text = str(duration)

        media_elem = SubElement(file_elem, "media")
        video_elem = SubElement(media_elem, "video")
        SubElement(video_elem, "duration").text = str(duration)


    # Write to XML file
    tree = ElementTree(xmeml)
    tree.write(output_xml, encoding="utf-8", xml_declaration=True)
    print(f"XMEML file successfully created: {output_xml}")

def main():
    parser = argparse.ArgumentParser(
        description="Generate Adobe Premiere-compatible XML timeline (.xmeml) using images and subtitles."
    )
    parser.add_argument(
        "-i", "--images_folder", required=True, help="Path to the folder containing the images."
    )
    parser.add_argument(
        "-s", "--srt_file", required=True, help="Path to the subtitle file (SRT format)."
    )
    parser.add_argument(
        "-o", "--output_xml", required=True, help="Path to save the output .xmeml file."
    )
    parser.add_argument(
        "-f", "--fps", type=int, default=24, help="Frames per second for the timeline (default: 24)."
    )

    args = parser.parse_args()

    try:
        create_xmeml(args.images_folder, args.srt_file, args.output_xml, args.fps)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
