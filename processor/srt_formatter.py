# srt_formatter.py

import re
from datetime import timedelta

from src.logger import get_logger

logger = get_logger(__name__)

def parse_srt(srt_content):
    """
    Parses SRT content into a list of subtitle entries.
    Each entry is a dictionary with keys: index, start, end, text.
    """
    logger.debug("Parsing SRT content...")
    pattern = re.compile(
        r'(\d+)\s+'
        r'(\d{2}:\d{2}:\d{2},\d{3})\s*-->\s*'
        r'(\d{2}:\d{2}:\d{2},\d{3})\s+'
        r'([\s\S]*?)(?=\n\d+\s+\d{2}:\d{2}:\d{2},\d{3}-->|$)',
        re.MULTILINE
    )
    entries = []
    for match in pattern.finditer(srt_content):
        index = int(match.group(1))
        start = match.group(2)
        end = match.group(3)
        text = match.group(4).strip().replace('\r', '')
        logger.debug("Parsed entry: index=%s, start=%s, end=%s, text=%s...", index, start, end, text[:30])
        entries.append({
            'index': index,
            'start': start,
            'end': end,
            'text': text
        })
    return entries

def time_to_seconds(time_str):
    """
    Converts time string 'HH:MM:SS,mmm' to total seconds.
    """
    logger.debug("Converting time to seconds: %s", time_str)
    h, m, s = time_str.split(':')
    s, ms = s.split(',')
    total = int(h)*3600 + int(m)*60 + int(s) + int(ms)/1000
    logger.debug("Total seconds: %s", total)
    return total

def seconds_to_time(seconds):
    """
    Converts total seconds to time string 'HH:MM:SS,mmm'.
    """
    logger.debug("Converting seconds to time: %s", seconds)
    td = timedelta(seconds=seconds)
    total_seconds = int(td.total_seconds())
    millis = int((td.total_seconds() - total_seconds) * 1000)
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    secs = total_seconds % 60
    time_str = f"{hours:02}:{minutes:02}:{secs:02},{millis:03}"
    logger.debug("Converted time: %s", time_str)
    return time_str

def format_srt(entries):
    """
    Formats a list of subtitle entries into SRT format.
    Ensures sequential numbering and chronological order.
    """
    logger.debug("Formatting SRT entries...")
    # Sort entries by start time
    sorted_entries = sorted(entries, key=lambda x: time_to_seconds(x['start']))
    
    # Adjust overlapping entries if necessary
    for i in range(1, len(sorted_entries)):
        prev = sorted_entries[i-1]
        current = sorted_entries[i]
        prev_end = time_to_seconds(prev['end'])
        current_start = time_to_seconds(current['start'])
        if current_start < prev_end:
            logger.debug(
                "Adjusting overlap: Entry %s starts before previous entry ends.",
                current['index']
            )
            # Adjust current start to be after previous end
            new_start = prev_end + 0.001  # Adding 1 millisecond
            sorted_entries[i]['start'] = seconds_to_time(new_start)
            # Ensure end time is after start time
            current_end = time_to_seconds(current['end'])
            if current_end <= new_start:
                logger.debug(
                    "Adjusting end time for entry %s to ensure it is after start time.",
                    current['index']
                )
                sorted_entries[i]['end'] = seconds_to_time(new_start + 2)  # Adding 2 seconds as default

    # Renumber entries
    for idx, entry in enumerate(sorted_entries, start=1):
        entry['index'] = idx
        logger.debug(
            "Renumbered entry: index=%s, start=%s, end=%s",
            entry['index'],
            entry['start'],
            entry['end'],
        )

    # Build SRT content
    srt_content = ""
    for entry in sorted_entries:
        srt_content += f"{entry['index']}\n{entry['start']} --> {entry['end']}\n{entry['text']}\n\n"
    
    logger.debug("SRT formatting completed.")
    return srt_content

def correct_srt_format(srt_content):
    """
    Corrects the formatting of an SRT file to ensure compatibility with YouTube.
    
    :param srt_content: Original SRT content as a string.
    :return: Corrected SRT content as a string.
    """
    logger.debug("Correcting SRT format...")
    entries = parse_srt(srt_content)
    if not entries:
        raise ValueError("No valid SRT entries found.")
    corrected_srt = format_srt(entries)
    logger.debug("SRT format correction completed.")
    return corrected_srt

if __name__ == "__main__":
    # Example usage
    input_file = "input.srt"
    output_file = "corrected_output.srt"
    
    with open(input_file, 'r', encoding='utf-8') as f:
        original_srt = f.read()
    
    try:
        corrected_srt = correct_srt_format(original_srt)
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(corrected_srt)
        logger.info("Corrected SRT has been saved to %s", output_file)
    except Exception as e:
        logger.error("Error: %s", e)

