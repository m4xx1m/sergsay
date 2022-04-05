import os
import sys
import requests
from loguru import logger
from tempfile import mkstemp
from playsound import playsound
from argparse import ArgumentParser


LOG_FORMAT = "<green>{time:YYYY-MM-DD HH:mm:ss}</green> <red>|</red> <cyan>{level}</cyan> <red>|</red> <bold>{message}</bold>"
API_LINK = "https://nextup.com/ivona/php/nextup-polly/CreateSpeech/CreateSpeechGet3.php?voice=Maxim&language=ru-RU&text={text}"

logger.remove()
logger.add(sys.stdout, format=LOG_FORMAT)


def main():
    parser = ArgumentParser()
    parser.add_argument("-t", "--text", required=True, help="Text in quotes")
    parser.add_argument("-s", "--save", default=None, help="Save audiofile to <path>")
    parser.add_argument("-p", "--play", default=None, action="store_true", help="Play sound")
    args = parser.parse_args()
    
    text = args.text.strip()

    if not text:
        logger.error("No text")
        exit(-1)

    logger.info("Making API request")   

    rq = requests.get(API_LINK.format(text=text))
    
    if rq.status_code != 200:
        logger.error(f'Error while making api request (code: {rq.status_code})')
        exit(-1)

    logger.info("Api request successful")
    logger.info(f"Link to sound: {rq.text}")

    if args.save or args.play:
        file_content = requests.get(rq.text, stream=True).content

    if args.save:
        logger.info("Saving")
        with open(str(args.save.strip()) + ".mp3", "wb") as _sound_file:
            _sound_file.write(file_content)

        logger.info(f"Sound saved to {args.save.strip()}.mp3")

    if args.play:
        fd, tempPath = mkstemp(prefix='PS', suffix=".mp3")

        with open(tempPath, "wb") as _tempfile:
            _tempfile.write(file_content)

        logger.info("Playing")
        playsound(tempPath)
        os.close(fd)
        os.remove(tempPath)


if __name__ == '__main__':
    logger.info("Initializing")
    main()
